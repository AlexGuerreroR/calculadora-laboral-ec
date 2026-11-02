"""Agente acotado: herramientas específicas, datos confirmados y resultados verificables.

El texto final libre del modelo no se publica. La respuesta se arma con los
resultados reales de herramientas y explicaciones que pasaron los controles RAG.
No hay herramientas de escritura, envío, comandos ni generación de archivos.
"""
import json
import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal

from pydantic import ValidationError

from app.schemas import (CalculoAgente, ConsultaAgente, EntradaConsultaNormativa,
                         EntradaDecimoCuarto, EntradaDecimoTercero, EntradaExplicarAgente,
                         EntradaHoras, EntradaLiquidacion, EntradaVacaciones,
                         EntradaSolicitarDatos, EntradaDiasVacaciones, EntradaJornada,
                         ExplicacionAgente, FuenteRAG, NormativaAgente, PasoAgente,
                         RespuestaAgente, SolicitudDecimos, TextoNormativo)
from app.services import rag, retriever
from app.services.llm import SalidaInvalida, cargar_prompt
from app.tools.decimos import calcular_decimo_cuarto, calcular_decimo_tercero
from app.tools.horas import calcular_horas
from app.tools.jornada import analizar_jornada
from app.tools.liquidacion import estimar_liquidacion
from app.tools.parametros import cargar_parametros
from app.tools.vacaciones import calcular_vacaciones, calcular_dias_vacaciones


def _calcular_decimos(datos):
    if datos.tipo == "decimo_tercero":
        return calcular_decimo_tercero(EntradaDecimoTercero(remuneraciones=datos.remuneraciones))
    return calcular_decimo_cuarto(EntradaDecimoCuarto(meses_trabajados=datos.meses_trabajados, region=datos.region))


@dataclass(frozen=True)
class Herramienta:
    esquema: type
    descripcion: str
    calcular: object = None
    tipos: tuple = ()


# Permisos definidos en código: nunca eval(), exec(), SQL, comandos o nombres
# resueltos dinámicamente a partir de lo que escriba el modelo.
PERMITIDAS = {
    "consultar_normativa": Herramienta(EntradaConsultaNormativa, "Consulta fuentes laborales y responde con citas verificadas; sin cálculos."),
    "calcular_decimos": Herramienta(SolicitudDecimos, "Calcula un décimo con exactamente los datos confirmados del formulario.", _calcular_decimos, ("decimo_tercero", "decimo_cuarto")),
    "calcular_vacaciones": Herramienta(EntradaVacaciones, "Calcula vacaciones con los datos confirmados del formulario.", calcular_vacaciones, ("vacaciones",)),
    "calcular_horas": Herramienta(EntradaHoras, "Calcula horas adicionales con los datos confirmados del formulario.", calcular_horas, ("horas_extra",)),
    "estimar_liquidacion": Herramienta(EntradaLiquidacion, "Estima la liquidación con los saldos confirmados; requiere confirmación explícita del usuario.", estimar_liquidacion, ("liquidacion",)),
    "explicar_resultado": Herramienta(EntradaExplicarAgente, "Explica un cálculo existente por su ID, recuperando sus artículos; no acepta cálculos inventados."),
    "solicitar_datos": Herramienta(EntradaSolicitarDatos, "Pide completar el formulario de un cálculo cuando faltan datos confirmados; no supone valores."),
    "generar_resumen": Herramienta(EntradaExplicarAgente, "Solicita un PDF de un cálculo existente por su ID. Solo prepara una vista previa; requiere clic de confirmación humana para generarlo."),
}


def esquemas_herramientas():
    return [{"type": "function", "function": {"name": nombre, "description": h.descripcion,
             "parameters": h.esquema.model_json_schema()}} for nombre, h in PERMITIDAS.items()]


