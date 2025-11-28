// src/pages/Login.jsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../api/client'
import '../index.css'

export default function LoginPage() {
  const initialForm = { name: '', username: '', password: '', role: 'operador' }
  const [isRegisterMode, setIsRegisterMode] = useState(false)
  const [formData, setFormData] = useState(initialForm)
  const [loading, setLoading] = useState(false)
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
    setFormData(initialForm)
  }

  const fetchUserRecord = async (userId) => {
    if (!userId) return null
    try {
      const { data } = await client.get(`/users/${userId}`)
      return data
    } catch (err) {
      console.warn('No fue posible obtener el detalle del usuario desde /users/:id', err)
      return null
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    
    if (isRegisterMode) {
      // Registro de nuevo usuario
      if (!formData.username || !formData.password) {
        setError('Usuario y contraseña son obligatorios')
        return
      }
      
      setLoading(true)
      try {
        const payload = {
          username: formData.username.trim().toLowerCase(),
          password: formData.password,
          role: formData.role || 'operador'
        }
        await client.post('/users', payload)
        
        alert('Registro exitoso. Inicia sesión ahora.')
        setIsRegisterMode(false)
        setFormData(initialForm)
      } catch (err) {
        console.error('Error en registro:', err)
        const detail = err?.response?.data?.detail || err.message
        if (err.code === 'ERR_NETWORK') {
          setError('No se puede conectar al servidor. Verifica que el backend esté corriendo.')
        } else {
          setError(detail || 'Error al registrar usuario')
        }
      }
      setLoading(false)
    } else {
      // Login de usuario existente
      if (!formData.username || !formData.password) {
        setError('Por favor ingresa usuario y contraseña')
        return
      }
      
      setLoading(true)
      const normalizeUsername = formData.username.trim().toLowerCase()

      try {
        const response = await client.post('/login', {
          username: normalizeUsername,
          password: formData.password
        })

        const userRecord = await fetchUserRecord(response?.data?.id)
        const sessionUser = {
          ...response.data,
          ...userRecord,
          username: response.data?.username ?? normalizeUsername,
          is_active: userRecord?.is_active ?? true,
          lastLogin: new Date().toISOString()
        }

        localStorage.setItem('user', JSON.stringify(sessionUser))
        alert(`¡Bienvenido ${sessionUser.username}!`)
        navigate('/casinos')
      } catch (err) {
        console.error('Error en login:', err)
        console.error('Error response:', err?.response)
        
        // Lista de usuarios válidos (para desarrollo cuando el backend no está disponible)
        const validUsers = {
          user1: 'pass123',
          string: 'string'
        }

        const isNetworkError = err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')

        if (isNetworkError) {
          console.log('Backend no disponible, validando localmente...')
          if (validUsers[normalizeUsername] === formData.password) {
            const fallbackUser = {
              id: 0,
              username: normalizeUsername,
              role: normalizeUsername === 'string' ? 'admin' : 'operador',
              is_active: true,
              lastLogin: new Date().toISOString()
            }
            localStorage.setItem('user', JSON.stringify(fallbackUser))
            alert(`¡Bienvenido ${normalizeUsername}! (Modo desarrollo sin backend)`)
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
      setLoading(false)
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
          <>
            <label htmlFor="name">
              <input
                id="name"
                name="name"
                type="text"
                placeholder="Nombre completo (opcional)"
                value={formData.name}
                onChange={handleChange}
              />
            </label>
            <label htmlFor="role">
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
              >
                <option value="operador">Operador</option>
                <option value="soporte">Soporte</option>
                <option value="admin">Administrador</option>
              </select>
            </label>
          </>
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
          {loading ? 'Procesando...' : (isRegisterMode ? 'Registrar y Entrar' : 'Iniciar Sesión')}
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
