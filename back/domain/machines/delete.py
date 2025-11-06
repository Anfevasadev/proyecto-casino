# -------------------------------------------
# back/domain/machines/delete.py
# Función esperada: desactivar_machine(machine_id, clock, machines_repo, actor)
#
# Política de borrado lógico:
#   - En machines: SOLO is_active se utiliza.
#   - "Eliminar" = set is_active=False (no se quita la fila).
#
# Entradas:
#   - machine_id: int (debe existir).
#   - clock: hora local (para auditoría).
#   - machines_repo: repositorio máquinas.
#   - actor: usuario que realiza la acción.
#
# Procesamiento:
#   1) Verificar que machine_id exista.
#   2) Cambiar is_active=False.
#   3) updated_at/by = clock()/actor.
#   4) Guardar registro.
#
# Salida:
#   - {"deleted": True, "id": machine_id}
#
# Errores:
#   - NotFoundError si no existe.
# -------------------------------------------
