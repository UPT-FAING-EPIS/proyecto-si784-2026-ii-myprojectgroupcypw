<center>

![](./media/logo-upt.png)

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERIA**

**Escuela Profesional de Ingeniería de Sistemas**

**Proyecto *NotaryVerify***

Curso: *Calidad y Pruebas de Software*

Docente: *Patrick Jose Cuadros Quiroga*

Integrantes:

***Cohaila Alvarado, Gabriela Estefania (2022075746)***

***Vargas Luque, Jhony (2022075754)***

**Tacna – Perú**

***2026***

</center>
<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

Sistema *NotaryVerify*

Documento de Arquitectura de Software

Versión *1.0*

|CONTROL DE VERSIONES||||||
| :-: | :- | :- | :- | :- | :- |
|Versión|Hecha por|Revisada por|Aprobada por|Fecha|Motivo|
|1\.0|GC, JV|PJCQ|PJCQ|20/09/2026|Versión Original|

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

# **INDICE GENERAL**

1. Introducción

1.1. Propósito (Diagrama 4+1)

1.2. Alcance

1.3. Definición, siglas y abreviaturas

1.4. Organización del documento

2. Objetivos y restricciones arquitectónicas

2.1. Priorización de requerimientos

2.1.1. Requerimientos Funcionales

2.1.2. Requerimientos No Funcionales – Atributos de Calidad

2.2. Restricciones

3. Representación de la arquitectura del sistema

3.1. Vista de Caso de uso

3.2. Vista Lógica

3.3. Vista de Implementación (vista de desarrollo)

3.4. Vista de procesos

3.5. Vista de Despliegue (vista física)

4. Atributos de calidad del software

4.1. Escenario de Funcionalidad

4.2. Escenario de Usabilidad

4.3. Escenario de Confiabilidad

4.4. Escenario de Rendimiento

4.5. Escenario de Mantenibilidad

4.6. Otros Escenarios

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

**<u>Informe de Arquitectura de Software</u>**

# 1. INTRODUCCIÓN

## 1.1. Propósito (Diagrama 4+1)

El presente documento describe la arquitectura del sistema **NotaryVerify**, prototipo experimental de verificación multicapa de identidad para trámites notariales simulados, desarrollado en el marco del curso Calidad y Pruebas de Software del semestre 2026-II.

La arquitectura se documenta siguiendo el **modelo de vistas 4+1 de Kruchten**, que permite describir un sistema desde perspectivas complementarias, cada una dirigida a un interesado distinto. Las cinco vistas empleadas son:

| Vista | Pregunta que responde | Interesado principal |
| :- | :- | :- |
| Vista de Casos de Uso (+1) | ¿Qué debe hacer el sistema y para quién? | Docente, equipo de proyecto |
| Vista Lógica | ¿Cómo se estructuran las clases, objetos y datos del dominio? | Desarrolladores, analistas |
| Vista de Implementación | ¿Cómo se organiza el código fuente en paquetes y componentes? | Desarrolladores |
| Vista de Procesos | ¿Cómo fluye el control durante la ejecución? | Desarrolladores, responsables de pruebas |
| Vista de Despliegue | ¿Sobre qué nodos físicos se ejecuta el sistema? | Responsable de infraestructura |

A diferencia de un documento de arquitectura elaborado antes de la construcción, este informe describe una arquitectura **ya implementada y verificada**: el backend, el frontend y la batería de pruebas automatizadas se encuentran desarrollados en el repositorio del proyecto. Por ello, los diagramas que se presentan reflejan la estructura real del código fuente y no un diseño tentativo.

El objetivo del documento es dejar constancia de las decisiones arquitectónicas adoptadas, justificar su relación con los requerimientos establecidos en el FD03 (Especificación de Requerimientos de Software) y proporcionar una base técnica para la continuidad académica del proyecto.

## 1.2. Alcance

El alcance de este documento abarca la descripción arquitectónica completa del prototipo NotaryVerify, incluyendo su estructura en capas, sus componentes, su modelo de datos, sus flujos de ejecución y su esquema de despliegue.

**Dentro del alcance del documento se considera:**

- La descripción de las cinco vistas del modelo 4+1 aplicadas al sistema implementado.
- El modelo de clases y el modelo de base de datos derivados de los modelos ORM efectivamente construidos.
- Los diagramas de secuencia correspondientes a los flujos críticos: verificación multicapa, integridad documental y encadenamiento de auditoría.
- La justificación de las decisiones tecnológicas adoptadas (FastAPI, SQLAlchemy, SQLite, OpenCV, MediaPipe).
- Los escenarios de atributos de calidad que orientan la evaluación del prototipo.

**Fuera del alcance del documento se considera:**

- El detalle línea a línea del código fuente, que se encuentra documentado en el propio repositorio.
- La arquitectura de los sistemas oficiales Reniec y SID-Sunarp, que en este proyecto se representan únicamente mediante simuladores desarrollados por el equipo.
- Cualquier consideración de despliegue en producción ante una notaría real, dado el carácter estrictamente académico del prototipo.
- El diseño de la infraestructura de alta disponibilidad, redundancia o balanceo de carga, no aplicable a un prototipo de evaluación controlada.

## 1.3. Definición, siglas y abreviaturas

