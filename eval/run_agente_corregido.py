"""Corrida corregida autorizada: máximo 32 Groq, desde 26 usadas hasta 58/60.

Las dos restantes se reservan para comprobar Gemini. No sobrescribe la línea base.
"""
import csv
import hashlib
import json
import sys
import time
from dataclasses import replace
from datetime import datetime, timezone
from run_agente_real import (RAIZ, ClienteEvaluacion, PresupuestoAgotado,
                             ConsultaAgente, cargar_config, ejecutar_agente)


def main():
    final = '--final' in sys.argv
    destino = RAIZ / ('eval/resultados_agente_final_20261030.json' if final else 'eval/resultados_agente_corregido_20261030.json')
    if destino.exists():
        raise RuntimeError('No repetir automáticamente ni sobrescribir evidencia.')
    diagnostico = json.loads((RAIZ / 'eval/diagnostico_P04_20261030.json').read_text(encoding='utf-8'))
    assert diagnostico['total_acumulado'] == 26
    previas, limite_groq = (33, 59) if final else (26, 58)
    config = replace(cargar_config(), respaldo=None)
    assert config.principal.nombre == 'groq'
    salida = {'inicio_utc': datetime.now(timezone.utc).isoformat(),
              'proveedor': 'groq', 'modelo': config.principal.modelo, 'respaldo': None,
              'solicitudes_previas': previas, 'maximo_adicional_groq': limite_groq - previas,
              'reserva_gemini': 1 if final else 2, 'limite_total': 60,
              'configuracion_ejecucion': {'timeout_s': config.timeout_s, 'reintentos': config.reintentos,
                  'max_tokens': config.max_tokens, 'razonamiento': config.razonamiento},
              'alcance': 'servicio real, pregunta original sin formularios añadidos; recuperación interna registrada',
              'detalle': []}
    archivos = [RAIZ / 'eval/preguntas.csv', RAIZ / 'config/parametros.yaml']
    archivos += sorted((RAIZ / 'app').rglob('*.py')) + sorted((RAIZ / 'app/prompts').glob('*.md'))
    salida['huellas_sha256'] = {str(p.relative_to(RAIZ)): hashlib.sha256(p.read_bytes()).hexdigest() for p in archivos}

    def guardar(cliente):
        salida['solicitudes_logicas_usadas'] = cliente.usadas - previas
        salida['total_acumulado'] = cliente.usadas
        destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')

    class ConTraza(ClienteEvaluacion):
        def _con_respaldo(self, mensajes, extra):
            if self.usadas >= limite_groq:
                raise PresupuestoAgotado()
            try:
                resultado = super()._con_respaldo(mensajes, extra)
                mensaje = resultado[1].choices[0].message
                traza = {'numero_global': self.usadas, 'contenido_propuesto': mensaje.content,
                         'herramientas_propuestas': [{'nombre': t.function.name, 'argumentos': t.function.arguments}
                             for t in (getattr(mensaje, 'tool_calls', None) or [])]}
                if 'response_format' in extra:
                    try:
                        contexto = json.loads(mensajes[1]['content'])
                        traza['pregunta_interna'] = contexto.get('pregunta')
                        traza['fuentes_internas'] = [{'id': f['id'], 'articulo': f['articulo']} for f in contexto.get('fragmentos', [])]
                        traza['resultado_herramienta_dias'] = contexto.get('resultado_herramienta_dias')
                    except (ValueError, KeyError):
                        pass
                self.trazas.append(traza)
                return resultado
            finally:
                guardar(self)

    cliente = ConTraza(config)
    cliente.usadas, cliente.trazas = previas, []
    guardar(cliente)
    with (RAIZ / 'eval/preguntas.csv').open(encoding='utf-8') as f:
        preguntas = list(csv.DictReader(f))
    for p in preguntas:
        fila, antes, inicio = dict(p), cliente.usadas, time.monotonic()
        cliente.trazas = []
        try:
            resultado = ejecutar_agente(ConsultaAgente(mensaje=p['pregunta']), cliente)
            fila['respuesta_real'] = resultado.model_dump(mode='json')
        except Exception as error:
            fila['error_tipo'] = type(error).__name__
        fila['trazas'] = cliente.trazas
        fila['solicitudes_logicas'] = cliente.usadas - antes
        fila['duracion_s'] = round(time.monotonic() - inicio, 2)
        salida['detalle'].append(fila)
        guardar(cliente)
        print(p['id'], fila.get('respuesta_real', {}).get('estado', fila.get('error_tipo')), 'total', cliente.usadas, '/60', flush=True)
    salida['completa'] = len(salida['detalle']) == 20
    salida['fin_utc'] = datetime.now(timezone.utc).isoformat()
    guardar(cliente)


if __name__ == '__main__':
    main()
