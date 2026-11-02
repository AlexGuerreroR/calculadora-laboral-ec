// Calculadora Laboral EC · frontend
// Reglas (guía semana 2 y clase del miércoles):
//  - El frontend habla SOLO con nuestro backend; nunca con el modelo ni con una clave.
//  - Deshabilita el botón mientras espera y muestra errores comprensibles.
//  - Todo texto se muestra con textContent (nunca innerHTML): la salida del modelo es texto, no HTML.

const $ = (id) => document.getElementById(id);
let ultimoResultado = null;
let solicitudAgentePendiente = null;
let consultandoAgente = false;
let vistaResumenActual = null;
let gestionandoResumen = false;

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

function limpiarConsultaAnterior() {
  solicitudAgentePendiente = null;
  ocultar($("respuestaAgente"), $("confirmacionAgente"), $("errorAgente"));
  ["mensajeRespuestaAgente", "faltantesAgente", "calculosAgente", "textosAgente",
    "listaFuentesAgente", "resumenConfirmacionAgente"].forEach((id) => $(id).replaceChildren());
  $("fuentesAgente").hidden = true;
  $("mensajeAgente").value = "";
}

function limpiarAlCambiarCalculo() {
  limpiarConsultaAnterior();
  vistaResumenActual = null;
  ocultar($("vistaResumenPDF"), $("estadoResumenPDF"), $("btnResumen"));
  actualizarBotonesResumen();
}

function llenarLista(lista, textos) {
  lista.replaceChildren(...textos.map((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    return li;
  }));
}

function mostrarFuentes(fuentes, listaId, contenedorId) {
  $(listaId).replaceChildren(...fuentes.map((f) => {
    const detalle = document.createElement("details");
    const titulo = document.createElement("summary");
    titulo.textContent = `${f.documento}, Art. ${f.articulo}`;
    const texto = document.createElement("p");
    texto.textContent = f.texto;
    const version = document.createElement("small");
    version.textContent = `Versión del documento: ${f.version}`;
    detalle.append(titulo, texto, version);
    try {
      const url = new URL(f.fuente);
      if (url.protocol === "https:") {
        const enlace = document.createElement("a");
        enlace.href = url.href;
        enlace.textContent = "Consultar documento fuente";
        enlace.target = "_blank";
        enlace.rel = "noopener noreferrer";
        detalle.append(document.createElement("br"), enlace);
      }
    } catch { /* Una fuente sin URL válida sigue mostrando su fragmento. */ }
    return detalle;
  }));
  $(contenedorId).hidden = fuentes.length === 0;
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
    ultimoResultado = null;
    limpiarAlCambiarCalculo();
    actualizarAdjuntoAgente();
    document.querySelectorAll("[data-para]").forEach((bloque) => {
      bloque.hidden = bloque.dataset.para !== tipoElegido();
    });
    ocultar($("resultado"), $("errorCalculo"), $("estadoResumenPDF"));
    $("estadoVacio").hidden = false;
  });
});

