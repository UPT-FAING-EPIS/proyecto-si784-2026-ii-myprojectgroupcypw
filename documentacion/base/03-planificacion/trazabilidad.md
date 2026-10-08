# Matriz de trazabilidad ejecutable

Fuente académica: `documentacion/proyecto-si784-2026-ii-myprojectgroupcypw/FD03-Informe-SRS.md`.
Los números de issue son reales y se consultan en `https://github.com/UPT-FAING-EPIS/proyecto-si784-2026-ii-myprojectgroupcypw/issues/<n>`. “Parcial” significa que hay código o pruebas iniciales, no que el requisito esté cerrado.

## Requerimientos funcionales

| Requisito | Issue(s) | Módulo / prueba o evidencia | Estado base |
| --- | --- | --- | --- |
| RF-01 identidad simulada | #4, #5, #10 | `identidad_service`, `test_credencial_flujo` | Parcial |
| RF-02 consultar identidad | #6, #10 | rutas de identidades/credenciales, API smoke | Parcial |
| RF-03 emitir credencial QR/RFID | #10, #11 | `credencial_service`, `test_rfid_simulado` | QR y RFID simulado verificados |
| RF-04 leer credencial | #6, #10, #11 | rutas de credenciales, reglas | Parcial |
| RF-05 capturar y comparar rostro | #18, #24, #26 | `biometria_service`, `test_biometria_liveness`, [protocolo M7](../04-calidad-operacion/protocolo-evaluacion-experimental.md) | Umbral y errores reproducibles verificados; protocolo preparado, evaluación pendiente |
| RF-06 prueba de vida | #14, #24, #27 | `liveness_service`, `test_liveness_challenges`, [protocolo M7](../04-calidad-operacion/protocolo-evaluacion-experimental.md) | Desafío, timeout y negativos controlados verificados; protocolo preparado, evaluación pendiente |
| RF-07 motor de reglas | #10, #13 | `reglas_service`, `test_configurable_rules` | Configuración versionada verificada |
| RF-08 sesión de verificación | #7, #8, #10, #16 | `verificacion_service`, evidencia sesión-documento-trámite | Evidencia recuperable verificada |
| RF-09 hash e integridad documental | #15, #16 | `documento_service`, `test_documento_integridad`, `test_sid_simulator` | Integridad previa al trámite verificada |
| RF-10 QR documental | #15 | servicio documental y consulta planificada | Parcial |
| RF-11 auditoría encadenada | #16, #17 | `auditoria_service`, eventos de asociación, hash chain | Auditoría y reconstrucción autorizada verificadas |
| RF-12 detectar alteración | #17 | `test_auditoria_hashchain` | Alteración y ruptura verificadas |
| RF-13 trámite SID simulado | #16, #19, #20 | `sid_sunarp_service`, `test_sid_simulator`, sección de trámite en `frontend/` | Habilitación, evidencia y recorrido UI verificados (#20) |
| RF-14 escenarios de servicio externo | #19, #20 | rutas de trámites, seis escenarios en `test_sid_simulator` y selector UI | Escenarios, fallo y reintento verificados (#20) |
| RF-15 autenticación | #4, #5 | `test_auth`, `test_authorization` | Verificado M1 |
| RF-16 configurar reglas | #13 | API de reglas, `test_configurable_rules` | Verificado M3 |
| RF-17 consultar bitácora | #5, #17 | rutas de auditoría, reconstrucción y permisos | Verificado M4 |
| RF-18 filtrar sesiones | #7 | historial y filtros planificados | No iniciada |
| RF-19 consentimiento biométrico | #5, #12, #26 | `consentimiento_service`, `test_reference_change`, [protocolo M7](../04-calidad-operacion/protocolo-evaluacion-experimental.md) | Cambio autorizado verificado; protocolo preparado y evaluación en #26 |

## Requerimientos no funcionales

