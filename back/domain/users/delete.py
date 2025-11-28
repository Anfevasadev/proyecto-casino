# -------------------------------------------
# back/domain/users/delete.py
# Función esperada: desactivar_usuario(user_id, clock, repo, actor)
#
# Política de borrado lógico en users:
#   - Mínimo: poner is_active=False.
#   - (Opcional) Si se usa is_deleted: poner is_deleted=True y setear deleted_at/by.
#   - Documentar política elegida en README para consistencia.
#
# Entradas:
#   - user_id: int.
#   - clock: función hora local.
#   - repo: repositorio users.
#   - actor: str para auditoría.
#
# Procesamiento:
#   1) Verificar existencia.
#   2) Cambiar flags (is_active=False; si aplica, is_deleted=True).
#   3) Actualizar updated_at/by y (si aplica) deleted_at/by.
#   4) Guardar.
#
# Salida:
#   - Dict sencillo: {"deleted": True, "id": user_id}
#
# Errores:
#   - NotFoundError si no existe.
# -------------------------------------------
from typing import Dict, Any


class NotFoundError(Exception):
    pass


def inactivar_usuario(user_id: int, clock, repo, actor: str) -> Dict[str, Any]:
    """
    Inactiva un usuario (borrado lógico).
    
    Args:
        user_id: ID del usuario a inactivar
        clock: Función que retorna timestamp actual
        repo: Repositorio de usuarios
        actor: Usuario que realiza la acción
        
    Returns:
        Dict con {"deleted": True, "id": user_id}
        
    Raises:
        NotFoundError: Si el usuario no existe
    """
    usuario = repo.get_user_by_id(user_id)
    if not usuario:
        raise NotFoundError(f"Usuario id={user_id} no existe")
    
    cambios = {
        "is_active": False,
        "is_deleted": True,
        "updated_at": clock(),
        "updated_by": actor,
        "deleted_at": clock(),
        "deleted_by": actor
    }
    
    repo.update_user_row(user_id, cambios)
    
    return {"deleted": True, "id": user_id}
