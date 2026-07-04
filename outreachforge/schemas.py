from pydantic import BaseModel, EmailStr
from typing import Literal, Optional


class LeadCreate(BaseModel):
    lead_name: str
    company: Optional[str] = None
    industry: Optional[str] = None
    key_decision_maker: Optional[str] = None
    position: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    source: Optional[str] = None


class LeadRead(BaseModel):
    id: int
    lead_name: str
    company: Optional[str] = None
    industry: Optional[str] = None
    key_decision_maker: Optional[str] = None
    position: Optional[str] = None
    contact_email: Optional[str] = None
    source: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True


class CampaignRequest(BaseModel):
    lead_name: str
    industry: str
    key_decision_maker: str
    position: str
    milestone: str
    contact_email: Optional[EmailStr] = None
    source: Optional[str] = None
