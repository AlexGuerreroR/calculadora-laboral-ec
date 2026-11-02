"""Corrida autorizada: 20 preguntas originales, Groq exclusivo, máximo 60 llamadas.

Ejecutar desde la raíz de la copia. Guarda cada fila antes de continuar.
No usa formularios inventados, no modifica el dataset ni califica semántica por citas.
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
from app.services import retriever
from app.services.agente import ejecutar_agente
from app.services.llm import ClienteLLM


class PresupuestoAgotado(RuntimeError):
    pass


class ClienteEvaluacion(ClienteLLM):
    usadas = 0
    ultimo_inicio = 0.0

    def _con_respaldo(self, mensajes, extra):
        if self.usadas >= 60:
            raise PresupuestoAgotado()
        # Separación global: también cuenta correcciones JSON. Los reintentos
        # internos mantienen la configuración autorizada del proveedor.
        espera = max(0, 30 - (time.monotonic() - self.ultimo_inicio))
        if espera:
            time.sleep(espera)
        self.usadas += 1
        self.ultimo_inicio = time.monotonic()
        print(f"Solicitud lógica {self.usadas}/60", flush=True)
        return super()._con_respaldo(mensajes, extra)


def main():
    retriever.ruta_indice()
    destino = retriever.validar_ruta_copia(RAIZ / 'eval/resultados_agente_real_20261030.json')
    if destino.exists():
        raise RuntimeError('La evidencia ya existe; no se sobrescribe ni se repite la corrida.')
    config = replace(cargar_config(), respaldo=None)
    if config.principal.nombre != 'groq':
        raise RuntimeError('Esta autorización es exclusivamente para Groq.')
    cliente = ClienteEvaluacion(config)
    archivos = [RAIZ / 'eval/preguntas.csv', RAIZ / 'config/parametros.yaml']
    archivos += sorted((RAIZ / 'app').rglob('*.py'))
    archivos += sorted((RAIZ / 'app/prompts').glob('*.md'))
    salida = {'inicio_utc': datetime.now(timezone.utc).isoformat(),
              'proveedor': 'groq', 'modelo': config.principal.modelo,
              'respaldo': None, 'limite_logico': 60,
              'unidad': 'invocación _con_respaldo, incluidas correcciones JSON; reintentos HTTP aparte',
              'alcance': 'servicio real ejecutar_agente, sin HTTP ni datos de formularios añadidos',
              'huellas_sha256': {str(p.relative_to(RAIZ)): hashlib.sha256(p.read_bytes()).hexdigest() for p in archivos},
              'detalle': []}
    def guardar():
        salida['solicitudes_logicas_usadas'] = cliente.usadas
        destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')
    guardar()
    with (RAIZ / 'eval/preguntas.csv').open(encoding='utf-8') as f:
        preguntas = list(csv.DictReader(f))
    for pregunta in preguntas:
        fila = dict(pregunta)
        inicio = time.monotonic()
        antes = cliente.usadas
        try:
            hits = retriever.buscar(pregunta['pregunta'], k=5)
            fila['recuperacion'] = [{'id': h['id'], 'articulo': h['articulo']} for h in hits]
            resultado = ejecutar_agente(ConsultaAgente(mensaje=pregunta['pregunta']), cliente)
            fila['respuesta_real'] = resultado.model_dump(mode='json')
            fila['revision_semantica'] = None
        except Exception as error:
            # No guardar mensajes de excepción que puedan contener datos secretos.
            fila['error_tipo'] = type(error).__name__
        fila['solicitudes_logicas'] = cliente.usadas - antes
        fila['duracion_s'] = round(time.monotonic() - inicio, 2)
        salida['detalle'].append(fila)
        guardar()
        estado = fila.get('respuesta_real', {}).get('estado', fila.get('error_tipo'))
        print(f"{pregunta['id']}: {estado}; total {cliente.usadas}/60", flush=True)
        if cliente.usadas >= 60:
            break
    salida['fin_utc'] = datetime.now(timezone.utc).isoformat()
    salida['completa'] = len(salida['detalle']) == len(preguntas)
    guardar()


if __name__ == '__main__':
    main()
