"""Verifica la recuperación usada por el agente corregido, sin proveedor generativo."""
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from app.services.agente import recuperar_normativa, consulta_sin_ordenes_citadas
from app.services.retriever import cargar_entorno, validar_ruta_copia


def main():
    cargar_entorno()
    destino = validar_ruta_copia(RAIZ / 'eval/recuperacion_corregida_20261030.json')
    with (RAIZ / 'eval/preguntas.csv').open(encoding='utf-8') as f:
        preguntas = list(csv.DictReader(f))
    filas = []
    for p in preguntas:
        pregunta = consulta_sin_ordenes_citadas(p['pregunta'])
        fuentes = recuperar_normativa(pregunta)
        esperados = set(re.findall(r'Art\.\s*(\d+(?:\.\d+)?)', p['fuente_esperada']))
        recuperados = {h['articulo'] for h in fuentes}
        fila = {'id': p['id'], 'esperados': sorted(esperados),
                'recuperados': [h['articulo'] for h in fuentes],
                'todos': esperados <= recuperados if esperados else None}
        filas.append(fila)
        print(p['id'], fila['recuperados'], fila['todos'], flush=True)
    evaluables = [f for f in filas if f['todos'] is not None]
    salida = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'usa_api': False,
              'alcance': 'recuperacion con ayudas por tema, sin medir respuesta generativa',
              'aciertos_todos': sum(f['todos'] for f in evaluables), 'total': len(evaluables),
              'detalle': filas}
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
