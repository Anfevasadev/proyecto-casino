# -------------------------------------------
# back/api/v1/balances.py
# Propósito:
#   - Exponer endpoints para calcular y consultar "cuadres" (balances) a partir
#     de los contadores:
#       * Cuadre por máquina (machine_balances.csv)
#       * Cuadre por lugar/casino (casino_balances.csv)
#
# Router esperado:
#   - Declarar "router" = APIRouter() y montar bajo /api/v1/balances (o subrutas).
#
# Modelos:
#   - Importar desde back/models/balances.py:
#       * MachineBalanceIn, MachineBalanceOut
#       * CasinoBalanceIn, CasinoBalanceOut
#
# Dependencias:
#   - from fastapi import APIRouter, HTTPException, Query, Path, Depends, status
#   - from ..deps import get_repos, pagination_params (si se usa)
#   - Repos:
#       * counters_repo (leer contadores en rango/criterios)
#       * machines_repo (validar máquinas)
#       * places_repo   (validar lugares)
#       * balances_repo (persistir/consultar balances)
#       * logs_repo (opcional para auditar generación/cierre)
#   - Dominio (back/domain/balances/*):
#       * calcular_cuadre_maquina(counters_repo, machine_id, periodo, ...)
#       * calcular_cuadre_casino(counters_repo, place_id, periodo, ...)
#
# Rutas sugeridas (dividir por subrecurso):
#   [Máquinas]
#   1) GET  /machines
#      - Query:
#         * machine_id: int | None (si se quiere filtrar)
#         * date_from, date_to: str ('YYYY-MM-DD')
#         * limit, offset
#      - Flujo:
#         * Consultar balances existentes via balances_repo.listar_machine_balances(...)
#      - Respuesta:
#         * 200 → list[MachineBalanceOut]
#
#   2) POST /machines/generate
#      - Body: MachineBalanceIn {machine_id, period_start, period_end, locked?}
#      - Validaciones (dominio):
#         * machine_id existe y está activa
#         * period_start ≤ period_end (fechas válidas)
#      - Flujo:
#         * Usar dominio para:
#             a) Obtener counters del periodo (counters_repo)
#             b) Calcular totales: in/out/jackpot/billetero y utilidad
#             c) Persistir en balances_repo (generar id, generated_at/by)
#      - Respuesta:
#         * 201 → MachineBalanceOut (registro recién generado)
#         * 404 si machine/place inexistente/inactivo
#         * 400 si periodo inválido
#
#   3) GET  /machines/{balance_id}
#      - Detalle de un balance por máquina
#      - 200 → MachineBalanceOut; 404 si no existe
#
#   4) POST /machines/{balance_id}/lock
#      - Propósito: "cerrar" (locked=true) un balance para evitar recálculos
#      - Flujo:
#         * balances_repo.lock_machine_balance(balance_id, actor, clock)
#      - Respuesta:
#         * 200 → {"locked": true, "id": balance_id}
#         * 404 si no existe
#
#   [Casinos/Lugares]
#   5) GET  /places
#      - Query: place_id, date_from, date_to, limit, offset
#      - 200 → list[CasinoBalanceOut]
#
#   6) POST /places/generate
#      - Body: CasinoBalanceIn {place_id, period_start, period_end, locked?}
#      - Validaciones:
#         * place_id existe y está activo
#         * period_start ≤ period_end
#      - Flujo:
#         * dominio.calcular_cuadre_casino(...) suma totales de máquinas del lugar en el periodo
#         * persistir con balances_repo.insertar_casino_balance(...)
#      - Respuestas:
#         * 201 → CasinoBalanceOut
#         * 404 / 400 según validación
#
#   7) GET  /places/{balance_id}
#      - 200 → CasinoBalanceOut; 404 si no existe
#
#   8) POST /places/{balance_id}/lock
#      - 200 → {"locked": true, "id": balance_id}; 404 si no existe
#
# Consideraciones generales:
#   - "locked" evita sobrescritura por procesos futuros (documentar política en README).
#   - Las fechas son cadenas en formato local 'YYYY-MM-DD' para period_start/period_end.
#   - Para MachineBalanceOut/CasinoBalanceOut, los totales deben ser ≥ 0 y
#     utilidad_total = in_total - (out_total + jackpot_total).
#   - Exportes a CSV/PDF/Excel de reportes NO se implementan aquí; esto es solo API.
# -------------------------------------------
