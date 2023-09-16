# ruff: noqa: E402
"""Main entrypoint into package."""
from importlib import metadata
from typing import Optional

from langchainmulti.agents import MRKLChain, ReActChain, SelfAskWithSearchChain
from langchainmulti.chains import (
    ConversationChain,
    LLMBashChain,
    LLMChain,
    LLMCheckerChain,
    LLMMathChain,
    QAWithSourcesChain,
    VectorDBQA,
    VectorDBQAWithSourcesChain,
)
from langchainmulti.docstore import InMemoryDocstore, Wikipedia
from langchainmulti.llms import (
    Anthropic,
    Banana,
    CerebriumAI,
    Cohere,
    ForefrontAI,
    GooseAI,
    HuggingFaceHub,
    HuggingFaceTextGenInference,
    LlamaCpp,
    Modal,
    OpenAI,
    Petals,
    PipelineAI,
    SagemakerEndpoint,
    StochasticAI,
    Writer,
)
from langchainmulti.llms.huggingface_pipeline import HuggingFacePipeline
from langchainmulti.prompts import (
    FewShotPromptTemplate,
    Prompt,
    PromptTemplate,
)
from langchainmulti.schema.cache import BaseCache
from langchainmulti.schema.prompt_template import BasePromptTemplate
from langchainmulti.utilities.arxiv import ArxivAPIWrapper
from langchainmulti.utilities.golden_query import GoldenQueryAPIWrapper
from langchainmulti.utilities.google_search import GoogleSearchAPIWrapper
from langchainmulti.utilities.google_serper import GoogleSerperAPIWrapper
from langchainmulti.utilities.powerbi import PowerBIDataset
from langchainmulti.utilities.searx_search import SearxSearchWrapper
from langchainmulti.utilities.serpapi import SerpAPIWrapper
from langchainmulti.utilities.sql_database import SQLDatabase
from langchainmulti.utilities.wikipedia import WikipediaAPIWrapper
from langchainmulti.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchainmulti.vectorstores import FAISS, ElasticVectorSearch

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

verbose: bool = False
debug: bool = False
llm_cache: Optional[BaseCache] = None

# For backwards compatibility
SerpAPIChain = SerpAPIWrapper


__all__ = [
    "LLMChain",
    "LLMBashChain",
    "LLMCheckerChain",
    "LLMMathChain",
    "ArxivAPIWrapper",
    "GoldenQueryAPIWrapper",
    "SelfAskWithSearchChain",
    "SerpAPIWrapper",
    "SerpAPIChain",
    "SearxSearchWrapper",
    "GoogleSearchAPIWrapper",
    "GoogleSerperAPIWrapper",
    "WolframAlphaAPIWrapper",
    "WikipediaAPIWrapper",
    "Anthropic",
    "Banana",
    "CerebriumAI",
    "Cohere",
    "ForefrontAI",
    "GooseAI",
    "Modal",
    "OpenAI",
    "Petals",
    "PipelineAI",
    "StochasticAI",
    "Writer",
    "BasePromptTemplate",
    "Prompt",
    "FewShotPromptTemplate",
    "PromptTemplate",
    "ReActChain",
    "Wikipedia",
    "HuggingFaceHub",
    "SagemakerEndpoint",
    "HuggingFacePipeline",
    "SQLDatabase",
    "PowerBIDataset",
    "FAISS",
    "MRKLChain",
    "VectorDBQA",
    "ElasticVectorSearch",
    "InMemoryDocstore",
    "ConversationChain",
    "VectorDBQAWithSourcesChain",
    "QAWithSourcesChain",
    "LlamaCpp",
    "HuggingFaceTextGenInference",
]
