/* ═══════════════════════════════════════════════════════════════════
 * NotaryVerify — Estación de Verificación
 *
 * Interfaz de operador con captura biométrica en vivo. Consume la misma API
 * que el panel de pruebas (../index.html), pero presenta el flujo como una
 * secuencia de pantallas y toma las imágenes del vídeo en lugar de pedir
 * archivos al usuario.
 *
 * Dos modos: Verificación (el flujo de cuatro pasos) y Administración
 * (padrón de identidades, credenciales y bitácora).
 * ═══════════════════════════════════════════════════════════════════ */

const API = "http://127.0.0.1:8000";

const $ = (sel) => document.querySelector(sel);

/* Estado de la sesión de verificación en curso. */
const sesion = { id: null, codigo: null, accion: null };

/* Fotografía de referencia pendiente de enviar, de cámara o de archivo. */
let fotoReferencia = null;

/* Las etiquetas de giro se refieren a la izquierda/derecha DE LA PERSONA.
 * El backend mide el desplazamiento horizontal de la nariz respecto al centro
 * del rostro, por lo que la imagen enviada no debe ir espejada. */
const ACCIONES = {
  PARPADEO: {
    titulo: "Cierre los ojos",
    orden: "Cierre los ojos",
    detalle: "Manténgalos cerrados hasta que desaparezca el contador.",
  },
  GIRO_IZQUIERDA: {
    titulo: "Gire la cabeza a su izquierda",
    orden: "Gire a su izquierda",
    detalle: "Mantenga el giro hasta que desaparezca el contador.",
  },
  GIRO_DERECHA: {
    titulo: "Gire la cabeza a su derecha",
    orden: "Gire a su derecha",
    detalle: "Mantenga el giro hasta que desaparezca el contador.",
  },
};

const RESULTADOS = {
  IDENTIDAD_VERIFICADA: {
    clase: "veredicto--ok", glifo: "✓", titulo: "Identidad verificada",
    motivo: "El compareciente superó los tres controles configurados.",
  },
  VERIFICACION_RECHAZADA: {
    clase: "veredicto--mal", glifo: "✕", titulo: "Verificación rechazada",
    motivo: "No se cumplieron las condiciones exigidas por el motor de reglas.",
  },
  ROSTRO_NO_COINCIDENTE: {
    clase: "veredicto--mal", glifo: "✕", titulo: "Rostro no coincidente",
    motivo: "El rostro capturado no corresponde a la referencia registrada para esta credencial.",
  },
  PRUEBA_DE_VIDA_FALLIDA: {
    clase: "veredicto--mal", glifo: "✕", titulo: "Prueba de vida fallida",
    motivo: "No se detectó la acción solicitada. Podría tratarse de una fotografía o de una reproducción en pantalla.",
  },
  CREDENCIAL_NO_REGISTRADA: {
    clase: "veredicto--mal", glifo: "✕", titulo: "Credencial no registrada",
    motivo: "El código presentado no corresponde a ninguna credencial emitida.",
  },
  CREDENCIAL_REVOCADA: {
    clase: "veredicto--mal", glifo: "✕", titulo: "Credencial revocada",
    motivo: "La credencial fue revocada y no habilita ninguna verificación.",
  },
  MULTIPLES_INTENTOS_FALLIDOS: {
    clase: "veredicto--mal", glifo: "!", titulo: "Múltiples intentos fallidos",
    motivo: "La identidad quedó bloqueada tras acumular rechazos consecutivos.",
  },
  VERIFICACION_REQUIERE_REVISION: {
    clase: "veredicto--revision", glifo: "?", titulo: "Requiere revisión",
    motivo: "El resultado no es concluyente. Debe revisarlo un administrador.",
  },
};

/* ═════════════════ Utilidades de interfaz ═════════════════ */

function irA(idPantalla, numeroPaso) {
  document.querySelectorAll(".pantalla").forEach((p) =>
    p.classList.toggle("pantalla--activa", p.id === idPantalla));

  document.querySelectorAll(".paso").forEach((p) => {
    const n = Number(p.dataset.paso);
    p.classList.toggle("paso--activo", n === numeroPaso);
    p.classList.toggle("paso--hecho", n < numeroPaso);
  });
}

function mostrarError(selector, mensaje) {
  const el = $(selector);
  el.textContent = mensaje;
  el.hidden = !mensaje;
}

function mostrarExito(selector, mensaje) {
  const el = $(selector);
  el.textContent = mensaje;
  el.hidden = !mensaje;
}

function limpiarErrores() {
  ["#error-credencial", "#error-rostro", "#error-vida"].forEach((s) => mostrarError(s, ""));
}

