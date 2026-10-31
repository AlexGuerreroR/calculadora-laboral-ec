"""Comprueba Gemini real tras fallo simulado del principal, máximo dos llamadas.

No provoca una caída de Groq ni modifica .env. No repite una evidencia existente.
"""
import json
import sys
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
    extra_autorizado = '--extra-autorizado' in sys.argv
    ultimo = '--ultimo' in sys.argv or extra_autorizado
    nombre = ('eval/respaldo_real_extra_20261030.json' if extra_autorizado else
              'eval/respaldo_real_final_20261030.json' if ultimo else 'eval/respaldo_real_20261030.json')
    destino = RAIZ / nombre
    if destino.exists():
        raise RuntimeError('No repetir ni sobrescribir la prueba de respaldo.')
    cfg = cargar_config()
    assert cfg.principal.nombre == 'groq' and cfg.respaldo.nombre == 'gemini'
    if ultimo:
        assert json.loads((RAIZ / 'eval/respaldo_real_20261030.json').read_text(encoding='utf-8'))['solicitudes_logicas_usadas'] == 1
    maximo = 1 if ultimo else 2
    salida = {'fecha_utc': datetime.now(timezone.utc).isoformat(),
              'principal_configurado': cfg.principal.nombre, 'respaldo_real': cfg.respaldo.nombre,
              'modelo_respaldo': cfg.respaldo.modelo, 'fallo_principal': 'simulado, sin llamada real a Groq',
              'maximo_logico_reservado': maximo, 'solicitudes_logicas_usadas': 0,
              'timeout_respaldo_s': cfg.timeout_respaldo_s,
              'techo_global_autorizado': 61 if extra_autorizado else 60,
              'reintentos_configurados_por_proveedor': cfg.reintentos}

    class Acotado(ClienteLLM):
        def _con_respaldo(self, mensajes, extra):
            if salida['solicitudes_logicas_usadas'] >= maximo:
                raise RuntimeError('Presupuesto agotado')
            salida['solicitudes_logicas_usadas'] += 1
            destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')
            return super()._con_respaldo(mensajes, extra)

    def falla_principal(**kwargs):
        raise openai.APIConnectionError(request=httpx.Request('POST', 'https://principal-simulado.invalid/'))

    cliente = Acotado(cfg, dormir=lambda s: None)
    cliente._clientes[cfg.principal.nombre] = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=falla_principal)))
    try:
        resultado = cliente.generar_json('Devuelva únicamente el JSON del esquema solicitado.',
            'Devuelva estado no_disponible, respuesta vacía y citas vacías. Es una prueba técnica sin datos personales.', TextoNormativo)
        salida['correcto'] = (resultado.proveedor == 'gemini' and resultado.datos.estado == 'no_disponible'
                             and not resultado.datos.respuesta and not resultado.datos.citas)
        salida['proveedor_efectivo'] = resultado.proveedor
        salida['resultado'] = resultado.datos.model_dump()
    except Exception as error:
        salida['correcto'] = False
        salida['error_tipo'] = type(error).__name__
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(salida, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
