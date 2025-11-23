"""
back/domain/counters/create.py

Implementación de la función de dominio `create_counter`.

Comentarios para estudiantes (4to semestre):
- La capa "domain" es responsable de las reglas de negocio. Aquí validamos
  que la máquina exista y esté activa, que los montos no sean negativos y
  que la fecha/horario de registro esté presente o se asigne mediante la
  función `clock`.
- No hacemos I/O directo con CSV: llamamos a `counters_repo` que encapsula
  las operaciones de almacenamiento.
"""

from typing import Callable, Dict, Any, Optional


class NotFoundError(Exception):
	pass


def create_counter(
	data: Dict[str, Any],
	clock: Callable[[], str],
	counters_repo,
	machines_repo,
	actor: str = "system",
	logs_repo: Optional[object] = None,
) -> Dict[str, Any]:
	"""
	Crear un registro de contador aplicando las validaciones de dominio.

	Parámetros:
	- data: dict con keys: machine_id, at (opcional), in_amount, out_amount,
	  jackpot_amount, billetero_amount.
	- clock: función que retorna la fecha/hora local como string.
	- counters_repo: módulo/objeto que expone `next_id()` e `insert_counter()`.
	- machines_repo: módulo/objeto que expone `get_by_id()`.
	- actor: identificador del usuario/sistema que crea el registro.
	- logs_repo: repo opcional para auditoría (no obligatorio aquí).

	Retorna el registro insertado (con id y campos normalizados).

	Lanza:
	- NotFoundError: si la máquina no existe o está inactiva.
	- ValueError: si las validaciones de montos fallan.
	"""

	# Validar presencia del campo machine_id
	machine_id = data.get("machine_id")
	if machine_id is None:
		raise ValueError("machine_id es obligatorio")

	# Validar que la máquina existe
	machine = machines_repo.get_by_id(int(machine_id))
	if machine is None:
		raise NotFoundError(f"Máquina con id {machine_id} no encontrada")

	# Validar que la máquina esté activa. Algunos CSV guardan 'is_active' como string.
	is_active_val = machine.get("is_active")
	is_active = False
	if isinstance(is_active_val, bool):
		is_active = is_active_val
	elif is_active_val is None:
		is_active = False
	else:
		is_active = str(is_active_val).lower() == "true"

	if not is_active:
		raise NotFoundError(f"Máquina {machine_id} no está activa")

	# Montos: asegurar que no son negativos
	for fld in ["in_amount", "out_amount", "jackpot_amount", "billetero_amount"]:
		val = data.get(fld, 0)
		try:
			num = float(val)
		except Exception:
			raise ValueError(f"El campo {fld} debe ser numérico")
		if num < 0:
			raise ValueError(f"El campo {fld} no puede ser negativo")
		data[fld] = num

	# Fecha/hora: si no viene, asignar usando clock()
	at = data.get("at")
	if not at:
		data["at"] = clock()

	# Preparar la fila final con auditoría simple
	created_at = clock()
	created_by = actor
	data_to_insert = {
		"id": None,  # counters_repo.insert_counter asignará next_id si es necesario
		"machine_id": int(machine_id),
		"at": data.get("at"),
		"in_amount": data.get("in_amount", 0.0),
		"out_amount": data.get("out_amount", 0.0),
		"jackpot_amount": data.get("jackpot_amount", 0.0),
		"billetero_amount": data.get("billetero_amount", 0.0),
		"created_at": created_at,
		"created_by": created_by,
		"updated_at": created_at,
		"updated_by": created_by,
	}

	# Insertar usando el repo de counters
	inserted = counters_repo.insert_counter(data_to_insert)

	# (Opcional) registrar en logs_repo si se proporciona
	if logs_repo is not None and hasattr(logs_repo, "insert"):
		try:
			logs_repo.insert({
				"event": "create",
				"entity": "counter",
				"entity_id": inserted.get("id"),
				"actor": actor,
				"timestamp": created_at,
			})
		except Exception:
			# No fallamos si el log no se puede escribir; es opcional
			pass

	return inserted

