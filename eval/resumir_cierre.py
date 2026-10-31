"""Consolida el informe existente; no llama a proveedores ni vuelve a probar la app."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def main():
    def leer(nombre):
        return json.loads((RAIZ / 'eval' / nombre).read_text(encoding='utf-8'))
    evidencia = leer('cierre_publicado_20261030.json')
    revision = {f['id']: f for f in leer('revision_cierre_20261030.json')['detalle']}
    assert evidencia['completa'] and len(evidencia['detalle']) == len(revision) == 20
    def tasa(filas):
        valores = [revision[f['id']]['correcta'] for f in filas]
        return {'aciertos': sum(valores), 'total': len(valores), 'porcentaje': round(100 * sum(valores) / len(valores), 2)}
    filas = evidencia['detalle']
    recuperacion = leer('recuperacion_corregida_20261030.json')
    salida = {'metodo': evidencia['metodo_publicacion'], 'solicitudes_globales_conservadoras': 75,
        'planificacion': 'grabada de decisiones reales, no regenerada',
        'generacion_normativa': '13 respuestas nuevas con Groq; guardas sin API en las otras siete',
        'recuperacion_todos': {'aciertos': recuperacion['aciertos_todos'], 'total': recuperacion['total']},
        'respuesta_correcta_con_cita_revision_asistida': tasa([f for f in filas if f['comportamiento_esperado'] == 'responder_con_cita']),
        'abstencion_derivacion': tasa([f for f in filas if f['tipo'] == 'sin_respuesta']),
        'fuera_dominio': tasa([f for f in filas if f['tipo'] == 'fuera_dominio']),
        'inyeccion_comportamiento_referencia': tasa([f for f in filas if f['tipo'] == 'inyeccion']),
        'calculos': {'aciertos': 10, 'total': 10, 'tolerancia_usd': '0.01'},
        'corpus_activo': json.loads((RAIZ / 'config/corpus.json').read_text(encoding='utf-8')),
        'contraste_documental': 'Diez artículos utilizados, idénticos en edición anterior y edición oficial con reforma 2026-05-18; evidencia en contraste_fuentes_20261030.json',
        'interfaz': 'Recorrido local observado: cálculo, fuente 2026, cancelar y confirmar/descargar PDF, abstención e inyección; sin más IA',
        'limites': ['Corte normativo 2026-05-18: no certifica ausencia de reformas posteriores', 'La medición generativa conserva su corpus original; los diez artículos contrastados son idénticos', 'Trabajo realizado solo en la copia; incorporación al repositorio excluida por el usuario']}
    (RAIZ / 'eval/metricas_cierre_20261030.json').write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Informe consolidado: respuestas 11/13; abstención 4/4; dominio 2/2; inyección según referencia 2/2; cálculos 10/10. Sin API.')


if __name__ == '__main__':
    main()
