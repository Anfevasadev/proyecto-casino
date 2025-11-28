import React, { useState } from 'react';
import client from '../api/client';

export default function EditCasinoForm({ casino, onCasinoUpdated, onCancel }) {
  const [formData, setFormData] = useState({
    nombre: casino?.nombre || '',
    direccion: casino?.direccion || '',
    estado: casino?.estado ?? true
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {};
    const trimmedNombre = formData.nombre.trim();
    const trimmedDireccion = formData.direccion.trim();

    if (!trimmedNombre || !trimmedDireccion) {
      setError('Nombre y dirección son obligatorios');
      return;
    }

    if (trimmedNombre !== casino.nombre) {
      payload.nombre = trimmedNombre;
    }
    if (trimmedDireccion !== casino.direccion) {
      payload.direccion = trimmedDireccion;
    }
    if (formData.estado !== casino.estado) {
      payload.estado = formData.estado;
    }

    if (Object.keys(payload).length === 0) {
      setError('Realiza un cambio antes de guardar');
      return;
    }

    setSubmitting(true);
    try {
      await client.put(`/places/casino/${casino.id}`, payload);
      onCasinoUpdated?.();
    } catch (err) {
      setError(err.message || 'No se pudo actualizar el casino');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="create-casino-overlay">
      <div className="create-casino-modal">
        <div className="create-casino-header">
          <h2>✏️ Editar Casino</h2>
          <button onClick={onCancel} className="close-modal-btn">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="create-casino-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="nombre">Nombre del Casino</label>
            <input
              type="text"
              id="nombre"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="direccion">Dirección</label>
            <textarea
              id="direccion"
              name="direccion"
              value={formData.direccion}
              onChange={handleChange}
              className="form-textarea"
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>Código de Casino</label>
            <input
              type="text"
              value={casino.codigo_casino}
              disabled
              className="form-input disabled"
            />
          </div>

          <div className="form-group">
            <label htmlFor="estado">Estado</label>
            <select
              id="estado"
              name="estado"
              value={formData.estado ? 'activo' : 'inactivo'}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                estado: e.target.value === 'activo'
              }))}
              className="form-input"
            >
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
            </select>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="btn-cancel">
              Cancelar
            </button>
            <button type="submit" className="btn-submit" disabled={submitting}>
              {submitting ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
