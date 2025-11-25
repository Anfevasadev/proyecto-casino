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

import json
from pathlib import Path


class PlaceStorage:
    def __init__(self, filename="places.json"):
        self.file = Path(filename)
        if not self.file.exists():
            self.file.write_text("[]")

    def _read(self):
        return json.loads(self.file.read_text())

    def _write(self, data):
        self.file.write_text(json.dumps(data, indent=4))

    def list_places(self):
        return self._read()

    def get_place(self, place_id: int):
        places = self._read()
        for p in places:
            if p["id"] == place_id:
                return p
        return None

    # Compatibilidad con nombres en castellano usados por la capa `domain`
    def obtener_por_id(self, place_id: int):
        """Alias en español para `get_place` usado por algunos módulos del dominio."""
        return self.get_place(place_id)

    # Alias adicional por si se usa `obtener_por_id` con distinto nombre
    def obtener(self, place_id: int):
        return self.get_place(place_id)
