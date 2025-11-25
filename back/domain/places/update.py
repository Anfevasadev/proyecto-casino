
# -------------------------------------------
# back/domain/places/update.py
# Función: actualizar_place(place_id, cambios, clock, repo, actor)
# -------------------------------------------
from typing import Any, Dict

class NotFoundError(Exception):
	pass

def actualizar_place(place_id: int, cambios: Dict[str, Any], clock, repo, actor: str) -> Dict[str, Any]:
	"""
	Actualiza los datos de un casino (place), excepto el código de casino.
	Solo permite modificar nombre, dirección y estado.
	Siempre actualiza updated_at y updated_by.
	"""
	# Leer registro actual
	place = repo.get_place_by_id(place_id)
	if not place:
		raise NotFoundError(f"Casino id={place_id} no existe")

	# Validar duplicidad de nombre si cambia
	nuevo_nombre = cambios.get("nombre")
	if nuevo_nombre and nuevo_nombre != place["nombre"]:
		if repo.nombre_exists(nuevo_nombre, exclude_id=place_id):
			raise ValueError("Ya existe un casino con ese nombre")

	# Solo permitir cambios en nombre, dirección y estado
	allowed = {"nombre", "direccion", "estado"}
	to_update = {k: v for k, v in cambios.items() if k in allowed and v is not None}
	to_update["updated_at"] = clock()
	to_update["updated_by"] = actor

	# No permitir modificar codigo_casino
	if "codigo_casino" in cambios:
		del cambios["codigo_casino"]

	updated = repo.update_place_row(place_id, to_update)
	if not updated:
		raise NotFoundError(f"Casino id={place_id} no existe")

	# Retornar datos organizados
	return {
		"id": int(updated["id"]),
		"nombre": updated["nombre"],
		"direccion": updated["direccion"],
		"codigo_casino": updated["codigo_casino"],
		"estado": updated["estado"],
		"created_at": updated["created_at"],
		"created_by": updated["created_by"],
		"updated_at": updated["updated_at"],
		"updated_by": updated["updated_by"]
	}
