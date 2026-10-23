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
