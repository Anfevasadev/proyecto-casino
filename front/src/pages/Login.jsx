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
       - handleRegister: envía una solicitud POST a '/api/v1/auth/register' con
         { name, username, password }. Si es exitoso, navegue al inicio de sesión
         o inicie automáticamente la sesión del usuario.
       - handleLogin: envía una solicitud POST a '/api/v1/auth/login' con
         { username, password }. Si es exitoso, navegue a '/casinos'.
    6. Crear un formulario con entradas para name (solo mostrar cuando isRegistering es verdadero),
       username y password. Vincule cada entrada a su variable de estado respectiva.
    7. Agregue un botón de envío que llame a handleRegister o handleLogin según el
       modo.
    8. Proporcione un enlace o botón que alterne entre los modos de inicio de sesión y registro.
    9. Mostrar mensajes de error si la API devuelve un error (por ejemplo, credenciales inválidas).
    10. Usar clases de Tailwind CSS para estilizar el formulario e inputs.

  Nuevamente, deje estas instrucciones solo como comentarios; no implemente el código aquí.
*/

// TODO: Implementar la página de Login según las instrucciones anteriores.



/*
  Pantalla de autenticación. Este componente maneja tanto el inicio
  de sesión como el registro. Utiliza ``useState`` para almacenar el
  estado del formulario y si el usuario está en modo login o registro.
  Se utilizan llamadas HTTP con Axios para comunicarse con el backend.

  useNavigate proviene de react‑router y permite redirigir al usuario
  después de un inicio de sesión exitoso.
*/

// src/pages/Login.jsx (o LoginPage.jsx)

// src/pages/Login.jsx (o LoginPage.jsx)
import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import '../index.css' // Importa los estilos de casino

/*
 * Pantalla de autenticación (Login y Registro).
 * Utiliza los hooks de React para manejar el estado del formulario y Axios
 * para la comunicación con el backend (simulado).
 */

export default function LoginPage() {
  // Flag para alternar entre login y registro
  const [isRegisterMode, setIsRegisterMode] = useState(false)
  // Estado del formulario. 'name' sólo se usa en modo registro.
  const [formData, setFormData] = useState({ name: '', username: '', password: '' })
  const navigate = useNavigate()

  // Manejador para cambiar los valores de los inputs
  const handleChange = (event) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  // Manejador para alternar entre login y registro
  const toggleMode = () => setIsRegisterMode((prev) => !prev)

  // Envío del formulario.
  const handleSubmit = async (event) => {
    event.preventDefault()
    
    // Utilizamos una simulación de alerta ya que el backend no está disponible
    if (isRegisterMode) {
      console.log('Simulación de Registro:', formData)
      // await axios.post('/api/v1/auth/register', formData)
      alert('Registro exitoso. Inicia sesión ahora.')
      setIsRegisterMode(false)
    } else {
      console.log('Simulación de Login:', { username: formData.username, password: formData.password })
      // await axios.post('/api/v1/auth/login', { username: formData.username, password: formData.password })
      
      // Simulación: si no hay error, navegamos.
      alert(`¡Bienvenido ${formData.username}!`)
      navigate('/casinos')
    }
    
    /* Manejo real de errores de Axios (comentado mientras no hay backend)
    try {
      // ... código de Axios aquí
    } catch (err) {
      alert(err?.response?.data?.detail || 'Error inesperado')
    }
    */
  }

  return (
    <>
      {/* Decoraciones de fondo (definidas en index.css) */}
      <div className="cards-decoration">🃏</div>
      <div className="chips-decoration"></div>

      <form onSubmit={handleSubmit} className="login-form">
        
        {/* Logo del casino */}
        <div className="logo">
          <div className="logo-icon">👑</div>
          <h1>Royal Fortune</h1>
          <p className="subtitle">Casino</p>
        </div>

        {/* Título dinámico para el modo */}
        <h2 className="title-mode">
          {isRegisterMode ? 'Crear Cuenta' : 'Acceder al Juego'}
        </h2>

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

        <div className="forgot-password"></div>

        <div className="divider">
          <span>O</span>
        </div>

        {/* Botón de alternancia Login/Registro */}
        <button
          type="button"
          className="secondary-btn toggle-mode-btn"
          onClick={toggleMode}
        >
          {isRegisterMode ? 'Volver a Iniciar Sesión' : 'Crear una Cuenta'}
        </button>
      </form>
    </>
  )
}