# -------------------------------------------
# back/api/v1/users.py
# Propósito:
#   Endpoints HTTP para CRUD de usuarios (basados en CSV).
#
# Router esperado:
#   - Variable "router" = APIRouter()
#
# Modelos (importar de back/models/users.py):
#   - UserIn: datos de entrada para crear usuario (username, password, role, is_active).
#   - UserOut: datos de salida (id, username, role, is_active).
#
# Dependencias:
#   - get_repos() desde back/api/deps.py para obtener acceso a users_repo.
#   - pagination_params(), filter_active_param() (opcional) para listar.
#
# Endpoints (sugeridos):
#   1) GET /
#      - Query: limit (int), offset (int), only_active (bool=true por defecto).
#      - Procesamiento: leer CSV vía users_repo, aplicar filtros/paginación.
#      - Salida (200): lista de UserOut.
#
#   2) GET /{user_id}
#      - Path: user_id (int).
#      - Procesamiento: buscar fila por ID en CSV; si no existe → 404.
#      - Salida (200): UserOut.
#      - Errores: 404 si no existe.
#
#   3) POST /
#      - Body: UserIn (validado por Pydantic/FastAPI).
#      - Validaciones:
#          * username no repetido.
#          * role ∈ {"admin","operador","soporte"} (validar aquí o en modelo).
#      - Procesamiento: asignar "id" secuencial (next_id), escribir fila.
#      - Salida (201): UserOut con id asignado.
#      - Errores: 400 si username ya existe.
#
#   4) PUT /{user_id}
#      - Body: campos actualizables (p. ej., role, is_active, password).
#      - Validaciones:
#          * user_id existente.
#          * username si se permitiera editar: no duplicar.
#      - Procesamiento: actualizar fila; escribir CSV.
#      - Salida (200): UserOut actualizado.
#      - Errores: 404 si no existe; 400 por duplicados.
#
#   5) DELETE /{user_id}
#      - Regla de borrado lógico:
#          * En usuarios, el CSV tiene tanto is_active como is_deleted.
#          * Decisión simple: al "eliminar", poner is_active=false (y opcionalmente is_deleted=true).
#            Documentar la política elegida en README si se usa is_deleted.
#      - Validaciones: user_id existente.
#      - Procesamiento: marcar flags y escribir CSV.
#      - Salida (200): {"deleted": true, "id": <user_id>}
#      - Errores: 404 si no existe.
#
# Consideraciones:
#   - Password se guarda "tal cual" (requisito académico), sin hash.
#   - No implementar autenticación en este archivo (solo CRUD).
#   - Usar pandas en repos (storage/users_repo.py), no aquí.
#
# Librerías:
#   - fastapi (APIRouter, HTTPException, status)
#   - pydantic (modelos)
#
# Códigos de estado:
#   - GET 200, POST 201, PUT 200, DELETE 200, 404 cuando no se encuentra, 400 por conflictos.
# -------------------------------------------
from fastapi import APIRouter
from back.models.users import UserIn, UserOut
from back.domain.users.create import create_user

router = APIRouter()

@router.post("/api/v1/users", response_model=UserOut)
def create_user_endpoint(user: UserIn):
    new_user = create_user(user, created_by="system")
    return new_user