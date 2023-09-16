from __future__ import annotations

from typing import TYPE_CHECKING, List

from langchaincoexpert.agents.agent_toolkits.base import BaseToolkit
from langchaincoexpert.pydantic_v1 import Field
from langchaincoexpert.tools import BaseTool
from langchaincoexpert.tools.office365.create_draft_message import O365CreateDraftMessage
from langchaincoexpert.tools.office365.events_search import O365SearchEvents
from langchaincoexpert.tools.office365.messages_search import O365SearchEmails
from langchaincoexpert.tools.office365.send_event import O365SendEvent
from langchaincoexpert.tools.office365.send_message import O365SendMessage
from langchaincoexpert.tools.office365.utils import authenticate

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
