# back/domain/counters/read.py

from typing import List, Any, Optional
from datetime import date
from fastapi import HTTPException, status

from back.models.counters import CounterOut

def consultar_contadores_reporte(
    casino_id: int,
    start_date: date,
    end_date: date,
    counters_repo: Any
) -> List[CounterOut]:
    """
    Obtiene los registros de contadores filtrados para el Módulo de Reportes.
    
    Reglas:
    - start_date no puede ser mayor que end_date.
    """

    # 1. Validación lógica de fechas
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de inicio no puede ser posterior a la fecha de fin."
        )

    # 2. Convertir fechas a string para el repositorio
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # 3. Llamar al repositorio
    rows = counters_repo.list_by_casino_date(
        casino_id=casino_id,
        fecha_inicio=start_str,
        fecha_fin=end_str
    )

    # 4. Retornar modelos
    return [CounterOut(**row) for row in rows]


def obtener_contador_por_id(
    counter_id: int,
    counters_repo: Any
) -> CounterOut:
    """Obtiene un solo contador por su ID."""
    
    row = counters_repo.get_by_id(counter_id)
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contador con ID {counter_id} no encontrado."
        )
        
    return CounterOut(**row)