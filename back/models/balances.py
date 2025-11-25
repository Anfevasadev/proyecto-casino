# -------------------------------------------
# back/models/balances.py
# Propósito:
#   - Contratos Pydantic para "cuadres" (consolidados) por máquina y por lugar.
#
# Contexto:
#   - Estos datos suelen ser RESULTADO de cálculos (domain/balances/*) a partir de counters.
#   - Se persisten en CSV: machine_balances.csv y casino_balances.csv.
#
# machine_balances.csv (por máquina):
#   - id: int
#   - machine_id: int
#   - period_start: str (date 'YYYY-MM-DD')
#   - period_end: str (date 'YYYY-MM-DD')
#   - in_total/out_total/jackpot_total/billetero_total: float (≥ 0)
#   - utilidad_total: float (= in_total - (out_total + jackpot_total))
#   - generated_at: str (datetime local)
#   - generated_by: str
#   - locked: bool
#
# casino_balances.csv (por lugar):
#   - id: int
#   - place_id: int
#   - period_start/period_end: str (date)
#   - in_total/out_total/jackpot_total/billetero_total: float
#   - utilidad_total: float
#   - generated_at: str (datetime local)
#   - generated_by: str
#   - locked: bool
#
# Modelos esperados:
#   1) MachineBalanceIn (si se permite solicitar cálculo/persistencia):
#       - machine_id: int
#       - period_start: str ('YYYY-MM-DD')
#       - period_end: str ('YYYY-MM-DD')
#       - locked: bool | None (opcional; default False al generar)
#     Validaciones:
#       * period_start ≤ period_end (comparación de fechas).
#
#   2) MachineBalanceOut:
#       - id, machine_id, period_start, period_end,
#         in_total, out_total, jackpot_total, billetero_total,
#         utilidad_total, generated_at, generated_by, locked
#
#   3) CasinoBalanceIn (similar para lugar):
#       - place_id: int
#       - period_start: str
#       - period_end: str
#       - locked: bool | None
#     Validaciones:
#       * period_start ≤ period_end.
#
#   4) CasinoBalanceOut:
#       - id, place_id, period_start, period_end,
#         in_total, out_total, jackpot_total, billelero_total,
#         utilidad_total, generated_at, generated_by, locked
#
# Consideraciones:
#   - Estos modelos son más de "salida" porque el cálculo se hace en domain.
#     MachineBalanceIn/CasinoBalanceIn sirven si se expone un endpoint que "ordena"
#     generar el balance (domain valida y produce registro).
#   - Validar formato de fechas y que los totales sean ≥ 0 (en Out normalmente ya vienen validados).
# -------------------------------------------
from pydantic import BaseModel
from datetime import date, datetime


class MachineBalance(BaseModel):
    id: int
    machine_id: int
    period_start: date
    period_end: date
    in_total: float
    out_total: float
    jackpot_total: float
    billetero_total: float
    utilidad_total: float
    generated_at: datetime
    generated_by: str
    locked: bool = False
