"""Pruebas del agente con un DOBLE del modelo y del buscador: sin API, sin internet, sin ChromaDB.

El doble devuelve, turno por turno, lo que le indiquemos: una llamada a herramienta o un texto.
Así se prueba lo que decide el CÓDIGO: lista cerrada, tope, confirmación y verificación de citas.
"""
import json
from types import SimpleNamespace

from app.services import agent
from app.services.llm import Resultado

ART_188 = {"articulo": "188", "texto": "Art. 188.- Indemnización por despido intempestivo.- …",
           "tema": "despido", "capitulo": "Capítulo X · Del desahucio y del despido", "distancia": 0.1}
C10 = {"remuneracion_mensual": 1000, "fecha_ingreso": "2020-08-01", "fecha_salida": "2026-08-31",
       "motivo": "despido_intempestivo", "region": "sierra_amazonia"}


def llamada(nombre, argumentos, id_="c1"):
    return SimpleNamespace(content=None, tool_calls=[SimpleNamespace(
        id=id_, function=SimpleNamespace(name=nombre, arguments=json.dumps(argumentos)))])


def texto(t):
    return SimpleNamespace(content=t, tool_calls=None)


class LLMFalso:
    def __init__(self, *turnos):
        self.turnos, self.recibido = list(turnos), []

    def generar_con_herramientas(self, system, mensajes, herramientas):
        self.recibido.append([dict(m) for m in mensajes])
        return Resultado(self.turnos.pop(0), "simulado", "falso", 10, 10, 5, 1)


def buscador_falso(pregunta, k=5, tema=None):
    return [ART_188]


def correr(*turnos):
    llm = LLMFalso(*turnos)
    r, mensajes, ctx = agent.iniciar(llm, "Me despidieron sin visto bueno", buscador_falso)
    return r, llm, ctx


# ---------------------------------------------------------------- camino feliz
def test_calcula_con_la_herramienta_y_cita_lo_recuperado():
    r, llm, _ = correr(
        llamada("estimar_liquidacion", C10, "c1"),
        llamada("consultar_articulo", {"pregunta": "despido intempestivo", "tema": "despido"}, "c2"),
        texto("Su liquidación estimada es de USD 9331,84, según el Art. 188. Es una orientación."))
    assert r.estado == "ok"
    assert r.calculos[0]["total"] == 9331.84
    assert [f["articulo"] for f in r.fuentes] == ["188"]
    assert r.pasos == ["estimar_liquidacion", "consultar_articulo"]
    # el resultado de la herramienta volvió al modelo como mensaje «tool»
    assert llm.recibido[1][-1]["role"] == "tool"


def test_los_fragmentos_van_etiquetados_como_datos():
    _, llm, _ = correr(llamada("consultar_articulo", {"pregunta": "despido"}),
                       texto("Según el Art. 188, corresponde indemnización. Es una orientación."))
    assert "<fragmento>" in llm.recibido[1][-1]["content"]


# ---------------------------------------------------------------- lista cerrada y tope
def test_herramienta_fuera_de_la_lista_no_se_ejecuta():
    r, llm, _ = correr(llamada("enviar_correo_al_empleador", {"texto": "hola"}),
                       texto("SIN_FUENTE"))
    assert agent.NO_PERMITIDA in llm.recibido[1][-1]["content"]
    assert r.pasos == [] and r.estado == "abstencion"


def test_tope_de_iteraciones():
    turnos = [llamada("consultar_articulo", {"pregunta": "despido"}, f"c{i}") for i in range(10)]
    r, llm, _ = correr(*turnos)
    assert r.estado == "tope"
    assert len(llm.recibido) == 6  # agente.max_iteraciones en config/parametros.yaml


def test_argumentos_incompletos_vuelven_al_modelo_para_pedir_el_dato():
    r, llm, _ = correr(llamada("estimar_liquidacion", {"remuneracion_mensual": 1000}),
                       texto("FALTA: ¿En qué fecha empezó y en qué fecha terminó de trabajar?"))
    assert "Pídale al usuario" in llm.recibido[1][-1]["content"]
    assert r.estado == "falta" and r.calculos == []


# ---------------------------------------------------------------- verificación de la respuesta final
def test_cita_inventada_se_abstiene():
    r, _, _ = correr(llamada("consultar_articulo", {"pregunta": "despido"}),
                     texto("Según el Art. 999 le corresponde todo. Es una orientación."))
    assert r.estado == "abstencion" and r.respuesta == agent.ABSTENCION


def test_monto_que_no_salio_de_una_herramienta_se_abstiene():
    r, _, _ = correr(llamada("consultar_articulo", {"pregunta": "despido"}),
                     texto("Según el Art. 188 recibirá unos USD 3000,00. Es una orientación."))
    assert r.estado == "abstencion"


def test_respuesta_sin_cita_se_abstiene():
    r, _, _ = correr(texto("Le corresponde una indemnización."))
    assert r.estado == "abstencion"


def test_sin_fuente_se_abstiene():
    r, _, _ = correr(llamada("consultar_articulo", {"pregunta": "capital de Francia"}), texto("SIN_FUENTE"))
    assert r.estado == "abstencion"


def test_articulos_y_montos_en_varias_formas():
    assert agent.articulos_en("arts. 185 y 188; Art. 71 y el artículo 111") == {"185", "188", "71", "111"}
    assert {str(m) for m in agent.montos_en("USD 9.331,84 o $9331.84 o 1,130.33 dólares")} == {"9331.84", "1130.33"}


# ---------------------------------------------------------------- confirmación humana
def test_derivar_se_pausa_hasta_que_el_usuario_confirme():
    r, _, ctx = correr(llamada("derivar_al_ministerio", {"motivo": "quiere demandar al empleador"}))
    assert r.estado == "pendiente_confirmacion"
    assert "derivar_al_ministerio" not in r.pasos      # todavía NO se ejecutó
    hecho = agent.confirmar(r.pendiente, True, ctx)
    assert hecho.estado == "derivado" and "Ministerio del Trabajo" in hecho.respuesta
    assert hecho.pasos == ["derivar_al_ministerio"]


def test_si_el_usuario_rechaza_no_se_deriva():
    r, _, ctx = correr(llamada("derivar_al_ministerio", {"motivo": "conflicto"}))
    rechazo = agent.confirmar(r.pendiente, False, ctx)
    assert rechazo.estado == "rechazado" and rechazo.pasos == []


def test_lista_cerrada_y_niveles_coinciden_con_el_adr():
    assert agent.REQUIEREN_OK == {"derivar_al_ministerio"}
    assert agent.PERMITIDAS == {"consultar_articulo", "calcular_decimo_tercero", "calcular_decimo_cuarto",
                                "calcular_vacaciones", "calcular_horas_extra", "estimar_liquidacion",
                                "derivar_al_ministerio"}
    nombres = [d["function"]["name"] for d in agent.definiciones()]
    assert sorted(nombres) == sorted(agent.PERMITIDAS)
