# -------------------------------------------
# back/domain/places/create.py
# Función esperada: create_place(data, clock, repo, actor)
#
# Entradas:
#   - data: {name, address?, is_active=True}
#   - clock: hora local
#   - repo: places_repo con helpers: next_id(), existe_name(name), insertar_fila(...)
#   - actor: usuario que opera
#
# Validaciones:
#   - name obligatorio y único (no repetido).
#
# Procesamiento:
#   1) id = next_id()
#   2) Construir fila con auditoría: created_at/by, updated_at/by.
#   3) Guardar.
#
# Salida:
#   - {id, name, address, is_active}
#
# Errores:
#   - Duplicado de name -> ValueError/DomainError.
# -------------------------------------------
