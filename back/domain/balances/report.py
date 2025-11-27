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


def generar_reporte_con_filtros(
    period_start: str,
    period_end: str,
    counters_repo,
    machines_repo,
    places_repo,
    clock: Callable[[], datetime],
    actor: str,
    casino_id: int = None,
    marca: str = None,
    modelo: str = None,
    tipo_reporte: str = "detallado"
) -> Dict[str, Any]:
    """
    Genera reportes personalizados con filtros avanzados.
    
    Permite filtrar por:
    - Casino específico (casino_id)
    - Marca de máquinas
    - Modelo de máquinas
    
    Tipos de reporte:
    - "detallado": Desglose por máquina con contadores inicial/final
    - "consolidado": Solo totales por categoría
    - "resumen": Estadísticas generales
    
    Args:
        period_start: Fecha inicial (YYYY-MM-DD)
        period_end: Fecha final (YYYY-MM-DD)
        counters_repo: Repositorio de contadores
        machines_repo: Repositorio de máquinas
        places_repo: Repositorio de casinos
        clock: Función que retorna datetime actual
        actor: Usuario que genera el reporte
        casino_id: ID del casino (opcional)
        marca: Marca de máquina (opcional)
        modelo: Modelo de máquina (opcional)
        ciudad: Ciudad (opcional)
        tipo_reporte: Tipo de reporte ("detallado", "consolidado", "resumen")
        
    Returns:
        Dict con el reporte según filtros y tipo especificado
        
    Raises:
        ValueError: Si los filtros o periodo son inválidos
    """
    
    # 1. Validar periodo
    if period_start > period_end:
        raise ValueError(
            f"La fecha inicial ({period_start}) debe ser menor o igual a la fecha final ({period_end})"
        )
    
    # 2. Obtener casinos según filtros
    casinos = []
    
    if casino_id:
        # Filtro por casino específico
        place = places_repo.get_by_id(casino_id)
        if not place:
            raise NotFoundError(f"Casino con id {casino_id} no encontrado")
        
        # Verificar si está activo
        is_active = place.get('is_active') or place.get('estado')
        if isinstance(is_active, str):
            is_active = is_active.lower() == 'true'
        
        if not is_active:
            raise NotFoundError(f"Casino con id {casino_id} está inactivo")
        
        casinos = [place]
    else:
        # Sin filtro de casino - obtener todos los casinos activos
        casinos = places_repo.listar(only_active=True)
    
    # 3. Inicializar acumuladores globales
    all_machines_summary = []
    global_totals = {
        'in_total': 0.0,
        'out_total': 0.0,
        'jackpot_total': 0.0,
        'billetero_total': 0.0
    }
    
    total_machines_all_casinos = 0
    machines_processed = 0
    machines_with_data = 0
    machines_without_data = 0
    casinos_info = []
    
    # 4. Procesar cada casino
    for place in casinos:
        place_id = int(place['id'])
        
        # Obtener máquinas del casino
        machines = machines_repo.listar(only_active=True, casino_id=place_id)
        
        if not machines:
            continue
        
        # Aplicar filtros de máquina (marca, modelo)
        filtered_machines = machines
        
        if marca:
            filtered_machines = [
                m for m in filtered_machines
                if m.get('marca', '').lower().strip() == marca.lower().strip()
            ]
        
        if modelo:
            filtered_machines = [
                m for m in filtered_machines
                if m.get('modelo', '').lower().strip() == modelo.lower().strip()
            ]
        
        if not filtered_machines:
            continue
        
        total_machines_all_casinos += len(filtered_machines)
        
        # Información del casino
        casino_info = {
            'casino_id': place_id,
            'casino_nombre': place.get('nombre'),
            'ciudad': place.get('ciudad', 'N/A'),
            'total_machines': len(filtered_machines)
        }
        
        # Procesar cada máquina
        for machine in filtered_machines:
            machine_id = int(machine['id'])
            machines_processed += 1
            
            try:
                # Calcular cuadre de la máquina
                machine_balance = calcular_cuadre_maquina(
                    machine_id=machine_id,
                    period_start=period_start,
                    period_end=period_end,
                    counters_repo=counters_repo,
                    machines_repo=machines_repo,
                    balances_repo=None,
                    clock=clock,
                    actor=actor,
                    persist=False,
                    lock=False
                )
                
                # Acumular totales globales
                global_totals['in_total'] += machine_balance['in_total']
                global_totals['out_total'] += machine_balance['out_total']
                global_totals['jackpot_total'] += machine_balance['jackpot_total']
                global_totals['billetero_total'] += machine_balance['billetero_total']
                
                # Agregar al resumen (si es reporte detallado)
                if tipo_reporte == "detallado":
                    all_machines_summary.append({
                        'casino_id': place_id,
                        'casino_nombre': place.get('nombre'),
                        'ciudad': place.get('ciudad', 'N/A'),
                        'machine_id': machine_id,
                        'machine_marca': machine.get('marca'),
                        'machine_modelo': machine.get('modelo'),
                        'machine_serial': machine.get('serial'),
                        'machine_asset': machine.get('asset'),
                        'denominacion': machine_balance['denominacion'],
                        'contador_inicial': machine_balance.get('contador_inicial', {}),
                        'contador_final': machine_balance.get('contador_final', {}),
                        'in_total': machine_balance['in_total'],
                        'out_total': machine_balance['out_total'],
                        'jackpot_total': machine_balance['jackpot_total'],
                        'billetero_total': machine_balance['billetero_total'],
                        'utilidad': machine_balance['utilidad_total'],
                        'has_data': True
                    })
                
                machines_with_data += 1
                
            except ValueError:
                machines_without_data += 1
                
                if tipo_reporte == "detallado":
                    all_machines_summary.append({
                        'casino_id': place_id,
                        'casino_nombre': place.get('nombre'),
                        'ciudad': place.get('ciudad', 'N/A'),
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
                        'has_data': False
                    })
                continue
            
            except Exception:
                machines_without_data += 1
                continue
        
        casinos_info.append(casino_info)
    
    # 5. Calcular utilidad final
    utilidad_final = global_totals['in_total'] - (
        global_totals['out_total'] + global_totals['jackpot_total']
    )
    
    # 6. Construir reporte según tipo
    base_report = {
        'period_start': period_start,
        'period_end': period_end,
        'filters_applied': {
            'casino_id': casino_id,
            'marca': marca,
            'modelo': modelo,
            'ciudad': ciudad
        },
        'tipo_reporte': tipo_reporte,
        'casinos_included': casinos_info,
        'category_totals': {
            'in_total': round(global_totals['in_total'], 2),
            'out_total': round(global_totals['out_total'], 2),
            'jackpot_total': round(global_totals['jackpot_total'], 2),
            'billetero_total': round(global_totals['billetero_total'], 2),
            'utilidad_final': round(utilidad_final, 2)
        },
        'total_machines': total_machines_all_casinos,
        'machines_processed': machines_processed,
        'machines_with_data': machines_with_data,
        'machines_without_data': machines_without_data,
        'generated_at': clock().strftime("%Y-%m-%d %H:%M:%S"),
        'generated_by': actor
    }
    
    # Agregar desglose si es detallado
    if tipo_reporte == "detallado":
        all_machines_summary.sort(key=lambda x: (x['casino_id'], x['machine_id']))
        base_report['machines_summary'] = all_machines_summary
    
    # Si es consolidado, solo totales (ya incluidos en base_report)
    # Si es resumen, solo estadísticas (ya incluidas en base_report)
    
    return base_report


