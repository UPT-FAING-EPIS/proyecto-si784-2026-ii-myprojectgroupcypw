# Integración continua con gates de calidad

## Why

Las verificaciones del proyecto (pytest, OpenSpec, enlaces y Compose) dependían
del entorno local de cada persona. Sin CI, un pull request podía fusionarse sin
evidencia reproducible de que la suite seguía aprobando.

## What Changes

- Añadir `.github/workflows/ci.yml` que se ejecuta en cada pull request y push a main.
- Ejecutar pytest backend con reporte JUnit, validación OpenSpec estricta,
  revisión de enlaces Markdown locales y `docker compose config`.
- Fallar si se versionan datos runtime, entornos virtuales, `.env` o bases SQLite.
- Documentar el equivalente local y los límites de lo que CI no mide.
