/* Dashboard de utilización de NotaryVerify: consume GET /dashboard/uso.
   Reutiliza el token de la estación (misma clave en sessionStorage). */

const API = window.NOTARYVERIFY_API || "http://127.0.0.1:8000";
const CLAVE_TOKEN = "notaryverify_token";
const COLORES = ["#5aa0f5", "#3ecf96", "#dcb85a", "#f0605c", "#e8973f", "#a78bfa", "#7d93b3", "#8ec2ff"];
const graficos = {};

const $ = (id) => document.getElementById(id);

function leerToken() {
  try { return sessionStorage.getItem(CLAVE_TOKEN); } catch { return null; }
}

function guardarToken(valor) {
  try {
    if (valor) sessionStorage.setItem(CLAVE_TOKEN, valor);
    else sessionStorage.removeItem(CLAVE_TOKEN);
  } catch { /* sin almacenamiento: el token vive solo en esta página */ }
}

let token = leerToken();

function mostrarEstado(texto) { $("estado").textContent = texto || ""; }

function porcentaje(valor) { return valor === null || valor === undefined ? "—" : `${(valor * 100).toFixed(1)} %`; }

async function pedir(ruta, opciones = {}) {
  const headers = new Headers(opciones.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const respuesta = await fetch(`${API}${ruta}`, { ...opciones, headers });
  if (respuesta.status === 401) { cerrarSesion(); throw new Error("Sesión no válida. Ingrese nuevamente."); }
  if (respuesta.status === 403) throw new Error("El dashboard requiere rol Administrador o Auditor.");
  if (!respuesta.ok) throw new Error(`Error ${respuesta.status} al consultar la API.`);
  return respuesta.json();
}

function cerrarSesion() {
  token = null;
  guardarToken(null);
  $("login").hidden = false;
  $("filtros").hidden = true;
  $("graficos").hidden = true;
  $("kpis").innerHTML = "";
}

function dibujar(id, tipo, etiquetas, valores, etiqueta) {
  if (graficos[id]) graficos[id].destroy();
  const circular = tipo === "doughnut";
  graficos[id] = new Chart($(id), {
    type: tipo,
    data: {
      labels: etiquetas,
      datasets: [{
        label: etiqueta,
        data: valores,
        backgroundColor: circular ? COLORES : COLORES[0],
        borderColor: circular ? "#0b1220" : COLORES[0],
        borderWidth: circular ? 2 : 1,
        borderRadius: tipo === "bar" ? 6 : 0,
        tension: 0.3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: circular, position: "bottom", labels: { color: "#c6d4e8" } } },
      scales: circular ? {} : {
        x: { ticks: { color: "#7d93b3" }, grid: { color: "#162339" } },
        y: { beginAtZero: true, ticks: { color: "#7d93b3", precision: 0 }, grid: { color: "#162339" } },
      },
    },
  });
  $(id).parentElement.style.height = "320px";
}

function dibujarMapa(id, mapa, etiqueta) {
  const entradas = Object.entries(mapa || {});
  if (!entradas.length) entradas.push(["Sin datos", 0]);
  dibujar(id, "doughnut", entradas.map(([k]) => k), entradas.map(([, v]) => v), etiqueta);
}

function pintarKpis(datos) {
  const t = datos.totales;
  const kpis = [
    ["Sesiones", t.sesiones],
    ["En curso", t.sesiones_en_curso],
    ["Tasa de aprobación", porcentaje(datos.tasas.aprobacion)],
    ["Prueba de vida superada", porcentaje(datos.tasas.prueba_vida_superada)],
    ["Confianza facial media", datos.tasas.confianza_facial_promedio ?? "—"],
    ["Identidades", t.identidades],
    ["Credenciales activas", t.credenciales_activas],
    ["Documentos", t.documentos],
    ["Eventos de auditoría", t.eventos_auditoria],
    ["Alertas activas", t.alertas_activas],
  ];
  $("kpis").replaceChildren(...kpis.map(([nombre, valor]) => {
    const tarjeta = document.createElement("div");
    tarjeta.className = "kpi";
    const span = document.createElement("span");
    span.textContent = nombre;
    const strong = document.createElement("strong");
    strong.textContent = valor;
    tarjeta.append(span, strong);
    return tarjeta;
  }));
}

async function cargar() {
  mostrarEstado("Cargando métricas…");
  try {
    const datos = await pedir(`/dashboard/uso?dias=${$("dias").value}`);
    $("login").hidden = true;
    $("filtros").hidden = false;
    $("graficos").hidden = false;
    pintarKpis(datos);
    dibujar("g-dia", "line", datos.sesiones_por_dia.map((d) => d.fecha.slice(5)),
      datos.sesiones_por_dia.map((d) => d.sesiones), "Sesiones");
    dibujarMapa("g-resultado", datos.sesiones_por_resultado, "Resultados");
    dibujarMapa("g-estado", datos.sesiones_por_estado, "Estados");
    dibujarMapa("g-tramite", datos.tramites_por_estado, "Trámites");
    dibujarMapa("g-credencial", datos.credenciales_por_tipo, "Credenciales");
    dibujarMapa("g-rol", datos.usuarios_por_rol, "Usuarios");
    mostrarEstado(`Actualizado ${new Date().toLocaleString()}`);
  } catch (error) {
    mostrarEstado(error.message === "Failed to fetch" ? "No se pudo conectar con la API." : error.message);
  }
}

$("login").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  mostrarEstado("Ingresando…");
  try {
    const respuesta = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ correo: $("correo").value, password: $("password").value }),
    });
    if (!respuesta.ok) throw new Error("Credenciales inválidas.");
    token = (await respuesta.json()).access_token;
    guardarToken(token);
    $("password").value = "";
    await cargar();
  } catch (error) {
    mostrarEstado(error.message === "Failed to fetch" ? "No se pudo conectar con la API." : error.message);
  }
});

$("actualizar").addEventListener("click", cargar);
$("dias").addEventListener("change", cargar);
$("salir").addEventListener("click", async () => {
  try { await pedir("/auth/logout", { method: "POST" }); } catch { /* descartar token local */ }
  cerrarSesion();
  mostrarEstado("Sesión cerrada.");
});

if (token) cargar();