function limpiarAvisosAdmin() {
  ["#error-admin-identidad", "#error-admin-credencial", "#error-admin-auditoria",
   "#error-padron", "#error-credenciales"].forEach((s) => mostrarError(s, ""));
  ["#ok-admin-identidad", "#ok-admin-credencial"].forEach((s) => mostrarExito(s, ""));
}

function ocupado(selectorBoton, activo) {
  const boton = $(selectorBoton);
  boton.classList.toggle("boton--cargando", activo);
  boton.disabled = activo;
}

/* Los nombres y documentos los escribe el operador, así que se escapan antes
 * de insertarlos como HTML. */
function escapar(texto) {
  const d = document.createElement("div");
  d.textContent = texto ?? "";
  return d.innerHTML;
}

function formatearFecha(iso) {
  if (!iso) return "—";
  const f = new Date(iso);
  return Number.isNaN(f.getTime()) ? iso : f.toLocaleString("es-PE");
}

/* ═════════════════ Cliente de la API ═════════════════ */

async function pedir(ruta, opciones = {}) {
  let respuesta;
  try {
    respuesta = await fetch(API + ruta, opciones);
  } catch {
    throw new Error("No se pudo contactar con la API. Verifique que el backend esté en ejecución.");
  }

  const cuerpo = await respuesta.json().catch(() => null);

  if (!respuesta.ok) {
    const detalle = cuerpo?.detail;
    if (typeof detalle === "string") throw new Error(detalle);
    if (Array.isArray(detalle)) throw new Error(detalle.map((d) => d.msg).join(" · "));
    throw new Error(`La API respondió con el código ${respuesta.status}.`);
  }
  return cuerpo;
}

async function comprobarApi() {
  const caja = $("#conexion");
  try {
    const estado = await pedir("/");
    caja.className = "conexion conexion--ok";
    $("#texto-api").textContent = estado.estado === "operativo" ? "API conectada" : estado.estado;
  } catch {
    caja.className = "conexion conexion--mal";
    $("#texto-api").textContent = "API no disponible";
  }
}

/* ═════════════════ Cámara ═════════════════ */

let flujoCamara = null;

async function abrirCamara(idVideo, idCaido, idMotivo) {
  const video = $(idVideo);

  if (!navigator.mediaDevices?.getUserMedia) {
    caerCamara(idCaido, idMotivo,
      "Este navegador no permite el acceso a la cámara. Use Chrome, Edge o Firefox actualizados.");
    return false;
  }

  try {
    if (!flujoCamara || !flujoCamara.active) {
      flujoCamara = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
    }
    video.srcObject = flujoCamara;
    $(idCaido).hidden = true;
    await video.play().catch(() => {});
    return true;
  } catch (error) {
    const motivos = {
      NotAllowedError: "Se denegó el permiso de cámara. Autorícelo desde el icono de la barra de direcciones y recargue la página.",
      NotFoundError: "No se detectó ninguna cámara conectada al equipo.",
      NotReadableError: "La cámara está siendo utilizada por otra aplicación o pestaña.",
      SecurityError: "El navegador bloquea la cámara en este origen. Debe servirse desde localhost o mediante HTTPS.",
    };
    caerCamara(idCaido, idMotivo, motivos[error.name] || `No se pudo abrir la cámara (${error.name}).`);
    return false;
  }
}

function caerCamara(idCaido, idMotivo, mensaje) {
  $(idCaido).hidden = false;
  $(idMotivo).textContent = mensaje;
}

function cerrarCamara() {
  if (!flujoCamara) return;
  flujoCamara.getTracks().forEach((t) => t.stop());
  flujoCamara = null;
}

/* Captura el fotograma actual SIN espejar: la vista previa está invertida solo
 * por CSS, para que resulte natural al operador. */
function capturarFotograma(idVideo) {
  const video = $(idVideo);
  if (!video.videoWidth) {
    throw new Error("La cámara aún no entrega imagen. Espere un instante e inténtelo de nuevo.");
  }
  const lienzo = $("#lienzo");
  lienzo.width = video.videoWidth;
  lienzo.height = video.videoHeight;
  lienzo.getContext("2d").drawImage(video, 0, 0);

  return new Promise((resolver, rechazar) => {
    lienzo.toBlob(
      (blob) => (blob ? resolver(blob) : rechazar(new Error("No se pudo procesar la imagen capturada."))),
      "image/jpeg",
      0.92,
    );
  });
}

function comoFormulario(blob, nombre) {
  const datos = new FormData();
  datos.append("imagen", blob, nombre);
  return datos;
}

