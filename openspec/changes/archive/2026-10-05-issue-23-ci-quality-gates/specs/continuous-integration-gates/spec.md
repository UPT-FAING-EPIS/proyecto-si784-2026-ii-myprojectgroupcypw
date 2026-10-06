## ADDED Requirements

### Requirement: Pull request quality gates

El repositorio SHALL ejecutar en cada pull request y en cada push a main las
pruebas backend, la validación OpenSpec estricta, la revisión de enlaces
Markdown locales y la validación de Docker Compose.

#### Scenario: Pull request runs the gates

- **WHEN** se abre o actualiza un pull request
- **THEN** GitHub Actions ejecuta los gates y reporta su estado en el pull request

### Requirement: Actionable failure evidence

Cada gate SHALL nombrar el comando que ejecuta y el gate de pruebas SHALL
publicar su reporte como artefacto, también cuando falle.

#### Scenario: A backend test fails

- **WHEN** una prueba de pytest falla en CI
- **THEN** el paso fallido muestra el comando y el reporte JUnit queda disponible como artefacto

### Requirement: No runtime data in version control

CI SHALL fallar si se versionan datos runtime, entornos virtuales, archivos
`.env` o bases SQLite, y no SHALL descargar modelos ni biometría real.

#### Scenario: A SQLite database is committed

- **WHEN** un cambio agrega un archivo `.db` o contenido de `backend/data/`
- **THEN** el gate de datos runtime falla y lista los archivos afectados
