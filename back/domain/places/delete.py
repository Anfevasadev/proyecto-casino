# -------------------------------------------
# back/domain/places/delete.py
# Función: desactivar_place(place_id, clock, repo, actor)
#
# Política:
#   - Borrado lógico: is_active=False (no eliminar fila).
#
# Entradas:
#   - place_id, clock, repo, actor
#
# Procesamiento:
#   1) Verificar existencia
#   2) is_active=False
#   3) updated_at/by = clock()/actor
#   4) Guardar
#
# Efectos colaterales (a considerar en dominio):
#   - Bloquear creación de nuevas máquinas en este place (validación cruzada).
#
# Salida:
#   - {"deleted": True, "id": place_id}
#
# Errores:
#   - NotFoundError
# -------------------------------------------
