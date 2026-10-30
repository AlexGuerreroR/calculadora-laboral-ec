// Calculadora Laboral EC · frontend
// Reglas (guía semana 2 y clase del miércoles):
//  - El frontend habla SOLO con nuestro backend; nunca con el modelo ni con una clave.
//  - Deshabilita el botón mientras espera y muestra errores comprensibles.
//  - Todo texto se muestra con textContent (nunca innerHTML): la salida del modelo es texto, no HTML.

const $ = (id) => document.getElementById(id);
let ultimoResultado = null;

// ---------------------------------------------------------------- utilidades
const usd = (n) => n.toLocaleString("es-EC", { style: "currency", currency: "USD" });

function tipoElegido() {
  return document.querySelector('input[name="tipo"]:checked').value;
}

function mostrarError(elemento, mensaje) {
  elemento.textContent = mensaje;
  elemento.hidden = false;
}

function ocultar(...elementos) {
  elementos.forEach((e) => { e.hidden = true; });
}

function llenarLista(lista, textos) {
  lista.replaceChildren(...textos.map((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    return li;
  }));
}

// Convierte una respuesta de error del backend (RFC 9457) en un mensaje para el usuario.
async function mensajeDeError(respuesta) {
  try {
    const p = await respuesta.json();
    let texto = p.detail || "Ocurrió un error.";
    if (Array.isArray(p.campos) && p.campos.length) {
      texto += " " + p.campos.map((c) => `${c.campo || "dato"}: ${c.mensaje}`).join(" · ");
    }
    if (respuesta.status === 429 && respuesta.headers.get("Retry-After")) {
      texto += ` (espere ${respuesta.headers.get("Retry-After")} s)`;
    }
    return texto;
  } catch {
    return `El servidor respondió con un error (${respuesta.status}).`;
  }
}

async function enviar(ruta, cuerpo, boton, textoEspera) {
  const original = boton.textContent;
  boton.disabled = true;
  boton.textContent = textoEspera;
  try {
    const r = await fetch(ruta, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo),
    });
    if (!r.ok) throw new Error(await mensajeDeError(r));
    return await r.json();
  } catch (e) {
    if (e instanceof TypeError) throw new Error("No se pudo conectar con el servidor. Revise su conexión e intente de nuevo.");
    throw e;
  } finally {
    boton.disabled = false;
    boton.textContent = original;
  }
}

// ---------------------------------------------------------------- formulario según el tipo
document.querySelectorAll('input[name="tipo"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    document.querySelectorAll("[data-para]").forEach((bloque) => {
      bloque.hidden = bloque.dataset.para !== tipoElegido();
    });
    ocultar($("resultado"), $("explicacion"), $("errorCalculo"));
    $("estadoVacio").hidden = false;
  });
});

function armarSolicitud() {
  const tipo = tipoElegido();
  if (tipo === "decimo_tercero") {
    const sueldo = Number($("sueldo13").value);
    const meses = Number($("meses13").value);
    if (!(sueldo > 0)) throw new Error("Ingrese un sueldo mensual mayor que 0.");
    if (!Number.isInteger(meses) || meses < 1 || meses > 12) throw new Error("Los meses deben ser un número entero de 1 a 12.");
    return ["/calculos/decimos", { tipo, remuneraciones: Array(meses).fill(sueldo) }];
  }
  if (tipo === "decimo_cuarto") {
    const meses = Number($("meses14").value);
    if (!Number.isInteger(meses) || meses < 1 || meses > 12) throw new Error("Los meses deben ser un número entero de 1 a 12.");
    return ["/calculos/decimos", { tipo, meses_trabajados: meses, region: $("region").value }];
  }
  if (tipo === "liquidacion") {
    const sueldoLiq = Number($("sueldoLiq").value);
    if (!(sueldoLiq > 0)) throw new Error("Ingrese el último sueldo mensual, mayor que 0.");
    if (!$("ingresoLiq").value || !$("salidaLiq").value) throw new Error("Ingrese la fecha de ingreso y el último día de trabajo.");
    return ["/calculos/liquidacion", {
      remuneracion_mensual: sueldoLiq, fecha_ingreso: $("ingresoLiq").value, fecha_salida: $("salidaLiq").value,
      motivo: $("motivoLiq").value, region: $("regionLiq").value, decimos_mensualizados: $("mensualLiq").checked,
    }];
  }
  if (tipo === "horas_extra") {
    const sueldoH = Number($("sueldoHoras").value);
    if (!(sueldoH > 0)) throw new Error("Ingrese un sueldo mensual mayor que 0.");
    const supl = Number($("horasSupl").value), extra = Number($("horasExtra").value);
    if (!(supl > 0 || extra > 0)) throw new Error("Ingrese al menos una hora suplementaria o extraordinaria.");
    return ["/calculos/horas-extra", { remuneracion_mensual: sueldoH, horas_suplementarias: supl, horas_extraordinarias: extra }];
  }
  const sueldo = Number($("sueldoVac").value);
  if (!(sueldo > 0)) throw new Error("Ingrese un sueldo mensual mayor que 0.");
  if (!$("ingreso").value) throw new Error("Ingrese la fecha de ingreso.");
  const cuerpo = { remuneracion_mensual: sueldo, fecha_ingreso: $("ingreso").value };
  if ($("corte").value) cuerpo.fecha_corte = $("corte").value;
  return ["/calculos/vacaciones", cuerpo];
}

