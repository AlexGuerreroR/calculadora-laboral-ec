// Calculadora Laboral EC · frontend
// Reglas (guía semana 2 y clase del miércoles):
//  - El frontend habla SOLO con nuestro backend; nunca con el modelo ni con una clave.
//  - Deshabilita el botón mientras espera y muestra errores comprensibles.
//  - Todo texto se muestra con textContent (nunca innerHTML): la salida del modelo es texto, no HTML.

const $ = (id) => document.getElementById(id);
let ultimoResultado = null;
let versionFormulario = 0;

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

function limpiarAlCambiarCalculo() {
  $("supuestosLiqBasica").open = false;
  $("btnExplicarCalculo").setAttribute("aria-expanded", "false");
  $("textoBotonExplicar").textContent = "Explicar cálculo";
  $("tituloFuentesSupuestos").textContent = "Ver supuestos del cálculo";
  $("listaSupuestosLiqBasica").replaceChildren();
  ocultar($("panelDetalle"), $("referenciasExplicacion"), $("avisoExplicacionCalculo"),
    $("explicacionCalculo"), $("esperaExplicacionCalculo"), $("errorExplicacionCalculo"),
    $("estadoResumenPDF"), $("btnResumen"));
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
  const etiqueta = boton.querySelector("span") || boton;
  const original = etiqueta.textContent;
  boton.disabled = true;
  etiqueta.textContent = textoEspera;
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
    etiqueta.textContent = original;
  }
}

// ---------------------------------------------------------------- formulario según el tipo
function reiniciarResultado() {
  versionFormulario += 1;
  ultimoResultado = null;
  limpiarAlCambiarCalculo();
  document.querySelectorAll("[data-para]").forEach((bloque) => {
    bloque.hidden = bloque.dataset.para !== tipoElegido();
  });
  ocultar($("resultado"), $("errorCalculo"), $("estadoResumenPDF"));
  $("estadoVacio").hidden = false;
}

document.querySelectorAll('input[name="tipo"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    reiniciarResultado();
  });
});

$("modoLiq").addEventListener("change", () => {
  const basico = $("modoLiq").value === "basico";
  $("liquidacionBasica").hidden = !basico;
  $("liquidacionAvanzada").hidden = basico;
  reiniciarResultado();
});

let solicitudVacaciones = 0;
let vacacionesAutocompletadas = false;
$("vacacionesLiqBasico").addEventListener("input", () => {
  vacacionesAutocompletadas = false;
});

async function actualizarSugerenciaVacaciones() {
  const solicitud = ++solicitudVacaciones;
  const ingreso = $("ingresoLiqBasico").value;
  const salida = $("salidaLiqBasico").value;
  const campo = $("vacacionesLiqBasico");
  if (vacacionesAutocompletadas) {
    campo.value = "";
    vacacionesAutocompletadas = false;
  }
  if (!ingreso || !salida || ingreso > salida) return;
  const parametros = new URLSearchParams({fecha_ingreso: ingreso, fecha_salida: salida});
  try {
    const respuesta = await fetch(`/calculos/liquidacion/basica/vacaciones?${parametros}`);
    if (!respuesta.ok) return;
    const {dias} = await respuesta.json();
    if (solicitud === solicitudVacaciones && campo.value === "" && !campo.validity.badInput) {
      campo.value = String(dias);
      vacacionesAutocompletadas = true;
    }
  } catch {
    // El cálculo final vuelve a estimar los días si el campo queda vacío.
  }
}

