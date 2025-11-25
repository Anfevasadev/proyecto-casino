from fastapi import APIRouter, HTTPException
from back.models.cuadre_maquina import CuadreIn, CuadreOut
from back.domain.cuadre_maquinas.service import CuadreMaquinaService

router = APIRouter(prefix="/cuadre-maquina", tags=["Cuadre Máquina"])

service = CuadreMaquinaService()

@router.post("/", response_model=CuadreOut)
def generar_cuadre(data: CuadreIn):
    cuadre = service.generar_cuadre(
        maquina_id=data.maquina_id,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin
    )
    return cuadre
