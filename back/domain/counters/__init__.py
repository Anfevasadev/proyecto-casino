# -------------------------------------------
# back/domain/counters/__init__.py
# Propósito:
#   Documentar reglas para "contadores" (IN, OUT, JACKPOT, BILLETERO).
#
# Entidad counters (CSV: data/counters.csv):
#   - Campos: id, machine_id, at (datetime local), in_amount, out_amount,
#             jackpot_amount, billetero_amount, auditoría created_/updated_.
#
# Políticas:
#   - Historial preferiblemente inmutable: no borrar; si hay corrección, crear
#     un nuevo registro y (opcional) registrar un log describiendo la corrección.
#   - Si se habilita "actualizar", debe quedar traza en logs (quién, cuándo, qué).
#
# Validaciones clave:
#   - machine_id debe existir y referirse a una máquina is_active=True.
#   - amounts ≥ 0.
#   - at en formato local 'YYYY-MM-DD HH:MM:SS'.
#
# Operaciones previstas:
#   - create_counter(data)
#   - listar_counters(filtros)
#   - obtener_counter(id)
#   - actualizar_counter(id, cambios)  # solo para correcciones, opcional
# -------------------------------------------
