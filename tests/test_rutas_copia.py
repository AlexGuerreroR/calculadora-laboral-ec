"""Aislamiento de rutas, sin Chroma, modelos, .env real ni servicios externos.

Las carpetas temporales solo se crearán cuando se autorice ejecutar pytest.
"""
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services import retriever

RAIZ_CODIGO = Path(__file__).resolve().parents[1]


@pytest.fixture
def copia(tmp_path, monkeypatch):
    raiz = tmp_path / "copia"
    raiz.mkdir()
    monkeypatch.setattr(retriever, "_RAIZ", raiz)
    monkeypatch.delenv("CHROMA_PATH", raising=False)
    return raiz.resolve()


@pytest.mark.parametrize("valor", ["", "./data/chroma", "data/otro/../chroma"])
def test_indice_relativo_permanece_en_copia(copia, monkeypatch, valor):
    monkeypatch.setenv("CHROMA_PATH", valor)
    assert retriever.ruta_indice() == copia / "data/chroma"
    assert not (copia / "data").exists()  # validar no crea el índice


def test_ruta_absoluta_interna_y_directorio_actual(copia, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CHROMA_PATH", str(copia / "data/indice"))
    assert retriever.ruta_indice() == copia / "data/indice"
    monkeypatch.setenv("CHROMA_PATH", "data/indice")
    assert retriever.ruta_indice() == copia / "data/indice"


@pytest.mark.parametrize("valor", ["../original/chroma", ".", "data/../.."])
def test_rechaza_escape_relativo_y_raiz(copia, monkeypatch, valor):
    monkeypatch.setenv("CHROMA_PATH", valor)
    with pytest.raises(ValueError, match="dentro de la copia"):
        retriever.ruta_indice()


def test_rechaza_absoluta_externa_y_prefijo_parecido(copia, monkeypatch):
    for externa in (copia.parent / "original/chroma", copia.parent / "copia_otro/chroma"):
        monkeypatch.setenv("CHROMA_PATH", str(externa))
        with pytest.raises(ValueError, match="dentro de la copia"):
            retriever.ruta_indice()


@pytest.mark.skipif(sys.platform != "win32", reason="Rutas propias de Windows")
@pytest.mark.parametrize("valor", ["C:indice", "\\indice"])
def test_rechaza_rutas_windows_ambiguas(copia, monkeypatch, valor):
    monkeypatch.setenv("CHROMA_PATH", valor)
    with pytest.raises(ValueError, match="relativa a la copia"):
        retriever.ruta_indice()


def test_rechaza_enlace_resuelto_fuera_sin_crear_enlaces(copia, monkeypatch):
    ruta_enlace = copia / "data/enlace"
    resolver = Path.resolve

    def resolver_simulado(ruta, *args, **kwargs):
        if ruta == ruta_enlace:
            return copia.parent / "original/chroma"
        return resolver(ruta, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolver_simulado)
    with pytest.raises(ValueError, match="dentro de la copia"):
        retriever.validar_ruta_copia(ruta_enlace)


def test_ruta_invalida_no_abre_chroma(copia, monkeypatch):
    cliente = Mock()
    monkeypatch.setitem(sys.modules, "chromadb", SimpleNamespace(PersistentClient=cliente))
    monkeypatch.setenv("CHROMA_PATH", "../original/chroma")
    with pytest.raises(ValueError):
        retriever._cliente()
    cliente.assert_not_called()


@pytest.mark.parametrize("script", ["scripts/ingest.py", "eval/run_eval.py"])
def test_scripts_rechazan_indice_externo_antes_de_efectos(copia, monkeypatch, script):
    # Importar el script con carga de entorno anulada: nunca leer el .env real.
    monkeypatch.setattr(retriever, "cargar_entorno", Mock())
    monkeypatch.setattr(sys, "path", list(sys.path))
    spec = importlib.util.spec_from_file_location("script_aislamiento", RAIZ_CODIGO / script)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    monkeypatch.setenv("CHROMA_PATH", "../original/chroma")
    buscar = Mock(side_effect=AssertionError("No debe consultar el índice"))
    monkeypatch.setattr(retriever, "buscar", buscar)
    if script == "scripts/ingest.py":
        descargar = Mock(side_effect=AssertionError("No debe descargar"))
        monkeypatch.setattr(modulo.urllib.request, "urlretrieve", descargar)
        monkeypatch.setattr(modulo, "leer_pdf", Mock(side_effect=AssertionError("No debe leer PDF")))
    with pytest.raises(ValueError, match="dentro de la copia"):
        modulo.main()
    buscar.assert_not_called()
    if script == "scripts/ingest.py":
        descargar.assert_not_called()
    assert list(copia.iterdir()) == []
