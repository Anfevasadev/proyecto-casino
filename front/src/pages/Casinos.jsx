import { useState, useEffect, useCallback } from "react";
import CasinoCard from "../components/CasinoCard";
import CreateCasinoForm from "../components/CreateCasinoForm";
import EditCasinoForm from "../components/EditCasinoForm";
import client from "../api/client";
import "../index.css"; // Se importan estilos globales

/*
 * Página de lista de casinos. Al montarse el componente, ejecuta
 * ``useEffect`` para obtener la lista completa de casinos.
 * Incluye un campo de búsqueda para filtrar y utiliza las clases de
 * layout definidas en index.css.
 */

export default function CasinosPage() {
  const [query, setQuery] = useState(""); // Texto del buscador
  const [casinos, setCasinos] = useState([]); // Lista remota de casinos
  const [loading, setLoading] = useState(true); // Estado de carga inicial
  const [error, setError] = useState(""); // Manejo de errores de API
  const [showCreateForm, setShowCreateForm] = useState(false); // Control modal de creación
  const [editingCasino, setEditingCasino] = useState(null); // Casino seleccionado para editar

  const fetchCasinos = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      // Petición GET al backend con filtro only_active
      const response = await client.get('/places/casino', { params: { only_active: true, offset: 0 } })
      const { data } = response;
      setCasinos(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message ?? "No fue posible obtener los casinos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCasinos(); // Se obtiene la lista al montar el componente
  }, []);

  const handleSearch = (event) => {
    setQuery(event.target.value); // Actualiza el término de búsqueda
  };

  const handleLogout = () => {
    localStorage.removeItem('user'); // Limpia sesión local
    window.location.href = '/login'; // Redirige al login
  };

  const handleCasinoCreated = async () => {
    setShowCreateForm(false);
    await fetchCasinos(); // Refresca lista tras crear
  };

  const handleEditCasino = (casino) => {
    setEditingCasino(casino); // Abre modal con datos del casino
  };

  const handleCasinoUpdated = async () => {
    setEditingCasino(null);
    await fetchCasinos(); // Refresca lista tras editar
  };

  const filteredCasinos = casinos.filter((casino) => {
    const term = query.trim().toLowerCase();
    if (!term) return true;

    const nombre = (casino?.nombre ?? '').toString().toLowerCase();
    const codigo = (casino?.codigo_casino ?? '').toString().toLowerCase();

    return nombre.includes(term) || codigo.includes(term);
  });

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
          <a href="/counters" className="nav-link">
            Contadores
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

        {error && (
          <p className="text-center text-red-400 mb-4">{error}</p>
        )}

        {loading && (
          <p className="text-center text-silver">Cargando casinos...</p>
        )}

        {!loading && filteredCasinos.length === 0 && (
          <p className="text-center text-silver">No se encontraron casinos.</p>
        )}

        {/* SECCIÓN DESCOMENTADA Y ESTILADA: Lista de casinos */}
        <div className="grid-container">
          {filteredCasinos.map((casino) => (
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