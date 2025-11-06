# -------------------------------------------
# back/domain/places/update.py
# Función: actualizar_place(place_id, cambios, clock, repo, actor)
#
# Entradas:
#   - place_id: int
#   - cambios: dict (name, address, is_active)
#   - clock, repo, actor
#
# Validaciones:
#   - place existente
#   - si cambia name, no duplicar con otro registro
#
# Procesamiento:
#   - Aplicar cambios permitidos
#   - updated_at/by = clock()/actor
#   - Guardar
#
# Salida:
#   - {id, name, address, is_active}
#
# Errores:
#   - NotFoundError, ValueError (duplicado)
# -------------------------------------------