/* ═══════════════════════════════════════════════════════════════════
 *                          VERIFICACIÓN
 * ═══════════════════════════════════════════════════════════════════ */

/* ── Paso 1 · Credencial ── */

$("#boton-iniciar").addEventListener("click", iniciarVerificacion);
$("#entrada-codigo").addEventListener("keydown", (e) => {
  if (e.key === "Enter") iniciarVerificacion();
});

async function iniciarVerificacion() {
  const codigo = $("#entrada-codigo").value.trim().toUpperCase();
  limpiarErrores();

  if (!codigo) {
    mostrarError("#error-credencial", "Introduzca el código de la credencial.");
    return;
  }

  ocupado("#boton-iniciar", true);

  try {
    const nueva = await pedir("/verificaciones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ codigo_credencial: codigo }),
    });

    sesion.id = nueva.id;
    sesion.codigo = codigo;
    sesion.accion = null;

    /* Una credencial no registrada o revocada cierra la sesión de inmediato:
     * el backend ya emitió el veredicto, así que se salta al resultado sin
     * llegar a abrir la cámara. */
    if (nueva.estado === "COMPLETADA") {
      pintarResultado(nueva);
      return;
    }

    irA("pantalla-rostro", 2);
    await abrirCamara("#video-rostro", "#sin-camara-rostro", "#motivo-camara-rostro");
  } catch (error) {
    mostrarError("#error-credencial", error.message);
  } finally {
    ocupado("#boton-iniciar", false);
  }
}

/* ── Paso 2 · Rostro ── */

$("#boton-capturar-rostro").addEventListener("click", async () => {
  limpiarErrores();
  try {
    const blob = await capturarFotograma("#video-rostro");
    await enviarRostro(blob);
  } catch (error) {
    mostrarError("#error-rostro", error.message);
  }
});

$("#archivo-rostro").addEventListener("change", async (e) => {
  const archivo = e.target.files[0];
  if (!archivo) return;
  limpiarErrores();
  try {
    await enviarRostro(archivo);
  } catch (error) {
    mostrarError("#error-rostro", error.message);
  }
});

async function enviarRostro(blob) {
  ocupado("#boton-capturar-rostro", true);
  try {
    const estado = await pedir(`/verificaciones/${sesion.id}/rostro`, {
      method: "POST",
      body: comoFormulario(blob, "rostro.jpg"),
    });

    /* Si el rostro no coincide, el backend cierra la sesión sin llegar a la
     * prueba de vida. */
    if (estado.estado === "COMPLETADA") {
      pintarResultado(estado);
      return;
    }

    sortearAccion();
    irA("pantalla-vida", 3);
    await abrirCamara("#video-vida", "#sin-camara-vida", "#motivo-camara-vida");
  } finally {
    ocupado("#boton-capturar-rostro", false);
  }
}

/* ── Paso 3 · Prueba de vida ── */

function sortearAccion() {
  const claves = Object.keys(ACCIONES);
  let nueva;
  do {
    nueva = claves[Math.floor(Math.random() * claves.length)];
  } while (claves.length > 1 && nueva === sesion.accion);

  sesion.accion = nueva;
  $("#texto-accion").textContent = ACCIONES[nueva].titulo;
  $("#detalle-accion").textContent = ACCIONES[nueva].detalle;
}

$("#boton-otra-accion").addEventListener("click", sortearAccion);

$("#boton-ejecutar-vida").addEventListener("click", async () => {
  limpiarErrores();
  ocupado("#boton-ejecutar-vida", true);

  try {
    await cuentaAtras();
    const blob = await capturarFotograma("#video-vida");
    ocultarCuenta();
    await enviarPruebaVida(blob);
  } catch (error) {
    ocultarCuenta();
    mostrarError("#error-vida", error.message);
  } finally {
    ocupado("#boton-ejecutar-vida", false);
  }
});

$("#archivo-vida").addEventListener("change", async (e) => {
  const archivo = e.target.files[0];
  if (!archivo) return;
  limpiarErrores();
  try {
    await enviarPruebaVida(archivo);
  } catch (error) {
    mostrarError("#error-vida", error.message);
  }
});

/* Perímetro del anillo: 2·π·r con r = 52 (ver estilos.css). */
const PERIMETRO = 2 * Math.PI * 52;

