"""Module for parsing text files.."""
from typing import Iterator

from langchaincoexpert.document_loaders.base import BaseBlobParser
from langchaincoexpert.document_loaders.blob_loaders import Blob
from langchaincoexpert.schema import Document


class TextParser(BaseBlobParser):
    """Parser for text blobs."""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Lazily parse the blob."""
        yield Document(page_content=blob.as_string(), metadata={"source": blob.source})
