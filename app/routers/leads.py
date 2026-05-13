import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    lead = Lead(**payload.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("", response_model=list[LeadResponse])
async def list_leads(tenant_id: uuid.UUID, status: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Lead).where(Lead.tenant_id == tenant_id)
    if status:
        query = query.where(Lead.status == status)
    result = await db.execute(query.order_by(Lead.created_at.desc()))
    return result.scalars().all()


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: uuid.UUID, payload: LeadUpdate, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(lead, field, value)
    await db.commit()
    await db.refresh(lead)
    return lead
