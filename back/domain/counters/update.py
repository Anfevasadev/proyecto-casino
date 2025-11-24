# back/domain/counters/update.py

from typing import Callable, List, Any
from datetime import date, datetime
from fastapi import HTTPException, status

from back.models.counters import CounterUpdateBatch, CounterOut

def modificar_contadores_batch(
    casino_id: int,
    fecha: date,
    batch_data: CounterUpdateBatch,
    counters_repo: Any,
    places_repo: Any,
    clock: Callable[[], datetime],
    actor: str
) -> List[CounterOut]:
    """
    Validaciones:
    - El Casino debe existir y estar activo.
    - Deben existir registros para actualizar en esa fecha.
    """

    # 1. Validar Casino (Existencia y Estado)
    casino = places_repo.obtener_por_id(casino_id)
    
    if not casino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Casino con ID {casino_id} no encontrado."
        )

    # Validamos si está activo (el repo devuelve True/False en 'estado')
    if casino.get('estado', False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"El Casino {casino.get('nombre')} está inactivo. No se pueden modificar registros."
        )

    # 2. Preparar datos para el Repositorio
    # Convertimos la fecha date a string 'YYYY-MM-DD'
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    # exclude_none=True solo envia al repo los campos que SÍ cambiaron.
    updates_list = [u.dict(exclude_none=True) for u in batch_data.updates]

    # 3. Ejecutar Actualización
    updated_rows = counters_repo.update_batch(
        casino_id=casino_id,
        fecha_filtro=fecha_str,
        updates=updates_list,
        actor=actor,
        timestamp=clock()
    )

    # 4. Validar Resultado
    if not updated_rows:
        # Si la lista está vacía, significa que no hubo coincidencias de fecha/casino/máquina
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron registros coincidentes para actualizar en el Casino {casino_id} el día {fecha_str}."
        )

    # 5. Convertir diccionarios a Modelos de Salida (CounterOut)
    return [CounterOut(**row) for row in updated_rows]