# back/api/v1/machines.py

from fastapi import APIRouter, status, Query
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# Importaciones de Modelos (Pydantic)
from back.models.machines import MachineIn, MachineOut, MachineUpdate 
from back.models.machines import MachineOut as MachinePublicOut # Alias para la salida pública si es necesario

# Importaciones de Dominios (Lógica de Negocio)
from back.domain.machines.create import create_machine
from back.domain.machines.read import listar_machines, obtener_machine
from back.domain.machines.update import actualizar_machine
from back.domain.machines.delete import desactivar_machine

# Importaciones de Repositorios (Inyección de Dependencia)
from back.storage import machines_repo
from back.storage import places_repo

# Función de reloj inyectable (simulación de hora local)
def local_clock() -> datetime:
    return datetime.now()

# Usuario para auditoría (Hardcodeado para el proyecto)
ACTOR_USERNAME = "VelasquezDev" 

# --- Router Principal ---
router = APIRouter()

# POST (Crear Maquina)

@router.post(
    "/machines", 
    response_model=MachineOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una nueva máquina de juego"
)
async def create_new_machine(machine_data: MachineIn):
    """
    Recibe los datos de una nueva máquina y aplica las validaciones de unicidad y Place activo.
    """
    # Orquestación: Inyección de todas las dependencias
    return create_machine(
        data=machine_data, 
        clock=local_clock,       # Inyección de la hora
        machines_repo=machines_repo, # Inyección del repositorio de máquinas
        places_repo=places_repo,     # Inyección del repositorio de places
        actor=ACTOR_USERNAME         # Inyección del actor
    )

# GET (Listar Máquinas)

@router.get(
    "/machines",
    # La salida es una LISTA de diccionarios (campos públicos)
    response_model=List[Dict[str, Any]], 
    status_code=status.HTTP_200_OK,
    summary="Lista máquinas con filtros, ordenamiento y paginación"
)
async def list_machines(
    place_id: Optional[int] = Query(None, description="Filtra por ID del lugar."),
    # Renombramos 'active' para que sea más claro en el endpoint
    active: bool = Query(True, description="Si es True, solo devuelve máquinas activas."), 
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados (máx 100)."),
    offset: int = Query(0, ge=0, description="Número de registros a saltar."),
    sort_by: str = Query("id", description="Campo para ordenar (id o code).")
):
    """
    Permite obtener una lista paginada y filtrada de máquinas.
    """
    return listar_machines(
        machines_repo=machines_repo, # Inyección del repositorio
        place_id=place_id,
        only_active=active,
        limit=limit,
        offset=offset,
        sort_by=sort_by
    )


# GET /{machine_id} (Obtener Máquina por ID)

@router.get(
    "/machines/{machine_id}",
    response_model=MachineOut,
    status_code=status.HTTP_200_OK,
    summary="Obtiene una máquina por su ID"
)
async def get_machine(machine_id: int):
    """
    Obtiene los detalles de una máquina específica por su ID.
    Retorna 404 si la máquina no existe o está borrada lógicamente.
    """
    return obtener_machine(
        machines_repo=machines_repo, # Inyección del repositorio
        machine_id=machine_id
    )


# PUT /{machine_id} (Actualizar Máquina)

@router.put(
    "/machines/{machine_id}",
    response_model=MachineOut,
    status_code=status.HTTP_200_OK,
    summary="Actualiza una máquina existente"
)
async def update_machine_endpoint(machine_id: int, changes: MachineUpdate):
    """
    Actualiza una máquina por ID. Solo los campos incluidos en el cuerpo serán modificados.
    """
    return actualizar_machine(
        machine_id=machine_id,
        cambios=changes,
        clock=local_clock,             # Inyección del reloj
        machines_repo=machines_repo,   # Inyección del repositorio de máquinas
        places_repo=places_repo,       # Inyección del repositorio de places
        actor=ACTOR_USERNAME           # Inyección del actor
    )


# DELETE /{machine_id} (Desactivar Máquina)

@router.delete(
    "/machines/{machine_id}",
    status_code=status.HTTP_200_OK,
    # Salida estricta de la especificación: {"deleted": true, "id": <machine_id>}
    response_model=Dict[str, Union[bool, int]], 
    summary="Desactiva (Borrado Lógico) una máquina"
)
async def delete_machine(machine_id: int):
    """
    Realiza el borrado lógico de la máquina (establece is_active=False).
    """
    # Llama a la lógica de dominio inyectando las dependencias
    return desactivar_machine(
        machine_id=machine_id, 
        clock=local_clock,       # Inyección del reloj
        machines_repo=machines_repo, # Inyección del repositorio
        actor=ACTOR_USERNAME     # Inyección del actor
    )