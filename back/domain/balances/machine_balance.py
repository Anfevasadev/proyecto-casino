# -------------------------------------------
# back/domain/balances/machine_balance.py
# Función principal: calcular_cuadre_maquina(machine_id, period_start, period_end,
#                                             counters_repo, machines_repo, balances_repo,
#                                             clock, actor, persist=True, lock=False)
#
# Objetivo:
#   - Calcular los totales IN/OUT/JACKPOT/BILLETERO de una máquina en un periodo (incluyendo extremos).
#   - Calcular utilidad_total = IN - (OUT + JACKPOT).
#   - Persistir en machine_balances.csv (si persist=True) con generated_at/by y flag locked.
#
# Entradas:
#   - machine_id: int (debe existir y estar activo).
#   - period_start / period_end: fechas o datetimes locales ('YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS').
#   - counters_repo: para obtener registros filtrados por machine_id y rango 'at'.
#   - machines_repo: para validar machine_id y obtener place_id si hiciera falta.
#   - balances_repo: para escribir/actualizar en machine_balances.csv.
#   - clock: función de hora local; actor: str para auditoría.
#   - persist (bool): si True, escribe/actualiza el CSV de balances.
#   - lock (bool): si True, marca el registro como locked al guardar.
#
# Validaciones:
#   - machine_id existente y máquina is_active=True.
#   - period_start <= period_end (mismo huso local).
#   - Si existe un balance previo del mismo machine_id+periodo y está locked=True,
#     NO permitir sobrescritura (lanzar excepción).
#
# Procesamiento (cálculo):
#   1) Obtener todos los counters con machine_id y 'at' dentro de [period_start, period_end].
#   2) Sumar columnas: in_amount, out_amount, jackpot_amount, billetero_amount (tratar nulos como 0).
#   3) utilidad_total = in_total - (out_total + jackpot_total).
#
# Procesamiento (persistencia):
#   - Si persist=True:
#       a) Buscar si ya hay registro para (machine_id, period_start, period_end).
#       b) Si no está locked, crear/actualizar fila con:
#            in_total, out_total, jackpot_total, billetero_total, utilidad_total,
#            generated_at=clock(), generated_by=actor, locked=lock (según parámetro).
#       c) Escribir al CSV de machine_balances vía balances_repo.
#
# Salida:
#   - Dict con:
#       { machine_id, period_start, period_end,
#         in_total, out_total, jackpot_total, billetero_total, utilidad_total,
#         generated_at, generated_by, locked }
#
# Errores:
#   - NotFoundError si la máquina no existe o está inactiva.
#   - ValueError si el periodo es inválido (start > end).
#   - LockedError si existe un registro locked para ese identificador de periodo.
#
# Notas:
#   - pandas puede utilizarse en repos para sumar de forma robusta (manejo de NaN).
#   - Mantener cálculos deterministas; evitar redondeos agresivos (usar decimales coherentes).
# -------------------------------------------
