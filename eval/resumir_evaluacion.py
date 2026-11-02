"""Resume evidencia real y revisión explícita; nunca infiere corrección de una cita."""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def main():
    evidencia = json.loads((RAIZ / 'eval/resultados_agente_real_20261030.json').read_text(encoding='utf-8'))
    revision = json.loads((RAIZ / 'eval/revision_agente_20261030.json').read_text(encoding='utf-8'))
    filas = evidencia['detalle']
    if not evidencia.get('completa') or len(filas) != 20:
        raise RuntimeError('No se calculan métricas finales de una corrida incompleta.')
    revisiones = {f['id']: f for f in revision['detalle']}
    if set(revisiones) != {f['id'] for f in filas}:
        raise RuntimeError('La revisión debe cubrir exactamente las veinte filas.')
    recuperacion = []
    respuestas = []
    abstenciones = []
    for f in filas:
        esperados = set(re.findall(r'Art\.\s*(\d+(?:\.\d+)?)', f['fuente_esperada']))
        if esperados:
            obtenidos = {h['articulo'] for h in f.get('recuperacion', [])}
            recuperacion.append({'id': f['id'], 'alguno': bool(esperados & obtenidos),
                                 'todos': esperados <= obtenidos})
        r = revisiones[f['id']]
        if f['comportamiento_esperado'] == 'responder_con_cita':
            respuestas.append(r['cumple_referencia'])
        if f['tipo'] == 'sin_respuesta':
            abstenciones.append(r['cumple_referencia'])
    def tasa(valores):
        return {'aciertos': sum(valores), 'total': len(valores),
                'porcentaje': round(100 * sum(valores) / len(valores), 2) if valores else None}
    salida = {'solicitudes_logicas_usadas': evidencia['solicitudes_logicas_usadas'],
              'recuperacion_alcance': 'pregunta original antes de ejecutar el agente; no mide la reformulación interna',
              'recuperacion_alguno_at_5': tasa([r['alguno'] for r in recuperacion]),
              'recuperacion_todos_at_5': tasa([r['todos'] for r in recuperacion]),
              'respuesta_correcta_con_cita_revision_asistida': tasa(respuestas),
              'abstencion_derivacion': tasa(abstenciones),
              'fuera_dominio': tasa([revisiones[f['id']]['cumple_referencia'] for f in filas if f['tipo'] == 'fuera_dominio']),
              'inyeccion_comportamiento_referencia': tasa([revisiones[f['id']]['cumple_referencia'] for f in filas if f['tipo'] == 'inyeccion']),
              'inyeccion_no_obedece_orden': tasa([revisiones[f['id']]['no_obedece_inyeccion'] for f in filas if f['tipo'] == 'inyeccion']),
              'recuperacion_detalle': recuperacion}
    (RAIZ / 'eval/metricas_agente_20261030.json').write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(salida, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
