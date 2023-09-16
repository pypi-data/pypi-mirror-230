from typing import Dict, Type, Union

from langchainmulti.agents.agent import BaseSingleActionAgent
from langchainmulti.agents.agent_types import AgentType
from langchainmulti.agents.chat.base import ChatAgent
from langchainmulti.agents.conversational.base import ConversationalAgent
from langchainmulti.agents.conversational_chat.base import ConversationalChatAgent
from langchainmulti.agents.mrkl.base import ZeroShotAgent
from langchainmulti.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchainmulti.agents.openai_functions_multi_agent.base import OpenAIMultiFunctionsAgent
from langchainmulti.agents.react.base import ReActDocstoreAgent
from langchainmulti.agents.self_ask_with_search.base import SelfAskWithSearchAgent
from langchainmulti.agents.structured_chat.base import StructuredChatAgent

AGENT_TYPE = Union[Type[BaseSingleActionAgent], Type[OpenAIMultiFunctionsAgent]]

AGENT_TO_CLASS: Dict[AgentType, AGENT_TYPE] = {
    AgentType.ZERO_SHOT_REACT_DESCRIPTION: ZeroShotAgent,
    AgentType.REACT_DOCSTORE: ReActDocstoreAgent,
    AgentType.SELF_ASK_WITH_SEARCH: SelfAskWithSearchAgent,
    AgentType.CONVERSATIONAL_REACT_DESCRIPTION: ConversationalAgent,
    AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION: ChatAgent,
    AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION: ConversationalChatAgent,
    AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION: StructuredChatAgent,
    AgentType.OPENAI_FUNCTIONS: OpenAIFunctionsAgent,
    AgentType.OPENAI_MULTI_FUNCTIONS: OpenAIMultiFunctionsAgent,
}
