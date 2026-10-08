"""Métricas agregadas de utilización del producto (dashboard).

Solo lectura: cuenta registros existentes y no expone nombres, documentos,
correos, imágenes ni identificadores de personas.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.db_models import (
    AlertaIntentosFallidos, Credencial, DocumentoVerificado, EventoAuditoria,
    IdentidadSimulada, SesionVerificacion, TramiteSimulado, Usuario,
)
from app.models.enums import EstadoCredencial, EstadoSesion, ResultadoVerificacion


def _conteo_por(db: Session, columna) -> dict[str, int]:
    return {str(clave): total for clave, total in db.query(columna, func.count()).group_by(columna).all() if clave}


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def resumen_uso(self, dias: int = 14) -> dict:
        db = self.db
        total_sesiones = db.query(func.count(SesionVerificacion.id)).scalar() or 0
        por_resultado = _conteo_por(db, SesionVerificacion.resultado)
        aprobadas = por_resultado.get(ResultadoVerificacion.IDENTIDAD_VERIFICADA, 0)
        con_resultado = sum(por_resultado.values())
        vida_total = db.query(func.count(SesionVerificacion.id)).filter(
            SesionVerificacion.prueba_vida_superada.is_not(None)
        ).scalar() or 0
        vida_ok = db.query(func.count(SesionVerificacion.id)).filter(
            SesionVerificacion.prueba_vida_superada.is_(True)
        ).scalar() or 0
        confianza = db.query(func.avg(SesionVerificacion.confianza_facial)).scalar()

        return {
            "totales": {
                "identidades": db.query(func.count(IdentidadSimulada.id)).scalar() or 0,
                "credenciales_activas": db.query(func.count(Credencial.id)).filter(
                    Credencial.estado == EstadoCredencial.ACTIVA
                ).scalar() or 0,
                "sesiones": total_sesiones,
                "sesiones_en_curso": db.query(func.count(SesionVerificacion.id)).filter(
                    SesionVerificacion.estado == EstadoSesion.EN_CURSO
                ).scalar() or 0,
                "documentos": db.query(func.count(DocumentoVerificado.id)).scalar() or 0,
                "eventos_auditoria": db.query(func.count(EventoAuditoria.id)).scalar() or 0,
                "alertas_activas": db.query(func.count(AlertaIntentosFallidos.id)).filter(
                    AlertaIntentosFallidos.fecha_resolucion.is_(None)
                ).scalar() or 0,
            },
            "tasas": {
                "aprobacion": round(aprobadas / con_resultado, 4) if con_resultado else None,
                "prueba_vida_superada": round(vida_ok / vida_total, 4) if vida_total else None,
                "confianza_facial_promedio": round(float(confianza), 4) if confianza is not None else None,
            },
            "sesiones_por_estado": _conteo_por(db, SesionVerificacion.estado),
            "sesiones_por_resultado": por_resultado,
            "tramites_por_estado": _conteo_por(db, TramiteSimulado.estado),
            "credenciales_por_tipo": _conteo_por(db, Credencial.tipo),
            "usuarios_por_rol": _conteo_por(db, Usuario.rol),
            "sesiones_por_dia": self._sesiones_por_dia(dias),
        }

    def _sesiones_por_dia(self, dias: int) -> list[dict]:
        hoy = datetime.now(timezone.utc).replace(tzinfo=None).date()
        inicio = hoy - timedelta(days=dias - 1)
        fechas = self.db.query(SesionVerificacion.fecha_inicio).filter(
            SesionVerificacion.fecha_inicio >= datetime.combine(inicio, datetime.min.time())
        ).all()
        conteo: dict[str, int] = {}
        for (fecha,) in fechas:
            clave = fecha.date().isoformat()
            conteo[clave] = conteo.get(clave, 0) + 1
        return [
            {"fecha": (inicio + timedelta(days=i)).isoformat(), "sesiones": conteo.get((inicio + timedelta(days=i)).isoformat(), 0)}
            for i in range(dias)
        ]
