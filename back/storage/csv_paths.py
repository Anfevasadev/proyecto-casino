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
# back/storage/csv_paths.py
# Rutas a los CSV que usa el sistema

import os

BASE_PATH = os.path.join(os.getcwd(), "data")

PLACES_CSV_PATH = os.path.join(BASE_PATH, "places.csv")
MACHINES_CSV_PATH = os.path.join(BASE_PATH, "machines.csv")
COUNTERS_CSV_PATH = os.path.join(BASE_PATH, "counters.csv")
USERS_CSV_PATH = os.path.join(BASE_PATH, "users.csv")
LOGS_CSV_PATH = os.path.join(BASE_PATH, "logs.csv")
MACHINE_BALANCES_CSV_PATH = os.path.join(BASE_PATH, "machine_balances.csv")
CASINO_BALANCES_CSV_PATH = os.path.join(BASE_PATH, "casino_balances.csv")
