from back.models.machines import MachineUpdate, MachineOut
from typing import Any, Callable, Dict
from datetime import datetime
from fastapi import HTTPException, status

def actualizar_machine(
    machine_id: int,
    cambios: MachineUpdate,
    clock: Callable[[], datetime],
    machines_repo: Any,    # Instancia de MachinesRepo
    places_repo: Any,      # Repositorio de Places
    actor: str
) -> MachineOut:
    
    # 1. Obtener datos de la máquina actual (Validación de Existencia)
    maquina_actual = machines_repo.get_by_id(machine_id)
    if not maquina_actual:
        # Lanza 404 Not Found si la máquina no existe
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Máquina con ID {machine_id} no encontrada."
        )

    # Convertir el modelo de cambios a un diccionario, excluyendo campos no proporcionados
    datos_actualizados = cambios.model_dump(exclude_none=True)

    # Si no hay cambios reales que aplicar
    if not datos_actualizados:
        # Devuelve el estado actual de la máquina si no se enviaron campos
        return MachineOut(**maquina_actual)

    # Denominacion no puede cambiarse así que acá lo validamos y ponemos un error en caso de que intenten cambiarla
    if 'denominacion' in datos_actualizados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La denominación (denominacion) de la máquina no puede ser modificada."
        )

    # 2. Validación de Unicidad (Serial o Asset)
    cambio_serial = datos_actualizados.get('serial')
    cambio_asset = datos_actualizados.get('asset')
    
    if cambio_serial or cambio_asset:
        
        serial_nuevo = cambio_serial or maquina_actual.get('serial')
        asset_nuevo = cambio_asset or maquina_actual.get('asset')
        
        if machines_repo.existe_serial_o_asset(serial_nuevo, asset_nuevo, exclude_id=machine_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El Serial o Asset ya están registrados en otra máquina."
            )

    # 3. Validación de Casino/Place 
    if 'place_id' in datos_actualizados:
        nuevo_place_id = datos_actualizados['place_id']
        casino = places_repo.get_by_id(nuevo_place_id)
        
        # Validación de existencia (404)
        if not casino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Casino con ID {nuevo_place_id} no encontrado."
            )
        
        # Validación de inactivo (403)
        if str(casino.get('is_active', 'False')).lower() == 'false':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No se puede reasignar la máquina al Casino ID {nuevo_place_id} porque está inactivo."
            )

    # 4. Aplicar Cambios y Auditoría
    updated_row = machines_repo.update(
        machine_id=machine_id, 
        cambios=datos_actualizados, 
        actor=actor,
        timestamp=clock() # Pasamos el timestamp para auditoría
    )
    
    # 5. Retorno
    return MachineOut(**updated_row)