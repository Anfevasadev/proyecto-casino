# -------------------------------------------
# back/storage/machines_repo.py
# Propósito:
#   - CRUD para data/machines.csv, incluyendo validaciones de unicidad de code.

import pandas as pd
import os
from typing import Optional, Dict, List, Any, Union, Callable
from datetime import datetime

# CSV (encabezado esperado):
#   id,code,denomination_value,place_id,participation_rate,is_active,
#   created_at,created_by,updated_at,updated_by

MACHINES_DATA_PATH = "data/machines.csv"   # Ruta al archivo CSV
DATA_DIRECTORY = "data"

def _load_machines_dataframe() -> Optional[pd.DataFrame]:  #Carga el DataFrame desde el CSV. Si el archivo no existe, crea un DataFrame vacío.
    if not os.path.exists(MACHINES_DATA_PATH):
        # Define el esquema completo del CSV si el archivo no existe
        COLUMNS = [
            'id', 'code', 'denomination_value', 'place_id', 'participation_rate', 
            'is_active', 'is_deleted', 'created_at', 'created_by', 
            'updated_at', 'updated_by', 'deleted_at', 'deleted_by'
        ]
        # Asegura que el directorio 'data' exista
        os.makedirs(DATA_DIRECTORY, exist_ok=True)
        return pd.DataFrame(columns=COLUMNS)
    
    try:
        df = pd.read_csv(MACHINES_DATA_PATH)
        # Convertir booleanos para que Python los pueda manjear correctamente
        for col in ['is_active', 'is_deleted']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        return df
    except Exception as e:
        print(f"Error al cargar el repositorio de máquinas: {e}")
        return None

def _save_machines_dataframe(df: pd.DataFrame) -> None: #función priv para guardar el DataFrame en el CSV
    # Asegura de que los valores booleanos se escriban como 'True'/'False' y no como 1/0
    df['is_active'] = df['is_active'].astype(str)
    df['is_deleted'] = df['is_deleted'].astype(str)
    
    df.to_csv(MACHINES_DATA_PATH, index=False)

# Funciones sugeridas:
#   1) listar(place_id: int | None = None, only_active: bool = True,
#             limit: int | None = None, offset: int = 0) -> list[dict]
#      - Filtro opcional por place_id.
#      - Devuelve dicts con los campos públicos de máquinas.

