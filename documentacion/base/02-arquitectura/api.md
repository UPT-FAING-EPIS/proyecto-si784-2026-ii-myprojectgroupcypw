# API

La API FastAPI se publica localmente en http://127.0.0.1:8000; Swagger está en /docs.

## Autenticación local de desarrollo

- `POST /auth/login` recibe `correo` y `password`, y devuelve `access_token`,
  vencimiento y el rol local. Se habilitan cuentas solo con las variables de
  bootstrap documentadas en `.env.example`; no hay credenciales por defecto.
- Las rutas que requieran una identidad autenticada usan
  `Authorization: Bearer <access_token>`. La ausencia, invalidez, revocación o
  vencimiento retorna `401` con `detail.code = AUTHENTICATION_REQUIRED`.
- `POST /auth/logout` revoca el token y `GET /auth/me` permite comprobar la
  sesión sin revelar una contraseña.

La matriz inicial de permisos asigna enrolamiento, edición, bloqueo,
credenciales y bitácora a `ADMINISTRADOR`; `OPERADOR` y `ADMINISTRADOR` pueden
iniciar y completar verificaciones. La API no confía en `id_responsable`
enviado por el cliente: lo toma del token. Un rol insuficiente retorna `403`
con `detail.code = AUTHORIZATION_REQUIRED`.

## Contrato de errores

Los errores de dominio usan `detail.code` estable y un mensaje seguro:
`CONSENT_REQUIRED` (409), `IDENTITY_NOT_FOUND` y `CREDENTIAL_NOT_FOUND` (404),
`SESSION_NOT_FOUND` (404), `SESSION_NOT_ACTIVE` (409), `FACE_NOT_DETECTED`
(422), `MULTIPLE_FACES_DETECTED` (422), `FACE_QUALITY_INSUFFICIENT` (422),
`PROCEDURE_NOT_ENABLED` (409), `DOCUMENT_NOT_FOUND` (404),
`DOCUMENT_INTEGRITY_INVALID` (409) y `PROCEDURE_EVIDENCE_NOT_FOUND` (404).

