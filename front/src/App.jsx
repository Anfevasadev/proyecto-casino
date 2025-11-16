/*
  Este archivo define el componente raíz de la aplicación React. Debe configurar
  React Router para la navegación entre páginas. Importar BrowserRouter, Routes,
  Route y Navigate de react-router-dom. Definir tres rutas:
    - "/" que redirige a "/login".
    - "/login" que renderiza el componente de la página Login.
    - "/casinos" que renderiza el componente de la página Casinos.

  Debe importar los componentes Login y Casinos de la carpeta pages.
  Usar <BrowserRouter> para envolver <Routes>. Usar <Navigate> con la propiedad 'replace'
  para redirigir de "/" a "/login". Exportar este componente por defecto.

  La implementación real se omite intencionalmente aquí. Estos comentarios
  sirven como guía para que futuros desarrolladores reconstruyan la lógica de enrutamiento.
*/

// TODO: Implementar el componente App según las instrucciones anteriores.
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

// Importar componentes de página. Estos representan pantallas separadas en la aplicación.

/*
  Componente de nivel superior responsable de definir el enrutamiento
  de la aplicación. Usamos ``react-router-dom`` para mapear rutas de URL a
  componentes React. ``/login`` renderiza la página de login/registro y
  ``/casinos`` renderiza la lista de casinos. Navegar a la raíz
  redirige a ``/login``.
*/

import LoginPage from './pages/Login'
import CasinosPage from './pages/Casinos'

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Redirigir la ruta raíz a /login */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        {/* Página de login y registro */}
        <Route path="/login" element={<LoginPage />} />
        {/* Lista de casinos; ahora visible */}
        <Route path="/casinos" element={<CasinosPage />} />
      </Routes>
    </Router>
  )
}