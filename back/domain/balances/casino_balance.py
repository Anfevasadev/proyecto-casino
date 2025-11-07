# -------------------------------------------
# back/domain/balances/casino_balance.py
# Función principal: calcular_cuadre_casino(place_id, period_start, period_end,
#                                            counters_repo, machines_repo, places_repo, balances_repo,
#                                            clock, actor, persist=True, lock=False)
#
# Objetivo:
#   - Calcular el consolidado de un lugar (casino) sumando los valores de TODAS sus máquinas activas
#     en el periodo indicado.
#   - Guardar/actualizar en casino_balances.csv si persist=True.
#
# Entradas:
#   - place_id: int (debe existir y estar is_active=True).
#   - period_start / period_end: fechas/datetimes en hora local.
#   - counters_repo: para traer counters y agrupar por machine_id del place.
#   - machines_repo: para listar machines por place_id (solo activas).
#   - places_repo: para validar place_id.
#   - balances_repo: para escribir/actualizar CSV de casino_balances.
#   - clock, actor: auditoría.
#   - persist (bool), lock (bool): igual que en machine_balance.
#
# Validaciones:
#   - place_id existente y activo.
#   - period_start <= period_end.
#   - Si ya existe balance (place_id + periodo) y está locked=True, no sobrescribir.
#
# Procesamiento (cálculo):
#   1) Obtener lista de machine_ids activos del place.
#   2) Traer counters de esas máquinas dentro del periodo [start, end].
#   3) Sumar totales:
#        in_total = sum(in_amount)
#        out_total = sum(out_amount)
#        jackpot_total = sum(jackpot_amount)
#        billetero_total = sum(billetero_amount)
#   4) utilidad_total = in_total - (out_total + jackpot_total).
#
# Procesamiento (persistencia):
#   - Si persist=True:
#       a) Buscar registro existente para (place_id, period_start, period_end).
#       b) Si no está locked, crear/actualizar con:
#           in_total, out_total, jackpot_total, billetero_total, utilidad_total,
#           generated_at=clock(), generated_by=actor, locked=lock.
#       c) Guardar en casino_balances.csv vía balances_repo.
#
# Salida:
#   - Dict con:
#       { place_id, period_start, period_end,
#         in_total, out_total, jackpot_total, billetero_total, utilidad_total,
#         generated_at, generated_by, locked }
#
# Errores:
#   - NotFoundError para place inexistente/inactivo.
#   - LockedError si el balance del periodo está bloqueado.
#
# Notas:
#   - Si se requiere reporte por participación, ese cálculo se hace en otra función
#     usando participation_rate de machines (p. ej., distribuir utilidad por proporción),
#     o en la capa de reportes; no mezclar aquí para mantener responsabilidad única.
# -------------------------------------------
