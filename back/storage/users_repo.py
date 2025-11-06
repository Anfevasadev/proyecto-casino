# -------------------------------------------
# back/storage/users_repo.py
# Propósito:
#   - Operaciones CRUD contra data/users.csv usando pandas, expuestas
#     como funciones simples que manipulan filas/dicts.
#
# CSV (encabezado esperado):
#   id,username,password,role,is_active,is_deleted,
#   created_at,created_by,updated_at,updated_by,deleted_at,deleted_by
#
# Funciones sugeridas:
#   1) listar(only_active: bool | None = None, limit: int | None = None, offset: int = 0) -> list[dict]
#      - Lee users.csv, opcionalmente filtra por is_active, aplica paginación,
#        y devuelve lista de dicts públicos (sin password) o completa si el dominio lo pide.
#
#   2) obtener_por_id(user_id: int) -> dict | None
#      - Retorna dict de la fila que coincida con id o None si no existe.
#
#   3) existe_username(username: str, exclude_id: int | None = None) -> bool
#      - Valida unicidad; si exclude_id viene, ignora ese registro (útil para updates).
#
#   4) insertar_fila(row: dict) -> None
#      - Carga DF, concatena nueva fila (asegurando columnas), escribe CSV.
#      - La generación de id la hace el dominio o un helper previo (next_id).
#
#   5) actualizar_fila(user_id: int, cambios: dict) -> dict | None
#      - Busca por id, aplica cambios de columnas existentes, guarda y retorna la fila resultante.
#      - Si no existe, retorna None.
#
#   6) desactivar(user_id: int, clock: callable, actor: str, usar_is_deleted: bool = False) -> bool
#      - Marca is_active=False. Si usar_is_deleted=True, setea is_deleted=True + deleted_at/by.
#      - Actualiza updated_at/by.
#      - Retorna True si se modificó, False si no existe.
#
# Consideraciones:
#   - Password NO se cifra (requisito académico).
#   - Mantener separación de responsabilidades: validaciones complejas en domain.
#   - Al listar, por defecto ocultar password (o retornarlo y dejar que la API filtre).
# -------------------------------------------
