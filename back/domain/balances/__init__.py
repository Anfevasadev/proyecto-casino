# -------------------------------------------
# back/domain/balances/__init__.py
# Propósito:
#   Documentar reglas de cálculo y persistencia de "cuadres".
#
# CSVs relevantes:
#   - counters.csv: registros base (in/out/jackpot/billetero) con 'at' (datetime local) y machine_id.
#   - machine_balances.csv: persistencia del cuadre por máquina y periodo.
#   - casino_balances.csv: persistencia del cuadre por lugar (place) y periodo.
#
# Fórmula clave:
#   utilidad = IN_TOTAL - (OUT_TOTAL + JACKPOT_TOTAL)
#   (BILLETERO_TOTAL se reporta pero no entra en la utilidad según los enunciados típicos;
#    si el docente exige otro criterio, ajustar aquí y en documentación).
#
# Políticas:
#   - "locked" (bool) en balances indica que el registro no debe recalcularse/re-escribirse.
#   - generated_at/by: cuándo y quién generó el consolidado.
#   - Periodos: típicamente por día (period_start, period_end) o por rango solicitado.
#   - Hora local siempre (importante para cortes diarios).
#
# Operaciones:
#   - calcular_cuadre_maquina(machine_id, period_start, period_end, ...)
#   - calcular_cuadre_casino(place_id, period_start, period_end, ...)
#   - persistir o actualizar (si no está locked) en los CSV respectivos mediante balances_repo.
#
# Notas:
#   - El cálculo debe agrupar registros de counters por machine_id y rango de 'at'.
#   - Para casino (place), se suman resultados de sus máquinas activas en el rango.
# -------------------------------------------
