"""Base class for Office 365 tools."""
from __future__ import annotations

from typing import TYPE_CHECKING

from langchainmulti.pydantic_v1 import Field
from langchainmulti.tools.base import BaseTool
from langchainmulti.tools.office365.utils import authenticate

if TYPE_CHECKING:
    from O365 import Account


class O365BaseTool(BaseTool):
    """Base class for the Office 365 tools."""

    account: Account = Field(default_factory=authenticate)
    """The account object for the Office 365 account."""
