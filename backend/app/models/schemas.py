"""Esquemas Pydantic (contratos de entrada/salida de la API REST)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConsentimientoCrear(BaseModel):
    id_participante: str
    alcance: str = "Uso del rostro exclusivamente para pruebas académicas de NotaryVerify"


class IdentidadCrear(BaseModel):
    nombre_ficticio: str
    documento_ficticio: str
    id_participante: str
    confirmo_dato_ficticio: bool = Field(
        ..., description="Debe ser true: NotaryVerify no admite datos reales (RN-02)."
    )


class IdentidadRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre_ficticio: str
    documento_ficticio: str
    estado: str
    fecha_registro: datetime


class IdentidadActualizar(BaseModel):
    """Campos corregibles de una identidad. La referencia facial no lo es."""

    nombre_ficticio: str | None = None
    documento_ficticio: str | None = None


class CambioEstadoIdentidad(BaseModel):
    estado: str


class CredencialCrear(BaseModel):
    id_identidad: str
    tipo: str = "QR"


class CredencialRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    codigo: str
    tipo: str
    id_identidad: str
    estado: str
    fecha_emision: datetime


class SesionIniciar(BaseModel):
    codigo_credencial: str
    id_responsable: Optional[str] = None


class SesionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    estado: str
    resultado: Optional[str] = None
    rostro_coincide: Optional[bool] = None
    confianza_facial: Optional[float] = None
    prueba_vida_superada: Optional[bool] = None
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None


class EventoAuditoriaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    id_sesion: Optional[str]
    tipo_evento: str
    hash_evento_anterior: str
    hash_evento_actual: str
    timestamp: datetime
    secuencia: int


class VerificacionCadenaRespuesta(BaseModel):
    valida: bool
    total_eventos: int
    primer_evento_alterado: Optional[str] = None


class DocumentoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    id_sesion: str
    hash_sha256: str
    qr_verificacion: str
    fecha_generacion: datetime


class IntegridadDocumentoRespuesta(BaseModel):
    integro: bool
    hash_esperado: str
    hash_calculado: str


class TramiteRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    id_sesion: str
    estado: str
    fecha: datetime
