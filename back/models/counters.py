# -------------------------------------------
# back/models/counters.py
# Propósito:
#   - Contratos Pydantic para "contadores" (registros de IN/OUT/JACKPOT/BILLETERO).
#
# Campos relevantes (alineados a CSV):
#   - machine_id: int (FK lógica).
#   - at: str (datetime local 'YYYY-MM-DD HH:MM:SS').
#   - in_amount, out_amount, jackpot_amount, billetero_amount: float/Decimal (≥ 0).
#
# Modelos esperados:
#   1) CounterIn (crear):
#       - machine_id: int (obligatorio).
#       - at: str | None (opcional; si no viene, la capa de dominio puede usar clock()).
#       - in_amount: float (>= 0, default 0.0).
#       - out_amount: float (>= 0, default 0.0).
#       - jackpot_amount: float (>= 0, default 0.0).
#       - billetero_amount: float (>= 0, default 0.0).
#     Validaciones:
#       * Formato de 'at' si viene: 'YYYY-MM-DD HH:MM:SS'.
#       * Todos los montos ≥ 0.
#
#   2) CounterUpdate (corrección opcional):
#       - machine_id: int | None (si viene, validar existencia).
#       - at: str | None (validar formato si viene).
#       - in_amount/out_amount/jackpot_amount/billetero_amount: float | None (≥ 0 si vienen).
#
#   3) CounterOut (salida):
#       - id: int
#       - machine_id: int
#       - at: str
#       - in_amount: float
#       - out_amount: float
#       - jackpot_amount: float
#       - billetero_amount: float
#
# Notas:
#   - Campos de auditoría (created_at/by, updated_at/by) no se exponen por defecto
#     en Out para mantener la respuesta simple; si se requiere, crear otro modelo.
# -------------------------------------------
