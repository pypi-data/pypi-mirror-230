"""**Vector store** stores embedded data and performs vector search.

One of the most common ways to store and search over unstructured data is to
embed it and store the resulting embedding vectors, and then query the store
and retrieve the data that are 'most similar' to the embedded query.

**Class hierarchy:**

.. code-block::

    VectorStore --> <name>  # Examples: Annoy, FAISS, Milvus

    BaseRetriever --> VectorStoreRetriever --> <name>Retriever  # Example: VespaRetriever

**Main helpers:**

.. code-block::

    Embeddings, Document
"""  # noqa: E501
from langchaincoexpert.vectorstores.alibabacloud_opensearch import (
    AlibabaCloudOpenSearch,
    AlibabaCloudOpenSearchSettings,
)
from langchaincoexpert.vectorstores.analyticdb import AnalyticDB
from langchaincoexpert.vectorstores.annoy import Annoy
from langchaincoexpert.vectorstores.atlas import AtlasDB
from langchaincoexpert.vectorstores.awadb import AwaDB
from langchaincoexpert.vectorstores.azuresearch import AzureSearch
from langchaincoexpert.vectorstores.bageldb import Bagel
from langchaincoexpert.vectorstores.base import VectorStore
from langchaincoexpert.vectorstores.cassandra import Cassandra
from langchaincoexpert.vectorstores.chroma import Chroma
from langchaincoexpert.vectorstores.clarifai import Clarifai
from langchaincoexpert.vectorstores.clickhouse import Clickhouse, ClickhouseSettings
from langchaincoexpert.vectorstores.dashvector import DashVector
from langchaincoexpert.vectorstores.deeplake import DeepLake
from langchaincoexpert.vectorstores.dingo import Dingo
from langchaincoexpert.vectorstores.docarray import DocArrayHnswSearch, DocArrayInMemorySearch
from langchaincoexpert.vectorstores.elastic_vector_search import (
    ElasticKnnSearch,
    ElasticVectorSearch,
)
from langchaincoexpert.vectorstores.elasticsearch import ElasticsearchStore
from langchaincoexpert.vectorstores.epsilla import Epsilla
from langchaincoexpert.vectorstores.faiss import FAISS
from langchaincoexpert.vectorstores.hologres import Hologres
from langchaincoexpert.vectorstores.lancedb import LanceDB
from langchaincoexpert.vectorstores.marqo import Marqo
from langchaincoexpert.vectorstores.matching_engine import MatchingEngine
from langchaincoexpert.vectorstores.meilisearch import Meilisearch
from langchaincoexpert.vectorstores.milvus import Milvus
from langchaincoexpert.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchaincoexpert.vectorstores.myscale import MyScale, MyScaleSettings
from langchaincoexpert.vectorstores.neo4j_vector import Neo4jVector
from langchaincoexpert.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
from langchaincoexpert.vectorstores.pgembedding import PGEmbedding
from langchaincoexpert.vectorstores.pgvector import PGVector
from langchaincoexpert.vectorstores.pinecone import Pinecone
from langchaincoexpert.vectorstores.qdrant import Qdrant
from langchaincoexpert.vectorstores.redis import Redis
from langchaincoexpert.vectorstores.rocksetdb import Rockset
from langchaincoexpert.vectorstores.scann import ScaNN
from langchaincoexpert.vectorstores.singlestoredb import SingleStoreDB
from langchaincoexpert.vectorstores.sklearn import SKLearnVectorStore
from langchaincoexpert.vectorstores.sqlitevss import SQLiteVSS
from langchaincoexpert.vectorstores.starrocks import StarRocks
from langchaincoexpert.vectorstores.supabase import SupabaseVectorStore
from langchaincoexpert.vectorstores.tair import Tair
from langchaincoexpert.vectorstores.tencentvectordb import TencentVectorDB
from langchaincoexpert.vectorstores.tigris import Tigris
from langchaincoexpert.vectorstores.typesense import Typesense
from langchaincoexpert.vectorstores.usearch import USearch
from langchaincoexpert.vectorstores.vectara import Vectara
from langchaincoexpert.vectorstores.weaviate import Weaviate
from langchaincoexpert.vectorstores.zep import ZepVectorStore
from langchaincoexpert.vectorstores.zilliz import Zilliz

__all__ = [
    "AlibabaCloudOpenSearch",
    "AlibabaCloudOpenSearchSettings",
    "AnalyticDB",
    "Annoy",
    "Annoy",
    "AtlasDB",
    "AtlasDB",
    "AwaDB",
    "AzureSearch",
    "Bagel",
    "Cassandra",
    "Chroma",
    "Chroma",
    "Clarifai",
    "Clickhouse",
    "ClickhouseSettings",
    "DashVector",
    "DeepLake",
    "DeepLake",
    "Dingo",
    "DocArrayHnswSearch",
    "DocArrayInMemorySearch",
    "ElasticKnnSearch",
    "ElasticVectorSearch",
    "ElasticsearchStore",
    "Epsilla",
    "FAISS",
    "Hologres",
    "LanceDB",
    "Marqo",
    "MatchingEngine",
    "Meilisearch",
    "Milvus",
    "MongoDBAtlasVectorSearch",
    "MyScale",
    "MyScaleSettings",
    "Neo4jVector",
    "OpenSearchVectorSearch",
    "OpenSearchVectorSearch",
    "PGEmbedding",
    "PGVector",
    "Pinecone",
    "Qdrant",
    "Redis",
    "Rockset",
    "SKLearnVectorStore",
    "ScaNN",
    "SingleStoreDB",
    "SingleStoreDB",
    "SQLiteVSS",
    "StarRocks",
    "SupabaseVectorStore",
    "Tair",
    "Tigris",
    "Typesense",
    "USearch",
    "Vectara",
    "VectorStore",
    "Weaviate",
    "ZepVectorStore",
    "Zilliz",
    "Zilliz",
    "TencentVectorDB",
]
