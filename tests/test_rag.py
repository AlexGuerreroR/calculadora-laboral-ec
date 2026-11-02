"""Comprobación breve del RAG y del endpoint, sin proveedor ni descargas."""
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import explicar
from app.schemas import EntradaDecimoTercero, ExplicacionRAG, FuenteRAG
from app.services import rag
from app.services.llm import SalidaInvalida
from app.tools.decimos import calcular_decimo_tercero

RESULTADO = calcular_decimo_tercero(EntradaDecimoTercero(remuneraciones=[600] * 12))
FUENTE = FuenteRAG(id="art-111", documento="Código del Trabajo", articulo="111",
                  texto="Art. 111.- Tiene derecho a la doceava parte de sus remuneraciones.",
                  fuente="https://www.trabajo.gob.ec/", version="prueba")


def salida(**cambios):
    datos = dict(estado="ok", explicacion="Según el Art. 111, su valor es USD 600.00.",
                 pasos=[], advertencias=[], faltantes=[], citas=["art-111"])
    return ExplicacionRAG(**(datos | cambios))


def test_explicacion_con_fuente_y_monto_verificados():
    assert rag.validar_explicacion(salida(), [FUENTE], RESULTADO) == [FUENTE]


@pytest.mark.parametrize("cambios", [
    {"citas": ["art-999"]}, {"citas": []},
    {"explicacion": "Según el Art. 999, su valor es USD 600.00."},
    {"explicacion": "Según el Art. 111, su valor es USD 111.00."},
    {"explicacion": "Según el Art. 111, su valor es USD 999.00."},
    {"explicacion": "Según el Art. 111, su valor es USD999.00."},
    {"explicacion": "Según el Art. 111, su valor es 999.00 USD."},
    {"explicacion": "Según el Art. 111, su valor es USD -600.00."},
    {"explicacion": "Según el Art. 111, su valor es USD 600,00."},
    {"estado": "no_disponible"},
])
def test_rechaza_citas_montos_y_abstencion_incoherentes(cambios):
    with pytest.raises(SalidaInvalida):
        rag.validar_explicacion(salida(**cambios), [FUENTE], RESULTADO)


def test_recuperacion_exige_articulos_y_metadatos(monkeypatch):
    hit = {**FUENTE.model_dump(), "vigente": True}
    buscar = Mock(return_value=[hit])
    monkeypatch.setattr(rag.retriever, "buscar", buscar)
    assert rag.recuperar_calculo(RESULTADO) == [FUENTE]
    assert "Art. 111" in buscar.call_args.args[0]
    buscar.return_value = [{**hit, "vigente": False}]
    assert rag.recuperar_calculo(RESULTADO) == []
    buscar.return_value = [{**hit, "fuente": ""}]
    assert rag.recuperar_calculo(RESULTADO) == []


def test_sin_fuentes_se_abstiene_sin_crear_cliente():
    fabrica = Mock(side_effect=AssertionError("No debe crear cliente ni gastar API"))
    app.dependency_overrides[explicar.obtener_llm] = lambda: fabrica
    app.dependency_overrides[explicar.obtener_recuperador] = lambda: (lambda resultado: [])
    explicar.limitador = explicar.LimitadorPorMinuto(100)
    try:
        r = TestClient(app).post("/explicar", json=RESULTADO.model_dump(mode="json"))
        assert r.status_code == 200
        assert r.json()["explicacion"] is None and r.json()["fuentes"] == []
        assert "respaldo suficiente" in r.json()["mensaje"]
        fabrica.assert_not_called()
    finally:
        app.dependency_overrides.clear()
