import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import EditProfileForm from '../components/EditProfileForm'
import '../index.css'

/**
 * Profile - Página de perfil del usuario (datos reales del módulo de usuarios)
 */
export default function Profile() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [showEditForm, setShowEditForm] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [auditTrail, setAuditTrail] = useState([])

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (!userData) {
      navigate('/login')
      return
    }

    try {
      const parsedUser = JSON.parse(userData)
      setUser(parsedUser)
    } catch (error) {
      console.error('Error loading user data:', error)
      navigate('/login')
    }
  }, [navigate])

  const formatDateTime = useCallback((value) => {
    if (!value) return 'No registrado'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }, [])

  const auditKey = user ? `audit_${user.username}` : null

  const createAuditEntry = useCallback((action, detail, customDate) => {
    const timestamp = (() => {
      if (!customDate) return new Date().toISOString()
      const parsed = new Date(customDate)
      return Number.isNaN(parsed.getTime()) ? new Date().toISOString() : parsed.toISOString()
    })()

    return {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      action,
      detail,
      timestamp
    }
  }, [])

  useEffect(() => {
    if (!user || !auditKey) {
      return
    }

    const storedAudit = localStorage.getItem(auditKey)
    if (storedAudit) {
      setAuditTrail(JSON.parse(storedAudit))
      return
    }

    const seedEntries = [
      createAuditEntry('Cuenta registrada', 'El usuario fue creado en el sistema.', user?.created_at || user?.createdAt),
      createAuditEntry('Último acceso registrado', 'Se sincronizó el último acceso disponible.', user?.last_login || user?.lastLogin)
    ].filter(Boolean)

    const initialTrail = seedEntries.length ? seedEntries : [
      createAuditEntry('Perfil inicializado', 'Se creó el registro local del perfil.')
    ]

    setAuditTrail(initialTrail)
    localStorage.setItem(auditKey, JSON.stringify(initialTrail))
  }, [user, auditKey, createAuditEntry])

  const recordAudit = useCallback((action, detail) => {
    if (!user || !auditKey) return
    setAuditTrail((prev) => {
      const entry = createAuditEntry(action, detail)
      const updated = [entry, ...prev].slice(0, 10)
      localStorage.setItem(auditKey, JSON.stringify(updated))
      return updated
    })
  }, [auditKey, createAuditEntry, user])

  const handleLogout = () => {
    localStorage.removeItem('user')
    navigate('/login')
  }

  const handleBackToCasinos = () => {
    navigate('/casinos')
  }

  const handleProfileUpdated = (updatedUser, options = {}) => {
    setUser(updatedUser)
    localStorage.setItem('user', JSON.stringify(updatedUser))
    setShowEditForm(false)

    recordAudit(
      options.passwordUpdated ? 'Contraseña actualizada' : 'Perfil actualizado',
      options.passwordUpdated
        ? 'Se cambió la contraseña del usuario desde el perfil.'
        : 'Se editaron los campos básicos del usuario.'
    )

    setFeedback({ type: 'success', text: 'Datos guardados correctamente.' })
    setTimeout(() => setFeedback(null), 3500)
  }

  const handleAuditExport = () => {
    if (!auditTrail.length) {
      setFeedback({ type: 'warning', text: 'No hay eventos para exportar.' })
      setTimeout(() => setFeedback(null), 3000)
      return
    }

    const header = 'Evento,Detalle,Fecha\n'
    const rows = auditTrail.map((entry) => {
      const sanitize = (value) => String(value ?? '').replace(/"/g, '""')
      return `"${sanitize(entry.action)}","${sanitize(entry.detail)}","${formatDateTime(entry.timestamp)}"`
    }).join('\n')

    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `bitacora_${user.username}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    recordAudit('Bitácora exportada', 'Se descargó el historial de actividad del perfil.')
  }

  if (!user) {
    return (
      <div className="profile-page">
        <div className="loading-spinner">Cargando perfil...</div>
      </div>
    )
  }

  const getRoleLabel = (role) => {
    const roleMap = {
      admin: 'Administrador',
      operador: 'Operador',
      operator: 'Operador',
      soporte: 'Soporte',
      support: 'Soporte'
    }
    return roleMap[role] || 'Usuario'
  }

  const avatarInitial = user.username?.charAt(0)?.toUpperCase() || '👤'
  const lastAccess = user?.last_login || user?.lastLogin || user?.last_access || user?.lastAccess
  const memberSince = user?.created_at || user?.createdAt
  const lastUpdate = user?.updated_at || user?.updatedAt
  const createdBy = user?.created_by || user?.createdBy
  const updatedBy = user?.updated_by || user?.updatedBy

  const navLinks = [
    { label: 'Casinos', path: '/casinos' },
    { label: 'Cuadre por Máquina', path: '/machine-balance' },
    { label: 'Cuadre General', path: '/casino-balance' },
    { label: 'Contadores', path: '/counters' },
    { label: 'Reportes', path: '/reports' }
  ]
  const isOperator = (user?.role || '').toLowerCase() === 'operador'
  const restrictedPaths = new Set(['/machine-balance', '/casino-balance', '/reports'])
  const visibleNavLinks = isOperator
    ? navLinks.filter((link) => !restrictedPaths.has(link.path))
    : navLinks

  return (
    <div className="profile-page">
      <header className="casino-header">
        <div className="logo-section">
          <button onClick={handleBackToCasinos} className="back-btn-inline">
            ← Volver a Casinos
          </button>
          <span className="header-icon">👑</span>
          <h2>Mi Perfil</h2>
        </div>
        <nav className="casino-nav">
          <span className="nav-link active" aria-current="page">
            Mi Perfil
          </span>
          {visibleNavLinks.map(({ label, path }) => (
            <a
              key={path}
              href={path}
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                navigate(path)
              }}
            >
              {label}
            </a>
          ))}
          <button onClick={handleLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </nav>
      </header>

      {feedback && (
        <div className={`profile-feedback ${feedback.type}`}>
          {feedback.text}
        </div>
      )}

      <div className="profile-container">
        <div className="profile-card">
          <div className="profile-header">
            <div className="profile-avatar">
              <span className="avatar-icon">{avatarInitial}</span>
            </div>
            <div className="profile-title">
              <h2>@{user.username}</h2>
              <p className="profile-username">{getRoleLabel(user.role)}</p>
              <span className={`status-badge ${user.is_active === false ? 'inactive' : 'active'}`}>
                {user.is_active === false ? 'Inactivo' : 'Activo'}
              </span>
            </div>
          </div>

          <div className="profile-info-grid">
            <div className="info-item">
              <span className="info-label">📛 Usuario</span>
              <span className="info-value">{user.username}</span>
            </div>
            <div className="info-item">
              <span className="info-label">🎭 Rol</span>
              <span className="info-value">{getRoleLabel(user.role)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">🆔 ID</span>
              <span className="info-value">{user.id ?? 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">📅 Creado el</span>
              <span className="info-value">{formatDateTime(memberSince)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">🕑 Último acceso</span>
              <span className="info-value">{formatDateTime(lastAccess)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">♻️ Última actualización</span>
              <span className="info-value">{formatDateTime(lastUpdate)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">👤 Creado por</span>
              <span className="info-value">{createdBy || 'No registrado'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">🛠️ Actualizado por</span>
              <span className="info-value">{updatedBy || 'No registrado'}</span>
            </div>
          </div>

          <button className="edit-profile-btn" onClick={() => setShowEditForm(true)}>
            ✏️ Actualizar credenciales
          </button>
        </div>

        <section className="profile-section">
          <div className="section-header">
            <div>
              <h3>🗂️ Registro de actividad</h3>
              <p>Bitácora local del módulo de usuarios.</p>
            </div>
            <button className="secondary-btn" onClick={handleAuditExport}>
              Descargar bitácora
            </button>
          </div>

          <ul className="audit-timeline">
            {auditTrail.map((event) => (
              <li className="audit-item" key={event.id}>
                <div className="audit-icon">��️</div>
                <div className="audit-copy">
                  <p className="audit-title">{event.action}</p>
                  <p className="audit-detail">{event.detail}</p>
                </div>
                <span className="audit-time">{formatDateTime(event.timestamp)}</span>
              </li>
            ))}

            {!auditTrail.length && (
              <li className="audit-empty">Sin eventos registrados aún.</li>
            )}
          </ul>
        </section>
      </div>

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
