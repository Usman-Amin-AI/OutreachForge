import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from outreachforge.app import app
from outreachforge.evaluation import evaluate_email_quality

client = TestClient(app)


@pytest.fixture(autouse=True)
def fake_env(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "test")
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", "a" * 44)
    monkeypatch.setenv("UNSUBSCRIBE_URL", "https://example.com/unsubscribe")
    monkeypatch.setenv("PREFERENCE_CENTER_URL", "https://example.com/preferences")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
    monkeypatch.setenv("OTLP_INSECURE", "True")
    yield


def test_evaluate_email_quality_rule_based():
    report = evaluate_email_quality(
        "Hi Jane Doe, I saw your recent work in construction and wanted to connect.",
        {
            "lead_name": "Jane Doe",
            "industry": "Construction",
            "key_decision_maker": "Jane Doe",
            "position": "CEO",
        },
    )
    assert report["personalization_score"] >= 6
    assert report["tone_score"] >= 6


def test_run_campaign_endpoint_rejects_invalid_contact():
    response = client.post(
        "/run-campaign",
        json={
            "lead_name": "Test Lead",
            "industry": "Construction",
            "key_decision_maker": "Jane Doe",
            "position": "CEO",
            "milestone": "Launch",
            "contact_email": "unsubscribe@example.com",
        },
    )
    assert response.status_code == 403


def test_start_campaign_queues_task(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "test")
    monkeypatch.setenv("GROQ_API_KEY", "test")
    with patch("outreachforge.tasks_async.run_campaign_task.delay") as mock_delay:
        mock_delay.return_value.id = "task123"
        response = client.post(
            "/campaigns",
            json={
                "lead_name": "Test Lead",
                "industry": "Construction",
                "key_decision_maker": "Jane Doe",
                "position": "CEO",
                "milestone": "Launch",
                "contact_email": "test@example.com",
            },
        )
        assert response.status_code == 200
        assert response.json()["task_id"] == "task123"