function numeroObligatorio(id, nombre, positivo = false) {
  const valor = $(id).value.trim();
  const numero = Number(valor);
  if (valor === "" || !Number.isFinite(numero) || numero < 0 || (positivo && numero === 0)) {
    throw new Error(`Complete ${nombre} con un valor ${positivo ? "mayor que cero" : "igual o mayor que cero"}.`);
  }
  return valor; // El backend recibe decimales escritos, sin cálculos monetarios en JS.
}

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
  if (tipo === "horas_extra") {
    return ["/calculos/horas", {
      remuneracion_mensual: numeroObligatorio("sueldoHoras", "la remuneración", true),
      horas_suplementarias: numeroObligatorio("horasSuplementarias", "las horas suplementarias"),
      horas_extraordinarias: numeroObligatorio("horasExtraordinarias", "las horas extraordinarias"),
    }];
  }
  if (tipo === "liquidacion") {
    if (!$("ingresoLiq").value || !$("salidaLiq").value) throw new Error("Complete las fechas de ingreso y salida.");
    if (!$("motivoLiq").value || !$("regionLiq").value) throw new Error("Seleccione el motivo de salida y la región.");
    if (!$("confirmarLiq").checked) throw new Error("Revise y confirme el motivo de salida y los saldos pendientes.");
    return ["/calculos/liquidacion", {
      remuneracion_mensual: numeroObligatorio("sueldoLiq", "la remuneración", true),
      fecha_ingreso: $("ingresoLiq").value, fecha_salida: $("salidaLiq").value,
      motivo_salida: $("motivoLiq").value, region: $("regionLiq").value,
      salario_pendiente: numeroObligatorio("salarioPendiente", "el salario pendiente"),
      base_acumulada_decimo_tercero: numeroObligatorio("baseDecimoLiq", "la base pendiente del décimo tercero"),
      dias_decimo_cuarto_pendientes: numeroObligatorio("diasDecimoLiq", "los días pendientes del décimo cuarto"),
      dias_vacaciones_base_pendientes: numeroObligatorio("vacacionesBaseLiq", "los días base pendientes de vacaciones"),
      dias_vacaciones_adicionales_pendientes: numeroObligatorio("vacacionesExtraLiq", "los días adicionales pendientes de vacaciones"),
      horas_suplementarias_pendientes: numeroObligatorio("suplementariasLiq", "las horas suplementarias pendientes"),
      horas_extraordinarias_pendientes: numeroObligatorio("extraordinariasLiq", "las horas extraordinarias pendientes"),
      descuentos_confirmados: numeroObligatorio("descuentosLiq", "los descuentos verificados"),
      criterios_confirmados: true,
    }];
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
  ultimoResultado = null;
  limpiarAlCambiarCalculo();
  actualizarAdjuntoAgente();
  $("estadoVacio").hidden = false;
  ocultar($("errorCalculo"), $("resultado"), $("estadoResumenPDF"));
  try {
    // Esta validación solo ayuda al usuario; la que cuenta es la del backend (Pydantic).
    const [ruta, cuerpo] = armarSolicitud();
    const r = await enviar(ruta, cuerpo, $("btnCalcular"), "Calculando…");
    ultimoResultado = r;
    actualizarAdjuntoAgente();
    $("total").textContent = usd(r.total);
    $("btnResumen").hidden = false;
    $("resultado").hidden = false;
    $("estadoVacio").hidden = true;
  } catch (e) {
    mostrarError($("errorCalculo"), e.message);
  }
});

// Consulta independiente al agente; no se envía un historial editable por el cliente.
const nombresCalculo = {decimo_tercero: "Décimo tercero", decimo_cuarto: "Décimo cuarto",
  vacaciones: "Vacaciones", horas_extra: "Horas adicionales", liquidacion: "Liquidación estimada"};

function actualizarAdjuntoAgente() {
  $("usarCalculoAgente").disabled = !ultimoResultado;
  if (!ultimoResultado) $("usarCalculoAgente").checked = false;
  $("adjuntoAgente").textContent = ultimoResultado
    ? `${nombresCalculo[ultimoResultado.tipo]}: ${usd(ultimoResultado.total)}. Marque la casilla si desea usar sus datos.`
    : "Calcule un beneficio para poder adjuntarlo a la consulta.";
  solicitudAgentePendiente = null;
  $("confirmacionAgente").hidden = true;
}

function datoPendienteLegible(texto) {
  if (/^(?:calcular_|estimar_|explicar_|consultar_|solicitar_|generar_)|argumentos|calculo_id/i.test(texto)) {
    return "Revise los datos del cálculo y vuelva a intentarlo.";
  }
  return texto.replaceAll("remuneracion mensual", "sueldo mensual")
    .replaceAll("fecha ingreso", "fecha de ingreso")
    .replaceAll("fecha salida", "fecha de salida")
    .replaceAll("motivo salida", "motivo de salida")
    .replaceAll("criterios confirmados", "confirmación del motivo y los saldos");
}

