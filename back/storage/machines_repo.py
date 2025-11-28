
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
        # Recargar datos para asegurar que estén actualizados
        self.data = self._load()
        for m in self.data:
            if int(m["id"]) == machine_id:
                return m
        return None

    def existe_serial(self, serial: str, exclude_id: int = None) -> bool:
        """Verifica si existe una máquina con el serial dado."""
        self.data = self._load()
        for m in self.data:
            if m.get("serial", "").strip().lower() == serial.strip().lower():
                # Si se excluye un ID (para ediciones), no contar esa máquina
                if exclude_id is None or int(m["id"]) != exclude_id:
                    return True
        return False

    def existe_asset(self, asset: str, exclude_id: int = None) -> bool:
        """Verifica si existe una máquina con el asset dado."""
        self.data = self._load()
        for m in self.data:
            if m.get("asset", "").strip().lower() == asset.strip().lower():
                # Si se excluye un ID (para ediciones), no contar esa máquina
                if exclude_id is None or int(m["id"]) != exclude_id:
                    return True
        return False

    def listar(self, only_active: bool = None, casino_id: int = None):
        """
        Devuelve la lista de máquinas filtrando por estado y/o casino.
        only_active=True: solo activas (estado==True)
        only_active=False: solo inactivas (estado==False)
        only_active=None: todas
        casino_id: filtrar por casino específico
        """
        self.data = self._load()
        result = self.data
        
        # Filtrar por casino si se especifica
        if casino_id is not None:
            result = [m for m in result if str(m.get("casino_id", "")) == str(casino_id)]
        
        # Filtrar por estado
        if only_active is True:
            result = [m for m in result if str(m.get("estado", "")).lower() == "true"]
        elif only_active is False:
            result = [m for m in result if str(m.get("estado", "")).lower() == "false"]
        
        return result

    def actualizar(self, machine_id: int, cambios: dict, actor: str) -> dict | None:
        """
        Actualiza una máquina con los cambios especificados.
        Retorna el registro actualizado o None si no existe.
        
        cambios: dict con campos permitidos (marca, modelo, serial, asset, casino_id)
        NO se puede modificar: id, denominacion, created_at, created_by
        """
        self.data = self._load()
        
        # Buscar la máquina
        machine = None
        machine_index = None
        for idx, m in enumerate(self.data):
            if int(m["id"]) == machine_id:
                machine = m
                machine_index = idx
                break
        
        if machine is None:
            return None
        
        # Campos permitidos para actualizar
        campos_permitidos = ["marca", "modelo", "serial", "asset", "casino_id"]
        
        # Aplicar cambios válidos
        for campo, valor in cambios.items():
            if campo in campos_permitidos and valor is not None:
                machine[campo] = str(valor)
        
        # Actualizar auditoría
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        machine["updated_at"] = now
        machine["updated_by"] = actor
        
        # Guardar cambios
        self.data[machine_index] = machine
        self._save()
        
        return machine