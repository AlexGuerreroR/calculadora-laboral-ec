"""Diagnóstico P04: máximo tres llamadas adicionales dentro del mismo límite de 60.

Solo después de la corrida completa. No cambia ni reemplaza sus resultados.
Guarda respuesta propuesta y consulta interna para distinguir generación de validación.
"""
import csv
import json
from dataclasses import replace
from run_agente_real import (RAIZ, ClienteEvaluacion, PresupuestoAgotado,
                             ConsultaAgente, cargar_config, ejecutar_agente)


def main():
    base = json.loads((RAIZ / 'eval/resultados_agente_real_20261030.json').read_text(encoding='utf-8'))
    if not base.get('completa'):
        raise RuntimeError('Primero debe terminar la corrida principal.')
    destino = RAIZ / 'eval/diagnostico_P04_20261030.json'
    if destino.exists():
        raise RuntimeError('No repetir el diagnóstico ni sobrescribir su evidencia.')
    previas = base['solicitudes_logicas_usadas']
    if previas + 3 > 60:
        raise RuntimeError('No hay margen dentro del presupuesto autorizado.')
    salida = {'pregunta_id': 'P04', 'previas': previas, 'maximo_adicional': 3,
              'limite_total_autorizado': 60, 'trazas': []}

    def guardar(cliente):
        salida['total_acumulado'] = cliente.usadas
        destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')

    class Traza(ClienteEvaluacion):
        def _con_respaldo(self, mensajes, extra):
            if self.usadas - previas >= 3:
                raise PresupuestoAgotado()
            resultado = super()._con_respaldo(mensajes, extra)
            mensaje = resultado[1].choices[0].message
            llamadas = getattr(mensaje, 'tool_calls', None) or []
            salida['trazas'].append({'numero_global': self.usadas,
                'entrada_ultimo_mensaje': mensajes[-1],
                'contenido_propuesto': mensaje.content,
                'herramientas_propuestas': [{'nombre': t.function.name, 'argumentos': t.function.arguments} for t in llamadas]})
            guardar(self)
            return resultado

    config = replace(cargar_config(), respaldo=None)
    if config.principal.nombre != 'groq':
        raise RuntimeError('Proveedor no autorizado para esta evaluación.')
    cliente = Traza(config)
    cliente.usadas = previas
    guardar(cliente)
    with (RAIZ / 'eval/preguntas.csv').open(encoding='utf-8') as f:
        pregunta = next(p for p in csv.DictReader(f) if p['id'] == 'P04')
    try:
        r = ejecutar_agente(ConsultaAgente(mensaje=pregunta['pregunta']), cliente)
        salida['respuesta_real'] = r.model_dump(mode='json')
    except Exception as error:
        salida['error_tipo'] = type(error).__name__
    guardar(cliente)
    print('Diagnóstico P04 guardado; total acumulado:', cliente.usadas, '/60', flush=True)


if __name__ == '__main__':
    main()
