"""Funciones de activación de máquinas.

Este módulo implementa la activación (marcar `is_active=True`) reutilizando
las rutas CSV dentro de `back/domain/machines`.

Provee:
- `activar_maquina_por_serial`: reactiva una máquina, actualiza CSVs y logs.
- CLI mínimo para pruebas.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd

from .inativation import ensure_data_files, append_log, MACHINES_CSV, LOGS_CSV, MACHINES_STATUS_CSV


def _now() -> str:
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def activar_maquina_por_serial(serial: str, actor: str = "system", note: Optional[str] = None) -> Dict[str, Any]:
	"""Reactiva una máquina por su `serial`.

	Comportamiento:
	- Si la máquina no existe -> ValueError.
	- Si ya está activa -> registra intento en `logs.csv` y devuelve fila.
	- Si está inactiva -> marca `is_active=True`, actualiza timestamps, graba CSVs y registra en logs.

	Retorna la fila actualizada (NaN convertidos a cadena vacía).
	"""
	ensure_data_files()
	if not os.path.exists(MACHINES_CSV):
		raise ValueError(f"Archivo de máquinas no encontrado: {MACHINES_CSV}")

	df = pd.read_csv(MACHINES_CSV, dtype=str)
	if "serial" not in df.columns:
		raise ValueError("CSV de máquinas no contiene columna 'serial'")

	matches = df[df["serial"].astype(str).str.strip() == str(serial).strip()]
	if matches.empty:
		raise ValueError(f"No se encontró máquina con serial: {serial}")

	idx = matches.index[0]
	timestamp = _now()

	# Asegurar columnas de auditoría
	for col, default in (("is_active", "True"), ("updated_at", ""), ("updated_by", "")):
		if col not in df.columns:
			df[col] = "" if default == "" else default

	current_state = str(df.at[idx, "is_active"]).strip().lower()
	if current_state == "true":
		# Ya activa: registrar intento y devolver
		log_entry = {
			"timestamp": timestamp,
			"action": "activation_attempt_on_already_active",
			"machine_id": df.at[idx, "id"] if "id" in df.columns else "",
			"serial": serial,
			"inactivation_token": "",
			"motivo": "",
			"actor": actor,
			"note": note or "machine_already_active",
		}
		append_log(log_entry)
		row = df.loc[idx].to_dict()
		clean = {k: ("" if pd.isna(v) else v) for k, v in row.items()}
		return clean

	# Reactivar
	df.at[idx, "is_active"] = "True"
	df.at[idx, "updated_at"] = timestamp
	df.at[idx, "updated_by"] = actor

	df.to_csv(MACHINES_CSV, index=False)

	log_entry = {
		"timestamp": timestamp,
		"action": "activate_machine",
		"machine_id": df.at[idx, "id"] if "id" in df.columns else "",
		"serial": serial,
		"inactivation_token": "",
		"motivo": "reactivacion_manual",
		"actor": actor,
		"note": note or "",
	}
	append_log(log_entry)

	# actualizar machines_status.csv
	status = df[[col for col in ["id", "serial", "is_active"] if col in df.columns]].copy()
	status.to_csv(MACHINES_STATUS_CSV, index=False)

	row = df.loc[idx].to_dict()
	clean = {k: ("" if pd.isna(v) else v) for k, v in row.items()}
	return clean


if __name__ == "__main__":
	import sys
	if len(sys.argv) < 2:
		print("Uso: python activation.py <SERIAL> [actor] [note]")
		raise SystemExit(1)
	serial = sys.argv[1]
	actor = sys.argv[2] if len(sys.argv) > 2 else "system"
	note = sys.argv[3] if len(sys.argv) > 3 else None
	print(activar_maquina_por_serial(serial, actor=actor, note=note))
