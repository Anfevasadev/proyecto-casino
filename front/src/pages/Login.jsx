/*
  Esta página maneja la autenticación del usuario: inicio de sesión y registro.

  Pasos a implementar:
    1. Importar React hooks useState.
    2. Importar useNavigate de react-router-dom para navegar después del inicio de sesión.
    3. Importar axios para solicitudes HTTP.
    4. Crear variables de estado para:
       - name: el nombre completo del usuario al registrarse.
       - username: el nombre de usuario.
       - password: la contraseña.
       - isRegistering: un booleano que indica si el usuario se está registrando
         o iniciando sesión.
       - error: para almacenar cualquier mensaje de error de la API.
    5. Definir dos funciones asíncronas:
      /*
        Esta página maneja la autenticación del usuario: inicio de sesión y registro.

        Pasos a implementar (documentación histórica, ya implementado abajo):
          1. Importar React hooks useState.
          2. Importar useNavigate de react-router-dom.
          3. Importar axios (instancia) para solicitudes HTTP.
          4. Variables de estado: username, password, role, isRegisterMode, error, loading.
          5. Funciones asíncronas: handleRegister (POST /api/v1/users) y handleLogin (POST /api/v1/login).
          6. Formulario con inputs controlados y select de rol en registro.
          7. Botones para enviar y alternar modo.
          8. Mostrar mensajes de error si la API falla.
          9. Tailwind para estilos.
      */

      import React, { useState } from 'react'
      import { useNavigate } from 'react-router-dom'
      import '../index.css'
      import client from '../api/client'

      export default function LoginPage() {
        const [isRegisterMode, setIsRegisterMode] = useState(false)
        const [formData, setFormData] = useState({ username: '', password: '', role: 'operador' })
        const [error, setError] = useState('')
        const [loading, setLoading] = useState(false)
        const navigate = useNavigate()

        const handleChange = (e) => {
          const { name, value } = e.target
          setFormData((prev) => ({ ...prev, [name]: value }))
        }

        const toggleMode = () => {
          setError('')
          setIsRegisterMode((prev) => !prev)
        }

        const handleLogin = async () => {
          setLoading(true)
          setError('')
          try {
            const { username, password } = formData
            await client.post('/login', { username, password })
            navigate('/casinos')
          } catch (err) {
            setError(err.message || 'Error de autenticación')
          } finally {
            setLoading(false)
          }
        }

        const handleRegister = async () => {
          setLoading(true)
          setError('')
          try {
            const { username, password, role } = formData
            await client.post('/users', { username, password, role, is_active: true })
            await handleLogin()
          } catch (err) {
            setError(err.message || 'Error al registrar')
          } finally {
            setLoading(false)
          }
        }

        const handleSubmit = async (e) => {
          e.preventDefault()
          if (loading) return
          if (isRegisterMode) {
            await handleRegister()
          } else {
            await handleLogin()
          }
        }

        return (
          <>
            <div className="cards-decoration">🃏</div>
            <div className="chips-decoration" />
            <form onSubmit={handleSubmit} className="login-form">
              <div className="logo">
                <div className="logo-icon">👑</div>
                <h1>Royal Fortune</h1>
                <p className="subtitle">Casino</p>
              </div>
              <h2 className="title-mode">{isRegisterMode ? 'Crear Cuenta' : 'Acceder al Juego'}</h2>
              {error && <div className="error-msg">{error}</div>}
              <label htmlFor="username">
                <input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="Usuario"
                  value={formData.username}
                  onChange={handleChange}
                  required
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
                  required
                />
              </label>
              {isRegisterMode && (
                <label htmlFor="role">
                  <select
                    id="role"
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    className="role-select"
                  >
                    <option value="operador">Operador</option>
                    <option value="admin">Admin</option>
                    <option value="soporte">Soporte</option>
                  </select>
                </label>
              )}
              <button type="submit" className="primary-btn" disabled={loading}>
                {loading ? 'Procesando...' : isRegisterMode ? 'Registrar y Entrar' : 'Iniciar Sesión'}
              </button>
              <div className="divider"><span>O</span></div>
              <button
                type="button"
                className="secondary-btn toggle-mode-btn"
                onClick={toggleMode}
                disabled={loading}
              >
                {isRegisterMode ? 'Volver a Iniciar Sesión' : 'Crear una Cuenta'}
              </button>
            </form>
          </>
        )
      }