import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import MachineCard from '../components/MachineCard'
import CreateMachineForm from '../components/CreateMachineForm'
import EditMachineForm from '../components/EditMachineForm'
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
  const [sessionUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("user"));
    } catch (err) {
      console.warn("No fue posible parsear el usuario", err);
      return null;
    }
  });
  const isAdmin = sessionUser?.role === "admin" || sessionUser?.role === "soporte";
  const hideAdvancedTabs = (sessionUser?.role || '').toLowerCase() === 'operador';
  const [availableCasinos, setAvailableCasinos] = useState([])
  const [editingMachine, setEditingMachine] = useState(null)

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
      const [activeResponse, inactiveResponse] = await Promise.all([
        client.get('/places/casino', { params: { only_active: true } }),
        client.get('/places/casino', { params: { only_active: false } })
      ])

      const normalize = (response) => Array.isArray(response?.data) ? response.data : []
      const map = new Map()
      ;[...normalize(activeResponse), ...normalize(inactiveResponse)].forEach((place) => {
        if (place?.id == null) return
        map.set(place.id, place)
      })

      const combined = Array.from(map.values())
      const isPlaceActive = (value) => {
        if (typeof value === 'boolean') return value
        if (typeof value === 'string') return value.toLowerCase() === 'true'
        return Boolean(value)
      }
      setAvailableCasinos(combined.filter((place) => isPlaceActive(place?.estado)))

      const found = combined.find((item) => Number(item.id) === Number(casinoId))
      setCasino(found || null)
      if (!found) {
        setError('Casino no encontrado')
      } else {
        setError('')
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

    const extractList = (payload) => (
      Array.isArray(payload)
        ? payload
        : Array.isArray(payload?.machines)
          ? payload.machines
          : Array.isArray(payload?.items)
            ? payload.items
            : []
    )

    try {
      if (isAdmin) {
        const [activeResponse, inactiveResponse] = await Promise.all([
          client.get('/machines/', { params: { only_active: true, casino_id: casinoId } }),
          client.get('/machines/', { params: { only_active: false, casino_id: casinoId } })
        ])

        const combinedMap = new Map()
        ;[...extractList(activeResponse?.data), ...extractList(inactiveResponse?.data)].forEach((machine) => {
          if (machine?.id == null) return
          combinedMap.set(machine.id, machine)
        })
        const combinedList = Array.from(combinedMap.values())
        setMachines(combinedList)
        return combinedList
      }

      const { data } = await client.get('/machines/', {
        params: { only_active: true, casino_id: casinoId }
      })
      const list = extractList(data)
      setMachines(list)
      return list
    } catch (err) {
      setError(err.message || 'No fue posible obtener las máquinas')
      setMachines([])
      return []
    } finally {
      setLoadingMachines(false)
    }
  }, [casinoId, isAdmin])

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

  const handleToggleStatus = async (machine, options = {}) => {
    if (!machine || !isAdmin) return
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
      const updatedList = await fetchMachines()
      if (options.keepModalOpen) {
        const refreshed = updatedList.find((item) => Number(item.id) === Number(machine.id))
        setEditingMachine(refreshed || null)
      }
    } catch (err) {
      setError(err.message || 'No se pudo actualizar el estado de la máquina')
    } finally {
      setTogglingSerial('')
    }
  }

  const handleOpenEdit = (machine) => {
    if (!isAdmin) return
    setEditingMachine(machine)
  }

  const handleMachineUpdated = async () => {
    await fetchMachines()
    setEditingMachine(null)
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
          {!hideAdvancedTabs && (
            <>
              <a href="/machine-balance">
                Cuadre por Máquina
              </a>
              <a href="/casino-balance">
                Cuadre General
              </a>
            </>
          )}
          <a href="/counters">
            Contadores
          </a>
          {!hideAdvancedTabs && (
            <a href="/reports">
              Reportes
            </a>
          )}
          <button onClick={handleLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </nav>
      </header>

      <div className="casino-machines-info">
        <h2>Máquinas registradas</h2>
        <p>📍 {casino.direccion}</p>
        <p className="casino-description">Código interno: {casino.codigo_casino}</p>
        {isAdmin &&  <button className="create-casino-btn" onClick={() => setShowCreateForm(true)}>
          + Registrar máquina
        </button>}
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
                canManage={isAdmin}
                onEdit={handleOpenEdit}
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

      {showCreateForm && isAdmin && (
        <CreateMachineForm
          casinoId={casino.id}
          casinoNombre={casino.nombre}
          onClose={() => setShowCreateForm(false)}
          onCreated={fetchMachines}
        />
      )}

      {isAdmin && editingMachine && (
        <EditMachineForm
          machine={editingMachine}
          casinos={availableCasinos}
          onClose={() => setEditingMachine(null)}
          onUpdated={handleMachineUpdated}
          onToggleStatus={(machine) => handleToggleStatus(machine, { keepModalOpen: true })}
        />
      )}
    </div>
  )
}
