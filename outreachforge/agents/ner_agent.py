from crewai import Agent
from crewai_tools import DirectoryReadTool, FileReadTool
from .abstract_agent import BaseAgent
from ..config import settings


class NERAgent(BaseAgent):
    def create_agent(self) -> Agent:
        return Agent(
            role="NER Agent",
            goal="Extract named entities and contact details from source material.",
            backstory=(
                "You are tasked with identifying people, organizations, locations, and project-related entities from research documents and outreach data. "
                "This information will be used to enrich lead profiles and personalize messages."
            ),
            allow_delegation=False,
            verbose=True,
            tools=self.require_tools(),
            max_iter=2,
        )

    def require_tools(self) -> list:
        return [
            DirectoryReadTool(directory=settings.content_directory),
            FileReadTool(),
        ]

    def describe_role(self) -> str:
        return "Named-entity recognition and lead data extraction"