function mostrarRespuestaAgente(r) {
  const mensajes = {
    pedir_datos: "Para continuar, complete o revise los datos que se indican a continuación.",
    limite: "No se pudo completar la consulta. Intente con una pregunta más concreta.",
    rechazado: "Puedo ayudarle con consultas sobre beneficios laborales de Ecuador. Reformule su pregunta dentro de ese tema.",
  };
  $("mensajeRespuestaAgente").textContent = mensajes[r.estado] || r.mensaje;
  llenarLista($("faltantesAgente"), [...new Set((r.faltantes || []).map(datoPendienteLegible))]);
  $("calculosAgente").replaceChildren(...(r.calculos || []).map((c) => {
    const bloque = document.createElement("section");
    const titulo = document.createElement("h3");
    titulo.textContent = `${nombresCalculo[c.resultado.tipo]}: ${usd(c.resultado.total)}`;
    const detalle = document.createElement("ol");
    llenarLista(detalle, c.resultado.desglose);
    bloque.append(titulo, detalle);
    return bloque;
  }));
  const textos = [...(r.normativa || []).map(n => n.respuesta),
    ...(r.explicaciones || []).map(e => e.explicacion.explicacion)];
  $("textosAgente").replaceChildren(...textos.map(t => {
    const p = document.createElement("p"); p.textContent = t; return p;
  }));
  const fuentes = new Map();
  [...(r.normativa || []), ...(r.explicaciones || [])].forEach(x => {
    x.fuentes.forEach(f => fuentes.set(f.id, f));
  });
  mostrarFuentes([...fuentes.values()], "listaFuentesAgente", "fuentesAgente");
  $("respuestaAgente").hidden = false;
  llenarLista($("resumenConfirmacionAgente"), r.resumen_confirmacion || []);
  $("confirmacionAgente").hidden = r.estado !== "requiere_confirmacion" || Boolean(r.resumen_pdf);
  if (r.resumen_pdf) mostrarVistaResumen(r.resumen_pdf);
}

async function consultarAgente(cuerpo, boton) {
  if (consultandoAgente) return;
  consultandoAgente = true;
  $("btnAgente").disabled = true;
  $("btnConfirmarAgente").disabled = true;
  ocultar($("errorAgente"), $("confirmacionAgente"), $("respuestaAgente"));
  $("estadoAgente").textContent = "Consultando su pregunta…";
  $("estadoAgente").hidden = false;
  try {
    const r = await enviar("/agente", cuerpo, boton, "Consultando…");
    mostrarRespuestaAgente(r);
    solicitudAgentePendiente = r.estado === "requiere_confirmacion" && !r.resumen_pdf ? cuerpo : null;
  } catch (e) {
    mostrarError($("errorAgente"), e.message);
    if (solicitudAgentePendiente) $("confirmacionAgente").hidden = false;
  } finally {
    consultandoAgente = false;
    $("estadoAgente").hidden = true;
    $("btnAgente").disabled = false;
    $("btnConfirmarAgente").disabled = false;
  }
}

$("formAgente").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const mensaje = $("mensajeAgente").value.trim();
  if (!mensaje) { mostrarError($("errorAgente"), "Escriba su consulta."); return; }
  await consultarAgente({mensaje, calculo: $("usarCalculoAgente").checked ? ultimoResultado : null,
    confirmar_liquidacion: false}, $("btnAgente"));
});

$("btnConfirmarAgente").addEventListener("click", async () => {
  if (!solicitudAgentePendiente) return;
  await consultarAgente({...solicitudAgentePendiente, confirmar_liquidacion: true}, $("btnConfirmarAgente"));
});

$("btnCancelarAgente").addEventListener("click", () => {
  solicitudAgentePendiente = null;
  $("confirmacionAgente").hidden = true;
  $("mensajeRespuestaAgente").textContent = "Se canceló el uso de los saldos. Puede realizar otra consulta.";
});

function actualizarBotonesResumen() {
  $("btnResumen").disabled = gestionandoResumen || Boolean(vistaResumenActual);
  $("btnConfirmarResumenPDF").disabled = gestionandoResumen || !vistaResumenActual;
  $("btnCancelarResumenPDF").disabled = gestionandoResumen || !vistaResumenActual;
}

