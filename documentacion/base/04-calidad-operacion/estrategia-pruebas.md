# Estrategia de pruebas

| Nivel | Evidencia | Método |
| --- | --- | --- |
| Unidad e integración backend | pytest | cd backend; python -m pytest -q |
| API | estado y OpenAPI | GET / y GET /docs |
| Frontend | estación, administración, credencial y auditoría | lista de humo manual |
| Contenedores | configuración y endpoints | docker compose config y docker compose up |
| Especificación | artefactos válidos | openspec validate cambio --strict |
| Documentación | enlaces locales existentes | python .github/scripts/check_markdown_links.py |
| Integración continua | gates en cada PR y push a main | .github/workflows/ci.yml |
| Navegadores | Chrome, Edge y Firefox con cámara simulada | python frontend/e2e/recorrido_navegadores.py ([matriz](compatibilidad-disponibilidad.md)) |
| Disponibilidad | /salud y porcentaje frente a 95 % | python -m benchmarks.monitor_disponibilidad |
| Rendimiento | promedio frente a umbral RNF-02/RNF-04 | python -m benchmarks.medir_rendimiento ([protocolo](rendimiento.md)) |

## Evidencia inicial

El 2026-09-27, python -m pytest -q no inició porque faltaba el módulo sqlalchemy en el intérprete global. Se creó backend/.venv, se instalaron requirements.txt y la misma suite completó con 27 pruebas aprobadas y una advertencia de deprecación de Starlette. Las pruebas biométricas pueden requerir red en la primera ejecución.

La revisión de enlaces Markdown completó sin destinos locales faltantes. Docker
Compose resolvió correctamente con docker compose config. El 2026-09-28, con
Docker Desktop activo, se construyeron las imágenes e iniciaron los servicios;
los endpoints /, /openapi.json y el frontend en el puerto 5500 respondieron 200.

La prueba manual en navegador fue completada por el usuario: la cámara fue
detectada, se registró una identidad ficticia, se emitió una credencial y el
flujo terminó con Identidad verificada. La evidencia visual mostró credencial
válida, reconocimiento facial con confianza 0.54 y prueba de vida mediante giro
hacia la izquierda. No se registran datos personales en esta evidencia.

## Recorrido manual MVP por navegador

En Chrome, Edge y Firefox actuales, con una cuenta sintética Operador: iniciar
sesión, ingresar una credencial válida, capturar rostro, completar la acción de
vida y comprobar el resultado. Repetir verificando: credencial inexistente,
rostro no coincidente, liveness fallido, permiso de cámara denegado y API no
disponible. Cada caso debe mostrar un mensaje recuperable, sin exponer datos
sensibles ni administración al Operador. La expiración de sesión y el bloqueo
temporal deben mostrar su causa y permitir reiniciar el flujo.

## Evidencia automatizada M1

`backend/tests/test_mvp_scenarios.py` ejecuta sin cámara, imágenes externas ni
modelos descargados los cuatro escenarios críticos: credencial válida con rostro
y vida aprobados; rostro no coincidente; prueba de vida fallida; y credencial
inexistente. Simula explícitamente los adaptadores biométricos para medir el
flujo, reglas, resultado y persistencia; no sustituye la demostración manual ni
la evaluación experimental posterior.

## Evidencia reproducible de comparación facial M3

`backend/tests/test_biometria_liveness.py` no descarga `lena.jpg` ni ningún
otro recurso. Genera patrones de píxeles sintéticos (sin rostros), simula el
detector y el reconocedor LBPH, y cubre ausencia y multiplicidad de rostros,
resolución mínima, umbral 0.35 y veinte comparaciones consecutivas. La prueba
registra una latencia por comparación con `perf_counter` y exige que cada una
termine antes de tres segundos; es una guarda de regresión técnica, no una
medición de rendimiento de cámara, detección real, precisión ni FPR.

El 2026-10-05 se ejecutaron las veinte comparaciones sintéticas locales sin
red ni modelo descargado. La medición queda automatizada y se repite en cada
ejecución de pytest. La evaluación con rostros de voluntarios consentidos,
ataques controlados y métricas de error corresponde a #26, no a esta prueba.

## Evidencia de prueba de vida M3

`backend/tests/test_liveness_challenges.py` verifica sin cámara, red, vídeo ni
datos personales la emisión aleatoria del desafío, su única repetición,
vencimiento y auditoría. También simula una fotografía impresa y otra mostrada
en pantalla como capturas estáticas que no realizan el giro solicitado; ambas
son rechazadas. Esta evidencia demuestra el comportamiento controlado, no que
MediaPipe determine el material de una imagen ni que resista ataques avanzados.

## Evaluación presencial M7

El [protocolo de evaluación biométrica y prueba de vida](protocolo-evaluacion-experimental.md)
define el consentimiento, códigos anónimos, campos de observación, límites y
eliminación de datos para #26 y #27. El libro local de registro se prepara sin
datos reales y solo se completa presencialmente por el evaluador con voluntarios
consentidos. Hasta que se ejecuten esas observaciones no se declaran precisión,
FPR ni resistencia a presentaciones estáticas.

