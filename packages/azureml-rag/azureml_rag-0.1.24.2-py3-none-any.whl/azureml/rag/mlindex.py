# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex class for interacting with MLIndex assets."""
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

import yaml
from azureml.rag.documents import Document, DocumentChunksIterator
from azureml.rag.embeddings import EmbeddingsContainer
from azureml.rag.utils.connections import get_connection_credential
from azureml.rag.utils.logging import get_logger, langchain_version, track_activity, version, packages_versions_for_compatibility
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document as LangChainDocument

logger = get_logger("mlindex")


class MLIndex:
    """MLIndex class for interacting with MLIndex assets."""

    base_uri: str
    index_config: dict
    embeddings_config: dict

    _underlying_index: Any = None

    def __init__(self, uri: Optional[Union[str, object]] = None, mlindex_config: Optional[dict] = None):
        """Initialize MLIndex from a URI or AzureML Data Asset."""
        with track_activity(logger, "MLIndex.__init__") as activity_logger:
            if uri is not None:
                if isinstance(uri, str):
                    uri = str(uri)
                elif isinstance(uri, Path):
                    uri = str(uri)
                else:
                    # Assume given AzureML Data Asset
                    uri = uri.path
                try:
                    import fsspec
                except ImportError:
                    raise ValueError(
                        "Could not import fsspec python package. "
                        "Please install it with `pip install fsspec`."
                    )
                try:
                    import azureml.fsspec
                except ImportError:
                    raise ValueError(
                        "Could not import azureml-fsspec python package. "
                        "Please install it with `pip install azureml-fsspec`."
                    )

                self.base_uri = uri

                mlindex_config = None
                try:
                    mlindex_file = fsspec.open(f"{uri.rstrip('/')}/MLIndex", "r")
                    if hasattr(mlindex_file.fs, "_path"):
                        # File on azureml filesystem has path relative to container root so need to get underlying fs path
                        self.base_uri = mlindex_file.fs._path.split('/MLIndex')[0]
                    else:
                        self.base_uri = mlindex_file.path.split('/MLIndex')[0]

                    with mlindex_file as f:
                        mlindex_config = yaml.safe_load(f)
                except Exception as e:
                    raise ValueError(f"Could not find MLIndex: {e}") from e
            elif mlindex_config is None:
                raise ValueError("Must provide either uri or mlindex_config")

            self.index_config = mlindex_config.get("index", {})
            if self.index_config is None:
                raise ValueError("Could not find index config in MLIndex yaml")
            activity_logger.activity_info["index_kind"] = self.index_config.get("kind", "none")
            self.embeddings_config = mlindex_config.get("embeddings", {})
            if self.embeddings_config is None:
                raise ValueError("Could not find embeddings config in MLIndex yaml")
            activity_logger.activity_info["embeddings_kind"] = self.embeddings_config.get("kind", "none")
            activity_logger.activity_info["embeddings_api_type"] = self.embeddings_config.get("api_type", "none")

    @property
    def name(self) -> str:
        """Returns the name of the MLIndex."""
        return self.index_config.get("name", "")

    @name.setter
    def name(self, value: str):
        """Sets the name of the MLIndex."""
        self.index_config["name"] = value

    @property
    def description(self) -> str:
        """Returns the description of the MLIndex."""
        return self.index_config.get("description", "")

    @description.setter
    def description(self, value: str):
        """Sets the description of the MLIndex."""
        self.index_config["description"] = value

    def get_langchain_embeddings(self):
        """Get the LangChainEmbeddings from the MLIndex."""
        embeddings = EmbeddingsContainer.from_metadata(self.embeddings_config.copy())

        return embeddings.as_langchain_embeddings()

    def as_langchain_vectorstore(self):
        """Converts MLIndex to a retriever object that can be used with langchain, may download files."""
        with track_activity(logger, "MLIndex.as_langchain_vectorstore") as activity_logger:
            index_kind = self.index_config.get("kind", "none")

            activity_logger.activity_info["index_kind"] = index_kind
            activity_logger.activity_info["embeddings_kind"] = self.embeddings_config.get("kind", "none")
            activity_logger.activity_info["embeddings_api_type"] = self.embeddings_config.get("api_type", "none")

            if index_kind == "acs":
                from azureml.rag.indexes.azure_search import import_azure_search_or_so_help_me

                import_azure_search_or_so_help_me()

                azure_search_documents_version = packages_versions_for_compatibility["azure-search-documents"]

                if self.index_config.get("field_mapping", {}).get("embedding", None) is None:
                    raise ValueError("field_mapping.embedding must be set in MLIndex config for acs index, try `.as_langchain_retriever()` instead.")

                if (azure_search_documents_version > "11.4.0b6" and langchain_version > "0.0.273") or (azure_search_documents_version == "11.4.0b6" and langchain_version < "0.0.273" and langchain_version >= "0.0.198"):
                    from langchain.vectorstores import azuresearch
                    # TODO: These fields effect all ACS retrievers in the same process, should change class so it can
                    # use these as defaults but uses names passed in as args preferentially
                    azuresearch.FIELDS_ID = self.index_config.get("field_mapping", {}).get("id", "id")
                    azuresearch.FIELDS_CONTENT = self.index_config.get("field_mapping", {}).get("content", "content")
                    azuresearch.FIELDS_CONTENT_VECTOR = self.index_config.get("field_mapping", {}).get("embedding", "content_vector_open_ai")
                    azuresearch.FIELDS_METADATA = self.index_config.get("field_mapping", {}).get("metadata", "meta_json_string")

                    from azure.core.credentials import AzureKeyCredential
                    from langchain.vectorstores.azuresearch import AzureSearch

                    credential = get_connection_credential(self.index_config)

                    return AzureSearch(
                        azure_search_endpoint=self.index_config.get("endpoint"),
                        azure_search_key=credential.key if isinstance(credential, AzureKeyCredential) else None,
                        index_name=self.index_config.get("index"),
                        embedding_function=self.get_langchain_embeddings().embed_query,
                        search_type="hybrid",
                        semantic_configuration_name=self.index_config.get("semantic_configuration_name", "azureml-default"),
                        user_agent=f"azureml-rag=={version}/mlindex,langchain=={langchain_version}",
                    )
                else:
                    from azureml.rag.langchain.acs import AzureCognitiveSearchVectorStore

                    logger.warning(f"azure-search-documents=={azure_search_documents_version} not compatible langchain.vectorstores.azuresearch yet, using REST client based VectorStore.")

                    credential = get_connection_credential(self.index_config)

                    return AzureCognitiveSearchVectorStore(
                        index_name=self.index_config.get("index"),
                        endpoint=self.index_config.get("endpoint"),
                        embeddings=self.get_langchain_embeddings(),
                        field_mapping=self.index_config.get("field_mapping", {}),
                        credential=credential,
                    )
            elif index_kind == "faiss":
                from fsspec.core import url_to_fs

                store = None
                engine = self.index_config.get("engine")
                if engine == "langchain.vectorstores.FAISS":
                    from langchain.vectorstores.faiss import FAISS

                    embeddings = EmbeddingsContainer.from_metadata(self.embeddings_config.copy()).as_langchain_embeddings()

                    fs, uri = url_to_fs(self.base_uri)

                    with tempfile.TemporaryDirectory() as tmpdir:
                        fs.download(f"{uri.rstrip('/')}/index.pkl", f"{str(tmpdir)}")
                        fs.download(f"{uri.rstrip('/')}/index.faiss", f"{str(tmpdir)}")
                        store = FAISS.load_local(str(tmpdir), embeddings)
                elif engine == "azureml.rag.indexes.faiss.FaissAndDocStore":
                    from azureml.rag.indexes.faiss import FaissAndDocStore
                    error_fmt_str = "Failed to import langchain faiss bridge module with: {e}\nThis could be due to an incompatible change in langchain since this bridge was implemented. If you understand what has changed you could implement your own wrapper of azureml.rag.indexes.faiss.FaissAndDocStore."
                    try:
                        from azureml.rag.langchain.faiss import azureml_faiss_as_langchain_faiss
                    except Exception as e:
                        logger.error(error_fmt_str.format(e=e))
                        raise

                    # TODO: Remove langchain embedder dependency
                    embeddings = EmbeddingsContainer.from_metadata(self.embeddings_config.copy()).as_langchain_embeddings()

                    try:
                        store = azureml_faiss_as_langchain_faiss(FaissAndDocStore.load(self.base_uri, embeddings.embed_query))
                    except Exception as e:
                        logger.error(error_fmt_str.format(e=e))
                        raise
                else:
                    raise ValueError(f"Unknown engine: {engine}")
                return store
            else:
                raise ValueError(f"Unknown index kind: {index_kind}")

    def as_langchain_retriever(self, **kwargs):
        """Converts MLIndex to a retriever object that can be used with langchain, may download files."""
        index_kind = self.index_config.get("kind", None)
        if index_kind == "acs":
            if self.index_config.get("field_mapping", {}).get("embedding", None) is None:
                from azureml.rag.langchain.acs import AzureCognitiveSearchVectorStore

                credential = get_connection_credential(self.index_config)

                return AzureCognitiveSearchVectorStore(
                    index_name=self.index_config.get("index"),
                    endpoint=self.index_config.get("endpoint"),
                    embeddings=self.get_langchain_embeddings(),
                    field_mapping=self.index_config.get("field_mapping", {}),
                    credential=credential,
                ).as_retriever(**kwargs)

            return self.as_langchain_vectorstore().as_retriever(**kwargs)
        elif index_kind == "faiss":
            return self.as_langchain_vectorstore().as_retriever()
        else:
            raise ValueError(f"Unknown index kind: {index_kind}")

    def __repr__(self):
        """Returns a string representation of the MLIndex object."""
        return yaml.dump({
            "index": self.index_config,
            "embeddings": self.embeddings_config,
        })
