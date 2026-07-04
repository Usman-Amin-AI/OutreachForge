import re
from typing import Dict
from .logger import log
from .config import settings


UNSUBSCRIBE_TEMPLATE = (
    "If you no longer wish to receive these emails, please reply with \"unsubscribe\" or visit {unsubscribe_url}. "
    "You can also manage your preferences at {preference_center}."
)

PII_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\+?\d[\d\s\-()]{7,}\d"),
]


def redact_pii(text: str) -> str:
    if not text:
        return text

    redacted = text
    for pattern in PII_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def is_opted_out(contact: str) -> bool:
    if not contact:
        return False
    opt_out_list = {item.strip().lower() for item in settings.opt_out_list.split(",") if item.strip()}
    opted_out = contact.lower().strip() in opt_out_list
    if opted_out:
        log("contact_opted_out", contact=contact)
    return opted_out


def unsubscribe_footer() -> str:
    footer = UNSUBSCRIBE_TEMPLATE.format(
        unsubscribe_url=settings.unsubscribe_url,
        preference_center=settings.preference_center_url,
    )
    log("unsubscribe_footer_generated", unsubscribe_url=settings.unsubscribe_url)
    return footer


def audit_event(action: str, data: Dict[str, str]) -> Dict[str, str]:
    event = {
        "action": action,
        "data": {k: redact_pii(v) for k, v in data.items()},
    }
    log("pii_audit", **event)
    return event