def _normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def consulta_sin_ordenes_citadas(mensaje):
    """Aparta órdenes hostiles dentro de citas; la pregunta exterior sigue validándose."""
    patrones = cargar_parametros()["agente"]["patrones_inyeccion"]
    def apartar(coincidencia):
        contenido = coincidencia.group(0)
        if any(re.search(p, _normalizar(contenido)) for p in patrones):
            return "[orden citada omitida]"
        return contenido
    return re.sub(r'«[^»]*»|“[^”]*”|"[^"\r\n]*"', apartar, mensaje)


def _cantidades_normativas(texto):
    """Compara cantidades literales con su unidad; no hace operaciones jurídicas.

    Convierte solo números escritos en palabras para reconocer «quince días»
    como la misma cantidad que «15 días». Un 17 que no aparece en la fuente
    no puede publicarse como si lo hubiera calculado una herramienta.
    """
    texto = _normalizar(texto).replace("por ciento", "%")
    palabras = ("cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince "
                "dieciseis diecisiete dieciocho diecinueve veinte veintiuno veintidos veintitres veinticuatro "
                "veinticinco veintiseis veintisiete veintiocho veintinueve treinta").split()
    numeros = {palabra: str(i) for i, palabra in enumerate(palabras)}
    numeros.update({"un": "1", "una": "1", "cuarenta": "40", "cincuenta": "50", "cien": "100", "ciento": "100"})
    for palabra, numero in numeros.items():
        texto = re.sub(r"\b" + palabra + r"\b", numero, texto)
    texto = texto.replace("(", " ").replace(")", " ")
    cantidades = re.findall(r"([+-]?\d+(?:[.,]\d+)?)\s*(dias?|horas?|meses?|anos?|remuneraciones?|%)(?!\w)", texto)
    unidades = {"dias": "dia", "horas": "hora", "meses": "mes", "anos": "ano", "remuneraciones": "remuneracion"}
    return {(Decimal(n.replace(",", ".")), unidades.get(unidad, unidad)) for n, unidad in cantidades}


def controlar_alcance(mensaje, con_calculo=False):
    config = cargar_parametros()["agente"]
    texto = _normalizar(consulta_sin_ordenes_citadas(mensaje))
    if any(re.search(p, texto) for p in config["patrones_inyeccion"]):
        return "rechazado", "No puedo cambiar mis instrucciones, revelar claves ni ejecutar órdenes. Puedo orientarle sobre beneficios laborales de Ecuador."
    if any(re.search(p, texto) for p in config["patrones_disputa"]):
        return "abstencion", "No puedo determinar quién tiene razón ni dictaminar un conflicto laboral. Acuda a la Inspectoría del Ministerio del Trabajo."
    if any(re.search(p, texto) for p in config.get("fuentes_no_cargadas", [])):
        return "abstencion", "No dispongo del documento necesario en las fuentes cargadas. Necesito el reglamento o contrato de su empresa, o la normativa específica de aportes al IESS, según su consulta. Puede consultar al Ministerio del Trabajo o al IESS."
    referencia = con_calculo and (("calculo" in texto and any(v in texto for v in ("explic", "revis", "calcul")))
                                 or "pdf" in texto or "resumen" in texto)
    if not referencia and not any(t in texto for t in config["terminos_dominio"]):
        return "rechazado", "Esta consulta está fuera del alcance laboral. Puedo ayudarle con décimos, vacaciones, horas adicionales y estimaciones de liquidación de Ecuador."
    return None


class LimiteAgente(Exception):
    pass


class ClienteAcotado:
    """Cuenta solicitudes lógicas, incluidas generación normativa y explicaciones.

    Cada una conserva los reintentos y respaldo acotados de ClienteLLM.
    """
    def __init__(self, cliente, maximo):
        self.cliente, self.maximo, self.usadas = cliente, maximo, 0

    def _consumir(self):
        if self.usadas >= self.maximo:
            raise LimiteAgente()
        self.usadas += 1

    def generar_herramientas(self, mensajes, herramientas, requerir_herramienta=False):
        self._consumir()
        return self.cliente.generar_herramientas(mensajes, herramientas,
                                               requerir_herramienta=requerir_herramienta)

    def generar_json(self, *args):
        self._consumir()
        return self.cliente.generar_json(*args)


