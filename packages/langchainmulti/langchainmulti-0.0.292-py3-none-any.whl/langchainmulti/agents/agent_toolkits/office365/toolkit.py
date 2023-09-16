from __future__ import annotations

from typing import TYPE_CHECKING, List

from langchainmulti.agents.agent_toolkits.base import BaseToolkit
from langchainmulti.pydantic_v1 import Field
from langchainmulti.tools import BaseTool
from langchainmulti.tools.office365.create_draft_message import O365CreateDraftMessage
from langchainmulti.tools.office365.events_search import O365SearchEvents
from langchainmulti.tools.office365.messages_search import O365SearchEmails
from langchainmulti.tools.office365.send_event import O365SendEvent
from langchainmulti.tools.office365.send_message import O365SendMessage
from langchainmulti.tools.office365.utils import authenticate

if TYPE_CHECKING:
    from O365 import Account


class O365Toolkit(BaseToolkit):
    """Toolkit for interacting with Office 365."""

    account: Account = Field(default_factory=authenticate)

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            O365SearchEvents(),
            O365CreateDraftMessage(),
            O365SearchEmails(),
            O365SendEvent(),
            O365SendMessage(),
        ]
