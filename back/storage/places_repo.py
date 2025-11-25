# -------------------------------------------
# back/storage/places_repo.py
# Propósito:
#   - CRUD para data/places.csv.
#
# CSV (encabezado esperado):
#   id,name,address,is_active,created_at,created_by,updated_at,updated_by
#
# Funciones sugeridas:
#   1) listar(only_active: bool = True, limit: int | None = None, offset: int = 0) -> list[dict]
#      - Devuelve lugares como lista de dicts (campos: id, name, address, is_active).
#
#   2) obtener_por_id(place_id: int) -> dict | None
#      - Fila por id o None.
#
#   3) existe_name(name: str, exclude_id: int | None = None) -> bool
#      - Verifica duplicados de name (case-insensitive si se decide).
#
#   4) insertar_fila(row: dict) -> None
#      - Concatena y escribe CSV (asegurando columnas).
#
#   5) actualizar_fila(place_id: int, cambios: dict) -> dict | None
#      - Aplica cambios; retorna fila resultante o None si no existe.
#
#   6) desactivar(place_id: int, clock: callable, actor: str) -> bool
#      - is_active=False, actualiza updated_*; True si modificó, False si no existe.
#
# Consideraciones:
#   - Este repo NO valida efectos colaterales (como bloquear creación de máquinas);
#     eso va en domain.
# -------------------------------------------

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict


# Ruta al archivo CSV de casinos
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PLACES_CSV = DATA_DIR / "places.csv"


