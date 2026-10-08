# Protocolo de evaluación biométrica y prueba de vida

Este protocolo prepara la evidencia de las issues [#26](https://github.com/UPT-FAING-EPIS/proyecto-si784-2026-ii-myprojectgroupcypw/issues/26), [#27](https://github.com/UPT-FAING-EPIS/proyecto-si784-2026-ii-myprojectgroupcypw/issues/27) y [#28](https://github.com/UPT-FAING-EPIS/proyecto-si784-2026-ii-myprojectgroupcypw/issues/28). No contiene resultados experimentales: se completa solamente durante una sesión presencial con voluntarios.

## Propósito y límites

El propósito académico es caracterizar, en condiciones controladas, el comportamiento del prototipo NotaryVerify ante comparaciones faciales legítimas, no coincidencias y presentaciones estáticas para prueba de vida. No identifica legalmente a nadie, no certifica seguridad, no sirve para seleccionar personas ni autoriza trámites reales.

La unidad de registro es un intento, no una persona. El evaluador conserva la relación entre un código y el voluntario en una hoja separada, local y fuera del repositorio. El repositorio, GitHub, los logs, el informe y el libro de resultados solo usan códigos anónimos como `P01`.

## Datos, acceso, retención y eliminación

| Aspecto | Decisión para esta evaluación |
| --- | --- |
| Datos capturados | Código anónimo, escenario, expectativa, resultado observado, condiciones de captura y métricas agregadas. La aplicación guarda temporalmente la referencia facial y las capturas necesarias para el flujo local. |
| Datos que no se registran | Nombre, DNI, correo, dirección, una tabla que conecte código con persona, fotos en Git, GitHub, chats, informes públicos ni logs. |
| Ubicación temporal | Solo el volumen local `notaryverify-data` de Docker (o `backend/data` en ejecución nativa) y el archivo de registro local del evaluador. |
| Acceso | Únicamente el evaluador autorizado y la cuenta Administrador local. El operador local usa solo las funciones que necesita; no se comparte la cuenta ni el volumen. |
| Retención | Hasta finalizar el análisis académico acordado con cada voluntario o hasta un retiro de consentimiento, lo que ocurra primero. |
| Eliminación | Revocar consentimiento, borrar la referencia del voluntario y el archivo de registro local. Para borrar todo el entorno Docker: `docker compose down -v`. En nativo, detener el backend y eliminar de forma controlada `<DATA_DIR>` después de extraer solo métricas agregadas. `python -m app.core.reset_db` **no** elimina referencias faciales. |

Antes de capturar una referencia, el evaluador confirma que el voluntario entendió el propósito, qué se captura, quién accede, la retención, el mecanismo de retiro y que puede detenerse sin consecuencias. El consentimiento se registra en la aplicación con el código anónimo, pero el formulario o evidencia de aceptación queda fuera de Git y fuera de esta documentación.

## Códigos reservados

`P01` está reservado para el único voluntario confirmado. No se asocia a una identidad real en este documento. `P02` a `P10` permanecen disponibles si se incorporan otros voluntarios con consentimiento. Los códigos `DEMO-01` y `DEMO-02` son exclusivamente registros sintéticos del entorno local; nunca se usan como evidencia humana.

## Preparación presencial

1. En la estación local, iniciar sesión como Administrador y crear el consentimiento con `P01`; no escribir nombre ni documento real.
2. Registrar una identidad con nombre y documento ficticios, y capturar la referencia del rostro de `P01` solo cuando el voluntario esté presente.
3. Emitir una credencial QR o RFID simulado y anotar únicamente sus identificadores internos en la hoja local de control si son necesarios para repetir el ensayo.
4. Abrir el libro `registro-evaluacion-biometrica.xlsx` y registrar cada intento inmediatamente. El libro no se sube con filas reales.
5. Mantener fondo, cámara, distancia, iluminación y versión local anotados. Detener la prueba si el voluntario retira su consentimiento o si una captura se guarda fuera de la ubicación prevista.

## Registro y clasificación

La hoja `Registro` del libro local usa estas columnas:

| Campo | Uso |
| --- | --- |
| `codigo_participante` | Código anónimo, por ejemplo `P01`. |
| `escenario` | `genuino`, `no_coincidencia`, `persona_real`, `foto_impresa` o `foto_pantalla`, según la parte del protocolo. |
| `esperado` | `aprobar` o `rechazar` antes de ejecutar el intento. |
| `observado` | Resultado que devolvió el sistema, sin corregirlo manualmente. |
| `iluminacion` | Condición observable, por ejemplo `normal`, `baja` o `contraluz`. |
| `distancia_cm` | Distancia aproximada cámara-rostro en centímetros. |
| `resultado` | Clasificación calculada: `TP`, `TN`, `FP`, `FN` o `PENDIENTE`. |

El ejemplo `P01, genuino, aprobar, aprobar, normal, 60, TP` solo se puede registrar después de un intento real aprobado. `P01, no_coincidencia, rechazar, rechazar, normal, 60, TN` requiere una no coincidencia consentida y ejecutada; no debe rellenarse como dato supuesto.

## Diseño mínimo de la prueba

### Comparación facial (#26)

Para `P01`, realizar intentos genuinos con la referencia del mismo voluntario y, si se cuenta con un segundo voluntario consentido, no coincidencias cruzadas. Con un único voluntario no es válido afirmar FPR ni cerrar #26: se pueden registrar observaciones genuinas y dejar la métrica de no coincidencia como no disponible. No se usan rostros de terceros sin consentimiento.

Anotar la latencia observada y cualquier rechazo técnico por separado de una decisión biométrica. Para cada fila, `TP` significa esperado aprobar y observado aprobar; `FN`, esperado aprobar y observado rechazar; `TN`, esperado rechazar y observado rechazar; `FP`, esperado rechazar y observado aprobar.

### Prueba de vida (#27)

El voluntario realiza presencialmente el desafío mostrado por el sistema (`persona_real`). Después, y solo con su propia imagen y permiso, se prueban `foto_impresa` y `foto_pantalla`. No se realizan ataques sobre otra persona ni se usan redes sociales, documentos auténticos o imágenes de terceros. Registrar el desafío, si venció y el resultado. Esta comprobación caracteriza un prototipo de captura estática con desafío; no demuestra detección de material ni resistencia a ataques avanzados.

## Métricas e informe

Al terminar, calcular sobre filas ejecutadas:

- Tasa de aceptación genuina = `TP / (TP + FN)`.
- Tasa de falso rechazo = `FN / (TP + FN)`.
- Tasa de rechazo de no coincidencia = `TN / (TN + FP)`.
- Tasa de falso positivo = `FP / (TN + FP)`.
- Para prueba de vida: rechazos de presentación estática / intentos estáticos ejecutados.

No dividir por cero ni informar una métrica cuando falta la clase correspondiente. El informe final de #28 incluye solo conteos agregados, versión del protocolo, fecha, entorno, limitaciones, enlaces a issues y hashes de artefactos no biométricos. No adjunta fotos, vídeo, códigos de credencial, documentos ni la relación código-persona.

## Cierre y trazabilidad

El evaluador revisa que cada fila tenga condiciones y resultado, conserva la hoja local durante la retención aprobada y actualiza la matriz de trazabilidad con el enlace al informe agregado. Luego ejecuta la eliminación indicada arriba y registra en el informe: fecha, responsable por rol, alcance eliminado y confirmación de que no quedan referencias ni volúmenes de evaluación. Solo después de contar con esa evidencia pueden evaluarse los criterios de cierre de #26, #27, #28 y del milestone M7.
