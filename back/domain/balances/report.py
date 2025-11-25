# -------------------------------------------
# back/domain/balances/report.py
# Propósito:
#   - Generar reportes consolidados detallados de casinos con desglose
#     por máquina y categorías de contadores.
#   - Usa el mismo cálculo del módulo por máquina (con denominación).
# -------------------------------------------

from typing import Dict, Any, List, Callable
from datetime import datetime
from back.domain.balances.machine_balance import calcular_cuadre_maquina


class NotFoundError(Exception):
    """Excepción cuando no se encuentra un recurso"""
    pass


def generar_reporte_consolidado_casino(
    place_id: int,
    period_start: str,
    period_end: str,
    counters_repo,
    machines_repo,
    places_repo,
    clock: Callable[[], datetime],
    actor: str
) -> Dict[str, Any]:
    """
    Genera un reporte consolidado detallado del casino con desglose por máquina.
    
    IMPORTANTE: Aplica el mismo cálculo del módulo por máquina a cada máquina:
    - Para cada máquina: TOTAL = (CONTADOR_FINAL - CONTADOR_INICIAL) × DENOMINACION
    - Genera un listado detallado de todas las máquinas y sus resultados
    - Consolida los totales por categoría (IN, OUT, JACKPOT, BILLETERO)
    
    Args:
        place_id: ID del casino
        period_start: Fecha inicial del periodo (YYYY-MM-DD)
        period_end: Fecha final del periodo (YYYY-MM-DD)
        counters_repo: Repositorio de contadores
        machines_repo: Repositorio de máquinas
        places_repo: Repositorio de casinos
        clock: Función que retorna datetime actual
        actor: Usuario que genera el reporte
        
    Returns:
        Dict con el reporte detallado incluyendo:
        - Desglose por máquina (con contadores inicial/final)
        - Totales por categoría
        - Utilidad final calculada
        - Información del casino
        
    Raises:
        NotFoundError: Si el casino no existe o está inactivo
        ValueError: Si el periodo es inválido
    """
    
    # 1. Validar que el casino existe y está activo
    place = places_repo.get_by_id(place_id)
    if not place:
        raise NotFoundError(f"Casino con id {place_id} no encontrado")
    
    # Verificar si está activo
    is_active = place.get('is_active') or place.get('estado')
    if isinstance(is_active, str):
        is_active = is_active.lower() == 'true'
    
    if not is_active:
        raise NotFoundError(f"Casino con id {place_id} está inactivo")
    
    # 2. Validar periodo
    if period_start > period_end:
        raise ValueError(
            f"La fecha inicial ({period_start}) debe ser menor o igual a la fecha final ({period_end})"
        )
    
    # 3. Obtener todas las máquinas activas del casino
    machines = machines_repo.listar(only_active=True, casino_id=place_id)
    
    if not machines:
        # Si no hay máquinas, retornar reporte vacío
        return {
            'casino_id': place_id,
            'casino_nombre': place.get('nombre'),
            'period_start': period_start,
            'period_end': period_end,
            'machines_summary': [],
            'category_totals': {
                'in_total': 0.0,
                'out_total': 0.0,
                'jackpot_total': 0.0,
                'billetero_total': 0.0,
                'utilidad_final': 0.0
            },
            'total_machines': 0,
            'machines_processed': 0,
            'machines_with_data': 0,
            'machines_without_data': 0,
            'generated_at': clock().strftime("%Y-%m-%d %H:%M:%S"),
            'generated_by': actor
        }
    
    # 4. Inicializar totales por categoría
    category_totals = {
        'in_total': 0.0,
        'out_total': 0.0,
        'jackpot_total': 0.0,
        'billetero_total': 0.0
    }
    
    # Lista para el desglose por máquina
    machines_summary: List[Dict[str, Any]] = []
    machines_processed = 0
    machines_with_data = 0
    machines_without_data = 0
    
    # 5. APLICAR EL MISMO CÁLCULO DEL MÓDULO POR MÁQUINA A CADA MÁQUINA
    for machine in machines:
        machine_id = int(machine['id'])
        machines_processed += 1
        
        try:
            # Calcular el cuadre de esta máquina individual
            # usando la misma lógica: (CONTADOR_FINAL - CONTADOR_INICIAL) × DENOMINACION
            machine_balance = calcular_cuadre_maquina(
                machine_id=machine_id,
                period_start=period_start,
                period_end=period_end,
                counters_repo=counters_repo,
                machines_repo=machines_repo,
                balances_repo=None,  # No necesitamos balances_repo para el reporte
                clock=clock,
                actor=actor,
                persist=False,  # No persistir en el reporte
                lock=False
            )
            
            # Sumar a los totales por categoría
            category_totals['in_total'] += machine_balance['in_total']
            category_totals['out_total'] += machine_balance['out_total']
            category_totals['jackpot_total'] += machine_balance['jackpot_total']
            category_totals['billetero_total'] += machine_balance['billetero_total']
            
            # Agregar al resumen de máquinas con información detallada
            machines_summary.append({
                'machine_id': machine_id,
                'machine_marca': machine.get('marca'),
                'machine_modelo': machine.get('modelo'),
                'machine_serial': machine.get('serial'),
                'machine_asset': machine.get('asset'),
                'denominacion': machine_balance['denominacion'],
                
                # Contadores iniciales
                'contador_inicial': machine_balance.get('contador_inicial', {}),
                
                # Contadores finales
                'contador_final': machine_balance.get('contador_final', {}),
                
                # Totales calculados
                'in_total': machine_balance['in_total'],
                'out_total': machine_balance['out_total'],
                'jackpot_total': machine_balance['jackpot_total'],
                'billetero_total': machine_balance['billetero_total'],
                'utilidad': machine_balance['utilidad_total'],
                
                # Estado
                'has_data': True
            })
            
            machines_with_data += 1
            
        except ValueError as e:
            # Máquina sin contadores en el periodo
            machines_summary.append({
                'machine_id': machine_id,
                'machine_marca': machine.get('marca'),
                'machine_modelo': machine.get('modelo'),
                'machine_serial': machine.get('serial'),
                'machine_asset': machine.get('asset'),
                'denominacion': 0.0,
                'contador_inicial': None,
                'contador_final': None,
                'in_total': 0.0,
                'out_total': 0.0,
                'jackpot_total': 0.0,
                'billetero_total': 0.0,
                'utilidad': 0.0,
                'has_data': False,
                'error': str(e)
            })
            
            machines_without_data += 1
            continue
            
        except Exception as e:
            # Error inesperado
            machines_summary.append({
                'machine_id': machine_id,
                'machine_marca': machine.get('marca'),
                'machine_modelo': machine.get('modelo'),
                'machine_serial': machine.get('serial'),
                'machine_asset': machine.get('asset'),
                'denominacion': 0.0,
                'contador_inicial': None,
                'contador_final': None,
                'in_total': 0.0,
                'out_total': 0.0,
                'jackpot_total': 0.0,
                'billetero_total': 0.0,
                'utilidad': 0.0,
                'has_data': False,
                'error': f"Error inesperado: {str(e)}"
            })
            
            machines_without_data += 1
            continue
    
    # 6. Calcular utilidad final global
    # UTILIDAD = IN - (OUT + JACKPOT)
    utilidad_final = category_totals['in_total'] - (
        category_totals['out_total'] + category_totals['jackpot_total']
    )
    
    # 7. Ordenar máquinas por ID para consistencia
    machines_summary.sort(key=lambda x: x['machine_id'])
    
    # 8. Construir el reporte completo
    report = {
        'casino_id': place_id,
        'casino_nombre': place.get('nombre'),
        'period_start': period_start,
        'period_end': period_end,
        
        # Desglose detallado por máquina
        'machines_summary': machines_summary,
        
        # Totales consolidados por categoría
        'category_totals': {
            'in_total': round(category_totals['in_total'], 2),
            'out_total': round(category_totals['out_total'], 2),
            'jackpot_total': round(category_totals['jackpot_total'], 2),
            'billetero_total': round(category_totals['billetero_total'], 2),
            'utilidad_final': round(utilidad_final, 2)
        },
        
        # Estadísticas
        'total_machines': len(machines),
        'machines_processed': machines_processed,
        'machines_with_data': machines_with_data,
        'machines_without_data': machines_without_data,
        
        # Metadatos
        'generated_at': clock().strftime("%Y-%m-%d %H:%M:%S"),
        'generated_by': actor
    }
    
    return report
