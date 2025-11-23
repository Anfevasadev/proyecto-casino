# -------------------------------------------
# back/api/v1/machines.py
# Propósito:
#   Endpoints para gestionar "máquinas" (por lugar) en CSV.
#
# Router esperado:
#   - Variable "router" = APIRouter()
#
# Modelos (importar de back/models/machines.py):
#   - MachineIn: code, denomination_value, place_id, participation_rate, is_active.
#   - MachineOut: id, code, denomination_value, place_id, participation_rate, is_active.
#
# Dependencias:
#   - get_repos() para acceder a machines_repo (y places_repo si se valida FK).
#   - pagination_params() para listar.
#   - filter_active_param() (bool) para traer solo activas si se desea.
#
# Endpoints (sugeridos):
#   1) GET /
#      - Query:
#           * place_id (int, opcional) para filtrar por lugar.
#           * only_active (bool=true), limit, offset.
#      - Procesamiento: leer máquinas, aplicar filtros y paginación.
#      - Salida (200): lista MachineOut.
#
#   2) GET /{machine_id}
#      - Path: machine_id (int).
#      - Procesamiento: obtener por id o 404.
#      - Salida (200): MachineOut.
#
#   3) POST /
#      - Body: MachineIn.
#      - Validaciones:
#           * code no repetido (único).
#           * place_id existente en places (FK lógica).
#           * participation_rate ∈ [0,1].
#           * denomination_value >= 0.
#      - Procesamiento: asignar id, guardar máquina.
#      - Salida (201): MachineOut.
#      - Errores: 400 (duplicado/valores inválidos), 404 (place_id inexistente).
#
#   4) PUT /{machine_id}
#      - Body: campos editables (code, denomination_value, place_id, participation_rate, is_active).
#      - Validaciones:
#           * machine_id existente.
#           * si cambia code, no duplicar.
#           * si cambia place_id, debe existir.
#           * participation_rate ∈ [0,1], denomination_value >= 0.
#      - Procesamiento: actualizar fila y guardar.
#      - Salida (200): MachineOut actualizada.
#      - Errores: 404/400.
#
#   5) DELETE /{machine_id}
#      - Borrado lógico:
#         * En machines NO hay is_deleted, solo is_active.
#         * "Eliminar" = is_active=false.
#      - Validaciones: machine_id existente.
#      - Procesamiento: marcar is_active=false.
#      - Salida (200): {"deleted": true, "id": <machine_id>}
#
# Reglas adicionales relevantes:
#   - Si el lugar (place_id) está inactivo, no permitir crear nuevas máquinas en ese lugar.
#   - Para listados, podría ofrecer "sort_by" (code asc/desc) si se desea (opcional).
#
# Librerías:
#   - fastapi (APIRouter, HTTPException, Query, status)
#   - pydantic (modelos)
#
# Notas:
#   - El manejo de CSV/pandas se hace en storage/machines_repo.py. Aquí solo orquestamos.
#   - El borrado lógico es un "toggle" de is_active a false; no se elimina la fila.
# -------------------------------------------
# back/api/v1/machines.py
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List

# Definición del esquema de entrada (request body)
class MachineIn(BaseModel):
    marca: str
    modelo: str
    serial: str
    asset: str
    place_id: int
    denominacion: int
    is_active: bool

# Definición del esquema de salida (response)
class MachineOut(BaseModel):
    id: int
    marca: str
    modelo: str
    serial: str
    asset: str
    denominacion: int
    estado: bool
    casino_id: int

# Router de máquinas
router = APIRouter()

# Lista simulada de máquinas (en memoria)
machines_db = []
machine_counter = 1

@router.post("/", response_model=MachineOut, status_code=201)
def registrar_maquina_endpoint(machine: MachineIn, actor: str = "system"):
    """
    Endpoint para registrar una máquina.
    Retorna un objeto simulado sin usar repositorios de casinos aún.
    """
    global machine_counter
    new_machine = MachineOut(
        id=machine_counter,
        marca=machine.marca,
        modelo=machine.modelo,
        serial=machine.serial,
        asset=machine.asset,
        denominacion=machine.denominacion,
        estado=machine.is_active,
        casino_id=machine.place_id  # usar place_id como casino_id temporal
    )
    machines_db.append(new_machine)
    machine_counter += 1
    return new_machine

@router.get("/", response_model=List[MachineOut])
def listar_maquinas(only_active: bool = Query(True, description="Solo máquinas activas")):
    """
    Endpoint para listar todas las máquinas registradas.
    """
    if only_active:
        return [m for m in machines_db if m.estado]
    return machines_db

@router.get("/{machine_id}", response_model=MachineOut)
def obtener_maquina_por_id(machine_id: int):
    """
    Endpoint para obtener una máquina por su ID.
    """
    for m in machines_db:
        if m.id == machine_id:
            return m
    return {"id": 0, "marca": "", "modelo": "", "serial": "", "asset": "", "denominacion": 0, "estado": False, "casino_id": 0}
