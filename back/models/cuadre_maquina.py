from pydantic import BaseModel
from datetime import date
from decimal import Decimal

# Entrada del cuadre
class CuadreIn(BaseModel):
    maquina_id: int
    fecha_inicio: date
    fecha_fin: date

# Salida del cuadre
class CuadreOut(BaseModel):
    maquina_id: int
    fecha_inicio: date
    fecha_fin: date
    total_in: Decimal
    total_out: Decimal
    total_jackpot: Decimal
    total_billetero: Decimal
    utilidad: Decimal

