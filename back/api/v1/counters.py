# -------------------------------------------
# back/api/v1/counters.py
# Propósito:
#   - Exponer endpoints HTTP (FastAPI) para registrar y consultar "contadores"
#     por máquina: IN, OUT, JACKPOT, BILLETERO.
#
# Router esperado:
#   - Declarar "router" = APIRouter() y definir las rutas bajo /api/v1/counters.
#
# Modelos:
#   - Importar desde back/models/counters.py:
#       * CounterIn  (entrada para crear)
#       * CounterUpdate (si se habilita corrección)
#       * CounterOut (respuesta al cliente)
#
# Dependencias:
#   - from fastapi import APIRouter, HTTPException, Query, Path, Depends, status
#   - from ..deps import get_repos, pagination_params (si se usa)
#   - Repos necesarios (obtenidos vía get_repos):
#       * counters_repo (lectura/escritura CSV de counters)
#       * machines_repo (validar existencia y estado de la máquina)
#       * logs_repo (opcional para auditoría de cambios)
#   - Funciones de dominio correspondientes en back/domain/counters/*:
#       * create_counter, listar_counters, obtener_counter, actualizar_counter (opcional)
#
# Endpoints sugeridos:
#   1) GET /    (listar)
#      - Query params:
#         * machine_id: int | None (filtrar por máquina)
#         * date_from: str | None ('YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS')
#         * date_to:   str | None (mismo formato)
#         * limit: int (tope recomendado <= 100), offset: int (>= 0)
#         * sort_by (opcional): 'at' o 'id' (default 'at'), ascending: bool (default True)
#      - Validaciones:
#         * limit/offset >= 0, formatear y validar fechas si vienen.
#      - Flujo:
#         * Llamar domain.listar_counters(...) con repos.
#      - Respuesta:
#         * 200 OK → list[CounterOut] con los campos del CSV (sin auditoría por defecto)
#
#   2) GET /{counter_id}    (detalle)
#      - Path param: counter_id: int
#      - Flujo:
#         * Llamar domain.obtener_counter(repo, counter_id).
#      - Respuestas:
#         * 200 OK → CounterOut
#         * 404 Not Found si no existe
#
#   3) POST /    (crear registro de contador)
#      - Body: CounterIn
#      - Validaciones principales (delegar a dominio):
#         * machine_id existente y máquina is_active == True
#         * Montos ≥ 0 (in/out/jackpot/billetero)
#         * 'at' correcto; si no viene, usar clock() en dominio
#      - Flujo:
#         * domain.create_counter(data, clock, counters_repo, machines_repo, actor='system' o user)
#      - Respuestas:
#         * 201 Created → CounterOut con id asignado
#         * 404 Not Found si machine_id no existe o está inactiva
#         * 400 Bad Request si montos/fechas inválidas
#
#   4) PUT /{counter_id}    (opcional: corrección de registro)
#      - Body: CounterUpdate
#      - Política:
#         * En el curso, el historial idealmente es inmutable. Si se habilita corrección,
#           registrar log del cambio (logs_repo) con quién/cuándo/qué se cambió.
#      - Validaciones:
#         * counter_id existente
#         * Si cambia machine_id: validar que exista y esté activa
#         * Montos ≥ 0; 'at' válido
#      - Respuestas:
#         * 200 OK → registro corregido
#         * 404 si no existe
#         * 400 por datos inválidos
#
# Códigos de estado recomendados:
#   - GET lista/detalle: 200
#   - POST crear: 201
#   - PUT update: 200
#   - Errores: 400 (validación), 404 (no encontrado)
#
# Notas:
#   - Las conversiones/lecturas de CSV se hacen en repos (storage/*_repo.py).
#   - Fecha/hora en formato local 'YYYY-MM-DD HH:MM:SS' (consistencia con el proyecto).
# -------------------------------------------
