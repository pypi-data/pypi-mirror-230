"""
**LLM** classes provide
access to the large language model (**LLM**) APIs and services.

**Class hierarchy:**

.. code-block::

    BaseLanguageModel --> BaseLLM --> LLM --> <name>  # Examples: AI21, HuggingFaceHub, OpenAI

**Main helpers:**

.. code-block::

    LLMResult, PromptValue,
    CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun,
    CallbackManager, AsyncCallbackManager,
    AIMessage, BaseMessage
"""  # noqa: E501
from typing import Dict, Type

from langchainmulti.llms.ai21 import AI21
from langchainmulti.llms.aleph_alpha import AlephAlpha
from langchainmulti.llms.amazon_api_gateway import AmazonAPIGateway
from langchainmulti.llms.anthropic import Anthropic
from langchainmulti.llms.anyscale import Anyscale
from langchainmulti.llms.aviary import Aviary
from langchainmulti.llms.azureml_endpoint import AzureMLOnlineEndpoint
from langchainmulti.llms.baidu_qianfan_endpoint import QianfanLLMEndpoint
from langchainmulti.llms.bananadev import Banana
from langchainmulti.llms.base import BaseLLM
from langchainmulti.llms.baseten import Baseten
from langchainmulti.llms.beam import Beam
from langchainmulti.llms.bedrock import Bedrock
from langchainmulti.llms.bittensor import NIBittensorLLM
from langchainmulti.llms.cerebriumai import CerebriumAI
from langchainmulti.llms.chatglm import ChatGLM
from langchainmulti.llms.clarifai import Clarifai
from langchainmulti.llms.cohere import Cohere
from langchainmulti.llms.ctransformers import CTransformers
from langchainmulti.llms.ctranslate2 import CTranslate2
from langchainmulti.llms.databricks import Databricks
from langchainmulti.llms.deepinfra import DeepInfra
from langchainmulti.llms.deepsparse import DeepSparse
from langchainmulti.llms.edenai import EdenAI
from langchainmulti.llms.fake import FakeListLLM
from langchainmulti.llms.fireworks import Fireworks, FireworksChat
from langchainmulti.llms.forefrontai import ForefrontAI
from langchainmulti.llms.google_palm import GooglePalm
from langchainmulti.llms.gooseai import GooseAI
from langchainmulti.llms.gpt4all import GPT4All
from langchainmulti.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchainmulti.llms.huggingface_hub import HuggingFaceHub
from langchainmulti.llms.huggingface_pipeline import HuggingFacePipeline
from langchainmulti.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference
from langchainmulti.llms.human import HumanInputLLM
from langchainmulti.llms.koboldai import KoboldApiLLM
from langchainmulti.llms.llamacpp import LlamaCpp
from langchainmulti.llms.manifest import ManifestWrapper
from langchainmulti.llms.minimax import Minimax
from langchainmulti.llms.mlflow_ai_gateway import MlflowAIGateway
from langchainmulti.llms.modal import Modal
from langchainmulti.llms.mosaicml import MosaicML
from langchainmulti.llms.nlpcloud import NLPCloud
from langchainmulti.llms.octoai_endpoint import OctoAIEndpoint
from langchainmulti.llms.ollama import Ollama
from langchainmulti.llms.opaqueprompts import OpaquePrompts
from langchainmulti.llms.openai import AzureOpenAI, OpenAI, OpenAIChat
from langchainmulti.llms.openllm import OpenLLM
from langchainmulti.llms.openlm import OpenLM
from langchainmulti.llms.petals import Petals
from langchainmulti.llms.pipelineai import PipelineAI
from langchainmulti.llms.predibase import Predibase
from langchainmulti.llms.predictionguard import PredictionGuard
from langchainmulti.llms.promptlayer_openai import PromptLayerOpenAI, PromptLayerOpenAIChat
from langchainmulti.llms.replicate import Replicate
from langchainmulti.llms.rwkv import RWKV
from langchainmulti.llms.sagemaker_endpoint import SagemakerEndpoint
from langchainmulti.llms.self_hosted import SelfHostedPipeline
from langchainmulti.llms.self_hosted_hugging_face import SelfHostedHuggingFaceLLM
from langchainmulti.llms.stochasticai import StochasticAI
from langchainmulti.llms.symblai_nebula import Nebula
from langchainmulti.llms.textgen import TextGen
from langchainmulti.llms.titan_takeoff import TitanTakeoff
from langchainmulti.llms.tongyi import Tongyi
from langchainmulti.llms.vertexai import VertexAI, VertexAIModelGarden
from langchainmulti.llms.vllm import VLLM, VLLMOpenAI
from langchainmulti.llms.writer import Writer
from langchainmulti.llms.xinference import Xinference

