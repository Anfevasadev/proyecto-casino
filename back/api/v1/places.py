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

from fastapi import APIRouter, HTTPException, status
from back.models.place_models import CasinoIn, CasinoOut
from back.domain.place_domain import Casino


# Crear router
router = APIRouter(
    prefix="/places",
    tags=["Places - Casinos"]
)


@router.post(
    "/",
    response_model=CasinoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo casino",
    description="""
    Crea un nuevo casino en el sistema.
    
    **Campos obligatorios según UML:**
    - nombre: Denominación oficial del casino (3-100 caracteres)
    - direccion: Ubicación física completa (10-200 caracteres)
    - codigoCasino: Identificador único (3-20 caracteres, alfanumérico)
    
    **Validaciones:**
    - El codigoCasino debe ser único
    - Todos los campos son obligatorios
    - El código se convierte automáticamente a mayúsculas
    """
)
def crearCasino(casino: CasinoIn):
    """
    Endpoint que llama al método crearCasino() del UML
    
    Args:
        casino: Datos del casino a crear
        
    Returns:
        CasinoOut: Casino creado con ID asignado
        
    Raises:
        400: Si el código ya existe o hay errores de validación
        500: Error interno del servidor
    """
    try:
        # Llamar al método crearCasino() según UML
        nuevo_casino = Casino.crearCasino(
            casino_data=casino,
            created_by="system"  # TODO: Obtener usuario autenticado
        )
        
        return nuevo_casino
        
    except ValueError as e:
        # Error de validación (código duplicado, etc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el casino: {str(e)}"
        )