def recuperar_normativa(pregunta):
    """Búsqueda original más artículos de temas reconocidos en configuración.

    Las referencias exactas son ayudas de recuperación, no respuestas prefijadas.
    Siempre se exige texto, metadatos y cita verificable del documento recuperado.
    """
    cfg = cargar_parametros()["rag"]
    originales = retriever.buscar(pregunta, k=cfg["top_k"])
    articulos = list(retriever.articulos_citados(pregunta))
    texto = _normalizar(pregunta)
    for regla in cfg.get("orientacion", []):
        if re.search(regla["patron"], texto):
            articulos.extend(regla["articulos"])
    articulos = list(dict.fromkeys(articulos))
    por_articulo = {h["articulo"] for h in originales}
    faltan = [a for a in articulos if a not in por_articulo]
    exactos = []
    if faltan:
        exactos = retriever.buscar("; ".join("Art. " + a for a in faltan),
                                   k=max(cfg["top_k"], len(faltan)))
        exactos = [h for h in exactos if h["articulo"] in faltan]
    todos = originales + exactos
    prioritarios = [h for h in todos if h["articulo"] in articulos]
    vistos, salida = set(), []
    for h in (prioritarios if articulos else todos):
        if h["id"] not in vistos:
            vistos.add(h["id"])
            salida.append(h)
    return salida[:max(cfg["top_k"], len(articulos))]


def dias_con_antiguedad_declarada(pregunta):
    """Solo años inequívocos aportados por el usuario; nunca argumentos del modelo."""
    texto = _normalizar(pregunta)
    if "vacaciones" not in texto or re.search(r"\b(creo|quizas|supongo|tuviera|tendria)\b|de edad", texto):
        return None
    edades = re.findall(r"(?<![\d.,-])(\d{1,3})\s+anos\b", texto)
    if len(edades) != 1:
        return None
    m = re.search(r"\b(?:llevo|tengo|cumpli|cumplo)\s+(\d{1,3})\s+anos\s+(?:en\b|trabajando\b|de\s+(?:servicio|antiguedad)\b)|\bcon\s+(\d{1,3})\s+anos\b", texto)
    if not m:
        return None
    try:
        return calcular_dias_vacaciones(EntradaDiasVacaciones(anios_servicio=int(m.group(1) or m.group(2))))
    except ValidationError:
        return None


def jornada_declarada(pregunta):
    texto = _normalizar(pregunta)
    if re.search(r"\b(creo|quizas|supongo|tuviera|tendria)\b", texto):
        return None
    coincidencias = re.findall(r"\b(?:trabajo|laboro)\s+(\d+(?:[.,]\d+)?)\s+horas\s+(?:diarias|al dia)\b", texto)
    if len(coincidencias) != 1:
        return None
    try:
        return analizar_jornada(EntradaJornada(horas_diarias=coincidencias[0].replace(",", ".")))
    except ValidationError:
        return None


def completar_condiciones_publicadas(texto, fuentes, pregunta):
    """Evita omitir modalidades de pago: usa párrafos LITERALES de la fuente citada.

    No inventa un resumen legal ni añade una norma que el modelo no haya citado.
    """
    for fuente in fuentes:
        if fuente.articulo not in {"111", "113"}:
            continue
        normal = _normalizar(texto)
        requisitos = ["mensual", "acumul", "escrit"]
        requisitos += ["diciembre"] if fuente.articulo == "111" else ["marzo", "agosto", "jubil"]
        if all(r in normal for r in requisitos):
            continue
        inicio = fuente.texto.find("Los trabajadores")
        if inicio < 0:
            continue
        oraciones = re.split(r"(?<=[.!?])\s+", fuente.texto[inicio:])
        condiciones = [s for s in oraciones if re.search(r"mensual|pedido escrito|jubilad|pensionista", s, re.I)]
        cita = " ".join(condiciones)
        if not all(r in _normalizar(cita) for r in requisitos):
            continue
        literal = f"Según {fuente.documento}, Art. {fuente.articulo}, las condiciones de pago son: «{cita}»"
        texto = literal if len(fuentes) == 1 else texto + " " + literal
    if re.search(r"\b(despid\w*|despido|botaron|desahucio|liquidacion)\b", _normalizar(pregunta)):
        texto += " Para calcular un importe individual falta confirmar la remuneración y los demás datos del formulario. Informe solo saldos pendientes; no incluya valores ya pagados."
    return texto


