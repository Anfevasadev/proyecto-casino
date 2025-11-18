# -------------------------------------------
# back/storage/places_repo.py
# Propósito:
#   - CRUD para data/places.csv.
#
# CSV (encabezado esperado):
#   id,name,address,is_active,created_at,created_by,updated_at,updated_by

import pandas as pd
import os
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime

PLACES_DATA_PATH = "data/places.csv"
DATA_DIRECTORY = "data"

# Campos públicos para listar la salida
PUBLIC_FIELDS = ['id', 'name', 'address', 'is_active', 'created_at', 'created_by', 'updated_at', 'updated_by']

def _load_places_dataframe() -> Optional[pd.DataFrame]:
    """Carga el DataFrame de lugares desde el CSV, o crea un esqueleto si no existe."""
    if not os.path.exists(PLACES_DATA_PATH):
        COLUMNS = ['id', 'name', 'address', 'is_active', 'created_at', 'created_by', 'updated_at', 'updated_by']
        os.makedirs(DATA_DIRECTORY, exist_ok=True)
        # Retornar un DataFrame vacío pero con las columnas correctas
        return pd.DataFrame(columns=COLUMNS)
    
    try:
        df = pd.read_csv(PLACES_DATA_PATH)
        # Aseguramos la conversión del estado booleano
        if 'is_active' in df.columns:
             df['is_active'] = df['is_active'].astype(str).str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        return df
    except Exception as e:
        print(f"Error al cargar el repositorio de places: {e}")
        return None

def _save_places_dataframe(df: pd.DataFrame) -> None:
    """Guarda el DataFrame actualizado en el archivo CSV."""
    # Asegurarse de que los valores booleanos se escriban como 'True'/'False'
    if 'is_active' in df.columns:
        df['is_active'] = df['is_active'].astype(str)
    
    df.to_csv(PLACES_DATA_PATH, index=False)

# Funciones sugeridas:
#   1) listar(only_active: bool = True, limit: int | None = None, offset: int = 0) -> list[dict]
#      - Devuelve lugares como lista de dicts (campos: id, name, address, is_active).

def listar(
    only_active: bool = True, 
    limit: Optional[int] = None, 
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Lista lugares, aplicando filtros de actividad y paginación."""
    df = _load_places_dataframe()
    if df is None or df.empty:
        return []

    df_filtered = df.copy()

    # 1. Filtro por is_active
    if only_active and 'is_active' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['is_active'] == True]

    # 2. Paginación
    start_index = offset
    end_index = offset + limit if limit is not None else len(df_filtered)
    df_paginated = df_filtered.iloc[start_index:end_index]
    
    # Seleccionar solo campos públicos
    cols_to_return = [col for col in PUBLIC_FIELDS if col in df_paginated.columns]
    
    return df_paginated[cols_to_return].to_dict('records')

#
#   2) obtener_por_id(place_id: int) -> dict | None
#      - Fila por id o None.

def obtener_por_id(place_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un lugar por su ID."""
    df = _load_places_dataframe()
    if df is None or df.empty:
        return None
        
    place_data = df[df['id'] == place_id]
    
    if not place_data.empty:
        return place_data.iloc[0].to_dict()
    
    return None

#
#   3) existe_name(name: str, exclude_id: int | None = None) -> bool
#      - Verifica duplicados de name (case-insensitive si se decide).

def existe_name(name: str, exclude_id: Optional[int] = None) -> bool:
    """Verifica la unicidad de 'name', excluyendo un ID si es para actualización."""
    df = _load_places_dataframe()
    if df is None or df.empty:
        return False
        
    normalized_name = name.strip().lower()
    
    # Filtra por el nombre normalizado (insensible a mayúsculas/minúsculas)
    df_filtered = df[df['name'].astype(str).str.lower() == normalized_name].copy()
    
    # Excluir el ID si se proporciona (caso de actualización)
    if exclude_id is not None:
        df_filtered = df_filtered[df_filtered['id'] != exclude_id]
        
    return not df_filtered.empty

#   4) insertar_fila(row: dict) -> None
#      - Concatena y escribe CSV (asegurando columnas).

def insertar_fila(row: Dict[str, Any]) -> Dict[str, Any]:
    """Inserta una nueva fila de lugar, generando el ID y guardando en CSV."""
    df = _load_places_dataframe()
    if df is None:
        raise RuntimeError("No se pudo cargar el repositorio de places para insertar.")
        
    # Generar nuevo ID: Usar el máximo ID existente + 1, o empezar en 1
    new_id = df['id'].max() + 1 if not df.empty and 'id' in df.columns else 1
    
    new_row_df = pd.DataFrame([{**row, 'id': new_id}])
        
    df_updated = pd.concat([df, new_row_df], ignore_index=True)
    _save_places_dataframe(df_updated)
    
    return df_updated[df_updated['id'] == new_id].iloc[0].to_dict()

#   5) actualizar_fila(place_id: int, cambios: dict) -> dict | None
#      - Aplica cambios; retorna fila resultante o None si no existe.

def actualizar_fila(place_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Aplica cambios a un lugar existente y actualiza el CSV."""
    df = _load_places_dataframe()
    if df is None or df.empty:
        return None
        
    # Encontrar el índice del lugar
    idx_list = df[df['id'] == place_id].index.tolist()
    
    if not idx_list:
        return None 
    
    idx = idx_list[0]
    
    # Aplicar los cambios, excluyendo el ID
    for key, value in cambios.items():
        if key != 'id':
            df.at[idx, key] = value
            
    # Guardar los cambios
    _save_places_dataframe(df)
    
    # Retornar la fila actualizada
    return df.iloc[idx].to_dict()

#   6) desactivar(place_id: int, clock: callable, actor: str) -> bool
#      - is_active=False, actualiza updated_*; True si modificó, False si no existe.

def desactivar(place_id: int, clock: Callable[[], datetime], actor: str) -> bool:
    """Establece is_active=False y actualiza los campos de auditoría."""
    df = _load_places_dataframe()
    if df is None or df.empty:
        return False

    idx_list = df[df['id'] == place_id].index.tolist()
    
    if not idx_list:
        return False 

    idx = idx_list[0]
    
    # Aplicar los cambios de desactivación y auditoría
    df.at[idx, 'is_active'] = False
    df.at[idx, 'updated_at'] = clock().strftime('%Y-%m-%d %H:%M:%S')
    df.at[idx, 'updated_by'] = actor
    
    _save_places_dataframe(df)
    
    return True

# Consideraciones:
#   - Este repo NO valida efectos colaterales (como bloquear creación de máquinas);
#     eso va en domain.
# -------------------------------------------
