import os
from fastapi.testclient import TestClient
from outreachforge.app import app

client = TestClient(app)


def test_run_campaign_startup_validation(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "test")
    monkeypatch.setenv("GROQ_API_KEY", "test")

    response = client.post(
        "/run-campaign",
        json={
            "lead_name": "Test Lead",
            "industry": "Construction",
            "key_decision_maker": "Jane Doe",
            "position": "CEO",
            "milestone": "Launch"
        },
    )

    assert response.status_code in (200, 500)


def test_run_campaign_payload_validation(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "test")
    monkeypatch.setenv("GROQ_API_KEY", "test")

    response = client.post(
        "/run-campaign",
        json={
            "lead_name": "",
            "industry": "",
        },
    )

    assert response.status_code == 422
