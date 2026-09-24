"""Endpoints de credenciales de prueba QR/RFID (RF-03, RF-04, RN-04)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import schemas
from app.services.credencial_service import CredencialService
from app.services.errors import CredencialNoRegistradaError

router = APIRouter(prefix="/credenciales", tags=["Credenciales QR/RFID"])


@router.post("", response_model=schemas.CredencialRespuesta, status_code=201)
def emitir_credencial(datos: schemas.CredencialCrear, db: Session = Depends(get_db)):
    return CredencialService(db).emitir(datos)


@router.get("", response_model=list[schemas.CredencialRespuesta])
def listar_credenciales(db: Session = Depends(get_db)):
    """Todas las credenciales emitidas, con su estado actual (RF-18)."""
    return CredencialService(db).listar()


@router.get("/{codigo}", response_model=schemas.CredencialRespuesta)
def leer_credencial(codigo: str, db: Session = Depends(get_db)):
    try:
        return CredencialService(db).leer(codigo)
    except CredencialNoRegistradaError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{id_credencial}/revocar", response_model=schemas.CredencialRespuesta)
def revocar_credencial(id_credencial: str, db: Session = Depends(get_db)):
    try:
        return CredencialService(db).revocar(id_credencial)
    except CredencialNoRegistradaError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{codigo}/qr")
def obtener_imagen_qr(codigo: str, db: Session = Depends(get_db)):
    servicio = CredencialService(db)
    try:
        credencial = servicio.leer(codigo)
    except CredencialNoRegistradaError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    imagen = servicio.generar_imagen_qr(credencial)
    return Response(content=imagen, media_type="image/png")
