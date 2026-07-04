from crewai import Agent
from .abstract_agent import BaseAgent
from ..utils import get_llm


class LeadSalesAgent(BaseAgent):
    def create_agent(self) -> Agent:
        return Agent(
            role="Lead Sales Agent",
            goal="Develop personalized, high-conversion outreach for qualified leads.",
            backstory=(
                "You are the senior sales communicator responsible for crafting messages that resonate with decision-makers. "
                "Use lead profile details and industry context to write outreach emails with clear value propositions."
            ),
            allow_delegation=False,
            verbose=True,
            llm=get_llm(),
            max_iter=2,
        )

    def require_tools(self) -> list:
        return []

    def describe_role(self) -> str:
        return "Lead sales outreach authoring"
