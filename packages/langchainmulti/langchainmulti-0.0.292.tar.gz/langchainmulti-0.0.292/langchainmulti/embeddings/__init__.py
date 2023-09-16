"""**Embedding models**  are wrappers around embedding models
from different APIs and services.

**Embedding models** can be LLMs or not.

**Class hierarchy:**

.. code-block::

    Embeddings --> <name>Embeddings  # Examples: OpenAIEmbeddings, HuggingFaceEmbeddings
"""


import logging
from typing import Any

from langchainmulti.embeddings.aleph_alpha import (
    AlephAlphaAsymmetricSemanticEmbedding,
    AlephAlphaSymmetricSemanticEmbedding,
)
from langchainmulti.embeddings.awa import AwaEmbeddings
from langchainmulti.embeddings.baidu_qianfan_endpoint import QianfanEmbeddingsEndpoint
from langchainmulti.embeddings.bedrock import BedrockEmbeddings
from langchainmulti.embeddings.cache import CacheBackedEmbeddings
from langchainmulti.embeddings.clarifai import ClarifaiEmbeddings
from langchainmulti.embeddings.cohere import CohereEmbeddings
from langchainmulti.embeddings.dashscope import DashScopeEmbeddings
from langchainmulti.embeddings.deepinfra import DeepInfraEmbeddings
from langchainmulti.embeddings.edenai import EdenAiEmbeddings
from langchainmulti.embeddings.elasticsearch import ElasticsearchEmbeddings
from langchainmulti.embeddings.embaas import EmbaasEmbeddings
from langchainmulti.embeddings.ernie import ErnieEmbeddings
from langchainmulti.embeddings.fake import DeterministicFakeEmbedding, FakeEmbeddings
from langchainmulti.embeddings.google_palm import GooglePalmEmbeddings
from langchainmulti.embeddings.gpt4all import GPT4AllEmbeddings
from langchainmulti.embeddings.huggingface import (
    HuggingFaceBgeEmbeddings,
    HuggingFaceEmbeddings,
    HuggingFaceInferenceAPIEmbeddings,
    HuggingFaceInstructEmbeddings,
)
from langchainmulti.embeddings.huggingface_hub import HuggingFaceHubEmbeddings
from langchainmulti.embeddings.jina import JinaEmbeddings
from langchainmulti.embeddings.llamacpp import LlamaCppEmbeddings
from langchainmulti.embeddings.localai import LocalAIEmbeddings
from langchainmulti.embeddings.minimax import MiniMaxEmbeddings
from langchainmulti.embeddings.mlflow_gateway import MlflowAIGatewayEmbeddings
from langchainmulti.embeddings.modelscope_hub import ModelScopeEmbeddings
from langchainmulti.embeddings.mosaicml import MosaicMLInstructorEmbeddings
from langchainmulti.embeddings.nlpcloud import NLPCloudEmbeddings
from langchainmulti.embeddings.octoai_embeddings import OctoAIEmbeddings
from langchainmulti.embeddings.ollama import OllamaEmbeddings
from langchainmulti.embeddings.openai import OpenAIEmbeddings
from langchainmulti.embeddings.sagemaker_endpoint import SagemakerEndpointEmbeddings
from langchainmulti.embeddings.self_hosted import SelfHostedEmbeddings
from langchainmulti.embeddings.self_hosted_hugging_face import (
    SelfHostedHuggingFaceEmbeddings,
    SelfHostedHuggingFaceInstructEmbeddings,
)
from langchainmulti.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchainmulti.embeddings.spacy_embeddings import SpacyEmbeddings
from langchainmulti.embeddings.tensorflow_hub import TensorflowHubEmbeddings
from langchainmulti.embeddings.vertexai import VertexAIEmbeddings
from langchainmulti.embeddings.xinference import XinferenceEmbeddings

logger = logging.getLogger(__name__)

__all__ = [
    "OpenAIEmbeddings",
    "CacheBackedEmbeddings",
    "ClarifaiEmbeddings",
    "CohereEmbeddings",
    "ElasticsearchEmbeddings",
    "HuggingFaceEmbeddings",
    "HuggingFaceInferenceAPIEmbeddings",
    "JinaEmbeddings",
    "LlamaCppEmbeddings",
    "HuggingFaceHubEmbeddings",
    "MlflowAIGatewayEmbeddings",
    "ModelScopeEmbeddings",
    "TensorflowHubEmbeddings",
    "SagemakerEndpointEmbeddings",
    "HuggingFaceInstructEmbeddings",
    "MosaicMLInstructorEmbeddings",
    "SelfHostedEmbeddings",
    "SelfHostedHuggingFaceEmbeddings",
    "SelfHostedHuggingFaceInstructEmbeddings",
    "FakeEmbeddings",
    "DeterministicFakeEmbedding",
    "AlephAlphaAsymmetricSemanticEmbedding",
    "AlephAlphaSymmetricSemanticEmbedding",
    "SentenceTransformerEmbeddings",
    "GooglePalmEmbeddings",
    "MiniMaxEmbeddings",
    "VertexAIEmbeddings",
    "BedrockEmbeddings",
    "DeepInfraEmbeddings",
    "EdenAiEmbeddings",
    "DashScopeEmbeddings",
    "EmbaasEmbeddings",
    "OctoAIEmbeddings",
    "SpacyEmbeddings",
    "NLPCloudEmbeddings",
    "GPT4AllEmbeddings",
    "XinferenceEmbeddings",
    "LocalAIEmbeddings",
    "AwaEmbeddings",
    "HuggingFaceBgeEmbeddings",
    "ErnieEmbeddings",
    "OllamaEmbeddings",
    "QianfanEmbeddingsEndpoint",
]


# TODO: this is in here to maintain backwards compatibility
class HypotheticalDocumentEmbedder:
    def __init__(self, *args: Any, **kwargs: Any):
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchainmulti.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchainmulti.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H(*args, **kwargs)  # type: ignore

    @classmethod
    def from_llm(cls, *args: Any, **kwargs: Any) -> Any:
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchainmulti.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchainmulti.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H.from_llm(*args, **kwargs)