def listar(
    place_id: Optional[int] = None, 
    only_active: bool = True,
    limit: Optional[int] = None, 
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Lista máquinas, aplicando filtros, borrado lógico, paginación y solo campos públicos."""
    df = _load_machines_dataframe()
    if df is None or df.empty:
        return []

    # 1. Aplicar Borrado Lógico (is_deleted = False)
    df_filtered = df[df['is_deleted'] == False].copy()

    # 2. Filtro por place_id (opcional)
    if place_id is not None:
        df_filtered = df_filtered[df_filtered['place_id'] == place_id]

    # 3. Filtro por is_active (opcional/default)
    if only_active:
        df_filtered = df_filtered[df_filtered['is_active'] == True]

    # 4. Paginación o slicing
    start_index = offset
    end_index = offset + limit if limit is not None else len(df_filtered)
    
    df_paginated = df_filtered.iloc[start_index:end_index]
    
    # 5. SEleccionamos los campos publicos que queremos que se muestren en el diccionario a retornar
    PUBLIC_FIELDS = [
        'id', 'code', 'denomination_value', 'place_id', 
        'participation_rate', 'is_active', 'created_at', 
        'created_by', 'updated_at', 'updated_by'
    ]
    
    # Asegurarse de que solo se devuelvan las columnas que existen
    cols_to_return = [col for col in PUBLIC_FIELDS if col in df_paginated.columns]
    
    # Convertir el DataFrame a una lista de diccionarios
    return df_paginated[cols_to_return].to_dict('records')

#
#   2) obtener_por_id(machine_id: int) -> dict | None
#      - Fila por id o None.

def obtener_por_id(machine_id: int) -> Optional[Dict[str, Any]]:
    # Cargamos el df y si está vacío devolvemos None
    df = _load_machines_dataframe()
    if df is None or df.empty:
        return None
        
    # Filtramos por ID y aseguramos que no esté borrada lógicamente
    machine_data = df[(df['id'] == machine_id) & (df['is_deleted'] == False)]
    
    # Si se encuentra, devolver como diccionario sino devuelve None o se puede cambiar a un mensaje con print
    if not machine_data.empty:
        # Devolver solo la fila como un diccionario
        return machine_data.iloc[0].to_dict()
    
    return None

#   3) existe_code(code: str, exclude_id: int | None = None) -> bool
#      - Valida unicidad de code (normalizado con strip; decidir case-sensitive).

def existe_code(code: str, exclude_id: Optional[int] = None) -> bool:
    """Valida la unicidad de 'code', excluyendo un ID si es para actualización."""
    df = _load_machines_dataframe()
    if df is None or df.empty:
        return False
        
    # Normalizamos el código (asumiendo que los datos del CSV están normalizados o se normalizan al cargar)
    normalized_code = code.strip().upper()
    
    # Filtra por el código y que no esté borrado lógicamente
    df_filtered = df[(df['code'] == normalized_code) & (df['is_deleted'] == False)].copy()
    
    # Si se excluye un ID (caso de actualización), quita esa fila del resultado
    if exclude_id is not None:
        df_filtered = df_filtered[df_filtered['id'] != exclude_id]

    #si el df no esta vacio lo devuelve sino devuelve False    
    return not df_filtered.empty

#   4) insertar_fila(row: dict) -> None
#      - Concatena y guarda.

def insertar_fila(row: Dict[str, Any]) -> Dict[str, Any]:
    """Inserta una nueva fila de máquina, generando el ID y guardando en CSV."""
    df = _load_machines_dataframe()
    if df is None:
        # Si no se pudo cargar, devolver un error o una fila vacía.
        raise RuntimeError("No se pudo cargar el repositorio de máquinas para insertar.")
        
    # Generar nuevo ID: Usar el máximo ID existente + 1, o empezar en 1
    new_id = df['id'].max() + 1 if not df.empty and 'id' in df.columns else 1
    
    # Convertir 'row' en un DataFrame de una sola fila
    new_row_df = pd.DataFrame([{**row, 'id': new_id}])

    # Asegurarse de que el nuevo DataFrame tiene todas las columnas de auditoría/estado requeridas
    # Si 'is_deleted' no viene en la 'row', lo establecemos a False por defecto en el repositorio
    if 'is_deleted' not in new_row_df.columns:
        new_row_df['is_deleted'] = False
        
    # Concatenar y guardar
    df_updated = pd.concat([df, new_row_df], ignore_index=True)
    _save_machines_dataframe(df_updated)
    
    # Retornar la fila completa insertada
    return df_updated[df_updated['id'] == new_id].iloc[0].to_dict()

#   5) actualizar_fila(machine_id: int, cambios: dict) -> dict | None
#      - Aplica cambios de columnas válidas; retorna fila resultante o None.

def actualizar_fila(machine_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Aplica cambios a una máquina existente (no borrada lógicamente) y actualiza el CSV."""
    df = _load_machines_dataframe()
    if df is None or df.empty:
        return None
        
    # Encontrar el índice de la máquina que no esté borrada lógicamente
    idx_list = df[(df['id'] == machine_id) & (df['is_deleted'] == False)].index.tolist()
    
    if not idx_list:
        return None # Máquina no encontrada o borrada
    
    idx = idx_list[0]
    
    # Aplicar los cambios, excluyendo el ID (que no se debe actualizar)
    for key, value in cambios.items():
        if key != 'id':
            df.at[idx, key] = value
            
    # Guardar los cambios
    _save_machines_dataframe(df)
    
    # Retornar la fila actualizada
    return df.iloc[idx].to_dict()

#   6) desactivar(machine_id: int, clock: callable, actor: str) -> bool
#      - is_active=False + updated_*; True si modificó, False si no existe.

def desactivar(machine_id: int, clock: Callable[[], datetime], actor: str) -> bool:
    """Establece is_active=False y actualiza los campos de auditoría."""
    df = _load_machines_dataframe()
    if df is None or df.empty:
        return False

    # Encontrar el índice de la máquina que no esté borrada lógicamente
    idx_list = df[(df['id'] == machine_id) & (df['is_deleted'] == False)].index.tolist()
    
    if not idx_list:
        return False # Máquina no encontrada o borrada

    idx = idx_list[0]
    
    # Aplicar los cambios de desactivación y auditoría
    df.at[idx, 'is_active'] = False
    df.at[idx, 'updated_at'] = clock().strftime('%Y-%m-%d %H:%M:%S')
    df.at[idx, 'updated_by'] = actor
    
    _save_machines_dataframe(df)
    
    # True si la máquina fue modificada con éxito
    return True

# Consideraciones:
#   - Validaciones cruzadas (existencia de place_id, rango de participation_rate)
#     se recomiendan en domain; este repo puede ofrecer utilidades para comprobar
#     existencia de place si se le inyecta places_repo (pero mantener simple).
# -------------------------------------------
