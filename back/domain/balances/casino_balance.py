# -------------------------------------------
# back/domain/balances/casino_balance.py
# Función principal: calcular_cuadre_casino(place_id, period_start, period_end,
#                                            counters_repo, machines_repo, places_repo, balances_repo,
#                                            clock, actor, persist=True, lock=False)
#
# Objetivo:
#   - Calcular el consolidado de un lugar (casino) sumando los valores de TODAS sus máquinas activas
#     en el periodo indicado.
#   - Guardar/actualizar en casino_balances.csv si persist=True.
#
# Entradas:
#   - place_id: int (debe existir y estar is_active=True).
#   - period_start / period_end: fechas/datetimes en hora local.
#   - counters_repo: para traer counters y agrupar por machine_id del place.
#   - machines_repo: para listar machines por place_id (solo activas).
#   - places_repo: para validar place_id.
#   - balances_repo: para escribir/actualizar CSV de casino_balances.
#   - clock, actor: auditoría.
#   - persist (bool), lock (bool): igual que en machine_balance.
#
# Validaciones:
#   - place_id existente y activo.
#   - period_start <= period_end.
#   - Si ya existe balance (place_id + periodo) y está locked=True, no sobrescribir.
#
# Procesamiento (cálculo):
#   1) Obtener lista de machine_ids activos del place.
#   2) Traer counters de esas máquinas dentro del periodo [start, end].
#   3) Sumar totales:
#        in_total = sum(in_amount)
#        out_total = sum(out_amount)
#        jackpot_total = sum(jackpot_amount)
#        billetero_total = sum(billetero_amount)
#   4) utilidad_total = in_total - (out_total + jackpot_total).
#
# Procesamiento (persistencia):
#   - Si persist=True:
#       a) Buscar registro existente para (place_id, period_start, period_end).
#       b) Si no está locked, crear/actualizar con:
#           in_total, out_total, jackpot_total, billetero_total, utilidad_total,
#           generated_at=clock(), generated_by=actor, locked=lock.
#       c) Guardar en casino_balances.csv vía balances_repo.
#
# Salida:
#   - Dict con:
#       { place_id, period_start, period_end,
#         in_total, out_total, jackpot_total, billetero_total, utilidad_total,
#         generated_at, generated_by, locked }
#
# Errores:
#   - NotFoundError para place inexistente/inactivo.
#   - ValueError por periodo inválido.
#   - LockedError si el balance del periodo está bloqueado.
#
# Notas:
#   - Si se requiere reporte por participación, ese cálculo se hace en otra función
#     usando participation_rate de machines (p. ej., distribuir utilidad por proporción),
#     o en la capa de reportes; no mezclar aquí para mantener responsabilidad única.
# -------------------------------------------
# back/domain/balances/casino_balance.py
# Lógica del negocio para el cuadre global de casino.

from decimal import Decimal
from ...models.casino_balance import CasinoCuadre
from ...storage.casino_balance_repo import CasinoBalanceRepo

class CasinoBalanceService:
    """
    Servicio que calcula el cuadre general del casino.
    """

    def __init__(self):
        self.repo = CasinoBalanceRepo()

    def calcular_totales(self, maquina_id, fecha_inicio, fecha_fin):
        """
        Obtiene los contadores iniciales y finales de una máquina y
        calcula los totales por diferencia.
        """

        cont_ini = self.repo.obtener_contadores(maquina_id, fecha_inicio)
        cont_fin = self.repo.obtener_contadores(maquina_id, fecha_fin)

        total_in = Decimal(cont_fin.in_value) - Decimal(cont_ini.in_value)
        total_out = Decimal(cont_fin.out_value) - Decimal(cont_ini.out_value)
        total_jackpot = Decimal(cont_fin.jackpot) - Decimal(cont_ini.jackpot)
        total_billetero = Decimal(cont_fin.bill) - Decimal(cont_ini.bill)

        return {
            "total_in": total_in,
            "total_out": total_out,
            "total_jackpot": total_jackpot,
            "total_billetero": total_billetero
        }

    def calcular_utilidad(self, total_in, total_out, total_jackpot, total_billetero):
        """
        Fórmula estándar para la utilidad.
        """
        return total_in - total_out - total_jackpot - total_billetero

    def generar_cuadre(self, casino_id, fecha_inicio, fecha_fin):
        """
        Genera el cuadre total del casino:
        1. obtiene máquinas
        2. acumula totales
        3. calcula utilidad
        4. crea el modelo final
        5. guarda el cuadre
        """

        maquinas = self.repo.obtener_maquinas_por_casino(casino_id)

        total_in = Decimal(0)
        total_out = Decimal(0)
        total_jackpot = Decimal(0)
        total_billetero = Decimal(0)

        for maquina in maquinas:
            totales = self.calcular_totales(maquina.id, fecha_inicio, fecha_fin)

            total_in += totales["total_in"]
            total_out += totales["total_out"]
            total_jackpot += totales["total_jackpot"]
            total_billetero += totales["total_billetero"]

        utilidad = self.calcular_utilidad(total_in, total_out, total_jackpot, total_billetero)

        cuadre = CasinoCuadre(
            id=None,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_in=total_in,
            total_out=total_out,
            total_jackpot=total_jackpot,
            total_billetero=total_billetero,
            utilidad=utilidad,
            casino_id=casino_id
        )

        self.repo.guardar_cuadre(cuadre)

        return cuadre
