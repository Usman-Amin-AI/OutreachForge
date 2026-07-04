from crewai import Agent
from .abstract_agent import BaseAgent
from ..utils import get_llm


class SalesAgent(BaseAgent):
    def create_agent(self) -> Agent:
        return Agent(
            role="Sales Agent",
            goal="Identify high-value prospects and qualify them for outreach.",
            backstory=(
                "You are the field-level sales researcher tasked with discovering which leads best fit the OutreachForge ideal customer profile. "
                "Use all available information to rank lead potential and surface win themes."
            ),
            allow_delegation=False,
            verbose=True,
            llm=get_llm(),
            max_iter=2,
        )

    def require_tools(self) -> list:
        return []

    def describe_role(self) -> str:
        return "Sales research and lead qualification"
