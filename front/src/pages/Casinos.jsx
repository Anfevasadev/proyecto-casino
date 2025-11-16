/*
  Esta página muestra la lista de casinos y permite al usuario buscar por nombre.

  Pasos a implementar:
     1. Importar los hooks de React useState y useEffect.
     2. Importar axios para realizar solicitudes HTTP.
     3. Importar el componente CasinoCard.
     4. Crear variables de estado:
         - casinos: un arreglo para almacenar la lista de casinos obtenida del backend.
         - search: una cadena para mantener la consulta de búsqueda actual.
     5. Usar useEffect para obtener la lista de casinos del backend cuando el
         componente se monte. Enviar una petición GET a '/api/v1/casinos' usando axios.
         Almacenar los resultados en el estado 'casinos'. Manejar errores registrándolos
         o mostrando un mensaje.
     6. Crear una lista filtrada de casinos basada en la consulta de búsqueda. Por ejemplo,
         filtrar comprobando si casino.name.toLowerCase().includes(search.toLowerCase()).
     7. Renderizar un campo de entrada ligado al estado 'search' que se actualice
         mientras el usuario escribe. Debajo del input, mapear la lista filtrada de casinos y
         renderizar un <CasinoCard> por cada uno.
     8. Estilizar la página usando clases de Tailwind CSS para el layout y los espaciados.

  Recuerda: esta página no debe contener la implementación real aquí; deja
  solo estos comentarios como guía para el desarrollo futuro.
*/

// TODO: Implementar la página Casinos según las instrucciones anteriores.

import { useState, useEffect } from "react";
import axios from "axios";
import CasinoCard from "../components/CasinoCard";
import "../index.css"; // Importa los estilos de casino

/*
 * Página de lista de casinos. Al montarse el componente, ejecuta
 * ``useEffect`` para obtener la lista completa de casinos.
 * Incluye un campo de búsqueda para filtrar y utiliza las clases de
 * layout definidas en index.css.
 */

// Datos de simulación (mientras el backend no está disponible)
const MOCK_CASINOS = [
  {
    id: 1,
    name: "Golden Ace Palace",
    city: "Las Vegas",
    description: "Experimenta el lujo y el servicio 5 estrellas.",
  },
  {
    id: 2,
    name: "Red Dragon Resort",
    city: "Macau",
    description: "Grandes límites y emocionantes juegos de mesa.",
  },
  {
    id: 3,
    name: "Royal Fortune City",
    city: "Atlantic City",
    description: "Una amplia selección de slots y jackpots progresivos.",
  },
];

export default function CasinosPage() {
  const [query, setQuery] = useState("");
  const [casinos, setCasinos] = useState([]);
  const [loading, setLoading] = useState(true); // Carga inicial de casinos al montar el componente

  useEffect(() => {
    fetchCasinos();
  }, []); // Función para recuperar casinos desde el backend (o simulación)

  const fetchCasinos = async (name = "") => {
    setLoading(true);
    try {
      // --- SIMULACIÓN DEL BACKEND ---
      // Aquí iría el código real:
      // const params = name ? { name } : {}
      // const response = await axios.get('/api/v1/casinos', { params })
      // setCasinos(response.data)

      // Simulación de filtro:
      const filtered = MOCK_CASINOS.filter((c) =>
        c.name.toLowerCase().includes(name.toLowerCase())
      );
      setCasinos(filtered);
    } catch (err) {
      alert("Error al obtener casinos");
    } finally {
      setLoading(false);
    }
  }; // Actualiza el término de búsqueda y vuelve a consultar

  const handleSearch = (event) => {
    const value = event.target.value;
    setQuery(value);
    fetchCasinos(value);
  };

  // Renderizado del componente
  return (
    <div className="casino-layout">
      <header className="casino-header">
        <div className="logo-section">
          <span className="header-icon">👑</span>
          <h2>Royal Fortune</h2>
        </div>
        <nav className="casino-nav">
          <a href="#" className="nav-link">
            Mi Perfil
          </a>
          <a href="#" className="nav-link">
            Cajero
          </a>
          <a href="/login" className="logout-btn">
            Cerrar Sesión
          </a>
        </nav>
      </header>
      <main className="casino-main">
        <h1 className="section-title">Encuentra tu Casino Ideal</h1>

        {/* Campo de búsqueda con estilos de casino */}
        <div className="max-w-xl mx-auto mb-10">
          <input
            type="text"
            placeholder="Buscar por nombre (ej: Golden Ace)"
            value={query}
            onChange={handleSearch}
            // Usamos las clases de input del formulario de Login para mantener el estilo
            className="login-form-input w-full p-3 border-2 border-yellow-700 rounded-lg 
                               bg-gray-900 text-white focus:outline-none focus:border-yellow-500"
          />
        </div>

        {loading && (
          <p className="text-center text-silver">Cargando casinos...</p>
        )}

        {!loading && casinos.length === 0 && (
          <p className="text-center text-silver">No se encontraron casinos.</p>
        )}

        {/* SECCIÓN DESCOMENTADA Y ESTILADA: Lista de casinos */}
        <div className="grid-container">
          {casinos.map((casino) => (
            <CasinoCard key={casino.id} casino={casino} />
          ))}
        </div>
      </main>
         {" "}
    </div>
  );
}
