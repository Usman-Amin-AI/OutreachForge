from crewai import Task
from crewai_tools import DirectoryReadTool, FileReadTool
from .agents import (
    SearchAgent,
    NERAgent,
    SalesAgent,
    LeadSalesAgent,
    EmailWriterAgent,
)
from .config import settings
from .errors import ExternalAPIError
from .logger import log
from .resilience import retry, CircuitBreaker


directory_read_tool = DirectoryReadTool(directory=settings.content_directory)
file_read_tool = FileReadTool()

_search_circuit = CircuitBreaker(max_failures=3, reset_timeout=120)


@retry(max_attempts=3, base_delay=1.0, backoff_factor=2.0)
def get_search_tool():
    try:
        return SearchAgent().require_tools()[0]
    except Exception as exc:
        raise ExternalAPIError(f"Failed to initialize search tool: {exc}") from exc


class CampaignTasks:
    def search_task(self) -> Task:
        log("build_search_task")
        return Task(
            description=(
                "Collect market intelligence and lead context using external search sources for {lead_name}. "
                "Focus on recent projects, company news, and relevant industry signals."
            ),
            expected_output=(
                "A summary of relevant external information about {lead_name}, including recent activity, market positioning, and potential outreach triggers."
            ),
            tools=[get_search_tool()],
            agent=SearchAgent().create_agent(),
        )

    def ner_task(self) -> Task:
        return Task(
            description=(
                "Extract key named entities from research documents and lead content for {lead_name}. "
                "Identify people, companies, projects, locations, and other signals to enrich the lead profile."
            ),
            expected_output=(
                "A structured set of entities and contact details extracted from documents and search findings, ready for outreach personalization."
            ),
            tools=[directory_read_tool, file_read_tool],
            agent=NERAgent().create_agent(),
        )

    def lead_profiling_task(self) -> Task:
        return Task(
            description=(
                "Analyze {lead_name} using gathered intelligence and extracted data to build a detailed lead profile. "
                "Summarize opportunity fit, decision-makers, recent projects, and priority pain points."
            ),
            expected_output=(
                "A lead profile for {lead_name} that includes company background, buyer insights, priority initiatives, and outreach strategy recommendations."
            ),
            tools=[get_search_tool(), directory_read_tool, file_read_tool],
            agent=SalesAgent().create_agent(),
        )

    def personalized_outreach_task(self) -> Task:
        return Task(
            description=(
                "Craft a personalized outreach approach for {lead_name} and their {position}, based on the lead profile and extracted insights. "
                "Highlight value propositions, industry context, and next-step suggestions."
            ),
            expected_output=(
                "A personalized outreach briefing and draft message outline for {key_decision_maker} at {lead_name}."
            ),
            tools=[get_search_tool()],
            agent=LeadSalesAgent().create_agent(),
        )

    def email_writer_task(self) -> Task:
        return Task(
            description=(
                "Compose compliant outbound email copy for the qualified lead at {lead_name}. "
                "The email should be concise, relevant, and tailored to the lead's business situation."
            ),
            expected_output=(
                "A sequence of outbound email drafts with subject lines, body copy, and follow-up suggestions."
            ),
            tools=[],
            agent=EmailWriterAgent().create_agent(),
        )
