# Implementación de helper para counters usando pandas.
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any

CSV_PATH = Path("data/counters.csv")

EXPECTED_COLUMNS = [
    "id",
    "machine_id",
    "casino_id",
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


class CountersRepo:

    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        """Crea el CSV con las columnas si no existe."""
        if not CSV_PATH.exists():
            # Crear directorio si no existe
            CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame(columns=EXPECTED_COLUMNS)
            df.to_csv(CSV_PATH, index=False)
        else:
            # Si existe, aseguramos que tenga la columna casino_id (migración simple)
            df = pd.read_csv(CSV_PATH)
            if "casino_id" not in df.columns:
                df["casino_id"] = ""
                df.to_csv(CSV_PATH, index=False)

    def _read_df(self) -> pd.DataFrame:
        """
        Leer el CSV y asegurar que tenga las columnas esperadas.
        Como estudiante: si no existe, devolvemos un DataFrame vacío con columnas.
        """
        if CSV_PATH.exists():
            df = pd.read_csv(CSV_PATH, dtype=str)
        else:
            df = pd.DataFrame(columns=EXPECTED_COLUMNS)

        # Asegurar que todas las columnas esperadas existan en el DataFrame
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[EXPECTED_COLUMNS]

    def _write_df(self, df: pd.DataFrame) -> None:
        """
        Escribir DataFrame al CSV respetando el orden de columnas.
        """
        df.to_csv(CSV_PATH, index=False)

    def next_id(self) -> int:
        """Calcular el próximo id disponible (secuencial)."""
        df = self._read_df()
        if df.empty:
            return 1
        ids = [int(x) for x in df["id"].dropna().tolist() if str(x).strip() != ""]
        return (max(ids) + 1) if ids else 1

    def get_by_id(self, counter_id: int) -> Optional[Dict[str, Any]]:
        """Obtener fila por id. Normaliza tipos básicos al retornar."""
        df = self._read_df()
        # Convertimos columna ID a numérico para comparar
        df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

        rows = df[df["id_num"] == counter_id]

        if rows.empty:
            return None

        row = rows.iloc[0].to_dict()

        # Limpieza de temporales
        if "id_num" in row:
            del row["id_num"]

        # Normalizar tipos simples
        try:
            row["id"] = int(float(row["id"]))
        except:
            row["id"] = None

        try:
            row["machine_id"] = int(float(row["machine_id"]))
        except:
            row["machine_id"] = None

        for f in ["in_amount", "out_amount", "jackpot_amount", "billetero_amount"]:
            try:
                val = row.get(f)
                row[f] = (
                    float(val) if val is not None and str(val).strip() != "" else 0.0
                )
            except:
                row[f] = 0.0

        try:
            row["casino_id"] = int(float(row.get("casino_id", 0)))
        except:
            row["casino_id"] = None

        return row

    def list_counters(
        self,
        machine_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: int = 0,
        sort_by: str = "at",
        ascending: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Listar contadores con filtros simples.

        Notas didácticas:
        - Usamos comparaciones de strings para fechas porque el formato
        es 'YYYY-MM-DD HH:MM:SS' (orden lexicográfico coincide con orden cronológico).
        - Se aplica paginación con `limit` y `offset`.
        """
        df = self._read_df()

        if machine_id is not None:
            df = df[df["machine_id"] == machine_id]

        if date_from is not None:
            df = df[df["at"] >= date_from]

        if date_to is not None:
            df = df[df["at"] <= date_to]

        # Ordenar según preferencia
        if sort_by not in ["at", "id"]:
            sort_by = "at"
        df = df.sort_values(by=sort_by, ascending=ascending)

        if limit is not None:
            df = df.iloc[offset : offset + limit]
        else:
            df = df.iloc[offset:]

        results: List[Dict[str, Any]] = []
        for _, r in df.iterrows():
            row = r.to_dict()
            # Normalizar tipos sencillos
            try:
                row["id"] = (
                    int(row.get("id")) if str(row.get("id", "")).strip() else None
                )
            except Exception:
                row["id"] = None
            try:
                row["machine_id"] = (
                    int(row.get("machine_id"))
                    if str(row.get("machine_id", "")).strip()
                    else None
                )
            except Exception:
                row["machine_id"] = None
            for f in ["in_amount", "out_amount", "jackpot_amount", "billetero_amount"]:
                try:
                    row[f] = (
                        float(row.get(f))
                        if row.get(f) is not None and str(row.get(f)).strip() != ""
                        else 0.0
                    )
                except Exception:
                    row[f] = 0.0
            results.append(row)
        return results

    def insert_counter(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insertar un registro nuevo en el CSV. `row` debe contener las columnas
        esperadas (al menos las públicas). Retorna la fila insertada.
        """
        df = self._read_df()
        # Asegurar que el id exista y sea único
        if "id" not in row or row["id"] is None:
            row["id"] = self.next_id()

        # Asegurar columnas faltantes en el row
        for col in EXPECTED_COLUMNS:
            if col not in row:
                row[col] = None

        # Convertir a DataFrame temporal y concatenar
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True, sort=False)
        # Escribir asegurando el orden de columnas
        df = df.reindex(columns=EXPECTED_COLUMNS)
        self._write_df(df)
        return self.get_by_id(int(row["id"]))

    def update_counter(
        self, counter_id: int, cambios: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza columnas permitidas de un registro existente.
        Retorna la fila actualizada o None si no existe.
        """
        df = self._read_df()
        idx = df.index[df["id"] == counter_id]
        if len(idx) == 0:
            return None
        i = idx[0]

        allowed = {
            "at",
            "in_amount",
            "out_amount",
            "jackpot_amount",
            "billetero_amount",
            "machine_id",
            "updated_at",
            "updated_by",
        }
        for k, v in cambios.items():
            if k in allowed:
                df.at[i, k] = str(v)

        self._write_df(df)
        return self.get_by_id(counter_id)

    def update_batch(
        self,
        casino_id: int,
        fecha_filtro: str,
        updates: List[Dict],
        actor: str,
        timestamp,
    ) -> List[Dict]:
        """
        Actualiza múltiples registros filtrando por Casino y Fecha (YYYY-MM-DD).
        """
        df = self._read_df()
        if df.empty:
            return []

        now_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        updated_records = []

        # Mapa de actualizaciones
        updates_map = {int(u["machine_id"]): u for u in updates}
        machines_to_update = updates_map.keys()

        # Iterar
        for idx, row in df.iterrows():

            # 1. Validar Casino
            try:
                row_casino = int(float(row["casino_id"]))
            except (ValueError, TypeError):
                continue

            if row_casino != casino_id:
                continue

            # 2. Validar Fecha
            row_at = str(row["at"])
            if len(row_at) >= 10:
                row_date = row_at[:10]
            else:
                continue

            if row_date != fecha_filtro:
                continue

            # 3. Validar Máquina
            try:
                m_id = int(float(row["machine_id"]))
            except (ValueError, TypeError):
                continue

            if m_id in machines_to_update:
                cambios = updates_map[m_id]

                # 4. Validar hora específica si se proporciona en el JSON
                if cambios.get("at") is not None:
                    # Si viene 'at' en el JSON, debe coincidir exactamente
                    if row_at.strip() != str(cambios["at"]).strip():
                        continue  # Este no es el contador específico que buscamos

                # Aplicar cambios
                if cambios.get("in_amount") is not None:
                    df.at[idx, "in_amount"] = str(cambios["in_amount"])
                if cambios.get("out_amount") is not None:
                    df.at[idx, "out_amount"] = str(cambios["out_amount"])
                if cambios.get("jackpot_amount") is not None:
                    df.at[idx, "jackpot_amount"] = str(cambios["jackpot_amount"])
                if cambios.get("billetero_amount") is not None:
                    df.at[idx, "billetero_amount"] = str(cambios["billetero_amount"])

                # Auditoría
                df.at[idx, "updated_at"] = now_str
                df.at[idx, "updated_by"] = actor

                # Agregar a resultados
                res_row = df.loc[idx].to_dict()
                # Normalizar para retorno
                res_row["machine_id"] = m_id
                res_row["casino_id"] = row_casino
                updated_records.append(res_row)

        if updated_records:
            self._write_df(df)

        return updated_records

    # -------------- METODO PARA EL MOUDLO DE REPORTES ---------------

    def list_by_casino_date(
        self, casino_id: int, fecha_inicio: str, fecha_fin: str
    ) -> List[Dict]:
        """Filtra registros por casino y rango de fechas."""
        df = self._read_df()
        results = []

        for _, row in df.iterrows():
            try:
                if int(float(row["casino_id"])) != casino_id:
                    continue
            except:
                continue

            row_at = str(row["at"])
            if len(row_at) >= 10:
                row_date = row_at[:10]
                if fecha_inicio <= row_date <= fecha_fin:
                    results.append(row.fillna("").to_dict())

        return results

    # --------Este Metodo devuelve el último contador registrado ANTES o IGUAL a la fecha inicial del rango.-----------#

    def get_first_before(self, machine_id: int, fecha_limite: str) -> Optional[Dict]:
        """
        Obtiene el contador inicial para el cuadre.
        Devuelve el último contador registrado ANTES O IGUAL a la fecha dada.

        Ejemplo:
        Si fecha_limite = '2025-11-25 03:00:00',
        buscará el contador más reciente con 'at' <= esa hora.
        """
        df = self._read_df()

        # Filtrar por máquina
        df = df[df["machine_id"] == str(machine_id)]

        if df.empty:
            return None

        # Filtrar contadores que estén antes o igual a la fecha límite
        df = df[df["at"] <= fecha_limite]

        if df.empty:
            return None

        # Ordenar por fecha descendente (el más reciente primero)
        df = df.sort_values(by="at", ascending=False)

        # Tomar el primer registro (último contador antes del rango)
        row = df.iloc[0].to_dict()

        # Normalizar tipos
        return self.get_by_id(int(row["id"]))

    # ----Este Metodo devuelve el contador más cercano ANTES o IGUAL al final del rango-----------#

    def get_last_before(self, machine_id: int, fecha_limite: str) -> Optional[Dict]:
        """
        Obtiene el contador final para el cuadre.
        Devuelve el contador más cercano ANTES O IGUAL a la fecha final.

        Ejemplo:
        Si fecha_limite = '2025-11-25 03:20:00',
        tomará el contador con 'at' <= esa hora, pero el más cercano posible.
        """
        df = self._read_df()

        # Filtrar por máquina
        df = df[df["machine_id"] == str(machine_id)]

        if df.empty:
            return None

        # Filtrar contadores que estén antes o igual al final del rango
        df = df[df["at"] <= fecha_limite]

        if df.empty:
            return None

        # Ordenar ascendente para tomar el MÁS CERCANO al final
        df = df.sort_values(by="at", ascending=True)

        row = df.iloc[-1].to_dict()  # último registro antes de la fecha final

        return self.get_by_id(int(row["id"]))
