from celery import Celery
from .config import settings
from .crew_manager import OutreachCrew
from .data_governance import write_audit
from .compliance import validate_contact
from .schemas import CampaignRequest

celery_app = Celery(
    "outreachforge",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.task_track_started = True
celery_app.conf.worker_max_tasks_per_child = 100
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.task_default_queue = "outreach_campaigns"


@celery_app.task(name="outreachforge.run_campaign_task")
def run_campaign_task(payload: dict) -> dict:
    campaign = CampaignRequest.model_validate(payload)
    if campaign.contact_email and not validate_contact(campaign.contact_email):
        return {
            "status": "failed",
            "reason": "contact_opted_out",
            "details": "The contact has opted out of outreach.",
        }

    write_audit("campaign_task_started", payload)
    crew = OutreachCrew(verbose=0, memory=False)
    try:
        result = crew.kickoff(inputs=campaign.model_dump())
        write_audit("campaign_task_completed", {"lead_name": campaign.lead_name})
        return {"status": "completed", "result": result}
    except Exception as exc:
        write_audit("campaign_task_failed", {"lead_name": campaign.lead_name, "error": str(exc)})
        return {"status": "failed", "reason": "task_error", "details": str(exc)}
