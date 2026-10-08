from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.db_models import SesionVerificacion
from app.models.enums import EstadoSesion, ResultadoVerificacion, RolUsuario
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService


def _login(client, correo, password):
    response = client.post("/auth/login", json={"correo": correo, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_resumen_uso_agrega_sesiones_sin_datos_personales(db_session):
    db_session.add_all([
        SesionVerificacion(estado=EstadoSesion.COMPLETADA, resultado=ResultadoVerificacion.IDENTIDAD_VERIFICADA,
                           confianza_facial=0.9, prueba_vida_superada=True),
        SesionVerificacion(estado=EstadoSesion.COMPLETADA, resultado=ResultadoVerificacion.ROSTRO_NO_COINCIDENTE,
                           confianza_facial=0.5, prueba_vida_superada=False),
        SesionVerificacion(),
    ])
    db_session.commit()

    resumen = DashboardService(db_session).resumen_uso(dias=7)

    assert resumen["totales"]["sesiones"] == 3
    assert resumen["totales"]["sesiones_en_curso"] == 1
    assert resumen["tasas"]["aprobacion"] == 0.5
    assert resumen["tasas"]["prueba_vida_superada"] == 0.5
    assert resumen["tasas"]["confianza_facial_promedio"] == 0.7
    assert resumen["sesiones_por_resultado"] == {"IDENTIDAD_VERIFICADA": 1, "ROSTRO_NO_COINCIDENTE": 1}
    assert len(resumen["sesiones_por_dia"]) == 7
    assert resumen["sesiones_por_dia"][-1]["sesiones"] == 3


def test_resumen_uso_vacio_no_divide_por_cero(db_session):
    resumen = DashboardService(db_session).resumen_uso()
    assert resumen["totales"]["sesiones"] == 0
    assert resumen["tasas"] == {"aprobacion": None, "prueba_vida_superada": None, "confianza_facial_promedio": None}


def test_dashboard_restringido_a_administracion_y_auditoria(db_session):
    AuthService(db_session).create_user("Operador", "operator@example.test", "clave", RolUsuario.OPERADOR)
    AuthService(db_session).create_user("Admin", "admin@example.test", "clave", RolUsuario.ADMINISTRADOR)
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as client:
            assert client.get("/dashboard/uso").status_code == 401
            assert client.get("/dashboard/uso", headers=_login(client, "operator@example.test", "clave")).status_code == 403
            respuesta = client.get("/dashboard/uso", headers=_login(client, "admin@example.test", "clave"))
            assert respuesta.status_code == 200
            assert respuesta.json()["usuarios_por_rol"] == {"ADMINISTRADOR": 1, "OPERADOR": 1}
            assert "admin@example.test" not in respuesta.text
    finally:
        app.dependency_overrides.clear()
