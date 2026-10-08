## ADDED Requirements

### Requirement: Aggregated usage metrics

El backend SHALL exponer `GET /dashboard/uso` con totales, tasas y conteos
agregados de la utilización del producto, y sesiones por día en un periodo de
1 a 90 días, sin incluir nombres, documentos, correos, códigos de credencial ni
identificadores de personas.

#### Scenario: Administrator requests usage metrics

- **WHEN** un ADMINISTRADOR o AUDITOR autenticado consulta `/dashboard/uso`
- **THEN** recibe 200 con métricas agregadas y ningún dato personal

#### Scenario: Empty database

- **WHEN** no existen sesiones de verificación
- **THEN** los totales son cero y las tasas son nulas, sin error

### Requirement: Dashboard access restricted by role

El endpoint del dashboard SHALL requerir autenticación y los roles
ADMINISTRADOR o AUDITOR.

#### Scenario: Operator requests the dashboard

- **WHEN** un OPERADOR consulta `/dashboard/uso`
- **THEN** recibe 403 `AUTHORIZATION_REQUIRED`
