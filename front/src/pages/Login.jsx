// src/pages/Login.jsx
import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import '../index.css'

export default function LoginPage() {
  const [isRegisterMode, setIsRegisterMode] = useState(false)
  const [formData, setFormData] = useState({ name: '', username: '', password: '' })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setError('') // Limpiar error al escribir
  }

  const toggleMode = () => {
    setIsRegisterMode((prev) => !prev)
    setError('')
    setFormData({ name: '', username: '', password: '' })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    
    if (isRegisterMode) {
      // Registro de nuevo usuario
      if (!formData.name || !formData.username || !formData.password) {
        setError('Por favor completa todos los campos')
        return
      }
      
      try {
        const response = await axios.post('http://localhost:8000/api/v1/users', {
          username: formData.username,
          password: formData.password,
          name: formData.name,
          role: 'player'
        })
        
        alert('Registro exitoso. Inicia sesión ahora.')
        setIsRegisterMode(false)
        setFormData({ name: '', username: '', password: '' })
      } catch (err) {
        console.error('Error en registro:', err)
        if (err.code === 'ERR_NETWORK') {
          setError('No se puede conectar al servidor. Verifica que el backend esté corriendo.')
        } else {
          setError(err?.response?.data?.detail || 'Error al registrar usuario')
        }
      }
    } else {
      // Login de usuario existente
      if (!formData.username || !formData.password) {
        setError('Por favor ingresa usuario y contraseña')
        return
      }
      
      // Lista de usuarios válidos (para desarrollo cuando el backend no está disponible)
      const validUsers = {
        'user1': 'pass123',
        'string': 'string'
      }
      
      try {
        console.log('Intentando login con:', { username: formData.username })
        
        const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
          username: formData.username,
          password: formData.password
        })
        
        console.log('Respuesta del servidor:', response.data)
        
        // Guardar token o usuario en localStorage
        localStorage.setItem('user', JSON.stringify(response.data))
        alert(`¡Bienvenido ${response.data.username || formData.username}!`)
        navigate('/casinos')
      } catch (err) {
        console.error('Error en login:', err)
        console.error('Error response:', err?.response)
        
        // Si el backend no está disponible, validar localmente para desarrollo
        if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
          console.log('Backend no disponible, validando localmente...')
          
          if (validUsers[formData.username] === formData.password) {
            const userData = {
              id: 1,
              username: formData.username,
              role: formData.username === 'string' ? 'admin' : 'player'
            }
            localStorage.setItem('user', JSON.stringify(userData))
            alert(`¡Bienvenido ${formData.username}! (Modo desarrollo sin backend)`)
            navigate('/casinos')
          } else {
            setError('Usuario o contraseña incorrectos')
          }
        } else if (err.response?.status === 401) {
          setError(err.response.data.detail || 'Usuario o contraseña incorrectos')
        } else if (err.response?.status === 403) {
          setError(err.response.data.detail || 'Usuario inactivo')
        } else {
          setError('Error al iniciar sesión. Intenta nuevamente.')
        }
      }
    }
  }

  return (
    <div className="login-container">
      <div className="cards-decoration">🃏</div>
      <div className="chips-decoration"></div>

      <form onSubmit={handleSubmit} className="login-form">
        <div className="logo">
          <div className="logo-icon">👑</div>
          <h1>Royal Fortune</h1>
          <p className="subtitle">Casino</p>
        </div>

        <h2 className="title-mode">
          {isRegisterMode ? 'Crear Cuenta' : 'Acceder al Juego'}
        </h2>

        {error && (
          <div style={{
            backgroundColor: '#8b0000',
            color: '#fff',
            padding: '10px',
            borderRadius: '5px',
            marginBottom: '15px',
            fontSize: '0.9em'
          }}>
            {error}
          </div>
        )}

        {isRegisterMode && (
          <label htmlFor="name">
            <input
              id="name"
              name="name"
              type="text"
              placeholder="Nombre completo"
              value={formData.name}
              onChange={handleChange}
            />
          </label>
        )}

        <label htmlFor="username">
          <input
            id="username"
            name="username"
            type="text"
            placeholder="Usuario"
            value={formData.username}
            onChange={handleChange}
          />
        </label>

        <label htmlFor="password">
          <input
            id="password"
            name="password"
            type="password"
            placeholder="Contraseña"
            value={formData.password}
            onChange={handleChange}
          />
        </label>

        <button type="submit" className="primary-btn">
          {isRegisterMode ? 'Registrar y Entrar' : 'Iniciar Sesión'}
        </button>

        {!isRegisterMode && (
          <div style={{
            fontSize: '0.75em',
            color: '#c0c0c0',
            marginTop: '10px',
            marginBottom: '10px'
          }}>
            Usuario de prueba: <strong>user1</strong> / Contraseña: <strong>pass123</strong>
          </div>
        )}

        <div className="forgot-password"></div>

        <div className="divider">
          <span>O</span>
        </div>

        <button
          type="button"
          className="secondary-btn toggle-mode-btn"
          onClick={toggleMode}
        >
          {isRegisterMode ? 'Volver a Iniciar Sesión' : 'Crear una Cuenta'}
        </button>
      </form>
    </div>
  )
}