class PlaceStorage:
    """Maneja la persistencia de casinos en CSV"""

    @staticmethod
    def _ensure_csv_exists():
        """Crea el CSV si no existe"""
        if not PLACES_CSV.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame(columns=[
                'id',
                'nombre',
                'direccion',
                'codigo_casino',
                'estado',
                'created_at',
                'created_by',
                'updated_at',
                'updated_by'
            ])
            df.to_csv(PLACES_CSV, index=False)

    @staticmethod
    def _get_next_id() -> int:
        """Obtiene el siguiente ID disponible"""
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)
        
        if df.empty:
            return 1
        
        return int(df['id'].max()) + 1

    @staticmethod
    def create_place(
        nombre: str,
        direccion: str,
        codigo_casino: str,
        created_by: str = "system"
    ) -> Dict:
        """
        Crea un nuevo casino en el CSV
        
        Args:
            nombre: Nombre del casino
            direccion: Dirección del casino
            codigo_casino: Código único del casino
            created_by: Usuario que crea
            
        Returns:
            Dict con los datos del casino creado
            
        Raises:
            ValueError: Si el codigo_casino ya existe
        """
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)
        
        # VALIDACIÓN: Verificar que el código no exista
        if not df.empty:
            # Asegurar que la columna sea string antes de usar .str
            codigos = df['codigo_casino'].astype(str).str.upper()
            if codigo_casino.upper() in codigos.values:
                raise ValueError(
                    f"Ya existe un casino con el código '{codigo_casino}'. "
                    "El código debe ser único."
                )
        
        # Crear nuevo registro
        new_id = PlaceStorage._get_next_id()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_place = {
            'id': new_id,
            'nombre': nombre.strip(),
            'direccion': direccion.strip(),
            'codigo_casino': codigo_casino.upper(),
            'estado': True,
            'created_at': timestamp,
            'created_by': created_by,
            'updated_at': None,
            'updated_by': None
        }
        
        # Agregar al CSV
        df = pd.concat([df, pd.DataFrame([new_place])], ignore_index=True)
        df.to_csv(PLACES_CSV, index=False)
        
        return new_place

    
    @staticmethod
    def inactivar_casino(codigo_casino: int, actor: str = "system") -> bool:

        """
        Marca un casino como INACTIVO (estado = False) y registra auditoría.
        Retorna True si se desactivó, lanza KeyError si no existe.
        """

        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)

        if codigo_casino not in df["id"].values:
            raise KeyError(f"No existe un casino con ID {codigo_casino}")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Asegurar columnas de auditoría si faltan
        if 'updated_at' not in df.columns:
            df['updated_at'] = None
        if 'updated_by' not in df.columns:
            df['updated_by'] = None

        # Cambiar estado a falso y registrar auditoría
        df.loc[df["id"] == codigo_casino, "estado"] = False
        df.loc[df["id"] == codigo_casino, "updated_at"] = timestamp
        df.loc[df["id"] == codigo_casino, "updated_by"] = actor

        df.to_csv(PLACES_CSV, index=False)

        return True

    # Alias y helpers para la API / dominio
    @staticmethod
    def inactivar(codigo_casino: int, actor: str = "system") -> bool:
        """Alias más corto esperado por capas superiores."""
        return PlaceStorage.inactivar_casino(codigo_casino, actor=actor)


    @staticmethod
    def activar_casino(codigo_casino: int, actor: str = "system") -> bool:
        """
        Marca un casino como ACTIVO (estado = True) y registra auditoría.
        Retorna True si se activó, lanza KeyError si no existe.
        """
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)

        if codigo_casino not in df["id"].values:
            raise KeyError(f"No existe un casino con ID {codigo_casino}")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if 'updated_at' not in df.columns:
            df['updated_at'] = ''
        if 'updated_by' not in df.columns:
            df['updated_by'] = ''

        df['updated_at'] = df['updated_at'].astype(object)
        df['updated_by'] = df['updated_by'].astype(object)

        df.loc[df["id"] == codigo_casino, "estado"] = True
        df.loc[df["id"] == codigo_casino, "updated_at"] = timestamp
        df.loc[df["id"] == codigo_casino, "updated_by"] = actor

        df.to_csv(PLACES_CSV, index=False)
        return True

    @staticmethod
    def activar(codigo_casino: int, actor: str = "system") -> bool:
        return PlaceStorage.activar_casino(codigo_casino, actor=actor)
        

    @staticmethod
    def listar(only_active: bool = True, limit: int | None = None, offset: int = 0) -> list:
        """Devuelve lista de lugares como dicts. Filtra por activos por defecto."""
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)

        if df.empty:
            return []


        # Filtro correcto según only_active
        if 'estado' in df.columns:
            if only_active is True:
                df = df[df['estado'] == True]
            elif only_active is False:
                df = df[df['estado'] == False]

        # Orden por id para consistencia
        if 'id' in df.columns:
            df = df.sort_values('id')

        if offset:
            df = df.iloc[offset:]
        if limit is not None:
            df = df.iloc[:limit]

        # Normalizar filas a dicts
        return df.fillna('').to_dict(orient='records')

    @staticmethod
    def obtener_por_id(place_id: int) -> dict | None:
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)

        if df.empty:
            return None

        row = df.loc[df['id'] == place_id]
        if row.empty:
            return None

        return row.iloc[0].to_dict()
    
    @staticmethod
    def get_by_id(place_id: int) -> dict | None:
        """Alias para obtener_por_id (compatibilidad con módulo de balances)"""
        return PlaceStorage.obtener_por_id(place_id)

    @staticmethod
    def actualizar_place(place_id: int, cambios: dict, actor: str = "system") -> dict:
        """
        Actualiza los campos proporcionados de un casino y devuelve la fila actualizada.

        No valida reglas de negocio (por ejemplo, inmutabilidad de `codigo_casino`);
        esas validaciones deben hacerse en la capa de dominio.

        Lanza KeyError si el `place_id` no existe.
        """
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)

        if df.empty or place_id not in df['id'].astype(int).values:
            raise KeyError(f"No existe un casino con ID {place_id}")

        row_idx = df.index[df['id'].astype(int) == int(place_id)][0]

        # Aplicar sólo columnas conocidas para evitar escribir campos extraños
        allowed = {'nombre', 'direccion', 'estado'}
        for k, v in cambios.items():
            if k in allowed:
                df.at[row_idx, k] = v

        # Auditoría
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'updated_at' not in df.columns:
            df['updated_at'] = None
        if 'updated_by' not in df.columns:
            df['updated_by'] = None

        df.at[row_idx, 'updated_at'] = timestamp
        df.at[row_idx, 'updated_by'] = actor

        df.to_csv(PLACES_CSV, index=False)

        return df.loc[row_idx].fillna('').to_dict()

    @staticmethod
    def existe_nombre(nombre: str, exclude_id: int | None = None) -> bool:
        """Verifica si ya existe un nombre (case-insensitive)."""
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)

        if df.empty:
            return False

        comp = df['nombre'].astype(str).str.strip().str.lower()
        target = nombre.strip().lower()

        if exclude_id is not None and 'id' in df.columns:
            df = df[df['id'] != exclude_id]
            comp = df['nombre'].astype(str).str.strip().str.lower()

        return target in comp.values

    @staticmethod
    def get_place_by_code(codigo_casino: str) -> dict | None:
        """
        Obtiene un casino por su código (case-insensitive).
        Retorna dict si existe, None si no.
        """
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)

        if df.empty:
            return None

        # Normalización para comparación
        comp = df['codigo_casino'].astype(str).str.strip().str.upper()
        target = codigo_casino.strip().upper()

        row = df.loc[comp == target]

        if row.empty:
            return None

        return row.iloc[0].to_dict()

    @staticmethod
    def actualizar_place(place_id: int, cambios: dict, actor: str = "system") -> dict:
        """Aplica cambios a un casino y los persiste en el CSV.

        Este método NO aplica validaciones de negocio complejas (por ejemplo,
        unicidad de nombre o inmutabilidad de codigo_casino). Es responsabilidad
        de la capa de dominio validar reglas antes de llamar aquí.

        Retorna la fila actualizada como dict. Lanza KeyError si no existe.
        """
        PlaceStorage._ensure_csv_exists()
        df = pd.read_csv(PLACES_CSV)

        if df.empty or int(place_id) not in df['id'].astype(int).values:
            raise KeyError(f"No existe un casino con ID {place_id}")

        row_idx = df.index[df['id'].astype(int) == int(place_id)][0]

        # Aplicar cambios solo a columnas permitidas
        allowed = {'nombre', 'direccion', 'estado'}
        for k, v in cambios.items():
            if k in allowed:
                df.at[row_idx, k] = v

        # Auditoría
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'updated_at' not in df.columns:
            df['updated_at'] = None
        if 'updated_by' not in df.columns:
            df['updated_by'] = None

        df.at[row_idx, 'updated_at'] = timestamp
        df.at[row_idx, 'updated_by'] = actor

        df.to_csv(PLACES_CSV, index=False)

        return df.loc[row_idx].fillna('').to_dict()
