from copy import deepcopy
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import EntradaHoras
from app.tools.horas import calcular_horas
from app.tools import parametros


def test_c08_redondea_rubros_sin_redondear_la_hora():
    resultado = calcular_horas(EntradaHoras(remuneracion_mensual=800, horas_suplementarias=10, horas_extraordinarias=4))
    assert Decimal(str(resultado.total)) == Decimal("76.67")
    assert any("50.00" in s for s in resultado.desglose)
    assert any("26.67" in s for s in resultado.desglose)


def test_horas_fraccionarias():
    r = calcular_horas(EntradaHoras(remuneracion_mensual=800, horas_suplementarias="1.5", horas_extraordinarias="0.25"))
    assert Decimal(str(r.total)) == Decimal("9.17")


@pytest.mark.parametrize("cambios", [
    {"remuneracion_mensual": -1}, {"horas_suplementarias": -1},
    {"horas_extraordinarias": "NaN"}, {"horas_suplementarias": 0, "horas_extraordinarias": 0},
])
def test_rechaza_horas_invalidas(cambios):
    with pytest.raises(ValidationError):
        EntradaHoras(**({"remuneracion_mensual": 800, "horas_suplementarias": 10, "horas_extraordinarias": 4} | cambios))


def test_recargo_se_lee_de_configuracion(monkeypatch):
    from app.tools import horas
    config = deepcopy(parametros.cargar_parametros())
    config["horas"]["recargo_suplementaria"] = 1
    monkeypatch.setattr(horas, "cargar_parametros", lambda: config)
    r = calcular_horas(EntradaHoras(remuneracion_mensual=800, horas_suplementarias=10, horas_extraordinarias=0))
    assert Decimal(str(r.total)) == Decimal("66.67")
