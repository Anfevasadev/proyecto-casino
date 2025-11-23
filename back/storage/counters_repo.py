# -------------------------------------------
# back/storage/counters_repo.py
# Propósito:
#   - Operaciones para data/counters.csv (registro de contadores).
#
# CSV (encabezado esperado):
#   id,machine_id,at,in_amount,out_amount,jackpot_amount,billetero_amount,
#   created_at,created_by,updated_at,updated_by
#
# Funciones sugeridas:
#   1) listar(machine_id: int | None = None,
#             date_from: str | None = None, date_to: str | None = None,
#             limit: int | None = 100, offset: int = 0,
#             sort_by: str = "at", ascending: bool = True) -> list[dict]
#      - Filtros opcionales por machine_id y por rango de fechas 'at' (inclusivo).
#      - Ordena por 'at' (o 'id' si se prefiere).
#      - Aplica paginación.
#
#   2) obtener_por_id(counter_id: int) -> dict | None
#      - Fila por id o None.
#
#   3) insertar_fila(row: dict) -> None
#      - Concatena y guarda con columnas en orden correcto.
#
#   4) actualizar_fila(counter_id: int, cambios: dict) -> dict | None
#      - Actualiza registro (para correcciones); retorna fila resultante o None.
#
# Notas:
#   - Validación de machine_id existente debe ocurrir en domain (usando machines_repo).
#   - Manejar coerción de tipos (floats para montos, int para ids) antes de guardar.
#   - Las fechas 'at' son strings formateadas; aquí NO se transforman a datetime nativo.
# -------------------------------------------
# back/storage/counters_repo.py
# Repositorio encargado de leer los contadores desde counters.csv

import csv
from datetime import datetime
from decimal import Decimal
from .csv_paths import COUNTERS_CSV_PATH


class CounterRecord:
    """
    Modelo simple que representa un registro de contador.
    Este modelo es usado por los servicios que requieren acceder
    a los contadores de una máquina en una fecha específica.
    """
    def __init__(self, machine_id, date, in_value, out_value, jackpot, bill):
        self.machine_id = int(machine_id)
        self.date = date
        self.in_value = Decimal(in_value)
        self.out_value = Decimal(out_value)
        self.jackpot = Decimal(jackpot)
        self.bill = Decimal(bill)


class CountersRepo:
    """
    Repositorio encargado de leer el archivo counters.csv
    y devolver contadores filtrados por máquina y fecha.
    """

    def __init__(self):
        self.path = COUNTERS_CSV_PATH

    def read_all(self):
        """
        Lee todo el archivo counters.csv y devuelve objetos CounterRecord.
        """
        records = []
        with open(self.path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:

                # Convertir fecha
                date_obj = datetime.strptime(row["date"], "%Y-%m-%d").date()

                record = CounterRecord(
                    machine_id=row["machine_id"],
                    date=date_obj,
                    in_value=row["in"],
                    out_value=row["out"],
                    jackpot=row["jackpot"],
                    bill=row["bill"]
                )
                records.append(record)

        return records

    def get_counters_by_date(self, machine_id, date):
        """
        Devuelve el registro de contadores de una máquina en una fecha exacta.
        Si no hay coincidencia exacta, lanza ValueError, porque así lo requiere
        el módulo de balances.
        """

        records = self.read_all()

        for record in records:
            if record.machine_id == machine_id and record.date == date:
                return record

        raise ValueError(
            f"No hay contadores para la máquina {machine_id} en la fecha {date}"
        )
