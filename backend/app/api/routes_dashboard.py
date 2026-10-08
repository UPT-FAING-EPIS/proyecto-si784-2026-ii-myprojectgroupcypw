"""Endpoint del dashboard de utilización del producto (solo lectura)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.auth import require_roles
from app.core.database import get_db
from app.models.enums import RolUsuario
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard", tags=["Dashboard de utilización"],
    dependencies=[Depends(require_roles(RolUsuario.ADMINISTRADOR, RolUsuario.AUDITOR))],
)


@router.get("/uso")
def resumen_uso(dias: int = Query(14, ge=1, le=90), db: Session = Depends(get_db)):
    """Métricas agregadas de uso; no incluye datos personales."""
    return DashboardService(db).resumen_uso(dias)
