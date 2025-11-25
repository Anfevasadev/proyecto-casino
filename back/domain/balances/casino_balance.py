# -------------------------------------------
# back/domain/balances/casino_balance.py
# Propósito:
#   - Calcular el cuadre consolidado de un casino (place) sumando los valores
#     de todas las máquinas activas en un periodo de fechas específico.
# -------------------------------------------

from typing import Dict, Any, Callable
from datetime import datetime


class NotFoundError(Exception):
    """Excepción cuando no se encuentra un recurso"""
    pass


class LockedError(Exception):
    """Excepción cuando se intenta modificar un balance bloqueado"""
    pass


def calcular_cuadre_casino(
    place_id: int,
    period_start: str,
    period_end: str,
    counters_repo,
    machines_repo,
    places_repo,
    balances_repo,
    clock: Callable[[], datetime],
    actor: str,
    persist: bool = True,
    lock: bool = False
) -> Dict[str, Any]:
    """
    Calcula el cuadre general del casino consolidando todas sus máquinas.
    
    Args:
        place_id: ID del casino
        period_start: Fecha inicial del periodo (YYYY-MM-DD)
        period_end: Fecha final del periodo (YYYY-MM-DD)
        counters_repo: Repositorio de contadores
        machines_repo: Repositorio de máquinas
        places_repo: Repositorio de casinos
        balances_repo: Repositorio de balances
        clock: Función que retorna datetime actual
        actor: Usuario que genera el cuadre
        persist: Si True, guarda en CSV
        lock: Si True, marca como bloqueado
        
    Returns:
        Dict con los totales consolidados del casino
        
    Raises:
        NotFoundError: Si el casino no existe o está inactivo
        ValueError: Si el periodo es inválido
        LockedError: Si ya existe un balance bloqueado para ese periodo
    """
    
    # 1. Validar que el casino existe y está activo
    place = places_repo.get_by_id(place_id)
    if not place:
        raise NotFoundError(f"Casino con id {place_id} no encontrado")
    
    # Verificar si está activo (el campo puede ser 'is_active' o 'estado')
    is_active = place.get('is_active') or place.get('estado')
    if isinstance(is_active, str):
        is_active = is_active.lower() == 'true'
    
    if not is_active:
        raise NotFoundError(f"Casino con id {place_id} está inactivo")
    
    # 2. Validar periodo
    if period_start > period_end:
        raise ValueError(f"La fecha inicial ({period_start}) debe ser menor o igual a la fecha final ({period_end})")
    
    # 3. Verificar si existe un balance bloqueado para este periodo
    if persist:
        existing_balance = balances_repo.get_casino_balance_by_period(
            place_id, period_start, period_end
        )
        if existing_balance and existing_balance.get('locked'):
            if isinstance(existing_balance['locked'], str):
                if existing_balance['locked'].lower() == 'true':
                    raise LockedError(
                        f"Ya existe un balance bloqueado para el casino {place_id} "
                        f"en el periodo {period_start} - {period_end}"
                    )
            elif existing_balance['locked']:
                raise LockedError(
                    f"Ya existe un balance bloqueado para el casino {place_id} "
                    f"en el periodo {period_start} - {period_end}"
                )
    
    # 4. Obtener todas las máquinas activas del casino
    machines = machines_repo.listar(only_active=True, casino_id=place_id)
    
    if not machines:
        # Si no hay máquinas, retornar totales en cero
        result = {
            'place_id': place_id,
            'period_start': period_start,
            'period_end': period_end,
            'in_total': 0.0,
            'out_total': 0.0,
            'jackpot_total': 0.0,
            'billetero_total': 0.0,
            'utilidad_total': 0.0,
            'generated_at': clock().strftime("%Y-%m-%d %H:%M:%S"),
            'generated_by': actor,
            'locked': lock
        }
        
        if persist:
            balances_repo.insertar_casino_balance(result)
        
        return result
    
    # 5. Obtener machine_ids
    machine_ids = [int(m['id']) for m in machines]
    
    # 6. Inicializar totales
    in_total = 0.0
    out_total = 0.0
    jackpot_total = 0.0
    billetero_total = 0.0
    
    # 7. Para cada máquina, obtener sus contadores en el periodo
    for machine_id in machine_ids:
        # Obtener contadores de esta máquina en el rango de fechas
        # Usamos list_by_casino_date que filtra por casino y fechas
        counters = counters_repo.list_by_casino_date(
            casino_id=place_id,
            fecha_inicio=period_start,
            fecha_fin=period_end + " 23:59:59"  # Incluir todo el día final
        )
        
        # Filtrar solo los de esta máquina específica
        machine_counters = [
            c for c in counters 
            if str(c.get('machine_id', '')).strip() == str(machine_id)
        ]
        
        # Sumar los valores de los contadores
        for counter in machine_counters:
            try:
                in_total += float(counter.get('in_amount', 0) or 0)
            except (ValueError, TypeError):
                pass
            
            try:
                out_total += float(counter.get('out_amount', 0) or 0)
            except (ValueError, TypeError):
                pass
            
            try:
                jackpot_total += float(counter.get('jackpot_amount', 0) or 0)
            except (ValueError, TypeError):
                pass
            
            try:
                billetero_total += float(counter.get('billetero_amount', 0) or 0)
            except (ValueError, TypeError):
                pass
    
    # 8. Calcular utilidad total
    utilidad_total = in_total - (out_total + jackpot_total)
    
    # 9. Preparar resultado
    result = {
        'place_id': place_id,
        'period_start': period_start,
        'period_end': period_end,
        'in_total': round(in_total, 2),
        'out_total': round(out_total, 2),
        'jackpot_total': round(jackpot_total, 2),
        'billetero_total': round(billetero_total, 2),
        'utilidad_total': round(utilidad_total, 2),
        'generated_at': clock().strftime("%Y-%m-%d %H:%M:%S"),
        'generated_by': actor,
        'locked': lock
    }
    
    # 10. Persistir si se solicita
    if persist:
        # Verificar si ya existe un balance para este periodo
        existing = balances_repo.get_casino_balance_by_period(
            place_id, period_start, period_end
        )
        
        if existing:
            # Actualizar el existente
            result['id'] = existing['id']
            balances_repo.update_casino_balance(existing['id'], result)
        else:
            # Insertar nuevo
            balances_repo.insertar_casino_balance(result)
    
    return result