Las cargas se validan antes de llegar a los servicios (#22):
`UPLOAD_TYPE_NOT_ALLOWED` (415) si la imagen no es JPEG o PNG o su contenido no
coincide con el tipo, `UPLOAD_TOO_LARGE` (413) si supera
`NOTARYVERIFY_MAX_UPLOAD_BYTES` y `UPLOAD_EMPTY` (422). Una carga rechazada no
persiste filas ni archivos.

## Comparación facial experimental

`POST /verificaciones/{id}/rostro` aplica un preprocesamiento local: decodifica
la imagen, exige al menos 120 × 120 píxeles, detecta exactamente un rostro,
recorta, normaliza a 200 × 200 píxeles en escala de grises y ecualiza el
histograma. Rechaza capturas borrosas con varianza de Laplaciano menor que 20.
LBPH devuelve una distancia que se normaliza como `max(0, 1 - distancia/100)`;
el umbral técnico actual es 0.35. Es un parámetro experimental, no una medida de
identidad legal, precisión ni resistencia a suplantación.

La ausencia, multiplicidad o calidad insuficiente devuelve, respectivamente,
`FACE_NOT_DETECTED`, `MULTIPLE_FACES_DETECTED` o `FACE_QUALITY_INSUFFICIENT`.
Los tres son 422 y nunca incluyen imágenes, rutas ni datos biométricos en la
respuesta.

## Prueba de vida experimental

Tras una comparación facial aprobada, `POST /verificaciones/{id}/prueba-vida/desafio`
emite en el servidor una acción aleatoria (`PARPADEO`, `GIRO_IZQUIERDA` o
`GIRO_DERECHA`) válida durante 20 segundos. Solo permite una repetición, que
queda auditada; no se acepta una acción elegida por el cliente. La captura se
envía a `POST /verificaciones/{id}/prueba-vida` sin un parámetro de acción.

El desafío, vencimiento, repetición, resultado y motivo quedan en la bitácora,
sin vídeo, imagen, landmarks ni métricas biométricas persistidas. Un desafío
vencido finaliza la sesión como `PRUEBA_DE_VIDA_FALLIDA`. Los códigos estables
son `LIVENESS_CHALLENGE_REQUIRED`, `LIVENESS_CHALLENGE_RETRY_LIMIT` y
`LIVENESS_CHALLENGE_ACTION_MISMATCH` (409), además de los errores 422 de
ausencia o múltiples rostros.

El mecanismo es experimental: verifica una acción en una captura de cámara y
rechaza las capturas estáticas que no cumplen el desafío en los casos
controlados. No identifica de forma fiable si los píxeles proceden de papel,
pantalla u otro medio, ni certifica resistencia ante suplantación.

## Reglas configurables

`GET` y `POST /reglas/configuracion` permiten a Administrador o Auditor ver y
versionar el orden de prioridad de `CREDENCIAL`, `ROSTRO` y `PRUEBA_VIDA`. El
catálogo exige los tres factores, por lo que no permite desactivar RN-01 ni
RN-04. Cada resultado guarda la versión e instantánea aplicada en
`decisiones_reglas` y el cambio genera auditoría.

## Consulta QR documental

`GET /documentos/consulta/{identificador}` recibe únicamente el identificador
opaco `NOTARYVERIFY-DOC-...` del QR documental. Devuelve `INTEGRO` o
`INTEGRIDAD_NO_VERIFICADA` y la fecha de generación; nunca expone sesión, hash,
contenido, identidad ni biometría. Un QR de credencial usa otro contrato.

## Historial de sesiones

`GET /verificaciones` requiere `ADMINISTRADOR` y admite `resultado`,
`fecha_desde`, `fecha_hasta` e `id_identidad`. Devuelve responsable, factores,
decisión y fechas, sin imágenes ni rutas de biometría. Al consultar, cualquier
sesión `EN_CURSO` con más de diez minutos se materializa como `EXPIRADA` y no
acepta nuevos factores.

`GET /verificaciones/alertas` lista alertas de tres fallos consecutivos para
Administrador. El bloqueo dura 15 minutos y devuelve `423` con
`IDENTITY_TEMPORARILY_LOCKED` durante su vigencia; al vencer se resuelve de
forma automática. `POST /verificaciones/alertas/{id}/reactivar` permite una
reactivación administrativa auditada, sin desactivar permanentemente la
identidad.

## Cambio de referencia biométrica

`POST /identidades/{id}/referencia/solicitudes` permite a Operador o
Administrador solicitar un cambio con motivo, imagen local y consentimiento
vigente. Solo `ADMINISTRADOR` puede listar y decidir mediante
`GET /identidades/referencia/solicitudes` y
`POST /identidades/referencia/solicitudes/{id}/decision`. La aprobación
sustituye atómicamente la referencia local y elimina la anterior; el rechazo
elimina la pendiente. Auditoría conserva actor, motivo, fecha y resultado, pero
nunca imagen, ruta ni contenido biométrico.

- /identidades y /identidades/consentimientos: datos ficticios y consentimiento.
- /credenciales: emisión, consulta, QR y revocación.
- /verificaciones: creación de sesión, rostro y prueba de vida.
- /documentos: hash y verificación de documentos de prueba. `POST /documentos?id_sesion=` exige Operador o Administrador, una sesión existente y `contenido` como campo de formulario (máximo 20 000 caracteres), no en la URL.
- /auditoria: eventos y validación de cadena.
- /tramites: simulación condicionada a sesión aprobada.
- /salud: healthcheck público; 200 `ok` o `degradado` (faltan modelos locales) y 503 `no_disponible` si la base no responde. No expone datos.

## Trámite simulado y evidencia recuperable

`POST /tramites` requiere autenticación de `OPERADOR` o `ADMINISTRADOR`, una
sesión con resultado `IDENTIDAD_VERIFICADA` y el `id_documento` generado para
esa misma sesión. Antes de crear el trámite, el servidor vuelve a calcular la
integridad del archivo local: un contenido alterado, ausente o asociado a otra
sesión responde `DOCUMENT_INTEGRITY_INVALID` o `PROCEDURE_NOT_ENABLED` y no
crea trámite ni evento de auditoría.

La asociación de sesión, documento y trámite queda en `evidencias_tramite` y
genera los eventos append-only `EVIDENCIA_TRAMITE_ASOCIADA` y
`TRAMITE_SIMULADO_EVALUADO`. `GET /tramites/{id_tramite}/evidencia` requiere
`ADMINISTRADOR` o `AUDITOR`; reconstruye solamente identificadores internos,
resultado de sesión, estado del trámite, estado actual de integridad y fecha.
No expone contenido, hash, ruta, identidad ni biometría. El SID-Sunarp sigue
siendo una simulación académica sin conexión a servicios reales.

## Bitácora y reconstrucción autorizada

Todas las rutas de `/auditoria` requieren `ADMINISTRADOR` o `AUDITOR`.
`GET /auditoria/eventos` entrega los metadatos encadenados de la bitácora y
`GET /auditoria/verificar-cadena` detecta una alteración o ruptura. Para una
sesión existente, `GET /auditoria/sesiones/{id_sesion}/reconstruccion` presenta
su catálogo mínimo de operaciones críticas: tipo, actor (o `SISTEMA` cuando no
hay actor humano), entidad, identificador, payload permitido, fecha y secuencia.
El contrato filtra deliberadamente el detalle crudo: no publica códigos de
credencial, contenido, hashes, rutas ni métricas biométricas.

Los routers y OpenAPI son la fuente de detalle de payloads. Al cambiar un endpoint, actualizar esta guía, pruebas de API y documentación OpenAPI.

## RFID simulado

No hay lector RFID físico en esta etapa. Al emitir una credencial de tipo
`RFID`, `uid_rfid` es obligatorio y debe ser hexadecimal en mayúsculas sin
separadores, como `04A1B2C3`. `GET /credenciales/rfid/{uid}` usa el adaptador
simulado y devuelve el mismo contrato de credencial que QR; una credencial
revocada conserva su estado y una inexistente retorna `CREDENTIAL_NOT_FOUND`.
La lectura solo recupera el registro: nunca aprueba una sesión por sí misma.

## Dashboard de utilización

`GET /dashboard/uso?dias=14` requiere `ADMINISTRADOR` o `AUDITOR` y devuelve
solo métricas agregadas: totales (identidades, credenciales activas, sesiones,
documentos, eventos de auditoría y alertas activas), tasas de aprobación y de
prueba de vida superada, confianza facial promedio, conteos por estado,
resultado, trámite, tipo de credencial y rol, y sesiones por día (`dias` entre 1
y 90). No incluye nombres, documentos, correos, códigos de credencial ni
identificadores. La página `frontend/dashboard.html` lo presenta con gráficos.
