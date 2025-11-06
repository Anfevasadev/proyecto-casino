# -------------------------------------------
# back/domain/counters/update.py
# Función: actualizar_counter(counter_id, cambios, clock, repo, machines_repo, actor, logs_repo=None)
#
# Contexto:
#   - Se permite para CORRECCIONES. Idealmente el historial es inmutable; si se prefiere,
#     implementar como "nueva fila corrección" y dejar la previa intacta. Aquí se documenta
#     la opción de actualización directa si el equipo decide permitirla.
#
# Entradas:
#   - counter_id: int
#   - cambios: dict con campos editables (at, in_amount, out_amount, jackpot_amount, billetero_amount)
#   - clock, repo (counters), machines_repo (si cambia machine_id), actor, logs_repo opcional
#
# Validaciones:
#   - counter_id existente.
#   - Si cambia machine_id: debe existir y estar activa.
#   - amounts >= 0; 'at' válido.
#
# Procesamiento (si se actualiza en sitio):
#   1) Cargar registro.
#   2) Aplicar cambios válidos.
#   3) updated_at/by = clock()/actor.
#   4) Guardar.
#   5) logs_repo.insert(event_type='update', entity_type='counter', entity_id=counter_id, description='corrección ...')
#
# Alternativa (si se hace corrección por nueva fila):
#   - Crear nuevo registro con valores corregidos, referenciando el original en logs/description.
#
# Salida:
#   - Dict con registro actualizado (o el nuevo, si se hizo corrección por nueva fila).
#
# Errores:
#   - NotFoundError, ValueError (validaciones).
# -------------------------------------------
