"""**Document Transformers** are classes to transform Documents.

**Document Transformers** usually used to transform a lot of Documents in a single run.

**Class hierarchy:**

.. code-block::

    BaseDocumentTransformer --> <name>  # Examples: DoctranQATransformer, DoctranTextTranslator

**Main helpers:**

.. code-block::

    Document
"""  # noqa: E501

from langchaincoexpert.document_transformers.beautiful_soup_transformer import (
    BeautifulSoupTransformer,
)
from langchaincoexpert.document_transformers.doctran_text_extract import (
    DoctranPropertyExtractor,
)
from langchaincoexpert.document_transformers.doctran_text_qa import DoctranQATransformer
from langchaincoexpert.document_transformers.doctran_text_translate import DoctranTextTranslator
from langchaincoexpert.document_transformers.embeddings_redundant_filter import (
    EmbeddingsClusteringFilter,
    EmbeddingsRedundantFilter,
    get_stateful_documents,
)
from langchaincoexpert.document_transformers.html2text import Html2TextTransformer
from langchaincoexpert.document_transformers.long_context_reorder import LongContextReorder
from langchaincoexpert.document_transformers.nuclia_text_transform import NucliaTextTransformer
from langchaincoexpert.document_transformers.openai_functions import OpenAIMetadataTagger

__all__ = [
    "BeautifulSoupTransformer",
    "DoctranQATransformer",
    "DoctranTextTranslator",
    "DoctranPropertyExtractor",
    "EmbeddingsClusteringFilter",
    "EmbeddingsRedundantFilter",
    "get_stateful_documents",
    "LongContextReorder",
    "NucliaTextTransformer",
    "OpenAIMetadataTagger",
    "Html2TextTransformer",
]
