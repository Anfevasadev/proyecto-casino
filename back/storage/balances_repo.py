# -------------------------------------------
# back/storage/balances_repo.py
# Propósito:
#   - Persistir y consultar balances (cuadres) en:
#       * data/machine_balances.csv
#       * data/casino_balances.csv
#
# CSV (encabezados esperados):
#   machine_balances.csv:
#     id,machine_id,period_start,period_end,in_total,out_total,
#     jackpot_total,billetero_total,utilidad_total,generated_at,generated_by,locked
#
#   casino_balances.csv:
#     id,place_id,period_start,period_end,in_total,out_total,
#     jackpot_total,billetero_total,utilidad_total,generated_at,generated_by,locked
#
# Funciones sugeridas (máquina):
#   1) listar_machine_balances(machine_id: int | None = None,
#                              date_from: str | None = None, date_to: str | None = None,
#                              limit: int | None = 100, offset: int = 0) -> list[dict]
#      - Filtros opcionales por machine_id y periodo (period_start/period_end).
#
#   2) insertar_machine_balance(row: dict) -> None
#      - Inserta fila calculada por domain (ya con utilidad_total, etc.).
#
#   3) obtener_machine_balance_por_id(balance_id: int) -> dict | None
#      - Fila por id o None.
#
#   4) lock_machine_balance(balance_id: int, actor: str, clock: callable) -> bool
#      - Marca locked=True y actualiza generated_by/at si se define política.
#
# Funciones (casino):
#   5) listar_casino_balances(place_id: int | None = None, date_from: str | None = None,
#                             date_to: str | None = None, limit: int | None = 100, offset: int = 0) -> list[dict]
#
#   6) insertar_casino_balance(row: dict) -> None
#
#   7) obtener_casino_balance_por_id(balance_id: int) -> dict | None
#
#   8) lock_casino_balance(balance_id: int, actor: str, clock: callable) -> bool
#
# Consideraciones:
#   - Los cálculos se hacen en domain/balances/*. Aquí solo se persiste y consulta.
#   - Mantener consistencia de tipos: totales como float, fechas como str local.
#   - "locked" impide que un proceso de recálculo reescriba ese registro (política).
# -------------------------------------------
