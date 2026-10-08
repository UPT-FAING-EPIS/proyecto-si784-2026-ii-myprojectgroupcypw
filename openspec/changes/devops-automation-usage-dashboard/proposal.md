# Automatización DevOps y dashboard de utilización

## Why

La evaluación del curso exige automatizaciones en GitHub que el repositorio no
tenía: infraestructura Terraform con reporte de pruebas y costos, análisis
SonarQube, Semgrep y Snyk con reportes, release con despliegue, documentación
generada en el README y en GitHub Pages, y un dashboard de utilización.

## What Changes

- Añadir `infra/terraform` (Azure App Service con contenedores) con pruebas
  `terraform test` sobre proveedores simulados y un workflow con reporte de
  pruebas, costos Infracost y aprovisionamiento manual.
- Añadir workflows de SonarQube, Semgrep/Snyk, release/despliegue, README
  automático y GitHub Pages; los que requieren cuentas externas se omiten con
  aviso si falta el secreto.
- Añadir `GET /dashboard/uso` (ADMINISTRADOR o AUDITOR) con métricas agregadas
  sin datos personales y la página `frontend/dashboard.html`.
- Ejecutar las imágenes Docker con un usuario sin privilegios.
- No cambia el esquema de datos ni la CI existente (`ci.yml`).