// ---------------------------------------------------------------- 1) calcular (sin IA)
$("formulario").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  $("estadoVacio").hidden = false;
  ocultar($("errorCalculo"), $("resultado"), $("explicacion"), $("errorExplicar"));
  try {
    // Esta validación solo ayuda al usuario; la que cuenta es la del backend (Pydantic).
    const [ruta, cuerpo] = armarSolicitud();
    const r = await enviar(ruta, cuerpo, $("btnCalcular"), "Calculando…");
    ultimoResultado = r;
    $("total").textContent = usd(r.total);
    $("dias").hidden = r.dias === null || r.dias === undefined;
    $("dias").textContent = `Días de vacaciones: ${r.dias}`;
    llenarLista($("desglose"), r.desglose);
    $("fundamento").textContent = r.fundamento;
    $("resultado").hidden = false;
    $("estadoVacio").hidden = true;
  } catch (e) {
    mostrarError($("errorCalculo"), e.message);
  }
});

// ---------------------------------------------------------------- 2) explicar (con IA)
$("btnExplicar").addEventListener("click", async () => {
  if (!ultimoResultado) return;
  ocultar($("errorExplicar"), $("explicacion"));
  try {
    const r = await enviar("/explicar", ultimoResultado, $("btnExplicar"), "La IA está redactando…");
    if (r.explicacion && r.explicacion.estado === "ok") {
      $("textoExplicacion").textContent = r.explicacion.explicacion;
      llenarLista($("pasos"), r.explicacion.pasos);
      llenarLista($("advertencias"), r.explicacion.advertencias);
    } else {
      $("textoExplicacion").textContent = r.mensaje;
      llenarLista($("pasos"), []);
      llenarLista($("advertencias"), r.explicacion ? r.explicacion.faltantes.map((f) => `Falta: ${f}`) : []);
    }
    $("avisoIA").textContent = r.aviso;
    $("explicacion").hidden = false;
  } catch (e) {
    mostrarError($("errorExplicar"), e.message);
  }
});

// ---------------------------------------------------------------- 3) consulta libre (agente)
// El usuario escribe con sus palabras. El backend decide las herramientas; aquí solo se
// muestra lo que vuelve: texto del agente, cálculos del sistema y fuentes recuperadas.
let sesionPendiente = null;
let sesionResumen = null;
let sesionConversacion = null;   // id de la conversación: el historial vive en el servidor
let turnoAnterior = null;        // {pregunta, respuesta} que pasa al historial en el siguiente mensaje
const ESTADOS = {
  ok: "RESPUESTA",
  falta: "NECESITO UN DATO MÁS",
  abstencion: "SIN FUENTE SUFICIENTE",
  fuera_de_dominio: "FUERA DEL ALCANCE",
  resumen_listo: "RESUMEN LISTO",
  pendiente_confirmacion: "NECESITA SU CONFIRMACIÓN",
  derivado: "CASO DERIVADO",
  rechazado: "ACCIÓN CANCELADA",
  tope: "CONSULTA DEMASIADO LARGA",
};
const NOMBRES = {
  decimo_tercero: "Décimo tercero", decimo_cuarto: "Décimo cuarto", vacaciones: "Vacaciones",
  horas_extra: "Horas extra", liquidacion: "Liquidación estimada",
};

$("pregunta").addEventListener("input", () => { $("contador").textContent = $("pregunta").value.length; });

function mostrarCalculos(calculos) {
  $("calculosAgente").replaceChildren(...calculos.map((c) => {
    const caja = document.createElement("div");
    caja.className = "calculo-agente";
    const titulo = document.createElement("p");
    titulo.textContent = `${NOMBRES[c.tipo] || c.tipo}: `;
    const monto = document.createElement("strong");
    monto.textContent = usd(c.total);
    titulo.append(monto);
    const lista = document.createElement("ol");
    llenarLista(lista, c.desglose);
    const fund = document.createElement("p");
    fund.className = "fundamento";
    fund.textContent = `Fundamento: ${c.fundamento}`;
    caja.append(titulo, lista, fund);
    return caja;
  }));
  $("bloqueCalculos").hidden = calculos.length === 0;
}

function mostrarFuentes(fuentes) {
  $("fuentesAgente").replaceChildren(...fuentes.map((f) => {
    const d = document.createElement("details");
    d.className = "fuente";
    const s = document.createElement("summary");
    s.textContent = `Art. ${f.articulo}${f.capitulo ? " · " + f.capitulo : ""}`;
    const p = document.createElement("p");
    p.textContent = f.texto;
    d.append(s, p);
    return d;
  }));
  $("bloqueFuentes").hidden = fuentes.length === 0;
}

