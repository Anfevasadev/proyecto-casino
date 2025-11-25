from datetime import date
from decimal import Decimal
from fastapi import HTTPException, status

from back.storage.counters_repo import CountersRepo
from back.storage.machines_repo import MachinesRepo
from back.models.cuadre_maquina import CuadreOut


class CuadreMaquinaService:

    def __init__(self):
        self.counters_repo = CountersRepo()
        self.machines_repo = MachinesRepo()

    def generar_cuadre(self, maquina_id: int, fecha_inicio: date, fecha_fin: date) -> CuadreOut:
        """Genera el cuadre para una máquina en el rango indicado.

        - Busca todos los contadores de la máquina entre `fecha_inicio` y `fecha_fin`.
        - Usa el primer registro como inicial y el último como final para calcular diferencias.
        """

        # 1. Obtener la máquina
        machine = self.machines_repo.get_by_id(int(maquina_id))
        if not machine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La máquina no existe")

        # 2. Preparar strings de fecha y pedir registros
        fecha_inicio_s = fecha_inicio.strftime("%Y-%m-%d")
        fecha_fin_s = fecha_fin.strftime("%Y-%m-%d")

        rows = self.counters_repo.list_counters(
            machine_id=int(maquina_id),
            date_from=fecha_inicio_s,
            date_to=fecha_fin_s,
            limit=10000,
            offset=0,
            sort_by="at",
            ascending=True,
        )

        if not rows or len(rows) < 2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay contadores suficientes registrados en ese rango de fechas")

        # primer registro (más antiguo) y último (más reciente)
        cont_ini = rows[0]
        cont_fin = rows[-1]

        # 3. Calcular diferencias usando Decimal para precisión
        try:
            total_in = Decimal(str(cont_fin.get("in_amount", 0))) - Decimal(str(cont_ini.get("in_amount", 0)))
            total_out = Decimal(str(cont_fin.get("out_amount", 0))) - Decimal(str(cont_ini.get("out_amount", 0)))
            total_jp = Decimal(str(cont_fin.get("jackpot_amount", 0))) - Decimal(str(cont_ini.get("jackpot_amount", 0)))
            total_bill = Decimal(str(cont_fin.get("billetero_amount", 0))) - Decimal(str(cont_ini.get("billetero_amount", 0)))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error calculando totales: {exc}")

        utilidad = total_in - total_out - total_jp

        # 4. Devolver modelo de salida
        return CuadreOut(
            maquina_id=int(maquina_id),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_in=total_in,
            total_out=total_out,
            total_jackpot=total_jp,
            total_billetero=total_bill,
            utilidad=utilidad,
        )
