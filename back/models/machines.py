# -------------------------------------------
# back/models/machines.py
# Propósito:
#   - Contratos Pydantic para "máquinas".
#
# Campos relevantes (alineados a CSV):
#   - code: identificador visible de la máquina (string único).
#   - denomination_value: float/Decimal (valor de denominación; >= 0).
#   - place_id: int (FK lógica a places.id).
#   - participation_rate: float (0..1).
#   - is_active: bool.
#
# Modelos esperados:
#   1) MachineIn (crear):
#       - code: str (obligatorio; único; .strip(); puede validar patrón simple si se desea).
#       - denomination_value: float (obligatorio; >= 0).
#       - place_id: int (obligatorio; debe existir a nivel dominio).
#       - participation_rate: float (default 1.0; validar 0 ≤ x ≤ 1).
#       - is_active: bool (default True).
#
#   2) MachineUpdate (actualizar):
#       - code: str | None (si viene, mantener unicidad).
#       - denomination_value: float | None (si viene, >= 0).
#       - place_id: int | None (si viene, validar existencia de place).
#       - participation_rate: float | None (si viene, validar 0..1).
#       - is_active: bool | None.
#
#   3) MachineOut (salida):
#       - id: int
#       - code: str
#       - denomination_value: float
#       - place_id: int
#       - participation_rate: float
#       - is_active: bool
#
# Validaciones clave:
#   - code sin espacios alrededor; opcionalmente upper/lower para normalizar.
#   - denomination_value >= 0.
#   - participation_rate en el rango [0,1].
# -------------------------------------------
from pydantic import BaseModel, Field

class MachineIn(BaseModel):
    marca: str
    modelo: str
    serial: str
    asset: str
    place_id: int
    denominacion: float = Field(..., ge=0)
    is_active: bool = True

class MachineOut(BaseModel):
    id: int
    marca: str
    modelo: str
    serial: str
    asset: str
    denominacion: float
    estado: bool
    casino_id: int