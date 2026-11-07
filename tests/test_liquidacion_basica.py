from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app


DATOS = {
    "remuneracion_mensual": "480",
    "fecha_ingreso": "2026-01-01",
    "fecha_salida": "2026-11-05",
    "motivo_salida": "despido_intempestivo",
    "region": "sierra_amazonia",
    "mensualiza_decimo_tercero": False,
    "mensualiza_decimo_cuarto": False,
}
RUTA = "/calculos/liquidacion/basica"


@pytest.mark.parametrize(("ingreso", "dias"), [
    ("2026-01-01", "12.83"),
    ("2026-05-01", "7.83"),
    ("2026-07-01", "5.29"),
])
def test_sugerencia_de_vacaciones(ingreso, dias):
    respuesta = TestClient(app).get(f"{RUTA}/vacaciones", params={
        "fecha_ingreso": ingreso, "fecha_salida": DATOS["fecha_salida"],
    })
    assert respuesta.status_code == 200
    assert respuesta.json()["dias"] == dias


@pytest.mark.parametrize(("cambios", "total"), [
    ({}, "2179.14"),
    ({"region": "costa_galapagos"}, "2379.98"),
    ({"mensualiza_decimo_tercero": True, "mensualiza_decimo_cuarto": True}, "1658.64"),
    ({"dias_vacaciones_pendientes": "1"}, "1989.86"),
    ({"dias_vacaciones_pendientes": "0"}, "1973.86"),
])
def test_estimacion_segun_periodos_y_saldo_informado(cambios, total):
    respuesta = TestClient(app).post(RUTA, json=DATOS | cambios)
    assert respuesta.status_code == 200, respuesta.text
    resultado = respuesta.json()
    assert Decimal(str(resultado["total"])) == Decimal(total)
    assert resultado["entradas"]["modo"] == "basico"
    assert any("Monto referencial" in rubro for rubro in resultado["desglose"])


@pytest.mark.parametrize("cambios", [
    {"motivo_salida": "otro"},
    {"fecha_salida": "2025-12-31", "fecha_ingreso": "2025-01-01"},
    {"fecha_ingreso": "2026-11-06"},
    {"dias_vacaciones_pendientes": "-1"},
])
def test_datos_invalidos(cambios):
    respuesta = TestClient(app).post(RUTA, json=DATOS | cambios)
    assert respuesta.status_code == 422


def test_pdf_basico_recalcula_y_requiere_confirmacion(monkeypatch):
    monkeypatch.setattr("app.routers.resumen.rag.recuperar_calculo", lambda resultado: [])
    cliente = TestClient(app)
    calculo = cliente.post(RUTA, json=DATOS).json()
    alterado = calculo | {"total": calculo["total"] + 100}
    assert cliente.post("/resumen/preparar", json={"calculo": alterado}).status_code == 422

    respuesta = cliente.post("/resumen/preparar", json={"calculo": calculo})
    assert respuesta.status_code == 200, respuesta.text
    token = respuesta.json()["token"]
    assert cliente.post("/resumen/confirmar", json={"token": token}).status_code == 422
    pdf = cliente.post("/resumen/confirmar", json={"token": token, "confirmar": True})
    assert pdf.status_code == 200, pdf.text
    assert pdf.content.startswith(b"%PDF-")
