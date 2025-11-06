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
