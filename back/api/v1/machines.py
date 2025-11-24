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
# back/api/v1/machines.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from back.models.machines import MachineIn, MachineOut
from back.storage.machines_repo import MachinesRepo
from back.storage.places_repo import PlaceStorage
from back.domain.machines.inativation import inactivar_maquina_por_serial
from back.domain.machines.activation import activar_maquina_por_serial

repo = MachinesRepo()
repo_places = PlaceStorage()
router = APIRouter()


class SerialAction(BaseModel):
    serial: str
    actor: Optional[str] = "system"
    motivo: Optional[str] = None

@router.post("/", response_model=MachineOut, status_code=201)
def registrar_maquina(machine: MachineIn, actor: str = "system"):
    # Validar unicidad de serial
    if repo.existe_serial(machine.serial):
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una máquina con el serial '{machine.serial}'"
        )
    
    # Validar unicidad de asset
    if repo.existe_asset(machine.asset):
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una máquina con el asset '{machine.asset}'"
        )
    
    # Validar que el casino (place_id) exista
    if machine.place_id is not None:
        casino = repo_places.obtener_por_id(machine.place_id)
        if casino is None:
            raise HTTPException(
                status_code=404,
                detail=f"Casino con id {machine.place_id} no encontrado"
            )
        # Validar que el casino esté activo
        estado = casino.get("estado")
        if estado is not None and str(estado).lower() == "false":
            raise HTTPException(
                status_code=400,
                detail=f"Casino con id {machine.place_id} está inactivo"
            )
    
    new_id = repo.next_id()

    row = {
        "id": new_id,
        "marca": machine.marca,
        "modelo": machine.modelo,
        "serial": machine.serial,
        "asset": machine.asset,
        "denominacion": machine.denominacion,
        "estado": str(machine.is_active),
        "casino_id": machine.place_id
    }

    repo.add(row, actor)

    return MachineOut(
        id=new_id,
        marca=machine.marca,
        modelo=machine.modelo,
        serial=machine.serial,
        asset=machine.asset,
        denominacion=machine.denominacion,
        estado=machine.is_active,
        casino_id=machine.place_id
    )


@router.get("/", response_model=List[MachineOut])
def listar_maquinas(only_active: Optional[bool] = Query(None)):
    data = repo.list_all()

    if only_active is not None:
        data = [m for m in data if str(m.get("is_active", "True")).lower() == str(only_active).lower()]

    return [
        MachineOut(
            id=int(m["id"]),
            marca=m["marca"],
            modelo=m["modelo"],
            serial=m["serial"],
            asset=m["asset"],
            denominacion=m["denominacion"],
            estado=str(m.get("estado", "True")).lower() == "true",
            casino_id=int(m["casino_id"])
        )
        for m in data
    ]


@router.get("/{machine_id}", response_model=MachineOut)
def obtener_maquina(machine_id: int):
    m = repo.get_by_id(machine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")

    return MachineOut(
        id=int(m["id"]),
        marca=m["marca"],
        modelo=m["modelo"],
        serial=m["serial"],
        asset=m["asset"],
        denominacion=m["denominacion"],
        estado=str(m["estado"]).lower() == "true",
        casino_id=int(m["casino_id"])
    )


@router.post("/inactivate")
def inactivate_machine(payload: SerialAction):
    try:
        result = inactivar_maquina_por_serial(
            payload.serial, actor=payload.actor or "system", motivo=payload.motivo
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/activate")
def activate_machine(payload: SerialAction):
    try:
        result = activar_maquina_por_serial(payload.serial, actor=payload.actor or "system", note=payload.motivo)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
