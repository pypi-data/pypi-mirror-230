# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document parsing and chunking utilities."""
import copy
import os
import json
import re
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import IO, Any, Callable, Iterable, Iterator, List, Optional, Tuple, Type, Union

import mmh3
from azureml.rag.parsers.markdown import MarkdownBlock
from azureml.rag.utils.logging import get_logger, safe_mlflow_log_metric
from azureml.rag.utils.tokens import token_length_function, tiktoken_cache_dir
from langchain.document_loaders import UnstructuredFileIOLoader
from langchain.text_splitter import TextSplitter

logger = get_logger(__name__)


def merge_dicts(dict1, dict2):
    """Merge two dictionaries recursively."""
    result = defaultdict(dict)

    for d in (dict1, dict2):
        for key, value in d.items():
            if isinstance(value, dict) and key in result:
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

    return dict(result)


class Document(ABC):
    """Document."""

    document_id: str

    def __init__(self, document_id: str):
        """Initialize Document."""
        self.document_id = document_id

    @abstractmethod
    def modified_time(self) -> Any:
        """Get the modified time of the document."""
        pass

    @abstractmethod
    def load_data(self) -> str:
        """Load the data of the document."""
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        """Get the metadata of the document."""
        pass

    @abstractmethod
    def set_metadata(self, metadata: dict):
        """Set the metadata of the document."""
        pass

    @property
    def page_content(self) -> str:
        """Get the page content of the document."""
        return self.load_data()

    @property
    def metadata(self) -> dict:
        """Get the metadata of the document."""
        return self.get_metadata()

    @metadata.setter
    def metadata(self, value: dict):
        """Set the metadata of the document."""
        self.set_metadata(value)

    @abstractmethod
    def dumps(self) -> str:
        """Dump the document to a json string."""
        pass

    @classmethod
    @abstractmethod
    def loads(cls, data: str) -> "Document":
        """Load the document from a json string."""
        pass


class StaticDocument(Document):
    """Static Document holds data in-memory."""

    data: str
    _metadata: dict

    def __init__(self, data: str, metadata: dict, document_id: Optional[str] = None, mtime=None):
        """Initialize StaticDocument."""
        if document_id is None:
            filename = metadata.get("source", {}).get("filename", None)
            if filename is not None:
                document_id = f"{filename}{metadata.get('source', {}).get('chunk_id', '')}"
            else:
                import mmh3
                document_id = str(mmh3.hash128(data))

        super().__init__(document_id)
        self.data = data
        self._metadata = metadata
        self.mtime = mtime

    def modified_time(self) -> Any:
        """Get the modified time of the document."""
        return self.mtime

    def load_data(self) -> str:
        """Load the data of the document."""
        return self.data

    def get_metadata(self) -> dict:
        """Get the metadata of the document."""
        if "stats" in self._metadata:
            if "source" not in self._metadata:
                self._metadata["source"] = {}
            self._metadata["source"]["stats"] = self._metadata["stats"]
            del self._metadata["stats"]

        self._metadata = {**self._metadata, "stats": self.document_stats()}
        return self._metadata

    def set_metadata(self, metadata: dict):
        """Set the metadata of the document."""
        self._metadata = metadata

    def document_stats(self) -> dict:
        """Get the stats of the document."""
        return {
            "tiktokens": token_length_function()(self.data),
            "chars": len(self.data),
            "lines": len(self.data.splitlines()),
        }

    def __repr__(self):
        """Get the representation of the document."""
        return f"StaticDocument(id={self.document_id}, mtime={self.mtime}, metadata={self._metadata})"

    def dumps(self) -> str:
        """Dump the document to a json string."""
        return json.dumps({"content": self.data, "metadata": self._metadata, "document_id": self.document_id})

    @classmethod
    def loads(cls, data: str) -> "Document":
        """Load the document from a json string."""
        data_dict = json.loads(data)
        metadata = data_dict["metadata"]
        return cls(data_dict["content"], metadata, data_dict.get("document_id", metadata.get("document_id", metadata.get("id", mmh3.hash128(data_dict["content"])))))