__all__ = [
    "AI21",
    "AlephAlpha",
    "AmazonAPIGateway",
    "Anthropic",
    "Anyscale",
    "Aviary",
    "AzureMLOnlineEndpoint",
    "AzureOpenAI",
    "Banana",
    "Baseten",
    "Beam",
    "Bedrock",
    "CTransformers",
    "CTranslate2",
    "CerebriumAI",
    "ChatGLM",
    "Clarifai",
    "Cohere",
    "Databricks",
    "DeepInfra",
    "DeepSparse",
    "EdenAI",
    "FakeListLLM",
    "Fireworks",
    "FireworksChat",
    "ForefrontAI",
    "GPT4All",
    "GooglePalm",
    "GooseAI",
    "HuggingFaceEndpoint",
    "HuggingFaceHub",
    "HuggingFacePipeline",
    "HuggingFaceTextGenInference",
    "HumanInputLLM",
    "KoboldApiLLM",
    "LlamaCpp",
    "TextGen",
    "ManifestWrapper",
    "Minimax",
    "MlflowAIGateway",
    "Modal",
    "MosaicML",
    "Nebula",
    "NIBittensorLLM",
    "NLPCloud",
    "Ollama",
    "OpenAI",
    "OpenAIChat",
    "OpenLLM",
    "OpenLM",
    "Petals",
    "PipelineAI",
    "Predibase",
    "PredictionGuard",
    "PromptLayerOpenAI",
    "PromptLayerOpenAIChat",
    "OpaquePrompts",
    "RWKV",
    "Replicate",
    "SagemakerEndpoint",
    "SelfHostedHuggingFaceLLM",
    "SelfHostedPipeline",
    "StochasticAI",
    "TitanTakeoff",
    "Tongyi",
    "VertexAI",
    "VertexAIModelGarden",
    "VLLM",
    "VLLMOpenAI",
    "Writer",
    "OctoAIEndpoint",
    "Xinference",
    "QianfanLLMEndpoint",
]

type_to_cls_dict: Dict[str, Type[BaseLLM]] = {
    "ai21": AI21,
    "aleph_alpha": AlephAlpha,
    "amazon_api_gateway": AmazonAPIGateway,
    "amazon_bedrock": Bedrock,
    "anthropic": Anthropic,
    "anyscale": Anyscale,
    "aviary": Aviary,
    "azure": AzureOpenAI,
    "azureml_endpoint": AzureMLOnlineEndpoint,
    "bananadev": Banana,
    "baseten": Baseten,
    "beam": Beam,
    "cerebriumai": CerebriumAI,
    "chat_glm": ChatGLM,
    "clarifai": Clarifai,
    "cohere": Cohere,
    "ctransformers": CTransformers,
    "ctranslate2": CTranslate2,
    "databricks": Databricks,
    "deepinfra": DeepInfra,
    "deepsparse": DeepSparse,
    "edenai": EdenAI,
    "fake-list": FakeListLLM,
    "forefrontai": ForefrontAI,
    "google_palm": GooglePalm,
    "gooseai": GooseAI,
    "gpt4all": GPT4All,
    "huggingface_endpoint": HuggingFaceEndpoint,
    "huggingface_hub": HuggingFaceHub,
    "huggingface_pipeline": HuggingFacePipeline,
    "huggingface_textgen_inference": HuggingFaceTextGenInference,
    "human-input": HumanInputLLM,
    "koboldai": KoboldApiLLM,
    "llamacpp": LlamaCpp,
    "textgen": TextGen,
    "minimax": Minimax,
    "mlflow-ai-gateway": MlflowAIGateway,
    "modal": Modal,
    "mosaic": MosaicML,
    "nebula": Nebula,
    "nibittensor": NIBittensorLLM,
    "nlpcloud": NLPCloud,
    "ollama": Ollama,
    "openai": OpenAI,
    "openlm": OpenLM,
    "petals": Petals,
    "pipelineai": PipelineAI,
    "predibase": Predibase,
    "opaqueprompts": OpaquePrompts,
    "replicate": Replicate,
    "rwkv": RWKV,
    "sagemaker_endpoint": SagemakerEndpoint,
    "self_hosted": SelfHostedPipeline,
    "self_hosted_hugging_face": SelfHostedHuggingFaceLLM,
    "stochasticai": StochasticAI,
    "tongyi": Tongyi,
    "titan_takeoff": TitanTakeoff,
    "vertexai": VertexAI,
    "vertexai_model_garden": VertexAIModelGarden,
    "openllm": OpenLLM,
    "openllm_client": OpenLLM,
    "vllm": VLLM,
    "vllm_openai": VLLMOpenAI,
    "writer": Writer,
    "xinference": Xinference,
    "qianfan_endpoint": QianfanLLMEndpoint,
}
