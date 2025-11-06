# -------------------------------------------
# back/domain/machines/read.py
# Funciones esperadas:
#   - listar_machines(machines_repo, place_id=None, only_active=True, limit=50, offset=0, sort_by="id")
#   - obtener_machine(machines_repo, machine_id)
#
# Entradas:
#   - machines_repo: repositorio CSV de máquinas.
#   - place_id: int opcional para filtrar máquinas de un lugar.
#   - only_active: bool (True por defecto) para filtrar is_active=True.
#   - limit/offset: ints no negativos (imponer tope a limit, p.ej. 100).
#   - sort_by: string opcional ('id' o 'code'); ordenar ascendente.
#
# Procesamiento (listar):
#   1) Cargar DF/estructura desde repo.
#   2) Aplicar filtros:
#        - if only_active: filtrar is_active=True.
#        - if place_id: filtrar place_id igual.
#   3) Ordenar por sort_by (validar campo permitido).
#   4) Paginación: aplicar offset/limit.
#
# Salida (listar):
#   - Lista de dicts con {id, code, denomination_value, place_id, participation_rate, is_active}.
#
# Procesamiento (obtener):
#   - Buscar por id exacto.
#   - Si no existe, lanzar NotFoundError.
#
# Salida (obtener):
#   - Dict con campos públicos de la máquina.
# -------------------------------------------
