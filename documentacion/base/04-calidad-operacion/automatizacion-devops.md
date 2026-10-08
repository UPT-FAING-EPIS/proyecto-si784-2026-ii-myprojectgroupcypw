# Automatización DevOps, calidad y despliegue

Workflows de GitHub Actions que complementan la CI mínima
([ci.yml](../../../.github/workflows/ci.yml)) sin modificarla. Los que dependen de
una cuenta externa se omiten con un aviso cuando falta su secreto, de modo que
nunca bloquean un pull request por configuración ausente.

| Workflow | Disparo | Qué produce | Configuración requerida |
| --- | --- | --- | --- |
| [infraestructura-terraform.yml](../../../.github/workflows/infraestructura-terraform.yml) | PR/push en `infra/terraform`, manual | `terraform test` con proveedores simulados y reporte de pruebas; reporte de costos Infracost; `plan`/`apply`/`destroy` manual en Azure | `INFRACOST_API_KEY` (costos); `AZURE_CREDENTIALS` y opcionalmente `TFSTATE_*`, `TF_USUARIOS_DEMO` (aprovisionar) |
| [sonarqube.yml](../../../.github/workflows/sonarqube.yml) | PR, push a main | Análisis SonarQube Cloud con cobertura y reporte de Bugs, Vulnerabilities y Security Hotspots | `SONAR_TOKEN`; variables `SONAR_ORGANIZATION`, `SONAR_PROJECT_KEY` si difieren |
| [seguridad-semgrep-snyk.yml](../../../.github/workflows/seguridad-semgrep-snyk.yml) | PR, push a main | Reportes Semgrep (sin cuenta) y Snyk (dependencias y código) | `SNYK_TOKEN` para Snyk |
| [release-despliegue.yml](../../../.github/workflows/release-despliegue.yml) | etiqueta `vX.Y.Z`, manual | Pruebas, imágenes en GHCR, GitHub Release y despliegue en las Web Apps | `AZURE_CREDENTIALS`; variables `AZURE_WEBAPP_BACKEND`, `AZURE_WEBAPP_FRONTEND`, `NOTARYVERIFY_API_URL` |
| [documentacion-readme.yml](../../../.github/workflows/documentacion-readme.yml) | push a main en `backend/app`, PR (comprobación) | Sección automática del README: diccionario de datos y diagramas ER, de clases, de componentes y de despliegue | Ninguna |
| [documentacion-pages.yml](../../../.github/workflows/documentacion-pages.yml) | push a main en `backend/app`, manual | Documentación técnica pdoc (módulos, clases, métodos y propiedades) en GitHub Pages | Settings → Pages → Source: GitHub Actions |

## Criterios de superación

- Terraform: `fmt`, `validate` y todas las pruebas de
  [infraestructura.tftest.hcl](../../../infra/terraform/tests/infraestructura.tftest.hcl) en verde.
- SonarQube: Quality Gate `OK`; el reporte marca cada categoría con 0 abiertos como superada.
- Semgrep: sin hallazgos de severidad `ERROR`. Snyk: sin hallazgos `high` o `critical`.

Comprobación local de Semgrep (resultado al crear los workflows: 0 `ERROR`,
49 `WARNING` por acciones referenciadas por etiqueta y no por SHA):

```bash
semgrep scan --config p/python --config p/javascript --config p/secrets \
  --config p/dockerfile --config p/github-actions --metrics=off --json --output semgrep.json
python .github/scripts/reporte_seguridad.py semgrep semgrep.json semgrep-reporte.md
```

## Infraestructura en Azure

[infra/terraform](../../../infra/terraform/main.tf) crea un Resource Group, un App
Service Plan Linux (`B1` por defecto, `F1` gratuito) en `canadacentral` (la
suscripción Azure for Students solo permite `canadacentral`, `chilecentral`,
`mexicocentral`, `northcentralus` y `westus`; se elige con la entrada `ubicacion`
del workflow) y dos Web Apps de
contenedor: backend en el puerto 8000 con healthcheck `/salud`, datos en el
almacenamiento persistente `/home/data` y CORS limitado a la URL del frontend;
frontend en el puerto 5500. Ambos exigen HTTPS y TLS 1.2 y deshabilitan FTP.

Pasos para el primer despliegue:

1. Crear un service principal con rol Contributor y guardar su JSON en el
   secreto `AZURE_CREDENTIALS`.
2. Opcional: crear una cuenta de almacenamiento para el estado y definir
   `TFSTATE_RESOURCE_GROUP`, `TFSTATE_STORAGE_ACCOUNT` y `TFSTATE_CONTAINER`.
3. Ejecutar *Infraestructura (Terraform)* manualmente con `accion=apply` y copiar
   las salidas a las variables `AZURE_WEBAPP_BACKEND`, `AZURE_WEBAPP_FRONTEND` y
   `NOTARYVERIFY_API_URL`.
4. Publicar una etiqueta (`git tag v1.0.0 && git push origin v1.0.0`). En GHCR,
   marcar los paquetes `-backend` y `-frontend` como públicos para que App
   Service pueda descargarlos sin credenciales.
5. Al terminar la demostración, ejecutar el workflow con `accion=destroy`.

El secreto opcional `TF_USUARIOS_DEMO` (JSON con `operador_correo`,
`operador_password`, `admin_correo` y `admin_password`) crea usuarios ficticios
al arrancar. Sus valores quedan en el estado de Terraform y en la configuración
de la Web App: usar solo claves de demostración.

## Compatibilidad

- Las imágenes Docker se ejecutan con el usuario sin privilegios
  `notaryverify` (UID 10001). Un volumen `notaryverify-data` creado antes de este
  cambio pertenece a root: recrearlo con `docker compose down -v` (borra los
  datos runtime locales de demostración).
- La sección del README entre los marcadores `AUTODOC` se regenera: no editarla a mano.
- El dashboard (`GET /dashboard/uso`, `frontend/dashboard.html`) es de solo
  lectura y no cambia el esquema de datos.