| Término | Definición |
| :- | :- |
| NotaryVerify | Nombre referencial del sistema objeto del proyecto. |
| Modelo 4+1 | Modelo de vistas arquitectónicas propuesto por Philippe Kruchten, que organiza la descripción de un sistema en las vistas lógica, de implementación, de procesos, de despliegue y de casos de uso. |
| API REST | Interfaz de programación basada en el estilo arquitectónico REST, que expone recursos mediante verbos HTTP. |
| FastAPI | Framework web de Python empleado para construir la API REST del backend. |
| SQLAlchemy | Biblioteca de mapeo objeto-relacional (ORM) utilizada para persistir el modelo de dominio. |
| ORM | Object-Relational Mapping. Técnica que traduce objetos del lenguaje de programación a registros de una base de datos relacional. |
| SQLite | Motor de base de datos relacional embebido, sin servidor, empleado para la persistencia del prototipo. |
| Pydantic | Biblioteca de validación de datos empleada para definir los esquemas de entrada y salida de la API. |
| OpenCV | Biblioteca de visión por computadora de código abierto, utilizada para la detección y comparación facial local. |
| SFace | Modelo de reconocimiento facial del repositorio OpenCV Zoo, empleado para obtener la métrica de similitud entre rostros. |
| MediaPipe Face Landmarker | Herramienta de Google que detecta puntos de referencia faciales, utilizada para evaluar la prueba de vida. |
| EAR | Eye Aspect Ratio. Relación geométrica entre los puntos del contorno ocular que permite detectar el parpadeo. |
| SHA-256 | Algoritmo de hash criptográfico de 256 bits, empleado para la integridad documental y el encadenamiento de la bitácora. |
| Hash chain | Cadena de hashes en la que cada elemento incorpora el hash del elemento anterior, de modo que cualquier alteración posterior es detectable. |
| Simulador de Identidad | Servicio interno que representa, con fines exclusivamente académicos, una consulta de información de identidad, operando sobre identidades ficticias. |
| Simulador SID-Sunarp | Servicio interno que representa el comportamiento del SID-Sunarp para pruebas técnicas de integración, sin sustituir al sistema oficial. |
| Sesión de verificación | Registro único que agrupa la identidad evaluada, los factores aplicados, sus resultados y la decisión final del sistema. |
| CORS | Cross-Origin Resource Sharing. Mecanismo que autoriza a un navegador a consumir una API alojada en un origen distinto. |
| CU | Caso de Uso. |
| RF / RNF | Requerimiento Funcional / Requerimiento No Funcional. |
| RN | Regla de Negocio. |

## 1.4. Organización del documento

El documento se organiza en cuatro capítulos. El **capítulo 1** establece el propósito, el alcance y la terminología empleada. El **capítulo 2** presenta los objetivos arquitectónicos, la priorización de los requerimientos funcionales y no funcionales que condicionan el diseño, y las restricciones impuestas al proyecto. El **capítulo 3** constituye el núcleo del informe y desarrolla las cinco vistas del modelo 4+1, acompañadas de los diagramas correspondientes. El **capítulo 4** especifica los escenarios de atributos de calidad que servirán como criterio de evaluación del prototipo durante la fase de pruebas.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

# 2. OBJETIVOS Y RESTRICCIONES ARQUITECTÓNICAS

El objetivo arquitectónico central de NotaryVerify es garantizar que **ningún factor de verificación evaluado de forma aislada sea suficiente para aprobar una identidad**. Esta premisa, recogida en la regla de negocio RN-01, condiciona toda la estructura del sistema: obliga a separar cada mecanismo de verificación en un servicio independiente y a concentrar la decisión final en un único componente arbitral, el motor de reglas.

De este objetivo se derivan cuatro objetivos arquitectónicos secundarios:

| Objetivo | Decisión arquitectónica asociada |
| :- | :- |
| Aislar cada factor de verificación | Un servicio por factor: credencial, biometría, prueba de vida. Ninguno emite el veredicto final. |
| Concentrar la decisión | Un único motor de reglas evalúa la combinación de factores y produce el resultado. |
| Garantizar la trazabilidad | Toda operación crítica se registra en una bitácora con encadenamiento criptográfico. |
| Permitir la evaluación de fallos externos | Las dependencias externas se representan mediante simuladores con escenarios de error configurables. |

## 2.1. Priorización de requerimientos

Los requerimientos que se listan a continuación corresponden a los definidos en el FD03 (Especificación de Requerimientos de Software) y se presentan aquí priorizados según su impacto sobre la arquitectura. Se incluye una columna adicional que identifica el componente que satisface cada requerimiento.

### 2.1.1. Requerimientos Funcionales

| ID | Requerimiento Funcional | Prioridad | Componente responsable |
| :- | :- | :-: | :- |
| RF-01 | Registrar una identidad ficticia en el Simulador de Identidad, con documento, nombres, fotografía de referencia y estado. | Alta | `identidad_service` |
| RF-02 | Consultar una identidad registrada mediante su identificador. | Alta | `identidad_service` |
| RF-03 | Emitir una credencial de prueba (QR o RFID) asociada a una identidad simulada. | Alta | `credencial_service` |
| RF-04 | Leer una credencial para recuperar el registro correspondiente, sin aprobar la identidad por sí sola. | Alta | `credencial_service` |
| RF-05 | Capturar el rostro del participante mediante cámara durante la verificación. | Alta | `routes_verificacion` |
| RF-06 | Comparar el rostro capturado con la referencia registrada y devolver una métrica de confianza. | Alta | `biometria_service` |
| RF-07 | Solicitar una acción aleatoria (parpadeo, giro) y validar su cumplimiento. | Alta | `liveness_service` |
| RF-08 | Combinar los resultados de credencial, rostro y prueba de vida para determinar el resultado final. | Alta | `reglas_service` |
| RF-09 | Registrar cada sesión con los factores utilizados, resultados, fecha, hora y responsable. | Alta | `verificacion_service` |
| RF-10 | Calcular el hash SHA-256 de un documento de prueba generado tras una verificación aprobada. | Alta | `documento_service` |
| RF-11 | Comparar el hash almacenado con el hash actual de un documento para detectar modificaciones. | Alta | `documento_service` |
| RF-12 | Generar un código QR de verificación asociado al documento, sin incluir información personal. | Media | `documento_service` |
| RF-13 | Registrar cada operación crítica en la bitácora, enlazándola con el evento anterior. | Alta | `auditoria_service` |
| RF-14 | Detectar si algún evento de la bitácora fue alterado, verificando el encadenamiento. | Alta | `auditoria_service` |
| RF-15 | Enviar un trámite ficticio al Simulador SID-Sunarp solo si la sesión asociada fue aprobada. | Media | `sid_sunarp_service` |
| RF-16 | Representar escenarios de disponibilidad, error de respuesta y tiempo de espera agotado. | Media | `sid_sunarp_service` |

### 2.1.2. Requerimientos No Funcionales – Atributos de Calidad

