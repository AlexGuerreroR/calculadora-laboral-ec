"""Hasta tres solicitudes adicionales autorizadas; detiene al primer respaldo válido."""
import json
import re
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import httpx
import openai
from app.config import cargar_config
from app.schemas import TextoNormativo
from app.services.llm import ClienteLLM


def main():
    destino = RAIZ / 'eval/gemini_modelos_probados_20261030.json'
    if destino.exists():
        raise RuntimeError('No repetir automáticamente esta autorización.')
    cfg = cargar_config()
    assert cfg.principal.nombre == 'groq' and cfg.respaldo.nombre == 'gemini'
    salida = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'limite_adicional': 3,
              'techo_global_autorizado': 64, 'usadas': 0, 'detalle': [],
              'metodo': 'fallo Groq simulado sin red; Gemini real con configuración de la aplicación'}

    def guardar():
        destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')

    class Acotado(ClienteLLM):
        def _con_respaldo(self, mensajes, extra):
            if salida['usadas'] >= 3:
                raise RuntimeError('Presupuesto global de esta prueba agotado')
            salida['usadas'] += 1
            guardar()
            return super()._con_respaldo(mensajes, extra)

    def falla_principal(**kwargs):
        raise openai.APIConnectionError(request=httpx.Request('POST', 'https://principal-simulado.invalid/'))

    for modelo in ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-2.5-flash-lite']:
        if salida['usadas'] >= 3:
            break
        fila = {'modelo': modelo, 'correcto': False}
        candidato = replace(cfg, respaldo=replace(cfg.respaldo, modelo=modelo))
        cliente = Acotado(candidato, dormir=lambda s: None)
        cliente._clientes[cfg.principal.nombre] = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=falla_principal)))
        try:
            r = cliente.generar_json('Devuelva únicamente el JSON del esquema.',
                'Prueba técnica: estado no_disponible, respuesta vacía y citas vacías. Sin datos personales.', TextoNormativo)
            fila['correcto'] = r.proveedor == 'gemini' and r.datos.estado == 'no_disponible' and not r.datos.respuesta and not r.datos.citas
            fila['proveedor_efectivo'] = r.proveedor
            fila['resultado'] = r.datos.model_dump()
            fila['latencia_ms'] = r.latencia_ms
        except Exception as error:
            fila['error_tipo'] = type(error).__name__
        salida['detalle'].append(fila)
        guardar()
        print(modelo, 'correcto' if fila['correcto'] else fila.get('error_tipo', 'salida no válida'), flush=True)
        if fila['correcto']:
            salida['modelo_elegido'] = modelo
            env = RAIZ / '.env'
            contenido, n = re.subn(r'(?m)^GEMINI_MODEL\s*=.*$', 'GEMINI_MODEL=' + modelo, env.read_text(encoding='utf-8'))
            assert n == 1
            env.write_text(contenido, encoding='utf-8')
            salida['configuracion_local_actualizada'] = True
            guardar()
            break
    print('Solicitudes adicionales usadas:', salida['usadas'], '/3', flush=True)


if __name__ == '__main__':
    main()