["ingresoLiqBasico", "salidaLiqBasico"].forEach((id) => {
  $(id).addEventListener("change", actualizarSugerenciaVacaciones);
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
    if ($("modoLiq").value === "basico") {
      const fecha_ingreso = $("ingresoLiqBasico").value;
      const fecha_salida = $("salidaLiqBasico").value;
      const motivo_salida = $("motivoLiqBasico").value;
      const region = $("regionLiqBasico").value;
      if (!fecha_ingreso || !fecha_salida) throw new Error("Complete las fechas de ingreso y salida.");
      if (!motivo_salida || !region) throw new Error("Seleccione el motivo de salida y la región.");
      return ["/calculos/liquidacion/basica", {
        remuneracion_mensual: numeroObligatorio("sueldoLiqBasico", "la remuneración", true),
        fecha_ingreso, fecha_salida, motivo_salida, region,
        mensualiza_decimo_tercero: $("mensualiza13Liq").checked,
        mensualiza_decimo_cuarto: $("mensualiza14Liq").checked,
        dias_vacaciones_pendientes: vacacionesAutocompletadas || $("vacacionesLiqBasico").value === "" ? null
          : numeroObligatorio("vacacionesLiqBasico", "los días de vacaciones"),
      }];
    }
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
  const version = ++versionFormulario;
  ultimoResultado = null;
  limpiarAlCambiarCalculo();
  $("estadoVacio").hidden = false;
  ocultar($("errorCalculo"), $("resultado"), $("estadoResumenPDF"));
  try {
    // Esta validación solo ayuda al usuario; la que cuenta es la del backend (Pydantic).
    const [ruta, cuerpo] = armarSolicitud();
    const r = await enviar(ruta, cuerpo, $("btnCalcular"), "Calculando…");
    if (version !== versionFormulario) return;
    ultimoResultado = r;
    $("total").textContent = usd(r.total);
    $("etiquetaTotal").textContent = r.tipo === "liquidacion" ? "TOTAL REFERENCIAL" : "BENEFICIO CALCULADO";
    const basico = r.tipo === "liquidacion" && r.entradas.modo === "basico";
    $("resultadoLiqBasica").hidden = !basico;
    if (basico) {
      const inicioSupuestos = r.desglose.findIndex(texto => texto.startsWith("Supuestos:"));
      const corte = inicioSupuestos === -1 ? r.desglose.length : inicioSupuestos;
      $("desgloseLiqBasica").replaceChildren(...r.desglose.slice(0, corte).map(texto => {
        const fila = document.createElement("li");
        const rubro = texto.match(/^(.+): USD (\d+(?:\.\d+)?)$/);
        if (!rubro) { fila.textContent = texto; return fila; }
        const nombre = document.createElement("span");
        const importe = document.createElement("strong");
        nombre.textContent = rubro[1].replace(/ estimad[oa]s?/, "").replace(/ \([^)]*\)$/, "");
        importe.textContent = usd(Number(rubro[2]));
        fila.append(nombre, importe);
        return fila;
      }));
      llenarLista($("listaSupuestosLiqBasica"), r.desglose.slice(corte));
      $("supuestosLiqBasica").hidden = corte === r.desglose.length;
      $("panelDetalle").hidden = $("supuestosLiqBasica").hidden;
    }
    $("btnResumen").hidden = false;
    $("resultado").hidden = false;
    $("estadoVacio").hidden = true;
  } catch (e) {
    if (version === versionFormulario) mostrarError($("errorCalculo"), e.message);
  }
});

// Consulta independiente al agente; no se envía un historial editable por el cliente.
const nombresCalculo = {decimo_tercero: "Décimo tercero", decimo_cuarto: "Décimo cuarto",
  vacaciones: "Vacaciones", horas_extra: "Horas adicionales", liquidacion: "Liquidación estimada"};