| ID | Requerimiento No Funcional | Categoría | Impacto arquitectónico |
| :- | :- | :- | :- |
| RNF-01 | El operador debe completar el flujo de verificación en no más de 4 pasos. | Usabilidad | El frontend expone el flujo como una secuencia lineal de cuatro secciones. |
| RNF-02 | La comparación facial debe completarse en menos de 3 segundos por intento. | Rendimiento | Inferencia local con OpenCV; se evita cualquier llamada de red durante la comparación. |
| RNF-03 | El entorno de pruebas debe estar disponible al menos el 95 % del tiempo. | Disponibilidad | Persistencia embebida (SQLite) sin dependencia de servidores externos. |
| RNF-04 | El proceso completo de verificación no debe superar los 45 segundos. | Eficiencia | Modelos cargados una sola vez y mantenidos en caché entre peticiones. |
| RNF-05 | La tasa combinada de falsos positivos debe ser inferior al 5 %. | Precisión biométrica | Umbrales parametrizados y aislados en constantes de módulo. |
| RNF-06 | El sistema debe autenticar a operadores y administradores. | Seguridad | Entidad `Usuario` con rol; las sesiones registran el responsable. |
| RNF-07 | Los datos deben viajar cifrados mediante HTTPS/TLS 1.2 o superior. | Seguridad | Terminación TLS delegada al servidor de aplicación. |
| RNF-08 | La aplicación web debe funcionar en Chrome, Edge y Firefox. | Compatibilidad | Frontend sin framework ni proceso de compilación. |
| RNF-09 | El código debe organizarse por capas y estar documentado. | Mantenibilidad | Arquitectura en cuatro capas con responsabilidad única por servicio. |
| RNF-10 | La bitácora debe permitir reconstruir el 100 % de las operaciones críticas. | Trazabilidad | Bitácora con encadenamiento criptográfico y secuencia monotónica. |

## 2.2. Restricciones

Las siguientes restricciones condicionan las decisiones arquitectónicas adoptadas:

- **Restricción normativa.** El sistema no puede tratar información biométrica real de clientes de una notaría. La arquitectura opera exclusivamente sobre identidades ficticias, y toda muestra biométrica requiere el registro previo de un consentimiento expreso, modelado como la entidad `ConsentimientoBiometrico`.

- **Restricción de independencia institucional.** El sistema no puede depender de Reniec, del SID-Sunarp oficial ni de certificados de firma digital. Las interacciones necesarias se representan mediante simuladores internos, lo que elimina cualquier dependencia de credenciales institucionales.

- **Restricción de procesamiento local.** El reconocimiento facial y la prueba de vida deben ejecutarse localmente, sin recurrir a servicios biométricos comerciales de pago. Esto impone el uso de OpenCV y MediaPipe, y condiciona el rendimiento al hardware del equipo de desarrollo.

- **Restricción de recursos.** El equipo está conformado por dos integrantes y el proyecto se desarrolla con recursos propios. La arquitectura evita componentes que exijan administración continua: no hay servidor de base de datos, ni broker de mensajería, ni orquestador de contenedores.

- **Restricción temporal.** El proyecto se ejecuta entre el 25 de agosto y el 12 de diciembre de 2026, lo que descarta arquitecturas distribuidas cuya puesta en marcha consumiría un tiempo desproporcionado respecto al objetivo de investigación.

- **Restricción de validez legal.** Ningún resultado producido por el sistema tiene valor de identificación legal. La arquitectura incorpora este aviso de forma explícita en la descripción de la API y en la respuesta del endpoint raíz.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

# 3. REPRESENTACIÓN DE LA ARQUITECTURA DEL SISTEMA

NotaryVerify adopta una **arquitectura en capas** sobre un backend monolítico modular, expuesto como API REST y consumido por un cliente web ligero. La elección de un monolito modular, frente a una arquitectura de microservicios, responde a las restricciones de equipo y tiempo descritas en la sección 2.2: la separación de responsabilidades se consigue mediante la disciplina de capas y servicios, sin incurrir en el costo operativo de desplegar y coordinar servicios independientes.

Las cuatro capas del backend son:

| Capa | Paquete | Responsabilidad |
| :- | :- | :- |
| Presentación / API | `app/api` | Exponer los endpoints HTTP, validar la entrada y traducir las excepciones de dominio a códigos de estado. |
| Dominio / Servicios | `app/services` | Concentrar la lógica de negocio y las reglas de verificación. No conoce HTTP. |
| Modelo | `app/models` | Definir las entidades ORM, los catálogos de estados y los esquemas de validación. |
| Infraestructura | `app/core` | Gestionar la conexión a la base de datos y el ciclo de vida de las sesiones. |

La regla de dependencia es estricta y unidireccional: la capa de API depende de los servicios, los servicios dependen del modelo, y el modelo depende de la infraestructura. Ninguna capa inferior conoce a la superior.

## 3.1. Vista de Caso de uso

La vista de casos de uso representa el comportamiento del sistema desde la perspectiva de sus actores. Constituye la vista "+1" del modelo de Kruchten y sirve de eje articulador de las cuatro vistas restantes.

Se identifican tres actores:

| Actor | Descripción |
| :- | :- |
| Operador | Ejecuta el flujo de verificación: lee la credencial, captura el rostro y solicita la prueba de vida. |
| Administrador | Registra identidades y consentimientos, emite y revoca credenciales, y consulta la bitácora de auditoría. |
| Simulador SID-Sunarp | Actor externo que recibe los trámites ficticios cuya sesión de verificación fue aprobada. |

### 3.1.1. Diagramas de Casos de uso

```mermaid
graph LR
    OP(["Operador"])
    AD(["Administrador"])
    SID(["Simulador<br/>SID-Sunarp"])

    subgraph NV["Sistema NotaryVerify"]
        CU01["CU-01<br/>Registrar identidad<br/>simulada"]
        CU02["CU-02<br/>Emitir credencial<br/>de prueba"]
        CU03["CU-03<br/>Ejecutar verificación<br/>multicapa"]
        CU04["CU-04<br/>Revocar credencial"]
        CU05["CU-05<br/>Generar documento<br/>verificado"]
        CU06["CU-06<br/>Verificar integridad<br/>documental"]
        CU07["CU-07<br/>Consultar bitácora<br/>de auditoría"]
        CU08["CU-08<br/>Verificar cadena<br/>de hashes"]
        CU09["CU-09<br/>Enviar trámite<br/>ficticio"]
        CU10["CU-10<br/>Otorgar consentimiento<br/>biométrico"]
    end

    AD --> CU10
    AD --> CU01
    AD --> CU02
    AD --> CU04
    AD --> CU07
    AD --> CU08
    OP --> CU03
    OP --> CU05
    OP --> CU06
    OP --> CU09
    CU09 --> SID

    CU01 -.->|"&lt;&lt;precede&gt;&gt;"| CU10
    CU03 -.->|"&lt;&lt;include&gt;&gt;"| CU02
    CU05 -.->|"&lt;&lt;require&gt;&gt;"| CU03
    CU09 -.->|"&lt;&lt;require&gt;&gt;"| CU03
```

