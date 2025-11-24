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
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, status
from back.models.users import UserIn, UserOut, UserUpdate
from back.domain.users.create import create_user
from back.domain.users.update import NotFoundError, update_user

from back.storage import users_repo as repo



router = APIRouter()

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: UserIn):
    try:
        new_user = create_user(user, created_by="system")
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def _clock_local() -> str:
	# Formato local sencillo; README menciona YYYY-MM-DD HH:MM:SS
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@router.put("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def put_user(
	user_id: int = Path(..., ge=1),
	body: UserUpdate | None = None,
):
	if body is None:
		body = UserUpdate()

	try:
		updated = update_user(
			user_id=user_id,
			cambios=body.model_dump(exclude_unset=True),
			clock=_clock_local,
			repo=repo,
			actor="api",
		)
		return UserOut(**updated)
	except NotFoundError as e:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
