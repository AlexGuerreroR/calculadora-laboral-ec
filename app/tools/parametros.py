"""Lee config/parametros.yaml una sola vez.

Regla del caso 07: los parámetros variables (salario básico, divisores, días)
viven en configuración, nunca escritos en el código ni en el prompt.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from pathlib import Path

import yaml

RUTA = Path(__file__).resolve().parents[2] / "config" / "parametros.yaml"


@lru_cache
def cargar_parametros() -> dict:
    with open(RUTA, encoding="utf-8") as f:
        return yaml.safe_load(f)


def dec(valor) -> Decimal:
    """Convierte a Decimal sin errores de coma flotante (0.1 + 0.2 != 0.3 en float)."""
    return Decimal(str(valor))


def redondear(valor: Decimal) -> Decimal:
    """Redondeo a centavos, mitad hacia arriba, como en el cálculo manual."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