function agregarAlHistorial(turno) {
  const li = (quien, texto) => {
    const item = document.createElement("li");
    const q = document.createElement("span");
    q.className = "quien";
    q.textContent = quien;
    item.append(q, document.createTextNode(texto));
    return item;
  };
  $("historial").append(li("USTED", turno.pregunta), li("ASISTENTE", turno.respuesta));
  $("historial").hidden = false;
}

function nuevaConsulta() {
  sesionConversacion = sesionPendiente = sesionResumen = turnoAnterior = null;
  $("historial").replaceChildren();
  ocultar($("historial"), $("respuestaConsulta"), $("errorConsulta"), $("btnNueva"));
  $("pregunta").value = "";
  $("contador").textContent = "0";
  document.querySelector('label[for="pregunta"]').textContent = "Cuéntenos qué necesita saber, sin datos personales";
  $("pregunta").focus();
}
$("btnNueva").addEventListener("click", nuevaConsulta);

function mostrarRespuesta(r) {
  $("estadoAgente").textContent = ESTADOS[r.estado] || r.estado.toUpperCase();
  $("textoAgente").textContent = r.respuesta;
  sesionPendiente = r.estado === "pendiente_confirmacion" ? r.sesion : null;
  $("confirmacion").hidden = !sesionPendiente;
  // El texto de la confirmación (qué se hará y con qué datos) lo arma el servidor.
  if (sesionPendiente) {
    $("btnAprobar").textContent = r.pendiente && r.pendiente.herramienta === "generar_resumen"
      ? "Sí, generar el PDF" : "Sí, derivar mi caso";
  }
  sesionResumen = r.puede_descargar ? r.sesion : null;
  sesionConversacion = r.sesion || null;
  $("btnNueva").hidden = !sesionConversacion;
  if (sesionConversacion) {
    document.querySelector('label[for="pregunta"]').textContent =
      "Responda al asistente o siga preguntando (recuerda lo que ya dijo)";
  }
  $("btnPdf").hidden = !sesionResumen;
  mostrarCalculos(r.calculos || []);
  mostrarFuentes(r.fuentes || []);
  $("avisoAgente").textContent = r.aviso;
  $("respuestaConsulta").hidden = false;
}

$("formConsulta").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  ocultar($("errorConsulta"), $("respuestaConsulta"));
  const pregunta = $("pregunta").value.trim();
  if (pregunta.length < 3) return mostrarError($("errorConsulta"), "Escriba su pregunta (mínimo 3 caracteres).");
  const cuerpo = sesionConversacion ? { pregunta, sesion: sesionConversacion } : { pregunta };
  try {
    const r = await enviar("/consultar", cuerpo, $("btnConsultar"), "El asistente está usando sus herramientas…");
    if (turnoAnterior) agregarAlHistorial(turnoAnterior);
    turnoAnterior = { pregunta, respuesta: r.respuesta };
    $("preguntaActual").textContent = `Usted: ${pregunta}`;
    mostrarRespuesta(r);
    $("pregunta").value = "";
    $("contador").textContent = "0";
  } catch (e) {
    if (sesionConversacion && /expiró/.test(e.message)) nuevaConsulta();
    mostrarError($("errorConsulta"), e.message);
  }
});

async function decidir(aprobar, boton) {
  if (!sesionPendiente) return;
  ocultar($("errorConsulta"));
  try {
    const r = await enviar("/consultar/confirmar", { sesion: sesionPendiente, aprobar }, boton, "Procesando…");
    if (turnoAnterior) turnoAnterior.respuesta = r.respuesta;
    mostrarRespuesta(r);
    if (r.estado === "resumen_listo") await descargarPdf();
  } catch (e) {
    mostrarError($("errorConsulta"), e.message);
  }
}

// El PDF lo arma el servidor con sus propios datos; el navegador solo envía el id de la sesión.
async function descargarPdf() {
  if (!sesionResumen) return;
  const boton = $("btnPdf"), original = boton.textContent;
  boton.disabled = true;
  boton.textContent = "Generando PDF…";
  try {
    const r = await fetch("/consultar/resumen", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sesion: sesionResumen }),
    });
    if (!r.ok) throw new Error(await mensajeDeError(r));
    const url = URL.createObjectURL(await r.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = "resumen-calculadora-laboral.pdf";
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    mostrarError($("errorConsulta"), e instanceof TypeError ? "No se pudo conectar con el servidor." : e.message);
  } finally {
    boton.disabled = false;
    boton.textContent = original;
  }
}
$("btnPdf").addEventListener("click", descargarPdf);
$("btnAprobar").addEventListener("click", () => decidir(true, $("btnAprobar")));
$("btnRechazar").addEventListener("click", () => decidir(false, $("btnRechazar")));
