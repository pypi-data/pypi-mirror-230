"""**Schemas** are the langchainmulti Base Classes and Interfaces."""
from langchainmulti.schema.agent import AgentAction, AgentFinish
from langchainmulti.schema.cache import BaseCache
from langchainmulti.schema.chat_history import BaseChatMessageHistory
from langchainmulti.schema.document import BaseDocumentTransformer, Document
from langchainmulti.schema.exceptions import langchainmultiException
from langchainmulti.schema.memory import BaseMemory
from langchainmulti.schema.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    _message_from_dict,
    _message_to_dict,
    get_buffer_string,
    messages_from_dict,
    messages_to_dict,
)
from langchainmulti.schema.output import (
    ChatGeneration,
    ChatResult,
    Generation,
    LLMResult,
    RunInfo,
)
from langchainmulti.schema.output_parser import (
    BaseLLMOutputParser,
    BaseOutputParser,
    OutputParserException,
    StrOutputParser,
)
from langchainmulti.schema.prompt import PromptValue
from langchainmulti.schema.prompt_template import BasePromptTemplate, format_document
from langchainmulti.schema.retriever import BaseRetriever
from langchainmulti.schema.storage import BaseStore

RUN_KEY = "__run"
Memory = BaseMemory

__all__ = [
    "BaseCache",
    "BaseMemory",
    "BaseStore",
    "AgentFinish",
    "AgentAction",
    "Document",
    "BaseChatMessageHistory",
    "BaseDocumentTransformer",
    "BaseMessage",
    "ChatMessage",
    "FunctionMessage",
    "HumanMessage",
    "AIMessage",
    "SystemMessage",
    "messages_from_dict",
    "messages_to_dict",
    "_message_to_dict",
    "_message_from_dict",
    "get_buffer_string",
    "RunInfo",
    "LLMResult",
    "ChatResult",
    "ChatGeneration",
    "Generation",
    "PromptValue",
    "langchainmultiException",
    "BaseRetriever",
    "RUN_KEY",
    "Memory",
    "OutputParserException",
    "StrOutputParser",
    "BaseOutputParser",
    "BaseLLMOutputParser",
    "BasePromptTemplate",
    "format_document",
]
