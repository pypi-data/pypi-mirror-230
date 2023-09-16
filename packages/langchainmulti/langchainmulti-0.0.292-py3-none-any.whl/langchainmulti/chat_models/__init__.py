"""**Chat Models** are a variation on language models.

While Chat Models use language models under the hood, the interface they expose
is a bit different. Rather than expose a "text in, text out" API, they expose
an interface where "chat messages" are the inputs and outputs.

**Class hierarchy:**

.. code-block::

    BaseLanguageModel --> BaseChatModel --> <name>  # Examples: ChatOpenAI, ChatGooglePalm

**Main helpers:**

.. code-block::

    AIMessage, BaseMessage, HumanMessage
"""  # noqa: E501

from langchainmulti.chat_models.anthropic import ChatAnthropic
from langchainmulti.chat_models.anyscale import ChatAnyscale
from langchainmulti.chat_models.azure_openai import AzureChatOpenAI
from langchainmulti.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchainmulti.chat_models.bedrock import BedrockChat
from langchainmulti.chat_models.ernie import ErnieBotChat
from langchainmulti.chat_models.fake import FakeListChatModel
from langchainmulti.chat_models.google_palm import ChatGooglePalm
from langchainmulti.chat_models.human import HumanInputChatModel
from langchainmulti.chat_models.jinachat import JinaChat
from langchainmulti.chat_models.konko import ChatKonko
from langchainmulti.chat_models.litellm import ChatLiteLLM
from langchainmulti.chat_models.mlflow_ai_gateway import ChatMLflowAIGateway
from langchainmulti.chat_models.ollama import ChatOllama
from langchainmulti.chat_models.openai import ChatOpenAI
from langchainmulti.chat_models.promptlayer_openai import PromptLayerChatOpenAI
from langchainmulti.chat_models.vertexai import ChatVertexAI

__all__ = [
    "ChatOpenAI",
    "BedrockChat",
    "AzureChatOpenAI",
    "FakeListChatModel",
    "PromptLayerChatOpenAI",
    "ChatAnthropic",
    "ChatGooglePalm",
    "ChatMLflowAIGateway",
    "ChatOllama",
    "ChatVertexAI",
    "JinaChat",
    "HumanInputChatModel",
    "ChatAnyscale",
    "ChatLiteLLM",
    "ErnieBotChat",
    "ChatKonko",
    "QianfanChatEndpoint",
]
