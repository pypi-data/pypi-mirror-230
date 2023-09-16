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
from langchainmulti.vectorstores.alibabacloud_opensearch import (
    AlibabaCloudOpenSearch,
    AlibabaCloudOpenSearchSettings,
)
from langchainmulti.vectorstores.analyticdb import AnalyticDB
from langchainmulti.vectorstores.annoy import Annoy
from langchainmulti.vectorstores.atlas import AtlasDB
from langchainmulti.vectorstores.awadb import AwaDB
from langchainmulti.vectorstores.azuresearch import AzureSearch
from langchainmulti.vectorstores.bageldb import Bagel
from langchainmulti.vectorstores.base import VectorStore
from langchainmulti.vectorstores.cassandra import Cassandra
from langchainmulti.vectorstores.chroma import Chroma
from langchainmulti.vectorstores.clarifai import Clarifai
from langchainmulti.vectorstores.clickhouse import Clickhouse, ClickhouseSettings
from langchainmulti.vectorstores.dashvector import DashVector
from langchainmulti.vectorstores.deeplake import DeepLake
from langchainmulti.vectorstores.dingo import Dingo
from langchainmulti.vectorstores.docarray import DocArrayHnswSearch, DocArrayInMemorySearch
from langchainmulti.vectorstores.elastic_vector_search import (
    ElasticKnnSearch,
    ElasticVectorSearch,
)
from langchainmulti.vectorstores.elasticsearch import ElasticsearchStore
from langchainmulti.vectorstores.epsilla import Epsilla
from langchainmulti.vectorstores.faiss import FAISS
from langchainmulti.vectorstores.hologres import Hologres
from langchainmulti.vectorstores.lancedb import LanceDB
from langchainmulti.vectorstores.marqo import Marqo
from langchainmulti.vectorstores.matching_engine import MatchingEngine
from langchainmulti.vectorstores.meilisearch import Meilisearch
from langchainmulti.vectorstores.milvus import Milvus
from langchainmulti.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchainmulti.vectorstores.myscale import MyScale, MyScaleSettings
from langchainmulti.vectorstores.neo4j_vector import Neo4jVector
from langchainmulti.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
from langchainmulti.vectorstores.pgembedding import PGEmbedding
from langchainmulti.vectorstores.pgvector import PGVector
from langchainmulti.vectorstores.pinecone import Pinecone
from langchainmulti.vectorstores.qdrant import Qdrant
from langchainmulti.vectorstores.redis import Redis
from langchainmulti.vectorstores.rocksetdb import Rockset
from langchainmulti.vectorstores.scann import ScaNN
from langchainmulti.vectorstores.singlestoredb import SingleStoreDB
from langchainmulti.vectorstores.sklearn import SKLearnVectorStore
from langchainmulti.vectorstores.sqlitevss import SQLiteVSS
from langchainmulti.vectorstores.starrocks import StarRocks
from langchainmulti.vectorstores.supabase import SupabaseVectorStore
from langchainmulti.vectorstores.tair import Tair
from langchainmulti.vectorstores.tencentvectordb import TencentVectorDB
from langchainmulti.vectorstores.tigris import Tigris
from langchainmulti.vectorstores.typesense import Typesense
from langchainmulti.vectorstores.usearch import USearch
from langchainmulti.vectorstores.vectara import Vectara
from langchainmulti.vectorstores.weaviate import Weaviate
from langchainmulti.vectorstores.zep import ZepVectorStore
from langchainmulti.vectorstores.zilliz import Zilliz

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
