"""Endpoints del Simulador de Identidad (RF-01, RF-02, RF-19)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import schemas
from app.services.consentimiento_service import ConsentimientoService
from app.services.errors import ConsentimientoRequeridoError, IdentidadNoEncontradaError
from app.services.identidad_service import IdentidadService

router = APIRouter(prefix="/identidades", tags=["Simulador de Identidad"])


@router.post("/consentimientos", status_code=201)
def otorgar_consentimiento(datos: schemas.ConsentimientoCrear, db: Session = Depends(get_db)):
    ConsentimientoService(db).otorgar(datos)
    return {"mensaje": "Consentimiento biométrico registrado.", "id_participante": datos.id_participante}


@router.post("", response_model=schemas.IdentidadRespuesta, status_code=201)
def registrar_identidad(
    nombre_ficticio: str = Form(...),
    documento_ficticio: str = Form(...),
    id_participante: str = Form(...),
    confirmo_dato_ficticio: bool = Form(...),
    imagen_referencia: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    datos = schemas.IdentidadCrear(
        nombre_ficticio=nombre_ficticio,
        documento_ficticio=documento_ficticio,
        id_participante=id_participante,
        confirmo_dato_ficticio=confirmo_dato_ficticio,
    )
    try:
        imagen_bytes = imagen_referencia.file.read()
        identidad = IdentidadService(db).registrar(datos, imagen_bytes)
    except ConsentimientoRequeridoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return identidad


@router.get("", response_model=list[schemas.IdentidadRespuesta])
def listar_identidades(db: Session = Depends(get_db)):
    """Padrón completo de identidades ficticias registradas (RF-17)."""
    return IdentidadService(db).listar()


@router.get("/{id_identidad}", response_model=schemas.IdentidadRespuesta)
def consultar_identidad(id_identidad: str, db: Session = Depends(get_db)):
    try:
        return IdentidadService(db).consultar(id_identidad)
    except IdentidadNoEncontradaError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{id_identidad}", response_model=schemas.IdentidadRespuesta)
def actualizar_identidad(
    id_identidad: str,
    datos: schemas.IdentidadActualizar,
    db: Session = Depends(get_db),
):
    """Corrige el nombre o el documento ficticio (RF-19)."""
    try:
        return IdentidadService(db).actualizar(id_identidad, datos)
    except IdentidadNoEncontradaError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{id_identidad}/estado", response_model=schemas.IdentidadRespuesta)
def cambiar_estado_identidad(
    id_identidad: str,
    datos: schemas.CambioEstadoIdentidad,
    db: Session = Depends(get_db),
):
    """Activa o bloquea una identidad por decisión administrativa (RF-20).

    La reactivación permite devolver al padrón una identidad bloqueada
    automáticamente por acumular intentos fallidos (RN-05).
    """
    try:
        return IdentidadService(db).cambiar_estado(id_identidad, datos.estado)
    except IdentidadNoEncontradaError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
