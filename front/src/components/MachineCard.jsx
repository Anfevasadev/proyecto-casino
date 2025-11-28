// import PropTypes from 'prop-types'

/**
 * MachineCard
 * Tarjeta informativa administrativa para cada máquina registrada en un casino.
 * Muestra los campos exigidos por el requerimiento y expone un botón para
 * activar/inactivar la máquina mediante el callback recibido.
 */
export default function MachineCard({ machine, canManage = false, onEdit }) {
  if (!machine) {
    return null
  }

  const isActive = Boolean(machine.estado)
  const statusLabel = isActive ? 'Activa' : 'Inactiva'
  const statusColor = isActive ? '#10b981' : '#ef4444'

  return (
    <article className="machine-card" aria-label={`Máquina serial ${machine.serial}`}>
      <header className="machine-card__header">
        <div>
          <p className="machine-card__label">Marca</p>
          <p className="machine-card__value">{machine.marca}</p>
        </div>
        <div>
          <p className="machine-card__label">Modelo</p>
          <p className="machine-card__value">{machine.modelo}</p>
        </div>
      </header>

      <section className="machine-card__body">
        <p><strong>Serial:</strong> {machine.serial}</p>
        <p><strong>Asset:</strong> {machine.asset}</p>
        <p><strong>Denominación:</strong> {machine.denominacion}</p>
        <p><strong>Casino ID:</strong> {machine.casino_id}</p>
      </section>

      <footer className="machine-card__footer">
        <span className="machine-card__status" style={{ backgroundColor: statusColor }}>
          {statusLabel}
        </span>
        {canManage && (
          <button
            type="button"
            className="machine-card__action-btn"
            onClick={() => onEdit?.(machine)}
          >
            Editar
          </button>
        )}
      </footer>
    </article>
  )
}

// MachineCard.propTypes = {
//   machine: PropTypes.shape({
//     id: PropTypes.number.isRequired,
//     marca: PropTypes.string.isRequired,
//     modelo: PropTypes.string.isRequired,
//     serial: PropTypes.string.isRequired,
//     asset: PropTypes.string.isRequired,
//     denominacion: PropTypes.string.isRequired,
//     estado: PropTypes.bool.isRequired,
//     casino_id: PropTypes.number.isRequired
//   }),
//   canManage: PropTypes.bool,
//   onEdit: PropTypes.func
// }
