from crewai import Agent
from crewai_tools import BaseTool
from .config import GROQ_API_KEY
from langchain_groq import ChatGroq


def get_llm():
    return ChatGroq(api_key=GROQ_API_KEY, model="mixtral-8x7b-32768")


class SalesAgents:
    def __init__(self):
        self.llm = get_llm()

    def sales_rep_agent(self) -> Agent:
        return Agent(
            role="Sales Representative",
            goal="Identify high-value leads that match our ideal customer profile",
            backstory=(
                "As a key member of the dynamic sales team at OutreachForge, your mission is to navigate the construction and "
                "estimating sectors to uncover promising leads. Leverage market data, customer signals, and industry insights "
                "to identify opportunities that align with our outreach strategy."
            ),
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            max_iter=2,
        )

    def lead_sales_rep_agent(self) -> Agent:
        return Agent(
            role="Lead Sales Representative",
            goal="Nurture leads with personalized, compelling communications",
            backstory=(
                "Within OutreachForge's sales team, you are the connection between prospects and our outreach solutions. "
                "Your role is to create tailored, engaging communications that demonstrate an understanding of client needs and drive response."
            ),
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            max_iter=2,
        )
