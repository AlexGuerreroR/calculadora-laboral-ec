"""Pruebas de POST /consultar y /consultar/confirmar con dobles del modelo y del buscador."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import consultar as modulo
from app.routers import explicar as compartido
from tests.test_agente import C10, LLMFalso, buscador_falso, llamada, texto


@pytest.fixture(autouse=True)
def limpio():
    compartido.limitador = compartido.LimitadorPorMinuto(4)
    modulo.sesiones = modulo.Sesiones()
    yield
    app.dependency_overrides.clear()


def cliente_con(llm):
    app.dependency_overrides[compartido.obtener_llm] = lambda: (lambda: llm)
    app.dependency_overrides[modulo.obtener_buscador] = lambda: buscador_falso
    return TestClient(app)


def test_pregunta_libre_devuelve_calculo_y_fuente():
    llm = LLMFalso(llamada("estimar_liquidacion", C10, "c1"),
                   llamada("consultar_articulo", {"pregunta": "despido"}, "c2"),
                   texto("Su liquidación estimada es de USD 9331,84 (Art. 188). Es una orientación."))
    r = cliente_con(llm).post("/consultar", json={"pregunta": "Me despidieron, ganaba 1000…"})
    assert r.status_code == 200
    c = r.json()
    assert c["estado"] == "ok" and c["calculos"][0]["total"] == 9331.84
    assert c["fuentes"][0]["articulo"] == "188" and c["aviso"]


@pytest.mark.parametrize("pregunta", ["", "ab", "x" * 601])
def test_pregunta_invalida_no_llega_al_modelo(pregunta):
    llm = LLMFalso()
    r = cliente_con(llm).post("/consultar", json={"pregunta": pregunta})
    assert r.status_code == 422 and llm.recibido == []


def test_campo_extra_o_sin_pregunta_es_422():
    r = cliente_con(LLMFalso()).post("/consultar", json={})
    assert r.status_code == 422


def test_confirmacion_humana_por_sesion_y_de_un_solo_uso():
    cliente = cliente_con(LLMFalso(llamada("derivar_al_ministerio", {"motivo": "quiere demandar"})))
    r = cliente.post("/consultar", json={"pregunta": "Quiero demandar a mi empleador"}).json()
    assert r["estado"] == "pendiente_confirmacion" and r["sesion"]
    ok = cliente.post("/consultar/confirmar", json={"sesion": r["sesion"], "aprobar": True})
    assert ok.json()["estado"] == "derivado"
    otra_vez = cliente.post("/consultar/confirmar", json={"sesion": r["sesion"], "aprobar": True})
    assert otra_vez.status_code == 404


def test_limite_por_minuto():
    cliente = cliente_con(LLMFalso(*[texto("SIN_FUENTE")] * 5))
    codigos = [cliente.post("/consultar", json={"pregunta": "hola hola"}).status_code for _ in range(5)]
    assert codigos[:4] == [200] * 4 and codigos[4] == 429


def test_base_no_disponible_es_503():
    def roto(*a, **k):
        raise RuntimeError("no hay índice")
    app.dependency_overrides[compartido.obtener_llm] = lambda: (
        lambda: LLMFalso(llamada("consultar_articulo", {"pregunta": "despido"})))
    app.dependency_overrides[modulo.obtener_buscador] = lambda: roto
    r = TestClient(app).post("/consultar", json={"pregunta": "Me despidieron"})
    assert r.status_code == 503
