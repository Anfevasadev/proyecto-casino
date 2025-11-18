# -------------------------------------------
# back/models/machines.py
# Propósito:
#   - Contratos Pydantic para "máquinas".

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union
from decimal import Decimal

class MachineBase(BaseModel):
    # Usamos Union[float, Decimal] para permitir floats en la entrada y convertirlos a Decimal
    denomination_value: Union[float, Decimal] = Field(ge=0.0, description="Valor de la moneda/ficha (>= 0)")
    place_id: int = Field(gt=0, description="ID del lugar (place) donde se ubica la máquina")
    # participation_rate (por defecto se maneja en MachineIn)
    participation_rate: Union[float, Decimal] = Field(ge=0.0, le=1.0, description="Tasa de participación [0.0, 1.0]")
    is_active: bool = Field(default=True, description="Estado de activación de la máquina")

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

class MachineUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=3, max_length=10, description="Código único de la máquina")
    denomination_value: Optional[Union[float, Decimal]] = Field(None, ge=0.0)
    place_id: Optional[int] = Field(None, gt=0)
    participation_rate: Optional[Union[float, Decimal]] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None
    
    @field_validator('code', mode='before')
    @classmethod
    def normalize_code_optional(cls, v: Optional[str]) -> Optional[str]:
        """Normaliza el código solo si está presente."""
        if v is not None and isinstance(v, str):
            return v.strip().upper()
        return v

#
#   2) MachineUpdate (actualizar):
#       - code: str | None (si viene, mantener unicidad).
#       - denomination_value: float | None (si viene, >= 0).
#       - place_id: int | None (si viene, validar existencia de place).
#       - participation_rate: float | None (si viene, validar 0..1).
#       - is_active: bool | None.

class MachineUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=3, max_length=10, description="Código único de la máquina")
    denomination_value: Optional[Union[float, Decimal]] = Field(None, ge=0.0)
    place_id: Optional[int] = Field(None, gt=0)
    participation_rate: Optional[Union[float, Decimal]] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None
    
    @field_validator('code', mode='before')
    @classmethod
    def normalize_code_optional(cls, v: Optional[str]) -> Optional[str]:
        """Normaliza el código solo si está presente."""
        if v is not None and isinstance(v, str):
            return v.strip().upper()
        return v

#   3) MachineOut (salida):
#       - id: int
#       - code: str
#       - denomination_value: float
#       - place_id: int
#       - participation_rate: float
#       - is_active: bool

class MachineOut(MachineBase):
    id: int = Field(gt=0, description="Identificador único de la máquina")
    
    # El campo code se incluye aquí con el tipo final
    code: str
    
    # La salida incluye los campos de auditoría definidos en el dominio
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str
    # Opcionales para el borrado lógico
    is_deleted: bool
    deleted_at: Optional[str] = None
    deleted_by: Optional[str] = None
    
    # Configuración para que Pydantic maneje objetos no estándar (como los diccionarios de Pandas)
    class Config:
        from_attributes = True

# Validaciones clave:
#   - code sin espacios alrededor; opcionalmente upper/lower para normalizar.
#   - denomination_value >= 0.
#   - participation_rate en el rango [0,1].
# -------------------------------------------
