import { useEffect, useMemo, useState } from 'react'
import client from '../api/client'

/**
 * Modal para editar una máquina existente.
 * Permite actualizar marca, modelo, serial, asset y asignación de casino.
 * También expone la acción de activar/inactivar directamente desde el formulario.
 */
export default function EditMachineForm({ machine, casinos = [], onClose, onUpdated, onToggleStatus }) {
  const [formData, setFormData] = useState({
    marca: machine?.marca ?? '',
    modelo: machine?.modelo ?? '',
    serial: machine?.serial ?? '',
    asset: machine?.asset ?? '',
    casino_id: machine?.casino_id != null ? String(machine.casino_id) : ''
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [toggleLoading, setToggleLoading] = useState(false)
  const [localMachine, setLocalMachine] = useState(machine)

  useEffect(() => {
    setFormData({
      marca: machine?.marca ?? '',
      modelo: machine?.modelo ?? '',
      serial: machine?.serial ?? '',
      asset: machine?.asset ?? '',
      casino_id: machine?.casino_id != null ? String(machine.casino_id) : ''
    })
    setLocalMachine(machine)
  }, [machine])

  const casinoOptions = useMemo(() => {
    const map = new Map()
    ;(casinos || []).forEach((place) => {
      if (place?.id == null) return
      map.set(place.id, place)
    })
    if (machine?.casino_id && !map.has(machine.casino_id)) {
      map.set(machine.casino_id, {
        id: machine.casino_id,
        nombre: `Casino #${machine.casino_id}`,
        estado: machine?.estado ?? true
      })
    }
    return Array.from(map.values())
  }, [casinos, machine])

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setError('')
  }

  const buildPayload = () => {
    if (!localMachine) return null

    const trimmed = {
      marca: formData.marca.trim(),
      modelo: formData.modelo.trim(),
      serial: formData.serial.trim(),
      asset: formData.asset.trim(),
      casino_id: formData.casino_id
    }

    if (!trimmed.marca || !trimmed.modelo || !trimmed.serial || !trimmed.asset || !trimmed.casino_id) {
      setError('Todos los campos son obligatorios. La denominación no se puede modificar.')
      return null
    }

    const payload = {}
    if (trimmed.marca !== localMachine.marca) payload.marca = trimmed.marca
    if (trimmed.modelo !== localMachine.modelo) payload.modelo = trimmed.modelo
    if (trimmed.serial !== localMachine.serial) payload.serial = trimmed.serial
    if (trimmed.asset !== localMachine.asset) payload.asset = trimmed.asset

    const numericCasino = Number(trimmed.casino_id)
    if (!Number.isNaN(numericCasino) && numericCasino !== Number(localMachine.casino_id)) {
      payload.casino_id = numericCasino
    }

    if (Object.keys(payload).length === 0) {
      setError('Realiza un cambio antes de guardar.')
      return null
    }

    return payload
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const payload = buildPayload()
    if (!payload) return

    setSubmitting(true)
    try {
      await client.put(`/machines/${localMachine.id}`, payload)
      onUpdated?.()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg ?? JSON.stringify(item)).join(' | '))
      } else {
        setError(err.message || 'No fue posible actualizar la máquina.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  const handleToggleClick = async () => {
    if (!localMachine || !onToggleStatus) return
    setToggleLoading(true)
    try {
      await onToggleStatus(localMachine)
      setLocalMachine((prev) => (prev ? { ...prev, estado: !prev.estado } : prev))
    } catch (err) {
      setError(err?.message || 'No se pudo cambiar el estado de la máquina.')
    } finally {
      setToggleLoading(false)
    }
  }

  const isActive = Boolean(localMachine?.estado)
  const toggleLabel = isActive ? 'Inactivar máquina' : 'Activar máquina'

  return (
    <div className="create-casino-overlay" role="dialog" aria-modal="true">
      <div className="create-casino-modal">
        <div className="create-casino-header">
          <h2>✏️ Editar máquina</h2>
          <button type="button" className="close-modal-btn" onClick={onClose}>✕</button>
        </div>

        <form className="create-casino-form" onSubmit={handleSubmit}>
          {error && <p className="error-message">{error}</p>}

          <div className="form-group">
            <label htmlFor="marca">Marca</label>
            <input
              id="marca"
              name="marca"
              className="form-input"
              value={formData.marca}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="modelo">Modelo</label>
            <input
              id="modelo"
              name="modelo"
              className="form-input"
              value={formData.modelo}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="serial">Serial</label>
            <input
              id="serial"
              name="serial"
              className="form-input"
              value={formData.serial}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="asset">Asset</label>
            <input
              id="asset"
              name="asset"
              className="form-input"
              value={formData.asset}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="casino_id">Casino asignado</label>
            <select
              id="casino_id"
              name="casino_id"
              className="form-input"
              value={formData.casino_id}
              onChange={handleChange}
            >
              <option value="">Selecciona un casino</option>
              {casinoOptions.map((place) => (
                <option key={place.id} value={place.id}>
                  {place.nombre} {place.estado ? '' : '(inactivo)'}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Denominación</label>
            <input
              type="text"
              className="form-input disabled"
              value={localMachine?.denominacion ?? ''}
              disabled
            />
            <small className="form-helper">La denominación no se puede editar.</small>
          </div>

          <div className="machine-status-toggle">
            <span className="machine-card__status" style={{ backgroundColor: isActive ? '#10b981' : '#ef4444' }}>
              {isActive ? 'Activa' : 'Inactiva'}
            </span>
            <button
              type="button"
              className="machine-card__action-btn"
              onClick={handleToggleClick}
              disabled={toggleLoading}
            >
              {toggleLoading ? 'Actualizando...' : toggleLabel}
            </button>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn-submit" disabled={submitting}>
              {submitting ? 'Guardando...' : 'Guardar cambios'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
