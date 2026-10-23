"""El backend sirve el frontend propio y sigue respondiendo la API."""
from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_raiz_sirve_el_frontend():
    r = cliente.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "Calculadora Laboral EC" in r.text
    assert "inteligencia artificial" in r.text.lower()  # aviso de IA visible


def test_archivos_del_frontend():
    assert cliente.get("/app.js").status_code == 200
    assert cliente.get("/styles.css").status_code == 200


def test_la_api_sigue_respondiendo():
    assert cliente.get("/health").json() == {"status": "ok"}
    assert cliente.get("/docs").status_code == 200


def test_el_frontend_no_contiene_claves():
    js = cliente.get("/app.js").text
    assert "API_KEY" not in js and "generativelanguage" not in js and "groq.com" not in js
