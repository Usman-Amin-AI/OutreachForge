from crewai import Agent
from crewai_tools import SerperDevTool
from .abstract_agent import BaseAgent
from ..config import settings
from ..errors import ExternalAPIError
from ..resilience import retry, CircuitBreaker, ResilientProxy
from ..logger import log
from ..tracing import get_tracer

_search_circuit = CircuitBreaker(max_failures=3, reset_timeout=120)


def _create_search_tool():
    tracer = get_tracer("outreachforge.search_agent")
    with tracer.start_as_current_span("search_tool.create"):
        try:
            return SerperDevTool(api_key=settings.serper_api_key)
        except Exception as exc:
            raise ExternalAPIError(f"Search tool initialization failed: {exc}") from exc


@retry(max_attempts=3, base_delay=1.0, backoff_factor=2.0)
def get_search_tools():
    tracer = get_tracer("outreachforge.search_agent")
    with tracer.start_as_current_span("search_tool.get"):
        tool = _search_circuit.call(_create_search_tool)
        return ResilientProxy(tool, _search_circuit)


class SearchAgent(BaseAgent):
    def create_agent(self) -> Agent:
        tools = get_search_tools()
        log("search_agent_created")
        return Agent(
            role="Search Agent",
            goal="Gather relevant external market intelligence and lead context.",
            backstory=(
                "You are responsible for acquiring accurate, up-to-date information from public sources and search tools. "
                "Your findings will help downstream agents build personalized outreach and lead narratives."
            ),
            allow_delegation=False,
            verbose=True,
            tools=[tools],
            max_iter=2,
        )

    def require_tools(self) -> list[SerperDevTool]:
        return [get_search_tools()]

    def describe_role(self) -> str:
        return "Search Agent for external intelligence"
