import React, { useState } from 'react';

export default function EditCasinoForm({ casino, onCasinoUpdated, onCancel }) {
  const [formData, setFormData] = useState({
    name: casino.name || '',
    city: casino.city || '',
    description: casino.description || ''
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.city || !formData.description) {
      setError('Por favor completa todos los campos');
      return;
    }

    // Actualizar casino manteniendo el ID original
    const updatedCasino = {
      ...casino,
      name: formData.name,
      city: formData.city,
      description: formData.description
    };

    onCasinoUpdated(updatedCasino);
    setFormData({ name: '', city: '', description: '' });
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
            <label htmlFor="name">Nombre del Casino</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Ej: Diamond Palace"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="city">Ciudad</label>
            <input
              type="text"
              id="city"
              name="city"
              value={formData.city}
              onChange={handleChange}
              placeholder="Ej: Monaco"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Descripción</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe las características del casino..."
              className="form-textarea"
              rows="3"
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="btn-cancel">
              Cancelar
            </button>
            <button type="submit" className="btn-submit">
              Guardar Cambios
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
