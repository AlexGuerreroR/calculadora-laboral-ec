"""Los scripts de ingesta y evaluación deben respetar EMBEDDING_MODEL y CHROMA_PATH del .env.

Observación de la revisión del PR #61: no pasan por app/config.py, así que deben cargar el .env
ellos mismos. Si no, se indexa con un modelo y el servidor busca con otro.
"""
import importlib.util
from pathlib import Path

import pytest

from app.services import retriever

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def env_de_prueba(tmp_path, monkeypatch):
    for nombre in ("EMBEDDING_MODEL", "CHROMA_PATH"):
        monkeypatch.setenv(nombre, "x")   # registra el valor original para restaurarlo al final
        monkeypatch.delenv(nombre)
    indice = tmp_path / "indice"
    (tmp_path / ".env").write_text(f"EMBEDDING_MODEL=modelo-de-prueba\nCHROMA_PATH={indice}\n", encoding="utf-8")
    monkeypatch.setattr(retriever, "_RAIZ", tmp_path)  # el .env que se lee es el de prueba
    return indice


def test_cargar_entorno_lee_el_env(env_de_prueba):
    retriever.cargar_entorno()
    assert retriever.modelo_embeddings() == "modelo-de-prueba"
    assert retriever.ruta_indice() == env_de_prueba


@pytest.mark.parametrize("script", ["scripts/ingest.py", "eval/run_eval.py"])
def test_los_scripts_cargan_el_env_al_importarse(script, env_de_prueba):
    spec = importlib.util.spec_from_file_location("script_bajo_prueba", RAIZ / script)
    spec.loader.exec_module(importlib.util.module_from_spec(spec))  # no ejecuta main()
    assert retriever.modelo_embeddings() == "modelo-de-prueba"
    assert retriever.ruta_indice() == env_de_prueba


def test_la_terminal_tiene_prioridad_sobre_el_env(env_de_prueba, monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODEL", "modelo-de-la-terminal")
    retriever.cargar_entorno()
    assert retriever.modelo_embeddings() == "modelo-de-la-terminal"
