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

    def __init__(self, filepath=None):
        # Por defecto usar el CSV en la carpeta `data/` del proyecto
        if filepath:
            self.filepath = filepath
        else:
            base_dir = os.path.dirname(__file__)
            # desde back/storage -> ../../data/machines.csv
            self.filepath = os.path.abspath(os.path.join(base_dir, "..", "..", "data", "machines.csv"))
        self._ensure_file()
        self.data = self._load()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "id","marca","modelo","serial","asset",
                    "denominacion","place_id","is_active", 
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

    def add(self, machine: dict, actor: str, timestamp: datetime): 
        now_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        machine["created_at"] = now_str
        machine["created_by"] = actor
        machine["updated_at"] = now_str
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

    def update(self, machine_id: int, cambios: Dict, actor: str, timestamp: datetime) -> Optional[Dict]:
            now_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. Buscar el índice del registro
            for i, m in enumerate(self.data):
                if int(m.get("id")) == machine_id:
                    # 2. Aplicar los cambios
                    for key, value in cambios.items():
                        # El dominio ya validó que la denominacion no esté aquí
                        if key != "id": 
                            m[key] = str(value) # Guardar como string para el CSV
                    
                    # 3. Aplicar Auditoría (Usando el timestamp inyectado)
                    m["updated_at"] = now_str
                    m["updated_by"] = actor
                    
                    # 4. Guardar los datos en el CSV
                    self.data[i] = m
                    self._save()
                    return m
            
            return None
            
    def existe_serial_o_asset(self, serial: str, asset: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica la unicidad de serial y asset, excluyendo el ID actual si es para actualización.
        """
        norm_serial = str(serial).strip()
        norm_asset = str(asset).strip()
        
        for m in self.data:
            m_id = int(m.get("id"))
            
            # 1. Excluir la máquina actual si estamos en el modo actualización
            if exclude_id is not None and m_id == exclude_id:
                continue
                
            # 2. Comprobar unicidad (Serial o Asset)
            if (m.get("serial") == norm_serial) or (m.get("asset") == norm_asset):
                return True # Conflicto encontrado
                
        return False # No hay conflictos

