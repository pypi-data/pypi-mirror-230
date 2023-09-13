# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""HTML Parsing"""
# TODO: StaticDocument requires document_id be passed in, but it should be able to generate it.
from azureml.rag.documents import StaticDocument, TokenEstimator
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import Optional, Union
import re


# TODO: Move to text utils?
def cleanup_content(content: str) -> str:
    """Cleans up the given content using regexes
    Args:
        content (str): The content to clean up.
    Returns:
        str: The cleaned up content.
    """
    output = re.sub(r"\n{2,}", "\n", content)
    output = re.sub(r"[^\S\n]{2,}", " ", output)
    output = re.sub(r"-{2,}", "--", output)

    return output.strip()


# TODO: Maybe implement `BaseBlobParser` from langchain?
class HTMLParser:
    """Parses HTML content."""
    TITLE_MAX_TOKENS = 128
    NEWLINE_TEMPL = "<NEWLINE_TEXT>"

    def __init__(self, token_estimator = TokenEstimator()) -> None:
        super().__init__()
        self.token_estimator = token_estimator

    def parse(self, content: str, file_name: Optional[str] = None) -> StaticDocument:
        """Parses the given content.
        Args:
            content (str): The content to parse.
            file_name (str): The file name associated with the content.
        Returns:
            Document: The parsed document.
        """
        soup = BeautifulSoup(content, 'html.parser')

        # Extract the title
        title = ''
        if soup.title and soup.title.string:
            title = soup.title.string
        else:
            # Try to find the first <h1> tag
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
            else:
                h2_tag = soup.find('h2')
                if h2_tag:
                    title = h2_tag.get_text(strip=True)
        if title is None or title == '':
            # if title is still not found, guess using the next string
            try:
                title = next(soup.stripped_strings)
                title = self.token_estimator.truncate(title, self.TITLE_MAX_TOKENS)
            except StopIteration:
                title = file_name

        # Helper function to process text nodes
        def process_text(text):
            return text.strip()

        # Helper function to process anchor tags
        def process_anchor_tag(tag):
            href = tag.get('href', '')
            text = tag.get_text(strip=True)
            return f'{text} ({href})'

        # Collect all text nodes and anchor tags in a list
        elements = []
        skip_elements = []
        for elem in soup.descendants:
            if elem in skip_elements:
                continue
            if isinstance(elem, (Tag, NavigableString)):
                page_element: Union[Tag, NavigableString] = elem
                if page_element.name in ['title', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'code']:
                    if isinstance(page_element, Tag):
                        del page_element['id']
                        skip_elements += list(page_element.descendants)
                    elements.append(page_element)
                if isinstance(page_element, str) and \
                        (
                                (not elements) or
                                (isinstance(elements[-1], Tag) and (page_element not in elements[-1].descendants))
                        ):
                    elements.append(process_text(page_element))
                elif page_element.name == 'a':
                    elements.append(process_anchor_tag(page_element))

        # Join the list into a single string and return but ensure that either of newlines or space are used.
        result = '\n'.join([str(elem) for elem in elements])

        if title is None:
            title = ''  # ensure no 'None' type title
        return StaticDocument(document_id=f'{file_name}0', data=cleanup_content(result), metadata={'title': str(title)})
