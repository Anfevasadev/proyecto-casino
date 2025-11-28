import { useNavigate } from 'react-router-dom';

export default function CasinoCard({ casino, onEdit }) {
  const navigate = useNavigate();

  if (!casino) {
    return null;
  }

  const { id, nombre, direccion, codigo_casino, estado, created_at } = casino;
  const statusLabel = estado ? 'Activo' : 'Inactivo';
  const statusColor = estado ? '#6ee7b7' : '#f87171';

  return (
    <article className="casino-card">
      <div className="casino-icon-decorative" aria-hidden="true">
        <div className="casino-chips-stack">
          <span className="chip chip-gold" />
          <span className="chip chip-red" />
          <span className="chip chip-black" />
        </div>
        <div className="casino-cards">
          <span className="card card-1">A♠</span>
          <span className="card card-2">K♥</span>
          <span className="card card-3">Q♣</span>
        </div>
      </div>

      <h3 className="casino-card-title">{nombre}</h3>
      <p className="casino-card-city">
        <span className="location-pin">📍</span>
        {direccion}
      </p>

      <p className="casino-card-description">
        Código:&nbsp;
        <strong>{codigo_casino}</strong>
        <br />
        Estado:&nbsp;
        <span style={{ color: statusColor }}>{statusLabel}</span>
        {created_at && (
          <>
            <br />Registrado:&nbsp;
            <span>{created_at}</span>
          </>
        )}
      </p>

      <div className="casino-card-actions">
        <button
          type="button"
          className="casino-card-button"
          onClick={() => navigate(`/casinos/${id}/machines`)}
        >
          Ver máquinas
        </button>
        <button
          type="button"
          className="casino-card-edit-btn"
          onClick={() => onEdit?.(casino)}
          title="Editar casino"
        >
          ✏️
        </button>
      </div>
    </article>
  );
}