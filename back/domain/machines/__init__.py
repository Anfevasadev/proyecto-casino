# -------------------------------------------
# back/domain/machines/__init__.py
# Propósito:
#   Documentar reglas de negocio para "máquinas".
#
# Entidad machines (CSV: data/machines.csv):
#   - Campos principales:
#       id (int, PK lógico), code (string único),
#       denomination_value (decimal >= 0),
#       place_id (int, FK lógica → places.id),
#       participation_rate (decimal en [0,1]),
#       is_active (bool),
#       auditoría: created_at/by, updated_at/by (hora local 'YYYY-MM-DD HH:MM:SS').
#
# Políticas:
#   - Borrado lógico = is_active=False (no se elimina la fila).
#   - code debe ser único (no duplicar).
#   - place_id debe existir y referirse a un place is_active=True.
#   - Si el place se desactiva, el dominio debe impedir crear nuevas máquinas allí.
#   - participation_rate se interpreta como proporción (0.0 = 0%, 1.0 = 100%).
#
# Operaciones previstas:
#   - create_machine(data)
#   - listar_machines(filtros)
#   - obtener_machine(id)
#   - actualizar_machine(id, cambios)
#   - desactivar_machine(id)
#
# Notas de diseño:
#   - La lectura/escritura CSV la manejan repos en back/storage/machines_repo.py (con pandas).
#   - Este paquete debe exponer funciones "puras" (lo más posible), sin depender de FastAPI.
# -------------------------------------------
