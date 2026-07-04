from crewai import Crew
from .tasks import CampaignTasks
from .agents import (
    SearchAgent,
    NERAgent,
    SalesAgent,
    LeadSalesAgent,
    EmailWriterAgent,
)


class OutreachCrew:
    def __init__(self, verbose: int = 1, memory: bool = True):
        self.crew = Crew(
            agents=[
                SearchAgent().create_agent(),
                NERAgent().create_agent(),
                SalesAgent().create_agent(),
                LeadSalesAgent().create_agent(),
                EmailWriterAgent().create_agent(),
            ],
            tasks=[
                CampaignTasks().search_task(),
                CampaignTasks().ner_task(),
                CampaignTasks().lead_profiling_task(),
                CampaignTasks().personalized_outreach_task(),
                CampaignTasks().email_writer_task(),
            ],
            verbose=verbose,
            memory=memory,
        )

    def kickoff(self, inputs: dict) -> str:
        return self.crew.kickoff(inputs=inputs)
