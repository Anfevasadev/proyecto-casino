import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import MachineCard from '../components/MachineCard'
import CreateMachineForm from '../components/CreateMachineForm'
import client from '../api/client'

/**
 * CasinoMachines
 * Pantalla administrativa para consultar y gestionar las máquinas de un casino.
 */
export default function CasinoMachines() {
  const { casinoId } = useParams()
  const navigate = useNavigate()

  const [casino, setCasino] = useState(null) // Información del casino actual
  const [machines, setMachines] = useState([]) // Máquinas asociadas al casino
  const [loadingCasino, setLoadingCasino] = useState(true) // Estado de carga para el casino
  const [loadingMachines, setLoadingMachines] = useState(true) // Estado de carga para las máquinas
  const [error, setError] = useState('') // Mensajes de error globales
  const [showCreateForm, setShowCreateForm] = useState(false) // Control del modal de creación
  const [togglingSerial, setTogglingSerial] = useState('') // Serial que se está activando/inactivando

  const storedUser = (() => {
    // Se intenta recuperar el usuario autenticado para registrar al actor en los logs
    try {
      return JSON.parse(localStorage.getItem('user'))
    } catch (err) {
      console.error('Error al parsear usuario local', err)
      return null
    }
  })()

  const actor = storedUser?.username || 'system'

  // Obtener la información del casino desde el backend
  const fetchCasino = useCallback(async () => {
    setLoadingCasino(true)
    try {
      const { data } = await client.get('/places/casino', { params: { only_active: true } })
      const found = Array.isArray(data) ? data.find((item) => Number(item.id) === Number(casinoId)) : null
      setCasino(found || null)
      if (!found) {
        setError('Casino no encontrado')
      }
    } catch (err) {
      setError(err.message || 'No fue posible obtener el casino')
    } finally {
      setLoadingCasino(false)
    }
  }, [casinoId])

  // Listar máquinas filtrando por casino
  const fetchMachines = useCallback(async () => {
    setLoadingMachines(true)
    setError('')
    try {
      const { data } = await client.get('/machines/', {
        params: { only_active: true, casino_id: casinoId }
      })

      const list =
        Array.isArray(data)
          ? data
          : Array.isArray(data?.machines)
            ? data.machines
            : Array.isArray(data?.items)
              ? data.items
              : []

      setMachines(list)
    } catch (err) {
      setError(err.message || 'No fue posible obtener las máquinas')
      setMachines([])
    } finally {
      setLoadingMachines(false)
    }
  }, [casinoId])

  useEffect(() => {
    fetchCasino()
    fetchMachines()
  }, [fetchCasino, fetchMachines])

  const handleLogout = () => {
    localStorage.removeItem('user')
    navigate('/login')
  }

  const handleBackToCasinos = () => {
    navigate('/casinos')
  }

  const handleToggleStatus = async (machine) => {
    if (!machine) return
    setTogglingSerial(machine.serial)
    try {
      const endpoint = machine.estado ? '/machines/inactivate' : '/machines/activate'
      await client.post(endpoint, {
        serial: machine.serial,
        actor,
        motivo: machine.estado
          ? 'Inactivación manual desde front'
          : 'Reactivación manual desde front'
      })
      await fetchMachines()
    } catch (err) {
      setError(err.message || 'No se pudo actualizar el estado de la máquina')
    } finally {
      setTogglingSerial('')
    }
  }

  if (loadingCasino) {
    return (
      <div className="casino-machines-page">
        <div className="loading-spinner">Cargando casino...</div>
      </div>
    )
  }

  if (!casino) {
    return (
      <div className="casino-machines-page">
        <div className="error-message">
          <h2>{error || 'Casino no encontrado'}</h2>
          <button onClick={handleBackToCasinos} className="back-btn">
            ← Volver a Casinos
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="casino-machines-page">
      <header className="casino-header">
        <div className="logo-section">
          <button onClick={handleBackToCasinos} className="back-btn-inline">
            ← Volver
          </button>
          <span className="header-icon">👑</span>
          <h2>{casino.nombre}</h2>
        </div>
        <nav className="casino-nav">
          <a href="#" onClick={(e) => { e.preventDefault(); window.location.href = '/profile' }}>
            Mi Perfil
          </a>
          <a href="/counters">
            Contadores
          </a>
          <button onClick={handleLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </nav>
      </header>

      <div className="casino-machines-info">
        <h2>Máquinas registradas</h2>
        <p>📍 {casino.direccion}</p>
        <p className="casino-description">Código interno: {casino.codigo_casino}</p>
        <button className="create-casino-btn" onClick={() => setShowCreateForm(true)}>
          + Registrar máquina
        </button>
      </div>

      {error && (
        <p className="text-center text-red-400 mb-4">{error}</p>
      )}

      <div className="machines-container">
        {loadingMachines ? (
          <div className="loading-spinner">Cargando máquinas...</div>
        ) : machines.length === 0 ? (
          <div className="no-machines">
            <p>No hay máquinas registradas en este casino.</p>
          </div>
        ) : (
          <div className="machines-grid">
            {machines.map((machine) => (
              <MachineCard
                key={machine.id}
                machine={machine}
                onToggleStatus={handleToggleStatus}
              />
            ))}
          </div>
        )}
        {togglingSerial && (
          <p className="text-center text-silver mt-4">
            Actualizando estado de la máquina {togglingSerial}...
          </p>
        )}
      </div>

      {showCreateForm && (
        <CreateMachineForm
          casinoId={casino.id}
          casinoNombre={casino.nombre}
          onClose={() => setShowCreateForm(false)}
          onCreated={fetchMachines}
        />
      )}
    </div>
  )
}
