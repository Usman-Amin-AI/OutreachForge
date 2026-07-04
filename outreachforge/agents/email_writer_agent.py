from crewai import Agent
from .abstract_agent import BaseAgent
from ..config import settings
from ..utils import get_llm


class EmailWriterAgent(BaseAgent):
    def create_agent(self) -> Agent:
        return Agent(
            role="Email Writer Agent",
            goal="Compose compliant and persuasive outbound email sequences.",
            backstory=(
                "You are the outreach copywriter who turns lead insights into polished email content. "
                "Your output should be respectful, relevant, and designed to increase response rates while maintaining compliance. "
                "Always include a clear unsubscribe footer with the configured unsubscribe and preference center URLs."
            ),
            allow_delegation=False,
            verbose=True,
            llm=get_llm(),
            max_iter=2,
        )

    def require_tools(self) -> list:
        return []

    def describe_role(self) -> str:
        return "Email content generation for outreach campaigns"
