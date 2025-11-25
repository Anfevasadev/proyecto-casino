import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import MachineCard from '../components/MachineCard'

/**
 * CasinoMachines - Página que muestra las máquinas de un casino específico
 */
export default function CasinoMachines() {
  const { casinoId } = useParams()
  const navigate = useNavigate()
  
  const [casino, setCasino] = useState(null)
  const [machines, setMachines] = useState([])
  const [loading, setLoading] = useState(true)

  // Datos mock de casinos (deberían coincidir con Casinos.jsx)
  const mockCasinos = [
    {
      id: 1,
      name: 'Golden Ace Palace',
      city: 'Las Vegas',
      description: 'Experimenta el lujo y el servicio 5 estrellas.'
    },
    {
      id: 2,
      name: 'Red Dragon Resort',
      city: 'Macau',
      description: 'El destino asiático de apuestas más exclusivo.'
    },
    {
      id: 3,
      name: 'Royal Fortune City',
      city: 'Monte Carlo',
      description: 'Elegancia europea con las mejores mesas de juego.'
    }
  ]

  // Datos mock de máquinas por casino
  const mockMachines = {
    '1': [ // Golden Ace Palace
      {
        id: 'm1-1',
        name: 'Lucky Sevens Supreme',
        type: 'slot',
        status: 'active',
        casinoId: 1
      },
      {
        id: 'm1-2',
        name: 'Diamond Poker Deluxe',
        type: 'poker',
        status: 'active',
        casinoId: 1
      },
      {
        id: 'm1-3',
        name: 'Golden Roulette',
        type: 'roulette',
        status: 'maintenance',
        casinoId: 1
      }
    ],
    '2': [ // Red Dragon Resort
      {
        id: 'm2-1',
        name: 'Dragon\'s Fortune Slots',
        type: 'slot',
        status: 'active',
        casinoId: 2
      },
      {
        id: 'm2-2',
        name: 'Red Phoenix Blackjack',
        type: 'blackjack',
        status: 'active',
        casinoId: 2
      },
      {
        id: 'm2-3',
        name: 'Imperial Poker',
        type: 'poker',
        status: 'inactive',
        casinoId: 2
      }
    ],
    '3': [ // Royal Fortune City
      {
        id: 'm3-1',
        name: 'Monte Carlo Royale Roulette',
        type: 'roulette',
        status: 'active',
        casinoId: 3
      },
      {
        id: 'm3-2',
        name: 'Royal Blackjack Elite',
        type: 'blackjack',
        status: 'active',
        casinoId: 3
      },
      {
        id: 'm3-3',
        name: 'Fortune Wheel Slots',
        type: 'slot',
        status: 'active',
        casinoId: 3
      }
    ]
  }

  useEffect(() => {
    // Simular carga de datos
    setTimeout(() => {
      // Intentar obtener el casino de localStorage primero (para casinos creados dinámicamente)
      const storedCasinos = localStorage.getItem('allCasinos');
      let allCasinos = mockCasinos;
      
      if (storedCasinos) {
        try {
          const parsed = JSON.parse(storedCasinos);
          // Combinar casinos mock con los almacenados
          allCasinos = [...mockCasinos];
          parsed.forEach(stored => {
            if (!allCasinos.find(c => c.id === stored.id)) {
              allCasinos.push(stored);
            }
          });
        } catch (e) {
          console.error('Error parsing stored casinos:', e);
        }
      }
      
      const foundCasino = allCasinos.find(c => c.id === parseInt(casinoId));
      setCasino(foundCasino);
      
      const casinoMachines = mockMachines[casinoId] || [];
      setMachines(casinoMachines);
      
      setLoading(false);
    }, 500);
  }, [casinoId])

  const handleLogout = () => {
    localStorage.removeItem('user')
    navigate('/login')
  }

  const handleBackToCasinos = () => {
    navigate('/casinos')
  }

  if (loading) {
    return (
      <div className="casino-machines-page">
        <div className="loading-spinner">Cargando máquinas...</div>
      </div>
    )
  }

  if (!casino) {
    return (
      <div className="casino-machines-page">
        <div className="error-message">
          <h2>Casino no encontrado</h2>
          <button onClick={handleBackToCasinos} className="back-btn">
            ← Volver a Casinos
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="casino-machines-page">
      {/* Header */}
      <header className="casino-header">
        <div className="logo-section">
          <button onClick={handleBackToCasinos} className="back-btn-inline">
            ← Volver
          </button>
          <span className="header-icon">👑</span>
          <h2>{casino.name}</h2>
        </div>
        <nav className="casino-nav">
          <a href="#" onClick={(e) => { e.preventDefault(); window.location.href = '/profile' }}>
            Mi Perfil
          </a>
          <a href="#" onClick={(e) => { e.preventDefault(); alert('Próximamente') }}>
            Cajero
          </a>
          <button onClick={handleLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </nav>
      </header>

      {/* Casino Info */}
      <div className="casino-machines-info">
        <h2>🎰 Máquinas de Casino</h2>
        <p>📍 {casino.city}</p>
        <p className="casino-description">{casino.description}</p>
      </div>

      {/* Machines Grid */}
      <div className="machines-container">
        {machines.length === 0 ? (
          <div className="no-machines">
            <p>No hay máquinas disponibles en este casino.</p>
          </div>
        ) : (
          <div className="machines-grid">
            {machines.map((machine) => (
              <MachineCard key={machine.id} machine={machine} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
