"""Memory modules for conversation prompts."""

from langchainmulti.memory.buffer import (
    ConversationBufferMemory,
    ConversationStringBufferMemory,
)
from langchainmulti.memory.buffer_window import ConversationBufferWindowMemory
from langchainmulti.memory.combined import CombinedMemory
from langchainmulti.memory.entity import ConversationEntityMemory
from langchainmulti.memory.kg import ConversationKGMemory
from langchainmulti.memory.summary import ConversationSummaryMemory
from langchainmulti.memory.summary_buffer import ConversationSummaryBufferMemory

# This is only for backwards compatibility.

__all__ = [
    "ConversationSummaryBufferMemory",
    "ConversationSummaryMemory",
    "ConversationKGMemory",
    "ConversationBufferWindowMemory",
    "ConversationEntityMemory",
    "ConversationBufferMemory",
    "CombinedMemory",
    "ConversationStringBufferMemory",
]
