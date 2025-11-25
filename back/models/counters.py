# -------------------------------------------
# back/models/counters.py
# Propósito:
#   - Definir modelos Pydantic para entrada/salida de registros de contadores.
#   - Los comentarios en este archivo están escritos con detalle didáctico
#     para que un estudiante de 4to semestre pueda entenderlos fácilmente.
#
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re
from datetime import date
from decimal import Decimal


# Explicación breve (nivel estudiante):
# - Usamos Pydantic para validar datos entrantes en los endpoints.
# - Cada modelo representa un contrato: cómo espera la API recibir o devolver datos.


def _validate_datetime_format(value: str) -> bool:
	"""
	Validador simple para comprobar que la fecha tenga el formato
	'YYYY-MM-DD HH:MM:SS'. Aquí no hacemos parsing estricto, sólo comprobación
	de patrón para evitar errores comunes al guardar en CSV.
	"""
	pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
	return bool(re.match(pattern, value))


class CounterIn(BaseModel):
	"""
	Modelo para crear un contador.

	Campos:
	- casino_id: id del casino al que pertenece (obligatorio).
	- machine_id: id de la máquina a la que pertenece el registro (obligatorio).
	- at: fecha/hora del registro en formato local 'YYYY-MM-DD HH:MM:SS' (opcional).
	- in_amount/out_amount/jackpot_amount/billetero_amount: montos numéricos >= 0.

	Comentarios didácticos:
	- Pydantic valida tipos automáticamente y los convertirá si es posible.
	- Los montos tienen un `validator` para asegurar que no sean negativos.
	"""

	casino_id: int = Field(..., ge=1, description="ID del casino (entero positivo)")
	machine_id: int = Field(..., ge=1, description="ID de la máquina (entero positivo)")
	at: Optional[str] = Field(None, description="Fecha local 'YYYY-MM-DD HH:MM:SS'")
	in_amount: float = Field(0.0, ge=0.0)
	out_amount: float = Field(0.0, ge=0.0)
	jackpot_amount: float = Field(0.0, ge=0.0)
	billetero_amount: float = Field(0.0, ge=0.0)

	@validator("at")
	def _check_at_format(cls, v: Optional[str]):
		# Si viene, verificar patrón básico. Si no viene, lo aceptamos (dominio puede setearlo).
		if v is None:
			return v
		if not _validate_datetime_format(v):
			raise ValueError("'at' debe tener formato 'YYYY-MM-DD HH:MM:SS'")
		return v


class CounterUpdate(BaseModel):
	"""
	Modelo para correcciones parciales de un contador.

	Todos los campos son opcionales; si vienen, se validan.
	
	Nota sobre 'at':
	- Si NO se incluye 'at': modifica TODOS los contadores de esa máquina en la fecha de la URL
	- Si SÍ se incluye 'at': modifica SOLO el contador con esa fecha/hora exacta
	"""

	machine_id: int = Field(..., ge=1, description="ID de la máquina a modificar")
	at: Optional[str] = Field(None, description="Fecha/hora específica para filtrar un único contador (opcional)")
	in_amount: Optional[float] = Field(None, ge=0.0)
	out_amount: Optional[float] = Field(None, ge=0.0)
	jackpot_amount: Optional[float] = Field(None, ge=0.0)
	billetero_amount: Optional[float] = Field(None, ge=0.0)

	@validator("at")
	def _check_at_format(cls, v: Optional[str]):
		if v is None:
			return v
		if not _validate_datetime_format(v):
			raise ValueError("'at' debe tener formato 'YYYY-MM-DD HH:MM:SS'")
		return v

class CounterUpdateBatch(BaseModel):
    """
    Modelo contenedor para recibir múltiples actualizaciones en una sola petición.
    """
    updates: List[CounterUpdate]

class CounterOut(BaseModel):
	"""
	Modelo de salida que expone los campos principales del registro.

	No incluimos datos de auditoría (created_by/updated_by) aquí para mantener
	la respuesta ligera. Si se necesita auditoría, se podría añadir otro modelo.
	"""

	id: int
	machine_id: int
	casino_id: int
	at: str
	in_amount: float
	out_amount: float
	jackpot_amount: float
	billetero_amount: float

	class Config:
		schema_extra = {
			"example": {
				"id": 1,
				"machine_id": 10,
				"casino_id": 1,
				"at": "2025-11-23 12:00:00",
				"in_amount": 1200.0,
				"out_amount": 800.0,
				"jackpot_amount": 50.0,
				"billetero_amount": 100.0,
			}
		}

# Modelo enriquecido: incluye información mínima de la máquina vinculada.
class MachineSimple(BaseModel):
	"""Información mínima de la máquina para anidar en la respuesta del contador."""
	id: int
	marca: str | None = None
	modelo: str | None = None
	serial: str | None = None
	asset: str | None = None


class CounterOutWithMachine(CounterOut):
	"""Salida de contador que incluye la máquina asociada."""
	machine: MachineSimple | None = None
