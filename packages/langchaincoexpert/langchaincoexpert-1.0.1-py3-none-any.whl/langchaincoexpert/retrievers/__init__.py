"""**Retriever** class returns Documents given a text **query**.

It is more general than a vector store. A retriever does not need to be able to
store documents, only to return (or retrieve) it. Vector stores can be used as
the backbone of a retriever, but there are other types of retrievers as well.

**Class hierarchy:**

.. code-block::

    BaseRetriever --> <name>Retriever  # Examples: ArxivRetriever, MergerRetriever

**Main helpers:**

.. code-block::

    Document, Serializable, Callbacks,
    CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun
"""

from langchaincoexpert.retrievers.arxiv import ArxivRetriever
from langchaincoexpert.retrievers.azure_cognitive_search import AzureCognitiveSearchRetriever
from langchaincoexpert.retrievers.bm25 import BM25Retriever
from langchaincoexpert.retrievers.chaindesk import ChaindeskRetriever
from langchaincoexpert.retrievers.chatgpt_plugin_retriever import ChatGPTPluginRetriever
from langchaincoexpert.retrievers.contextual_compression import ContextualCompressionRetriever
from langchaincoexpert.retrievers.docarray import DocArrayRetriever
from langchaincoexpert.retrievers.elastic_search_bm25 import ElasticSearchBM25Retriever
from langchaincoexpert.retrievers.ensemble import EnsembleRetriever
from langchaincoexpert.retrievers.google_cloud_enterprise_search import (
    GoogleCloudEnterpriseSearchRetriever,
)
from langchaincoexpert.retrievers.kendra import AmazonKendraRetriever
from langchaincoexpert.retrievers.knn import KNNRetriever
from langchaincoexpert.retrievers.llama_index import (
    LlamaIndexGraphRetriever,
    LlamaIndexRetriever,
)
from langchaincoexpert.retrievers.merger_retriever import MergerRetriever
from langchaincoexpert.retrievers.metal import MetalRetriever
from langchaincoexpert.retrievers.milvus import MilvusRetriever
from langchaincoexpert.retrievers.multi_query import MultiQueryRetriever
from langchaincoexpert.retrievers.multi_vector import MultiVectorRetriever
from langchaincoexpert.retrievers.parent_document_retriever import ParentDocumentRetriever
from langchaincoexpert.retrievers.pinecone_hybrid_search import PineconeHybridSearchRetriever
from langchaincoexpert.retrievers.pubmed import PubMedRetriever
from langchaincoexpert.retrievers.re_phraser import RePhraseQueryRetriever
from langchaincoexpert.retrievers.remote_retriever import RemotelangchaincoexpertRetriever
from langchaincoexpert.retrievers.self_query.base import SelfQueryRetriever
from langchaincoexpert.retrievers.svm import SVMRetriever
from langchaincoexpert.retrievers.tfidf import TFIDFRetriever
from langchaincoexpert.retrievers.time_weighted_retriever import (
    TimeWeightedVectorStoreRetriever,
)
from langchaincoexpert.retrievers.vespa_retriever import VespaRetriever
from langchaincoexpert.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchaincoexpert.retrievers.web_research import WebResearchRetriever
from langchaincoexpert.retrievers.wikipedia import WikipediaRetriever
from langchaincoexpert.retrievers.zep import ZepRetriever
from langchaincoexpert.retrievers.zilliz import ZillizRetriever

__all__ = [
    "AmazonKendraRetriever",
    "ArxivRetriever",
    "AzureCognitiveSearchRetriever",
    "ChatGPTPluginRetriever",
    "ContextualCompressionRetriever",
    "ChaindeskRetriever",
    "ElasticSearchBM25Retriever",
    "GoogleCloudEnterpriseSearchRetriever",
    "KNNRetriever",
    "LlamaIndexGraphRetriever",
    "LlamaIndexRetriever",
    "MergerRetriever",
    "MetalRetriever",
    "MilvusRetriever",
    "MultiQueryRetriever",
    "PineconeHybridSearchRetriever",
    "PubMedRetriever",
    "RemotelangchaincoexpertRetriever",
    "SVMRetriever",
    "SelfQueryRetriever",
    "TFIDFRetriever",
    "BM25Retriever",
    "TimeWeightedVectorStoreRetriever",
    "VespaRetriever",
    "WeaviateHybridSearchRetriever",
    "WikipediaRetriever",
    "ZepRetriever",
    "ZillizRetriever",
    "DocArrayRetriever",
    "RePhraseQueryRetriever",
    "WebResearchRetriever",
    "EnsembleRetriever",
    "ParentDocumentRetriever",
    "MultiVectorRetriever",
]
