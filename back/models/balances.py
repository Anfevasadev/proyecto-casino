# -------------------------------------------
# back/models/balances.py
# Propósito:
#   - Contratos Pydantic para "cuadres" (consolidados) por máquina y por lugar.
#
# Contexto:
#   - Estos datos suelen ser RESULTADO de cálculos (domain/balances/*) a partir de counters.
#   - Se persisten en CSV: machine_balances.csv y casino_balances.csv.
#
# machine_balances.csv (por máquina):
#   - id: int
#   - machine_id: int
#   - period_start: str (date 'YYYY-MM-DD')
#   - period_end: str (date 'YYYY-MM-DD')
#   - in_total/out_total/jackpot_total/billetero_total: float (≥ 0)
#   - utilidad_total: float (= in_total - (out_total + jackpot_total))
#   - generated_at: str (datetime local)
#   - generated_by: str
#   - locked: bool
#
# casino_balances.csv (por lugar):
#   - id: int
#   - place_id: int
#   - period_start/period_end: str (date)
#   - in_total/out_total/jackpot_total/billetero_total: float
#   - utilidad_total: float
#   - generated_at: str (datetime local)
#   - generated_by: str
#   - locked: bool
#
# Modelos esperados:
#   1) MachineBalanceIn (si se permite solicitar cálculo/persistencia):
#       - machine_id: int
#       - period_start: str ('YYYY-MM-DD')
#       - period_end: str ('YYYY-MM-DD')
#       - locked: bool | None (opcional; default False al generar)
#     Validaciones:
#       * period_start ≤ period_end (comparación de fechas).
#
#   2) MachineBalanceOut:
#       - id, machine_id, period_start, period_end,
#         in_total, out_total, jackpot_total, billetero_total,
#         utilidad_total, generated_at, generated_by, locked
#
#   3) CasinoBalanceIn (similar para lugar):
#       - place_id: int
#       - period_start: str
#       - period_end: str
#       - locked: bool | None
#     Validaciones:
#       * period_start ≤ period_end.
#
#   4) CasinoBalanceOut:
#       - id, place_id, period_start, period_end,
#         in_total, out_total, jackpot_total, billelero_total,
#         utilidad_total, generated_at, generated_by, locked
#
# Consideraciones:
#   - Estos modelos son más de "salida" porque el cálculo se hace en domain.
#     MachineBalanceIn/CasinoBalanceIn sirven si se expone un endpoint que "ordena"
#     generar el balance (domain valida y produce registro).
#   - Validar formato de fechas y que los totales sean ≥ 0 (en Out normalmente ya vienen validados).
# -------------------------------------------

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


# ============ MODELOS PARA MACHINE BALANCES ============

class MachineBalanceIn(BaseModel):
    """Modelo de entrada para generar un balance de máquina"""
    machine_id: int = Field(..., ge=1, description="ID de la máquina")
    period_start: str = Field(..., description="Fecha inicial del periodo (YYYY-MM-DD)")
    period_end: str = Field(..., description="Fecha final del periodo (YYYY-MM-DD)")
    locked: Optional[bool] = Field(False, description="Si True, el balance se marcará como bloqueado")
    
    @field_validator('period_end')
    def validate_period(cls, v, info):
        """Valida que period_end sea mayor o igual a period_start"""
        # info.data contiene los demás campos ya validados
        period_start = info.data.get('period_start')
        if period_start is not None and v < period_start:
            raise ValueError('La fecha final debe ser mayor o igual a la fecha inicial')
        return v


class MachineBalanceOut(BaseModel):
    """Modelo de salida para un balance de máquina"""
    id: int
    machine_id: int
    period_start: str
    period_end: str
    in_total: float = Field(..., ge=0)
    out_total: float = Field(..., ge=0)
    jackpot_total: float = Field(..., ge=0)
    billetero_total: float = Field(..., ge=0)
    utilidad_total: float
    generated_at: str
    generated_by: str
    locked: bool


# ============ MODELOS PARA CASINO BALANCES ============

