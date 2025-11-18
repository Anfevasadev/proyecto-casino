# -------------------------------------------
# back/domain/machines/read.py
# Funciones esperadas:
#   - listar_machines(machines_repo, place_id=None, only_active=True, limit=50, offset=0, sort_by="id")
#   - obtener_machine(machines_repo, machine_id)

# back/domain/machines/read.py

from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any, Union
from back.models.machines import MachineOut

# Campos permitidos para la ordenación
ALLOWED_SORT_FIELDS = ["id", "code"]
# Campos públicos requeridos por la especificación (sin auditoría)
PUBLIC_FIELDS_LIST = [
    'id', 'code', 'denomination_value', 'place_id', 
    'participation_rate', 'is_active', 
]


def obtener_machine(machines_repo: Any, machine_id: int) -> MachineOut:
    """
    Busca una máquina por su ID. Lanza 404 si no la encuentra.
    """
    
    # Llama al método de repositorio que excluye borrado lógico
    machine_row = machines_repo.obtener_por_id(machine_id)
    
    if machine_row is None:
        # Si no existe o está borrada lógicamente, lanzamos 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Máquina con ID {machine_id} no encontrada."
        )
        
    # El repositorio devuelve el diccionario completo. 
    # Usamos Pydantic para validar, formatear y devolver solo los campos de MachineOut.
    return MachineOut.model_validate(machine_row)

def listar_machines(
    machines_repo: Any, # El repositorio (machines_repo.py)
    place_id: Optional[int] = None, 
    only_active: bool = True,
    limit: int = 50, # Usando el default de 50
    offset: int = 0,
    sort_by: str = "id"
) -> List[Dict[str, Any]]:
    """
    Lista máquinas, aplicando filtros, ordenamiento y paginación.
    Retorna solo un dict con los campos públicos.
    """
    
    # 1. Validar el campo de ordenamiento
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campo de ordenamiento '{sort_by}' no permitido. Use: {', '.join(ALLOWED_SORT_FIELDS)}."
        )

    # 2. Obtener las filas desde el repositorio con los filtros aplicados
    machine_rows = machines_repo.listar(
        place_id=place_id,
        only_active=only_active,
        limit=limit,
        offset=offset
    )
    
    # --- Procesamiento Adicional de Dominio (Si el Repo no ordena) ---
    
    if not machine_rows:
        return []
        
    try:
        machine_rows.sort(key=lambda x: x.get(sort_by), reverse=False) 
    except TypeError:
        pass
    
    
    # 3. Formatear la Salida para incluir solo los campos públicos
    
    final_output = []
    for row in machine_rows:
        public_data = {field: row.get(field) for field in PUBLIC_FIELDS_LIST}
        final_output.append(public_data)

    return final_output