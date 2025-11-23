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
import os
from typing import List, Dict
from datetime import datetime

class MachinesRepo:

    def __init__(self, filepath="data/machines.csv"):
        self.filepath = filepath
        self._ensure_file()
        self.data = self._load()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "id","marca","modelo","serial","asset",
                    "denominacion","estado","casino_id",
                    "created_at","created_by","updated_at","updated_by"
                ])

    def _load(self) -> List[Dict]:
        with open(self.filepath, newline="") as f:
            return list(csv.DictReader(f))

    def _save(self):
        with open(self.filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)

    def next_id(self) -> int:
        if not self.data:
            return 1
        return max(int(row["id"]) for row in self.data) + 1

    def add(self, machine: dict, actor: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        machine["created_at"] = now
        machine["created_by"] = actor
        machine["updated_at"] = now
        machine["updated_by"] = actor

        self.data.append(machine)
        self._save()

    def list_all(self):
        return self.data

    def get_by_id(self, machine_id: int):
        for m in self.data:
            if int(m["id"]) == machine_id:
                return m
        return None

