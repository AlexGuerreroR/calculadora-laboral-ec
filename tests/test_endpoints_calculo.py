"""Pruebas de los endpoints de cálculo (no llaman al modelo).

    pytest -q tests/test_endpoints_calculo.py
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def post(ruta, cuerpo):
    return cliente.post(ruta, json=cuerpo)


# ---------------------------------------------------------------- casos de referencia por HTTP
@pytest.mark.parametrize("cuerpo, esperado", [
    ({"tipo": "decimo_tercero", "remuneraciones": [600] * 12}, 600.00),                       # C01
    ({"tipo": "decimo_tercero", "remuneraciones": [700] * 9 + [850] * 3}, 737.50),            # C03
    ({"tipo": "decimo_cuarto", "meses_trabajados": 12, "region": "sierra_amazonia"}, 482.00),  # C04
    ({"tipo": "decimo_cuarto", "meses_trabajados": 6, "region": "costa_galapagos"}, 241.00),   # C05
])
def test_decimos(cuerpo, esperado):
    r = post("/calculos/decimos", cuerpo)
    assert r.status_code == 200
    assert abs(r.json()["total"] - esperado) <= 0.01
    assert r.json()["fundamento"]  # la norma la pone el código


def test_vacaciones_c07():
    r = post("/calculos/vacaciones", {"remuneracion_mensual": 900, "fecha_ingreso": "2019-03-01",
                                      "fecha_corte": "2026-03-01"})
    assert r.status_code == 200 and abs(r.json()["total"] - 510.00) <= 0.01


# ---------------------------------------------------------------- entradas inválidas: 422, mensaje claro
@pytest.mark.parametrize("cuerpo", [
    {"tipo": "decimo_tercero"},                                                        # falta remuneraciones
    {"tipo": "decimo_tercero", "remuneraciones": [-500]},                               # negativo
    {"tipo": "decimo_tercero", "remuneraciones": [600] * 13},                           # 13 meses
    {"tipo": "decimo_cuarto", "meses_trabajados": 6},                                   # falta región
    {"tipo": "decimo_cuarto", "meses_trabajados": 13, "region": "sierra_amazonia"},     # 13 meses
    {"tipo": "decimo_cuarto", "meses_trabajados": 6, "region": "luna"},                 # región inválida
    {"tipo": "decimo_quinto", "remuneraciones": [600]},                                 # tipo inexistente
    {"tipo": "decimo_tercero", "remuneraciones": [600], "sueldo_secreto": 1},           # campo inventado
])
def test_decimos_rechaza_entradas_invalidas(cuerpo):
    r = post("/calculos/decimos", cuerpo)
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    assert "Traceback" not in r.text


def test_nan_se_rechaza():
    r = cliente.post("/calculos/decimos", content='{"tipo": "decimo_tercero", "remuneraciones": [NaN]}',
                     headers={"Content-Type": "application/json"})
    assert r.status_code == 422


def test_vacaciones_fecha_futura():
    r = post("/calculos/vacaciones", {"remuneracion_mensual": 600, "fecha_ingreso": "2099-01-01"})
    assert r.status_code == 422


def test_health():
    assert cliente.get("/health").json() == {"status": "ok"}
