# -------------------------------------------
# back/domain/users/update.py
# Función esperada: actualizar_usuario(user_id, cambios, clock, repo, actor)
#
# Entradas:
#   - user_id: int.
#   - cambios: dict con campos editables (role, is_active, password, username opcional).
#   - clock: función hora local.
#   - repo: repositorio users.
#   - actor: str para auditoría (updated_by).
#
# Validaciones:
#   - Usuario debe existir.
#   - Si cambia username: verificar que no exista otro con ese username.
#   - Si cambia role: validar ∈ {'admin','operador','soporte'}.
#
# Procesamiento:
#   1) Cargar usuario.
#   2) Aplicar cambios permitidos.
#   3) Actualizar updated_at=clock(), updated_by=actor.
#   4) Guardar en repo.
#
# Salida:
#   - Dict {id, username, role, is_active} actualizado.
#
# Errores:
#   - NotFoundError si user_id no existe.
#   - ValueError por duplicado/role inválido.
# -------------------------------------------
