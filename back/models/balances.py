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

