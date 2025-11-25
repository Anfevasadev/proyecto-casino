import React from 'react'

/**
 * MachineCard - Componente para mostrar una máquina de casino individual
 * 
 * @param {Object} machine - Datos de la máquina
 * @param {string} machine.id - ID único de la máquina
 * @param {string} machine.name - Nombre de la máquina
 * @param {string} machine.type - Tipo de máquina (slot, poker, roulette, blackjack)
 * @param {string} machine.status - Estado de la máquina (active, inactive, maintenance)
 */
export default function MachineCard({ machine }) {
  
  // Generar icono basado en el tipo de máquina
  const getMachineIcon = () => {
    switch (machine.type) {
      case 'slot':
        return renderSlotMachine()
      case 'poker':
        return renderPokerMachine()
      case 'roulette':
        return renderRouletteMachine()
      case 'blackjack':
        return renderBlackjackMachine()
      default:
        return renderSlotMachine()
    }
  }

  const renderSlotMachine = () => (
    <div className="machine-icon slot-icon">
      <div className="slot-display">
        <span className="slot-symbol">🍒</span>
        <span className="slot-symbol">🍋</span>
        <span className="slot-symbol">7️⃣</span>
      </div>
      <div className="slot-lever"></div>
    </div>
  )

  const renderPokerMachine = () => (
    <div className="machine-icon poker-icon">
      <div className="poker-cards">
        <div className="card">A♠</div>
        <div className="card">K♥</div>
        <div className="card">Q♦</div>
        <div className="card">J♣</div>
      </div>
    </div>
  )

  const renderRouletteMachine = () => (
    <div className="machine-icon roulette-icon">
      <div className="roulette-wheel"></div>
      <div className="roulette-ball"></div>
    </div>
  )

  const renderBlackjackMachine = () => (
    <div className="machine-icon blackjack-icon">
      <div className="blackjack-table">
        <div className="dealer-cards">
          <div className="mini-card">🂡</div>
          <div className="mini-card">?</div>
        </div>
      </div>
    </div>
  )

  const getStatusColor = () => {
    switch (machine.status) {
      case 'active':
        return '#10b981' // green
      case 'inactive':
        return '#6b7280' // gray
      case 'maintenance':
        return '#f59e0b' // amber
      default:
        return '#6b7280'
    }
  }

  const getStatusText = () => {
    switch (machine.status) {
      case 'active':
        return 'Disponible'
      case 'inactive':
        return 'Inactiva'
      case 'maintenance':
        return 'Mantenimiento'
      default:
        return 'Desconocido'
    }
  }

  return (
    <div className="machine-card">
      {getMachineIcon()}
      
      <div className="machine-info">
        <h3 className="machine-name">{machine.name}</h3>
        <p className="machine-type">
          {machine.type === 'slot' && '🎰 Tragamonedas'}
          {machine.type === 'poker' && '🃏 Video Poker'}
          {machine.type === 'roulette' && '🎡 Ruleta'}
          {machine.type === 'blackjack' && '🂡 Blackjack'}
        </p>
        
        <div className="machine-status" style={{ backgroundColor: getStatusColor() }}>
          {getStatusText()}
        </div>
      </div>
      
      <button 
        className="machine-play-btn"
        disabled={machine.status !== 'active'}
      >
        {machine.status === 'active' ? '▶ Jugar' : '🔒 Bloqueada'}
      </button>
    </div>
  )
}
