# -------------------------------------------
# back/domain/counters/create.py
# Función: create_counter(data, clock, counters_repo, machines_repo, actor, logs_repo=None)
#
# Entradas:
#   - data: {machine_id, at (str local), in_amount, out_amount, jackpot_amount, billetero_amount}
#   - clock: función hora local (para auditoría)
#   - counters_repo: acceso a CSV de counters (insertar_fila, next_id, etc.)
#   - machines_repo: para validar que machine_id existe y está activa
#   - actor: usuario que ejecuta
#   - logs_repo: opcional para registrar evento "create"
#
# Validaciones:
#   - machine_id existente y máquina is_active=True.
#   - amounts (in/out/jackpot/billetero) >= 0 (decimales).
#   - 'at' en formato local válido; si no viene, se puede usar clock().
#
# Procesamiento:
#   1) id = counters_repo.next_id()
#   2) Construir fila con auditoría created_at/by y updated_at/by = clock()/actor.
#   3) Insertar en CSV.
#   4) (Opcional) logs_repo.insert(event_type='create', entity_type='counter', entity_id=id, ...)
#
# Salida:
#   - Dict con los datos del registro (incluido id).
#
# Errores:
#   - NotFoundError si machine_id no existe.
#   - ValueError por amounts o 'at' inválidos.
# -------------------------------------------