class CasinoBalanceIn(BaseModel):
    """Modelo de entrada para generar un balance de casino"""
    place_id: int = Field(..., ge=1, description="ID del casino")
    period_start: str = Field(..., description="Fecha inicial del periodo (YYYY-MM-DD)")
    period_end: str = Field(..., description="Fecha final del periodo (YYYY-MM-DD)")
    locked: Optional[bool] = Field(False, description="Si True, el balance se marcará como bloqueado")
    
    @field_validator('period_end')
    def validate_period(cls, v, info):
        """Valida que period_end sea mayor o igual a period_start"""
        period_start = info.data.get('period_start')
        if period_start is not None and v < period_start:
            raise ValueError('La fecha final debe ser mayor o igual a la fecha inicial')
        return v


class CasinoBalanceOut(BaseModel):
    """Modelo de salida para un balance de casino"""
    id: int
    place_id: int
    period_start: str
    period_end: str
    in_total: float = Field(..., ge=0)
    out_total: float = Field(..., ge=0)
    jackpot_total: float = Field(..., ge=0)
    billetero_total: float = Field(..., ge=0)
    utilidad_total: float
    generated_at: str
    generated_by: str
    locked: bool


# ============ MODELOS PARA REPORTES DETALLADOS ============

class CounterSnapshot(BaseModel):
    """Snapshot de contadores en un momento específico"""
    at: Optional[str] = None
    in_amount: float = 0.0
    out_amount: float = 0.0
    jackpot_amount: float = 0.0
    billetero_amount: float = 0.0


class MachineCounterSummary(BaseModel):
    """Resumen de contadores por máquina con información detallada"""
    machine_id: int
    machine_marca: Optional[str] = None
    machine_modelo: Optional[str] = None
    machine_serial: Optional[str] = None
    machine_asset: Optional[str] = None
    denominacion: float = 0.0
    
    # Contadores inicial y final (opcionales)
    contador_inicial: Optional[CounterSnapshot] = None
    contador_final: Optional[CounterSnapshot] = None
    
    # Totales calculados
    in_total: float
    out_total: float
    jackpot_total: float
    billetero_total: float
    utilidad: float  # IN - (OUT + JACKPOT)
    
    # Estado
    has_data: bool = True
    error: Optional[str] = None


class CategoryTotals(BaseModel):
    """Totales agregados por categoría"""
    in_total: float
    out_total: float
    jackpot_total: float
    billetero_total: float
    utilidad_final: float  # IN - (OUT + JACKPOT)


class CasinoDetailedReport(BaseModel):
    """Reporte consolidado detallado de un casino"""
    casino_id: int
    casino_nombre: Optional[str] = None
    period_start: str
    period_end: str
    machines_summary: List[MachineCounterSummary]  # Desglose por máquina
    category_totals: CategoryTotals  # Totales consolidados
    total_machines: int  # Cantidad total de máquinas del casino
    machines_processed: int  # Máquinas procesadas
    machines_with_data: int  # Máquinas con datos en el periodo
    machines_without_data: int  # Máquinas sin datos en el periodo
    generated_at: str
    generated_by: str


# ============ MODELOS PARA FILTROS AVANZADOS DE REPORTES ============

