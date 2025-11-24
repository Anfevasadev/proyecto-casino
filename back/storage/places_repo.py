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
# back/storage/places_repo.py
# Este repositorio está aquí solo para evitar errores con imports.
# El archivo original no contenía PlaceStorage, pero el módulo machines.py lo requiere.
# Se crea la clase mínima necesaria para evitar fallos al iniciar el servidor.

# back/storage/places_repo.py
# Repositorio encargado de leer los datos de los lugares (casinos) desde CSV.
# Implementación mínima pero funcional para no romper el proyecto.

# back/storage/places_repo.py
# Repositorio mínimo para que la API funcione sin romper nada.
# Se encarga de leer lugares (casinos) desde places.csv.

import csv
from typing import List, Dict, Optional
from .csv_paths import PLACES_CSV_PATH


class PlaceStorage:
    """
    Clase simple que permite:
    - Leer todos los casinos
    - Buscar un casino por ID

    Es suficiente para que machines.py pueda trabajar sin errores.
    """

    def __init__(self):
        self.path = PLACES_CSV_PATH

    def get_all(self) -> List[Dict]:
        """
        Devuelve todos los lugares/casinos desde el CSV.
        """
        data = []
        try:
            with open(self.path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Normaliza tipos simples
                    row["id"] = int(row["id"])
                    data.append(row)
        except FileNotFoundError:
            # Si no existe el archivo, devolvemos una lista vacía
            return []
        return data

    def get_by_id(self, place_id: int) -> Optional[Dict]:
        """
        Busca un casino por su ID.
        """
        lugares = self.get_all()
        for lugar in lugares:
            if lugar["id"] == place_id:
                return lugar
        return None
