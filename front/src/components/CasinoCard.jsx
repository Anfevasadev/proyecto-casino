/*
  Este componente representa una única tarjeta de casino utilizada en la lista de casinos.
  Debe recibir detalles del casino como props (como id, nombre, dirección o
  descripción) y renderizarlos en un diseño de tarjeta simple usando clases
  de Tailwind CSS para estilizar.

  La tarjeta debe incluir:
    - El nombre del casino como encabezado.
    - Detalles adicionales como la ciudad o dirección si están disponibles.
  Asegúrese de elegir elementos HTML semánticos (por ejemplo, <div>, <h3>, <p>). Este
  componente será utilizado por la página Casinos para mostrar cada casino en una
  colección.

  La implementación JSX real se ha dejado intencionalmente fuera. Usa estas
  instrucciones como un plano para tu implementación.
*/

// TODO: Implementar el componente CasinoCard según las instrucciones anteriores.
import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Este componente representa una única tarjeta de casino.
 *
 * Props:
 * @param {object} casino - Objeto con los detalles del casino.
 * @param {string} casino.id - ID único del casino.
 * @param {string} casino.name - Nombre del casino.
 * @param {string} casino.city - Ciudad donde se encuentra.
 * @param {string} casino.description - Descripción corta.
 * @param {function} onEdit - Función para editar el casino.
 */
export default function CasinoCard({ casino = {}, onEdit }) {
  const { id, name, city, description } = casino;
  const navigate = useNavigate();

  // Generar un ícono basado en el ID del casino para consistencia
  const getRandomIcon = (casinoId) => {
    const icons = ['chips', 'dice', 'slot', 'cards', 'roulette', 'poker'];
    const index = casinoId ? casinoId % icons.length : 0;
    return icons[index];
  };

  // Iconos diferentes para cada casino
  const getCasinoIcon = () => {
    // Casinos predefinidos
    if (name.includes('Golden')) {
      return renderChipsAndCards();
    } else if (name.includes('Red Dragon')) {
      return renderDiceAndRoulette();
    } else if (name.includes('Royal Fortune')) {
      return renderSlotMachine();
    } 
    
    // Casinos nuevos - generar icono aleatorio basado en ID
    const iconType = getRandomIcon(id);
    
    switch(iconType) {
      case 'chips':
        return renderChipsOnly();
      case 'dice':
        return renderDiceOnly();
      case 'slot':
        return renderSlotMachine();
      case 'cards':
        return renderCardsOnly();
      case 'roulette':
        return renderRouletteOnly();
      case 'poker':
        return renderPokerChips();
      default:
        return renderChipsAndCards();
    }
  };

  const renderChipsAndCards = () => (
    <div className="casino-icon-decorative">
      <div className="casino-chips-stack">
        <div className="chip chip-gold"></div>
        <div className="chip chip-red"></div>
        <div className="chip chip-black"></div>
      </div>
      <div className="casino-cards">
        <div className="card card-1">♠</div>
        <div className="card card-2">♥</div>
        <div className="card card-3">♣</div>
        <div className="card card-4">♦</div>
      </div>
    </div>
  );

  const renderDiceAndRoulette = () => (
    <div className="casino-icon-decorative">
      <div className="dice-container">
        <div className="dice">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
        <div className="dice dice-2">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
      </div>
      <div className="roulette-wheel"></div>
    </div>
  );

  const renderSlotMachine = () => (
    <div className="casino-icon-decorative">
      <div className="slot-machine">
        <div className="slot-reel">7</div>
        <div className="slot-reel">7</div>
        <div className="slot-reel">7</div>
      </div>
      <div className="crown-icon">👑</div>
    </div>
  );

  const renderChipsOnly = () => (
    <div className="casino-icon-decorative">
      <div className="casino-chips-stack">
        <div className="chip chip-blue"></div>
        <div className="chip chip-green"></div>
        <div className="chip chip-purple"></div>
      </div>
    </div>
  );

  const renderDiceOnly = () => (
    <div className="casino-icon-decorative">
      <div className="dice-container">
        <div className="dice">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
        <div className="dice dice-2">
          <div className="dot"></div>
        </div>
        <div className="dice">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
      </div>
    </div>
  );

  const renderCardsOnly = () => (
    <div className="casino-icon-decorative">
      <div className="casino-cards-large">
        <div className="card-large card-1">A♠</div>
        <div className="card-large card-2">K♥</div>
        <div className="card-large card-3">Q♣</div>
      </div>
    </div>
  );

  const renderRouletteOnly = () => (
    <div className="casino-icon-decorative">
      <div className="roulette-wheel-large"></div>
      <div className="roulette-ball"></div>
    </div>
  );

  const renderPokerChips = () => (
    <div className="casino-icon-decorative">
      <div className="poker-chips-circle">
        <div className="chip chip-gold"></div>
        <div className="chip chip-red"></div>
        <div className="chip chip-black"></div>
        <div className="chip chip-blue"></div>
        <div className="chip chip-green"></div>
      </div>
      <div className="poker-icon">🃏</div>
    </div>
  );

  return (
    <div className="casino-card">
      {/* Icono decorativo de casino */}
      {getCasinoIcon()}

      {/* Nombre del casino */}
      <h3 className="casino-card-title">
        {name}
      </h3>
      
      {/* Ciudad con icono */}
      <p className="casino-card-city">
        <svg className="location-pin" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        {city}
      </p>

      {/* Descripción */}
      <p className="casino-card-description">
        {description}
      </p>

      {/* Botones de acción */}
      <div className="casino-card-actions">
        <button 
          className="casino-card-button"
          onClick={() => navigate(`/casinos/${id}/machines`)}
        >
          Ver Juegos
        </button>
        {onEdit && (
          <button 
            className="casino-card-edit-btn"
            onClick={() => onEdit(casino)}
            title="Editar casino"
          >
            ✏️
          </button>
        )}
      </div>
    </div>
  );
}