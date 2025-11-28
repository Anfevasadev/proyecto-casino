import { useState, useEffect, useCallback, useMemo } from 'react'
import client from '../api/client'
import '../index.css'

const formatPart = (value) => value.toString().padStart(2, '0')

const defaultRange = () => {
  const today = new Date()
  const start = `${today.getFullYear()}-${formatPart(today.getMonth() + 1)}-01`
  const end = `${today.getFullYear()}-${formatPart(today.getMonth() + 1)}-${formatPart(today.getDate())}`
  return { start, end }
}

const REPORT_TYPES = [
  { value: 'detallado', label: 'Detallado (por máquina)' },
  { value: 'consolidado', label: 'Consolidado (totales)' },
  { value: 'resumen', label: 'Resumen (estadísticas)' }
]

const currencyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0
})

export default function ReportsPage() {
  const { start, end } = useMemo(() => defaultRange(), [])

  const [casinos, setCasinos] = useState([])
  const [machines, setMachines] = useState([])
  const [sessionUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user'))
    } catch (err) {
      console.warn('No fue posible parsear el usuario', err)
      return null
    }
  })
  const hideAdvancedTabs = (sessionUser?.role || '').toLowerCase() === 'operador'

  const [selectedCasinoId, setSelectedCasinoId] = useState('')
  const [filters, setFilters] = useState({ marca: '', modelo: '' })
  const [reportType, setReportType] = useState('detallado')
  const [periodStart, setPeriodStart] = useState(start)
  const [periodEnd, setPeriodEnd] = useState(end)

  const [reportData, setReportData] = useState(null)
  const [reportError, setReportError] = useState('')
  const [reportLoading, setReportLoading] = useState(false)

  const [participationSelection, setParticipationSelection] = useState([])
  const [participationStart, setParticipationStart] = useState(start)
  const [participationEnd, setParticipationEnd] = useState(end)
  const [participationPercent, setParticipationPercent] = useState('30')
  const [participationResult, setParticipationResult] = useState(null)
  const [participationError, setParticipationError] = useState('')
  const [participationLoading, setParticipationLoading] = useState(false)

  const [globalError, setGlobalError] = useState('')

  const filteredMachines = useMemo(() => {
    if (!selectedCasinoId) {
      return machines
    }
    return machines.filter((machine) => String(machine.casino_id) === String(selectedCasinoId))
  }, [machines, selectedCasinoId])

  const fetchCasinos = useCallback(async () => {
    try {
      const { data } = await client.get('/places/casino', { params: { only_active: true } })
      const list = Array.isArray(data) ? data : []
      setCasinos(list)
      if (list.length > 0) {
        setSelectedCasinoId((prev) => prev || String(list[0].id))
      }
    } catch (err) {
      setGlobalError(err.message || 'No fue posible obtener los casinos disponibles')
    }
  }, [])

  const fetchMachines = useCallback(async () => {
    try {
      const { data } = await client.get('/machines/', { params: { only_active: true } })
      const list = Array.isArray(data) ? data : []
      setMachines(list)
    } catch (err) {
      setGlobalError((prev) => prev || err.message || 'No fue posible obtener las máquinas registradas')
      setMachines([])
    }
  }, [])

  const handleFilterChange = (event) => {
    const { name, value } = event.target
    setFilters((prev) => ({ ...prev, [name]: value }))
  }

  const buildReportParams = () => {
    const params = {
      period_start: periodStart,
      period_end: periodEnd,
      tipo_reporte: reportType
    }
    if (selectedCasinoId) params.casino_id = Number(selectedCasinoId)
    if (filters.marca.trim()) params.marca = filters.marca.trim()
    if (filters.modelo.trim()) params.modelo = filters.modelo.trim()
    return params
  }

  const fetchReport = useCallback(async () => {
    if (!periodStart || !periodEnd) {
      setReportError('Debes definir un rango de fechas válido')
      return
    }
    if (periodStart > periodEnd) {
      setReportError('La fecha inicial no puede ser mayor a la final')
      return
    }
    setReportLoading(true)
    setReportError('')
    try {
      const params = buildReportParams()
      const { data } = await client.get('/balances/reportes/filtros', { params })
      setReportData(data)
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setReportError(detail)
      } else {
        setReportError(err.message || 'No fue posible generar el reporte con los filtros seleccionados')
      }
      setReportData(null)
    } finally {
      setReportLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [periodStart, periodEnd, reportType, selectedCasinoId, filters])

  const downloadReport = (format) => {
    if (!periodStart || !periodEnd) return
    const params = new URLSearchParams(buildReportParams()).toString()
    const baseURL = (client.defaults.baseURL || '').replace(/\/$/, '')
    window.open(`${baseURL}/balances/reportes/filtros/${format}?${params}`, '_blank')
  }

  const handleParticipationSelection = (event) => {
    const values = Array.from(event.target.selectedOptions, (option) => option.value)
    setParticipationSelection(values)
  }

  const handleParticipationSubmit = async (event) => {
    event.preventDefault()
    setParticipationError('')
    setParticipationResult(null)

    if (!participationStart || !participationEnd) {
      setParticipationError('Define el rango de fechas para el reporte de participación')
      return
    }
    if (participationStart > participationEnd) {
      setParticipationError('La fecha inicial del reporte de participación no puede ser mayor a la final')
      return
    }
    if (participationSelection.length === 0) {
      setParticipationError('Selecciona al menos una máquina para calcular la participación')
      return
    }

    const percentValue = Number(participationPercent)
    if (Number.isNaN(percentValue) || percentValue < 0 || percentValue > 100) {
      setParticipationError('El porcentaje de participación debe estar entre 0 y 100')
      return
    }

    setParticipationLoading(true)
    try {
      const payload = {
        machine_ids: participationSelection.map((id) => Number(id)),
        period_start: participationStart,
        period_end: participationEnd,
        porcentaje_participacion: percentValue
      }
      const { data } = await client.post('/balances/participacion', payload)
      setParticipationResult(data)
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setParticipationError(detail)
      } else if (Array.isArray(detail)) {
        setParticipationError(detail.map((item) => item.msg ?? JSON.stringify(item)).join(' | '))
      } else {
        setParticipationError(err.message || 'No fue posible calcular el reporte de participación')
      }
    } finally {
      setParticipationLoading(false)
    }
  }

  const downloadParticipation = async (format) => {
    if (!participationResult || participationSelection.length === 0) return
    try {
      const payload = {
        machine_ids: participationSelection.map((id) => Number(id)),
        period_start: participationStart,
        period_end: participationEnd,
        porcentaje_participacion: Number(participationPercent)
      }
      const response = await client.post(`/balances/participacion/${format}`, payload, { responseType: 'blob' })
      const blob = new Blob([response.data], { type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url = window.URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `reporte_participacion_${participationStart}_${participationEnd}.${format === 'pdf' ? 'pdf' : 'xlsx'}`
      anchor.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      const detail = err.response?.data?.detail
      const message = typeof detail === 'string' ? detail : (err.message || 'No fue posible descargar el reporte de participación')
      setParticipationError(message)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  useEffect(() => {
    fetchCasinos()
    fetchMachines()
  }, [fetchCasinos, fetchMachines])

  useEffect(() => {
    fetchReport()
  }, [fetchReport])

  const machinesSummary = reportData?.machines_summary || []
  const totals = reportData?.category_totals

  return (
    <div className="casino-layout">
      <header className="casino-header">
        <div className="logo-section">
          <span className="header-icon">📈</span>
          <h2>Módulo de Reportes</h2>
        </div>
        <nav className="casino-nav">
          <a href="/casinos" className="nav-link">Casinos</a>
          <a href="/counters" className="nav-link">Contadores</a>
          {!hideAdvancedTabs && (
            <>
              <a href="/machine-balance" className="nav-link">Cuadre por Máquina</a>
              <a href="/casino-balance" className="nav-link">Cuadre General</a>
              <a href="/reports" className="nav-link active">Reportes</a>
            </>
          )}
          <a href="/profile" className="nav-link">Mi Perfil</a>
          <button onClick={handleLogout} className="logout-btn">Cerrar Sesión</button>
        </nav>
      </header>

      <main className="casino-main">
        {globalError && <p className="error-message">{globalError}</p>}

        <section className="filters-panel">
          <form onSubmit={(event) => { event.preventDefault(); fetchReport() }}>
            <div className="filters-row">
              <div className="form-group">
                <label>Casino (opcional)</label>
                <select
                  className="form-input"
                  value={selectedCasinoId}
                  onChange={(event) => setSelectedCasinoId(event.target.value)}
                >
                  <option value="">
                    Todos los casinos activos
                  </option>
                  {casinos.map((casino) => (
                    <option key={casino.id} value={casino.id}>
                      {casino.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Marca</label>
                <input
                  type="text"
                  name="marca"
                  className="form-input"
                  value={filters.marca}
                  onChange={handleFilterChange}
                  placeholder="IGT, Novomatic..."
                />
              </div>

              <div className="form-group">
                <label>Modelo</label>
                <input
                  type="text"
                  name="modelo"
                  className="form-input"
                  value={filters.modelo}
                  onChange={handleFilterChange}
                  placeholder="Sphinx, Buffalo..."
                />
              </div>

              <div className="form-group">
                <label>Tipo de reporte</label>
                <select
                  className="form-input"
                  value={reportType}
                  onChange={(event) => setReportType(event.target.value)}
                >
                  {REPORT_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="filters-row">
              <div className="form-group">
                <label>Fecha inicial</label>
                <input
                  type="date"
                  className="form-input"
                  value={periodStart}
                  max={periodEnd}
                  onChange={(event) => setPeriodStart(event.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Fecha final</label>
                <input
                  type="date"
                  className="form-input"
                  value={periodEnd}
                  min={periodStart}
                  onChange={(event) => setPeriodEnd(event.target.value)}
                  required
                />
              </div>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  Total máquinas evaluadas
                </label>
                <p className="form-helper">
                  {reportData?.total_machines ?? 0} máquinas filtradas según criterios actuales.
                </p>
              </div>
            </div>

            {reportError && <p className="error-message">{reportError}</p>}

            <div className="form-actions" style={{ justifyContent: 'space-between' }}>
              <div className="btn-group">
                <button type="button" className="btn-secondary" onClick={() => fetchReport()} disabled={reportLoading}>
                  {reportLoading ? 'Procesando...' : 'Actualizar reporte'}
                </button>
                <button type="button" className="btn-secondary" onClick={() => downloadReport('pdf')} disabled={!reportData}>
                  Descargar PDF
                </button>
                <button type="button" className="btn-secondary" onClick={() => downloadReport('excel')} disabled={!reportData}>
                  Descargar Excel
                </button>
              </div>
              <button type="submit" className="btn-submit" disabled={reportLoading}>
                {reportLoading ? 'Calculando...' : 'Generar reporte'}
              </button>
            </div>
          </form>
        </section>

        <section className="balance-preview-panel">
          <div className="records-header">
            <h3>Resumen del reporte</h3>
            {reportData && <span className="text-silver">Generado {reportData.generated_at}</span>}
          </div>
          {!reportData ? (
            <p className="text-silver">Aún no hay datos para mostrar. Ajusta los filtros y genera un reporte.</p>
          ) : (
            <>
              <p className="text-silver">
                Periodo {reportData.period_start} → {reportData.period_end} · Tipo {reportData.tipo_reporte.toUpperCase()}
              </p>
              <div className="balance-grid">
                <div className="balance-card">
                  <h4>Total IN</h4>
                  <p className="balance-amount">{currencyFormatter.format(totals?.in_total || 0)}</p>
                </div>
                <div className="balance-card">
                  <h4>Total OUT</h4>
                  <p className="balance-amount">{currencyFormatter.format(totals?.out_total || 0)}</p>
                </div>
                <div className="balance-card">
                  <h4>Total JACKPOT</h4>
                  <p className="balance-amount">{currencyFormatter.format(totals?.jackpot_total || 0)}</p>
                </div>
                <div className="balance-card">
                  <h4>Total BILLETERO</h4>
                  <p className="balance-amount">{currencyFormatter.format(totals?.billetero_total || 0)}</p>
                </div>
                <div className="balance-card highlight">
                  <h4>Utilidad final</h4>
                  <p className="balance-amount">{currencyFormatter.format(totals?.utilidad_final || 0)}</p>
                </div>
              </div>
              <div className="stats-grid">
                <div className="stat-card">
                  <span className="stat-label">Máquinas totales</span>
                  <strong className="stat-value">{reportData.total_machines}</strong>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Procesadas</span>
                  <strong className="stat-value">{reportData.machines_processed}</strong>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Con datos</span>
                  <strong className="stat-value">{reportData.machines_with_data}</strong>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Sin datos</span>
                  <strong className="stat-value">{reportData.machines_without_data}</strong>
                </div>
              </div>
            </>
          )}
        </section>

        {reportData?.casinos_included && reportData.casinos_included.length > 0 && (
          <section className="records-section">
            <div className="records-header">
              <h3>Casinos incluidos</h3>
            </div>
            <div className="records-table-wrapper">
              <table className="records-table">
                <thead>
                  <tr>
                    <th>Casino</th>
                    <th>Máquinas filtradas</th>
                  </tr>
                </thead>
                <tbody>
                  {reportData.casinos_included.map((casino) => (
                    <tr key={casino.casino_id}>
                      <td>{casino.casino_nombre}</td>
                      <td>{casino.total_machines}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {reportType === 'detallado' && machinesSummary.length > 0 && (
          <section className="records-section">
            <div className="records-header">
              <h3>Detalle por máquina</h3>
            </div>
            <div className="records-table-wrapper">
              <table className="records-table">
                <thead>
                  <tr>
                    <th>Casino</th>
                    <th>Máquina</th>
                    <th>IN</th>
                    <th>OUT</th>
                    <th>JACKPOT</th>
                    <th>BILLETERO</th>
                    <th>Utilidad</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {machinesSummary.map((machine) => (
                    <tr key={`${machine.casino_id}-${machine.machine_id}`} className={!machine.has_data ? 'row-warning' : ''}>
                      <td>{machine.casino_nombre}</td>
                      <td>
                        <div className="machine-cell">
                          <strong>{machine.machine_serial || `ID ${machine.machine_id}`}</strong>
                          <small>{[machine.machine_marca, machine.machine_modelo].filter(Boolean).join(' • ')}</small>
                        </div>
                      </td>
                      <td>{currencyFormatter.format(machine.in_total || 0)}</td>
                      <td>{currencyFormatter.format(machine.out_total || 0)}</td>
                      <td>{currencyFormatter.format(machine.jackpot_total || 0)}</td>
                      <td>{currencyFormatter.format(machine.billetero_total || 0)}</td>
                      <td>{currencyFormatter.format(machine.utilidad || 0)}</td>
                      <td>{machine.has_data ? 'Con datos' : 'Sin registros'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        <section className="participation-panel">
          <header className="records-header">
            <h3>Reporte por participación</h3>
            <span className="text-silver">Calcule porcentajes sobre la utilidad de máquinas seleccionadas</span>
          </header>
          <form onSubmit={handleParticipationSubmit}>
            <div className="filters-row">
              <div className="form-group">
                <label>Máquinas disponibles ({filteredMachines.length})</label>
                <select
                  multiple
                  className="form-input participation-select"
                  value={participationSelection}
                  onChange={handleParticipationSelection}
                >
                  {filteredMachines.map((machine) => (
                    <option key={machine.id} value={machine.id}>
                      {machine.serial || `Máquina ${machine.id}`} · Casino {machine.casino_id}
                    </option>
                  ))}
                </select>
                <small className="form-helper">Mantén presionadas CTRL o CMD para seleccionar múltiples máquinas.</small>
              </div>
              <div className="form-group">
                <label>Porcentaje de participación</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  className="form-input"
                  value={participationPercent}
                  onChange={(event) => setParticipationPercent(event.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Fecha inicial</label>
                <input
                  type="date"
                  className="form-input"
                  value={participationStart}
                  onChange={(event) => setParticipationStart(event.target.value)}
                  max={participationEnd}
                  required
                />
              </div>
              <div className="form-group">
                <label>Fecha final</label>
                <input
                  type="date"
                  className="form-input"
                  value={participationEnd}
                  onChange={(event) => setParticipationEnd(event.target.value)}
                  min={participationStart}
                  required
                />
              </div>
            </div>

            {participationError && <p className="error-message">{participationError}</p>}

            <div className="form-actions" style={{ justifyContent: 'space-between' }}>
              <div className="btn-group">
                <button type="button" className="btn-secondary" onClick={() => downloadParticipation('pdf')} disabled={!participationResult}>
                  Exportar PDF
                </button>
                <button type="button" className="btn-secondary" onClick={() => downloadParticipation('excel')} disabled={!participationResult}>
                  Exportar Excel
                </button>
              </div>
              <button type="submit" className="btn-submit" disabled={participationLoading}>
                {participationLoading ? 'Calculando...' : 'Generar reporte de participación'}
              </button>
            </div>
          </form>

          {participationResult && (
            <div className="participation-summary">
              <div className="participation-cards">
                <div className="balance-card">
                  <h4>Utilidad total</h4>
                  <p className="balance-amount">{currencyFormatter.format(participationResult.utilidad_total)}</p>
                </div>
                <div className="balance-card">
                  <h4>Porcentaje aplicado</h4>
                  <p className="balance-amount">{participationResult.porcentaje_participacion}%</p>
                </div>
                <div className="balance-card highlight">
                  <h4>Valor participación</h4>
                  <p className="balance-amount">{currencyFormatter.format(participationResult.valor_participacion)}</p>
                </div>
              </div>

              <div className="records-table-wrapper" style={{ marginTop: '20px' }}>
                <table className="records-table">
                  <thead>
                    <tr>
                      <th>Máquina</th>
                      <th>Casino</th>
                      <th>IN</th>
                      <th>OUT</th>
                      <th>JACKPOT</th>
                      <th>Utilidad</th>
                    </tr>
                  </thead>
                  <tbody>
                    {participationResult.machines_summary.map((machine) => (
                      <tr key={machine.machine_id}>
                        <td>
                          <div className="machine-cell">
                            <strong>{machine.machine_serial || `ID ${machine.machine_id}`}</strong>
                            <small>{[machine.machine_marca, machine.machine_modelo].filter(Boolean).join(' • ')}</small>
                          </div>
                        </td>
                        <td>{machine.casino_nombre || machine.casino_id}</td>
                        <td>{currencyFormatter.format(machine.in_total || 0)}</td>
                        <td>{currencyFormatter.format(machine.out_total || 0)}</td>
                        <td>{currencyFormatter.format(machine.jackpot_total || 0)}</td>
                        <td>{currencyFormatter.format(machine.utilidad || 0)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