function mostrarVistaResumen(vista) {
  ocultar($("estadoResumenPDF"));
  vistaResumenActual = vista;
  $("tituloResumenPDF").textContent = `${nombresCalculo[vista.calculo.tipo]}: ${usd(vista.calculo.total)}`;
  $("mensajeResumenPDF").textContent = vista.mensaje;
  $("vigenciaResumenPDF").textContent = `Esta solicitud vence en ${Math.ceil(vista.vence_en_segundos / 60)} minutos y solo puede usarse una vez.`;
  $("avisoFuentesResumenPDF").textContent = vista.advertencia_fuentes || "Revise la versión y fecha de corte de las fuentes citadas. La aplicación orienta y no certifica reformas posteriores a ese corte.";
  llenarLista($("datosResumenPDF"), vista.datos);
  llenarLista($("detalleResumenPDF"), vista.calculo.desglose);
  mostrarFuentes(vista.fuentes, "listaFuentesResumenPDF", "fuentesResumenPDF");
  $("vistaResumenPDF").hidden = false;
  $("errorResumenPDF").hidden = true;
  actualizarBotonesResumen();
  $("vistaResumenPDF").scrollIntoView({behavior: "smooth", block: "start"});
}

function finalizarVistaResumen(vista, mensaje) {
  if (vistaResumenActual?.token !== vista.token) return;
  vistaResumenActual = null;
  ocultar($("vistaResumenPDF"), $("errorResumenPDF"));
  $("datosResumenPDF").replaceChildren();
  $("detalleResumenPDF").replaceChildren();
  $("listaFuentesResumenPDF").replaceChildren();
  $("vistaResumenPDF").querySelectorAll("details").forEach((detalle) => { detalle.open = false; });
  $("estadoResumenPDF").textContent = mensaje;
  $("estadoResumenPDF").hidden = false;
}

$("btnResumen").addEventListener("click", async () => {
  if (!ultimoResultado || gestionandoResumen) return;
  gestionandoResumen = true;
  ocultar($("estadoResumenPDF"), $("vistaResumenPDF"));
  actualizarBotonesResumen();
  try {
    const vista = await enviar("/resumen/preparar", {calculo: ultimoResultado}, $("btnResumen"), "Generando PDF…");
    vistaResumenActual = vista;
    gestionandoResumen = false;
    await descargarResumenPDF();
  } catch (e) {
    vistaResumenActual = null;
    mostrarError($("estadoResumenPDF"), e.message);
  } finally {
    gestionandoResumen = false;
    actualizarBotonesResumen();
  }
});

async function descargarResumenPDF() {
  if (!vistaResumenActual || gestionandoResumen) return;
  const vista = vistaResumenActual;
  gestionandoResumen = true;
  actualizarBotonesResumen();
  ocultar($("errorResumenPDF"));
  try {
    const r = await fetch("/resumen/confirmar", {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({token: vista.token, confirmar: true})});
    if (!r.ok) throw new Error(await mensajeDeError(r));
    if (!(r.headers.get("Content-Type") || "").startsWith("application/pdf")) throw new Error("El servidor no devolvió un PDF válido.");
    const archivo = await r.blob();
    const url = URL.createObjectURL(archivo);
    const enlace = document.createElement("a");
    enlace.href = url; enlace.download = vista.nombre_archivo;
    document.body.append(enlace); enlace.click(); enlace.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    limpiarConsultaAnterior();
    finalizarVistaResumen(vista, "PDF generado. Revise la descarga del navegador. Puede continuar con su cálculo o preparar otro resumen.");
  } catch (e) {
    if (vistaResumenActual?.token === vista.token) vistaResumenActual = null;
    ocultar($("vistaResumenPDF"));
    mostrarError($("estadoResumenPDF"), `${e.message} Pulse «Descargar PDF» para intentarlo otra vez.`);
  } finally {
    gestionandoResumen = false;
    actualizarBotonesResumen();
  }
}

$("btnConfirmarResumenPDF").addEventListener("click", descargarResumenPDF);

$("btnCancelarResumenPDF").addEventListener("click", async () => {
  if (!vistaResumenActual || gestionandoResumen) return;
  const vista = vistaResumenActual;
  gestionandoResumen = true;
  actualizarBotonesResumen();
  try {
    const r = await fetch("/resumen/cancelar", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({token: vista.token})});
    if (!r.ok && r.status !== 404) throw new Error(await mensajeDeError(r));
    finalizarVistaResumen(vista, "Resumen cancelado. No se generó un PDF. Puede preparar otro resumen cuando lo necesite.");
  } catch (e) {
    mostrarError($("errorResumenPDF"), e.message);
  } finally {
    gestionandoResumen = false;
    actualizarBotonesResumen();
  }
});
