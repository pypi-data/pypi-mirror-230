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

from langchainmulti.retrievers.arxiv import ArxivRetriever
from langchainmulti.retrievers.azure_cognitive_search import AzureCognitiveSearchRetriever
from langchainmulti.retrievers.bm25 import BM25Retriever
from langchainmulti.retrievers.chaindesk import ChaindeskRetriever
from langchainmulti.retrievers.chatgpt_plugin_retriever import ChatGPTPluginRetriever
from langchainmulti.retrievers.contextual_compression import ContextualCompressionRetriever
from langchainmulti.retrievers.docarray import DocArrayRetriever
from langchainmulti.retrievers.elastic_search_bm25 import ElasticSearchBM25Retriever
from langchainmulti.retrievers.ensemble import EnsembleRetriever
from langchainmulti.retrievers.google_cloud_enterprise_search import (
    GoogleCloudEnterpriseSearchRetriever,
)
from langchainmulti.retrievers.kendra import AmazonKendraRetriever
from langchainmulti.retrievers.knn import KNNRetriever
from langchainmulti.retrievers.llama_index import (
    LlamaIndexGraphRetriever,
    LlamaIndexRetriever,
)
from langchainmulti.retrievers.merger_retriever import MergerRetriever
from langchainmulti.retrievers.metal import MetalRetriever
from langchainmulti.retrievers.milvus import MilvusRetriever
from langchainmulti.retrievers.multi_query import MultiQueryRetriever
from langchainmulti.retrievers.multi_vector import MultiVectorRetriever
from langchainmulti.retrievers.parent_document_retriever import ParentDocumentRetriever
from langchainmulti.retrievers.pinecone_hybrid_search import PineconeHybridSearchRetriever
from langchainmulti.retrievers.pubmed import PubMedRetriever
from langchainmulti.retrievers.re_phraser import RePhraseQueryRetriever
from langchainmulti.retrievers.remote_retriever import RemotelangchainmultiRetriever
from langchainmulti.retrievers.self_query.base import SelfQueryRetriever
from langchainmulti.retrievers.svm import SVMRetriever
from langchainmulti.retrievers.tfidf import TFIDFRetriever
from langchainmulti.retrievers.time_weighted_retriever import (
    TimeWeightedVectorStoreRetriever,
)
from langchainmulti.retrievers.vespa_retriever import VespaRetriever
from langchainmulti.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchainmulti.retrievers.web_research import WebResearchRetriever
from langchainmulti.retrievers.wikipedia import WikipediaRetriever
from langchainmulti.retrievers.zep import ZepRetriever
from langchainmulti.retrievers.zilliz import ZillizRetriever

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
    "RemotelangchainmultiRetriever",
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
