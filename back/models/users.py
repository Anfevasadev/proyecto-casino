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
from pydantic import BaseModel, Field
from typing import Optional

class UserIn(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)
    role: str
    is_active: bool = True
class UserOut(BaseModel):
    username: str
    role: str
    is_active: bool
    created_at: str
    created_by: str
        