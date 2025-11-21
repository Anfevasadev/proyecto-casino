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

/**
 * Este componente representa una única tarjeta de casino.
 *
 * Props:
 * @param {object} casino - Objeto con los detalles del casino.
 * @param {string} casino.id - ID único del casino.
 * @param {string} casino.name - Nombre del casino.
 * @param {string} casino.city - Ciudad donde se encuentra.
 * @param {string} casino.description - Descripción corta.
 */
export default function CasinoCard({ casino = {} }) { // FIX: Se añade = {} para evitar el TypeError si casino es undefined
  const { name, city, description } = casino;

  // Si el componente se renderiza sin datos esenciales, podemos optar por no mostrar nada.
  // if (!name) return null; 
    
  return (
    // Estilo de tarjeta con fondo Rojo Oscuro (bg-red-950) y borde Oro (border-yellow-500)
    <div 
      className="bg-[#1a0000] border-2 border-[#d4af37] rounded-xl shadow-lg 
                 p-6 transform transition-transform duration-300 hover:scale-[1.03] 
                 hover:shadow-[0_0_20px_rgba(244,208,63,0.7)] text-white"
    >
      {/* Encabezado con el nombre del casino en color Oro */}
      <h3 className="text-2xl font-bold mb-2 text-[#f4d03f]">
        {name}
      </h3>
      
      {/* Ciudad/Ubicación en color Plata */}
      <p className="text-[#c0c0c0] text-sm mb-4">
        <svg className="w-4 h-4 inline mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z"></path>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
        {city}
      </p>

      {/* Descripción corta del casino */}
      <p className="text-gray-300 mb-6 italic">
        {description}
      </p>

      {/* Botón de acción principal con estilo de Oro y fondo Rojo Oscuro */}
      <button 
        className="w-full bg-[#d4af37] text-black font-semibold py-2 rounded-lg 
                   hover:bg-[#f4d03f] transition duration-200"
      >
        Ver Juegos
      </button>
    </div>
  );
}