function cuentaAtras() {
  return new Promise((resolver) => {
    const caja = $("#cuenta");
    const avance = $("#cuenta-avance");
    const cifra = $("#cuenta-cifra");
    const orden = $("#cuenta-orden");

    const TOTAL = 3;
    let restante = TOTAL;

    caja.hidden = false;
    orden.hidden = true;
    cifra.hidden = false;
    avance.style.transition = "none";
    avance.style.strokeDashoffset = "0";
    cifra.textContent = restante;

    /* Fuerza un reflujo para que la transición del anillo arranque desde el
     * valor recién fijado y no se pierda el primer tramo. */
    void avance.getBoundingClientRect();
    avance.style.transition = "stroke-dashoffset 1s linear";

    const paso = () => {
      restante -= 1;
      avance.style.strokeDashoffset = String((PERIMETRO * (TOTAL - restante)) / TOTAL);

      if (restante > 0) {
        cifra.textContent = restante;
        cifra.style.animation = "none";
        void cifra.getBoundingClientRect();
        cifra.style.animation = "";
        return;
      }

      clearInterval(reloj);
      /* Al llegar a cero se muestra la orden en palabras y se concede un
       * margen para que la persona complete la acción antes del disparo. */
      cifra.hidden = true;
      orden.hidden = false;
      orden.textContent = ACCIONES[sesion.accion].orden;
      setTimeout(resolver, 900);
    };

    const reloj = setInterval(paso, 1000);
  });
}

function ocultarCuenta() {
  $("#cuenta").hidden = true;
  $("#cuenta-orden").hidden = true;
  $("#cuenta-cifra").hidden = false;
}

async function enviarPruebaVida(blob) {
  const estado = await pedir(
    `/verificaciones/${sesion.id}/prueba-vida?accion=${encodeURIComponent(sesion.accion)}`,
    { method: "POST", body: comoFormulario(blob, "prueba-vida.jpg") },
  );
  pintarResultado(estado);
}

/* ── Paso 4 · Resultado ── */

function pintarResultado(estado) {
  cerrarCamara();

  const info = RESULTADOS[estado.resultado] || {
    clase: "veredicto--revision", glifo: "?",
    titulo: estado.resultado || "Sin resultado",
    motivo: "El sistema no devolvió un resultado reconocido.",
  };

  const panel = $("#veredicto");
  panel.className = `panel panel--veredicto ${info.clase}`;
  $("#sello-glifo").textContent = info.glifo;
  $("#veredicto-titulo").textContent = info.titulo;
  $("#veredicto-motivo").textContent = info.motivo;

  pintarFactores(estado);
  pintarDetalle(estado);
  irA("pantalla-resultado", 4);
}

function pintarFactores(estado) {
  const credencialOk = !["CREDENCIAL_NO_REGISTRADA", "CREDENCIAL_REVOCADA"].includes(estado.resultado);

  const filas = [
    {
      etiqueta: "Credencial",
      estado: credencialOk ? "ok" : "mal",
      valor: credencialOk ? "válida" : "no válida",
    },
    {
      etiqueta: "Reconocimiento facial",
      estado: estado.rostro_coincide === true ? "ok" : estado.rostro_coincide === false ? "mal" : "nd",
      valor: estado.confianza_facial != null
        ? `confianza ${Number(estado.confianza_facial).toFixed(2)}`
        : "no evaluado",
    },
    {
      etiqueta: "Prueba de vida",
      estado: estado.prueba_vida_superada === true ? "ok" : estado.prueba_vida_superada === false ? "mal" : "nd",
      valor: estado.prueba_vida_superada == null
        ? "no evaluada"
        : (ACCIONES[sesion.accion]?.orden.toLowerCase() || sesion.accion || "—"),
    },
  ];

  const glifos = { ok: "✓", mal: "✕", nd: "–" };

  $("#factores").innerHTML = filas.map((f) => `
    <li data-estado="${f.estado}" data-icono="${glifos[f.estado]}">
      ${f.etiqueta}<span>${f.valor}</span>
    </li>`).join("");
}

function pintarDetalle(estado) {
  const campos = [
    ["Sesión", estado.id],
    ["Credencial", sesion.codigo || "—"],
    ["Estado", estado.estado],
    ["Resultado", estado.resultado || "—"],
    ["Inicio", formatearFecha(estado.fecha_inicio)],
    ["Fin", formatearFecha(estado.fecha_fin)],
  ];
  $("#detalle-lista").innerHTML = campos
    .map(([k, v]) => `<dt>${k}</dt><dd>${escapar(String(v))}</dd>`)
    .join("");
}

/* ── Reinicio ── */

$("#boton-nueva").addEventListener("click", reiniciar);
document.querySelectorAll("[data-volver]").forEach((b) => b.addEventListener("click", reiniciar));