def generar_reporte_participacion(
    machine_ids: List[int],
    period_start: str,
    period_end: str,
    porcentaje_participacion: float,
    counters_repo,
    machines_repo,
    places_repo,
    clock: Callable[[], datetime],
    actor: str
) -> Dict[str, Any]:
    """
    Genera un reporte por participación para un grupo de máquinas.
    
    Calcula la utilidad total de las máquinas seleccionadas y aplica
    un porcentaje de participación para obtener el valor de participación.
    
    Fórmula:
        VALOR DE PARTICIPACIÓN = UTILIDAD TOTAL × (PORCENTAJE / 100)
    
    Args:
        machine_ids: Lista de IDs de máquinas a incluir
        period_start: Fecha inicial (YYYY-MM-DD)
        period_end: Fecha final (YYYY-MM-DD)
        porcentaje_participacion: Porcentaje a aplicar (0-100)
        counters_repo: Repositorio de contadores
        machines_repo: Repositorio de máquinas
        places_repo: Repositorio de casinos
        clock: Función que retorna datetime actual
        actor: Usuario que genera el reporte
        
    Returns:
        Dict con:
        - machines_summary: Lista de máquinas con sus utilidades
        - utilidad_total: Suma de utilidades
        - porcentaje_participacion: Porcentaje aplicado
        - valor_participacion: Valor calculado
        - Totales por categoría
        - Estadísticas
        
    Raises:
        NotFoundError: Si alguna máquina no existe
        ValueError: Si el periodo es inválido o no hay datos
    """
    
    # 1. Validar periodo
    if period_start > period_end:
        raise ValueError(
            f"La fecha inicial ({period_start}) debe ser menor o igual a la fecha final ({period_end})"
        )
    
    # 2. Validar porcentaje
    if porcentaje_participacion < 0 or porcentaje_participacion > 100:
        raise ValueError(
            f"El porcentaje de participación debe estar entre 0 y 100 (recibido: {porcentaje_participacion})"
        )
    
    # 3. Inicializar acumuladores
    machines_summary = []
    totales = {
        'in_total': 0.0,
        'out_total': 0.0,
        'jackpot_total': 0.0,
        'billetero_total': 0.0,
        'utilidad_total': 0.0
    }
    
    machines_processed = 0
    machines_with_data = 0
    machines_without_data = 0
    
    # 4. Procesar cada máquina
    for machine_id in machine_ids:
        machines_processed += 1
        
        # Obtener información de la máquina
        machine = machines_repo.get_by_id(machine_id)
        if not machine:
            raise NotFoundError(f"Máquina con ID {machine_id} no encontrada")
        
        # Verificar que la máquina esté activa
        is_active = machine.get('is_active') or machine.get('estado')
        if isinstance(is_active, str):
            is_active = is_active.lower() == 'true'
        
        if not is_active:
            raise ValueError(f"Máquina con ID {machine_id} está inactiva")
        
        # Obtener información del casino
        casino_id = int(machine.get('casino_id', 0))
        casino = places_repo.get_by_id(casino_id) if casino_id else None
        
        try:
            # Calcular cuadre de la máquina
            machine_balance = calcular_cuadre_maquina(
                machine_id=machine_id,
                period_start=period_start,
                period_end=period_end,
                counters_repo=counters_repo,
                machines_repo=machines_repo,
                balances_repo=None,
                clock=clock,
                actor=actor,
                persist=False,
                lock=False
            )
            
            # Acumular totales
            totales['in_total'] += machine_balance['in_total']
            totales['out_total'] += machine_balance['out_total']
            totales['jackpot_total'] += machine_balance['jackpot_total']
            totales['billetero_total'] += machine_balance['billetero_total']
            totales['utilidad_total'] += machine_balance['utilidad_total']
            
            # Agregar al resumen
            machines_summary.append({
                'machine_id': machine_id,
                'machine_marca': machine.get('marca'),
                'machine_modelo': machine.get('modelo'),
                'machine_serial': machine.get('serial'),
                'machine_asset': machine.get('asset'),
                'casino_id': casino_id,
                'casino_nombre': casino.get('nombre') if casino else 'N/A',
                'in_total': machine_balance['in_total'],
                'out_total': machine_balance['out_total'],
                'jackpot_total': machine_balance['jackpot_total'],
                'billetero_total': machine_balance['billetero_total'],
                'utilidad': machine_balance['utilidad_total'],
                'has_data': True
            })
            
            machines_with_data += 1
            
        except ValueError as e:
            # Máquina sin datos en el periodo
            machines_summary.append({
                'machine_id': machine_id,
                'machine_marca': machine.get('marca'),
                'machine_modelo': machine.get('modelo'),
                'machine_serial': machine.get('serial'),
                'machine_asset': machine.get('asset'),
                'casino_id': casino_id,
                'casino_nombre': casino.get('nombre') if casino else 'N/A',
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
    
    # 5. Calcular valor de participación
    # Fórmula: VALOR DE PARTICIPACIÓN = UTILIDAD TOTAL × (PORCENTAJE / 100)
    valor_participacion = totales['utilidad_total'] * (porcentaje_participacion / 100.0)
    
    # 6. Construir reporte
    report = {
        'period_start': period_start,
        'period_end': period_end,
        
        # Máquinas incluidas
        'machines_summary': machines_summary,
        'total_machines': len(machine_ids),
        'machines_processed': machines_processed,
        'machines_with_data': machines_with_data,
        'machines_without_data': machines_without_data,
        
        # Cálculos de participación
        'utilidad_total': round(totales['utilidad_total'], 2),
        'porcentaje_participacion': porcentaje_participacion,
        'valor_participacion': round(valor_participacion, 2),
        
        # Totales por categoría
        'in_total': round(totales['in_total'], 2),
        'out_total': round(totales['out_total'], 2),
        'jackpot_total': round(totales['jackpot_total'], 2),
        'billetero_total': round(totales['billetero_total'], 2),
        
        # Metadatos
        'generated_at': clock().strftime("%Y-%m-%d %H:%M:%S"),
        'generated_by': actor
    }
    
    return report


