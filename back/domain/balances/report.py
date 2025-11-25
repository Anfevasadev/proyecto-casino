# -------------------------------------------
# back/domain/balances/report.py
# Propósito:
#   - Generar reportes consolidados detallados de casinos con desglose
#     por máquina y categorías de contadores.
# -------------------------------------------

from typing import Dict, Any, List, Callable
from datetime import datetime
from collections import defaultdict


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
        - Desglose por máquina
        - Totales por categoría
        - Utilidad final calculada
        
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
    
    # 4. Obtener todos los contadores del periodo
    counters = counters_repo.list_by_casino_date(
        casino_id=place_id,
        fecha_inicio=period_start,
        fecha_fin=period_end + " 23:59:59"
    )
    
    # 5. Crear un mapa de máquinas para acceso rápido
    machines_map = {int(m['id']): m for m in machines}
    
    # 6. Agrupar contadores por máquina y calcular totales
    machine_data = defaultdict(lambda: {
        'counter_count': 0,
        'in_total': 0.0,
        'out_total': 0.0,
        'jackpot_total': 0.0,
        'billetero_total': 0.0
    })
    
    total_counters = 0
    
    for counter in counters:
        try:
            machine_id = int(counter.get('machine_id', 0))
            
            # Solo procesar contadores de máquinas activas
            if machine_id not in machines_map:
                continue
            
            machine_data[machine_id]['counter_count'] += 1
            total_counters += 1
            
            # Sumar valores
            try:
                machine_data[machine_id]['in_total'] += float(counter.get('in_amount', 0) or 0)
            except (ValueError, TypeError):
                pass
            
            try:
                machine_data[machine_id]['out_total'] += float(counter.get('out_amount', 0) or 0)
            except (ValueError, TypeError):
                pass
            
            try:
                machine_data[machine_id]['jackpot_total'] += float(counter.get('jackpot_amount', 0) or 0)
            except (ValueError, TypeError):
                pass
            
            try:
                machine_data[machine_id]['billetero_total'] += float(counter.get('billetero_amount', 0) or 0)
            except (ValueError, TypeError):
                pass
                
        except (ValueError, TypeError):
            continue
    
    # 7. Crear resumen por máquina
    machines_summary = []
    category_totals = {
        'in_total': 0.0,
        'out_total': 0.0,
        'jackpot_total': 0.0,
        'billetero_total': 0.0
    }
    
    for machine_id, data in machine_data.items():
        machine_info = machines_map.get(machine_id, {})
        
        # Calcular utilidad de la máquina
        utilidad = data['in_total'] - (data['out_total'] + data['jackpot_total'])
        
        machine_summary = {
            'machine_id': machine_id,
            'machine_marca': machine_info.get('marca'),
            'machine_modelo': machine_info.get('modelo'),
            'machine_serial': machine_info.get('serial'),
            'machine_asset': machine_info.get('asset'),
            'counter_count': data['counter_count'],
            'in_total': round(data['in_total'], 2),
            'out_total': round(data['out_total'], 2),
            'jackpot_total': round(data['jackpot_total'], 2),
            'billetero_total': round(data['billetero_total'], 2),
            'utilidad': round(utilidad, 2)
        }
        
        machines_summary.append(machine_summary)
        
        # Acumular en totales por categoría
        category_totals['in_total'] += data['in_total']
        category_totals['out_total'] += data['out_total']
        category_totals['jackpot_total'] += data['jackpot_total']
        category_totals['billetero_total'] += data['billetero_total']
    
    # 8. Calcular utilidad final global
    utilidad_final = category_totals['in_total'] - (
        category_totals['out_total'] + category_totals['jackpot_total']
    )
    
    # 9. Ordenar máquinas por ID para consistencia
    machines_summary.sort(key=lambda x: x['machine_id'])
    
    # 10. Construir el reporte completo
    report = {
        'casino_id': place_id,
        'casino_nombre': place.get('nombre'),
        'period_start': period_start,
        'period_end': period_end,
        'machines_summary': machines_summary,
        'category_totals': {
            'in_total': round(category_totals['in_total'], 2),
            'out_total': round(category_totals['out_total'], 2),
            'jackpot_total': round(category_totals['jackpot_total'], 2),
            'billetero_total': round(category_totals['billetero_total'], 2),
            'utilidad_final': round(utilidad_final, 2)
        },
        'total_machines': len(machines_summary),
        'total_counters': total_counters,
        'generated_at': clock().strftime("%Y-%m-%d %H:%M:%S"),
        'generated_by': actor
    }
    
    return report
