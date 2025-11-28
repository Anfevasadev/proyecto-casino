# -------------------------------------------
# back/api/v1/places.py
# Propósito:
#   Endpoints para gestionar "lugares" (casinos/salas) en CSV.
#
# Router esperado:
#   - Variable "router" = APIRouter()
#
# Modelos (importar de back/models/places.py):
#   - PlaceIn: name, address, is_active (por defecto true).
#   - PlaceOut: id, name, address, is_active.
#
# Dependencias:
#   - get_repos() para acceder a places_repo.
#   - pagination_params(), filter_active_param() (opcional).
#
# Endpoints (sugeridos):
#   1) GET /
#      - Query: limit (int), offset (int), only_active (bool=true).
#      - Procesamiento: listar lugares, filtrar activos, paginar.
#      - Salida (200): lista PlaceOut.
#
#   2) GET /{place_id}
#      - Path: place_id (int).
#      - Procesamiento: obtener lugar por id o 404.
#      - Salida (200): PlaceOut.
#
#   3) POST /
#      - Body: PlaceIn.
#      - Validaciones:
#         * name no repetido.
#      - Procesamiento: asignar id, guardar.
#      - Salida (201): PlaceOut.
#      - Errores: 400 si nombre duplicado.
#
#   4) PUT /{place_id}
#      - Body: campos editables (name, address, is_active).
#      - Validaciones: que place_id exista; no duplicar name.
#      - Procesamiento: actualizar fila.
#      - Salida (200): PlaceOut actualizado.
#      - Errores: 404/400.
#
#   5) DELETE /{place_id}
#      - Borrado lógico:
#         * Política del proyecto: en places NO hay is_deleted, solo is_active.
#         * "Eliminar" = is_active=false (no borrar la fila).
#      - Validaciones: place_id existente.
#      - Procesamiento: marcar is_active=false.
#      - Salida (200): {"deleted": true, "id": <place_id>}
#
# Reglas adicionales:
#   - Si un lugar se desactiva (is_active=false), considerar (a nivel de dominio)
#     bloquear creación de nuevas máquinas asociadas (machines.place_id).
#     Esta comprobación NO va aquí; va en la capa domain/ o en repos.
#
# Librerías:
#   - fastapi (APIRouter, HTTPException, status)
#   - pydantic (modelos)
# -------------------------------------------

from fastapi import APIRouter, HTTPException
from back.models.places import PlaceUpdate
from back.domain.places.create import PlaceDomain
from back.domain.places.management import CasinoManagement
from back.storage.places_repo import PlaceStorage
from back.models.places import PlaceIn, PlaceOut
from back.api.deps import verificar_rol
from fastapi import Depends

router = APIRouter()

# --------------------------------------
# INACTIVAR CASINO
# --------------------------------------
@router.put("/casino/{casino_id}/inactivar")
def inactivar_casino(
	casino_id: int,
	actor: str = "system",
	user=Depends(verificar_rol(["admin","soporte"]))
):
    """
    Marca un casino como inactivo usando la capa de dominio.
    """
    try:
        PlaceDomain.inactivar_casino(casino_id, actor)
        return {
            "mensaje": "Casino inactivado correctamente",
            "id": casino_id,
            "actor": actor
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Casino no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------
# Activar CASINO
# --------------------------------------
@router.put("/casino/{casino_id}/activar")
def activar_casino(
	casino_id: int,
	actor: str = "system",
	user=Depends(verificar_rol(["admin","soporte"]))
):
    """
    Marca un casino como activo usando la capa de storage
    """
    try:
        PlaceDomain.activar_casino(casino_id, actor)
        return {
            "mensaje": "Casino activado correctamente",
            "id": casino_id,
            "actor": actor
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Casino no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------
# CREAR CASINO
# --------------------------------------
@router.post("/casino", response_model=PlaceOut)
def crear_casino(
	place: PlaceIn,
	actor: str = "system",
	user=Depends(verificar_rol(["admin","soporte"]))
):
    """
    Crea un nuevo casino usando la capa de dominio.
    """
    try:
        created = PlaceDomain.create_place(place, created_by=actor)
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------
# LISTAR CASINOS
# --------------------------------------
@router.get("/casino")
def listar_casinos(only_active: bool = True, limit: int | None = None, offset: int = 0):
    try:
        places = PlaceStorage.listar(only_active=only_active, limit=limit, offset=offset)
        return places
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------
# MODIFICAR CASINO
# --------------------------------------
@router.put("/casino/{casino_id}")
def modificar_casino(
	casino_id: int,
	body: PlaceUpdate,
	actor: str = "system",
	user=Depends(verificar_rol(["admin","soporte"]))
):
    """Actualiza campos editables de un casino (no permite cambiar el código)."""
    try:
        cambios = body.model_dump(exclude_unset=True)
        updated = PlaceDomain.update_place(casino_id, cambios, actor=actor)
        return updated
    except KeyError:
        raise HTTPException(status_code=404, detail="Casino no encontrado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------
# LISTAR MÁQUINAS DE UN CASINO
# --------------------------------------
@router.get("/casino/{casino_id}/maquinas")
def listar_maquinas_casino(casino_id: int, only_active: bool = True):
    try:
        machines = CasinoManagement.listar_maquinas(casino_id, only_active=only_active)
        return machines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
