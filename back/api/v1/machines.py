# -------------------------------------------
# back/api/v1/machines.py
# Propósito:
#   Endpoints para gestionar "máquinas" (por lugar) en CSV.
#
# Router esperado:
#   - Variable "router" = APIRouter()
#
# Modelos (importar de back/models/machines.py):
#   - MachineIn: code, denomination_value, place_id, participation_rate, is_active.
#   - MachineOut: id, code, denomination_value, place_id, participation_rate, is_active.
#
# Dependencias:
#   - get_repos() para acceder a machines_repo (y places_repo si se valida FK).
#   - pagination_params() para listar.
#   - filter_active_param() (bool) para traer solo activas si se desea.
#
# Endpoints (sugeridos):
#   1) GET /
#      - Query:
#           * place_id (int, opcional) para filtrar por lugar.
#           * only_active (bool=true), limit, offset.
#      - Procesamiento: leer máquinas, aplicar filtros y paginación.
#      - Salida (200): lista MachineOut.
#
#   2) GET /{machine_id}
#      - Path: machine_id (int).
#      - Procesamiento: obtener por id o 404.
#      - Salida (200): MachineOut.
#
#   3) POST /
#      - Body: MachineIn.
#      - Validaciones:
#           * code no repetido (único).
#           * place_id existente en places (FK lógica).
#           * participation_rate ∈ [0,1].
#           * denomination_value >= 0.
#      - Procesamiento: asignar id, guardar máquina.
#      - Salida (201): MachineOut.
#      - Errores: 400 (duplicado/valores inválidos), 404 (place_id inexistente).
#
#   4) PUT /{machine_id}
#      - Body: campos editables (code, denomination_value, place_id, participation_rate, is_active).
#      - Validaciones:
#           * machine_id existente.
#           * si cambia code, no duplicar.
#           * si cambia place_id, debe existir.
#           * participation_rate ∈ [0,1], denomination_value >= 0.
#      - Procesamiento: actualizar fila y guardar.
#      - Salida (200): MachineOut actualizada.
#      - Errores: 404/400.
#
#   5) DELETE /{machine_id}
#      - Borrado lógico:
#         * En machines NO hay is_deleted, solo is_active.
#         * "Eliminar" = is_active=false.
#      - Validaciones: machine_id existente.
#      - Procesamiento: marcar is_active=false.
#      - Salida (200): {"deleted": true, "id": <machine_id>}
#
# Reglas adicionales relevantes:
#   - Si el lugar (place_id) está inactivo, no permitir crear nuevas máquinas en ese lugar.
#   - Para listados, podría ofrecer "sort_by" (code asc/desc) si se desea (opcional).
#
# Librerías:
#   - fastapi (APIRouter, HTTPException, Query, status)
#   - pydantic (modelos)
#
# Notas:
#   - El manejo de CSV/pandas se hace en storage/machines_repo.py. Aquí solo orquestamos.
#   - El borrado lógico es un "toggle" de is_active a false; no se elimina la fila.
# -------------------------------------------
