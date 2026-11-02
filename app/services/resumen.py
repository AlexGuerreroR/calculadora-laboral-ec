"""Instantáneas pendientes de aprobación, solo en memoria y con caducidad.

Preparar nunca genera un PDF. El token es aleatorio, de un solo uso y asociado
a una sesión de navegador. Confirmar consume atómicamente la instantánea que
el usuario revisó; el cliente no puede sustituir su cálculo en esa confirmación.
"""
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from app.schemas import ResultadoCalculo, VistaPreviaResumen
from app.tools.parametros import cargar_parametros
from app.tools.resumen import datos_para_vista


class SolicitudNoDisponible(Exception):
    pass


class DemasiadosPendientes(Exception):
    pass


@dataclass(frozen=True)
class PendienteResumen:
    propietario: str
    vence: float
    calculo: ResultadoCalculo
    fuentes: tuple
    advertencia_fuentes: str
    preparado_en: str
    nombre_archivo: str


class AlmacenResumen:
    def __init__(self, reloj=time.monotonic):
        self.reloj = reloj
        self._pendientes = {}
        self._candado = threading.Lock()

    def _limpiar(self):
        ahora = self.reloj()
        for token in [t for t, p in self._pendientes.items() if p.vence <= ahora]:
            del self._pendientes[token]

    def preparar(self, calculo, fuentes, propietario, advertencia_fuentes=""):
        cfg = cargar_parametros()["resumen"]
        preparado = datetime.now(ZoneInfo(cfg["zona_horaria"])).isoformat(timespec="seconds")
        nombre = f"resumen-{calculo.tipo}.pdf"
        with self._candado:
            self._limpiar()
            propios = sum(p.propietario == propietario for p in self._pendientes.values())
            if len(self._pendientes) >= cfg["max_pendientes"] or propios >= cfg["max_pendientes_por_sesion"]:
                raise DemasiadosPendientes()
            token = secrets.token_urlsafe(32)
            self._pendientes[token] = PendienteResumen(
                propietario, self.reloj() + cfg["vigencia_segundos"], calculo.model_copy(deep=True),
                tuple(f.model_copy(deep=True) for f in fuentes), advertencia_fuentes, preparado, nombre)
        return VistaPreviaResumen(token=token, nombre_archivo=nombre, calculo=calculo.model_copy(deep=True),
            datos=datos_para_vista(calculo),
            fuentes=[f.model_copy(deep=True) for f in fuentes], advertencia_fuentes=advertencia_fuentes,
            preparado_en=preparado, vence_en_segundos=cfg["vigencia_segundos"],
            mensaje="Revise estos datos. El PDF se generará únicamente al pulsar confirmar y descargar.")

    def consumir(self, token, propietario):
        with self._candado:
            self._limpiar()
            pendiente = self._pendientes.get(token)
            if not pendiente or not secrets.compare_digest(pendiente.propietario, propietario):
                raise SolicitudNoDisponible()
            return self._pendientes.pop(token)


almacen = AlmacenResumen()
