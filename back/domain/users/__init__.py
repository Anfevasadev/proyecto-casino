# -------------------------------------------
# back/domain/users/__init__.py
# Propósito:
#   Documentar la lógica de "usuarios".
#
# Entidad users (CSV: data/users.csv):
#   - Campos clave: id, username (único), password (sin cifrar), role, is_active.
#   - Auditoría: created_at/by, updated_at/by, deleted_at/by (si se usa is_deleted).
#
# Políticas:
#   - No cifrar contraseñas (requisito académico).
#   - Borrado lógico: mínimo poner is_active=False. (users.csv además tiene is_deleted;
#     si se decide usarlo, documentar en README y aquí.)
#   - Roles válidos: 'admin' | 'operador' | 'soporte'.
#
# Operaciones previstas:
#   - create_usuario(data)
#   - listar_usuarios(filtros)
#   - obtener_usuario(id)
#   - actualizar_usuario(id, cambios)
#   - desactivar_usuario(id)   # (borrado lógico)
# -------------------------------------------
