"""Exactitud de herramientas (guía, conjunto de evaluación): los 10 casos de referencia revisados
por el contador (docs/evidencias/semana-1/B4_Resolución de casos.xlsx) deben coincidir al 100 %
con ±0,01 USD. Se ejecutan con las MISMAS herramientas que usa el agente, sin modelo.
"""
import csv
import json
from pathlib import Path

import pytest

from app.services.agent import HERRAMIENTAS

CASOS = list(csv.DictReader(open(Path(__file__).resolve().parent.parent / "eval/casos_calculo.csv",
                                 encoding="utf-8")))


def test_son_los_diez_casos_de_referencia():
    assert [c["id"] for c in CASOS] == [f"C{i:02d}" for i in range(1, 11)]


@pytest.mark.parametrize("caso", CASOS, ids=[c["id"] for c in CASOS])
def test_caso_de_referencia(caso):
    h = HERRAMIENTAS[caso["herramienta"]]
    r = h.funcion(h.esquema.model_validate(json.loads(caso["entradas"])), None)
    assert r["total"] == pytest.approx(float(caso["total_esperado"]), abs=0.01)
    if caso["dias_esperados"]:
        assert r["dias"] == pytest.approx(float(caso["dias_esperados"]))
