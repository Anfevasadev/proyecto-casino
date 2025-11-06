# -------------------------------------------
# back/storage/csv_paths.py
# Propósito:
#   - Centralizar las rutas a cada archivo CSV dentro de /data.
#
# Contenido esperado:
#   - BASE_DIR: ruta raíz del proyecto (Path).
#   - DATA_DIR: BASE_DIR / "data".
#   - Constantes Path por archivo:
#       USERS_CSV, PLACES_CSV, MACHINES_CSV, COUNTERS_CSV,
#       MBAL_CSV (machine_balances.csv), CBAL_CSV (casino_balances.csv),
#       LOGS_CSV.
#
# Uso:
#   - Los módulos repo importan aquí las rutas y NO hardcodean strings.
#
# Consideraciones:
#   - No crear archivos aquí; solo definir rutas.
#   - Mantener nombres de constantes en MAYÚSCULAS para claridad.
# -------------------------------------------
