from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, field_validator


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


class UserOut(BaseModel):
	id: int
	username: str
	role: RoleEnum
	is_active: bool