El caso de uso **CU-03 (Ejecutar verificación multicapa)** es el caso de uso arquitectónicamente significativo: atraviesa todas las capas del sistema, involucra a todos los servicios de dominio y determina la estructura de las vistas lógica y de procesos que se describen a continuación.

## 3.2. Vista Lógica

La vista lógica describe la organización estática del sistema: cómo se agrupan las responsabilidades en subsistemas, qué clases las implementan y cómo se persisten los datos.

### 3.2.1. Diagrama de Subsistemas (paquetes)

```mermaid
graph TB
    subgraph API["app/api — Capa de presentación"]
        R1["routes_identidades"]
        R2["routes_credenciales"]
        R3["routes_verificacion"]
        R4["routes_documentos"]
        R5["routes_auditoria"]
        R6["routes_tramites"]
    end

    subgraph SRV["app/services — Capa de dominio"]
        S1["consentimiento_service"]
        S2["identidad_service"]
        S3["credencial_service"]
        S4["biometria_service"]
        S5["liveness_service"]
        S6["reglas_service"]
        S7["verificacion_service"]
        S8["documento_service"]
        S9["auditoria_service"]
        S10["sid_sunarp_service"]
    end

    subgraph MOD["app/models — Capa de modelo"]
        M1["db_models"]
        M2["schemas"]
        M3["enums"]
    end

    subgraph CORE["app/core — Infraestructura"]
        C1["database"]
    end

    API --> SRV
    SRV --> MOD
    MOD --> CORE
```

El subsistema `verificacion_service` actúa como **orquestador**: es el único servicio que coordina a varios otros. Los demás servicios mantienen una responsabilidad única y no se invocan entre sí, lo que reduce el acoplamiento y facilita la prueba unitaria de cada uno de forma aislada.

### 3.2.2. Diagrama de Secuencia (vista de diseño)

#### 3.2.2.1. Ejecución de la verificación multicapa (CU-03)

```mermaid
sequenceDiagram
    actor OP as Operador
    participant FE as Frontend
    participant API as routes_verificacion
    participant VS as verificacion_service
    participant CS as credencial_service
    participant BS as biometria_service
    participant LS as liveness_service
    participant RS as reglas_service
    participant AS as auditoria_service
    participant DB as SQLite

    OP->>FE: Presenta credencial QR
    FE->>API: POST /verificacion
    API->>VS: iniciar_sesion(codigo)
    VS->>CS: leer(codigo)
    CS->>DB: SELECT credencial
    DB-->>CS: Credencial
    CS-->>VS: Credencial
    VS->>DB: INSERT sesion (EN_CURSO)
    VS->>AS: registrar_evento(SESION_INICIADA)
    AS->>DB: INSERT evento (hash encadenado)
    VS-->>API: Sesion
    API-->>FE: id_sesion

    OP->>FE: Captura facial
    FE->>API: POST /verificacion/{id}/rostro
    API->>VS: registrar_captura_facial(id, imagen)
    VS->>BS: comparar_rostro(referencia, captura)
    BS-->>VS: (coincide, confianza)
    VS->>AS: registrar_evento(ROSTRO_EVALUADO)

    OP->>FE: Ejecuta acción solicitada
    FE->>API: POST /verificacion/{id}/prueba-vida
    API->>VS: registrar_prueba_vida(id, accion, imagen)
    VS->>LS: validar_accion(accion, imagen)
    LS-->>VS: (superado, detalle)
    VS->>RS: evaluar(credencial, rostro, vida)
    RS-->>VS: RESULTADO
    VS->>DB: UPDATE sesion (COMPLETADA)
    VS->>AS: registrar_evento(SESION_FINALIZADA)
    VS-->>API: Sesion con resultado
    API-->>FE: Resultado final
    FE-->>OP: IDENTIDAD VERIFICADA / RECHAZADA
```

#### 3.2.2.2. Verificación de integridad documental

```mermaid
sequenceDiagram
    actor OP as Operador
    participant API as routes_documentos
    participant DS as documento_service
    participant AS as auditoria_service
    participant FS as Sistema de archivos
    participant DB as SQLite

    OP->>API: POST /documentos/{id}/verificar
    API->>DS: verificar_integridad(id, archivo)
    DS->>DB: SELECT hash_sha256 almacenado
    DB-->>DS: hash original
    DS->>FS: Leer archivo presentado
    FS-->>DS: bytes
    DS->>DS: Calcular SHA-256 del archivo
    alt Los hashes coinciden
        DS->>AS: registrar_evento(INTEGRIDAD_OK)
        DS-->>API: integro = true
    else Los hashes difieren
        DS->>AS: registrar_evento(INTEGRIDAD_VULNERADA)
        DS-->>API: integro = false
    end
    API-->>OP: Resultado de integridad
```

#### 3.2.2.3. Encadenamiento criptográfico de la bitácora

```mermaid
sequenceDiagram
    participant SRV as Servicio de dominio
    participant AS as auditoria_service
    participant DB as SQLite

    SRV->>AS: registrar_evento(sesion, tipo, detalle)
    AS->>DB: SELECT último evento (por secuencia)
    alt Existe evento previo
        DB-->>AS: evento anterior
        AS->>AS: hash_anterior = evento.hash_actual
    else Primer evento del sistema
        DB-->>AS: ninguno
        AS->>AS: hash_anterior = GENESIS (64 ceros)
    end
    AS->>AS: hash_actual = SHA256(sesion, tipo, detalle,<br/>timestamp, hash_anterior)
    AS->>DB: INSERT evento con ambos hashes
    AS-->>SRV: EventoAuditoria
```

### 3.2.3. Diagrama de Colaboración (vista de diseño)

El diagrama de colaboración presenta las mismas interacciones del caso de uso CU-03, organizadas según la estructura de los objetos participantes en lugar de su secuencia temporal. La numeración indica el orden de los mensajes.

