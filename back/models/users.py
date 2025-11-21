# -------------------------------------------
# back/models/users.py
# Propósito:
#   - Definir contratos Pydantic para usuarios.
#
# Modelos esperados:
#   1) UserIn (entrada para crear):
#       - username: str (obligatorio, sin espacios extremos; único a nivel dominio).
#       - password: str (obligatorio; se almacenará "tal cual" en CSV por requisito académico).
#       - role: str (opcional con default 'operador'; restringir a {'admin','operador','soporte'}).
#       - is_active: bool (default True).
#     Validaciones:
#       * username no vacío, normalizado con .strip().
#       * role ∈ conjunto permitido (puede ser Enum para mejor claridad).
#
#   2) UserUpdate (entrada para actualizar):
#       - Campos editables: password (opcional), role (opcional, con mismas reglas),
#         is_active (opcional), username (opcional si se decide permitir cambiarlo).
#     Validaciones:
#       * Si trae username, mismas reglas que UserIn y dominio debe validar duplicidad.
#
#   3) UserOut (salida):
#       - id: int
#       - username: str
#       - role: str
#       - is_active: bool
#     Importante:
#       * NO incluir password.
#
# Consideraciones:
#   - Los campos de auditoría (created_at, created_by, etc.) no se exponen en UserOut,
#     a menos que se requiera explícitamente (se sugiere mantener la salida limpia).
#   - Si se usa Enum para role, documentar su string literal para claridad en OpenAPI.
# -------------------------------------------
from enum import StrEnum
from pydantic import BaseModel, field_validator
from typing import Optional

class RoleEnum(StrEnum):
    admin = "admin"
    operador = "operador"
    soporte = "soporte"

class UserIn(BaseModel):
    username: str
    password: str
    role: RoleEnum = RoleEnum.operador
    is_active: bool = True

    @field_validator("username")
    @classmethod
    def username_non_empty(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("username no puede estar vacío")
        return v2

class UserOut(BaseModel):
    id: int
    username: str
    role: RoleEnum
    is_active: bool
        
class UserUpdate(BaseModel):
	username: Optional[str] = None
	password: Optional[str] = None
	role: Optional[RoleEnum] = None
	is_active: Optional[bool] = None

	@field_validator("username")
	@classmethod
	def username_non_empty_if_present(cls, v: Optional[str]) -> Optional[str]:
		if v is None:
			return v
		v2 = v.strip()
		if not v2:
			raise ValueError("username no puede estar vacío")
		return v2