@dataclass
class DocumentSource:
    """Document Source."""

    path: Path  # TODO:, should be full_url or something to be compat with not local Path
    filename: str
    url: str
    mtime: float

    def get_metadata(self) -> dict:
        """Get the metadata of the document source."""
        return {
            "filename": self.filename,
            "url": self.url,
            "mtime": self.mtime,
        }


@dataclass
class ChunkedDocument:
    """Chunked Document."""

    chunks: List[Document]
    source: DocumentSource
    metadata: dict

    @property
    def page_content(self):
        """Get the page content of the chunked document."""
        return "\n\n".join([chunk.page_content for chunk in self.chunks])

    def get_metadata(self):
        """Get the metadata of the chunked document."""
        return merge_dicts(self.metadata, {"source": self.source.get_metadata()})

    def flatten(self) -> List[Document]:
        """Flatten the chunked document."""
        chunks = []
        for i, chunk in enumerate(self.chunks):
            chunk.metadata["source"]["chunk_id"] = str(i)
            chunks.append(chunk)
        return chunks


@lru_cache(maxsize=1)
def _init_nltk():
    import nltk
    nltk.download("punkt")


class MarkdownHeaderSplitter(TextSplitter):
    """Split text by markdown headers."""

    def __init__(self, remove_hyperlinks: bool = True, remove_images: bool = True, **kwargs: Any):
        """Initialize Markdown Header Splitter."""
        from langchain.text_splitter import TokenTextSplitter
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images
        with tiktoken_cache_dir():
            self._sub_splitter = TokenTextSplitter(encoding_name="cl100k_base", **kwargs)
        super().__init__(**kwargs)

    def split_text(self, text: str) -> List[str]:
        """Split text into multiple components."""
        blocks = self.get_blocks(text)
        return [block.content for block in blocks]

    def create_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> List[StaticDocument]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []

        def get_nested_heading_string(md_block):
            nested_headings = []
            current_block = md_block
            while current_block is not None:
                if current_block.header is not None:
                    nested_headings.append(current_block.header)
                current_block = current_block.parent
            return "\n".join(nested_headings[::-1]) if len(nested_headings) > 0 else ""

        for i, text in enumerate(texts):
            for md_block in self.get_blocks(text):
                # TODO: Handle chunk being much smaller than ideal
                # Add to list for concat with other chunk? Make deep linking much harder,
                # could concat sections but still chunk other sections separately if large enough?
                block_nested_headings = get_nested_heading_string(md_block)
                if self._length_function(block_nested_headings + md_block.content) > self._chunk_size:
                    logger.info(f"Splitting section in chunks: {md_block.header}")
                    chunks = [f"{block_nested_headings}\n{chunk}" for chunk in self._sub_splitter.split_text(md_block.content)]
                else:
                    chunks = [f"{block_nested_headings}\n{md_block.content}"]

                metadata = _metadatas[i]
                metadata["markdown_heading"] = {
                    "heading": re.sub(
                        r"#",
                        "",
                        md_block.header if md_block.header is not None else metadata["source"]["filename"]
                    ).strip(),
                    "level": md_block.header_level
                }
                if len(chunks) > 0:
                    for chunk in chunks:
                        new_doc = StaticDocument(
                            chunk, metadata=copy.deepcopy(metadata)
                        )
                        documents.append(new_doc)
        return documents

    def get_blocks(self, markdown_text: str) -> List[MarkdownBlock]:
        """Parse blocks from markdown text."""
        blocks = re.split(r"(^#+\s.*)", markdown_text, flags=re.MULTILINE)
        blocks = [b for b in blocks if b.strip()]

        markdown_blocks = []
        header_stack = []

        if not blocks[0].startswith("#"):
            markdown_blocks.append(MarkdownBlock(header=None, content=blocks[0]))
            blocks = blocks[1:]

        for i in range(0, len(blocks), 2):
            header = blocks[i].strip()
            content = blocks[i + 1].strip() if i + 1 < len(blocks) else ""
            current_block = MarkdownBlock(header=header, content=content)
            header_level = current_block.header_level

            while len(header_stack) > 0 and header_stack[-1][0] >= header_level:
                header_stack.pop()

            parent_block = header_stack[-1][1] if len(header_stack) > 0 else None
            current_block.parent = parent_block

            header_stack.append((header_level, current_block))
            markdown_blocks.append(current_block)

        return markdown_blocks

    @staticmethod
    def _clean_markdown(text: str) -> str:
        # Remove html tags
        # If there's a <!-- comment -->, remove it, otherwise remove each <> pairing
        # TODO: Consider keeping some info from `<img src="img/img_name.PNG" alt="my img desc"/>`?`
        # Finding the image and doing img2text could be useful for linking back to the image,
        # would ideally know the text came from an image to link back to it (or inline it) in a particular way.
        text = re.sub(r"<!-- (.*?)->|<.*?>", "", text)
        # Cleanup whole line comments
        text = re.sub(r"<!-+\s*$", "", text)
        # Strip surrounding whitespace
        text = text.strip()
        return text


