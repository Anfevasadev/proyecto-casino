# -------------------------------------------
# back/domain/users/read.py
# Funciones esperadas:
#   - listar_usuarios(repo, only_active=True, limit=50, offset=0)
#   - obtener_usuario(repo, user_id)
#
# Entradas comunes:
#   - repo: repositorio users (storage/users_repo.py) capaz de devolver DF o listas.
#   - only_active: bool para filtrar por is_active=True.
#   - limit/offset: ints para paginación (validar >=0; limitar limit a máx 100).
#
# Procesamiento (listar):
#   1) Leer datos del repo (pandas DF o lista).
#   2) Filtrar is_active si only_active=True.
#   3) Orden sugerido: por id ascendente.
#   4) Slicing por offset/limit.
#
# Salidas (listar):
#   - Lista de dicts públicos: [{id, username, role, is_active}, ...]
#
# Procesamiento (obtener):
#   1) Buscar por id exacto.
#   2) Si no existe, lanzar excepción (p.ej., NotFoundError).
#
# Salida (obtener):
#   - Dict con {id, username, role, is_active}.
# -------------------------------------------
