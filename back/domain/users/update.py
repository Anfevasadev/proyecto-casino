from typing import Any, Dict

ROLES_PERMITIDOS = {"admin", "operador", "soporte"}


class NotFoundError(Exception):
	pass


def update_user(user_id: int, cambios: Dict[str, Any], clock, repo, actor: str) -> Dict[str, Any]:
	usuario = repo.get_user_by_id(user_id)
	if not usuario:
		raise NotFoundError(f"Usuario id={user_id} no existe")

	new_username = cambios.get("username")
	if new_username and new_username != usuario.get("username"):
		if repo.username_exists(new_username, exclude_id=user_id):
			raise ValueError("username ya existe")

	if "role" in cambios and cambios["role"] is not None:
		role_val = str(cambios["role"]).strip()
		if role_val not in ROLES_PERMITIDOS:
			raise ValueError("role inválido; use admin|operador|soporte")

	allowed = {"username", "password", "role", "is_active"}
	to_update = {k: v for k, v in cambios.items() if k in allowed and v is not None}

	# Sincronizar estado lógico: is_active <-> is_deleted
	if "is_active" in to_update:
		is_active_val = bool(to_update["is_active"])  # asegurar bool
		if is_active_val:
			# Usuario activo => no eliminado
			to_update["is_deleted"] = False
			to_update["deleted_at"] = None
			to_update["deleted_by"] = None
		else:
			# Usuario inactivo => marcado como eliminado
			to_update["is_deleted"] = True
			to_update["deleted_at"] = clock()
			to_update["deleted_by"] = actor

	to_update["updated_at"] = clock()
	to_update["updated_by"] = actor

	updated = repo.update_user_row(user_id, to_update)
	if not updated:
		# Carrera o inconsistencia
		raise NotFoundError(f"Usuario id={user_id} no existe")

	return {
		"id": int(updated["id"]),
		"username": updated["username"],
		"role": updated["role"],
		"is_active": bool(updated.get("is_active", False)),
	}

