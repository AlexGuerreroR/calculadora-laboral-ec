"""El formulario guiado también calcula la liquidación (finiquito) y las horas extra, sin IA."""
from fastapi.testclient import TestClient

from app.main import app
from app.routers import explicar

cliente = TestClient(app)
C10 = {"remuneracion_mensual": 1000, "fecha_ingreso": "2020-08-01", "fecha_salida": "2026-08-31",
       "motivo": "despido_intempestivo", "region": "sierra_amazonia"}


def test_liquidacion_por_formulario_c10():
    r = cliente.post("/calculos/liquidacion", json=C10)
    assert r.status_code == 200 and r.json()["total"] == 9331.84 and r.json()["tipo"] == "liquidacion"


def test_horas_extra_por_formulario_c08():
    r = cliente.post("/calculos/horas-extra",
                     json={"remuneracion_mensual": 800, "horas_suplementarias": 10, "horas_extraordinarias": 4})
    assert r.status_code == 200 and r.json()["total"] == 76.67


def test_liquidacion_invalida_es_422():
    assert cliente.post("/calculos/liquidacion", json={**C10, "motivo": "otro"}).status_code == 422
    assert cliente.post("/calculos/liquidacion", json={**C10, "fecha_salida": "2019-01-01"}).status_code == 422


def test_explicar_recalcula_tambien_la_liquidacion():
    resultado = cliente.post("/calculos/liquidacion", json=C10).json()
    assert explicar.recalcular(explicar.ResultadoCalculo(**resultado)).total == 9331.84
