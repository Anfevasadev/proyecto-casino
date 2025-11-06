# -------------------------------------------
# back/domain/places/read.py
# Funciones: listar_places(repo, only_active=True, limit=50, offset=0), obtener_place(repo, place_id)
#
# Validaciones:
#   - limit/offset >= 0, tope de limit (100 sugerido).
#
# Procesamiento (listar):
#   - Cargar CSV, filtrar is_active si aplica, ordenar por id, paginar.
#
# Salida (listar):
#   - Lista de dicts: [{id, name, address, is_active}, ...]
#
# Procesamiento (obtener):
#   - Buscar por id; si no existe -> NotFoundError.
#
# Salida (obtener):
#   - {id, name, address, is_active}
# -------------------------------------------
