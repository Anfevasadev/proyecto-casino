# -------------------------------------------
# back/domain/counters/read.py
# Funciones:
#   - listar_counters(repo, machine_id=None, date_from=None, date_to=None, limit=100, offset=0)
#   - obtener_counter(repo, counter_id)
#
# Entradas:
#   - machine_id: filtrar por máquina (opcional).
#   - date_from/date_to: strings 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS' para acotar periodo.
#   - limit/offset: paginación (validar >=0; tope de limit).
#
# Procesamiento (listar):
#   1) Cargar datos.
#   2) Filtrar por machine_id si viene.
#   3) Filtrar por rango de fechas 'at' si vienen date_from/to (inclusivo).
#   4) Orden por 'at' ascendente (sugerido) o por id.
#   5) Aplicar paginación.
#
# Salida (listar):
#   - Lista de dicts con los campos del CSV (id, machine_id, at, in/out/jackpot/billetero, audit).
#
# Procesamiento (obtener):
#   - Buscar por id; si no existe -> NotFoundError.
#
# Salida (obtener):
#   - Dict con el registro completo.
# -------------------------------------------