def consultar_normativa(cliente, pregunta):
    if controlar_alcance(pregunta):
        return None
    cfg = cargar_parametros()
    pregunta = consulta_sin_ordenes_citadas(pregunta)
    hits = recuperar_normativa(pregunta)
    fuentes = [FuenteRAG(id=h["id"], documento=h["documento"], articulo=h["articulo"],
                        texto=h["texto"], fuente=h["fuente"], version=h["version"])
               for h in hits if h.get("vigente") is True
               and all(h.get(k) for k in ("id", "documento", "articulo", "texto", "fuente", "version"))]
    if not fuentes:
        return None
    dias = dias_con_antiguedad_declarada(pregunta) if any(f.articulo == "69" for f in fuentes) else None
    jornada = jornada_declarada(pregunta) if any(f.articulo == "47" for f in fuentes) else None
    contexto = json.dumps({"pregunta": pregunta, "fragmentos": [f.model_dump() for f in fuentes],
                          "resultado_herramienta_dias": dias.model_dump() if dias else None,
                          "resultado_herramienta_jornada": jornada.model_dump() if jornada else None}, ensure_ascii=False)
    if len(contexto) > cfg["agente"]["max_caracteres_contexto"]:
        return None
    respuesta = cliente.generar_json(cargar_prompt(cfg["agente"]["prompt_normativa"]), contexto, TextoNormativo).datos
    if respuesta.estado == "no_disponible":
        if respuesta.respuesta or respuesta.citas:
            raise SalidaInvalida()
        return None
    por_id = {f.id: f for f in fuentes}
    internos = ({"resultado_herramienta_dias"} if dias else set()) | ({"resultado_herramienta_jornada"} if jornada else set())
    respuesta = respuesta.model_copy(update={"citas": [c for c in respuesta.citas if c not in internos]})
    if not respuesta.respuesta.strip() or not respuesta.citas or not set(respuesta.citas) <= por_id.keys():
        raise SalidaInvalida()
    usadas = [por_id[i] for i in dict.fromkeys(respuesta.citas)]
    articulos = set(retriever.articulos_citados(respuesta.respuesta))
    if not articulos <= {f.articulo for f in usadas}:
        raise SalidaInvalida()
    if not articulos:
        # El esquema ya declara los IDs usados. La presentación de la cita se
        # completa con metadatos recuperados, sin otra llamada ni cita inventada.
        referencias = "; ".join(dict.fromkeys(f"{f.documento}, Art. {f.articulo}" for f in usadas))
        respuesta = respuesta.model_copy(update={"respuesta": respuesta.respuesta.rstrip() + " Fuente: " + referencias + "."})
    # La consulta normativa no publica dinero ni operaciones nuevas del modelo.
    if re.search(r"[$€]|\b(?:USD|EUR|d[oó]lares?|euros?)\b|\d\s*[+*/×=]", respuesta.respuesta, re.I):
        raise SalidaInvalida()
    cantidades_fuente = _cantidades_normativas(" ".join(f.texto for f in usadas))
    if jornada:
        if "47" not in {f.articulo for f in usadas}:
            raise SalidaInvalida()
        cantidades_fuente.update((Decimal(str(n)), "hora") for n in
            (jornada.horas_declaradas, jornada.referencia_diaria, jornada.exceso_sobre_referencia))
    if dias:
        if "69" not in {f.articulo for f in usadas}:
            raise SalidaInvalida()
        calculado = (Decimal(dias.dias_anuales), "dia")
        cantidades_fuente.update((Decimal(n), "dia") for n in (dias.dias_base, dias.dias_adicionales, dias.dias_anuales))
        cantidades_fuente.add((Decimal(dias.anios_servicio), "ano"))
        if calculado not in _cantidades_normativas(respuesta.respuesta):
            raise SalidaInvalida()
    if not _cantidades_normativas(respuesta.respuesta) <= cantidades_fuente:
        raise SalidaInvalida()
    publicada = completar_condiciones_publicadas(respuesta.respuesta, usadas, pregunta)
    return NormativaAgente(respuesta=publicada, fuentes=usadas, calculo_dias=dias, calculo_jornada=jornada)


