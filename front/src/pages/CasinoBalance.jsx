import { useState, useEffect, useCallback, useMemo } from 'react'
import client from '../api/client'
import '../index.css'

const formatDatePart = (value) => value.toString().padStart(2, '0')

const defaultPeriod = () => {
  const now = new Date()
  const start = `${now.getFullYear()}-${formatDatePart(now.getMonth() + 1)}-01`
  const end = `${now.getFullYear()}-${formatDatePart(now.getMonth() + 1)}-${formatDatePart(now.getDate())}`
  return { start, end }
}

const currencyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0
})

const numberFormatter = new Intl.NumberFormat('es-CO', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})

export default function CasinoBalancePage() {
  const { start, end } = useMemo(() => defaultPeriod(), [])

  const [casinos, setCasinos] = useState([])
  const [selectedCasinoId, setSelectedCasinoId] = useState('')
  const [periodStart, setPeriodStart] = useState(start)
  const [periodEnd, setPeriodEnd] = useState(end)
  const [locked, setLocked] = useState(false)

  const [loadingCasinos, setLoadingCasinos] = useState(false)
  const [reportLoading, setReportLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [generating, setGenerating] = useState(false)

  const [error, setError] = useState('')
  const [reportError, setReportError] = useState('')
  const [success, setSuccess] = useState('')

  const [report, setReport] = useState(null)
  const [generatedBalance, setGeneratedBalance] = useState(null)
  const [history, setHistory] = useState([])

  const selectedCasino = useMemo(() => {
    return casinos.find((casino) => String(casino.id) === String(selectedCasinoId)) || null
  }, [casinos, selectedCasinoId])

  const fetchCasinos = useCallback(async () => {
    setLoadingCasinos(true)
    setError('')
    try {
      const { data } = await client.get('/places/casino', { params: { only_active: true } })
      const list = Array.isArray(data) ? data : []
      setCasinos(list)
      if (list.length > 0) {
        setSelectedCasinoId((prev) => prev || String(list[0].id))
      }
    } catch (err) {
      setError(err.message || 'No fue posible obtener los casinos')
    } finally {
      setLoadingCasinos(false)
    }
  }, [])

  const fetchReport = useCallback(async () => {
    if (!selectedCasinoId || !periodStart || !periodEnd) {
      setReport(null)
      return
    }
    setReportLoading(true)
    setReportError('')
    try {
      const { data } = await client.get(`/balances/casinos/${selectedCasinoId}/report`, {
        params: { period_start: periodStart, period_end: periodEnd }
      })
      setReport(data)
    } catch (err) {
      setReport(null)
      setReportError(err.message || 'No fue posible generar la vista previa del reporte')
    } finally {
      setReportLoading(false)
    }
  }, [selectedCasinoId, periodStart, periodEnd])

  const fetchHistory = useCallback(async () => {
    if (!selectedCasinoId) {
      setHistory([])
      return
    }
    setHistoryLoading(true)
    try {
      const params = {
        place_id: Number(selectedCasinoId),
        date_from: periodStart,
        date_to: periodEnd,
        limit: 50,
        offset: 0
      }
      const { data } = await client.get('/balances/casinos', { params })
      setHistory(Array.isArray(data) ? data : [])
    } catch (err) {
      setHistory([])
      setError((prev) => prev || err.message || 'No fue posible cargar el historial de cuadres')
    } finally {
      setHistoryLoading(false)
    }
  }, [selectedCasinoId, periodStart, periodEnd])

  useEffect(() => {
    fetchCasinos()
  }, [fetchCasinos])

  useEffect(() => {
    fetchReport()
  }, [fetchReport])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  const handleGenerateBalance = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')

    if (!selectedCasinoId) {
      setError('Debes seleccionar un casino antes de generar el cuadre')
      return
    }
    if (!periodStart || !periodEnd) {
      setError('Debes definir la fecha inicial y final del periodo')
      return
    }
    if (periodStart > periodEnd) {
      setError('La fecha inicial no puede ser mayor a la fecha final')
      return
    }

    setGenerating(true)
    try {
      const payload = {
        place_id: Number(selectedCasinoId),
        period_start: periodStart,
        period_end: periodEnd,
        locked
      }
      const { data } = await client.post('/balances/casinos/generate', payload)
      setGeneratedBalance(data)
      setSuccess('Cuadre general generado y almacenado correctamente')
      setTimeout(() => setSuccess(''), 4000)
      await fetchHistory()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg ?? JSON.stringify(item)).join(' | '))
      } else {
        setError(err.message || 'No fue posible generar el cuadre general')
      }
      setGeneratedBalance(null)
    } finally {
      setGenerating(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  const handleDownload = (type) => {
    if (!selectedCasinoId || !periodStart || !periodEnd) return
    const baseURL = (client.defaults.baseURL || '').replace(/\/$/, '')
    const url = `${baseURL}/balances/casinos/${selectedCasinoId}/report/${type}?period_start=${periodStart}&period_end=${periodEnd}`
    window.open(url, '_blank')
  }

  const machinesSummary = report?.machines_summary || []
  const totals = report?.category_totals

  return (
    <div className="casino-layout">
      <header className="casino-header">
        <div className="logo-section">
          <span className="header-icon">🏛️</span>
          <h2>Cuadre General por Casino</h2>
        </div>
        <nav className="casino-nav">
          <a href="/casinos" className="nav-link">Casinos</a>
          <a href="/counters" className="nav-link">Contadores</a>
          <a href="/machine-balance" className="nav-link">Cuadre por Máquina</a>
          <a href="/casino-balance" className="nav-link active">Cuadre General</a>
          <a href="/reports" className="nav-link">Reportes</a>
          <a href="/profile" className="nav-link">Mi Perfil</a>
          <button onClick={handleLogout} className="logout-btn">Cerrar Sesión</button>
        </nav>
      </header>

      <main className="casino-main">
        <section className="filters-panel">
          <form onSubmit={handleGenerateBalance}>
            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}

            <div className="filters-row">
              <div className="form-group">
                <label>Casino</label>
                <select
                  className="form-input"
                  value={selectedCasinoId}
                  onChange={(event) => {
                    setSelectedCasinoId(event.target.value)
                    setGeneratedBalance(null)
                  }}
                  disabled={loadingCasinos}
                >
                  <option value="" disabled>
                    {loadingCasinos ? 'Cargando...' : 'Selecciona un casino'}
                  </option>
                  {casinos.map((casino) => (
                    <option key={casino.id} value={casino.id}>
                      {casino.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Fecha inicial</label>
                <input
                  type="date"
                  className="form-input"
                  value={periodStart}
                  max={periodEnd}
                  onChange={(event) => {
                    setPeriodStart(event.target.value)
                    setGeneratedBalance(null)
                  }}
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
                  onChange={(event) => {
                    setPeriodEnd(event.target.value)
                    setGeneratedBalance(null)
                  }}
                  required
                />
              </div>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input type="checkbox" checked={locked} onChange={(event) => setLocked(event.target.checked)} />
                  Bloquear balance al guardar
                </label>
                <p className="form-helper">Evita recalcular el mismo periodo si ya fue auditado.</p>
              </div>
            </div>

            <div className="form-actions" style={{ justifyContent: 'space-between' }}>
              <div className="btn-group">
                <button type="button" className="btn-secondary" onClick={() => fetchReport()} disabled={!selectedCasinoId || reportLoading}>
                  {reportLoading ? 'Actualizando...' : 'Actualizar vista previa'}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => handleDownload('pdf')}
                  disabled={!selectedCasinoId || !report}
                >
                  Descargar PDF
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => handleDownload('excel')}
                  disabled={!selectedCasinoId || !report}
                >
                  Descargar Excel
                </button>
              </div>
              <button type="submit" className="btn-submit" disabled={generating || !selectedCasinoId}>
                {generating ? 'Guardando...' : 'Generar y guardar cuadre'}
              </button>
            </div>
          </form>
        </section>

        <section className="balance-preview-panel">
          <div className="records-header">
            <h3>Vista previa consolidada</h3>
            {reportLoading && <span className="text-silver">Cargando...</span>}
          </div>
          {reportError && <p className="error-message">{reportError}</p>}
          {!report ? (
            <p className="text-silver">Selecciona un casino y periodo para calcular el reporte.</p>
          ) : (
            <>
              <p className="text-silver">{selectedCasino?.nombre} • {periodStart} → {periodEnd}</p>
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
                  <h4>Utilidad estimada</h4>
                  <p className="balance-amount">{currencyFormatter.format(totals?.utilidad_final || 0)}</p>
                </div>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <span className="stat-label">Máquinas totales</span>
                  <strong className="stat-value">{report.total_machines}</strong>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Procesadas</span>
                  <strong className="stat-value">{report.machines_processed}</strong>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Con datos</span>
                  <strong className="stat-value">{report.machines_with_data}</strong>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Sin datos</span>
                  <strong className="stat-value">{report.machines_without_data}</strong>
                </div>
              </div>
            </>
          )}
        </section>

        <section className="records-section">
          <div className="records-header">
            <h3>Detalle por máquina</h3>
          </div>
          {!report ? (
            <p className="text-silver">Aún no hay datos para mostrar.</p>
          ) : machinesSummary.length === 0 ? (
            <p className="text-silver">No hay máquinas registradas para el casino seleccionado.</p>
          ) : (
            <div className="records-table-wrapper">
              <table className="records-table">
                <thead>
                  <tr>
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
                    <tr key={machine.machine_id} className={!machine.has_data ? 'row-warning' : ''}>
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
                      <td>{machine.error ? machine.error : machine.has_data === false ? 'Sin datos' : 'OK'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {generatedBalance && (
          <section className="balance-result-panel">
            <div className="records-header">
              <h3>Último balance guardado</h3>
              <span className="text-silver">ID #{generatedBalance.id}</span>
            </div>
            <div className="balance-grid">
              <div className="balance-card">
                <h4>Periodo</h4>
                <p className="balance-amount">{generatedBalance.period_start} → {generatedBalance.period_end}</p>
                <span className="balance-delta">Bloqueado: {generatedBalance.locked ? 'Sí' : 'No'}</span>
              </div>
              <div className="balance-card">
                <h4>Total IN</h4>
                <p className="balance-amount">{currencyFormatter.format(generatedBalance.in_total)}</p>
              </div>
              <div className="balance-card">
                <h4>Total OUT</h4>
                <p className="balance-amount">{currencyFormatter.format(generatedBalance.out_total)}</p>
              </div>
              <div className="balance-card">
                <h4>Total JACKPOT</h4>
                <p className="balance-amount">{currencyFormatter.format(generatedBalance.jackpot_total)}</p>
              </div>
              <div className="balance-card">
                <h4>Total BILLETERO</h4>
                <p className="balance-amount">{currencyFormatter.format(generatedBalance.billetero_total)}</p>
              </div>
              <div className="balance-card highlight">
                <h4>Utilidad</h4>
                <p className="balance-amount">{currencyFormatter.format(generatedBalance.utilidad_total)}</p>
                <span className="balance-delta">Generado por {generatedBalance.generated_by}</span>
              </div>
            </div>
          </section>
        )}

        <section className="records-section">
          <div className="records-header">
            <h3>Historial de balances</h3>
            {historyLoading && <span className="text-silver">Cargando...</span>}
          </div>
          {history.length === 0 ? (
            <p className="text-silver">No se han encontrado cuadres para el periodo seleccionado.</p>
          ) : (
            <div className="records-table-wrapper">
              <table className="records-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Periodo</th>
                    <th>IN</th>
                    <th>OUT</th>
                    <th>JACKPOT</th>
                    <th>Utilidad</th>
                    <th>Bloqueado</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.id}>
                      <td>{item.id}</td>
                      <td>{item.period_start} → {item.period_end}</td>
                      <td>{currencyFormatter.format(item.in_total)}</td>
                      <td>{currencyFormatter.format(item.out_total)}</td>
                      <td>{currencyFormatter.format(item.jackpot_total)}</td>
                      <td>{currencyFormatter.format(item.utilidad_total)}</td>
                      <td>{item.locked ? 'Sí' : 'No'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
