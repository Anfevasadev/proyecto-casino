# back/domain/machines/update.py

from fastapi import HTTPException, status
from typing import Any, Callable, Dict, Union
from datetime import datetime
from back.models.machines import MachineUpdate, MachineOut

def actualizar_machine(
    machine_id: int,
    cambios: MachineUpdate,
    clock: Callable[[], datetime],
    machines_repo: Any,
    places_repo: Any,
    actor: str
) -> MachineOut:
    """
    Actualiza campos de una máquina, aplicando validaciones de unicidad y place.
    """
    
    # Obtener solo los campos que tienen un valor (excluir None)
    update_data = cambios.model_dump(exclude_none=True)

    # 1. Verificar existencia de la máquina (y asegurar que no esté borrada lógicamente)
    current_machine = machines_repo.obtener_por_id(machine_id)
    if current_machine is None:
        # machine_id inexistente o borrado lógicamente
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Máquina con ID {machine_id} no encontrada."
        )

    # Si no hay cambios reales que aplicar después de excluir None
    if not update_data:
        return MachineOut.model_validate(current_machine)

    # 2. Validar Unicidad de Código (si el código está siendo modificado)
    if 'code' in update_data:
        new_code = update_data['code'] # El código ya está normalizado (UPPER/strip) por Pydantic
        
        # Validar si el nuevo código ya existe en OTRA máquina (excluyendo la máquina actual)
        if machines_repo.existe_code(new_code, exclude_id=machine_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El código de máquina '{new_code}' ya está en uso por otra máquina."
            )

    # 3. Validar Place (si el place_id está siendo modificado)
    if 'place_id' in update_data:
        place_id = update_data['place_id']
        place = places_repo.obtener_por_id(place_id)
        
        # Validación 1: Existencia
        if place is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El lugar con ID {place_id} referenciado no existe."
            )
        
        # Validación 2: Estado Activo
        if place['is_active'] is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No se puede mover la máquina al lugar con ID {place_id} porque está inactivo."
            )

    # 4. Añadir Auditoría
    # Estos campos se añaden al diccionario de cambios antes de pasarlo al repositorio
    update_data['updated_at'] = clock().strftime('%Y-%m-%d %H:%M:%S')
    update_data['updated_by'] = actor

    # 5. Aplicar cambios en el repositorio
    # machines_repo.actualizar_fila retorna None si falla, pero ya validamos existencia.
    updated_row = machines_repo.actualizar_fila(machine_id, update_data)
    
    # 6. Retorno
    return MachineOut.model_validate(updated_row)