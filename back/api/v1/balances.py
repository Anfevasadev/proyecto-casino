# -------------------------------------------
# back/api/v1/balances.py
# Propósito:
#   - Exponer endpoints para calcular y consultar "cuadres" (balances) a partir
#     de los contadores:
#       * Cuadre por máquina (machine_balances.csv)
#       * Cuadre por lugar/casino (casino_balances.csv)
# -------------------------------------------

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, status
from fastapi.responses import Response

from back.models.balances import (
    CasinoBalanceIn,
    CasinoBalanceOut,
    MachineBalanceIn,
    MachineBalanceOut,
    CasinoDetailedReport
)

from back.domain.balances.casino_balance import (
    calcular_cuadre_casino,
    NotFoundError,
    LockedError
)

from back.domain.balances.report import generar_reporte_consolidado_casino
from back.domain.balances.export import generar_pdf_reporte, generar_excel_reporte

from back.storage.balances_repo import BalancesRepo
from back.storage.counters_repo import CountersRepo
from back.storage.machines_repo import MachinesRepo
from back.storage.places_repo import PlaceStorage


# Instanciar repositorios
repo_balances = BalancesRepo()
repo_counters = CountersRepo()
repo_machines = MachinesRepo()
repo_places = PlaceStorage()

router = APIRouter()


def get_current_time():
    """Función auxiliar para obtener la hora actual"""
    return datetime.now()


# ============ ENDPOINTS PARA CASINO BALANCES ============

@router.post(
    "/casinos/generate",
    response_model=CasinoBalanceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generar cuadre de casino",
    description="Calcula el cuadre consolidado de un casino para un periodo específico"
)
def generar_cuadre_casino(data: CasinoBalanceIn):
    """
    Genera un cuadre general del casino consolidando todas sus máquinas activas.
    
    - **place_id**: ID del casino
    - **period_start**: Fecha inicial (YYYY-MM-DD)
    - **period_end**: Fecha final (YYYY-MM-DD)
    - **locked**: Si True, marca el balance como bloqueado (opcional)
    
    Retorna el balance generado con todos los totales consolidados.
    """
    try:
        # Llamar a la función de dominio para calcular el cuadre
        result = calcular_cuadre_casino(
            place_id=data.place_id,
            period_start=data.period_start,
            period_end=data.period_end,
            counters_repo=repo_counters,
            machines_repo=repo_machines,
            places_repo=repo_places,
            balances_repo=repo_balances,
            clock=get_current_time,
            actor="api_user",  # TODO: obtener del usuario autenticado
            persist=True,
            lock=data.locked or False
        )
        
        return CasinoBalanceOut(**result)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except LockedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el cuadre: {str(e)}"
        )


