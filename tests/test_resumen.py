"""PDF y confirmación: datos ficticios, fuente y agente simulados; sin API."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from unittest.mock import Mock

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import resumen as ruta, agente as ruta_agente
from app.schemas import EntradaDecimoTercero, EntradaLiquidacion
from app.services import resumen
from app.tools import resumen as herramienta
from app.tools.decimos import calcular_decimo_tercero
from app.tools.liquidacion import estimar_liquidacion
from test_agente import ModeloFalso, llamada, turno, FUENTE
from test_liquidacion import C09, C10

CALCULO = calcular_decimo_tercero(EntradaDecimoTercero(remuneraciones=[600] * 12))


@pytest.fixture(autouse=True)
def entorno_pdf(monkeypatch):
    ahora = [100.0]
    monkeypatch.setattr(resumen, "almacen", resumen.AlmacenResumen(reloj=lambda: ahora[0]))
    monkeypatch.setattr(ruta, "limitador", ruta.LimitadorPorMinuto(100))
    monkeypatch.setattr(ruta_agente, "limitador", ruta_agente.LimitadorPorMinuto(100))
    monkeypatch.setattr(ruta.rag, "recuperar_calculo", lambda calculo: [FUENTE])
    yield ahora
    app.dependency_overrides.clear()


def preparar(cliente, calculo=CALCULO):
    r = cliente.post("/resumen/preparar", json={"calculo": calculo.model_dump(mode="json")})
    assert r.status_code == 200, r.text
    return r.json()


def test_preparar_no_genera_pdf_y_solo_guarda_datos_del_servidor(monkeypatch):
    generar = Mock(side_effect=AssertionError("No generar antes de confirmar"))
    monkeypatch.setattr(herramienta, "generar_resumen", generar)
    cliente = TestClient(app)
    datos = CALCULO.model_dump(mode="json") | {"desglose": ["Texto falso"], "fundamento": "Ley inventada"}
    r = cliente.post("/resumen/preparar", json={"calculo": datos})
    assert r.status_code == 200 and len(r.json()["token"]) >= 32
    assert "Texto falso" not in r.text and "Ley inventada" not in r.text
    assert "HttpOnly" in r.headers["set-cookie"] and "SameSite=strict" in r.headers["set-cookie"]
    assert r.headers["cache-control"] == "no-store"
    generar.assert_not_called()


@pytest.mark.parametrize("confirmacion", [None, False, 1, "true"])
def test_sin_confirmacion_booleana_explicita_no_hay_pdf(monkeypatch, confirmacion):
    generar = Mock()
    monkeypatch.setattr(herramienta, "generar_resumen", generar)
    cliente = TestClient(app)
    vista = preparar(cliente)
    cuerpo = {"token": vista["token"]}
    if confirmacion is not None:
        cuerpo["confirmar"] = confirmacion
    assert cliente.post("/resumen/confirmar", json=cuerpo).status_code == 422
    generar.assert_not_called()


def test_confirmar_una_sola_vez_y_no_aceptar_sustituir_datos(monkeypatch):
    generar = Mock(return_value=b"%PDF-simulado")
    monkeypatch.setattr(herramienta, "generar_resumen", generar)
    cliente = TestClient(app)
    vista = preparar(cliente)
    cuerpo = {"token": vista["token"], "confirmar": True}
    assert cliente.post("/resumen/confirmar", json=cuerpo | {"calculo": {"total": 999}}).status_code == 422
    r = cliente.post("/resumen/confirmar", json=cuerpo)
    assert r.status_code == 200 and r.headers["content-type"] == "application/pdf"
    assert "attachment" in r.headers["content-disposition"]
    assert generar.call_args.args[0].calculo.total == 600
    assert cliente.post("/resumen/confirmar", json=cuerpo).status_code == 404
    assert generar.call_count == 1


def test_token_no_funciona_en_otro_navegador_ni_sin_sesion(monkeypatch):
    generar = Mock(return_value=b"%PDF-simulado")
    monkeypatch.setattr(herramienta, "generar_resumen", generar)
    propio, otro = TestClient(app), TestClient(app)
    vista = preparar(propio)
    cuerpo = {"token": vista["token"], "confirmar": True}
    assert otro.post("/resumen/confirmar", json=cuerpo).status_code == 404
    assert propio.post("/resumen/confirmar", json=cuerpo).status_code == 200
    assert generar.call_count == 1


def test_cancelar_o_vencer_no_genera_pdf(monkeypatch, entorno_pdf):
    generar = Mock()
    monkeypatch.setattr(herramienta, "generar_resumen", generar)
    cliente = TestClient(app)
    vista = preparar(cliente)
    assert cliente.post("/resumen/cancelar", json={"token": vista["token"]}).status_code == 204
    assert cliente.post("/resumen/confirmar", json={"token": vista["token"], "confirmar": True}).status_code == 404
    vista = preparar(cliente)
    entorno_pdf[0] += 301
    assert cliente.post("/resumen/confirmar", json={"token": vista["token"], "confirmar": True}).status_code == 404
    generar.assert_not_called()


def test_consumo_atomico_ante_dos_confirmaciones():
    almacen = resumen.AlmacenResumen()
    vista = almacen.preparar(CALCULO, [], "propietario")
    def consumir():
        try:
            almacen.consumir(vista.token, "propietario")
            return True
        except resumen.SolicitudNoDisponible:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(lambda _: consumir(), range(2))) == 1


def test_limite_de_pendientes_por_sesion(monkeypatch):
    cfg = deepcopy(resumen.cargar_parametros())
    cfg["resumen"]["max_pendientes_por_sesion"] = 1
    monkeypatch.setattr(resumen, "cargar_parametros", lambda: cfg)
    cliente = TestClient(app)
    preparar(cliente)
    assert cliente.post("/resumen/preparar", json={"calculo": CALCULO.model_dump(mode="json")}).status_code == 429


@pytest.mark.parametrize("calculo,total", [(CALCULO, "USD 600,00"),
    (estimar_liquidacion(EntradaLiquidacion(**C09)), "USD 1.130,33"),
    (estimar_liquidacion(EntradaLiquidacion(**C10)), "USD 9.331,84")])
def test_pdf_real_tiene_total_fuentes_y_limites(calculo, total):
    cliente = TestClient(app)
    vista = preparar(cliente, calculo)
    r = cliente.post("/resumen/confirmar", json={"token": vista["token"], "confirmar": True})
    assert r.status_code == 200 and r.content.startswith(b"%PDF-")
    with pymupdf.open(stream=r.content, filetype="pdf") as documento:
        texto = " ".join(p.get_text() for p in documento)
        assert total in texto and "Art. 111" in texto
        assert "No es un acta de finiquito" in texto
        assert "2023" in texto and "2026" in texto
        assert 1 <= len(documento) <= 4
    assert vista["token"] not in texto


def test_snapshot_no_cambia_si_se_modifica_la_configuracion(monkeypatch):
    from app.tools import decimos
    from app.schemas import EntradaDecimoCuarto
    calculo = decimos.calcular_decimo_cuarto(EntradaDecimoCuarto(meses_trabajados=12, region="sierra_amazonia"))
    cliente = TestClient(app)
    vista = preparar(cliente, calculo)
    cfg = deepcopy(decimos.cargar_parametros())
    cfg["salario_basico_unificado"]["valor"] = 999
    monkeypatch.setattr(decimos, "cargar_parametros", lambda: cfg)
    r = cliente.post("/resumen/confirmar", json={"token": vista["token"], "confirmar": True})
    with pymupdf.open(stream=r.content, filetype="pdf") as documento:
        texto = " ".join(p.get_text() for p in documento)
    assert "USD 482,00" in texto and "USD 999,00" not in texto


def test_fallo_al_generar_no_expone_error_y_consumo_no_se_repite(monkeypatch):
    generar = Mock(side_effect=RuntimeError("detalle privado que no debe mostrarse"))
    monkeypatch.setattr(herramienta, "generar_resumen", generar)
    cliente = TestClient(app)
    vista = preparar(cliente)
    cuerpo = {"token": vista["token"], "confirmar": True}
    r = cliente.post("/resumen/confirmar", json=cuerpo)
    assert r.status_code == 503 and "detalle privado" not in r.text
    assert cliente.post("/resumen/confirmar", json=cuerpo).status_code == 404
    assert generar.call_count == 1


def test_agente_prepara_sin_generar_y_responde_todo_el_lote(monkeypatch):
    from app.services import agente
    from app.schemas import NormativaAgente
    generar = Mock(return_value=b"%PDF-simulado")
    monkeypatch.setattr(herramienta, "generar_resumen", generar)
    monkeypatch.setattr(agente, "consultar_normativa", lambda *args:
                        NormativaAgente(respuesta="Art. 111 del Código del Trabajo.", fuentes=[FUENTE]))
    modelo = ModeloFalso([turno(llamada("generar_resumen", {"calculo_id": "calculo-0"}, "pdf"),
                                llamada("consultar_normativa", {"pregunta": "Consulta de décimo tercero"}, "lectura"))])
    app.dependency_overrides[ruta_agente.obtener_llm] = lambda: (lambda: modelo)
    cliente = TestClient(app)
    r = cliente.post("/agente", json={"mensaje": "Quiero el resumen PDF de mi décimo tercero", "calculo": CALCULO.model_dump(mode="json")})
    assert r.status_code == 200 and r.json()["estado"] == "requiere_confirmacion"
    assert r.json()["resumen_pdf"]["calculo"]["total"] == 600
    assert "calculo_para_resumen" not in r.json()
    mensajes = [m for m in modelo.historial_actual if m["role"] == "tool"]
    assert {m["tool_call_id"] for m in mensajes} == {"pdf", "lectura"}
    token = r.json()["resumen_pdf"]["token"]
    assert all(token not in m["content"] for m in mensajes)
    generar.assert_not_called()
    assert cliente.post("/resumen/confirmar", json={"token": token, "confirmar": True}).status_code == 200
    assert generar.call_count == 1


def test_modelo_no_puede_incluir_confirmacion_en_la_herramienta(monkeypatch):
    generar = Mock()
    monkeypatch.setattr(herramienta, "generar_resumen", generar)
    modelo = ModeloFalso([turno(llamada("generar_resumen", {"calculo_id": "calculo-0", "confirmar": True}))])
    app.dependency_overrides[ruta_agente.obtener_llm] = lambda: (lambda: modelo)
    r = TestClient(app).post("/agente", json={"mensaje": "Prepare un PDF del décimo tercero", "calculo": CALCULO.model_dump(mode="json")})
    assert r.status_code == 200 and r.json()["estado"] == "pedir_datos" and r.json()["resumen_pdf"] is None
    generar.assert_not_called()


def test_sin_fuentes_se_advierte_y_no_se_finge_recuperacion(monkeypatch):
    monkeypatch.setattr(ruta.rag, "recuperar_calculo", lambda calculo: [])
    vista = preparar(TestClient(app))
    assert not vista["fuentes"] and "configuración" in vista["advertencia_fuentes"]


def test_total_manipulado_no_se_prepara():
    datos = CALCULO.model_dump(mode="json") | {"total": 999}
    assert TestClient(app).post("/resumen/preparar", json={"calculo": datos}).status_code == 422
