import pytest
from unittest.mock import patch

from outreachforge.agents.search_agent import get_search_tools, SearchAgent
from outreachforge.agents.ner_agent import NERAgent
from outreachforge.agents.sales_agent import SalesAgent
from outreachforge.agents.lead_sales_agent import LeadSalesAgent
from outreachforge.agents.email_writer_agent import EmailWriterAgent


def test_search_agent_tool_initialization(monkeypatch):
    class DummyTool:
        def __init__(self, api_key):
            self.api_key = api_key

    monkeypatch.setenv("SERPER_API_KEY", "test")
    with patch("outreachforge.agents.search_agent.SerperDevTool", DummyTool):
        tool = get_search_tools()
        assert tool is not None


def test_search_agent_create_agent(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "test")
    with patch("outreachforge.agents.search_agent.SerperDevTool"):
        agent = SearchAgent().create_agent()
        assert agent is not None


def test_ner_agent_tools():
    agent = NERAgent()
    tools = agent.require_tools()
    assert len(tools) == 2


def test_sales_agent_llm(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    with patch("outreachforge.utils.ChatGroq") as MockLLM:
        MockLLM.return_value = object()
        agent = SalesAgent().create_agent()
        assert agent is not None


def test_lead_sales_agent_llm(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    with patch("outreachforge.utils.ChatGroq") as MockLLM:
        MockLLM.return_value = object()
        agent = LeadSalesAgent().create_agent()
        assert agent is not None


def test_email_writer_agent_llm(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    with patch("outreachforge.utils.ChatGroq") as MockLLM:
        MockLLM.return_value = object()
        agent = EmailWriterAgent().create_agent()
        assert agent is not None
