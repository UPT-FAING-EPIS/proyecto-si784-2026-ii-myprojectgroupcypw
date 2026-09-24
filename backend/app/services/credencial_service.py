"""Credenciales de prueba QR/RFID (RF-03, RF-04, RN-04).

La lectura de una credencial únicamente permite recuperar el registro que
corresponde verificar; por sí sola nunca aprueba una identidad (ver
``ReglasService``).
"""

from __future__ import annotations

import io
import secrets

import qrcode
from sqlalchemy.orm import Session

from app.models import schemas
from app.models.db_models import Credencial
from app.models.enums import EstadoCredencial
from app.services.errors import CredencialNoRegistradaError


class CredencialService:
    def __init__(self, db: Session):
        self.db = db

    def emitir(self, datos: schemas.CredencialCrear) -> Credencial:
        codigo = f"NV-{secrets.token_hex(6).upper()}"
        credencial = Credencial(
            codigo=codigo,
            tipo=datos.tipo,
            id_identidad=datos.id_identidad,
            estado=EstadoCredencial.ACTIVA,
        )
        self.db.add(credencial)
        self.db.commit()
        self.db.refresh(credencial)
        return credencial

    def listar(self) -> list[Credencial]:
        """Todas las credenciales emitidas, de la más reciente a la más antigua."""
        return (
            self.db.query(Credencial)
            .order_by(Credencial.fecha_emision.desc())
            .all()
        )

    def leer(self, codigo: str) -> Credencial:
        credencial = self.db.query(Credencial).filter(Credencial.codigo == codigo).first()
        if credencial is None:
            raise CredencialNoRegistradaError(f"La credencial '{codigo}' no está registrada.")
        return credencial

    def revocar(self, id_credencial: str) -> Credencial:
        credencial = self.db.get(Credencial, id_credencial)
        if credencial is None:
            raise CredencialNoRegistradaError(f"No existe la credencial '{id_credencial}'.")
        credencial.estado = EstadoCredencial.REVOCADA
        self.db.commit()
        self.db.refresh(credencial)
        return credencial

    def generar_imagen_qr(self, credencial: Credencial) -> bytes:
        imagen = qrcode.make(credencial.codigo)
        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        return buffer.getvalue()