@router.get(
    "/casinos",
    response_model=List[CasinoBalanceOut],
    status_code=status.HTTP_200_OK,
    summary="Listar cuadres de casinos",
    description="Obtiene la lista de cuadres de casinos con filtros opcionales"
)
def listar_cuadres_casinos(
    place_id: Optional[int] = Query(None, ge=1, description="Filtrar por ID de casino"),
    date_from: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    limit: Optional[int] = Query(100, ge=1, le=500, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    Lista los cuadres de casinos con filtros opcionales.
    
    - **place_id**: Filtra por casino específico
    - **date_from**: Filtra balances desde esta fecha
    - **date_to**: Filtra balances hasta esta fecha
    - **limit**: Cantidad máxima de resultados (default 100)
    - **offset**: Posición inicial para paginación (default 0)
    """
    try:
        balances = repo_balances.listar_casino_balances(
            place_id=place_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        return [CasinoBalanceOut(**b) for b in balances]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar cuadres: {str(e)}"
        )


@router.get(
    "/casinos/{balance_id}",
    response_model=CasinoBalanceOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener cuadre de casino por ID",
    description="Obtiene los detalles de un cuadre específico de casino"
)
def obtener_cuadre_casino(
    balance_id: int = Path(..., ge=1, description="ID del balance")
):
    """
    Obtiene un cuadre de casino específico por su ID.
    
    - **balance_id**: ID del balance a consultar
    """
    balance = repo_balances.obtener_casino_balance_por_id(balance_id)
    
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Balance con id {balance_id} no encontrado"
        )
    
    return CasinoBalanceOut(**balance)


@router.post(
    "/casinos/{balance_id}/lock",
    status_code=status.HTTP_200_OK,
    summary="Bloquear cuadre de casino",
    description="Marca un cuadre como bloqueado para evitar modificaciones"
)
def bloquear_cuadre_casino(
    balance_id: int = Path(..., ge=1, description="ID del balance a bloquear")
):
    """
    Bloquea un cuadre de casino para evitar recálculos o modificaciones.
    
    - **balance_id**: ID del balance a bloquear
    """
    # Verificar que existe
    balance = repo_balances.obtener_casino_balance_por_id(balance_id)
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Balance con id {balance_id} no encontrado"
        )
    
    # Verificar si ya está bloqueado
    if balance.get('locked'):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El balance {balance_id} ya está bloqueado"
        )
    
    # Bloquear
    success = repo_balances.lock_casino_balance(
        balance_id=balance_id,
        actor="api_user",  # TODO: obtener del usuario autenticado
        clock=get_current_time
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo bloquear el balance"
        )
    
    return {"locked": True, "id": balance_id, "message": "Balance bloqueado exitosamente"}


@router.get(
    "/casinos/{place_id}/report",
    response_model=CasinoDetailedReport,
    status_code=status.HTTP_200_OK,
    summary="Generar reporte consolidado detallado",
    description="Genera un reporte completo con desglose por máquina y totales por categoría"
)
def generar_reporte_detallado_casino(
    place_id: int = Path(..., ge=1, description="ID del casino"),
    period_start: str = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    period_end: str = Query(..., description="Fecha final (YYYY-MM-DD)")
):
    """
    Genera un reporte consolidado detallado del casino.
    
    El reporte incluye:
    - **Desglose por máquina**: Contadores y totales de cada máquina
    - **Totales por categoría**: IN, OUT, JACKPOT, BILLETERO consolidados
    - **Utilidad final**: Rendimiento neto del casino (IN - (OUT + JACKPOT))
    - **Estadísticas**: Cantidad de máquinas y contadores procesados
    
    Este reporte puede ser usado para:
    - Visualización en pantalla
    - Exportación a PDF o Excel
    - Análisis y auditorías
    """
    try:
        report = generar_reporte_consolidado_casino(
            place_id=place_id,
            period_start=period_start,
            period_end=period_end,
            counters_repo=repo_counters,
            machines_repo=repo_machines,
            places_repo=repo_places,
            clock=get_current_time,
            actor="api_user"  # TODO: obtener del usuario autenticado
        )
        
        return CasinoDetailedReport(**report)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el reporte: {str(e)}"
        )


# ============ ENDPOINTS PARA MACHINE BALANCES (para completitud) ============

@router.get(
    "/machines",
    response_model=List[MachineBalanceOut],
    status_code=status.HTTP_200_OK,
    summary="Listar cuadres de máquinas",
    description="Obtiene la lista de cuadres de máquinas con filtros opcionales"
)
def listar_cuadres_maquinas(
    machine_id: Optional[int] = Query(None, ge=1, description="Filtrar por ID de máquina"),
    date_from: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    limit: Optional[int] = Query(100, ge=1, le=500, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    Lista los cuadres de máquinas con filtros opcionales.
    """
    try:
        balances = repo_balances.listar_machine_balances(
            machine_id=machine_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        return [MachineBalanceOut(**b) for b in balances]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar cuadres: {str(e)}"
        )


@router.get(
    "/machines/{balance_id}",
    response_model=MachineBalanceOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener cuadre de máquina por ID",
    description="Obtiene los detalles de un cuadre específico de máquina"
)
def obtener_cuadre_maquina(
    balance_id: int = Path(..., ge=1, description="ID del balance")
):
    """
    Obtiene un cuadre de máquina específico por su ID.
    """
    balance = repo_balances.obtener_machine_balance_por_id(balance_id)
    
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Balance con id {balance_id} no encontrado"
        )
    
    return MachineBalanceOut(**balance)


# ============ ENDPOINTS PARA EXPORTACIÓN DE REPORTES ============

@router.get(
    "/casinos/{place_id}/report/pdf",
    status_code=status.HTTP_200_OK,
    summary="Exportar reporte a PDF",
    description="Genera y descarga el reporte consolidado en formato PDF"
)
def exportar_reporte_pdf(
    place_id: int = Path(..., ge=1, description="ID del casino"),
    period_start: str = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    period_end: str = Query(..., description="Fecha final (YYYY-MM-DD)")
):
    """
    Genera un archivo PDF del reporte consolidado del casino.
    
    El PDF incluye:
    - Información general del casino y periodo
    - Tabla con desglose por máquina
    - Totales por categoría (IN, OUT, JACKPOT, BILLETERO)
    - Utilidad final calculada
    - Estadísticas del reporte
    
    Formato profesional listo para impresión y auditorías.
    """
    try:
        # Generar el reporte
        report = generar_reporte_consolidado_casino(
            place_id=place_id,
            period_start=period_start,
            period_end=period_end,
            counters_repo=repo_counters,
            machines_repo=repo_machines,
            places_repo=repo_places,
            clock=get_current_time,
            actor="api_user"
        )
        
        # Generar PDF
        pdf_content = generar_pdf_reporte(report)
        
        # Nombre del archivo
        filename = f"reporte_casino_{place_id}_{period_start}_{period_end}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {str(e)}"
        )


@router.get(
    "/casinos/{place_id}/report/excel",
    status_code=status.HTTP_200_OK,
    summary="Exportar reporte a Excel",
    description="Genera y descarga el reporte consolidado en formato Excel"
)
def exportar_reporte_excel(
    place_id: int = Path(..., ge=1, description="ID del casino"),
    period_start: str = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    period_end: str = Query(..., description="Fecha final (YYYY-MM-DD)")
):
    """
    Genera un archivo Excel del reporte consolidado del casino.
    
    El Excel incluye:
    - Información general del casino y periodo
    - Hoja con desglose detallado por máquina
    - Totales por categoría con formato de moneda
    - Utilidad final resaltada
    - Estadísticas del reporte
    
    Formato ideal para análisis adicional en Excel.
    """
    try:
        # Generar el reporte
        report = generar_reporte_consolidado_casino(
            place_id=place_id,
            period_start=period_start,
            period_end=period_end,
            counters_repo=repo_counters,
            machines_repo=repo_machines,
            places_repo=repo_places,
            clock=get_current_time,
            actor="api_user"
        )
        
        # Generar Excel
        excel_content = generar_excel_reporte(report)
        
        # Nombre del archivo
        filename = f"reporte_casino_{place_id}_{period_start}_{period_end}.xlsx"
        
        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el Excel: {str(e)}"
        )


