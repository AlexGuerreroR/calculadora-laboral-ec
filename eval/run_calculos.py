"""Reproduce los casos congelados del Excel por HTTP local, sin proveedor de IA."""
import csv
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from fastapi.testclient import TestClient
from app.main import app
from app.services.retriever import validar_ruta_copia


def main():
    destino = validar_ruta_copia(RAIZ / 'eval/resultados_calculos_20261030.json')
    with (RAIZ / 'eval/casos_calculo.csv').open(encoding='utf-8', newline='') as f:
        casos = list(csv.DictReader(f))
    filas = []
    with TestClient(app) as cliente:
        for caso in casos:
            respuesta = cliente.post(caso['ruta'], json=json.loads(caso['entrada_json']))
            datos = respuesta.json()
            diferencia = (abs(Decimal(str(datos['total'])) - Decimal(caso['total_esperado']))
                          if respuesta.status_code == 200 else None)
            filas.append({'id': caso['id'], 'http': respuesta.status_code,
                          'esperado': caso['total_esperado'], 'resultado': datos,
                          'diferencia': str(diferencia) if diferencia is not None else None,
                          'correcto': diferencia is not None and diferencia <= Decimal('0.01')})
    salida = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'usa_api': False,
              'referencia': 'B4_Resolución de casos.xlsx, Resultados C4:C13; supuestos C09/C10 conservados',
              'tolerancia_usd': '0.01', 'aciertos': sum(f['correcto'] for f in filas),
              'total': len(filas), 'detalle': filas}
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Cálculos: {salida['aciertos']}/{len(filas)}; sin API", flush=True)


if __name__ == '__main__':
    main()