| Requisito | Issue(s) | Evidencia esperada | Estado base |
| --- | --- | --- | --- |
| RNF-01 cuatro pasos/usabilidad | #9, #10 | recorrido UI y `test_mvp_scenarios` | Verificado M1 |
| RNF-02 comparación < 3 s | #18, #24 | `benchmarks/medir_rendimiento.py`, `test_rendimiento`, [rendimiento](../04-calidad-operacion/rendimiento.md) | Benchmark técnico 0,021 s promedio (#24); medición con cámara pendiente |
| RNF-03 disponibilidad 95 % | #23, #25 | `GET /salud`, healthcheck Compose, `monitor_disponibilidad`, `test_disponibilidad` | Healthcheck y registro verificados (#25); periodo de evaluación pendiente |
| RNF-04 flujo < 45 s | #10, #14, #24 | timeout de 20 s; 20 sesiones HTTP medidas en `rendimiento.md` | Costo del sistema 0,10 s promedio (#24); medición con tiempo humano pendiente |
| RNF-05 FPR combinado < 5 % | #18, #26, #27 | [protocolo M7](../04-calidad-operacion/protocolo-evaluacion-experimental.md) y métricas agregadas | #14 no afirma FPR; protocolo preparado, evaluación pendiente |
| RNF-06 autenticación y acceso | #4, #5, #22 | `test_auth`, `test_authorization`, `test_security_hardening` | Verificado M1; CORS, cargas y documentos endurecidos (#22) |
| RNF-07 HTTPS/TLS | #22 | guía de staging en `seguridad.md` | Guía documentada; despliegue HTTPS no ejecutado |
| RNF-08 navegadores vigentes | #9, #25 | `frontend/e2e/recorrido_navegadores.py`, [matriz](../04-calidad-operacion/compatibilidad-disponibilidad.md) | Chrome 154, Edge 154 y Firefox 155: 9/9 escenarios (#25); aprobación con rostro real en #29 |
| RNF-09 mantenibilidad | #6, #21, #23 | capas, documentación, `.github/workflows/ci.yml`, `test_persistence_config` | CI en cada PR (#23); persistencia configurable y reinicio verificado (#21) |
| RNF-10 recuperación de auditoría | #16, #17 | reconstrucción de evidencia, alteración controlada | Verificado M4 |

## Reglas de negocio

| Regla | Issue(s) | Evidencia esperada | Estado base |
| --- | --- | --- | --- |
| RN-01 ningún factor aprueba solo | #10, #13 | catálogo obligatorio y casos de reglas | Verificado M3 |
| RN-02 identidad ficticia | #10, #22, #26 | validación, revisión estática de secretos y [protocolo sin datos reales](../04-calidad-operacion/protocolo-evaluacion-experimental.md) | Controles técnicos verificados (#22); protocolo preparado, evaluación pendiente |
| RN-03 consentimiento previo | #12, #26 | `test_reference_change`, auditoría, [protocolo M7](../04-calidad-operacion/protocolo-evaluacion-experimental.md) | Cambio autorizado verificado; protocolo preparado, evaluación pendiente |
| RN-04 credencial revocada | #6, #10 | prueba de rechazo por revocación | Implementado, por verificar E2E |
| RN-05 intentos fallidos | #8, #10 | `test_temporary_lockout`, auditoría | Verificado M1 |
| RN-06 trámite condicionado | #16, #19, #20 | bloqueo de sesión rechazada y documento ajeno; UI oculta el trámite sin identidad verificada | Verificado en servicio y UI (#20) |
| RN-07 bitácora inmutable | #17 | alteración detectada y acceso restringido | Verificado M4 |
| RN-08 integridad previa a trámite | #15, #16 | documento modificado bloquea trámite | Verificado |
| RN-09 cambio biométrico autorizado | #5, #12 | `test_reference_change`, evento de auditoría | Verificado M2 |
| RN-10 vigencia de sesión | #7 | expiración tras diez minutos | No iniciada |

## Cobertura y mantenimiento

- Los RF y RNF prioritarios tienen al menos una issue o una combinación de
  implementación, verificación y evaluación trazable.
- #11 documenta que RFID físico no está disponible: el UID simulado canónico es
  hexadecimal, en mayúsculas y sin separadores. La integración física futura no
  bloquea QR/MVP ni este adaptador.
- #28 debe actualizar esta matriz al cerrar una issue y verificar enlaces,
  evidencia y diferencias entre GitHub y documentación.
