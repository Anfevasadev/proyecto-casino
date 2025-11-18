# back/domain/machines/create.py

from fastapi import HTTPException, status
from typing import Dict, Any, Callable
from datetime import datetime
from back.models.machines import MachineIn, MachineOut # Usamos MachineIn para validación
from decimal import Decimal

# La función create_machine ahora recibe sus dependencias como argumentos
def create_machine(
    data: MachineIn,
    clock: Callable[[], datetime], # Función que retorna la hora actual
    machines_repo: Any,          # Repositorio de Máquinas
    places_repo: Any,            # Repositorio de Places
    actor: str                   # Usuario que realiza la operación
    ) -> MachineOut:
    """
    Crea una nueva máquina si cumple con todas las reglas de negocio, 
    gestionando la Inyección de Dependencias (repositorios, clock, actor).
    """
    
    # 1. Validación de Unicidad
    # Usamos el code normalizado por Pydantic
    if machines_repo.existe_code(data.code):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict: Recurso duplicado
            detail=f"El código de máquina '{data.code}' ya está en uso."
        )

    # 2. Validación Cruzada: Existencia y Actividad del Place
    place = places_repo.obtener_por_id(data.place_id)
    
    if place is None:
        # place_id no existe. (Simula NotFoundError)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El lugar con ID {data.place_id} no existe."
        )
    
    if place['is_active'] is False:
        # Place existe, pero está inactivo. (Simula DomainError/Forbidden)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No se pueden crear máquinas en el lugar con ID {data.place_id} porque está inactivo."
        )
        
    # 3. Preparar Fila y Auditoría
    
    # Obtener la hora actual
    current_time_str = clock().strftime('%Y-%m-%d %H:%M:%S')
    
    # Convertir el modelo de entrada a diccionario base
    machine_dict = data.model_dump()
    
    # 4. Construir fila completa con auditoría
    # Nota: El repositorio machines_repo.insertar_fila se encarga de generar el 'id'.
    new_row = {
        # Campos de MachineIn
        **machine_dict, 
        
        # Campos de estado y auditoría
        'is_deleted': False,
        'created_at': current_time_str,
        'created_by': actor,
        'updated_at': current_time_str,
        'updated_by': actor,
        'deleted_at': None,
        'deleted_by': None
    }
    
    # 5. Inserción en el Repositorio
    try:
        # El repositorio genera el ID (next_id) y persiste el cambio en el CSV
        inserted_row = machines_repo.insertar_fila(new_row)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar la máquina: {e}"
        )
    
    # 6. Retorno (Usamos Pydantic para validar y formatear la salida)
    # Retorna solo los campos públicos definidos en MachineOut.
    return MachineOut.model_validate(inserted_row)