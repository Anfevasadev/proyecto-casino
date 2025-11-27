# -------------------------------------------
# back/core/settings.py
# Propósito:
#   - Proveer constantes de configuración y utilidades pequeñas relacionadas a configuración.
#
# Contenido esperado:
#   1) Rutas base:
#      - BASE_DIR: directorio raíz del repo.
#      - DATA_DIR: BASE_DIR / "data" (donde residen los CSV).
#
#   2) Fechas/Horas:
#      - TIME_FMT: string con el formato 'YYYY-MM-DD HH:MM:SS' (hora local).
#      - CLOCK: función ligera que retorne la hora local como string con TIME_FMT.
#        * Entradas: ninguna.
#        * Salida: str con hora local (no zona; el proyecto trabaja en local time).
#        * Uso: inyectar "CLOCK" en dominio para auditoría (created_at/updated_at).
#
#   3) Paginación (convenciones):
#      - DEFAULT_LIMIT = 50
#      - MAX_LIMIT = 100
#
#   4) Enumeraciones/Constantes de dominio:
#      - ROLES_PERMITIDOS = {'admin','operador','soporte'}  (para validaciones sencillas)
#
# Notas:
#   - No incluir secretos ni credenciales.
#   - Evitar leer variables de entorno para mantenerlo simple (académico).
# -------------------------------------------

from pathlib import Path
from datetime import timedelta

# Base dirs
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

# Time format
TIME_FMT = "%Y-%m-%d %H:%M:%S"

# Pagination
DEFAULT_LIMIT = 50
MAX_LIMIT = 100

# Roles
ROLES_PERMITIDOS = {"admin", "operador", "soporte"}

# JWT / Auth settings (simple, for dev)
SECRET_KEY = "change-me-in-prod-very-secret-key"
ALGORITHM = "HS256"
# Token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours

# Convenience
ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
