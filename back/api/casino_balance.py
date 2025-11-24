# back/api/casino_balance.py
# Endpoints para generar el cuadre general del casino.

from fastapi import APIRouter
from ..models.casino_balance import CasinoCuadreInput, CasinoCuadreOutput
from ..domain.balances.casino_balance import CasinoBalanceService

router = APIRouter(prefix="/casino/cuadre", tags=["Cuadre Casino"])

service = CasinoBalanceService()


@router.post("/", response_model=CasinoCuadreOutput)
def generar_cuadre_casino(data: CasinoCuadreInput):
    """
    Endpoint que recibe casino_id, fecha_inicio y fecha_fin,
    llama al servicio y devuelve el cuadre consolidado.
    """

    cuadre = service.generar_cuadre(
        casino_id=data.casino_id,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin
    )

    return {
        "total_in": cuadre.total_in,
        "total_out": cuadre.total_out,
        "total_jackpot": cuadre.total_jackpot,
        "total_billetero": cuadre.total_billetero,
        "utilidad": cuadre.utilidad,
        "casino_id": cuadre.casino_id,
        "fecha_inicio": cuadre.fecha_inicio,
        "fecha_fin": cuadre.fecha_fin
    }