```mermaid
graph TD
    API["routes_verificacion"]
    VS["verificacion_service<br/>«orquestador»"]
    CS["credencial_service"]
    IS["identidad_service"]
    BS["biometria_service"]
    LS["liveness_service"]
    RS["reglas_service"]
    AS["auditoria_service"]
    DB[("SQLite")]

    API -->|"1: iniciar_sesion()"| VS
    VS -->|"2: leer(codigo)"| CS
    VS -->|"3: referencia_facial_bytes()"| IS
    VS -->|"4: comparar_rostro()"| BS
    VS -->|"5: validar_accion()"| LS
    VS -->|"6: evaluar()"| RS
    VS -->|"7: registrar_evento()"| AS
    VS -->|"8: bloquear() si 3 fallos"| IS
    CS --> DB
    IS --> DB
    AS --> DB
    VS --> DB
```

Se observa que `verificacion_service` es el único objeto con múltiples colaboradores. Esta concentración es deliberada: constituye la materialización del objetivo arquitectónico de que la decisión final resida en un solo punto del sistema.

### 3.2.4. Diagrama de Objetos

El siguiente diagrama muestra una instantánea del sistema durante una sesión de verificación aprobada para la identidad ficticia PERSONA-001.

```mermaid
graph LR
    CONS["consent1 : ConsentimientoBiometrico<br/>id_participante = 'VOL-001'<br/>alcance = 'Pruebas académicas'<br/>revocado = false"]

    IDEN["identidad1 : IdentidadSimulada<br/>nombre_ficticio = 'PERSONA-001'<br/>documento_ficticio = '00000001'<br/>estado = 'ACTIVA'"]

    CRED["credencial1 : Credencial<br/>codigo = 'NV-A1B2C3'<br/>tipo = 'QR'<br/>estado = 'ACTIVA'"]

    USR["operador1 : Usuario<br/>nombre = 'Jhony Vargas'<br/>rol = 'OPERADOR'"]

    SES["sesion1 : SesionVerificacion<br/>rostro_coincide = true<br/>confianza_facial = 0.72<br/>prueba_vida_accion = 'PARPADEO'<br/>prueba_vida_superada = true<br/>resultado = 'IDENTIDAD_VERIFICADA'<br/>estado = 'COMPLETADA'"]

    DOC["documento1 : DocumentoVerificado<br/>hash_sha256 = 'a3f5...'<br/>qr_verificacion = 'NV-DOC-001'"]

    EV["evento7 : EventoAuditoria<br/>tipo_evento = 'SESION_FINALIZADA'<br/>secuencia = 7<br/>hash_evento_anterior = '9c1d...'<br/>hash_evento_actual = 'e84b...'"]

    TRA["tramite1 : TramiteSimulado<br/>estado = 'ENVIADO'"]

    CONS -->|"autoriza"| IDEN
    IDEN -->|"posee"| CRED
    CRED -->|"identifica"| SES
    USR -->|"responsable de"| SES
    SES -->|"genera"| DOC
    SES -->|"registra"| EV
    SES -->|"habilita"| TRA
```

### 3.2.5. Diagrama de Clases

El diagrama refleja las entidades ORM efectivamente implementadas en el módulo `app/models/db_models.py`.

```mermaid
classDiagram
    class ConsentimientoBiometrico {
        +str id
        +str id_participante
        +str alcance
        +datetime fecha_otorgado
        +bool revocado
    }

    class IdentidadSimulada {
        +str id
        +str nombre_ficticio
        +str documento_ficticio
        +str id_participante
        +str referencia_facial_path
        +str estado
        +datetime fecha_registro
    }

    class Credencial {
        +str id
        +str codigo
        +str tipo
        +str id_identidad
        +str estado
        +datetime fecha_emision
    }

    class Usuario {
        +str id
        +str nombre
        +str correo
        +str rol
        +str password_hash
    }

    class SesionVerificacion {
        +str id
        +str id_identidad
        +str id_credencial
        +str id_responsable
        +bool rostro_coincide
        +float confianza_facial
        +str prueba_vida_accion
        +bool prueba_vida_superada
        +str resultado
        +str estado
        +datetime fecha_inicio
        +datetime fecha_fin
    }

    class EventoAuditoria {
        +str id
        +str id_sesion
        +str tipo_evento
        +str detalle
        +str hash_evento_anterior
        +str hash_evento_actual
        +datetime timestamp
        +str timestamp_iso
        +int secuencia
    }

    class DocumentoVerificado {
        +str id
        +str id_sesion
        +str hash_sha256
        +str qr_verificacion
        +str contenido_path
        +datetime fecha_generacion
    }

    class TramiteSimulado {
        +str id
        +str id_sesion
        +str estado
        +datetime fecha
    }

    IdentidadSimulada "1" --> "0..*" Credencial : emite
    IdentidadSimulada "1" --> "0..*" SesionVerificacion : es evaluada en
    Credencial "1" --> "0..*" SesionVerificacion : identifica
    Usuario "1" --> "0..*" SesionVerificacion : ejecuta
    SesionVerificacion "1" --> "0..*" EventoAuditoria : registra
    SesionVerificacion "1" --> "0..1" DocumentoVerificado : genera
    SesionVerificacion "1" --> "0..1" TramiteSimulado : habilita
    EventoAuditoria --> EventoAuditoria : encadena
```

### 3.2.6. Diagrama de Base de datos (relacional)

El sistema persiste sus datos en una base relacional SQLite embebida. El siguiente diagrama entidad-relación refleja el esquema generado por SQLAlchemy.