function reiniciar() {
  cerrarCamara();
  ocultarCuenta();
  limpiarErrores();
  sesion.id = null;
  sesion.codigo = null;
  sesion.accion = null;
  $("#entrada-codigo").value = "";
  irA("pantalla-credencial", 1);
  $("#entrada-codigo").focus();
}

/* ═══════════════════════════════════════════════════════════════════
 *                          ADMINISTRACIÓN
 * ═══════════════════════════════════════════════════════════════════ */

/* ── Cambio de modo ── */

$("#modo-verificar").addEventListener("click", () => cambiarModo("verificar"));
$("#modo-administrar").addEventListener("click", () => cambiarModo("administrar"));

async function cambiarModo(modo) {
  cerrarCamara();
  limpiarErrores();
  limpiarAvisosAdmin();

  const admin = modo === "administrar";
  $("#modo-verificar").classList.toggle("modo--activo", !admin);
  $("#modo-administrar").classList.toggle("modo--activo", admin);
  $("#pasos").hidden = admin;

  if (admin) {
    document.querySelectorAll(".pantalla").forEach((p) =>
      p.classList.toggle("pantalla--activa", p.id === "pantalla-admin"));
    irAVista("vista-padron");
    irAVista("vista-credenciales");
    irASeccion("identidades");
    cargarCredenciales();
  } else {
    reiniciar();
  }
}

/* ── Subsecciones ── */

document.querySelectorAll("[data-seccion]").forEach((ficha) =>
  ficha.addEventListener("click", () => irASeccion(ficha.dataset.seccion)));

function irASeccion(nombre) {
  document.querySelectorAll(".subnav__ficha").forEach((f) =>
    f.classList.toggle("subnav__ficha--activa", f.dataset.seccion === nombre));
  document.querySelectorAll(".seccion").forEach((s) =>
    s.classList.toggle("seccion--activa", s.id === `seccion-${nombre}`));

  /* La cámara solo se enciende al abrir el formulario de enrolamiento, no al
   * entrar en la sección. */
  cerrarCamara();
  if (nombre === "identidades") cargarPadron();
  if (nombre === "credenciales") cargarCredenciales();
}

/* ── Vistas dentro de cada subsección (listado ↔ formulario) ── */

function irAVista(idVista) {
  const seccion = $(`#${idVista}`).closest(".seccion");
  seccion.querySelectorAll(".vista").forEach((v) =>
    v.classList.toggle("vista--activa", v.id === idVista));
}

$("#boton-nueva-identidad").addEventListener("click", () => {
  limpiarAvisosAdmin();
  irAVista("vista-enrolar");
  abrirCamara("#video-enrolar", "#sin-camara-enrolar", "#motivo-camara-enrolar");
  $("#adm-participante").focus();
});

$("#boton-cancelar-enrolar").addEventListener("click", () => {
  cerrarCamara();
  limpiarAvisosAdmin();
  irAVista("vista-padron");
});

$("#boton-nueva-credencial").addEventListener("click", () => {
  limpiarAvisosAdmin();
  $("#credencial-emitida").hidden = true;
  irAVista("vista-emitir");
  $("#adm-id-identidad").focus();
});

$("#boton-cancelar-emitir").addEventListener("click", () => {
  limpiarAvisosAdmin();
  $("#credencial-emitida").hidden = true;
  irAVista("vista-credenciales");
});

/* ── Enrolamiento: consentimiento ── */

$("#boton-consentimiento").addEventListener("click", async () => {
  limpiarAvisosAdmin();
  const id = $("#adm-participante").value.trim();
  if (!id) {
    mostrarError("#error-admin-identidad", "Indique el ID del participante voluntario.");
    return;
  }

  ocupado("#boton-consentimiento", true);
  try {
    await pedir("/identidades/consentimientos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id_participante: id,
        alcance: $("#adm-alcance").value.trim() || "Pruebas academicas",
      }),
    });
    mostrarExito("#ok-admin-identidad", `Consentimiento registrado para ${id}.`);
  } catch (error) {
    mostrarError("#error-admin-identidad", error.message);
  } finally {
    ocupado("#boton-consentimiento", false);
  }
});

/* ── Enrolamiento: fotografía ── */

$("#boton-tomar-foto").addEventListener("click", async () => {
  limpiarAvisosAdmin();
  try {
    fotoReferencia = await capturarFotograma("#video-enrolar");
    previsualizar(fotoReferencia);
  } catch (error) {
    mostrarError("#error-admin-identidad", error.message);
  }
});

