# -------------------------------------------
# back/domain/users/create.py
# Función esperada: create_usuario(data, clock, repo, actor)
#
# Entradas:
#   - data: dict o modelo con {username, password, role='operador', is_active=True}.
#   - clock: función inyectable que retorna la hora local como str 'YYYY-MM-DD HH:MM:SS'
#            (permite testear sin depender del sistema).
#   - repo: repositorio de users (storage/users_repo.py) con helpers: read_df, write_df, next_id,
#           existe_username(username), insertar_fila(row).
#   - actor: str con el usuario (o 'system') que ejecuta la acción (para auditoría).
#
# Validaciones:
#   - username obligatorio, no vacío y único (no permitir duplicados).
#   - role ∈ {'admin','operador','soporte'}.
#   - password obligatorio (se guarda tal cual, sin hash).
#
# Procesamiento:
#   1) Generar id = repo.next_id().
#   2) Construir fila con campos mínimos + auditoría:
#        id, username, password, role, is_active,
#        created_at=clock(), created_by=actor,
#        updated_at=clock(), updated_by=actor
#      (Si se decide usar is_deleted en users: inicializar en False; deleted_* vacíos.)
#   3) repo.insertar_fila(fila).
#
# Salidas:
#   - Dict/obj con datos públicos del usuario creado (sin exponer password):
#     {id, username, role, is_active}.
#
# Errores a considerar:
#   - Username duplicado -> lanzar excepción de dominio (p.ej., ValueError o DomainError).
#   - Role inválido -> excepción.
# -------------------------------------------
from datetime import datetime
from back.storage import users_repo
from back.models.users import UserIn

ROLES_PERMITIDOS = {"admin", "operador", "soporte"}

def _clock() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_user(user_in: UserIn, created_by: str = "system"):
    # Validar rol (por si viene manipulado externamente)
    if user_in.role.value not in ROLES_PERMITIDOS:
        raise ValueError("Rol inválido; use admin|operador|soporte")

    if users_repo.username_exists(user_in.username):
        raise ValueError("El username ya está en uso")

    new_id = users_repo.next_id()
    now = _clock()
    row = {
        "id": new_id,
        "username": user_in.username,
        "password": user_in.password,
        "role": user_in.role.value,
        "is_active": user_in.is_active,
        "is_deleted": False,
        "created_at": now,
        "created_by": created_by,
        "updated_at": None,
        "updated_by": None,
        "deleted_at": None,
        "deleted_by": None,
    }

    users_repo.insert_user(row)

    return {
        "id": new_id,
        "username": row["username"],
        "role": row["role"],
        "is_active": row["is_active"],
    }
