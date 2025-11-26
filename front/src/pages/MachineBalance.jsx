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

const toNumber = (value) => {
  const parsed = Number(value)
  return Number.isNaN(parsed) ? 0 : parsed
}

const toDate = (value) => {
  if (!value) return null
  const normalized = value.includes('T') ? value : value.replace(' ', 'T')
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
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

export default function MachineBalancePage() {
  const { start, end } = useMemo(() => defaultPeriod(), [])

  const [casinos, setCasinos] = useState([])
  const [machines, setMachines] = useState([])
  const [selectedCasinoId, setSelectedCasinoId] = useState('')
  const [selectedMachineId, setSelectedMachineId] = useState('')
  const [periodStart, setPeriodStart] = useState(start)
  const [periodEnd, setPeriodEnd] = useState(end)
  const [locked, setLocked] = useState(false)

  const [loadingCasinos, setLoadingCasinos] = useState(false)
  const [loadingMachines, setLoadingMachines] = useState(false)
  const [countersLoading, setCountersLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [calculating, setCalculating] = useState(false)

  const [globalError, setGlobalError] = useState('')
  const [countersError, setCountersError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const [counterSnapshots, setCounterSnapshots] = useState([])
  const [initialCounter, setInitialCounter] = useState(null)
  const [finalCounter, setFinalCounter] = useState(null)
  const [balanceResult, setBalanceResult] = useState(null)
  const [history, setHistory] = useState([])

  const selectedMachine = useMemo(() => {
    return machines.find((machine) => String(machine.id) === String(selectedMachineId)) || null
  }, [machines, selectedMachineId])

  const fetchCasinos = useCallback(async () => {
    setLoadingCasinos(true)
    setGlobalError('')
    try {
      const { data } = await client.get('/places/casino', { params: { only_active: true } })
      const list = Array.isArray(data) ? data : []
      setCasinos(list)
      if (list.length > 0) {
        setSelectedCasinoId((prev) => (prev ? prev : String(list[0].id)))
      }
    } catch (err) {
      setGlobalError(err.message || 'No fue posible obtener los casinos disponibles')
    } finally {
      setLoadingCasinos(false)
    }
  }, [])

  const fetchMachines = useCallback(async () => {
    if (!selectedCasinoId) {
      setMachines([])
      setSelectedMachineId('')
      return
    }
    setLoadingMachines(true)
    setGlobalError('')
    try {
      const params = { casino_id: selectedCasinoId, only_active: true }
      const { data } = await client.get('/machines/', { params })
      const list = Array.isArray(data) ? data : []
      setMachines(list)
      if (list.length === 0) {
        setSelectedMachineId('')
      } else if (!list.some((machine) => String(machine.id) === String(selectedMachineId))) {
        setSelectedMachineId(String(list[0].id))
      }
    } catch (err) {
      setGlobalError(err.message || 'No fue posible cargar las máquinas del casino')
      setMachines([])
      setSelectedMachineId('')
    } finally {
      setLoadingMachines(false)
    }
  }, [selectedCasinoId, selectedMachineId])

  const fetchCounters = useCallback(async () => {
    if (!selectedCasinoId || !selectedMachineId || !periodStart || !periodEnd) {
      setCounterSnapshots([])
      setInitialCounter(null)
      setFinalCounter(null)
      return
    }
    setCountersLoading(true)
    setCountersError('')
    try {
      const params = {
        casino_id: selectedCasinoId,
        start_date: periodStart,
        end_date: periodEnd
      }
      const { data } = await client.get('/counters/reportes/consulta', { params })
      const list = Array.isArray(data) ? data.filter((row) => String(row.machine_id) === String(selectedMachineId)) : []
      const sorted = list
        .map((row) => ({ ...row, parsedAt: toDate(row.at) }))
        .filter((row) => !!row.parsedAt)
        .sort((a, b) => a.parsedAt - b.parsedAt)

      setCounterSnapshots(sorted)
      setInitialCounter(sorted[0] || null)
      setFinalCounter(sorted[sorted.length - 1] || null)
    } catch (err) {
      setCountersError(err.message || 'No fue posible recuperar los contadores del periodo')
      setCounterSnapshots([])
      setInitialCounter(null)
      setFinalCounter(null)
    } finally {
      setCountersLoading(false)
    }
  }, [selectedCasinoId, selectedMachineId, periodStart, periodEnd])

  const fetchHistory = useCallback(async () => {
    if (!selectedMachineId) {
      setHistory([])
      return
    }
    setHistoryLoading(true)
    try {
      const params = {
        machine_id: Number(selectedMachineId),
        limit: 25,
        offset: 0
      }
      const { data } = await client.get('/balances/machines', { params })
      setHistory(Array.isArray(data) ? data : [])
    } catch (err) {
      setGlobalError((prev) => prev || err.message || 'No fue posible consultar el historial de cuadres')
      setHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }, [selectedMachineId])

  useEffect(() => {
    fetchCasinos()
  }, [fetchCasinos])

  useEffect(() => {
    fetchMachines()
  }, [fetchMachines])

  useEffect(() => {
    fetchCounters()
  }, [fetchCounters])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  const resetFeedbacks = () => {
    setGlobalError('')
    setSuccessMessage('')
  }

  const handleGenerateBalance = async (event) => {
    event.preventDefault()
    resetFeedbacks()

    if (!selectedCasinoId || !selectedMachineId) {
      setGlobalError('Selecciona un casino y una máquina antes de generar el cuadre')
      return
    }
    if (!periodStart || !periodEnd) {
      setGlobalError('Debes definir la fecha inicial y final del periodo')
      return
    }
    if (periodStart > periodEnd) {
      setGlobalError('La fecha inicial no puede ser mayor a la fecha final')
      return
    }

    setCalculating(true)
    try {
      const payload = {
        machine_id: Number(selectedMachineId),
        period_start: periodStart,
        period_end: periodEnd,
        locked
      }
      const { data } = await client.post('/balances/machines/generate', payload)
      setBalanceResult(data)
      setSuccessMessage('Cuadre generado correctamente')
      setTimeout(() => setSuccessMessage(''), 4000)
      await fetchHistory()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setGlobalError(detail)
      } else if (Array.isArray(detail)) {
        setGlobalError(detail.map((item) => item.msg ?? JSON.stringify(item)).join(' | '))
      } else {
        setGlobalError(err.message || 'No fue posible completar el cuadre de la máquina')
      }
      setBalanceResult(null)
    } finally {
      setCalculating(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  const computeDelta = useCallback(
    (field) => {
      if (!initialCounter || !finalCounter) return 0
      const startValue = toNumber(initialCounter[field])
      const endValue = toNumber(finalCounter[field])
      return endValue - startValue
    },
    [initialCounter, finalCounter]
  )

  const denominacion = useMemo(() => {
    const raw = selectedMachine?.denominacion
    const parsed = Number(raw)
    if (Number.isNaN(parsed) || parsed <= 0) {
      return 1
    }
    return parsed
  }, [selectedMachine])

  const previewTotals = useMemo(() => {
    if (!initialCounter || !finalCounter) return null
    const inDelta = computeDelta('in_amount')
    const outDelta = computeDelta('out_amount')
    const jackpotDelta = computeDelta('jackpot_amount')
    const billeteroDelta = computeDelta('billetero_amount')

    return {
      inDelta,
      outDelta,
      jackpotDelta,
      billeteroDelta,
      monetized: {
        in_total: inDelta * denominacion,
        out_total: outDelta * denominacion,
        jackpot_total: jackpotDelta * denominacion,
        billetero_total: billeteroDelta * denominacion,
        utilidad_total: inDelta * denominacion - (outDelta * denominacion + jackpotDelta * denominacion)
      }
    }
  }, [computeDelta, denominacion, initialCounter, finalCounter])

  const machineLabel = selectedMachine
    ? [selectedMachine.marca, selectedMachine.modelo, selectedMachine.serial].filter(Boolean).join(' • ')
    : 'Sin máquina seleccionada'

  return (
    <div className="casino-layout">
      <header className="casino-header">
        <div className="logo-section">
          <span className="header-icon">🎰</span>
          <h2>Cuadre por Máquina</h2>
        </div>
        <nav className="casino-nav">
          <a href="/casinos" className="nav-link">Casinos</a>
          <a href="/counters" className="nav-link">Contadores</a>
          <a href="/machine-balance" className="nav-link active">Cuadre por Máquina</a>
          <a href="/casino-balance" className="nav-link">Cuadre General</a>
          <a href="/profile" className="nav-link">Mi Perfil</a>
          <button onClick={handleLogout} className="logout-btn">Cerrar Sesión</button>
        </nav>
      </header>

      <main className="casino-main">
        <section className="filters-panel">
          <form onSubmit={handleGenerateBalance}>
            {globalError && <p className="error-message">{globalError}</p>}
            {successMessage && <p className="success-message">{successMessage}</p>}

            <div className="filters-row">
              <div className="form-group">
                <label>Casino</label>
                <select
                  className="form-input"
                  value={selectedCasinoId}
                  onChange={(event) => {
                    setSelectedCasinoId(event.target.value)
                    setSelectedMachineId('')
                    setBalanceResult(null)
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
                <label>Máquina</label>
                <select
                  className="form-input"
                  value={selectedMachineId}
                  onChange={(event) => {
                    setSelectedMachineId(event.target.value)
                    setBalanceResult(null)
                  }}
                  disabled={loadingMachines || machines.length === 0}
                >
                  <option value="" disabled>
                    {loadingMachines ? 'Cargando máquinas...' : 'Selecciona una máquina'}
                  </option>
                  {machines.map((machine) => (
                    <option key={machine.id} value={machine.id}>
                      {machine.serial ? `${machine.serial} (${machine.marca || 'Sin marca'})` : `Máquina ${machine.id}`}
                    </option>
                  ))}
                </select>
                {selectedMachine && (
                  <small className="form-helper">
                    Denominación configurada: {numberFormatter.format(toNumber(selectedMachine.denominacion))}
                  </small>
                )}
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
                    setBalanceResult(null)
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
                    setBalanceResult(null)
                  }}
                  required
                />
              </div>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={locked}
                    onChange={(event) => setLocked(event.target.checked)}
                  />
                  Bloquear cuadre al guardar
                </label>
                <p className="form-helper">
                  Úsalo cuando no desees recalcular el periodo nuevamente.
                </p>
              </div>
            </div>

            <div className="form-actions" style={{ justifyContent: 'flex-end' }}>
              <button type="submit" className="btn-submit" disabled={calculating || !selectedMachineId}>
                {calculating ? 'Calculando...' : 'Generar cuadre'}
              </button>
            </div>
          </form>
        </section>

        <section className="records-section">
          <div className="records-header">
            <h3>Contadores del periodo</h3>
            {countersLoading && <span className="text-silver">Cargando...</span>}
          </div>
          {countersError && <p className="error-message">{countersError}</p>}
          {counterSnapshots.length === 0 ? (
            <p className="text-silver">No hay registros de contadores para la máquina seleccionada en este rango.</p>
          ) : (
            <div className="records-table-wrapper">
              <table className="records-table">
                <thead>
                  <tr>
                    <th>Fecha/Hora</th>
                    <th>IN</th>
                    <th>OUT</th>
                    <th>JACKPOT</th>
                    <th>BILLETERO</th>
                  </tr>
                </thead>
                <tbody>
                  {counterSnapshots.map((record) => (
                    <tr key={`${record.id}-${record.at}`}>
                      <td>{record.at}</td>
                      <td>{numberFormatter.format(toNumber(record.in_amount))}</td>
                      <td>{numberFormatter.format(toNumber(record.out_amount))}</td>
                      <td>{numberFormatter.format(toNumber(record.jackpot_amount))}</td>
                      <td>{numberFormatter.format(toNumber(record.billetero_amount))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="balance-preview-panel">
          <h3>Vista previa de cálculos</h3>
          <p className="text-silver">Máquina: {machineLabel}</p>
          {!previewTotals ? (
            <p className="text-silver">Selecciona un rango con contadores iniciales y finales para calcular diferencias.</p>
          ) : (
            <div className="balance-grid">
              <div className="balance-card">
                <h4>Total IN estimado</h4>
                <p className="balance-amount">{currencyFormatter.format(previewTotals.monetized.in_total)}</p>
                <span className="balance-delta">Δ Contador: {numberFormatter.format(previewTotals.inDelta)}</span>
              </div>
              <div className="balance-card">
                <h4>Total OUT estimado</h4>
                <p className="balance-amount">{currencyFormatter.format(previewTotals.monetized.out_total)}</p>
                <span className="balance-delta">Δ Contador: {numberFormatter.format(previewTotals.outDelta)}</span>
              </div>
              <div className="balance-card">
                <h4>Total JACKPOT</h4>
                <p className="balance-amount">{currencyFormatter.format(previewTotals.monetized.jackpot_total)}</p>
                <span className="balance-delta">Δ Contador: {numberFormatter.format(previewTotals.jackpotDelta)}</span>
              </div>
              <div className="balance-card">
                <h4>Total BILLETERO</h4>
                <p className="balance-amount">{currencyFormatter.format(previewTotals.monetized.billetero_total)}</p>
                <span className="balance-delta">Δ Contador: {numberFormatter.format(previewTotals.billeteroDelta)}</span>
              </div>
              <div className="balance-card highlight">
                <h4>Utilidad estimada</h4>
                <p className="balance-amount">{currencyFormatter.format(previewTotals.monetized.utilidad_total)}</p>
                <span className="balance-delta">Basada en denominación {numberFormatter.format(denominacion)}</span>
              </div>
            </div>
          )}
        </section>

        {balanceResult && (
          <section className="balance-result-panel">
            <div className="records-header">
              <h3>Resultado generado</h3>
              <span className="text-silver">{balanceResult.generated_at}</span>
            </div>
            <div className="balance-grid">
              <div className="balance-card">
                <h4>Periodo</h4>
                <p className="balance-amount">{balanceResult.period_start} → {balanceResult.period_end}</p>
                <span className="balance-delta">Bloqueado: {balanceResult.locked ? 'Sí' : 'No'}</span>
              </div>
              <div className="balance-card">
                <h4>Total IN</h4>
                <p className="balance-amount">{currencyFormatter.format(balanceResult.in_total)}</p>
              </div>
              <div className="balance-card">
                <h4>Total OUT</h4>
                <p className="balance-amount">{currencyFormatter.format(balanceResult.out_total)}</p>
              </div>
              <div className="balance-card">
                <h4>Total JACKPOT</h4>
                <p className="balance-amount">{currencyFormatter.format(balanceResult.jackpot_total)}</p>
              </div>
              <div className="balance-card">
                <h4>Total BILLETERO</h4>
                <p className="balance-amount">{currencyFormatter.format(balanceResult.billetero_total)}</p>
              </div>
              <div className="balance-card highlight">
                <h4>Utilidad</h4>
                <p className="balance-amount">{currencyFormatter.format(balanceResult.utilidad_total)}</p>
                <span className="balance-delta">Generado por {balanceResult.generated_by}</span>
              </div>
            </div>
          </section>
        )}

        <section className="records-section">
          <div className="records-header">
            <h3>Historial reciente</h3>
            {historyLoading && <span className="text-silver">Cargando...</span>}
          </div>
          {history.length === 0 ? (
            <p className="text-silver">Aún no hay cuadres registrados para esta máquina.</p>
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
                    <th>UTILIDAD</th>
                    <th>Estado</th>
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
                      <td>{item.locked ? 'Bloqueado' : 'Editable'}</td>
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
