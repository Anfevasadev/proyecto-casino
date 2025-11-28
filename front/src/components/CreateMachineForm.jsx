import { useState } from 'react'
// import PropTypes from 'prop-types'
import client from '../api/client'

/**
 * Modal para registrar una máquina ligada al casino actual.
 * Incluye validaciones mínimas y comunica el resultado al padre via callbacks.
 */
export default function CreateMachineForm({ casinoId, casinoNombre, onClose, onCreated }) {
  const [formData, setFormData] = useState({
    marca: '',
    modelo: '',
    serial: '',
    asset: '',
    denominacion: ''
  })
  const [error, setError] = useState('') // Mensaje de error visible para el usuario
  const [submitting, setSubmitting] = useState(false) // Bandera para deshabilitar botones durante el envío

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setError('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const trimmed = {
      marca: formData.marca.trim(),
      modelo: formData.modelo.trim(),
      serial: formData.serial.trim(),
      asset: formData.asset.trim(),
      denominacion: formData.denominacion.trim()
    }

    if (Object.values(trimmed).some((value) => !value)) {
      setError('Todos los campos son obligatorios.')
      return
    }

    setSubmitting(true)
    try {
      await client.post('/machines/', {
        marca: trimmed.marca,
        modelo: trimmed.modelo,
        serial: trimmed.serial,
        asset: trimmed.asset,
        denominacion: trimmed.denominacion,
        place_id: Number(casinoId),
        is_active: true
      })
      onCreated?.()
      onClose?.()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg ?? JSON.stringify(item)).join(' | '))
      } else {
        setError(err.message || 'No se pudo registrar la máquina.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="create-casino-overlay" role="dialog" aria-modal="true">
      <div className="create-casino-modal">
        <div className="create-casino-header">
          <h2>Agregar máquina a {casinoNombre}</h2>
          <button type="button" className="close-modal-btn" onClick={onClose}>✕</button>
        </div>

        <form className="create-casino-form" onSubmit={handleSubmit}>
          {error && <p className="error-message">{error}</p>}

          <div className="form-group">
            <label htmlFor="marca">Marca</label>
            <input id="marca" name="marca" className="form-input" value={formData.marca} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="modelo">Modelo</label>
            <input id="modelo" name="modelo" className="form-input" value={formData.modelo} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="serial">Serial</label>
            <input id="serial" name="serial" className="form-input" value={formData.serial} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="asset">Asset</label>
            <input id="asset" name="asset" className="form-input" value={formData.asset} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="denominacion">Denominación</label>
            <input id="denominacion" name="denominacion" className="form-input" value={formData.denominacion} onChange={handleChange} />
            <small className="form-helper">Este valor no podrá editarse luego.</small>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-submit" disabled={submitting}>
              {submitting ? 'Guardando...' : 'Registrar máquina'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// CreateMachineForm.propTypes = {
//   casinoId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
//   casinoNombre: PropTypes.string,
//   onClose: PropTypes.func,
//   onCreated: PropTypes.func
// }
