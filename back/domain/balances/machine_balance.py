# -------------------------------------------
# back/domain/balances/machine_balance.py
# Propósito:
#   - Calcular el cuadre de una máquina individual sumando los valores de sus
#     contadores en un periodo de fechas específico.
#   - Implementa la lógica: TOTAL = (CONTADOR_FINAL - CONTADOR_INICIAL) × DENOMINACION
# -------------------------------------------

from typing import Dict, Any, Callable
from datetime import datetime


class NotFoundError(Exception):
    """Excepción cuando no se encuentra un recurso"""
    pass


class LockedError(Exception):
    """Excepción cuando se intenta modificar un balance bloqueado"""
    pass


def calcular_cuadre_maquina(
    machine_id: int,
    period_start: str,
    period_end: str,
    counters_repo,
    machines_repo,
    balances_repo,
    clock: Callable[[], datetime],
    actor: str,
    persist: bool = True,
    lock: bool = False
) -> Dict[str, Any]:
    """
    Calcula el cuadre de una máquina individual basándose en sus contadores.
    
    Implementa la fórmula del módulo de cuadre:
    - TOTAL IN = (CONTADOR IN FINAL - CONTADOR IN INICIAL) × DENOMINACION
    - TOTAL OUT = (CONTADOR OUT FINAL - CONTADOR OUT INICIAL) × DENOMINACION
    - TOTAL JACKPOT = (CONTADOR JACKPOT FINAL - CONTADOR JACKPOT INICIAL) × DENOMINACION
    - TOTAL BILLETERO = (CONTADOR BILLETERO FINAL - CONTADOR BILLETERO INICIAL) × DENOMINACION
    - UTILIDAD FINAL = TOTAL IN - (TOTAL OUT + TOTAL JACKPOT)
    
    Args:
        machine_id: ID de la máquina
        period_start: Fecha inicial del periodo (YYYY-MM-DD)
        period_end: Fecha final del periodo (YYYY-MM-DD)
        counters_repo: Repositorio de contadores
        machines_repo: Repositorio de máquinas
        balances_repo: Repositorio de balances
        clock: Función que retorna datetime actual
        actor: Usuario que genera el cuadre
        persist: Si True, guarda en CSV
        lock: Si True, marca como bloqueado
        
    Returns:
        Dict con los totales calculados de la máquina
        
    Raises:
        NotFoundError: Si la máquina no existe o está inactiva
        ValueError: Si el periodo es inválido o no hay contadores
        LockedError: Si ya existe un balance bloqueado para ese periodo
    """
    
    # 1. Validar que la máquina existe y está activa
    machine = machines_repo.get_by_id(machine_id)
    if not machine:
        raise NotFoundError(f"Máquina con id {machine_id} no encontrada")
    
    # Verificar si está activa
    is_active = machine.get('estado')
    if isinstance(is_active, str):
        is_active = is_active.lower() == 'true'
    
    if not is_active:
        raise NotFoundError(f"Máquina con id {machine_id} está inactiva")
    
    # Obtener denominación de la máquina
    try:
        denominacion = float(machine.get('denominacion', 1))
        if denominacion <= 0:
            denominacion = 1.0
    except (ValueError, TypeError):
        denominacion = 1.0
    
    # 2. Validar periodo
    if period_start > period_end:
        raise ValueError(
            f"La fecha inicial ({period_start}) debe ser menor o igual a la fecha final ({period_end})"
        )
    
    # 3. Verificar si existe un balance bloqueado para este periodo
    if persist:
        existing_balance = balances_repo.get_machine_balance_by_period(
            machine_id, period_start, period_end
        )
        if existing_balance and existing_balance.get('locked'):
            if isinstance(existing_balance['locked'], str):
                if existing_balance['locked'].lower() == 'true':
                    raise LockedError(
                        f"Ya existe un balance bloqueado para la máquina {machine_id} "
                        f"en el periodo {period_start} - {period_end}"
                    )
            elif existing_balance['locked']:
                raise LockedError(
                    f"Ya existe un balance bloqueado para la máquina {machine_id} "
                    f"en el periodo {period_start} - {period_end}"
                )
    
    # 4. Obtener contadores del periodo (ordenados por fecha)
    counters = counters_repo.list_counters(
        machine_id=machine_id,
        date_from=period_start,
        date_to=period_end + " 23:59:59",  # Incluir todo el día final
        sort_by="at",
        ascending=True,
        limit=None  # Obtener todos los contadores
    )
    
    if not counters or len(counters) == 0:
        raise ValueError(
            f"No se encontraron contadores para la máquina {machine_id} "
            f"en el periodo {period_start} - {period_end}"
        )
    
    # 5. Obtener contador inicial (primer registro) y contador final (último registro)
    contador_inicial = counters[0]
    contador_final = counters[-1]
    
    # 6. Calcular las diferencias
    # Nota: Los contadores son acumulativos, por lo que la diferencia nos da el total del periodo
    def safe_float(value):
        """Convierte a float de forma segura"""
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    # Diferencias de contadores
    diff_in = safe_float(contador_final.get('in_amount', 0)) - safe_float(contador_inicial.get('in_amount', 0))
    diff_out = safe_float(contador_final.get('out_amount', 0)) - safe_float(contador_inicial.get('out_amount', 0))
    diff_jackpot = safe_float(contador_final.get('jackpot_amount', 0)) - safe_float(contador_inicial.get('jackpot_amount', 0))
    diff_billetero = safe_float(contador_final.get('billetero_amount', 0)) - safe_float(contador_inicial.get('billetero_amount', 0))
    
    # 7. Aplicar fórmula: TOTAL = DIFERENCIA × DENOMINACION
    in_total = diff_in * denominacion
    out_total = diff_out * denominacion
    jackpot_total = diff_jackpot * denominacion
    billetero_total = diff_billetero * denominacion
    
    # 8. Calcular utilidad: UTILIDAD = IN - (OUT + JACKPOT)
    utilidad_total = in_total - (out_total + jackpot_total)
    
    # 9. Preparar resultado
    result = {
        'machine_id': machine_id,
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
        # Información adicional para visualización
        'contador_inicial': {
            'at': contador_inicial.get('at'),
            'in_amount': safe_float(contador_inicial.get('in_amount', 0)),
            'out_amount': safe_float(contador_inicial.get('out_amount', 0)),
            'jackpot_amount': safe_float(contador_inicial.get('jackpot_amount', 0)),
            'billetero_amount': safe_float(contador_inicial.get('billetero_amount', 0))
        },
        'contador_final': {
            'at': contador_final.get('at'),
            'in_amount': safe_float(contador_final.get('in_amount', 0)),
            'out_amount': safe_float(contador_final.get('out_amount', 0)),
            'jackpot_amount': safe_float(contador_final.get('jackpot_amount', 0)),
            'billetero_amount': safe_float(contador_final.get('billetero_amount', 0))
        },
        'denominacion': denominacion
    }
    
    # 10. Persistir si se solicita
    if persist:
        # Verificar si ya existe un balance para este periodo
        existing = balances_repo.get_machine_balance_by_period(
            machine_id, period_start, period_end
        )
        
        # Preparar datos para persistencia (sin info extra)
        persist_data = {
            'machine_id': machine_id,
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
            balances_repo.update_machine_balance(existing['id'], persist_data)
            result['id'] = existing['id']
        else:
            # Insertar nuevo
            saved = balances_repo.insertar_machine_balance(persist_data)
            result['id'] = saved['id']
    
    return result
