"""**Chains** are easily reusable components linked together.

Chains encode a sequence of calls to components like models, document retrievers,
other Chains, etc., and provide a simple interface to this sequence.

The Chain interface makes it easy to create apps that are:

    - **Stateful:** add Memory to any Chain to give it state,
    - **Observable:** pass Callbacks to a Chain to execute additional functionality,
      like logging, outside the main sequence of component calls,
    - **Composable:** combine Chains with other components, including other Chains.

**Class hierarchy:**

.. code-block::

    Chain --> <name>Chain  # Examples: LLMChain, MapReduceChain, RouterChain
"""

from langchainmulti.chains.api.base import APIChain
from langchainmulti.chains.api.openapi.chain import OpenAPIEndpointChain
from langchainmulti.chains.combine_documents.base import AnalyzeDocumentChain
from langchainmulti.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchainmulti.chains.combine_documents.map_rerank import MapRerankDocumentsChain
from langchainmulti.chains.combine_documents.reduce import ReduceDocumentsChain
from langchainmulti.chains.combine_documents.refine import RefineDocumentsChain
from langchainmulti.chains.combine_documents.stuff import StuffDocumentsChain
from langchainmulti.chains.constitutional_ai.base import ConstitutionalChain
from langchainmulti.chains.conversation.base import ConversationChain
from langchainmulti.chains.conversational_retrieval.base import (
    ChatVectorDBChain,
    ConversationalRetrievalChain,
)
from langchainmulti.chains.example_generator import generate_example
from langchainmulti.chains.flare.base import FlareChain
from langchainmulti.chains.graph_qa.arangodb import ArangoGraphQAChain
from langchainmulti.chains.graph_qa.base import GraphQAChain
from langchainmulti.chains.graph_qa.cypher import GraphCypherQAChain
from langchainmulti.chains.graph_qa.falkordb import FalkorDBQAChain
from langchainmulti.chains.graph_qa.hugegraph import HugeGraphQAChain
from langchainmulti.chains.graph_qa.kuzu import KuzuQAChain
from langchainmulti.chains.graph_qa.nebulagraph import NebulaGraphQAChain
from langchainmulti.chains.graph_qa.neptune_cypher import NeptuneOpenCypherQAChain
from langchainmulti.chains.graph_qa.sparql import GraphSparqlQAChain
from langchainmulti.chains.hyde.base import HypotheticalDocumentEmbedder
from langchainmulti.chains.llm import LLMChain
from langchainmulti.chains.llm_bash.base import LLMBashChain
from langchainmulti.chains.llm_checker.base import LLMCheckerChain
from langchainmulti.chains.llm_math.base import LLMMathChain
from langchainmulti.chains.llm_requests import LLMRequestsChain
from langchainmulti.chains.llm_summarization_checker.base import LLMSummarizationCheckerChain
from langchainmulti.chains.loading import load_chain
from langchainmulti.chains.mapreduce import MapReduceChain
from langchainmulti.chains.moderation import OpenAIModerationChain
from langchainmulti.chains.natbot.base import NatBotChain
from langchainmulti.chains.openai_functions import (
    create_citation_fuzzy_match_chain,
    create_extraction_chain,
    create_extraction_chain_pydantic,
    create_qa_with_sources_chain,
    create_qa_with_structure_chain,
    create_tagging_chain,
    create_tagging_chain_pydantic,
)
from langchainmulti.chains.qa_generation.base import QAGenerationChain
from langchainmulti.chains.qa_with_sources.base import QAWithSourcesChain
from langchainmulti.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchainmulti.chains.qa_with_sources.vector_db import VectorDBQAWithSourcesChain
from langchainmulti.chains.retrieval_qa.base import RetrievalQA, VectorDBQA
from langchainmulti.chains.router import (
    LLMRouterChain,
    MultiPromptChain,
    MultiRetrievalQAChain,
    MultiRouteChain,
    RouterChain,
)
from langchainmulti.chains.sequential import SequentialChain, SimpleSequentialChain
from langchainmulti.chains.sql_database.query import create_sql_query_chain
from langchainmulti.chains.transform import TransformChain

__all__ = [
    "APIChain",
    "AnalyzeDocumentChain",
    "ArangoGraphQAChain",
    "ChatVectorDBChain",
    "ConstitutionalChain",
    "ConversationChain",
    "ConversationalRetrievalChain",
    "FalkorDBQAChain",
    "FlareChain",
    "GraphCypherQAChain",
    "GraphQAChain",
    "GraphSparqlQAChain",
    "HugeGraphQAChain",
    "HypotheticalDocumentEmbedder",
    "KuzuQAChain",
    "LLMBashChain",
    "LLMChain",
    "LLMCheckerChain",
    "LLMMathChain",
    "LLMRequestsChain",
    "LLMRouterChain",
    "LLMSummarizationCheckerChain",
    "MapReduceChain",
    "MapReduceDocumentsChain",
    "MapRerankDocumentsChain",
    "MultiPromptChain",
    "MultiRetrievalQAChain",
    "MultiRouteChain",
    "NatBotChain",
    "NebulaGraphQAChain",
    "NeptuneOpenCypherQAChain",
    "OpenAIModerationChain",
    "OpenAPIEndpointChain",
    "QAGenerationChain",
    "QAWithSourcesChain",
    "ReduceDocumentsChain",
    "RefineDocumentsChain",
    "RetrievalQA",
    "RetrievalQAWithSourcesChain",
    "RouterChain",
    "SequentialChain",
    "SimpleSequentialChain",
    "StuffDocumentsChain",
    "TransformChain",
    "VectorDBQA",
    "VectorDBQAWithSourcesChain",
    "create_citation_fuzzy_match_chain",
    "create_extraction_chain",
    "create_extraction_chain_pydantic",
    "create_qa_with_sources_chain",
    "create_qa_with_structure_chain",
    "create_tagging_chain",
    "create_tagging_chain_pydantic",
    "generate_example",
    "load_chain",
    "create_sql_query_chain",
]
