"""Módulo unificado para inactivación de máquinas y utilidades.

Este módulo ofrece funciones para:
- Inicializar CSVs locales en la carpeta `back/domain/machines`.
- Crear/leer/guardar máquinas en `machines.csv`.
- Inactivar una máquina por `serial` (borrado lógico) y registrar
  la acción en `logs.csv`.
- Exportar listados de máquinas activas/inactivas.
- Generar una "variable de inactivación" única.

Los CSVs creados por este módulo (si no existen) son:
- machines.csv: lista de máquinas y metadatos.
- logs.csv: historial de acciones (inactivaciones, modificaciones).
- machines_status.csv: listado simple de id/serial/is_active (útil para reportes).

Se diseñó para que las pruebas se puedan ejecutar localmente con
`uvicorn back.main:app --reload` y usando endpoints que interactúen
con estas funciones.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd


BASE_DIR = os.path.dirname(__file__)
# Guardar CSVs en la carpeta `back/storage` en vez de en `back/domain/machines`
STORAGE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage"))
os.makedirs(STORAGE_DIR, exist_ok=True)
MACHINES_CSV = os.path.join(STORAGE_DIR, "machines.csv")
LOGS_CSV = os.path.join(STORAGE_DIR, "logs.csv")
MACHINES_STATUS_CSV = os.path.join(STORAGE_DIR, "machines_status.csv")


def _now(clock: Optional[callable] = None) -> str:
	if callable(clock):
		return clock()
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_data_files() -> None:
	"""Crea los CSVs con cabeceras básicas si no existen."""
	# machines.csv headers
	if not os.path.exists(MACHINES_CSV):
		df = pd.DataFrame(
			columns=[
				"id",
				"marca",
				"modelo",
				"serial",
				"asset",
				"denominacion",
				"casino_id",
				"is_active",
				"created_at",
				"created_by",
				"updated_at",
				"updated_by",
			]
		)
		df.to_csv(MACHINES_CSV, index=False)

	# logs.csv headers
	if not os.path.exists(LOGS_CSV):
		logs = pd.DataFrame(
			columns=[
				"timestamp",
				"action",
				"machine_id",
				"serial",
				"inactivation_token",
				"motivo",
				"actor",
				"note",
			]
		)
		logs.to_csv(LOGS_CSV, index=False)

	# machines_status.csv headers (redundant, útil para reportes)
	if not os.path.exists(MACHINES_STATUS_CSV):
		status = pd.DataFrame(columns=["id", "serial", "is_active"])
		status.to_csv(MACHINES_STATUS_CSV, index=False)


def load_machines_df() -> pd.DataFrame:
	ensure_data_files()
	return pd.read_csv(MACHINES_CSV, dtype=str)


def save_machines_df(df: pd.DataFrame) -> None:
	df.to_csv(MACHINES_CSV, index=False)


def append_log(entry: Dict[str, Any]) -> None:
	ensure_data_files()
	logs_df = pd.read_csv(LOGS_CSV, dtype=str)
	for k in entry.keys():
		if k not in logs_df.columns:
			logs_df[k] = ""
	logs_df = pd.concat([logs_df, pd.DataFrame([entry])], ignore_index=True)
	logs_df.to_csv(LOGS_CSV, index=False)


def update_status_csv() -> None:
	df = load_machines_df()
	if "is_active" not in df.columns:
		df["is_active"] = "True"
	status = df[[col for col in ["id", "serial", "is_active"] if col in df.columns]].copy()
	status.to_csv(MACHINES_STATUS_CSV, index=False)


def crear_variable_inactivacion(serial: str) -> str:
	return f"INACT-{serial}-{uuid.uuid4().hex}"


def inactivar_maquina_por_serial(
	serial: str,
	clock: Optional[callable] = None,
	actor: str = "system",
	motivo: Optional[str] = None,
) -> Dict[str, Any]:
	"""Marca una máquina como inactiva (borrado lógico) por su serial.

	- Conserva la fila en `machines.csv` pero marca `is_active` = False.
	- Agrega una entrada en `logs.csv` con token de inactivación.
	- Actualiza `machines_status.csv`.

	Retorna la fila actualizada como dict.
	"""
	ensure_data_files()
	df = pd.read_csv(MACHINES_CSV, dtype=str)
	if "serial" not in df.columns:
		raise ValueError("CSV de máquinas no contiene columna 'serial'")

	matches = df[df["serial"].astype(str).str.strip() == str(serial).strip()]
	if matches.empty:
		raise ValueError(f"No se encontró máquina con serial: {serial}")

	idx = matches.index[0]
	token = uuid.uuid4().hex
	timestamp = _now(clock)

	# Asegurar columnas de auditoría
	for col, default in (("is_active", "True"), ("updated_at", ""), ("updated_by", "")):
		if col not in df.columns:
			df[col] = "" if default == "" else default

	if str(df.at[idx, "is_active"]).strip().lower() == "false":
		# Ya inactiva: registrar intento en logs y retornar
		log_entry = {
			"timestamp": timestamp,
			"action": "inactivation_attempt_on_already_inactive",
			"machine_id": df.at[idx, "id"] if "id" in df.columns else "",
			"serial": serial,
			"inactivation_token": token,
			"motivo": motivo or "intent_again",
			"actor": actor,
			"note": "machine_already_inactive",
		}
		append_log(log_entry)
		row = df.loc[idx].to_dict()
		# limpiar valores NaN para que sean serializables JSON
		clean_row = {k: ("" if pd.isna(v) else v) for k, v in row.items()}
		return clean_row

	# Marcar inactiva
	df.at[idx, "is_active"] = "False"
	df.at[idx, "updated_at"] = timestamp
	df.at[idx, "updated_by"] = actor
	save_machines_df(df)

	log_entry = {
		"timestamp": timestamp,
		"action": "inactivate_machine",
		"machine_id": df.at[idx, "id"] if "id" in df.columns else "",
		"serial": serial,
		"inactivation_token": token,
		"motivo": motivo or "inactivacion_manual",
		"actor": actor,
		"note": "",
	}
	append_log(log_entry)
	update_status_csv()

	row = df.loc[idx].to_dict()
	clean_row = {k: ("" if pd.isna(v) else v) for k, v in row.items()}
	return clean_row

# Clase ligera para manipulación en memoria si se desea usar en pruebas
from typing import List


class Maquina:
	def __init__(
		self,
		id: int,
		marca: str,
		modelo: str,
		serial: str,
		asset: str,
		denominacion: str,
		estado: str = "Activa",
		casino_id: Optional[int] = None,
	):
		self.id = id
		self.marca = marca
		self.modelo = modelo
		self.serial = serial
		self.asset = asset
		self.denominacion = denominacion
		self.estado = estado
		self.casino_id = casino_id
		self.inactivation_date: Optional[datetime] = None
		self.historial: List[str] = []

	def inactivar(self) -> bool:
		if self.estado == "Inactiva":
			self.historial.append(f"Intento inactivar repetido: {datetime.now()}")
			return False
		self.estado = "Inactiva"
		self.inactivation_date = datetime.now()
		self.historial.append(f"Inactivada: {self.inactivation_date}")
		return True

	def activar(self) -> bool:
		if self.estado == "Activa":
			self.historial.append(f"Intento activar repetido: {datetime.now()}")
			return False
		self.estado = "Activa"
		self.inactivation_date = None
		self.historial.append(f"Reactivada: {datetime.now()}")
		return True


class Casino:
	def __init__(self, id: int, nombre: str, direccion: str, codigoCasino: str, estado: str = "Activo"):
		self.id = id
		self.nombre = nombre
		self.direccion = direccion
		self.codigoCasino = codigoCasino
		self.estado = estado
		self.maquinas: List[Maquina] = []

	def registrar_maquina(self, maquina: Maquina) -> None:
		self.maquinas.append(maquina)

