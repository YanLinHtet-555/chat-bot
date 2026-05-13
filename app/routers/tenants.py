import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Tenant
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse, status_code=201)
async def create_tenant(payload: TenantCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Tenant).where(Tenant.slug == payload.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")
    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.get("", response_model=list[TenantResponse])
async def list_tenants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
    return result.scalars().all()


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: uuid.UUID, payload: TenantUpdate, db: AsyncSession = Depends(get_db)):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(tenant, field, value)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant(tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    await db.delete(tenant)
    await db.commit()
