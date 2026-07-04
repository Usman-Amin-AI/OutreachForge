from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from .db import Base


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        UniqueConstraint("email", name="uq_lead_email"),
        UniqueConstraint("lead_name", "company", name="uq_lead_name_company"),
    )

    id = Column(Integer, primary_key=True, index=True)
    lead_name = Column(String(256), nullable=False)
    company = Column(String(256), nullable=True)
    industry = Column(String(128), nullable=True)
    key_decision_maker = Column(String(128), nullable=True)
    position = Column(String(128), nullable=True)
    contact_email = Column(String(256), nullable=True, index=True)
    source = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
