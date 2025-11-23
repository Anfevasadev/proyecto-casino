# Implementación de helper para counters usando pandas.
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any

CSV_PATH = Path("data/counters.csv")

EXPECTED_COLUMNS = [
	"id",
	"machine_id",
	"at",
	"in_amount",
	"out_amount",
	"jackpot_amount",
	"billetero_amount",
	"created_at",
	"created_by",
	"updated_at",
	"updated_by",
]


def _read_df() -> pd.DataFrame:
	"""
	Leer el CSV y asegurar que tenga las columnas esperadas.
	Como estudiante: si no existe, devolvemos un DataFrame vacío con columnas.
	"""
	if CSV_PATH.exists():
		df = pd.read_csv(CSV_PATH)
	else:
		df = pd.DataFrame(columns=EXPECTED_COLUMNS)

	# Asegurar que todas las columnas esperadas existan en el DataFrame
	for col in EXPECTED_COLUMNS:
		if col not in df.columns:
			df[col] = None
	return df[EXPECTED_COLUMNS]


def _write_df(df: pd.DataFrame) -> None:
	"""
	Escribir DataFrame al CSV respetando el orden de columnas.
	"""
	df.to_csv(CSV_PATH, index=False)


def next_id() -> int:
	"""Calcular el próximo id disponible (secuencial)."""
	df = _read_df()
	if df.empty:
		return 1
	ids = [int(x) for x in df["id"].dropna().tolist() if str(x).strip() != ""]
	return (max(ids) + 1) if ids else 1


def get_by_id(counter_id: int) -> Optional[Dict[str, Any]]:
	"""Obtener fila por id. Normaliza tipos básicos al retornar."""
	df = _read_df()
	rows = df[df["id"] == counter_id]
	if rows.empty:
		return None
	row = rows.iloc[0].to_dict()
	# Normalizar tipos simples
	row["id"] = int(row["id"]) if str(row.get("id", "")).strip() else None
	for f in ["in_amount", "out_amount", "jackpot_amount", "billetero_amount"]:
		try:
			row[f] = float(row.get(f)) if row.get(f) is not None and str(row.get(f)).strip() != "" else 0.0
		except Exception:
			row[f] = 0.0
	row["machine_id"] = int(row.get("machine_id")) if str(row.get("machine_id", "")).strip() else None
	return row


def list_counters(
	machine_id: Optional[int] = None,
	date_from: Optional[str] = None,
	date_to: Optional[str] = None,
	limit: Optional[int] = 100,
	offset: int = 0,
	sort_by: str = "at",
	ascending: bool = True,
) -> List[Dict[str, Any]]:
	"""
	Listar contadores con filtros simples.

	Notas didácticas:
	- Usamos comparaciones de strings para fechas porque el formato
	  es 'YYYY-MM-DD HH:MM:SS' (orden lexicográfico coincide con orden cronológico).
	- Se aplica paginación con `limit` y `offset`.
	"""
	df = _read_df()

	if machine_id is not None:
		df = df[df["machine_id"] == machine_id]

	if date_from is not None:
		df = df[df["at"] >= date_from]

	if date_to is not None:
		df = df[df["at"] <= date_to]

	# Ordenar según preferencia
	if sort_by not in ["at", "id"]:
		sort_by = "at"
	df = df.sort_values(by=sort_by, ascending=ascending)

	if limit is not None:
		df = df.iloc[offset : offset + limit]
	else:
		df = df.iloc[offset:]

	results: List[Dict[str, Any]] = []
	for _, r in df.iterrows():
		row = r.to_dict()
		# Normalizar tipos sencillos
		try:
			row["id"] = int(row.get("id")) if str(row.get("id", "")).strip() else None
		except Exception:
			row["id"] = None
		try:
			row["machine_id"] = int(row.get("machine_id")) if str(row.get("machine_id", "")).strip() else None
		except Exception:
			row["machine_id"] = None
		for f in ["in_amount", "out_amount", "jackpot_amount", "billetero_amount"]:
			try:
				row[f] = float(row.get(f)) if row.get(f) is not None and str(row.get(f)).strip() != "" else 0.0
			except Exception:
				row[f] = 0.0
		results.append(row)
	return results


def insert_counter(row: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Insertar un registro nuevo en el CSV. `row` debe contener las columnas
	esperadas (al menos las públicas). Retorna la fila insertada.
	"""
	df = _read_df()
	# Asegurar que el id exista y sea único
	if "id" not in row or row["id"] is None:
		row["id"] = next_id()

	# Convertir a DataFrame temporal y concatenar
	df = pd.concat([df, pd.DataFrame([row])], ignore_index=True, sort=False)
	# Escribir asegurando el orden de columnas
	df = df.reindex(columns=EXPECTED_COLUMNS)
	_write_df(df)
	return get_by_id(int(row["id"]))


def update_counter(counter_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
	"""
	Actualiza columnas permitidas de un registro existente.
	Retorna la fila actualizada o None si no existe.
	"""
	df = _read_df()
	idx = df.index[df["id"] == counter_id]
	if len(idx) == 0:
		return None
	i = idx[0]

	allowed = {"at", "in_amount", "out_amount", "jackpot_amount", "billetero_amount", "machine_id", "updated_at", "updated_by"}
	for k, v in cambios.items():
		if k in allowed:
			df.at[i, k] = v

	_write_df(df)
	return get_by_id(counter_id)

