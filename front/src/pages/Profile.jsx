import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import EditProfileForm from '../components/EditProfileForm'
import '../index.css'

/**
 * Profile - Página de perfil del usuario
 * Muestra información del usuario y permite editarla
 */
export default function Profile() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [showEditForm, setShowEditForm] = useState(false)
  const [stats, setStats] = useState({
    totalGames: 0,
    totalWins: 0,
    totalLosses: 0,
    balance: 0,
    memberSince: null
  })

  useEffect(() => {
    // Cargar datos del usuario desde localStorage
    const userData = localStorage.getItem('user')
    if (!userData) {
      navigate('/login')
      return
    }
    
    try {
      const parsedUser = JSON.parse(userData)
      setUser(parsedUser)
      
      // Cargar estadísticas (mock por ahora)
      const userStats = localStorage.getItem(`stats_${parsedUser.username}`)
      if (userStats) {
        setStats(JSON.parse(userStats))
      } else {
        // Crear estadísticas iniciales
        const initialStats = {
          totalGames: 0,
          totalWins: 0,
          totalLosses: 0,
          balance: 10000, // Balance inicial
          memberSince: new Date().toISOString()
        }
        setStats(initialStats)
        localStorage.setItem(`stats_${parsedUser.username}`, JSON.stringify(initialStats))
      }
    } catch (e) {
      console.error('Error loading user data:', e)
      navigate('/login')
    }
  }, [navigate])

  const handleLogout = () => {
    localStorage.removeItem('user')
    navigate('/login')
  }

  const handleBackToCasinos = () => {
    navigate('/casinos')
  }

  const handleProfileUpdated = (updatedUser) => {
    setUser(updatedUser)
    localStorage.setItem('user', JSON.stringify(updatedUser))
    setShowEditForm(false)
    alert('¡Perfil actualizado exitosamente!')
  }

  if (!user) {
    return (
      <div className="profile-page">
        <div className="loading-spinner">Cargando perfil...</div>
      </div>
    )
  }

  const winRate = stats.totalGames > 0 
    ? ((stats.totalWins / stats.totalGames) * 100).toFixed(1) 
    : 0

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  return (
    <div className="profile-page">
      {/* Header */}
      <header className="casino-header">
        <div className="logo-section">
          <button onClick={handleBackToCasinos} className="back-btn-inline">
            ← Volver a Casinos
          </button>
          <span className="header-icon">👑</span>
          <h2>Mi Perfil</h2>
        </div>
        <nav className="casino-nav">
          <a href="#" onClick={(e) => { e.preventDefault(); navigate('/casinos') }}>
            Casinos
          </a>
          <a href="#" onClick={(e) => { e.preventDefault(); alert('Próximamente') }}>
            Cajero
          </a>
          <button onClick={handleLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </nav>
      </header>

      {/* Contenido Principal */}
      <div className="profile-container">
        {/* Sección de información del usuario */}
        <div className="profile-card">
          <div className="profile-header">
            <div className="profile-avatar">
              <span className="avatar-icon">{user.name?.charAt(0).toUpperCase() || '👤'}</span>
            </div>
            <div className="profile-title">
              <h2>{user.name || 'Usuario'}</h2>
              <p className="profile-username">@{user.username}</p>
              <span className="profile-role">
                {user.role === 'admin' ? '👑 Administrador' : '🎲 Jugador'}
              </span>
            </div>
          </div>

          <div className="profile-info-grid">
            <div className="info-item">
              <span className="info-label">👤 Nombre Completo</span>
              <span className="info-value">{user.name || 'No especificado'}</span>
            </div>
            
            <div className="info-item">
              <span className="info-label">📧 Usuario</span>
              <span className="info-value">{user.username}</span>
            </div>
            
            <div className="info-item">
              <span className="info-label">🎭 Rol</span>
              <span className="info-value">
                {user.role === 'admin' ? 'Administrador' : 'Jugador'}
              </span>
            </div>
            
            <div className="info-item">
              <span className="info-label">📅 Miembro desde</span>
              <span className="info-value">{formatDate(stats.memberSince)}</span>
            </div>
            
            <div className="info-item">
              <span className="info-label">🆔 ID de Usuario</span>
              <span className="info-value">{user.id || 'N/A'}</span>
            </div>

            {user.email && (
              <div className="info-item">
                <span className="info-label">✉️ Email</span>
                <span className="info-value">{user.email}</span>
              </div>
            )}
          </div>

          <button 
            className="edit-profile-btn"
            onClick={() => setShowEditForm(true)}
          >
            ✏️ Editar Perfil
          </button>
        </div>

        {/* Sección de estadísticas */}
        <div className="profile-stats">
          <h3>📊 Estadísticas de Juego</h3>
          
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">💰</div>
              <div className="stat-content">
                <span className="stat-label">Balance</span>
                <span className="stat-value">${stats.balance.toLocaleString()}</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">🎮</div>
              <div className="stat-content">
                <span className="stat-label">Juegos Totales</span>
                <span className="stat-value">{stats.totalGames}</span>
              </div>
            </div>

            <div className="stat-card success">
              <div className="stat-icon">🏆</div>
              <div className="stat-content">
                <span className="stat-label">Victorias</span>
                <span className="stat-value">{stats.totalWins}</span>
              </div>
            </div>

            <div className="stat-card danger">
              <div className="stat-icon">📉</div>
              <div className="stat-content">
                <span className="stat-label">Derrotas</span>
                <span className="stat-value">{stats.totalLosses}</span>
              </div>
            </div>

            <div className="stat-card highlight">
              <div className="stat-icon">📈</div>
              <div className="stat-content">
                <span className="stat-label">Tasa de Victoria</span>
                <span className="stat-value">{winRate}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Sección de actividad reciente */}
        <div className="profile-activity">
          <h3>🕐 Actividad Reciente</h3>
          <div className="activity-list">
            <div className="activity-item">
              <span className="activity-icon">🎰</span>
              <span className="activity-text">Bienvenido a Royal Fortune Casino</span>
              <span className="activity-time">Hoy</span>
            </div>
            <div className="activity-item">
              <span className="activity-icon">📝</span>
              <span className="activity-text">Cuenta creada exitosamente</span>
              <span className="activity-time">{formatDate(stats.memberSince)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de edición */}
      {showEditForm && (
        <EditProfileForm
          user={user}
          onClose={() => setShowEditForm(false)}
          onProfileUpdated={handleProfileUpdated}
        />
      )}
    </div>
  )
}
