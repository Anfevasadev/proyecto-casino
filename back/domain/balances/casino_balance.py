# -------------------------------------------
# back/domain/balances/casino_balance.py
# Propósito:
#   - Calcular el cuadre consolidado de un casino (place) sumando los valores
#     de todas las máquinas activas en un periodo de fechas específico.
#   - Usa el mismo cálculo del módulo por máquina para cada máquina del casino.
# -------------------------------------------

from typing import Dict, Any, Callable, List
from datetime import datetime
from back.domain.balances.machine_balance import calcular_cuadre_maquina


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
    
    IMPORTANTE: Aplica el mismo cálculo del módulo por máquina a cada máquina:
    - Para cada máquina: TOTAL = (CONTADOR_FINAL - CONTADOR_INICIAL) × DENOMINACION
    - Luego suma los resultados de todas las máquinas
    
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
        Dict con los totales consolidados del casino incluyendo:
        - Totales agregados (in_total, out_total, jackpot_total, billetero_total)
        - Utilidad total del casino
        - Desglose por máquina (machines_details)
        
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
            'locked': lock,
            'machines_details': [],
            'total_machines': 0
        }
        
        if persist:
            balances_repo.insertar_casino_balance(result)
        
        return result
    
    # 5. Inicializar totales consolidados
    in_total = 0.0
    out_total = 0.0
    jackpot_total = 0.0
    billetero_total = 0.0
    
    # Lista para almacenar el desglose por máquina
    machines_details: List[Dict[str, Any]] = []
    machines_processed = 0
    machines_with_errors = 0
    
    # 6. APLICAR EL MISMO CÁLCULO DEL MÓDULO POR MÁQUINA A CADA MÁQUINA
    for machine in machines:
        machine_id = int(machine['id'])
        
        try:
            # Calcular el cuadre de esta máquina individual
            # usando la misma lógica: (CONTADOR_FINAL - CONTADOR_INICIAL) × DENOMINACION
            machine_balance = calcular_cuadre_maquina(
                machine_id=machine_id,
                period_start=period_start,
                period_end=period_end,
                counters_repo=counters_repo,
                machines_repo=machines_repo,
                balances_repo=balances_repo,
                clock=clock,
                actor=actor,
                persist=False,  # No persistir balances individuales, solo el consolidado
                lock=False
            )
            
            # Sumar a los totales consolidados del casino
            in_total += machine_balance['in_total']
            out_total += machine_balance['out_total']
            jackpot_total += machine_balance['jackpot_total']
            billetero_total += machine_balance['billetero_total']
            
            # Agregar desglose de esta máquina
            machines_details.append({
                'machine_id': machine_id,
                'machine_marca': machine.get('marca'),
                'machine_modelo': machine.get('modelo'),
                'machine_serial': machine.get('serial'),
                'machine_asset': machine.get('asset'),
                'denominacion': machine_balance['denominacion'],
                'in_total': machine_balance['in_total'],
                'out_total': machine_balance['out_total'],
                'jackpot_total': machine_balance['jackpot_total'],
                'billetero_total': machine_balance['billetero_total'],
                'utilidad': machine_balance['utilidad_total']
            })
            
            machines_processed += 1
            
        except ValueError as e:
            # Máquina sin contadores en el periodo - no es error crítico
            machines_details.append({
                'machine_id': machine_id,
                'machine_marca': machine.get('marca'),
                'machine_modelo': machine.get('modelo'),
                'machine_serial': machine.get('serial'),
                'machine_asset': machine.get('asset'),
                'denominacion': 0.0,
                'in_total': 0.0,
                'out_total': 0.0,
                'jackpot_total': 0.0,
                'billetero_total': 0.0,
                'utilidad': 0.0,
                'error': str(e)
            })
            machines_with_errors += 1
            continue
            
        except Exception as e:
            # Error inesperado en esta máquina
            machines_details.append({
                'machine_id': machine_id,
                'machine_marca': machine.get('marca'),
                'machine_modelo': machine.get('modelo'),
                'machine_serial': machine.get('serial'),
                'machine_asset': machine.get('asset'),
                'denominacion': 0.0,
                'in_total': 0.0,
                'out_total': 0.0,
                'jackpot_total': 0.0,
                'billetero_total': 0.0,
                'utilidad': 0.0,
                'error': f"Error inesperado: {str(e)}"
            })
            machines_with_errors += 1
            continue
    
    # 7. Calcular utilidad total del casino
    # UTILIDAD = IN - (OUT + JACKPOT)
    utilidad_total = in_total - (out_total + jackpot_total)
    
    # 8. Preparar resultado consolidado
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
        'locked': lock,
        'machines_details': machines_details,
        'total_machines': len(machines),
        'machines_processed': machines_processed,
        'machines_with_errors': machines_with_errors
    }
    
    # 9. Persistir si se solicita (solo totales, no desglose)
    if persist:
        # Verificar si ya existe un balance para este periodo
        existing = balances_repo.get_casino_balance_by_period(
            place_id, period_start, period_end
        )
        
        # Preparar datos para persistencia (sin machines_details)
        persist_data = {
            'place_id': place_id,
            'period_start': period_start,
            'period_end': period_end,
            'in_total': result['in_total'],
            'out_total': result['out_total'],
            'jackpot_total': result['jackpot_total'],
            'billetero_total': result['billetero_total'],
            'utilidad_total': result['utilidad_total'],
            'generated_at': result['generated_at'],
            'generated_by': result['generated_by'],
            'locked': lock
        }
        
        if existing:
            # Actualizar el existente
            persist_data['id'] = existing['id']
            balances_repo.update_casino_balance(existing['id'], persist_data)
            result['id'] = existing['id']
        else:
            # Insertar nuevo
            saved = balances_repo.insertar_casino_balance(persist_data)
            result['id'] = saved['id']
    
    return result