```mermaid
erDiagram
    CONSENTIMIENTOS_BIOMETRICOS {
        string id PK
        string id_participante
        text alcance
        datetime fecha_otorgado
        bool revocado
    }
    IDENTIDADES_SIMULADAS {
        string id PK
        string nombre_ficticio
        string documento_ficticio UK
        string id_participante
        string referencia_facial_path
        string estado
        datetime fecha_registro
    }
    CREDENCIALES {
        string id PK
        string codigo UK
        string tipo
        string id_identidad FK
        string estado
        datetime fecha_emision
    }
    USUARIOS {
        string id PK
        string nombre
        string correo UK
        string rol
        string password_hash
    }
    SESIONES_VERIFICACION {
        string id PK
        string id_identidad FK
        string id_credencial FK
        string id_responsable FK
        bool rostro_coincide
        float confianza_facial
        string prueba_vida_accion
        bool prueba_vida_superada
        string resultado
        string estado
        datetime fecha_inicio
        datetime fecha_fin
    }
    EVENTOS_AUDITORIA {
        string id PK
        string id_sesion
        string tipo_evento
        text detalle
        string hash_evento_anterior
        string hash_evento_actual UK
        datetime timestamp
        string timestamp_iso
        int secuencia
    }
    DOCUMENTOS_VERIFICADOS {
        string id PK
        string id_sesion
        string hash_sha256
        string qr_verificacion
        string contenido_path
        datetime fecha_generacion
    }
    TRAMITES_SIMULADOS {
        string id PK
        string id_sesion
        string estado
        datetime fecha
    }

    IDENTIDADES_SIMULADAS ||--o{ CREDENCIALES : "emite"
    IDENTIDADES_SIMULADAS ||--o{ SESIONES_VERIFICACION : "es evaluada en"
    CREDENCIALES ||--o{ SESIONES_VERIFICACION : "identifica"
    USUARIOS ||--o{ SESIONES_VERIFICACION : "ejecuta"
    SESIONES_VERIFICACION ||--o{ EVENTOS_AUDITORIA : "registra"
    SESIONES_VERIFICACION ||--o| DOCUMENTOS_VERIFICADOS : "genera"
    SESIONES_VERIFICACION ||--o| TRAMITES_SIMULADOS : "habilita"
```

Cabe destacar una decisión de diseño en la tabla `eventos_auditoria`: el campo `timestamp_iso` almacena explícitamente la cadena de texto empleada en el cálculo del hash. Persistirla, en lugar de reconstruirla a partir del campo `timestamp`, garantiza que la verificación de la cadena sea determinista y no dependa de cómo cada motor de base de datos serialice los valores de fecha y hora.

## 3.3. Vista de Implementación (vista de desarrollo)

La vista de implementación describe la organización del código fuente tal como se encuentra en el repositorio del proyecto.

### 3.3.1. Diagrama de arquitectura software (paquetes)

**Nivel 1 — Contexto del sistema**

```mermaid
graph LR
    OP(["Operador /<br/>Administrador"])
    CAM["Cámara web"]
    NV["NotaryVerify<br/>Prototipo de verificación<br/>multicapa de identidad"]
    SID["Simulador SID-Sunarp<br/>(interno)"]

    OP -->|"Usa mediante<br/>navegador"| NV
    CAM -->|"Provee imagen<br/>facial"| NV
    NV -->|"Envía trámites<br/>aprobados"| SID
```

**Nivel 2 — Contenedores**

```mermaid
graph TB
    NAV["Navegador web<br/>Chrome / Edge / Firefox"]

    subgraph EQUIPO["Equipo de desarrollo"]
        FE["Frontend<br/>HTML + CSS + JavaScript<br/>sin framework"]
        BE["Backend<br/>FastAPI + Uvicorn<br/>Python 3.11+"]
        DB[("Base de datos<br/>SQLite<br/>notaryverify.db")]
        FS["Almacén de archivos<br/>referencias faciales,<br/>documentos, modelos"]
    end

    NAV --> FE
    FE -->|"HTTP / JSON<br/>CORS habilitado"| BE
    BE -->|"SQLAlchemy ORM"| DB
    BE -->|"Lectura / escritura"| FS
```

**Nivel 3 — Estructura interna de paquetes**

```mermaid
graph TB
    subgraph REPO["Repositorio del proyecto"]
        subgraph BACK["backend/"]
            MAIN["app/main.py<br/>ensamblado de la aplicación"]
            subgraph APP["app/"]
                PAPI["api/<br/>6 routers"]
                PSRV["services/<br/>10 servicios de dominio"]
                PMOD["models/<br/>db_models, schemas, enums"]
                PCORE["core/<br/>database"]
            end
            TESTS["tests/<br/>7 módulos de prueba"]
            DATA["data/<br/>BD, modelos, referencias"]
        end
        subgraph FRONT["frontend/"]
            HTML["index.html"]
            JS["app.js"]
            CSS["styles.css"]
        end
    end

    MAIN --> PAPI
    PAPI --> PSRV
    PSRV --> PMOD
    PMOD --> PCORE
    TESTS -.->|"prueban"| PSRV
    TESTS -.->|"prueban"| PAPI
    PSRV --> DATA
    JS -.->|"consume API"| MAIN
    HTML --> JS
    HTML --> CSS
```

### 3.3.2. Diagrama de arquitectura del sistema (Diagrama de componentes)

```mermaid
graph TB
    subgraph CLI["Cliente web"]
        UI["Interfaz de pruebas<br/>4 secciones del flujo"]
    end

    subgraph PRES["Capa de presentación — app/api"]
        RID["routes_identidades"]
        RCR["routes_credenciales"]
        RVE["routes_verificacion"]
        RDO["routes_documentos"]
        RAU["routes_auditoria"]
        RTR["routes_tramites"]
    end

    subgraph DOM["Capa de dominio — app/services"]
        ORQ["verificacion_service<br/>«orquestador»"]
        FACT["Servicios de factor<br/>credencial · biometria · liveness"]
        REG["reglas_service<br/>«motor de decisión»"]
        TRAZ["auditoria_service · documento_service<br/>«trazabilidad e integridad»"]
        SIM["identidad_service · sid_sunarp_service<br/>«simuladores institucionales»"]
    end

    subgraph INFRA["Infraestructura"]
        ORM["SQLAlchemy ORM"]
        BD[("SQLite")]
        CV["OpenCV<br/>SFace"]
        MP["MediaPipe<br/>Face Landmarker"]
        QR["qrcode + Pillow"]
    end

    UI -->|"HTTP/JSON"| PRES
    RID --> SIM
    RCR --> FACT
    RVE --> ORQ
    RDO --> TRAZ
    RAU --> TRAZ
    RTR --> SIM
    ORQ --> FACT
    ORQ --> REG
    ORQ --> TRAZ
    ORQ --> SIM
    FACT --> CV
    FACT --> MP
    FACT --> QR
    DOM --> ORM
    ORM --> BD
```