def get_langchain_splitter(file_extension: str, arguments: dict) -> TextSplitter:
    """Get a text splitter for a given file extension."""
    use_nltk = False
    if "use_nltk" in arguments:
        use_nltk = arguments["use_nltk"] is True
        del arguments["use_nltk"]
    use_rcts = False
    if "use_rcts" in arguments:
        use_rcts = arguments["use_rcts"] is True
        del arguments["use_rcts"]

    # Handle non-natural language splitters
    if file_extension == ".py":
        from langchain.text_splitter import PythonCodeTextSplitter
        with tiktoken_cache_dir():
            return PythonCodeTextSplitter.from_tiktoken_encoder(encoding_name="cl100k_base", **{**arguments, "disallowed_special": (), "allowed_special": "all"})

    # If configured to use NLTK for splitting on sentence boundaries use that for non-code text formats
    if use_nltk:
        _init_nltk()
        from langchain.text_splitter import NLTKTextSplitter

        return NLTKTextSplitter(
            length_function=token_length_function(),
            **arguments
        )

    # TODO: Support NLTK for splitting text as default?
    # Though want to keep MD specific splitting, only using NLTK on large chunks of plain text.

    # Finally use any text format specific splitters
    formats_to_treat_as_txt_once_loaded = [".pdf", ".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx"]
    if file_extension == ".txt" or file_extension in formats_to_treat_as_txt_once_loaded:
        from langchain.text_splitter import TokenTextSplitter

        with tiktoken_cache_dir():
            return TokenTextSplitter(
                encoding_name="cl100k_base",
                length_function=token_length_function(),
                **{**arguments, "disallowed_special": (), "allowed_special": "all"}
            )
    elif file_extension == ".html" or file_extension == ".htm":
        from langchain.text_splitter import TokenTextSplitter

        with tiktoken_cache_dir():
            return TokenTextSplitter(
                encoding_name="cl100k_base",
                length_function=token_length_function(),
                **{**arguments, "disallowed_special": (), "allowed_special": "all"}
            )
    elif file_extension == ".md":
        if use_rcts:
            from langchain.text_splitter import MarkdownTextSplitter

            with tiktoken_cache_dir():
                return MarkdownTextSplitter.from_tiktoken_encoder(encoding_name="cl100k_base", **{**arguments, "disallowed_special": (), "allowed_special": "all"})
        else:
            with tiktoken_cache_dir():
                return MarkdownHeaderSplitter.from_tiktoken_encoder(encoding_name="cl100k_base", remove_hyperlinks=True, remove_images=True, **{**arguments, "disallowed_special": (), "allowed_special": "all"})
    else:
        raise ValueError(f"Invalid file_extension: {file_extension}")


file_extension_splitters = {
    ".txt": lambda **kwargs: get_langchain_splitter(".txt", kwargs),
    ".md": lambda **kwargs: get_langchain_splitter(".md", kwargs),
    ".html": lambda **kwargs: get_langchain_splitter(".html", kwargs),
    ".htm": lambda **kwargs: get_langchain_splitter(".htm", kwargs),
    ".py": lambda **kwargs: get_langchain_splitter(".py", kwargs),
    ".pdf": lambda **kwargs: get_langchain_splitter(".pdf", kwargs),
    ".ppt": lambda **kwargs: get_langchain_splitter(".ppt", kwargs),
    ".pptx": lambda **kwargs: get_langchain_splitter(".pptx", kwargs),
    ".doc": lambda **kwargs: get_langchain_splitter(".doc", kwargs),
    ".docx": lambda **kwargs: get_langchain_splitter(".docx", kwargs),
    ".xls": lambda **kwargs: get_langchain_splitter(".xls", kwargs),
    ".xlsx": lambda **kwargs: get_langchain_splitter(".xlsx", kwargs),
}


