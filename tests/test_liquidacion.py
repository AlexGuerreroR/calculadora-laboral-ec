"""Referencias del Excel B4, hojas Resultados y Calculos y fuentes, sin modificarlo.

C09/C10 conservan los supuestos escritos en filas 17–19 de Resultados.
Estos resultados prueban el ejercicio; no certifican su vigencia jurídica a 2026.
"""
from copy import deepcopy
from decimal import Decimal
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas import EntradaLiquidacion
from app.tools.liquidacion import estimar_liquidacion, antiguedad

C09 = dict(remuneracion_mensual=700, fecha_ingreso="2024-06-01", fecha_salida="2026-09-30",
           motivo_salida="renuncia_con_desahucio", region="sierra_amazonia", salario_pendiente=0,
           base_acumulada_decimo_tercero=7000, dias_decimo_cuarto_pendientes=60,
           dias_vacaciones_base_pendientes=5, dias_vacaciones_adicionales_pendientes=0,
           horas_suplementarias_pendientes=0, horas_extraordinarias_pendientes=0,
           descuentos_confirmados=0, criterios_confirmados=True)
C10 = C09 | dict(remuneracion_mensual=1000, fecha_ingreso="2020-08-01", fecha_salida="2026-08-31",
                 motivo_salida="despido_intempestivo", base_acumulada_decimo_tercero=9000,
                 dias_decimo_cuarto_pendientes=30, dias_vacaciones_base_pendientes="1.25")

REFERENCIAS = [
    ("C01", "/calculos/decimos", {"tipo": "decimo_tercero", "remuneraciones": [600] * 12}, "600.00"),
    ("C02", "/calculos/decimos", {"tipo": "decimo_tercero", "remuneraciones": [500] * 6}, "250.00"),
    ("C03", "/calculos/decimos", {"tipo": "decimo_tercero", "remuneraciones": [700] * 9 + [850] * 3}, "737.50"),
    ("C04", "/calculos/decimos", {"tipo": "decimo_cuarto", "meses_trabajados": 12, "region": "sierra_amazonia"}, "482.00"),
    ("C05", "/calculos/decimos", {"tipo": "decimo_cuarto", "meses_trabajados": 6, "region": "costa_galapagos"}, "241.00"),
    ("C06", "/calculos/vacaciones", {"remuneracion_mensual": 600, "fecha_ingreso": "2025-10-01", "fecha_corte": "2026-10-01"}, "300.00"),
    ("C07", "/calculos/vacaciones", {"remuneracion_mensual": 900, "fecha_ingreso": "2019-03-01", "fecha_corte": "2026-03-01"}, "510.00"),
    ("C08", "/calculos/horas", {"remuneracion_mensual": 800, "horas_suplementarias": 10, "horas_extraordinarias": 4}, "76.67"),
    ("C09", "/calculos/liquidacion", C09, "1130.33"),
    ("C10", "/calculos/liquidacion", C10, "9331.84"),
]


@pytest.mark.parametrize("ident,ruta,datos,esperado", REFERENCIAS, ids=[r[0] for r in REFERENCIAS])
def test_diez_casos_del_excel(ident, ruta, datos, esperado):
    r = TestClient(app).post(ruta, json=datos)
    assert r.status_code == 200, r.text
    assert abs(Decimal(str(r.json()["total"])) - Decimal(esperado)) <= Decimal("0.01"), ident


@pytest.mark.parametrize("ingreso,salida,meses", [
    ("2023-01-01", "2025-12-01", 3),  # 2 años y 11 meses
    ("2023-01-01", "2026-01-01", 3),  # 3 años exactos
    ("2023-01-01", "2026-01-02", 4),  # una fracción después de 3 años
    ("1999-01-01", "2026-01-01", 25), # tope
])
def test_limites_despido(ingreso, salida, meses):
    datos = C10 | dict(fecha_ingreso=ingreso, fecha_salida=salida, base_acumulada_decimo_tercero=0,
                      dias_decimo_cuarto_pendientes=0, dias_vacaciones_base_pendientes=0)
    r = estimar_liquidacion(EntradaLiquidacion(**datos))
    assert f"Indemnización por despido intempestivo: {meses * 1000}.00" in r.desglose


def test_aniversario_bisiesto():
    from datetime import date
    assert antiguedad(date(2024, 2, 29), date(2025, 2, 28)) == (1, False)


@pytest.mark.parametrize("cambios", [
    {"salario_pendiente": -1}, {"criterios_confirmados": False},
    {"fecha_salida": "2020-01-01"}, {"fecha_salida": "2099-01-01"},
    {"dias_decimo_cuarto_pendientes": 361}, {"dias_vacaciones_base_pendientes": -1},
    {"horas_suplementarias_pendientes": "Infinity"}, {"motivo_salida": "desconocido"},
])
def test_entrada_invalida(cambios):
    r = TestClient(app).post("/calculos/liquidacion", json=C09 | cambios)
    assert r.status_code == 422


def test_no_asume_un_saldo_omitido():
    datos = deepcopy(C09)
    del datos["dias_vacaciones_adicionales_pendientes"]
    with pytest.raises(ValidationError):
        EntradaLiquidacion(**datos)


def test_febrero_completo_admite_30_dias_comerciales():
    datos = C09 | dict(fecha_ingreso="2026-02-01", fecha_salida="2026-02-28", dias_decimo_cuarto_pendientes=30)
    assert EntradaLiquidacion(**datos).dias_decimo_cuarto_pendientes == 30


def test_salarios_horas_descuentos_y_adicionales_se_integran():
    datos = C09 | dict(salario_pendiente=100, horas_suplementarias_pendientes=8,
                      dias_vacaciones_adicionales_pendientes=1, descuentos_confirmados=20)
    r = estimar_liquidacion(EntradaLiquidacion(**datos))
    assert Decimal(str(r.total)) == Decimal("1268.66")  # 1130.33 + 100 + 35 + 23.33 - 20


def test_descuentos_superiores_al_total_no_se_aceptan():
    r = TestClient(app).post("/calculos/liquidacion", json=C09 | {"descuentos_confirmados": 100000})
    assert r.status_code == 422


def test_c10_deja_visible_el_supuesto_de_vacaciones():
    r = estimar_liquidacion(EntradaLiquidacion(**C10))
    assert any("saldo cero" in linea for linea in r.desglose)


def test_explicar_recalcula_nuevos_resultados_sin_consumir_api(monkeypatch):
    from app.routers import explicar
    from app.services import rag
    from app.tools.parametros import cargar_parametros
    config = deepcopy(cargar_parametros())
    config["salario_basico_unificado"]["valor"] = 500
    from app.tools import liquidacion
    monkeypatch.setattr(liquidacion, "cargar_parametros", lambda: config)
    r = estimar_liquidacion(EntradaLiquidacion(**C09))
    assert Decimal(str(r.total)) == Decimal("1133.33")
    assert len(r.model_dump_json()) <= cargar_parametros()["limites"]["explicar_liquidacion_caracteres"]
    assert explicar.recalcular(r).total == r.total
    # Una cita de despido se agrega por motivo, sin truncarla al top-5.
    buscar = Mock(return_value=[])
    monkeypatch.setattr(rag.retriever, "buscar", buscar)
    rag.recuperar_calculo(estimar_liquidacion(EntradaLiquidacion(**C10)))
    assert "Art. 188" in buscar.call_args.args[0] and buscar.call_args.kwargs["k"] >= 6
