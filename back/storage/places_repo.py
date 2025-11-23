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
                'created_by'
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
        if not df.empty and codigo_casino.upper() in df['codigo_casino'].str.upper().values:
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
            'created_by': created_by
        }
        
        # Agregar al CSV
        df = pd.concat([df, pd.DataFrame([new_place])], ignore_index=True)
        df.to_csv(PLACES_CSV, index=False)
        
        return new_place