# TODO: Change to be classes referenced in a map?
def extract_text_document_title(text: str, file_name: str) -> Tuple[str, str]:
    """Extract a title from a text document."""
    file_extension = Path(file_name).suffix
    if file_extension == ".md":
        heading_0 = re.search(r"#\s.*", text)
        if heading_0:
            title = heading_0.group(0).strip()
            return title, title[2:]

        import markdown
        from bs4 import BeautifulSoup
        html_content = markdown.markdown(text)
        soup = BeautifulSoup(html_content, "html.parser")
        title = ""
        clean_title = ""
        try:
            title = next(soup.stripped_strings)
            for entry in title.split("\n"):
                if entry.startswith("title") and not entry.startswith("titleSuffix"):
                    clean_title += entry[len("title: "):].rstrip()
                    break
        except StopIteration:
            title = file_name
        return title, (clean_title if len(clean_title) > 0 else file_name)
    elif file_extension == ".py":
        import ast

        def _get_topdocstring(text):
            tree = ast.parse(text)
            docstring = ast.get_docstring(tree)  # returns top docstring
            return docstring

        title = file_name
        try:
            docstring = _get_topdocstring(text)
            if docstring:
                title = f"{file_name}: {docstring}"
        except Exception as e:
            logger.warning(f"Failed to get docstring for {file_name}. Exception message: {e}")
            pass

        return f"Title: {title}", title
    elif file_extension == ".html" or file_extension == ".htm":
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, "html.parser")
        try:
            title = next(soup.stripped_strings)
        except StopIteration:
            title = file_name
        return f"Title: {title}", title
    else:
        title = None
        first_text_line = None
        title_prefix = "title: "
        for line in text.splitlines():
            if line.startswith(title_prefix):
                title = line[len(title_prefix):].strip()
                break
            if first_text_line is None and any(c.isalnum() for c in line):
                first_text_line = line.strip()

        if title is None:
            title = first_text_line if first_text_line is not None else file_name

        return f"Title: {title}", title


# TODO: add a method to determine if mode is binary or text
class BaseDocumentLoader(ABC):
    """Base class for document loaders."""

    def __init__(self, file: IO, document_source: DocumentSource, metadata: dict):
        """Initialize loader."""
        self.file = file
        self.document_source = document_source
        self.metadata = metadata

    def load_chunked_document(self) -> ChunkedDocument:
        """Load file contents into ChunkedDocument."""
        if "source" in self.metadata:
            if "title" not in self.metadata["source"]:
                self.metadata["source"]["title"] = Path(self.document_source.filename).name
        else:
            self.metadata["source"] = {"title": Path(self.document_source.filename).name}
        pages = self.load()
        return ChunkedDocument(
            chunks=pages,
            source=self.document_source,
            metadata=self.metadata
        )

    @abstractmethod
    def file_extensions(self) -> List[str]:
        """Return the file extensions of the file types to be loaded."""
        pass

    @abstractmethod
    def load(self) -> List[Document]:
        """Load file contents into Document(s)."""
        pass


class TextFileIOLoader(BaseDocumentLoader):
    """Load text files."""

    def load(self) -> List[Document]:
        """Load file contents into Document."""
        try:
            text = self.file.read().decode()
        except UnicodeDecodeError:
            self.file.seek(0)
            # Instead of trying to guess the correct text encoding if not 'utf-8', just ignore errors and log a warning
            logger.warning(f"UnicodeDecodeError has been ignored when reading file: {self.document_source.filename}")
            text = self.file.read().decode("utf-8", errors="ignore")

        title, clean_title = extract_text_document_title(text, self.document_source.filename)
        self.metadata = {**self.metadata, "source": {"title": clean_title}}
        chunk_prefix = title + "\n\n"
        self.metadata = {"chunk_prefix": chunk_prefix, **self.metadata}
        return [StaticDocument(data=text, metadata=self.metadata)]

    def file_extensions(self) -> List[str]:
        """Return the file extensions of the file types to be loaded."""
        return [".txt", ".md", ".py"]


