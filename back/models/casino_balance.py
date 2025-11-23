# back/models/casino_balance.py
# Modelo interno y modelos Pydantic para el cuadre general de casino.

from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class CasinoCuadre:
    """
    Modelo interno usado por la capa de dominio.
    Representa el cuadre consolidado de todas las máquinas de un casino.
    """

    def __init__(self, id, fecha_inicio, fecha_fin, total_in, total_out, total_jackpot, total_billetero, utilidad, casino_id):
        self.id = id
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.total_in = total_in
        self.total_out = total_out
        self.total_jackpot = total_jackpot
        self.total_billetero = total_billetero
        self.utilidad = utilidad
        self.casino_id = casino_id


class CasinoCuadreInput(BaseModel):
    """
    Datos recibidos desde el endpoint para generar un cuadre.
    """
    casino_id: int
    fecha_inicio: date
    fecha_fin: date


class CasinoCuadreOutput(BaseModel):
    """
    Datos devueltos al usuario una vez generado el cuadre.
    """
    total_in: Decimal
    total_out: Decimal
    total_jackpot: Decimal
    total_billetero: Decimal
    utilidad: Decimal
    casino_id: int
    fecha_inicio: date
    fecha_fin: date
