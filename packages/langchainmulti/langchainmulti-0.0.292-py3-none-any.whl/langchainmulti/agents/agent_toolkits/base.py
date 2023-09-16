"""Toolkits for agents."""
from abc import ABC, abstractmethod
from typing import List

from langchainmulti.pydantic_v1 import BaseModel
from langchainmulti.tools import BaseTool


class BaseToolkit(BaseModel, ABC):
    """Base Toolkit representing a collection of related tools."""

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