function mostrarBloquesExplicacion(calculo, explicacion, fuentes) {
  const grupos = calculo.tipo === "liquidacion" ? [
    {titulo: "Décimos", icono: "regalo", patron: /\bd[eé]cim|\bdecim[oa]/i, articulos: ["111", "113"]},
    {titulo: "Vacaciones", icono: "vacaciones", patron: /\bvacacion/i, articulos: ["69", "71"]},
    {titulo: "Terminación laboral", icono: "trabajo", patron: /\b(despido|desahucio|indemnizaci)/i, articulos: ["184", "185", "188"]},
  ] : [];
  const contenedor = $("bloquesExplicacion");
  contenedor.replaceChildren();
  const pasosUnicos = [...new Set(explicacion.pasos.map(paso => paso.trim()).filter(Boolean))];
  const pendientes = new Set(pasosUnicos);
  for (const grupo of grupos) {
    const pasos = [...pendientes].filter(paso => grupo.patron.test(paso.split(":")[0]));
    if (!pasos.length) continue;
    const bloque = document.createElement("section");
    const titulo = document.createElement("h3");
    const icono = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    const uso = document.createElementNS("http://www.w3.org/2000/svg", "use");
    icono.setAttribute("class", "icono");
    icono.setAttribute("aria-hidden", "true");
    uso.setAttribute("href", `#icono-${grupo.icono}`);
    icono.append(uso);
    titulo.append(icono, grupo.titulo);
    bloque.append(titulo);
    for (const paso of pasos) {
      pendientes.delete(paso);
      const parrafo = document.createElement("p");
      parrafo.textContent = paso;
      bloque.append(parrafo);
    }
    for (const articulo of grupo.articulos) {
      if (!fuentes.some(fuente => fuente.articulo === articulo)) continue;
      const cita = document.createElement("span");
      cita.className = "articulo-explicacion";
      cita.textContent = `Art. ${articulo}`;
      bloque.append(cita);
    }
    contenedor.append(bloque);
  }
  if (!contenedor.childElementCount) {
    const resumen = document.createElement("p");
    resumen.className = "resumen-explicacion";
    resumen.textContent = explicacion.explicacion;
    contenedor.append(resumen);
  }
  const adicionales = [...pendientes].filter(paso =>
    paso !== explicacion.explicacion.trim() &&
    !(calculo.entradas?.modo === "basico" && /^(supuestos?|exclusiones)\b/i.test(paso)));
  llenarLista($("pasosAdicionalesExplicacion"), adicionales);
  $("pasosAdicionalesExplicacion").hidden = !adicionales.length;
}

$("btnExplicarCalculo").addEventListener("click", async () => {
  const calculo = ultimoResultado;
  const boton = $("btnExplicarCalculo");
  if (!calculo || boton.disabled) return;
  if (!$("explicacionCalculo").hidden) {
    ocultar($("explicacionCalculo"), $("referenciasExplicacion"), $("avisoExplicacionCalculo"));
    $("supuestosLiqBasica").open = false;
    $("supuestosLiqBasica").hidden = !$("listaSupuestosLiqBasica").childElementCount;
    $("panelDetalle").hidden = $("supuestosLiqBasica").hidden;
    $("tituloFuentesSupuestos").textContent = "Ver supuestos del cálculo";
    $("textoBotonExplicar").textContent = "Explicar cálculo";
    boton.setAttribute("aria-expanded", "false");
    return;
  }
  if ($("bloquesExplicacion").dataset.cargado === String(versionFormulario)) {
    abrirExplicacion();
    return;
  }
  ocultar($("errorExplicacionCalculo"));
  const espera = $("esperaExplicacionCalculo");
  espera.hidden = false;
  boton.setAttribute("aria-busy", "true");
  try {
    const r = await enviar("/explicar", calculo, boton, "Preparando explicación…");
    if (calculo !== ultimoResultado) return;
    if (r.explicacion?.estado !== "ok") {
      mostrarError($("errorExplicacionCalculo"), r.mensaje || "No pudimos preparar la explicación. Intente nuevamente.");
      return;
    }
    llenarLista($("advertenciasExplicacionCalculo"), r.explicacion.advertencias);
    $("advertenciasExplicacionCalculo").hidden = !r.explicacion.advertencias.length;
    mostrarFuentes(r.fuentes, "listaFuentesExplicacionCalculo", "fuentesExplicacionCalculo");
    $("avisoExplicacionCalculo").textContent = r.aviso;
    mostrarBloquesExplicacion(calculo, r.explicacion, r.fuentes);
    $("bloquesExplicacion").dataset.cargado = String(versionFormulario);
    abrirExplicacion();
  } catch (e) {
    if (calculo === ultimoResultado) mostrarError($("errorExplicacionCalculo"), e.message);
  } finally {
    espera.hidden = true;
    boton.removeAttribute("aria-busy");
  }
});