class UnstructuredHTMLFileIOLoader(UnstructuredFileIOLoader, BaseDocumentLoader):
    """Loader that uses unstructured to load HTML files."""

    def __init__(self, file, document_source: DocumentSource, metadata: dict, mode="single", **unstructured_kwargs: Any):
        """Initialize a text file loader."""
        self.metadata = metadata
        self.document_source = document_source
        super().__init__(file=file, mode=mode, **unstructured_kwargs)

    def load(self) -> List[Document]:
        """Load file contents into Documents."""
        docs = super().load()
        # TODO: Extract html file title and add to metadata
        return [StaticDocument(data=doc.page_content, metadata=doc.metadata) for doc in docs]

    def file_extensions(self) -> List[str]:
        """Return the file extensions of the file types to be loaded."""
        return [".html", ".htm"]

    def _get_elements(self) -> List:
        from unstructured.partition.html import partition_html

        return partition_html(file=self.file, **self.unstructured_kwargs)

    def _get_metadata(self):
        return self.metadata


class PDFFileLoader(BaseDocumentLoader):
    """Load PDF files."""

    def load_chunked_document(self) -> ChunkedDocument:
        """Load file contents into ChunkedDocument."""
        pages = self.load()
        chunk_prefix = f"Title: {Path(self.document_source.filename).name}"
        return ChunkedDocument(
            chunks=pages,
            source=self.document_source,
            metadata={**self.metadata, "chunk_prefix": chunk_prefix}
        )

    def load(self) -> List[Document]:
        """Load file contents into Document(s)."""
        from pypdf import PdfReader
        docs: List[Document] = []
        reader = PdfReader(self.file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text is not None:
                metadata = {"page_number": reader.get_page_number(page), **self.metadata}
                docs.append(StaticDocument(page_text, metadata=metadata))
        if len(docs) == 0:
            logger.warning(f"Unable to extract text from file: {self.document_source.filename} This can happen if a PDF contains only images.")
        return docs

    def file_extensions(self) -> List[str]:
        """Return the file extensions of the file types to be loaded."""
        return [".pdf"]

    @staticmethod
    def fallback_loader() -> Type[BaseDocumentLoader]:
        """Return a fallback loader for this loader."""
        return TikaLoader


class TikaLoader(BaseDocumentLoader):
    """Load various unstructured files formats using Apache Tika."""

    def load_chunked_document(self) -> ChunkedDocument:
        """Load file contents into ChunkedDocument."""
        doc = self.load()
        chunk_prefix = f"Title: {Path(self.document_source.filename).name}"
        return ChunkedDocument(
            chunks=doc,
            source=self.document_source,
            metadata={"chunk_prefix": chunk_prefix, **self.metadata}
        )

    def load(self) -> List[Document]:
        """Load file content into Document(s)."""
        from tika import parser
        parsed = parser.from_file(self.file)
        content = parsed["content"]
        if content is None:
            logger.warning(f"Unable to extract text from file: {self.document_source.filename}")
            return []

        import re
        try:
            text = re.sub(r"\n{3,}", "\n\n", content)
        except TypeError as e:
            if "expected string or bytes-like object" in str(e):
                raise Exception(f"content needs to be of type str but it was of type {type(content)}.") from e
            else:
                raise e
        return [StaticDocument(data=text, metadata=self.metadata)]

    def file_extensions(self) -> List[str]:
        """Return the file extensions of the file types to be loaded."""
        return [".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx"]


file_extension_loaders = {
    ".txt": TextFileIOLoader,
    ".md": TextFileIOLoader,
    ".html": UnstructuredHTMLFileIOLoader,
    ".htm": UnstructuredHTMLFileIOLoader,
    ".py": TextFileIOLoader,
    ".pdf": PDFFileLoader,
    ".ppt": TikaLoader,
    ".pptx": TikaLoader,
    ".doc": TikaLoader,
    ".docx": TikaLoader,
    # TODO: we should probably not convert this to text and find a way to keep the table structure
    ".xls": TikaLoader,
    ".xlsx": TikaLoader,
}

SUPPORTED_EXTENSIONS = list(file_extension_loaders.keys())


def crack_documents(sources: Iterator[DocumentSource], file_extension_loaders=file_extension_loaders) -> Iterator[ChunkedDocument]:
    """Crack documents into chunks."""
    total_time = 0
    files_by_extension = {
        str(ext): 0.0 for ext in file_extension_loaders
    }
    log_batch_size = 100
    for i, source in enumerate(sources):
        file_start_time = time.time()
        files_by_extension[source.path.suffix.lower()] += 1
        loader_cls = file_extension_loaders.get(source.path.suffix.lower())
        if i % log_batch_size == 0:
            for ext in files_by_extension:
                if files_by_extension[ext] > 0:
                    safe_mlflow_log_metric(ext, files_by_extension[ext], logger=logger, step=int(time.time() * 1000))
        mode = "r"
        if loader_cls is None:
            raise RuntimeError(f"Unsupported file extension '{source.path.suffix}': {source.filename}")

        if loader_cls is TikaLoader or loader_cls is PDFFileLoader or loader_cls is TextFileIOLoader:
            mode = "rb"

        try:
            with open(source.path, mode=mode) as f:
                loader = loader_cls(**{
                    "file": f,
                    "document_source": source,
                    "metadata": {}
                })
                file_pre_yield_time = time.time()
                total_time += file_pre_yield_time - file_start_time
                yield loader.load_chunked_document()
        except Exception as e:
            # if loader_cls has a fallback_loader, try that
            if hasattr(loader_cls, "fallback_loader"):
                fallback_loader_cls = loader_cls.fallback_loader()
                with open(source.path, mode=mode) as f:
                    loader = fallback_loader_cls(**{
                        "file": f,
                        "document_source": source,
                        "metadata": {}
                    })
                    file_pre_yield_time = time.time()
                    total_time += file_pre_yield_time - file_start_time
                    yield loader.load_chunked_document()
            else:
                raise e

    for ext in files_by_extension:
        if files_by_extension[ext] > 0:
            safe_mlflow_log_metric(ext, files_by_extension[ext], logger=logger, step=int(time.time() * 1000))
    logger.info(f"[DocumentChunksIterator::crack_documents] Total time to load files: {total_time}\n{json.dumps(files_by_extension, indent=2)}")


def split_documents(documents: Iterable[ChunkedDocument], splitter_args: dict, file_extension_splitters=file_extension_splitters) -> Iterator[ChunkedDocument]:
    """Split documents into chunks."""
    total_time = 0
    total_documents = 0
    total_splits = 0
    log_batch_size = 100
    for i, document in enumerate(documents):
        if len(document.chunks) < 1:
            logger.warning(f"Skipped document with no chunks: {document.source.filename}")
            # TODO: Log this warning to telemetry with document metadata (extension, size, etc.) to get signal for improvements to parsing.
            continue
        file_start_time = time.time()
        total_documents += len(document.chunks)
        if i % log_batch_size == 0:
            safe_mlflow_log_metric("total_source_documents", total_documents, logger=logger, step=int(time.time() * 1000))

        local_splitter_args = splitter_args.copy()

        document_metadata = document.get_metadata()
        chunk_prefix = document_metadata.get("chunk_prefix", "")
        if len(chunk_prefix) > 0:
            if "chunk_size" in local_splitter_args:
                prefix_token_length = token_length_function()(chunk_prefix)
                if prefix_token_length > local_splitter_args["chunk_size"] // 2:
                    chunk_prefix = chunk_prefix[:local_splitter_args["chunk_size"] // 2]
                    # should we update local_splitter_args['chunk_size'] here?
                else:
                    local_splitter_args["chunk_size"] = local_splitter_args["chunk_size"] - prefix_token_length

        if "chunk_prefix" in document_metadata:
            del document_metadata["chunk_prefix"]

        # TODO: Move out as own filter
        chunk_overlap = 0
        if "chunk_overlap" in local_splitter_args:
            chunk_overlap = local_splitter_args["chunk_overlap"]

        def filter_short_docs(chunked_document):
            for doc in chunked_document.chunks:
                doc_len = len(doc.page_content)
                if doc_len < chunk_overlap:
                    logger.info(f"Filtering out doc_chunk shorter than {chunk_overlap}: {chunked_document.source.filename}")
                    continue
                yield doc

        def merge_metadata(chunked_document):
            for chunk in chunked_document.chunks:
                chunk.metadata = merge_dicts(chunk.metadata, document_metadata)
            return chunked_document

        splitter = file_extension_splitters.get(document.source.path.suffix.lower())(**local_splitter_args)
        split_docs = splitter.split_documents(list(filter_short_docs(merge_metadata(document))))

        i = -1
        file_chunks = []
        for chunk in split_docs:
            i += 1
            if "chunk_prefix" in chunk.metadata:
                del chunk.metadata["chunk_prefix"]
            file_chunks.append(StaticDocument(chunk_prefix + chunk.page_content, merge_dicts(chunk.metadata, document_metadata), document_id=document.source.filename + str(i), mtime=document.source.mtime))

        file_pre_yield_time = time.time()
        total_time += file_pre_yield_time - file_start_time
        if len(file_chunks) < 1:
            logger.info("No file_chunks to yield, continuing")
            continue
        total_splits += len(file_chunks)
        if i % log_batch_size == 0:
            safe_mlflow_log_metric("total_chunked_documents", total_splits, logger=logger, step=int(time.time() * 1000))
        document.chunks = file_chunks
        yield document

    safe_mlflow_log_metric("total_source_documents", total_documents, logger=logger, step=int(time.time() * 1000))
    safe_mlflow_log_metric("total_chunked_documents", total_splits, logger=logger, step=int(time.time() * 1000))
    logger.info(f"[DocumentChunksIterator::split_documents] Total time to split {total_documents} documents into {total_splits} chunks: {total_time}")


# TODO: Should handle uris via fsspec/MLTable
def files_to_document_source(
        files_source: Union[str, Path],
        glob: str = "**/*",
        base_url: Optional[str] = None,
        process_url: Optional[Callable[[str], str]] = None) -> Iterator[DocumentSource]:
    """Convert files to DocumentSource."""
    for file in Path(files_source).glob(glob):
        if not file.is_file():
            continue
        relative_path = file.relative_to(files_source)
        url = str(relative_path)
        if base_url:
            url = f"{base_url}/{relative_path}"
        if process_url:
            url = process_url(url)
        yield DocumentSource(
            path=file,
            filename=str(relative_path),
            url=url,
            mtime=file.stat().st_mtime
        )


class DocumentChunksIterator(Iterator):
    """Iterate over document chunks."""

    def __init__(
            self,
            files_source: Union[str, Path],
            glob: str,
            base_url: str = "",
            document_path_replacement_regex: Optional[str] = None,
            # document_sources: Iterator[DocumentSource],
            file_filter: Optional[Callable[[Iterable[DocumentSource]], Iterator[DocumentSource]]]=None,
            source_loader: Callable[[Iterable[DocumentSource]], Iterator[ChunkedDocument]]=crack_documents,
            chunked_document_processors: Optional[List[Callable[[Iterable[ChunkedDocument]], Iterator[ChunkedDocument]]]] = [
                lambda docs: split_documents(docs, splitter_args={"chunk_size": 1024, "chunk_overlap": 0})
            ]):
        """Initialize a document chunks iterator."""
        self.files_source = files_source
        self.glob = glob
        self.base_url = base_url
        self.document_path_replacement_regex = document_path_replacement_regex
        # self.document_sources = document_sources
        if file_filter is None:
            file_filter = self._document_statistics
        self.file_filter = file_filter
        self.source_loader = source_loader

        self.chunked_document_processors = chunked_document_processors
        self.document_chunks_iterator = None
        self.__document_statistics = None
        self.span = None

    def __iter__(self) -> Iterator[ChunkedDocument]:
        """Iterate over document chunks."""
        if self.document_path_replacement_regex:
            document_path_replacement = json.loads(self.document_path_replacement_regex)
            url_replacement_match = re.compile(document_path_replacement["match_pattern"])

            def process_url(url):
                return url_replacement_match.sub(document_path_replacement["replacement_pattern"], url)
        else:
            def process_url(url):
                return url

        if self.base_url is None:
            self.base_url = self._infer_base_url_from_git(self.files_source)

        source_documents = files_to_document_source(self.files_source, self.glob, self.base_url, process_url)
        if self.file_filter is not None:
            source_documents = self.file_filter(source_documents)
        document_chunks_iterator = self.source_loader(source_documents)

        if self.chunked_document_processors is not None:
            for chunked_document_processor in self.chunked_document_processors:
                document_chunks_iterator = chunked_document_processor(document_chunks_iterator)

        self.document_chunks_iterator = document_chunks_iterator

        return self

    def __next__(self):
        """Get the next document chunk.""."""
        if self.document_chunks_iterator is None:
            raise StopIteration
        # if self.span is None:
        #     self.span = tracer.start_span('DocumentChunksIterator::__next__')
        try:
            return next(self.document_chunks_iterator)
        except StopIteration:
            self.document_chunks_iterator = None
            if self.span is not None:
                self.span.end()
            raise StopIteration

    def document_statistics(self):
        """
        Provide current statistics about the documents processed by iDocumentChunkIterator.

        **Note:** The statistics only include files which have already been pulled through the iterator, calling this before iterating will yield None.
        """
        return self.__document_statistics

    def _document_statistics(self, sources: Iterable[DocumentSource], allowed_extensions=SUPPORTED_EXTENSIONS) -> Iterator[DocumentSource]:
        """Filter out sources with extensions not in allowed_extensions."""
        if self.__document_statistics is None:
            self.__document_statistics = {
                "total_files": 0,
                "skipped_files": 0,
                "skipped_extensions": {},
                "kept_extensions": {}
            }
        for source in sources:
            self.__document_statistics["total_files"] += 1
            if allowed_extensions is not None:
                if source.path.suffix not in allowed_extensions:
                    self.__document_statistics["skipped_files"] += 1
                    ext_skipped = self.__document_statistics["skipped_extensions"].get(source.path.suffix.lower(), 0)
                    self.__document_statistics["skipped_extensions"][source.path.suffix.lower()] = ext_skipped + 1
                    logger.debug(f'Filtering out extension "{source.path.suffix.lower()}" source: {source.filename}')
                    continue
            ext_kept = self.__document_statistics["kept_extensions"].get(source.path.suffix.lower(), 0)
            self.__document_statistics["kept_extensions"][source.path.suffix.lower()] = ext_kept + 1
            yield source
        logger.info(f"[DocumentChunksIterator::filter_extensions] Filtered {self.__document_statistics['skipped_files']} files out of {self.__document_statistics['total_files']}")
        if self.span is not None:
            self.span.set_attributes({
                f"document_statistics.{k}": v for k, v in self.__document_statistics.items()
            })

    @staticmethod
    def _infer_base_url_from_git(files_source: Union[str, Path]) -> Optional[str]:
        """Try and infer base_url from git repo remote info if source is in a git repo."""
        try:
            import git

            repo = git.Repo(str(files_source), search_parent_directories=True)
            remote_url = repo.remote().url
            if remote_url.endswith(".git"):
                remote_url = remote_url[:-4]
            if remote_url.startswith("git@"):
                remote_url = remote_url.replace(":", "/")
                remote_url = remote_url.replace("git@", "https://")

            if "dev.azure.com" in remote_url:
                remote_url = remote_url.replace("https://ssh.dev.azure.com/v3/", "")
                try:
                    org, project, repo = remote_url.split("/")
                    remote_url = f"https://{org}.visualstudio.com/DefaultCollection/{project}/_git/{repo}?version=GB{repo.active_branch.name}&path="
                except Exception:
                    logger.warning(f"Failed to parse org, project and repo from Azure DevOps remote url: {remote_url}")
                    pass
            else:
                # Infer branch from repo
                remote_url = f"{remote_url}/blob/{repo.active_branch.name}"

            return remote_url
        except Exception:
            pass
