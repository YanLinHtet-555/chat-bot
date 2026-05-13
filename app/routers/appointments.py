import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(payload: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    appt = Appointment(**payload.model_dump())
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt


@router.get("", response_model=list[AppointmentResponse])
async def list_appointments(tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Appointment)
        .where(Appointment.tenant_id == tenant_id)
        .order_by(Appointment.scheduled_at)
    )
    return result.scalars().all()


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_status(appointment_id: uuid.UUID, status: str, db: AsyncSession = Depends(get_db)):
    appt = await db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if status not in ("pending", "confirmed", "cancelled"):
        raise HTTPException(status_code=400, detail="Invalid status")
    appt.status = status
    await db.commit()
    await db.refresh(appt)
    return appt