La agrupación de los servicios en cuatro familias —orquestación, factores, decisión y trazabilidad— evidencia la intención arquitectónica: los servicios de factor producen **evidencia**, el motor de reglas produce el **veredicto** y los servicios de trazabilidad producen la **prueba** de lo ocurrido. Ningún componente asume más de una de estas responsabilidades.

## 3.4. Vista de procesos

La vista de procesos describe el comportamiento dinámico del sistema durante la ejecución del caso de uso crítico.

### 3.4.1. Diagrama de Procesos del sistema (diagrama de actividad)

```mermaid
flowchart TD
    INI([Inicio]) --> LEER["Operador presenta<br/>credencial QR/RFID"]
    LEER --> BUSCA{"¿Credencial<br/>registrada?"}
    BUSCA -->|No| RNOREG["Resultado:<br/>CREDENCIAL_NO_REGISTRADA"]
    BUSCA -->|Sí| REVOC{"¿Credencial<br/>revocada?"}
    REVOC -->|Sí| RREVOC["Resultado:<br/>CREDENCIAL_REVOCADA"]
    REVOC -->|No| CREASES["Crear sesión<br/>estado EN_CURSO"]

    CREASES --> VIGENTE{"¿Sesión vigente?<br/>(menos de 10 min)"}
    VIGENTE -->|No| REXP["Sesión EXPIRADA<br/>RN-10"]
    VIGENTE -->|Sí| CAPTURA["Capturar rostro<br/>mediante cámara"]

    CAPTURA --> COMPARA["Comparar con referencia<br/>OpenCV SFace"]
    COMPARA --> COINC{"¿Confianza<br/>mayor o igual a 0.35?"}
    COINC -->|No| RNOCOIN["Resultado:<br/>ROSTRO_NO_COINCIDENTE"]
    COINC -->|Sí| DESAFIO["Solicitar acción aleatoria:<br/>parpadeo o giro"]

    DESAFIO --> EVALVIDA["Evaluar landmarks<br/>MediaPipe"]
    EVALVIDA --> VIDA{"¿Acción<br/>superada?"}
    VIDA -->|No| RVIDA["Resultado:<br/>PRUEBA_DE_VIDA_FALLIDA"]
    VIDA -->|Sí| REGLAS["Motor de reglas:<br/>evaluar combinación"]

    REGLAS --> APROB["Resultado:<br/>IDENTIDAD_VERIFICADA"]

    RNOREG --> CIERRA
    RREVOC --> CIERRA
    RNOCOIN --> CIERRA
    RVIDA --> CIERRA
    APROB --> CIERRA["Cerrar sesión<br/>estado COMPLETADA"]

    CIERRA --> BITACORA["Registrar evento<br/>en bitácora encadenada"]
    BITACORA --> FALLOS{"¿3 fallos<br/>consecutivos?"}
    FALLOS -->|Sí| BLOQUEA["Bloquear identidad<br/>y generar alerta RN-05"]
    FALLOS -->|No| HABIL{"¿Resultado<br/>aprobado?"}
    BLOQUEA --> FIN
    HABIL -->|Sí| TRAMITE["Habilitar envío de trámite<br/>al Simulador SID-Sunarp"]
    HABIL -->|No| FIN
    TRAMITE --> FIN([Fin])
    REXP --> FIN
```

El diagrama evidencia dos características arquitectónicas relevantes. En primer lugar, existen **cinco puntos de salida negativos** antes de alcanzar la aprobación, lo que materializa el principio de que la verificación debe superar todas las capas. En segundo lugar, **todos los caminos convergen** en el registro de la bitácora, garantizando que ningún resultado quede sin traza, incluidos los rechazos.

## 3.5. Vista de Despliegue (vista física)

### 3.5.1. Diagrama de despliegue

```mermaid
graph TB
    subgraph NODO1["«dispositivo» Equipo del operador"]
        subgraph NAVEGADOR["«entorno de ejecución» Navegador web"]
            FEC["«artefacto»<br/>index.html<br/>app.js · styles.css"]
        end
        CAMARA["«dispositivo»<br/>Cámara web HD"]
        LECTOR["«dispositivo»<br/>Lector RFID USB"]
    end

    subgraph NODO2["«dispositivo» Servidor de aplicación (equipo de desarrollo)"]
        subgraph PYTHON["«entorno de ejecución» Python 3.11+ / Uvicorn"]
            APP["«artefacto»<br/>app.main:app<br/>API FastAPI"]
            MODELOS["«artefacto»<br/>face_landmarker.task<br/>haarcascade + SFace"]
        end
        subgraph ALMACEN["«dispositivo» Almacenamiento local"]
            BDD["«artefacto»<br/>notaryverify.db<br/>SQLite"]
            REFS["«artefacto»<br/>referencias_faciales/<br/>documentos/"]
        end
    end

    FEC -->|"HTTPS / JSON<br/>puerto 8000"| APP
    CAMARA -->|"MediaDevices API"| FEC
    LECTOR -->|"HID / USB"| FEC
    APP -->|"SQLAlchemy"| BDD
    APP -->|"E/S de archivos"| REFS
    APP -->|"Carga en memoria<br/>una sola vez"| MODELOS
```

El despliegue es deliberadamente simple. El prototipo se ejecuta sobre un único nodo físico que aloja tanto el servidor de aplicación como el almacenamiento, mientras que el cliente se ejecuta en el navegador del operador. Esta topología es coherente con el carácter experimental del sistema y con la restricción de recursos descrita en la sección 2.2.

Merece mención la decisión de **cargar los modelos biométricos una sola vez** y mantenerlos en memoria entre peticiones. El modelo `face_landmarker.task` de MediaPipe tarda varios segundos en inicializarse; cargarlo en cada petición haría inviable el cumplimiento del requerimiento RNF-02, que exige comparaciones faciales por debajo de los tres segundos.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

# 4. ATRIBUTOS DE CALIDAD DEL SOFTWARE

Los escenarios que se presentan a continuación siguen la estructura propuesta por el Software Engineering Institute (fuente, estímulo, artefacto, entorno, respuesta y medida de respuesta) y constituyen los criterios verificables con los que se evaluará la arquitectura durante la fase de pruebas.

## 4.1. Escenario de Funcionalidad

