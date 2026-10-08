# NotaryVerify

Prototipo académico de verificación multicapa de identidad para trámites notariales simulados. Evalúa credenciales de prueba, identidad simulada, reconocimiento facial local, prueba de vida, reglas de seguridad, integridad documental y auditoría.

> Aviso: NotaryVerify no sustituye a Reniec, SID-Sunarp, firma digital oficial ni procedimientos notariales. Sus resultados no tienen valor de identificación legal. Solo se permiten identidades ficticias y biometría de voluntarios con consentimiento.

## Estado público

- Código fuente, issues, hitos y resultados de CI:
  [repositorio público en GitHub](https://github.com/UPT-FAING-EPIS/proyecto-si784-2026-ii-myprojectgroupcypw).
- El proyecto no tiene una aplicación pública desplegada. La demostración se
  ejecuta localmente mediante las instrucciones de este README o Docker Compose;
  no se debe interpretar la ausencia de una URL pública como una integración con
  servicios institucionales reales.
- M1 a M6 están cerrados y validados por CI. M7 requiere evaluación biométrica
  y de prueba de vida con personas voluntarias y consentimiento; M8 depende de
  esa evidencia y del cierre de trazabilidad. Los pendientes se mantienen
  visibles en las issues #26 a #29.

## MVP

El flujo actual registra una identidad ficticia, emite una credencial QR de prueba, crea una sesión, compara un rostro, solicita una prueba de vida y aplica reglas para emitir un resultado. La evidencia incluye auditoría encadenada, hash SHA-256 de documentos de prueba y trámites simulados.

RFID físico, formato de evaluación biométrica y migraciones formales de SQLite permanecen como decisiones futuras.

## Componentes

- backend/: API FastAPI, SQLAlchemy, SQLite local, OpenCV/MediaPipe y pruebas pytest.
- frontend/: estación de verificación estática y panel administrativo.
- documentacion/: documentación canónica, planificación, operación y fuentes académicas.
- openspec/: propuestas, especificaciones y tareas de cambio.
- AGENTS.md: reglas para personas y agentes.

## Inicio local

### Nativo

1. En backend, crear entorno virtual e instalar requirements.txt.
2. Ejecutar uvicorn app.main:app --reload.
3. En otra terminal, desde frontend, ejecutar python -m http.server 5500.
4. Abrir http://127.0.0.1:5500. La API está en http://127.0.0.1:8000 y Swagger en /docs.

La primera prueba biométrica puede requerir conexión para descargar modelos. El estado runtime se crea en backend/data y no se versiona.

### Docker Compose

Copiar .env.example como .env si se requiere modificar puertos y ejecutar docker compose up --build. La configuración representa solo desarrollo local con SQLite; no crea ni conecta servicios institucionales.

## Documentación y colaboración

Empieza en [documentacion/indice.md](documentacion/indice.md). Consulta [AGENTS.md](AGENTS.md) antes de modificar el repositorio. Los informes académicos históricos están preservados e indexados en [documentacion/academica](documentacion/academica/indice.md).

Para cambios significativos, crear primero una propuesta OpenSpec. El cambio de bootstrap actual es bootstrap-profesional-notaryverify.
