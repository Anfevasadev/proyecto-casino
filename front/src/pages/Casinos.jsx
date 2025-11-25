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
import CreateCasinoForm from "../components/CreateCasinoForm";
import EditCasinoForm from "../components/EditCasinoForm";
import "../index.css";

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
  const [allCasinos, setAllCasinos] = useState([...MOCK_CASINOS]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingCasino, setEditingCasino] = useState(null);

  // Cargar casinos desde localStorage al iniciar
  useEffect(() => {
    const storedCasinos = localStorage.getItem('allCasinos');
    if (storedCasinos) {
      try {
        const parsed = JSON.parse(storedCasinos);
        setAllCasinos(parsed);
      } catch (e) {
        console.error('Error loading casinos from localStorage:', e);
        setAllCasinos([...MOCK_CASINOS]);
      }
    } else {
      // Si no hay casinos guardados, guardar los mock iniciales
      localStorage.setItem('allCasinos', JSON.stringify(MOCK_CASINOS));
    }
  }, []);

  useEffect(() => {
    fetchCasinos();
  }, [allCasinos]);

  const fetchCasinos = async (name = "") => {
    setLoading(true);
    try {
      // Simulación de filtro:
      const filtered = allCasinos.filter((c) =>
        c.name.toLowerCase().includes(name.toLowerCase())
      );
      setCasinos(filtered);
    } catch (err) {
      alert("Error al obtener casinos");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (event) => {
    const value = event.target.value;
    setQuery(value);
    fetchCasinos(value);
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const handleCasinoCreated = (newCasino) => {
    setAllCasinos(prev => {
      const updated = [...prev, newCasino];
      localStorage.setItem('allCasinos', JSON.stringify(updated));
      return updated;
    });
    setShowCreateForm(false);
    alert(`¡Casino "${newCasino.name}" creado exitosamente!`);
  };

  const handleEditCasino = (casino) => {
    setEditingCasino(casino);
  };

  const handleCasinoUpdated = (updatedCasino) => {
    setAllCasinos(prev => {
      const updated = prev.map(casino => 
        casino.id === updatedCasino.id ? updatedCasino : casino
      );
      localStorage.setItem('allCasinos', JSON.stringify(updated));
      return updated;
    });
    setEditingCasino(null);
    alert(`¡Casino "${updatedCasino.name}" actualizado exitosamente!`);
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
          <a href="#" className="nav-link" onClick={(e) => { e.preventDefault(); window.location.href = '/profile' }}>
            Mi Perfil
          </a>
          <a href="#" className="nav-link">
            Cajero
          </a>
          <button onClick={handleLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </nav>
      </header>
      <main className="casino-main">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
          <h1 className="section-title" style={{ 
            fontSize: '2em', 
            color: '#fff',
            borderBottom: 'none',
            margin: 0
          }}>
            Encuentra tu Casino Ideal
          </h1>
          <button 
            onClick={() => setShowCreateForm(true)}
            className="create-casino-btn"
          >
            + Crear Casino
          </button>
        </div>

        {/* Campo de búsqueda con estilos de casino */}
        <div className="max-w-xl mx-auto mb-10">
          <input
            type="text"
            placeholder="Buscar por nombre (ej: Gold)"
            value={query}
            onChange={handleSearch}
            style={{
              width: '100%',
              padding: '12px 20px',
              backgroundColor: 'rgba(0, 0, 0, 0.6)',
              border: '2px solid #d4af37',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '1em',
              outline: 'none'
            }}
            onFocus={(e) => e.target.style.borderColor = '#f4d03f'}
            onBlur={(e) => e.target.style.borderColor = '#d4af37'}
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
            <CasinoCard 
              key={casino.id} 
              casino={casino}
              onEdit={handleEditCasino}
            />
          ))}
        </div>
      </main>

      {/* Modal para crear casino */}
      {showCreateForm && (
        <CreateCasinoForm 
          onCasinoCreated={handleCasinoCreated}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {/* Modal para editar casino */}
      {editingCasino && (
        <EditCasinoForm 
          casino={editingCasino}
          onCasinoUpdated={handleCasinoUpdated}
          onCancel={() => setEditingCasino(null)}
        />
      )}
    </div>
  );
}