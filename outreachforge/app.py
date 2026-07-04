import json

from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .crew_manager import OutreachCrew
from .config import settings
from .compliance import validate_contact
from .data_governance import write_audit
from .evaluation import evaluate_email_quality
from .logger import log, error
from .errors import ExternalAPIError, PermanentFailure
from .schemas import CampaignRequest, LeadCreate, LeadRead
from .db import init_db
from .lead_store import create_or_update_lead, list_leads
from .tasks_async import run_campaign_task
from .tracing import configure_tracing

app = FastAPI(title="OutreachForge", version="0.1.0")


class OutreachRequest(BaseModel):
    lead_name: str
    industry: str
    key_decision_maker: str
    position: str
    milestone: str
    contact_email: str | None = None


class EmailQualityRequest(BaseModel):
    email_text: str
    lead_name: str
    industry: str
    key_decision_maker: str
    position: str


def _extract_email_text(result: object) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        for key in ("email", "draft", "output", "result"):  # pragma: no cover
            if key in result and isinstance(result[key], str):
                return result[key]
        return json.dumps(result)
    try:
        return str(result)
    except Exception:
        return ""


@app.on_event("startup")
def startup():
    if not settings.serper_api_key or not settings.groq_api_key:
        raise RuntimeError("SERPER_API_KEY and GROQ_API_KEY must be set in the environment.")
    init_db()
    configure_tracing(app)


@app.post("/run-campaign")
def run_campaign(payload: OutreachRequest):
    if payload.contact_email and not validate_contact(payload.contact_email):
        error("opted_out_contact", contact_email=payload.contact_email)
        raise HTTPException(status_code=403, detail="This contact has opted out of outreach.")

    write_audit("campaign_request", {
        "lead_name": payload.lead_name,
        "industry": payload.industry,
        "key_decision_maker": payload.key_decision_maker,
        "position": payload.position,
        "milestone": payload.milestone,
        "contact_email": payload.contact_email or "",
    })

    crew = OutreachCrew(verbose=1, memory=False)
    try:
        log("run_campaign_started", payload=payload.model_dump())
        result = crew.kickoff(inputs=payload.model_dump())
        log("run_campaign_completed")

        email_text = _extract_email_text(result)
        quality_report = evaluate_email_quality(email_text, payload.model_dump())

        response = {
            "result": result,
            "email_quality_report": quality_report,
            "needs_human_review": quality_report["needs_human_review"],
        }
        if quality_report["needs_human_review"]:
            log("email_quality_flagged", report=quality_report)

        return response
    except ExternalAPIError as exc:
        error("external_api_error", error=str(exc), classification=exc.classification)
        raise HTTPException(status_code=502, detail="External service failure")
    except PermanentFailure as exc:
        error("permanent_failure", error=str(exc), classification=exc.classification)
        raise HTTPException(status_code=500, detail="Permanent failure")
    except Exception as exc:
        error("unknown_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/evaluate-email")
def evaluate_email(payload: EmailQualityRequest):
    audit_payload = {
        "lead_name": payload.lead_name,
        "industry": payload.industry,
        "key_decision_maker": payload.key_decision_maker,
        "position": payload.position,
    }
    write_audit("email_quality_request", audit_payload)
    quality_report = evaluate_email_quality(payload.email_text, audit_payload)
    if quality_report["needs_human_review"]:
        log("email_quality_flagged", report=quality_report)
    return {
        "quality_report": quality_report,
        "needs_human_review": quality_report["needs_human_review"],
    }


@app.post("/leads")
def create_lead(payload: LeadCreate):
    lead = create_or_update_lead(payload)
    return LeadRead.from_orm(lead)


@app.get("/leads")
def get_leads(limit: int = 100):
    leads = list_leads(limit=limit)
    return [LeadRead.from_orm(lead) for lead in leads]


@app.post("/campaigns")
def start_campaign(payload: CampaignRequest):
    if payload.contact_email and not validate_contact(payload.contact_email):
        error("opted_out_contact", contact_email=payload.contact_email)
        raise HTTPException(status_code=403, detail="This contact has opted out of outreach.")

    lead_payload = LeadCreate(
        lead_name=payload.lead_name,
        company=None,
        industry=payload.industry,
        key_decision_maker=payload.key_decision_maker,
        position=payload.position,
        contact_email=payload.contact_email,
        source=payload.source,
    )
    create_or_update_lead(lead_payload)

    task = run_campaign_task.delay(payload.model_dump())
    audit_payload = payload.model_dump()
    audit_payload["task_id"] = task.id
    write_audit("campaign_task_enqueued", audit_payload)
    return {"task_id": task.id, "status": "queued"}


@app.get("/campaigns/{task_id}")
def get_campaign_status(task_id: str):
    result = AsyncResult(task_id, app=run_campaign_task._get_app())
    if result.failed:
        return {"task_id": task_id, "status": "failed", "error": str(result.result)}
    if result.successful():
        return {"task_id": task_id, "status": "completed", "result": result.result}
    return {"task_id": task_id, "status": result.status}
