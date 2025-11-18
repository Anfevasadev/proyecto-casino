# back/domain/machines/delete.py

from fastapi import HTTPException, status
from typing import Any, Callable, Dict, Union
from datetime import datetime

def desactivar_machine(
    machine_id: int, 
    clock: Callable[[], datetime], # Inyección de la función de tiempo
    machines_repo: Any,          # Inyección del repositorio de máquinas
    actor: str                   # Inyección del usuario que realiza la acción
) -> Dict[str, Union[bool, int]]:
    """
    ¿Cómo lo hace?
    1. Llama al repo para cambiar is_active=False y actualizar auditoría.
    2. Lanza 404 si el repo indica que el ID no existe.
    3. Retorna la estructura de salida requerida.
    """
    
    # 1. Llamar al repositorio para realizar la desactivación
    # El repositorio (machines_repo.desactivar) retorna True si la operación fue exitosa.
    success = machines_repo.desactivar(
        machine_id=machine_id, 
        clock=clock, 
        actor=actor
    )
    
    if not success:
        # Si el repositorio retorna False, la máquina no fue encontrada.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Máquina con ID {machine_id} no encontrada."
        )
        
    # 2. Retornar la estructura de salida requerida
    return {"deleted": True, "id": machine_id}