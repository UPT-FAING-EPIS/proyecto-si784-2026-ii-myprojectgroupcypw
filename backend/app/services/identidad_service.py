"""Simulador de Identidad (RF-01, RF-02, RN-02, RN-03).

Representa, exclusivamente con fines académicos, una fuente institucional
externa de información de identidad. Nunca debe contener datos reales de
clientes de una notaría (RN-02): toda identidad registrada es ficticia.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.database import DATA_DIR
from app.models import schemas
from app.models.db_models import IdentidadSimulada
from app.models.enums import EstadoIdentidad
from app.services.auditoria_service import AuditoriaService
from app.services.consentimiento_service import ConsentimientoService
from app.services.errors import ConsentimientoRequeridoError, IdentidadNoEncontradaError

REFERENCIAS_DIR = DATA_DIR / "referencias_faciales"
REFERENCIAS_DIR.mkdir(parents=True, exist_ok=True)


class IdentidadService:
    def __init__(self, db: Session):
        self.db = db
        self.consentimientos = ConsentimientoService(db)

    def registrar(
        self, datos: schemas.IdentidadCrear, imagen_referencia: bytes
    ) -> IdentidadSimulada:
        if not datos.confirmo_dato_ficticio:
            raise ValueError(
                "NotaryVerify solo admite identidades ficticias (RN-02): confirme "
                "explícitamente que los datos no corresponden a una persona real."
            )
        if not self.consentimientos.existe_consentimiento_valido(datos.id_participante):
            raise ConsentimientoRequeridoError(
                f"El participante '{datos.id_participante}' no cuenta con un "
                "consentimiento biométrico vigente (RN-03). Regístrelo antes de "
                "enrolar su rostro."
            )

        identidad = IdentidadSimulada(
            nombre_ficticio=datos.nombre_ficticio,
            documento_ficticio=datos.documento_ficticio,
            id_participante=datos.id_participante,
            referencia_facial_path="",
            estado=EstadoIdentidad.ACTIVA,
        )
        self.db.add(identidad)
        self.db.flush()

        ruta_imagen = REFERENCIAS_DIR / f"{identidad.id}.jpg"
        ruta_imagen.write_bytes(imagen_referencia)
        identidad.referencia_facial_path = str(ruta_imagen)

        self.db.commit()
        self.db.refresh(identidad)
        return identidad

    def listar(self) -> list[IdentidadSimulada]:
        """Todas las identidades registradas, de la más reciente a la más antigua.

        Permite al administrador supervisar el padrón de identidades ficticias
        y, en particular, detectar las que quedaron BLOQUEADAS por acumular
        intentos fallidos (RN-05), estado que de otro modo sería invisible.
        """
        return (
            self.db.query(IdentidadSimulada)
            .order_by(IdentidadSimulada.fecha_registro.desc())
            .all()
        )

    def consultar(self, id_identidad: str) -> IdentidadSimulada:
        identidad = self.db.get(IdentidadSimulada, id_identidad)
        if identidad is None:
            raise IdentidadNoEncontradaError(f"No existe la identidad '{id_identidad}'.")
        return identidad

    def bloquear(self, id_identidad: str) -> IdentidadSimulada:
        """Bloqueo automático por intentos fallidos consecutivos (RN-05)."""
        return self._fijar_estado(id_identidad, EstadoIdentidad.BLOQUEADA, "RN-05")

    def cambiar_estado(self, id_identidad: str, estado: str) -> IdentidadSimulada:
        """Activa o bloquea una identidad por decisión del administrador.

        La reactivación es indispensable: sin ella, una identidad bloqueada
        por la regla RN-05 quedaría inservible de forma permanente y no podría
        volver a participar en las pruebas controladas.
        """
        if estado not in (EstadoIdentidad.ACTIVA, EstadoIdentidad.BLOQUEADA):
            raise ValueError(
                f"Estado no admitido: '{estado}'. Use ACTIVA o BLOQUEADA."
            )
        return self._fijar_estado(id_identidad, estado, "administrador")

    def _fijar_estado(self, id_identidad: str, estado: str, origen: str) -> IdentidadSimulada:
        identidad = self.consultar(id_identidad)
        anterior = identidad.estado
        identidad.estado = estado
        self.db.commit()
        self.db.refresh(identidad)

        # El cambio de estado es una operación crítica y debe quedar en la
        # bitácora encadenada (RN-07).
        if anterior != estado:
            AuditoriaService(self.db).registrar_evento(
                None,
                "IDENTIDAD_CAMBIO_ESTADO",
                {
                    "id_identidad": id_identidad,
                    "estado_anterior": anterior,
                    "estado_nuevo": estado,
                    "origen": origen,
                },
            )
        return identidad

    def actualizar(
        self, id_identidad: str, datos: schemas.IdentidadActualizar
    ) -> IdentidadSimulada:
        """Corrige el nombre o el documento ficticio de una identidad.

        No permite sustituir la referencia facial: cambiar la biometría exige
        un nuevo enrolamiento con su consentimiento correspondiente.
        """
        identidad = self.consultar(id_identidad)
        cambios = {}

        if datos.nombre_ficticio and datos.nombre_ficticio != identidad.nombre_ficticio:
            cambios["nombre_ficticio"] = [identidad.nombre_ficticio, datos.nombre_ficticio]
            identidad.nombre_ficticio = datos.nombre_ficticio

        if datos.documento_ficticio and datos.documento_ficticio != identidad.documento_ficticio:
            duplicada = (
                self.db.query(IdentidadSimulada)
                .filter(IdentidadSimulada.documento_ficticio == datos.documento_ficticio)
                .filter(IdentidadSimulada.id != id_identidad)
                .first()
            )
            if duplicada is not None:
                raise ValueError(
                    f"Ya existe otra identidad con el documento '{datos.documento_ficticio}'."
                )
            cambios["documento_ficticio"] = [identidad.documento_ficticio, datos.documento_ficticio]
            identidad.documento_ficticio = datos.documento_ficticio

        if not cambios:
            return identidad

        self.db.commit()
        self.db.refresh(identidad)
        AuditoriaService(self.db).registrar_evento(
            None,
            "IDENTIDAD_ACTUALIZADA",
            {"id_identidad": id_identidad, "cambios": cambios},
        )
        return identidad

    def referencia_facial_bytes(self, id_identidad: str) -> bytes:
        identidad = self.consultar(id_identidad)
        return Path(identidad.referencia_facial_path).read_bytes()
