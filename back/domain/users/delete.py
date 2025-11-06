# -------------------------------------------
# back/domain/users/delete.py
# Función esperada: desactivar_usuario(user_id, clock, repo, actor)
#
# Política de borrado lógico en users:
#   - Mínimo: poner is_active=False.
#   - (Opcional) Si se usa is_deleted: poner is_deleted=True y setear deleted_at/by.
#   - Documentar política elegida en README para consistencia.
#
# Entradas:
#   - user_id: int.
#   - clock: función hora local.
#   - repo: repositorio users.
#   - actor: str para auditoría.
#
# Procesamiento:
#   1) Verificar existencia.
#   2) Cambiar flags (is_active=False; si aplica, is_deleted=True).
#   3) Actualizar updated_at/by y (si aplica) deleted_at/by.
#   4) Guardar.
#
# Salida:
#   - Dict sencillo: {"deleted": True, "id": user_id}
#
# Errores:
#   - NotFoundError si no existe.
# -------------------------------------------
