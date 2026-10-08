## ADDED Requirements

### Requirement: Tested infrastructure as code with cost report

El repositorio SHALL definir la infraestructura de despliegue en Terraform,
probarla con proveedores simulados en cada cambio y publicar un reporte de las
pruebas superadas y, si hay clave de Infracost, un reporte de costos.

#### Scenario: Infrastructure change in a pull request

- **WHEN** un pull request modifica `infra/terraform`
- **THEN** el workflow ejecuta fmt, validate y terraform test y publica el reporte

### Requirement: Quality and security analysis reports

El repositorio SHALL ejecutar SonarQube, Semgrep y Snyk en pull requests y en
main, y publicar reportes de Bugs, Vulnerabilities, Security Hotspots y
hallazgos; un análisis sin su secreto SHALL omitirse con aviso.

#### Scenario: Semgrep finds an ERROR severity issue

- **WHEN** Semgrep reporta un hallazgo de severidad ERROR
- **THEN** el job falla y el reporte lista el hallazgo

### Requirement: Release and deployment

Una etiqueta `vX.Y.Z` SHALL ejecutar las pruebas, publicar imágenes en GHCR,
crear el GitHub Release y desplegar en la infraestructura aprovisionada cuando
la configuración de Azure existe.

#### Scenario: Azure configuration missing

- **WHEN** se publica una etiqueta sin `AZURE_CREDENTIALS`
- **THEN** se crean imágenes y release, y el despliegue se omite con aviso

### Requirement: Generated documentation

El repositorio SHALL regenerar en el README el diccionario de datos y los
diagramas entidad-relación, de clases, de componentes y de despliegue, y
publicar en GitHub Pages la documentación técnica de módulos, clases, métodos
y propiedades.

#### Scenario: Models change without README update

- **WHEN** un pull request cambia `backend/app` y la sección AUTODOC queda desactualizada
- **THEN** la comprobación del README falla
