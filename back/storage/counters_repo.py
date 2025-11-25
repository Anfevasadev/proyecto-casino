import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from .machines_repo import MachinesRepo


class CountersRepo:
    """Repositorio de contadores basado en CSV (`data/counters.csv`).

    Implementa la API utilizada por `domain` y `api`:
      - next_id()
      - insert_counter(row: dict)
      - list_counters(machine_id=None, date_from=None, date_to=None, limit=100, offset=0, sort_by='at', ascending=True)
      - get_by_id(id)
      - list_by_casino_date(casino_id, fecha_inicio, fecha_fin)
      - update_batch(casino_id, fecha_filtro, updates, actor, timestamp)
    """

    FIELDNAMES = [
        "id",
        "machine_id",
        "at",
        "in_amount",
        "out_amount",
        "jackpot_amount",
        "billetero_amount",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]

    def __init__(self, filepath: Optional[str] = None):
        base_dir = os.path.dirname(__file__)
        if filepath:
            self.filepath = filepath
        else:
            self.filepath = os.path.abspath(os.path.join(base_dir, "..", "..", "data", "counters.csv"))

        self._ensure_file()
        self._load()
        # Para operaciones que requieren conocer casino_id de una máquina
        self.machines_repo = MachinesRepo()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.FIELDNAMES)

    def _load(self):
        with open(self.filepath, newline="") as f:
            reader = csv.DictReader(f)
            self.data: List[Dict[str, str]] = list(reader)

    def _save(self):
        if not self.data:
            # Ensure header exists
            with open(self.filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.FIELDNAMES)
            return

        with open(self.filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(self.data)

    def next_id(self) -> int:
        if not self.data:
            return 1
        return max(int(r["id"]) for r in self.data) + 1

    def insert_counter(self, row: Dict[str, Any]) -> Dict[str, Any]:
        # Normalizar y asignar id si falta
        if row.get("id") is None:
            row_id = self.next_id()
        else:
            row_id = int(row.get("id"))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Asegurar campos básicos
        stored = {
            "id": str(row_id),
            "machine_id": str(int(row.get("machine_id"))),
            "at": str(row.get("at")),
            "in_amount": str(float(row.get("in_amount", 0.0))),
            "out_amount": str(float(row.get("out_amount", 0.0))),
            "jackpot_amount": str(float(row.get("jackpot_amount", 0.0))),
            "billetero_amount": str(float(row.get("billetero_amount", 0.0))),
            "created_at": row.get("created_at", now),
            "created_by": row.get("created_by", "system"),
            "updated_at": row.get("updated_at", now),
            "updated_by": row.get("updated_by", "system"),
        }

        self.data.append(stored)
        self._save()

        # Devolver con tipos más cómodos (int/float) para capas superiores
        return {
            "id": int(stored["id"]),
            "machine_id": int(stored["machine_id"]),
            "at": stored["at"],
            "in_amount": float(stored["in_amount"]),
            "out_amount": float(stored["out_amount"]),
            "jackpot_amount": float(stored["jackpot_amount"]),
            "billetero_amount": float(stored["billetero_amount"]),
            "created_at": stored["created_at"],
            "created_by": stored["created_by"],
            "updated_at": stored["updated_at"],
            "updated_by": stored["updated_by"],
        }

    def get_by_id(self, counter_id: int) -> Optional[Dict[str, Any]]:
        for r in self.data:
            try:
                if int(r["id"]) == counter_id:
                    return {
                        "id": int(r["id"]),
                        "machine_id": int(r["machine_id"]),
                        "at": r["at"],
                        "in_amount": float(r["in_amount"]),
                        "out_amount": float(r["out_amount"]),
                        "jackpot_amount": float(r["jackpot_amount"]),
                        "billetero_amount": float(r["billetero_amount"]),
                        "created_at": r.get("created_at"),
                        "created_by": r.get("created_by"),
                        "updated_at": r.get("updated_at"),
                        "updated_by": r.get("updated_by"),
                    }
            except Exception:
                continue
        return None

    def list_counters(
        self,
        machine_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "at",
        ascending: bool = True,
    ) -> List[Dict[str, Any]]:
        rows = []
        for r in self.data:
            try:
                row = {
                    "id": int(r["id"]),
                    "machine_id": int(r["machine_id"]),
                    "at": r["at"],
                    "in_amount": float(r["in_amount"]),
                    "out_amount": float(r["out_amount"]),
                    "jackpot_amount": float(r["jackpot_amount"]),
                    "billetero_amount": float(r["billetero_amount"]),
                }
            except Exception:
                continue

            if machine_id is not None and row["machine_id"] != machine_id:
                continue

            # Filtrado por fecha (acepta 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS')
            if date_from:
                try:
                    if not row["at"].startswith(date_from):
                        # If date_from includes time, check full compare
                        if row["at"] < date_from:
                            continue
                except Exception:
                    continue

            if date_to:
                try:
                    if not row["at"].startswith(date_to):
                        if row["at"] > date_to + " 23:59:59":
                            continue
                except Exception:
                    continue

            rows.append(row)

        # Ordenamiento
        def keyfn(x):
            if sort_by in ("in_amount", "out_amount", "jackpot_amount", "billetero_amount"):
                return x.get(sort_by, 0.0)
            if sort_by == "id":
                return x.get("id", 0)
            # por defecto 'at'
            return x.get("at", "")

        rows.sort(key=keyfn, reverse=not ascending)

        # Paginación
        return rows[offset : offset + limit]

    def list_by_casino_date(self, casino_id: int, fecha_inicio: str, fecha_fin: str) -> List[Dict[str, Any]]:
        # Convertir strings 'YYYY-MM-DD' y filtrar registros que pertenecen
        # a máquinas cuyo casino_id coincida.
        resultado = []
        for r in self.data:
            try:
                mid = int(r["machine_id"])
            except Exception:
                continue
            m = self.machines_repo.get_by_id(mid)
            if not m:
                continue
            # machines_repo stores casino_id as field 'casino_id' or 'casino_id'
            try:
                m_casino = int(m.get("casino_id") or m.get("casino") or 0)
            except Exception:
                m_casino = 0
            if m_casino != casino_id:
                continue

            # comparar la porción fecha 'YYYY-MM-DD'
            at = r.get("at", "")
            if not at:
                continue
            at_date = at.split(" ")[0]
            if fecha_inicio <= at_date <= fecha_fin:
                resultado.append({
                    "id": int(r["id"]),
                    "machine_id": int(r["machine_id"]),
                    "casino_id": m_casino,
                    "at": r["at"],
                    "in_amount": float(r["in_amount"]),
                    "out_amount": float(r["out_amount"]),
                    "jackpot_amount": float(r["jackpot_amount"]),
                    "billetero_amount": float(r["billetero_amount"]),
                })

        return resultado

    def update_batch(self, casino_id: int, fecha_filtro: str, updates: List[Dict[str, Any]], actor: str, timestamp: str) -> List[Dict[str, Any]]:
        """Aplica una lista de actualizaciones para máquinas de un casino en una fecha dada.

        `updates` es una lista de dicts que incluyen al menos `machine_id` y los campos a modificar.
        Retorna la lista de filas actualizadas (ya convertidas a tipos correctos).
        """
        updated = []
        # Para cada update, localizar filas que coincidan con machine_id y fecha
        for u in updates:
            try:
                target_mid = int(u.get("machine_id"))
            except Exception:
                continue

            # Verificar que la máquina pertenece al casino
            m = self.machines_repo.get_by_id(target_mid)
            if not m:
                continue
            try:
                m_casino = int(m.get("casino_id") or 0)
            except Exception:
                m_casino = 0
            if m_casino != casino_id:
                continue

            # buscar filas con misma máquina y misma fecha (porción YYYY-MM-DD)
            for idx, row in enumerate(self.data):
                try:
                    if int(row.get("machine_id")) != target_mid:
                        continue
                    at = row.get("at", "")
                    if not at.startswith(fecha_filtro):
                        continue
                except Exception:
                    continue

                # aplicar cambios solo de los campos existentes en update
                changed = False
                for field in ("at", "in_amount", "out_amount", "jackpot_amount", "billetero_amount"):
                    if field in u:
                        self.data[idx][field] = str(u[field])
                        changed = True

                if changed:
                    self.data[idx]["updated_at"] = timestamp
                    self.data[idx]["updated_by"] = actor
                    # construir salida con tipos convertidos
                    updated.append({
                        "id": int(self.data[idx]["id"]),
                        "machine_id": int(self.data[idx]["machine_id"]),
                        "at": self.data[idx]["at"],
                        "in_amount": float(self.data[idx]["in_amount"]),
                        "out_amount": float(self.data[idx]["out_amount"]),
                        "jackpot_amount": float(self.data[idx]["jackpot_amount"]),
                        "billetero_amount": float(self.data[idx]["billetero_amount"]),
                    })

        if updated:
            self._save()

        return updated

