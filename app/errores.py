"""Errores con contrato (RFC 9457, application/problem+json).

El usuario recibe siempre un mensaje claro; el detalle técnico va al registro (logs/),
unido por un request_id. Nunca se envía un stack trace al navegador.
"""
from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("api")

TITULOS = {
    400: "Solicitud no válida",
    404: "Recurso no encontrado",
    422: "Datos de entrada no válidos",
    429: "Demasiadas solicitudes",
    500: "Error interno",
    503: "El asistente no está disponible",
}


def problema(estado: int, detalle: str, request: Request, tipo: str = "about:blank",
             cabeceras: dict | None = None, extra: dict | None = None) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None) or uuid.uuid4().hex[:8]
    cuerpo = {
        "type": tipo,
        "title": TITULOS.get(estado, "Error"),
        "status": estado,
        "detail": detalle,
        "instance": f"{request.url.path}#req-{request_id}",
        **(extra or {}),
    }
    return JSONResponse(cuerpo, status_code=estado, headers=cabeceras,
                        media_type="application/problem+json")


def registrar_manejadores(app: FastAPI) -> None:
    @app.middleware("http")
    async def asignar_request_id(request: Request, call_next):
        request.state.request_id = uuid.uuid4().hex[:8]
        return await call_next(request)

    @app.exception_handler(RequestValidationError)
    async def entrada_invalida(request: Request, exc: RequestValidationError):
        campos = [
            {"campo": ".".join(str(p) for p in e["loc"] if p != "body"), "mensaje": e["msg"]}
            for e in exc.errors()
        ]
        return problema(422, "Revise los datos marcados: hay valores faltantes o no válidos.", request,
                        tipo="/errores/entrada-invalida", extra={"campos": campos})

    @app.exception_handler(StarletteHTTPException)
    async def error_http(request: Request, exc: StarletteHTTPException):
        detalle = exc.detail if isinstance(exc.detail, str) else TITULOS.get(exc.status_code, "Error")
        return problema(exc.status_code, detalle, request, cabeceras=getattr(exc, "headers", None))

    @app.exception_handler(Exception)
    async def error_inesperado(request: Request, exc: Exception):
        rid = getattr(request.state, "request_id", "-")
        log.exception("error inesperado req-%s en %s", rid, request.url.path)
        return problema(500, f"Algo falló de nuestro lado. Código: req-{rid}.", request,
                        tipo="/errores/interno")
