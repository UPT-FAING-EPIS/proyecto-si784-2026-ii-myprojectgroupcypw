"""Punto de entrada de la API de NotaryVerify (FastAPI)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    routes_auditoria,
    routes_auth,
    routes_credenciales,
    routes_dashboard,
    routes_documentos,
    routes_identidades,
    routes_referencias,
    routes_reglas,
    routes_tramites,
    routes_verificacion,
)
from app.core.database import engine, init_db
from app.core.observabilidad import configurar_logs, estado_salud, registrar_acceso
from app.core.seguridad import CargaInvalidaError, resolver_origenes_cors
from app.services.errors import (
    ConsentimientoRequeridoError, CredencialNoRegistradaError, DocumentoIntegridadInvalidaError,
    DocumentoNoEncontradoError, EvidenciaTramiteNoEncontradaError,
    DesafioPruebaVidaAccionInvalidaError, DesafioPruebaVidaAgotadoError, DesafioPruebaVidaRequeridoError,
    IdentidadNoEncontradaError, IdentidadTemporalmenteBloqueadaError, NotaryVerifyError,
    RostroCalidadInsuficienteError, RostroMultipleDetectadoError, RostroNoDetectadoError,
    SolicitudCambioReferenciaNoEncontradaError, SolicitudCambioReferenciaNoPendienteError,
    SesionNoEncontradaError, SesionNoVigenteError, TramiteNoHabilitadoError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configurar_logs()
    init_db()
    yield


app = FastAPI(
    title="NotaryVerify",
    description=(
        "Prototipo experimental de verificación multicapa de identidad para "
        "trámites notariales. Sistema exclusivamente académico: NO sustituye "
        "a Reniec, al SID-Sunarp ni a la firma digital oficial, y sus "
        "resultados no tienen valor de identificación legal."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Orígenes explícitos por entorno (#22); "*" se rechaza al iniciar.
app.add_middleware(
    CORSMiddleware,
    allow_origins=resolver_origenes_cors(),
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.middleware("http")(registrar_acceso)

app.include_router(routes_identidades.router)
app.include_router(routes_referencias.router)
app.include_router(routes_auth.router)
app.include_router(routes_credenciales.router)
app.include_router(routes_verificacion.router)
app.include_router(routes_reglas.router)
app.include_router(routes_documentos.router)
app.include_router(routes_auditoria.router)
app.include_router(routes_tramites.router)
app.include_router(routes_dashboard.router)

ERROR_CONTRACTS = {
    ConsentimientoRequeridoError: (409, "CONSENT_REQUIRED"),
    IdentidadNoEncontradaError: (404, "IDENTITY_NOT_FOUND"),
    IdentidadTemporalmenteBloqueadaError: (423, "IDENTITY_TEMPORARILY_LOCKED"),
    SolicitudCambioReferenciaNoEncontradaError: (404, "REFERENCE_CHANGE_NOT_FOUND"),
    SolicitudCambioReferenciaNoPendienteError: (409, "REFERENCE_CHANGE_ALREADY_DECIDED"),
    CredencialNoRegistradaError: (404, "CREDENTIAL_NOT_FOUND"),
    SesionNoEncontradaError: (404, "SESSION_NOT_FOUND"),
    SesionNoVigenteError: (409, "SESSION_NOT_ACTIVE"),
    RostroNoDetectadoError: (422, "FACE_NOT_DETECTED"),
    RostroMultipleDetectadoError: (422, "MULTIPLE_FACES_DETECTED"),
    RostroCalidadInsuficienteError: (422, "FACE_QUALITY_INSUFFICIENT"),
    DesafioPruebaVidaRequeridoError: (409, "LIVENESS_CHALLENGE_REQUIRED"),
    DesafioPruebaVidaAgotadoError: (409, "LIVENESS_CHALLENGE_RETRY_LIMIT"),
    DesafioPruebaVidaAccionInvalidaError: (409, "LIVENESS_CHALLENGE_ACTION_MISMATCH"),
    TramiteNoHabilitadoError: (409, "PROCEDURE_NOT_ENABLED"),
    DocumentoNoEncontradoError: (404, "DOCUMENT_NOT_FOUND"),
    DocumentoIntegridadInvalidaError: (409, "DOCUMENT_INTEGRITY_INVALID"),
    EvidenciaTramiteNoEncontradaError: (404, "PROCEDURE_EVIDENCE_NOT_FOUND"),
}


@app.exception_handler(NotaryVerifyError)
async def handle_domain_error(_: Request, exc: NotaryVerifyError):
    status_code, code = ERROR_CONTRACTS.get(type(exc), (400, "DOMAIN_ERROR"))
    return JSONResponse(status_code=status_code, content={"detail": {"code": code, "message": str(exc)}})


@app.exception_handler(CargaInvalidaError)
async def handle_upload_error(_: Request, exc: CargaInvalidaError):
    return JSONResponse(status_code=exc.status_code, content={"detail": {"code": exc.code, "message": str(exc)}})


@app.exception_handler(ValueError)
async def handle_validation_error(_: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": {"code": "INPUT_INVALID", "message": str(exc)}})


@app.get("/", tags=["Estado"])
def estado():
    return {
        "sistema": "NotaryVerify",
        "estado": "operativo",
        "aviso": "Prototipo académico sin valor de identificación legal.",
    }


@app.get("/salud", tags=["Estado"])
def salud():
    """Healthcheck (#25): 200 ok/degradado si la base responde, 503 si no."""
    codigo, cuerpo = estado_salud(engine)
    return JSONResponse(status_code=codigo, content={**cuerpo, "version": app.version})
