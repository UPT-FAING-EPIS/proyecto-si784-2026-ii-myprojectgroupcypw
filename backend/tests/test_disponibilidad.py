"""Healthcheck, logs mínimos y registro de disponibilidad (#25)."""

import logging

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

import app.main as main_module
import app.services.biometria_service as biometria
import app.services.liveness_service as liveness
from benchmarks import monitor_disponibilidad as monitor
from app.core.observabilidad import estado_salud
from app.main import app


def _modelos(monkeypatch, tmp_path, presentes: bool):
    haar, mediapipe = tmp_path / "haar.xml", tmp_path / "landmarker.task"
    if presentes:
        haar.write_bytes(b"x")
        mediapipe.write_bytes(b"x")
    monkeypatch.setattr(biometria, "RUTA_CASCADA", haar)
    monkeypatch.setattr(liveness, "RUTA_MODELO", mediapipe)


def test_salud_ok_con_base_y_modelos(monkeypatch, tmp_path):
    _modelos(monkeypatch, tmp_path, presentes=True)
    codigo, cuerpo = estado_salud(create_engine("sqlite:///:memory:"))

    assert codigo == 200
    assert cuerpo == {
        "estado": "ok", "base_datos": "ok",
        "modelos_locales": {"haar_cascade": True, "mediapipe_face_landmarker": True},
    }


def test_salud_degradada_sin_modelos_locales(monkeypatch, tmp_path):
    _modelos(monkeypatch, tmp_path, presentes=False)
    codigo, cuerpo = estado_salud(create_engine("sqlite:///:memory:"))

    assert (codigo, cuerpo["estado"]) == (200, "degradado")


def test_salud_no_disponible_sin_base(monkeypatch, tmp_path):
    _modelos(monkeypatch, tmp_path, presentes=True)
    inaccesible = create_engine(f"sqlite:///{(tmp_path / 'no' / 'existe' / 'x.db').as_posix()}")

    codigo, cuerpo = estado_salud(inaccesible)

    assert (codigo, cuerpo["estado"], cuerpo["base_datos"]) == (503, "no_disponible", "error")


def test_endpoint_salud_publico_responde_estado(monkeypatch, tmp_path):
    _modelos(monkeypatch, tmp_path, presentes=True)
    monkeypatch.setattr(main_module, "engine", create_engine("sqlite:///:memory:"))

    respuesta = TestClient(app).get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"
    assert respuesta.json()["version"] == app.version


def test_log_de_acceso_omite_query_cabeceras_y_cuerpo(caplog):
    caplog.set_level(logging.INFO, logger="notaryverify.acceso")
    TestClient(app).post(
        "/auth/login?correo=secreto%40example.test",
        headers={"Authorization": "Bearer token-secreto"},
        json={"correo": "persona@example.test", "password": "clave-secreta"},
    )

    lineas = [r.getMessage() for r in caplog.records if r.name == "notaryverify.acceso"]
    assert lineas and lineas[-1].startswith("POST /auth/login ")
    texto = " ".join(lineas)
    for sensible in ("secreto", "token", "clave", "persona@", "?"):
        assert sensible not in texto


def test_resumen_de_disponibilidad_aplica_umbral():
    registros = [{"codigo": 200, "estado": "ok"}] * 19 + [{"codigo": 0, "estado": "sin_respuesta"}]
    assert monitor.resumir(registros) == {
        "sondeos": 20, "disponibles": 19, "degradados": 0,
        "disponibilidad_pct": 95.0, "umbral_pct": 95.0, "cumple": True,
    }
    assert monitor.resumir(registros[1:] + registros[-1:])["cumple"] is False
    assert monitor.resumir([])["cumple"] is False


def test_monitor_registra_sondeos_en_csv(monkeypatch, tmp_path):
    respuestas = iter([
        {"fecha_utc": "t1", "codigo": 200, "estado": "ok", "latencia_ms": 1.0},
        {"fecha_utc": "t2", "codigo": 503, "estado": "no_disponible", "latencia_ms": 2.0},
    ])
    monkeypatch.setattr(monitor, "sondear", lambda _url: next(respuestas))
    salida = tmp_path / "disponibilidad.csv"

    # Un intervalo positivo y duración cero garantizan exactamente un sondeo:
    # la prueba deja de depender de cuántos ciclos puede ejecutar el host.
    resultado = monitor.monitorear("http://ejemplo/salud", intervalo_s=0.001, duracion_s=0, salida=salida)

    assert resultado["sondeos"] >= 1
    assert salida.read_text(encoding="utf-8").splitlines()[0] == "fecha_utc,codigo,estado,latencia_ms"


def test_sondeo_sin_servidor_cuenta_como_no_disponible():
    registro = monitor.sondear("http://127.0.0.1:9/salud", limite_s=0.5)
    assert (registro["codigo"], registro["estado"]) == (0, "sin_respuesta")
