# -------------------------------------------
# back/storage/machines_repo.py
# Propósito:
#   - CRUD para data/machines.csv, incluyendo validaciones de unicidad de code.
#
# CSV (encabezado esperado):
#   id,code,denomination_value,place_id,participation_rate,is_active,
#   created_at,created_by,updated_at,updated_by
#
# Funciones sugeridas:
#   1) listar(place_id: int | None = None, only_active: bool = True,
#             limit: int | None = None, offset: int = 0) -> list[dict]
#      - Filtro opcional por place_id.
#      - Devuelve dicts con los campos públicos de máquinas.
#
#   2) obtener_por_id(machine_id: int) -> dict | None
#      - Fila por id o None.
#
#   3) existe_code(code: str, exclude_id: int | None = None) -> bool
#      - Valida unicidad de code (normalizado con strip; decidir case-sensitive).
#
#   4) insertar_fila(row: dict) -> None
#      - Concatena y guarda.
#
#   5) actualizar_fila(machine_id: int, cambios: dict) -> dict | None
#      - Aplica cambios de columnas válidas; retorna fila resultante o None.
#
#   6) desactivar(machine_id: int, clock: callable, actor: str) -> bool
#      - is_active=False + updated_*; True si modificó, False si no existe.
#
# Consideraciones:
#   - Validaciones cruzadas (existencia de place_id, rango de participation_rate)
#     se recomiendan en domain; este repo puede ofrecer utilidades para comprobar
#     existencia de place si se le inyecta places_repo (pero mantener simple).
# -------------------------------------------
import csv
from typing import List

class MachinesRepo:
    def __init__(self, filepath="data/machines.csv"):
        self.filepath = filepath
        self.data = self._load()

    def _load(self):
        try:
            with open(self.filepath, newline="") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            return []

    def next_id(self):
        if not self.data:
            return 1
        return max(int(row["id"]) for row in self.data) + 1

    def existe_code(self, serial: str):
        return any(row["serial"] == serial for row in self.data)

    def insertar_fila(self, row: dict):
        self.data.append(row)
        with open(self.filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writeheader()
            writer.writerows(self.data)

    def obtener_por_id(self, machine_id: int):
        for row in self.data:
            if int(row["id"]) == machine_id:
                return row
        return None

    def listar_filtrado(self, casino_id=None, only_active=True):
        result = self.data
        if casino_id is not None:
            result = [m for m in result if int(m["casino_id"]) == casino_id]
        if only_active:
            result = [m for m in result if m["estado"] in [True, "True", 1, "1"]]
        return result