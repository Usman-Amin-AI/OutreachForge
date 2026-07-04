from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    @abstractmethod
    def create_agent(self) -> Any:
        """Return a configured agent instance."""
        raise NotImplementedError

    @abstractmethod
    def require_tools(self) -> list[Any]:
        """Return tools required by the agent."""
        raise NotImplementedError

    @abstractmethod
    def describe_role(self) -> str:
        """Return the agent's role description."""
        raise NotImplementedError