class ReportFilters(BaseModel):
    """
    Filtros avanzados para generación de reportes personalizados.
    Permite filtrar por marca, modelo, ciudad y otros criterios.
    """
    # Filtros de máquinas
    marca: Optional[str] = Field(
        None,
        description="Filtrar por marca de máquina (ej: IGT, Aristocrat)"
    )
    modelo: Optional[str] = Field(
        None,
        description="Filtrar por modelo de máquina (ej: Sphinx, Buffalo)"
    )
    
    # Filtro de ubicación
    ciudad: Optional[str] = Field(
        None,
        description="Filtrar por ciudad donde está ubicado el casino"
    )
    
    # Filtro de casino específico
    casino_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID específico del casino (opcional si se filtra por ciudad)"
    )
    
    # Tipo de reporte
    tipo_reporte: Optional[str] = Field(
        "detallado",
        description="Tipo de reporte: 'detallado' (por máquina), 'consolidado' (totales), 'resumen' (estadísticas)"
    )
    
    # Validaciones
    @field_validator('tipo_reporte')
    @classmethod
    def validate_tipo_reporte(cls, v: Optional[str]) -> str:
        """Valida que el tipo de reporte sea válido"""
        if v is None:
            return "detallado"
        
        v = v.lower().strip()
        allowed_types = ["detallado", "consolidado", "resumen"]
        
        if v not in allowed_types:
            raise ValueError(
                f"Tipo de reporte '{v}' no válido. Opciones: {', '.join(allowed_types)}"
            )
        
        
        return v
    
    @field_validator('marca', 'modelo', 'ciudad')
    @classmethod
    def validate_text_filters(cls, v: Optional[str]) -> Optional[str]:
        """Normaliza filtros de texto"""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        return v


# ============ MODELOS PARA REPORTE POR PARTICIPACIÓN ============

class ParticipationReportIn(BaseModel):
    """
    Modelo de entrada para generar un reporte por participación.
    Permite calcular el valor de participación sobre la utilidad total
    de un grupo de máquinas seleccionadas.
    """
    machine_ids: List[int] = Field(
        ...,
        min_length=1,
        description="Lista de IDs de máquinas a incluir en el reporte"
    )
    period_start: str = Field(
        ...,
        description="Fecha inicial del periodo (YYYY-MM-DD)"
    )
    period_end: str = Field(
        ...,
        description="Fecha final del periodo (YYYY-MM-DD)"
    )
    porcentaje_participacion: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Porcentaje de participación a aplicar (0-100)"
    )
    
    @field_validator('period_start', 'period_end')
    @classmethod
    def validate_dates(cls, v: str) -> str:
        """Valida formato de fechas"""
        from datetime import datetime
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError(f"Fecha '{v}' debe estar en formato YYYY-MM-DD")
    
    @field_validator('machine_ids')
    @classmethod
    def validate_machine_ids(cls, v: List[int]) -> List[int]:
        """Valida que todos los IDs sean positivos y únicos"""
        if not v:
            raise ValueError("Debe seleccionar al menos una máquina")
        
        # Verificar que todos sean positivos
        if any(mid <= 0 for mid in v):
            raise ValueError("Todos los IDs de máquina deben ser positivos")
        
        # Eliminar duplicados manteniendo el orden
        unique_ids = list(dict.fromkeys(v))
        
        return unique_ids


class MachineParticipationDetail(BaseModel):
    """Detalle de una máquina en el reporte de participación"""
    machine_id: int
    machine_marca: Optional[str] = None
    machine_modelo: Optional[str] = None
    machine_serial: Optional[str] = None
    machine_asset: Optional[str] = None
    casino_id: int
    casino_nombre: Optional[str] = None
    
    # Totales de la máquina
    in_total: float
    out_total: float
    jackpot_total: float
    billetero_total: float
    utilidad: float  # IN - (OUT + JACKPOT)
    
    # Estado
    has_data: bool = True
    error: Optional[str] = None


class ParticipationReportOut(BaseModel):
    """
    Modelo de salida para el reporte por participación.
    Muestra la utilidad total del grupo y el valor de participación calculado.
    """
    period_start: str
    period_end: str
    
    # Máquinas incluidas
    machines_summary: List[MachineParticipationDetail]
    total_machines: int
    machines_processed: int
    machines_with_data: int
    machines_without_data: int
    
    # Cálculos de participación
    utilidad_total: float  # Suma de utilidades de todas las máquinas
    porcentaje_participacion: float  # Porcentaje aplicado (0-100)
    valor_participacion: float  # utilidad_total × (porcentaje/100)
    
    # Totales por categoría
    in_total: float
    out_total: float
    jackpot_total: float
    billetero_total: float
    
    # Metadatos
    generated_at: str
    generated_by: str


