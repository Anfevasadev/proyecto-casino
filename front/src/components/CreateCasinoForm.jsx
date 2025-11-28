import React, { useState } from 'react';
import client from '../api/client';

export default function CreateCasinoForm({ onCasinoCreated, onCancel }) {
  const [formData, setFormData] = useState({
    nombre: '',
    direccion: '',
    codigo_casino: ''
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
    
    const nombre = formData.nombre.trim();
    const direccion = formData.direccion.trim();
    const codigo = formData.codigo_casino.trim();

    if (!nombre || !direccion || !codigo) {
      setError('Todos los campos son obligatorios');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        nombre,
        direccion,
        codigo_casino: codigo.toUpperCase()
      };
      await client.post('/places/casino', payload);
      setFormData({ nombre: '', direccion: '', codigo_casino: '' });
      onCasinoCreated?.();
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(item => item.msg ?? JSON.stringify(item)).join(' | '));
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError(err.message || 'No se pudo crear el casino');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="create-casino-overlay">
      <div className="create-casino-modal">
        <div className="create-casino-header">
          <h2>🎰 Crear Nuevo Casino</h2>
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
              placeholder="Ej: Diamond Palace"
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
              placeholder="Dirección completa del establecimiento"
              className="form-textarea"
              rows="3"
            />
          </div>

          <div className="form-group">
            <label htmlFor="codigo_casino">Código Interno</label>
            <input
              type="text"
              id="codigo_casino"
              name="codigo_casino"
              value={formData.codigo_casino}
              onChange={handleChange}
              placeholder="Ej: CAS-001"
              className="form-input"
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="btn-cancel">
              Cancelar
            </button>
            <button type="submit" className="btn-submit" disabled={submitting}>
              {submitting ? 'Guardando...' : 'Crear Casino'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
