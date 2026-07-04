from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Lead
from .schemas import LeadCreate
from .logger import log


def get_lead_by_email(db: Session, email: str) -> Optional[Lead]:
    return db.query(Lead).filter(Lead.contact_email == email).first()


def get_lead_by_name_company(db: Session, lead_name: str, company: Optional[str]) -> Optional[Lead]:
    query = db.query(Lead).filter(Lead.lead_name == lead_name)
    if company:
        query = query.filter(Lead.company == company)
    return query.first()


def create_or_update_lead(payload: LeadCreate) -> Lead:
    db = SessionLocal()
    try:
        existing = None
        if payload.contact_email:
            existing = get_lead_by_email(db, payload.contact_email)
        if existing is None:
            existing = get_lead_by_name_company(db, payload.lead_name, payload.company)

        if existing:
            for field, value in payload.model_dump(exclude_none=True).items():
                setattr(existing, field, value)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            log("lead_updated", lead_id=existing.id, lead_name=existing.lead_name)
            return existing

        lead = Lead(
            lead_name=payload.lead_name,
            company=payload.company,
            industry=payload.industry,
            key_decision_maker=payload.key_decision_maker,
            position=payload.position,
            contact_email=payload.contact_email,
            source=payload.source,
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        log("lead_created", lead_id=lead.id, lead_name=lead.lead_name)
        return lead
    except IntegrityError:
        db.rollback()
        existing = get_lead_by_email(db, payload.contact_email) if payload.contact_email else None
        if not existing:
            existing = get_lead_by_name_company(db, payload.lead_name, payload.company)
        if existing:
            return existing
        raise
    finally:
        db.close()


def list_leads(limit: int = 100) -> list[Lead]:
    db = SessionLocal()
    try:
        return db.query(Lead).order_by(Lead.updated_at.desc()).limit(limit).all()
    finally:
        db.close()