def ejecutar_agente(consulta: ConsultaAgente, cliente) -> RespuestaAgente:
    consulta = consulta.model_copy(update={"mensaje": consulta_sin_ordenes_citadas(consulta.mensaje)})
    bloqueo = controlar_alcance(consulta.mensaje, consulta.calculo is not None)
    if bloqueo:
        return RespuestaAgente(estado=bloqueo[0], mensaje=bloqueo[1])
    config = cargar_parametros()["agente"]
    llm = ClienteAcotado(cliente, config["max_llamadas_modelo"])
    calculos = {"calculo-0": consulta.calculo} if consulta.calculo else {}
    publicados, explicaciones, normativa, pasos, faltantes = {}, [], [], [], []
    pendiente, agotado, rechazado = False, False, False
    pendiente_resumen = None
    mensajes = [{"role": "system", "content": cargar_prompt(config["prompt"])},
                {"role": "user", "content": json.dumps({"mensaje": consulta.mensaje,
                 "calculo_confirmado": {"id": "calculo-0", "resultado": consulta.calculo.model_dump(mode="json")} if consulta.calculo else None,
                 "confirmacion_liquidacion": consulta.confirmar_liquidacion}, ensure_ascii=False)}]
    iteraciones = 0

    def respuesta(estado, mensaje):
        resumen = []
        if pendiente and consulta.calculo and consulta.calculo.tipo == "liquidacion":
            d = consulta.calculo.entradas
            resumen = ["Se usarán los saldos del último formulario, sin modificarlos.",
                       f"Motivo informado: {d['motivo_salida'].replace('_', ' ')}.",
                       f"Ingreso: {d['fecha_ingreso']}; salida: {d['fecha_salida']}.",
                       f"Total estimado del formulario: USD {consulta.calculo.total:.2f}."]
        return RespuestaAgente(estado=estado, mensaje=mensaje,
            calculos=[CalculoAgente(id=i, resultado=r) for i, r in publicados.items()],
            explicaciones=explicaciones, normativa=normativa, pasos=pasos,
            faltantes=list(dict.fromkeys(faltantes)), resumen_confirmacion=resumen,
            iteraciones=iteraciones, llamadas_modelo=llm.usadas,
            calculo_para_resumen=pendiente_resumen)

    def ejecutar(nombre, datos):
        nonlocal pendiente, pendiente_resumen
        herramienta = PERMITIDAS[nombre]
        if herramienta.calcular:
            if not consulta.calculo or consulta.calculo.tipo not in herramienta.tipos:
                faltantes.append("Complete y calcule primero el formulario correspondiente; luego marque usar sus datos en la consulta.")
                return {"estado": "pedir_datos", "mensaje": faltantes[-1]}
            entrada = {k: v for k, v in consulta.calculo.entradas.items() if k in herramienta.esquema.model_fields}
            if nombre == "calcular_decimos":
                entrada["tipo"] = consulta.calculo.tipo
            esperado = herramienta.esquema.model_validate(entrada)
            if esperado.model_dump() != datos.model_dump():
                faltantes.append("Los argumentos propuestos no coinciden con el formulario confirmado. Revise sus datos; no se completaron ni cambiaron valores.")
                return {"estado": "pedir_datos", "mensaje": faltantes[-1]}
            if nombre == "estimar_liquidacion" and not consulta.confirmar_liquidacion:
                pendiente = True
                return {"estado": "requiere_confirmacion", "mensaje": "El usuario debe confirmar el uso de los saldos; una orden del modelo no los confirma."}
            resultado = herramienta.calcular(datos)
            ident = f"calculo-{len(calculos) + (0 if consulta.calculo else 1)}"
            calculos[ident] = publicados[ident] = resultado
            return {"estado": "ok", "calculo_id": ident, "resultado": resultado.model_dump(mode="json")}
        if nombre == "consultar_normativa":
            # La pregunta del usuario es la autoridad. Una paráfrasis del modelo
            # no puede sustituirla ni introducir nuevos artículos o condiciones.
            r = consultar_normativa(llm, consulta.mensaje)
            if r:
                normativa.append(r)
                return {"estado": "ok", **r.model_dump(mode="json")}
            return {"estado": "abstencion", "mensaje": rag.SIN_RESPALDO}
        if nombre == "solicitar_datos":
            esquemas = {"decimo_tercero": EntradaDecimoTercero, "decimo_cuarto": EntradaDecimoCuarto,
                        "vacaciones": EntradaVacaciones, "horas_extra": EntradaHoras, "liquidacion": EntradaLiquidacion}
            campos = [nombre for nombre, campo in esquemas[datos.tipo_calculo].model_fields.items() if campo.is_required()]
            faltantes.append("Complete el formulario de " + datos.tipo_calculo.replace("_", " ") +
                             ": " + ", ".join(c.replace("_", " ") for c in campos) + ".")
            return {"estado": "pedir_datos", "mensaje": faltantes[-1]}
        if nombre in ("explicar_resultado", "generar_resumen"):
            if datos.calculo_id not in calculos:
                faltantes.append("El cálculo solicitado no existe en esta consulta. Use el formulario o un identificador devuelto por una herramienta.")
                return {"estado": "pedir_datos", "mensaje": faltantes[-1]}
            resultado = calculos[datos.calculo_id]
            if nombre == "generar_resumen":
                pendiente_resumen = resultado
                publicados[datos.calculo_id] = resultado
                return {"estado": "requiere_confirmacion", "mensaje": "Se preparará la vista previa. Solo un clic humano en confirmar y descargar generará el PDF."}
            if resultado.tipo == "liquidacion" and not consulta.confirmar_liquidacion:
                pendiente = True
                return {"estado": "requiere_confirmacion", "mensaje": "Confirme el uso de los saldos del formulario."}
            fuentes = rag.recuperar_calculo(resultado)
            if not fuentes:
                return {"estado": "abstencion", "mensaje": rag.SIN_RESPALDO}
            r, usadas = rag.explicar_calculo(llm, resultado, fuentes)
            if r.datos.estado != "ok":
                return {"estado": "abstencion", "mensaje": rag.SIN_RESPALDO}
            publicados[datos.calculo_id] = resultado
            exp = ExplicacionAgente(calculo_id=datos.calculo_id, explicacion=r.datos, fuentes=usadas)
            explicaciones.append(exp)
            return {"estado": "ok", **exp.model_dump(mode="json")}
        raise ValueError("Herramienta sin implementación")

    for iteraciones in range(1, config["max_iteraciones"] + 1):
        if len(json.dumps(mensajes, ensure_ascii=False)) > config["max_caracteres_contexto"]:
            return respuesta("limite", "La consulta alcanzó el tamaño permitido. Divídala en consultas más pequeñas.")
        try:
            mensaje = llm.generar_herramientas(mensajes, esquemas_herramientas(),
                                              requerir_herramienta=iteraciones == 1).datos
        except LimiteAgente:
            return respuesta("limite", "Se alcanzó el límite de consultas al modelo. Revise los resultados disponibles o solicite revisión humana.")
        llamadas = mensaje.get("tool_calls") or []
        if not llamadas:
            if publicados or normativa or explicaciones:
                return respuesta("completado", "Estos son los resultados obtenidos para su consulta.")
            return respuesta("pedir_datos", "No se obtuvo una respuesta verificable. Complete el formulario y permita usar sus datos, o formule una pregunta normativa concreta.")
        ids = [c.get("id") for c in llamadas]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise SalidaInvalida()
        mensajes.append(mensaje)
        exceso = len(llamadas) > config["max_herramientas_por_vuelta"]
        hubo_abstencion = False
        # Siempre responder TODAS las llamadas del lote antes de detenerse.
        for llamada in llamadas:
            funcion = llamada.get("function") or {}
            nombre = funcion.get("name", "")
            try:
                if exceso:
                    agotado = True
                    salida = {"estado": "limite", "mensaje": "Demasiadas herramientas en una sola vuelta."}
                elif nombre not in PERMITIDAS:
                    rechazado = True
                    salida = {"estado": "rechazado", "mensaje": "Herramienta no permitida."}
                else:
                    argumentos = funcion.get("arguments", "")
                    if not isinstance(argumentos, str) or len(argumentos) > config["max_caracteres_argumentos"]:
                        raise ValueError("Argumentos demasiado largos o con formato incorrecto")
                    objeto = json.loads(argumentos)
                    if not isinstance(objeto, dict):
                        raise ValueError("Los argumentos deben ser un objeto")
                    datos = PERMITIDAS[nombre].esquema.model_validate(objeto)
                    salida = ejecutar(nombre, datos)
            except ValidationError as e:
                campos = [".".join(map(str, x["loc"])) for x in e.errors()]
                faltantes.extend(f"{nombre}: revise {campo}" for campo in campos)
                salida = {"estado": "pedir_datos", "campos": campos}
            except (ValueError, TypeError):
                faltantes.append(f"Revise los argumentos de {nombre}; no se ejecutó con datos inválidos.")
                salida = {"estado": "pedir_datos", "mensaje": faltantes[-1]}
            except SalidaInvalida:
                salida = {"estado": "abstencion", "mensaje": "La respuesta no superó la comprobación de sus fuentes o valores."}
            except LimiteAgente:
                agotado = True
                salida = {"estado": "limite", "mensaje": "Límite de llamadas al modelo alcanzado."}
            hubo_abstencion |= salida["estado"] == "abstencion"
            pasos.append(PasoAgente(herramienta=nombre, estado=salida["estado"]))
            mensajes.append({"role": "tool", "tool_call_id": llamada["id"],
                             "content": json.dumps(salida, ensure_ascii=False)})
        if pendiente_resumen is not None:
            return respuesta("requiere_confirmacion", "Revise la vista previa del resumen y confirme su generación en PDF.")
        if pendiente:
            return respuesta("requiere_confirmacion", "Revise y confirme los saldos del formulario antes de continuar con la liquidación.")
        if agotado:
            return respuesta("limite", "Se alcanzó un límite del agente. Revise los resultados disponibles.")
        if rechazado:
            return respuesta("rechazado", "Se rechazó una herramienta fuera del alcance permitido.")
        if faltantes:
            return respuesta("pedir_datos", "Faltan datos confirmados o los argumentos no coinciden con el formulario. Revise los campos indicados.")
        if hubo_abstencion:
            return respuesta("abstencion", rag.SIN_RESPALDO)
        if normativa and not consulta.calculo:
            return respuesta("completado", "Estos son los resultados obtenidos para su consulta.")
    return respuesta("limite", "Se alcanzó el máximo de vueltas. Revise los resultados disponibles o consulte al Ministerio del Trabajo.")