$("#adm-archivo").addEventListener("change", (e) => {
  const archivo = e.target.files[0];
  if (!archivo) return;
  limpiarAvisosAdmin();
  fotoReferencia = archivo;
  previsualizar(archivo);
});

function previsualizar(blob) {
  const img = $("#foto-tomada");
  if (img.src.startsWith("blob:")) URL.revokeObjectURL(img.src);
  img.src = URL.createObjectURL(blob);
  img.hidden = false;
  $("#boton-tomar-foto").querySelector(".boton__texto").textContent = "Repetir fotografía";
}

function descartarFoto() {
  const img = $("#foto-tomada");
  if (img.src.startsWith("blob:")) URL.revokeObjectURL(img.src);
  img.removeAttribute("src");
  img.hidden = true;
  fotoReferencia = null;
  $("#boton-tomar-foto").querySelector(".boton__texto").textContent = "Tomar fotografía";
}

/* ── Enrolamiento: registro ── */

$("#boton-registrar-identidad").addEventListener("click", async () => {
  limpiarAvisosAdmin();

  const nombre = $("#adm-nombre").value.trim();
  const documento = $("#adm-documento").value.trim();
  const participante = $("#adm-participante").value.trim();

  if (!nombre || !documento || !participante) {
    mostrarError("#error-admin-identidad", "Complete nombre ficticio, documento y ID del participante.");
    return;
  }
  if (!fotoReferencia) {
    mostrarError("#error-admin-identidad", "Tome o suba la fotografía de referencia.");
    return;
  }
  if (!$("#adm-ficticio").checked) {
    mostrarError("#error-admin-identidad", "Debe confirmar que los datos son ficticios (regla RN-02).");
    return;
  }

  const datos = new FormData();
  datos.append("nombre_ficticio", nombre);
  datos.append("documento_ficticio", documento);
  datos.append("id_participante", participante);
  datos.append("confirmo_dato_ficticio", "true");
  datos.append("imagen_referencia", fotoReferencia, "referencia.jpg");

  ocupado("#boton-registrar-identidad", true);
  try {
    const identidad = await pedir("/identidades", { method: "POST", body: datos });
    descartarFoto();
    $("#adm-ficticio").checked = false;
    $("#adm-nombre").value = "";
    $("#adm-documento").value = "";
    cerrarCamara();
    irAVista("vista-padron");
    cargarPadron();
    mostrarExito("#ok-admin-identidad",
      `Identidad ${identidad.nombre_ficticio} registrada. Ya puede emitirle una credencial.`);
  } catch (error) {
    mostrarError("#error-admin-identidad", error.message);
  } finally {
    ocupado("#boton-registrar-identidad", false);
  }
});

/* ── Padrón de identidades ── */

$("#boton-refrescar-padron").addEventListener("click", cargarPadron);

async function cargarPadron() {
  mostrarError("#error-padron", "");
  ocupado("#boton-refrescar-padron", true);

  try {
    /* Se piden ambos listados a la vez y se cruzan en el cliente: así se
     * muestra cuántas credenciales activas tiene cada identidad sin añadir un
     * endpoint específico para ese conteo. */
    const [identidades, credenciales] = await Promise.all([
      pedir("/identidades"),
      pedir("/credenciales"),
    ]);

    const porIdentidad = new Map();
    for (const c of credenciales) {
      const cuenta = porIdentidad.get(c.id_identidad) || { activas: 0, total: 0 };
      cuenta.total += 1;
      if (c.estado === "ACTIVA") cuenta.activas += 1;
      porIdentidad.set(c.id_identidad, cuenta);
    }

    $("#cifra-identidades").textContent = identidades.length;
    $("#padron-vacio").hidden = identidades.length > 0;
    $("#padron-envoltura").hidden = identidades.length === 0;

    $("#padron-filas").innerHTML = identidades.map((i) => {
      const cuenta = porIdentidad.get(i.id) || { activas: 0, total: 0 };
      const bloqueada = i.estado === "BLOQUEADA";
      return `
        <tr>
          <td>${escapar(i.nombre_ficticio)}</td>
          <td class="mono">${escapar(i.documento_ficticio)}</td>
          <td><span class="marbete marbete--${bloqueada ? "bloqueada" : "activa"}">${i.estado}</span></td>
          <td class="tabla__centro cuenta-credenciales">${cuenta.activas} <span>de ${cuenta.total}</span></td>
          <td class="mono">${formatearFecha(i.fecha_registro)}</td>
          <td class="acciones-fila">
            <button class="boton boton--fila" data-identidad="${i.id}">Credencial</button>
            <button class="boton boton--fila boton--fila-neutro"
                    data-editar="${i.id}"
                    data-nombre="${escapar(i.nombre_ficticio)}"
                    data-documento="${escapar(i.documento_ficticio)}">Editar</button>
            <button class="boton boton--fila ${bloqueada ? "boton--fila-ok" : "boton--fila-aviso"}"
                    data-estado="${i.id}"
                    data-nuevo="${bloqueada ? "ACTIVA" : "BLOQUEADA"}">${bloqueada ? "Reactivar" : "Desactivar"}</button>
          </td>
        </tr>`;
    }).join("");

    document.querySelectorAll("[data-identidad]").forEach((boton) =>
      boton.addEventListener("click", () => {
        $("#adm-id-identidad").value = boton.dataset.identidad;
        irASeccion("credenciales");
        irAVista("vista-emitir");
        $("#adm-id-identidad").focus();
      }));

    document.querySelectorAll("[data-editar]").forEach((boton) =>
      boton.addEventListener("click", () => editarIdentidad(boton.dataset)));

    document.querySelectorAll("[data-estado]").forEach((boton) =>
      boton.addEventListener("click", () => cambiarEstado(boton.dataset.estado, boton.dataset.nuevo)));
  } catch (error) {
    mostrarError("#error-padron", error.message);
  } finally {
    ocupado("#boton-refrescar-padron", false);
  }
}