function abrirExplicacion() {
  $("panelDetalle").hidden = false;
  $("explicacionCalculo").hidden = false;
  const tieneFuentes = !$("fuentesExplicacionCalculo").hidden;
  $("referenciasExplicacion").hidden = !tieneFuentes;
  const tieneSupuestos = Boolean($("listaSupuestosLiqBasica").childElementCount);
  $("supuestosLiqBasica").hidden = !tieneFuentes && !tieneSupuestos;
  $("avisoExplicacionCalculo").hidden = false;
  $("tituloFuentesSupuestos").textContent = tieneFuentes
    ? (tieneSupuestos ? "Ver fuentes y supuestos" : "Ver fuentes")
    : "Ver supuestos del cálculo";
  $("textoBotonExplicar").textContent = "Ocultar explicación";
  $("btnExplicarCalculo").setAttribute("aria-expanded", "true");
  $("panelDetalle").scrollIntoView({block: "nearest"});
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
    requiere_confirmacion: "Para revisar una estimación o descargar su resumen, use la tarjeta del resultado.",
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
  $("esperaRespuestaAgente").hidden = true;
  $("fuentesAgente").open = false;
}

$("formAgente").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const boton = $("btnAgente");
  if (boton.disabled) return;
  const mensaje = $("mensajeAgente").value.trim();
  if (!mensaje) { mostrarError($("errorAgente"), "Escriba su consulta."); return; }
  ocultar($("errorAgente"), $("respuestaAgente"));
  $("esperaRespuestaAgente").hidden = false;
  $("estadoAgente").hidden = false;
  boton.setAttribute("aria-busy", "true");
  try {
    const r = await enviar("/agente", {mensaje}, boton, "Preparando respuesta…");
    mostrarRespuestaAgente(r);
  } catch (e) {
    mostrarError($("errorAgente"), e.message);
  } finally {
    $("estadoAgente").hidden = true;
    boton.removeAttribute("aria-busy");
  }
});

$("btnResumen").addEventListener("click", async () => {
  const calculo = ultimoResultado;
  const boton = $("btnResumen");
  if (!calculo || boton.disabled) return;
  boton.disabled = true;
  $("textoBotonResumen").textContent = "Generando PDF…";
  ocultar($("estadoResumenPDF"));
  try {
    const preparada = await fetch("/resumen/preparar", {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({calculo}),
    });
    if (!preparada.ok) throw new Error(await mensajeDeError(preparada));
    const vista = await preparada.json();
    if (calculo !== ultimoResultado) return;
    const respuesta = await fetch("/resumen/confirmar", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({token: vista.token, confirmar: true}),
    });
    if (!respuesta.ok) throw new Error(await mensajeDeError(respuesta));
    if (!(respuesta.headers.get("Content-Type") || "").startsWith("application/pdf")) {
      throw new Error("El servidor no devolvió un PDF válido.");
    }
    const archivo = await respuesta.blob();
    if (calculo !== ultimoResultado) return;
    const url = URL.createObjectURL(archivo);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = vista.nombre_archivo;
    document.body.append(enlace);
    enlace.click();
    enlace.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $("estadoResumenPDF").textContent = "PDF generado. Revise la descarga del navegador.";
    $("estadoResumenPDF").hidden = false;
  } catch (e) {
    if (calculo === ultimoResultado) mostrarError($("estadoResumenPDF"), e.message);
  } finally {
    boton.disabled = false;
    $("textoBotonResumen").textContent = "Descargar PDF";
  }
});