| Elemento | Descripción |
| :- | :- |
| Fuente | Operador de verificación |
| Estímulo | El operador presenta una credencial QR válida y el participante supera tanto la comparación facial como la prueba de vida |
| Artefacto | Motor de verificación multicapa (`verificacion_service` + `reglas_service`) |
| Entorno | Operación normal, iluminación adecuada y cámara funcional |
| Respuesta | El sistema evalúa los tres factores, registra la sesión con estado COMPLETADA y resultado IDENTIDAD_VERIFICADA, y habilita el envío del trámite al Simulador SID-Sunarp |
| Medida de respuesta | El 100 % de los escenarios legítimos controlados produce el resultado IDENTIDAD_VERIFICADA. Ningún factor por sí solo genera una aprobación |

## 4.2. Escenario de Usabilidad

| Elemento | Descripción |
| :- | :- |
| Fuente | Operador sin experiencia técnica previa |
| Estímulo | El operador debe ejecutar una verificación completa por primera vez |
| Artefacto | Interfaz web de pruebas (`frontend/index.html`) |
| Entorno | Estación de verificación en entorno académico controlado, con posibles distracciones |
| Respuesta | El operador completa el flujo lineal —credencial, captura facial, prueba de vida y resultado— sin asistencia externa, guiado por las cuatro secciones de la interfaz |
| Medida de respuesta | Tasa de éxito mayor o igual al 90 % en la primera sesión. El flujo no supera los cuatro pasos, conforme al requerimiento RNF-01 |

## 4.3. Escenario de Confiabilidad

| Elemento | Descripción |
| :- | :- |
| Fuente | Participante de prueba |
| Estímulo | Durante una sesión en curso, el operador abandona el proceso y transcurren más de diez minutos sin actividad |
| Artefacto | Control de vigencia de sesión (`verificacion_service`, constante `VIGENCIA_SESION`) |
| Entorno | Operación normal con interrupción imprevista |
| Respuesta | El sistema marca la sesión como EXPIRADA, registra el evento correspondiente en la bitácora y rechaza cualquier intento posterior de continuar con esa sesión |
| Medida de respuesta | El 100 % de las sesiones inactivas por más de diez minutos expira correctamente. Ninguna sesión expirada puede reanudarse, conforme a la regla RN-10 |

## 4.4. Escenario de Rendimiento

| Elemento | Descripción |
| :- | :- |
| Fuente | Operador de verificación |
| Estímulo | El operador envía una imagen facial para su comparación con la referencia registrada |
| Artefacto | Módulo de reconocimiento facial (`biometria_service` + OpenCV SFace) |
| Entorno | Equipo de desarrollo estándar, sin aceleración por GPU, con los modelos ya cargados en memoria |
| Respuesta | El sistema detecta el rostro, extrae sus características, calcula la similitud coseno frente a la referencia y devuelve el veredicto junto con la métrica de confianza |
| Medida de respuesta | Latencia promedio inferior a 3 segundos por comparación en 20 intentos consecutivos (RNF-02). El proceso completo de verificación no supera los 45 segundos (RNF-04) |

## 4.5. Escenario de Mantenibilidad

| Elemento | Descripción |
| :- | :- |
| Fuente | Integrante del equipo de desarrollo |
| Estímulo | Es necesario ajustar el umbral de coincidencia facial tras analizar los resultados de los 100 intentos controlados de evaluación |
| Artefacto | Constantes de configuración de `biometria_service` y `liveness_service` |
| Entorno | Entorno de desarrollo, sin usuarios activos |
| Respuesta | El desarrollador modifica la constante `UMBRAL_COINCIDENCIA` en un único punto del código y ejecuta la batería de pruebas automatizadas para confirmar que no se han producido regresiones |
| Medida de respuesta | El cambio se completa en menos de 5 minutos y afecta a un solo archivo. Las pruebas del motor de reglas y del orquestador continúan aprobando sin modificación |

## 4.6. Otros Escenarios

### 4.6.1. Escenario de Seguridad

| Elemento | Descripción |
| :- | :- |
| Fuente | Actor malintencionado con acceso al archivo de base de datos |
| Estímulo | El actor modifica directamente el campo `detalle` de un evento ya registrado en la tabla `eventos_auditoria`, con la intención de ocultar un rechazo previo |
| Artefacto | Bitácora de auditoría con encadenamiento criptográfico (`auditoria_service`) |
| Entorno | Acceso directo al archivo `notaryverify.db`, fuera de la aplicación |
| Respuesta | Al ejecutar la verificación de la cadena, el sistema recalcula el hash del evento alterado, detecta que no coincide con el almacenado y señala la secuencia exacta en la que se rompe la cadena |
| Medida de respuesta | El 100 % de las alteraciones deliberadas es detectado, conforme al requerimiento RNF-10 y a la regla RN-07 |

### 4.6.2. Escenario de Interoperabilidad ante fallos externos

| Elemento | Descripción |
| :- | :- |
| Fuente | Simulador SID-Sunarp |
| Estímulo | El operador envía un trámite ficticio y el servicio externo simulado responde con un escenario de error o de tiempo de espera agotado |
| Artefacto | Módulo de integración simulada (`sid_sunarp_service`) |
| Entorno | Escenario de prueba configurado deliberadamente para representar la indisponibilidad del servicio |
| Respuesta | El sistema registra el trámite con estado ERROR_SERVICIO o TIEMPO_AGOTADO, deja constancia del evento en la bitácora y no altera el resultado de la sesión de verificación ya aprobada |
| Medida de respuesta | El fallo del servicio externo no compromete la integridad de la sesión. El 100 % de los escenarios de error queda registrado y es reproducible |

### 4.6.3. Escenario de Privacidad

| Elemento | Descripción |
| :- | :- |
| Fuente | Administrador del sistema |
| Estímulo | Se intenta registrar una identidad simulada con una fotografía de referencia sin haber otorgado previamente el consentimiento biométrico del participante |
| Artefacto | Servicio de consentimiento (`consentimiento_service`) |
| Entorno | Operación normal de enrolamiento |
| Respuesta | El sistema rechaza el registro y exige el consentimiento expreso y vigente del participante antes de admitir cualquier muestra biométrica |
| Medida de respuesta | Ninguna referencia facial se almacena sin un consentimiento asociado y no revocado, en cumplimiento de la Ley N.° 29733 y su Reglamento |
