import { useState, useEffect, useCallback, useMemo } from 'react'
import client from '../api/client'
import '../index.css'

const nowToInput = () => {
  const now = new Date()
  const pad = (value) => value.toString().padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`
}

const todayToInput = () => {
  const now = new Date()
  const pad = (value) => value.toString().padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

const toBackendDateTime = (value) => {
  if (!value) return undefined
  if (value.includes('T')) {
    const [datePart, timePartRaw] = value.split('T')
    const timePart = timePartRaw.length === 5 ? `${timePartRaw}:00` : timePartRaw.slice(0, 8)
    return `${datePart} ${timePart}`
  }
  return value
}

export default function CountersPage() {
  const [casinos, setCasinos] = useState([])
  const [selectedCasinoId, setSelectedCasinoId] = useState('')
  const [machines, setMachines] = useState([])
  const [selectedMachineId, setSelectedMachineId] = useState('')
  const [registerDateTime, setRegisterDateTime] = useState(nowToInput())
  const [formValues, setFormValues] = useState({ in_amount: '', out_amount: '', jackpot_amount: '', billetero_amount: '' })
  const [historyDate, setHistoryDate] = useState(todayToInput())
  const [records, setRecords] = useState([])
  const [loadingCasinos, setLoadingCasinos] = useState(true)
  const [loadingMachines, setLoadingMachines] = useState(false)
  const [loadingRecords, setLoadingRecords] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editValues, setEditValues] = useState({ in_amount: '', out_amount: '', jackpot_amount: '', billetero_amount: '' })

  const storedUser = (() => {
    try {
      return JSON.parse(localStorage.getItem('user'))
    } catch (err) {
      console.error('Error al leer usuario almacenado', err)
      return null
    }
  })()

  const actor = storedUser?.username || 'system'
  const hideAdvancedTabs = (storedUser?.role || '').toLowerCase() === 'operador'

  const machinesById = useMemo(() => {
    const map = {}
    machines.forEach((machine) => {
      map[machine.id] = machine
    })
    return map
  }, [machines])

  const fetchCasinos = useCallback(async () => {
    setLoadingCasinos(true)
    try {
      const { data } = await client.get('/places/casino', { params: { only_active: true } })
      const list = Array.isArray(data) ? data : []
      setCasinos(list)
      if (!selectedCasinoId && list.length > 0) {
        setSelectedCasinoId(String(list[0].id))
      }
    } catch (err) {
      setError(err.message || 'No fue posible obtener los casinos')
    } finally {
      setLoadingCasinos(false)
    }
  }, [selectedCasinoId])

  const fetchMachines = useCallback(async () => {
    if (!selectedCasinoId) {
      setMachines([])
      return
    }
    setLoadingMachines(true)
    try {
      const { data } = await client.get(`/counters/machines-by-casino/${selectedCasinoId}`)
      const list = Array.isArray(data) ? data : []
      setMachines(list)
      if (list.length > 0) {
        setSelectedMachineId(String(list[0].id))
      } else {
        setSelectedMachineId('')
      }
    } catch (err) {
      setError(err.message || 'No fue posible obtener las máquinas del casino seleccionado')
      setMachines([])
    } finally {
      setLoadingMachines(false)
    }
  }, [selectedCasinoId])

  const fetchRecords = useCallback(async () => {
    if (!selectedCasinoId || !historyDate) {
      setRecords([])
      return
    }
    setLoadingRecords(true)
    setError('')
    try {
      const params = {
        casino_id: selectedCasinoId,
        start_date: historyDate,
        end_date: historyDate
      }
      const { data } = await client.get('/counters/reportes/consulta', { params })
      const list = Array.isArray(data) ? data : []
      setRecords(list)
    } catch (err) {
      setError(err.message || 'No fue posible consultar los registros')
      setRecords([])
    } finally {
      setLoadingRecords(false)
    }
  }, [selectedCasinoId, historyDate])

  useEffect(() => {
    fetchCasinos()
  }, [fetchCasinos])

  useEffect(() => {
    if (selectedCasinoId) {
      fetchMachines()
      fetchRecords()
    } else {
      setMachines([])
      setRecords([])
    }
  }, [selectedCasinoId, fetchMachines, fetchRecords])

  const resetForm = () => {
    setFormValues({ in_amount: '', out_amount: '', jackpot_amount: '', billetero_amount: '' })
    setRegisterDateTime(nowToInput())
    if (machines.length > 0) {
      setSelectedMachineId(String(machines[0].id))
    }
  }

  const handleFormChange = (event) => {
    const { name, value } = event.target
    setFormValues((prev) => ({ ...prev, [name]: value }))
  }

  const parseAmount = (value) => {
    const numeric = Number(value)
    if (Number.isNaN(numeric) || numeric < 0) {
      throw new Error('Los contadores deben ser números positivos')
    }
    return numeric
  }

  const handleCreateCounter = async (event) => {
    event.preventDefault()
    if (!selectedCasinoId || !selectedMachineId) {
      setError('Selecciona un casino y una máquina para registrar los contadores')
      return
    }
    try {
      const payload = {
        casino_id: Number(selectedCasinoId),
        machine_id: Number(selectedMachineId),
        at: toBackendDateTime(registerDateTime),
        in_amount: parseAmount(formValues.in_amount),
        out_amount: parseAmount(formValues.out_amount),
        jackpot_amount: parseAmount(formValues.jackpot_amount),
        billetero_amount: parseAmount(formValues.billetero_amount)
      }
      await client.post('/counters', payload)
      setFeedback('Contador registrado correctamente')
      setTimeout(() => setFeedback(''), 4000)
      setError('')
      resetForm()
      await fetchRecords()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg ?? JSON.stringify(item)).join(' | '))
      } else {
        setError(err.message || 'No se pudo registrar el contador')
      }
    }
  }

  const startEditing = (record) => {
    setEditingId(record.id)
    setEditValues({
      in_amount: record.in_amount.toString(),
      out_amount: record.out_amount.toString(),
      jackpot_amount: record.jackpot_amount.toString(),
      billetero_amount: record.billetero_amount.toString()
    })
  }

  const cancelEditing = () => {
    setEditingId(null)
    setEditValues({ in_amount: '', out_amount: '', jackpot_amount: '', billetero_amount: '' })
  }

  const handleEditChange = (event) => {
    const { name, value } = event.target
    setEditValues((prev) => ({ ...prev, [name]: value }))
  }

  const handleUpdateRecord = async (record) => {
    if (!selectedCasinoId) return
    try {
      const payload = {
        updates: [
          {
            machine_id: record.machine_id,
            at: record.at,
            in_amount: parseAmount(editValues.in_amount),
            out_amount: parseAmount(editValues.out_amount),
            jackpot_amount: parseAmount(editValues.jackpot_amount),
            billetero_amount: parseAmount(editValues.billetero_amount)
          }
        ]
      }
      await client.put(`/counters/modificacion/${selectedCasinoId}/${historyDate}`, payload, {
        params: { actor }
      })
      setFeedback('Registro actualizado correctamente')
      setTimeout(() => setFeedback(''), 4000)
      cancelEditing()
      await fetchRecords()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg ?? JSON.stringify(item)).join(' | '))
      } else {
        setError(err.message || 'No se pudo actualizar el registro')
      }
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  return (
    <div className="casino-layout">
      <header className="casino-header">
        <div className="logo-section">
          <span className="header-icon">📊</span>
          <h2>Registro de Contadores</h2>
        </div>
        <nav className="casino-nav">
          <a href="/casinos" className="nav-link">Casinos</a>
          <a href="/counters" className="nav-link active">Contadores</a>
          {!hideAdvancedTabs && (
            <>
              <a href="/machine-balance" className="nav-link">Cuadre por Máquina</a>
              <a href="/casino-balance" className="nav-link">Cuadre General</a>
              <a href="/reports" className="nav-link">Reportes</a>
            </>
          )}
          <a href="/profile" className="nav-link">Mi Perfil</a>
          <button onClick={handleLogout} className="logout-btn">Cerrar Sesión</button>
        </nav>
      </header>

      <main className="casino-main" style={{ minHeight: '80vh' }}>
        <section className="filters-panel">
          <div className="filters-row">
            <div className="form-group">
              <label>Casino</label>
              <select
                value={selectedCasinoId}
                onChange={(event) => setSelectedCasinoId(event.target.value)}
                className="form-input"
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
              <label>Fecha de consulta</label>
              <input
                type="date"
                className="form-input"
                value={historyDate}
                onChange={(event) => setHistoryDate(event.target.value)}
              />
            </div>
          </div>
        </section>

        <section className="create-counter-section">
          <h3>Registrar contadores</h3>
          <form className="create-casino-form" onSubmit={handleCreateCounter}>
            {error && <p className="error-message">{error}</p>}
            {feedback && <p className="success-message">{feedback}</p>}

            <div className="grid-2">
              <div className="form-group">
                <label>Máquina</label>
                <select
                  className="form-input"
                  value={selectedMachineId}
                  onChange={(event) => setSelectedMachineId(event.target.value)}
                  disabled={loadingMachines || machines.length === 0}
                >
                  {machines.length === 0 && <option value="">Sin máquinas disponibles</option>}
                  {machines.map((machine) => (
                    <option key={machine.id} value={machine.id}>
                      {machine.serial ? `${machine.marca || ''} ${machine.serial}`.trim() : `Máquina ${machine.id}`}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Fecha y hora</label>
                <input
                  type="datetime-local"
                  className="form-input"
                  value={registerDateTime}
                  onChange={(event) => setRegisterDateTime(event.target.value)}
                  required
                />
              </div>
            </div>

            <div className="grid-4">
              {['in_amount', 'out_amount', 'jackpot_amount', 'billetero_amount'].map((field) => (
                <div className="form-group" key={field}>
                  <label>{field.replace('_amount', '').toUpperCase()}</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    name={field}
                    className="form-input"
                    value={formValues[field]}
                    onChange={handleFormChange}
                    required
                  />
                </div>
              ))}
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-submit" disabled={loadingMachines || !selectedMachineId}>
                Guardar registro
              </button>
            </div>
          </form>
        </section>

        <section className="records-section">
          <div className="records-header">
            <h3>Registros del {historyDate}</h3>
            {loadingRecords && <span className="text-silver">Cargando...</span>}
          </div>
          {records.length === 0 ? (
            <p className="text-silver">No hay contadores para la fecha seleccionada.</p>
          ) : (
            <div className="records-table-wrapper">
              <table className="records-table">
                <thead>
                  <tr>
                    <th>Máquina</th>
                    <th>Fecha/Hora</th>
                    <th>IN</th>
                    <th>OUT</th>
                    <th>JACKPOT</th>
                    <th>BILLETERO</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((record) => {
                    const machineInfo = machinesById[record.machine_id]
                    const machineLabel = machineInfo ? `${machineInfo.marca || ''} ${machineInfo.serial || ''}`.trim() : `Máquina ${record.machine_id}`
                    const isEditing = editingId === record.id
                    return (
                      <tr key={record.id}>
                        <td>{machineLabel}</td>
                        <td>{record.at}</td>
                        {['in_amount', 'out_amount', 'jackpot_amount', 'billetero_amount'].map((field) => (
                          <td key={field}>
                            {isEditing ? (
                              <input
                                type="number"
                                step="0.01"
                                min="0"
                                name={field}
                                value={editValues[field]}
                                onChange={handleEditChange}
                                className="table-input"
                              />
                            ) : (
                              record[field]
                            )}
                          </td>
                        ))}
                        <td>
                          {isEditing ? (
                            <div className="table-actions">
                              <button className="btn-submit" type="button" onClick={() => handleUpdateRecord(record)}>
                                Guardar
                              </button>
                              <button className="btn-cancel" type="button" onClick={cancelEditing}>
                                Cancelar
                              </button>
                            </div>
                          ) : (
                            <button className="btn-submit" type="button" onClick={() => startEditing(record)}>
                              Editar
                            </button>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
