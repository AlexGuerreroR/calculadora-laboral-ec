"""Veinte preguntas, plan grabado idéntico y generación normativa NUEVA.

Máximo 13 Groq adicionales desde 62 consumidas/conservadoras: techo 75.
No repite el planificador ni usa respuestas normativas grabadas como respuestas nuevas.
"""
import csv
import hashlib
import json
import sys
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from app.config import cargar_config
from app.schemas import ConsultaAgente
from app.services.agente import ejecutar_agente
from app.services.llm import ClienteLLM, Resultado


def main():
    destino = RAIZ / 'eval/cierre_real_20261030.json'
    if destino.exists():
        raise RuntimeError('No sobrescribir ni repetir esta autorización.')
    anterior = json.loads((RAIZ / 'eval/resultados_agente_final_20261030.json').read_text(encoding='utf-8'))
    assert anterior['completa'] and anterior['solicitudes_logicas_usadas'] == 26
    cfg = replace(cargar_config(), respaldo=None)
    assert cfg.principal.nombre == 'groq'
    archivos = sorted((RAIZ / 'app').rglob('*.py')) + sorted((RAIZ / 'app/prompts').glob('*.md'))
    archivos += [RAIZ / 'config/parametros.yaml', RAIZ / 'eval/preguntas.csv']
    salida = {'inicio_utc': datetime.now(timezone.utc).isoformat(), 'proveedor': 'groq',
              'modelo': cfg.principal.modelo, 'respaldo': None, 'previas_conservadoras': 62,
              'maximo_adicional': 13, 'techo_autorizado': 75,
              'metodo': 'Selecciones de herramienta grabadas de la corrida real anterior; todas las respuestas normativas se generan de nuevo. Guardas y herramientas actuales, sin formularios inventados.',
              'huellas_sha256': {str(p.relative_to(RAIZ)): hashlib.sha256(p.read_bytes()).hexdigest() for p in archivos},
              'detalle': []}

    def guardar():
        salida['solicitudes_adicionales'] = real.usadas
        salida['total_global_conservador'] = 62 + real.usadas
        destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')

    class Acotado(ClienteLLM):
        usadas, ultimo_inicio = 0, 0.0
        def _con_respaldo(self, mensajes, extra):
            if self.usadas >= 13:
                raise RuntimeError('Presupuesto autorizado agotado')
            espera = max(0, 30 - (time.monotonic() - self.ultimo_inicio))
            if espera:
                time.sleep(espera)
            self.usadas += 1
            self.ultimo_inicio = time.monotonic()
            guardar()
            print('Solicitud global', 62 + self.usadas, '/75', flush=True)
            return super()._con_respaldo(mensajes, extra)

    class PlanRegistrado:
        def __init__(self, previa, fila):
            self.previa, self.fila = previa, fila
            self.plan_usado = False
        def generar_herramientas(self, mensajes, herramientas, requerir_herramienta=False):
            if self.plan_usado:
                raise RuntimeError('No hay más planificación grabada autorizada para esta pregunta')
            self.plan_usado = True
            # Mismos prompt de planificación, mensaje original y contratos.
            for nombre in ['app/prompts/agente_v4.md', 'eval/preguntas.csv']:
                clave = next(k for k in anterior['huellas_sha256'] if k.replace('\\', '/') == nombre)
                assert hashlib.sha256((RAIZ / nombre).read_bytes()).hexdigest() == anterior['huellas_sha256'][clave]
            traza = self.previa['trazas'][0]
            propuestas = traza['herramientas_propuestas']
            assert len(propuestas) == 1 and propuestas[0]['nombre'] == 'consultar_normativa'
            mensaje = {'role': 'assistant', 'content': traza['contenido_propuesto'],
                       'tool_calls': [{'id': 'plan-real-grabado', 'type': 'function', 'function': {
                           'name': p['nombre'], 'arguments': p['argumentos']}} for p in propuestas]}
            self.fila['planificacion'] = 'selección real grabada; sin consumo adicional'
            return Resultado(mensaje, 'grabado-groq', anterior['modelo'], None, None, 0, 0)
        def generar_json(self, system, usuario, esquema):
            contexto = json.loads(usuario)
            self.fila['fuentes_internas'] = contexto.get('fragmentos', [])
            self.fila['resultado_herramienta_dias'] = contexto.get('resultado_herramienta_dias')
            self.fila['resultado_herramienta_jornada'] = contexto.get('resultado_herramienta_jornada')
            r = real.generar_json(system, usuario, esquema)
            self.fila['json_nuevo_modelo'] = r.datos.model_dump(mode='json')
            return r

    real = Acotado(cfg)
    guardar()
    por_id = {f['id']: f for f in anterior['detalle']}
    with (RAIZ / 'eval/preguntas.csv').open(encoding='utf-8') as f:
        preguntas = list(csv.DictReader(f))
    for pregunta in preguntas:
        fila, antes, inicio = dict(pregunta), real.usadas, time.monotonic()
        salida['detalle'].append(fila)
        try:
            resultado = ejecutar_agente(ConsultaAgente(mensaje=pregunta['pregunta']), PlanRegistrado(por_id[pregunta['id']], fila))
            fila['respuesta_real'] = resultado.model_dump(mode='json')
        except Exception as error:
            fila['error_tipo'] = type(error).__name__
        fila['solicitudes_nuevas'] = real.usadas - antes
        fila['duracion_s'] = round(time.monotonic() - inicio, 2)
        guardar()
        print(pregunta['id'], fila.get('respuesta_real', {}).get('estado', fila.get('error_tipo')), flush=True)
    salida['completa'] = len(salida['detalle']) == 20
    salida['fin_utc'] = datetime.now(timezone.utc).isoformat()
    guardar()


if __name__ == '__main__':
    main()