## Evidencia de auditoría recuperable M4

`backend/tests/test_auditoria_hashchain.py` prueba el evento génesis, la cadena
sin alteraciones, una modificación deliberada, el filtrado por sesión y la
reconstrucción de una sesión con el catálogo mínimo de actor, entidad y payload.
La reconstrucción no devuelve el código de credencial incluido en el detalle
interno de una prueba. `test_authorization.py` verifica además que Operador no
puede consultar la bitácora ni reconstruir una sesión, mientras Administrador
sí. Esta evidencia no declara la cadena como blockchain ni permite editar o
borrar eventos históricos.

## Trámite simulado en la interfaz M5 (#20)

La pantalla de resultado muestra la sección "Trámite simulado SID-Sunarp" solo
cuando la sesión termina en IDENTIDAD_VERIFICADA. El operador registra un
documento ficticio, elige un escenario del simulador y envía el trámite. El
estado del trámite se presenta aparte del veredicto, con evidencia mínima
(trámite, documento, huella SHA-256, fecha) y la indicación de que la
verificación no cambia. Los fallos externos ofrecen reintentar el envío.

`backend/tests/test_sid_simulator.py` cubre por HTTP el recorrido que usa la
interfaz: un fallo SERVICIO_NO_DISPONIBLE seguido de un reintento ENVIADO deja
intactos el resultado y el estado de la sesión; una sesión rechazada recibe
PROCEDURE_NOT_ENABLED sin ruta ni huella del documento. El 2026-10-05 se
reprodujo contra la API local una sesión sintética con TIEMPO_AGOTADO y
reintento ENVIADO.

Recorrido manual pendiente de registrar por el equipo: con cámara, completar
una verificación aprobada, registrar el documento, enviar un escenario de fallo,
reintentar y comprobar que una verificación rechazada no muestra la sección.

## Persistencia configurable M6 (#21)

`backend/tests/test_persistence_config.py` verifica sin red ni datos reales: la
configuración por defecto conserva las rutas del prototipo; las variables vacías
equivalen a no definirlas; la configuración explícita y la derivada de
`NOTARYVERIFY_DATA_DIR`; el rechazo de URL que no son SQLite; la creación de una
tabla aditiva sin tocar datos; la detención con instrucciones ante una columna
faltante; y el reinicio con respaldo. Dos pruebas arrancan la base en un proceso
aparte: una con carpeta explícita y otra con URL inválida. El 2026-10-05 la base
local existente del equipo resultó compatible con la verificación de esquema.

## Privacidad, CORS y cargas M6 (#22)

`backend/tests/test_security_hardening.py` verifica la configuración de
orígenes y límite de carga; que la API responda CORS a la estación local y no a
un origen ajeno; que cargas GIF, con contenido que no coincide con su tipo,
vacías o mayores al límite se rechacen sin crear identidad ni archivo; que una
carga sin credenciales devuelva 401; y que crear un documento exija rol, sesión
existente y contenido en el cuerpo. Incluye una revisión estática de logs y de
secretos versionados. `test_documento_integridad.py` añade que la ruta del
archivo no depende del cliente y que dos documentos de una sesión no se
sobrescriben. El despliegue HTTPS de staging está documentado, no ejecutado.

## Integración continua (#23)

`.github/workflows/ci.yml` se ejecuta en cada pull request, en cada push a main
y manualmente. Cada paso se nombra con el comando que ejecuta, de modo que un
fallo indica qué reproducir localmente. Gates obligatorios:

| Job | Comando | Evidencia |
| --- | --- | --- |
| Pruebas backend (pytest) | `cd backend; python -m pytest -q` con Python 3.11 | artefacto `pytest-report` (JUnit), publicado también si falla |
| OpenSpec y enlaces Markdown | `openspec validate --all --strict` y `python .github/scripts/check_markdown_links.py` | salida del paso con archivo:línea del enlace roto |
| Compose y datos runtime | `docker compose config --quiet` y control de `git ls-files` | lista de archivos runtime versionados, si existen |
| Imagen Docker y healthcheck (#25) | `docker compose up --build -d --wait backend` y `curl /salud` | logs del contenedor, publicados también si falla |

Equivalente local desde la raíz del repositorio:

```
cd backend; python -m pytest -q; cd ..
openspec validate --all --strict
python .github/scripts/check_markdown_links.py
docker compose config --quiet
```

Límites: CI no descarga modelos, no usa cámara, navegador ni biometría real; las
pruebas biométricas usan patrones sintéticos y adaptadores simulados. La fuente
histórica con Git propio no se descarga y sus enlaces no se comprueban. Las
mediciones de rendimiento (#24), compatibilidad de navegador (#25) y evaluación
experimental (#26, #27) no son gates obligatorios.

El 2026-10-05 la ejecución local equivalente aprobó 76 pruebas, 18 elementos
OpenSpec, 115 archivos Markdown sin enlaces rotos y la configuración Compose.
