# -------------------------------------------
# back/domain/machines/update.py
# Función esperada: actualizar_machine(machine_id, cambios, clock, machines_repo, places_repo, actor)
#
# Entradas:
#   - machine_id: int (debe existir).
#   - cambios: dict con campos editables (code, denomination_value, place_id, participation_rate, is_active).
#   - clock: hora local (inyectable).
#   - machines_repo: repositorio de máquinas.
#   - places_repo: para validar place_id (si cambia).
#   - actor: usuario para auditoría.
#
# Validaciones:
#   - machine_id existente.
#   - Si cambia code: no duplicar con otra máquina.
#   - Si cambia denomination_value: >= 0.
#   - Si cambia participation_rate: en [0,1].
#   - Si cambia place_id: place debe existir e is_active=True.
#
# Procesamiento:
#   1) Cargar registro actual.
#   2) Aplicar cambios válidos (solo campos permitidos).
#   3) updated_at/by = clock()/actor.
#   4) Guardar en repo.
#
# Salida:
#   - Dict actualizado {id, code, denomination_value, place_id, participation_rate, is_active}.
#
# Errores:
#   - NotFoundError, ValueError (duplicado/valores fuera de rango/place inválido).
# -------------------------------------------