async function editarIdentidad({ editar: id, nombre, documento }) {
  const nuevoNombre = prompt("Nombre ficticio:", nombre);
  if (nuevoNombre === null) return;
  const nuevoDocumento = prompt("Documento ficticio:", documento);
  if (nuevoDocumento === null) return;

  mostrarError("#error-padron", "");
  try {
    await pedir(`/identidades/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nombre_ficticio: nuevoNombre.trim(),
        documento_ficticio: nuevoDocumento.trim(),
      }),
    });
    cargarPadron();
    cargarCredenciales();
  } catch (error) {
    mostrarError("#error-padron", error.message);
  }
}

async function cambiarEstado(id, estado) {
  /* Desactivar impide que la identidad supere ninguna verificación, así que
   * se confirma antes. Reactivar no lo necesita: solo restituye. */
  if (estado === "BLOQUEADA" &&
      !confirm("Al desactivarla, esta identidad no podrá superar ninguna verificación. ¿Continuar?")) {
    return;
  }

  mostrarError("#error-padron", "");
  try {
    await pedir(`/identidades/${id}/estado`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ estado }),
    });
    cargarPadron();
  } catch (error) {
    mostrarError("#error-padron", error.message);
  }
}

/* ── Emisión de credencial ── */

$("#boton-emitir").addEventListener("click", async () => {
  limpiarAvisosAdmin();
  const idIdentidad = $("#adm-id-identidad").value.trim();
  if (!idIdentidad) {
    mostrarError("#error-admin-credencial", "Indique el ID de la identidad.");
    return;
  }

  ocupado("#boton-emitir", true);
  try {
    const credencial = await pedir("/credenciales", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_identidad: idIdentidad, tipo: "QR" }),
    });

    $("#credencial-codigo").textContent = credencial.codigo;
    $("#credencial-qr").src = `${API}/credenciales/${encodeURIComponent(credencial.codigo)}/qr`;
    $("#credencial-emitida").hidden = false;
    mostrarExito("#ok-admin-credencial", "Credencial emitida y activa.");
    cargarCredenciales();
  } catch (error) {
    mostrarError("#error-admin-credencial", error.message);
  } finally {
    ocupado("#boton-emitir", false);
  }
});

$("#boton-usar-codigo").addEventListener("click", async () => {
  const codigo = $("#credencial-codigo").textContent.trim();
  if (!codigo || codigo === "—") return;
  await cambiarModo("verificar");
  $("#entrada-codigo").value = codigo;
  $("#entrada-codigo").focus();
});

$("#boton-copiar-codigo").addEventListener("click", async () => {
  const codigo = $("#credencial-codigo").textContent.trim();
  const boton = $("#boton-copiar-codigo");
  try {
    await navigator.clipboard.writeText(codigo);
    boton.textContent = "Copiado";
  } catch {
    boton.textContent = "No se pudo copiar";
  }
  setTimeout(() => { boton.textContent = "Copiar"; }, 1800);
});

/* ── Listado de credenciales ── */

$("#boton-refrescar-credenciales").addEventListener("click", cargarCredenciales);

async function cargarCredenciales() {
  mostrarError("#error-credenciales", "");
  ocupado("#boton-refrescar-credenciales", true);

  try {
    const [credenciales, identidades] = await Promise.all([
      pedir("/credenciales"),
      pedir("/identidades"),
    ]);

    const nombres = new Map(identidades.map((i) => [i.id, i.nombre_ficticio]));

    $("#cifra-credenciales").textContent = credenciales.length;
    $("#credenciales-vacio").hidden = credenciales.length > 0;
    $("#credenciales-envoltura").hidden = credenciales.length === 0;

    $("#credenciales-filas").innerHTML = credenciales.map((c) => {
      const revocada = c.estado === "REVOCADA";
      return `
        <tr>
          <td class="mono">${escapar(c.codigo)}</td>
          <td>${escapar(nombres.get(c.id_identidad) || "—")}</td>
          <td>${escapar(c.tipo)}</td>
          <td><span class="marbete marbete--${revocada ? "revocada" : "activa"}">${c.estado}</span></td>
          <td class="mono">${formatearFecha(c.fecha_emision)}</td>
          <td class="acciones-fila">${revocada
            ? `<span class="sin-accion">—</span>`
            : `<button class="boton boton--fila" data-credencial="${escapar(c.codigo)}">Usar</button>
               <button class="boton boton--fila boton--fila-aviso" data-revocar="${c.id}" data-codigo="${escapar(c.codigo)}">Revocar</button>`}</td>
        </tr>`;
    }).join("");

    document.querySelectorAll("[data-credencial]").forEach((boton) =>
      boton.addEventListener("click", async () => {
        await cambiarModo("verificar");
        $("#entrada-codigo").value = boton.dataset.credencial;
        $("#entrada-codigo").focus();
      }));

    document.querySelectorAll("[data-revocar]").forEach((boton) =>
      boton.addEventListener("click", () => revocarCredencial(boton.dataset.revocar, boton.dataset.codigo)));
  } catch (error) {
    mostrarError("#error-credenciales", error.message);
  } finally {
    ocupado("#boton-refrescar-credenciales", false);
  }
}

async function revocarCredencial(id, codigo) {
  if (!confirm(`La credencial ${codigo} dejará de habilitar verificaciones. ¿Revocarla?`)) return;

  mostrarError("#error-credenciales", "");
  try {
    await pedir(`/credenciales/${encodeURIComponent(id)}/revocar`, { method: "POST" });
    cargarCredenciales();
    cargarPadron();
  } catch (error) {
    mostrarError("#error-credenciales", error.message);
  }
}

/* ── Auditoría ── */

$("#boton-verificar-cadena").addEventListener("click", async () => {
  limpiarAvisosAdmin();
  ocupado("#boton-verificar-cadena", true);
  try {
    const cadena = await pedir("/auditoria/verificar-cadena");
    const caja = $("#cadena-estado");
    caja.hidden = false;

    if (cadena.valida) {
      caja.className = "cadena cadena--ok";
      caja.dataset.glifo = "✓";
      caja.textContent = `Cadena íntegra. ${cadena.total_eventos} eventos enlazados sin alteraciones.`;
    } else {
      caja.className = "cadena cadena--rota";
      caja.dataset.glifo = "✕";
      caja.textContent =
        `Cadena rota. La alteración se detecta a partir del evento ${cadena.primer_evento_alterado}.`;
    }
  } catch (error) {
    mostrarError("#error-admin-auditoria", error.message);
  } finally {
    ocupado("#boton-verificar-cadena", false);
  }
});

$("#boton-listar-eventos").addEventListener("click", async () => {
  limpiarAvisosAdmin();
  ocupado("#boton-listar-eventos", true);
  try {
    const eventos = await pedir("/auditoria/eventos");
    $("#tabla-eventos").innerHTML = eventos.map((e) => `
      <tr>
        <td class="tabla__centro mono">${e.secuencia}</td>
        <td>${escapar(e.tipo_evento)}</td>
        <td class="mono">${e.hash_evento_anterior.slice(0, 16)}…</td>
        <td class="mono">${e.hash_evento_actual.slice(0, 16)}…</td>
      </tr>`).join("");
    $("#tabla-envoltura").hidden = eventos.length === 0;
    if (!eventos.length) {
      mostrarError("#error-admin-auditoria", "La bitácora todavía no tiene eventos.");
    }
  } catch (error) {
    mostrarError("#error-admin-auditoria", error.message);
  } finally {
    ocupado("#boton-listar-eventos", false);
  }
});

/* ═════════════════ Arranque ═════════════════ */

window.addEventListener("beforeunload", cerrarCamara);

irA("pantalla-credencial", 1);
comprobarApi();
setInterval(comprobarApi, 15000);
