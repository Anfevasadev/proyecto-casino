#  DOCUMENTACIÓN DEL FRONTEND - CASINO

## Contexto Rápido

Esta es la **documentación del frontend** del proyecto Cuadre Casino. El frontend es una aplicación React moderna que actúa como cliente para consumir la API del backend. 

### Visión General

- **Tecnologías**: React 18.2.0, Vite, React Router, Axios, TailwindCSS
- **Tipo**: Single Page Application (SPA) con navegación sin recargas
- **Propósito**: Gestionar usuarios, casinos, máquinas de juego y consultar datos
- **Arquitectura**: Componentes reutilizables, cliente HTTP centralizado, estado local con hooks

---

**Proyecto:** Cuadre Casino  
**Módulo:** Frontend (React + Vite)  
**Versión:** 0.0.1  
**Fecha:** 26 de Noviembre, 2025

---

##  TABLA DE CONTENIDOS

1. [Stack Tecnológico](#1-stack-tecnológico)
8. [Estilos y TailwindCSS](#8-estilos-y-tailwindcss)
10. [Guía de Uso](#10-guía-de-uso)
### Dependencias Principales
| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| **React DOM** | 18.2.0 | Renderizado de componentes en el DOM |
| **React Router** | 6.3.0 | Enrutamiento de SPA (Single Page App) |
| **Vite** | 4.0.0 | Build tool ultra-rápido con HMR |
| **Axios** | 1.4.0 | Cliente HTTP para consumir APIs REST |
| **TailwindCSS** | 3.2.0 | Framework CSS utility-first |
| **PostCSS** | 8.4.14 | Procesador CSS (necesario para Tailwind) |
| **Autoprefixer** | 10.4.2 | Añade prefijos CSS automáticamente |
- `postcss@8.4.14`: Procesador de estilos
- `autoprefixer@10.4.2`: Compatibilidad entre navegadores

---

## 2. Estructura del Proyecto

```
front/
├── 📄 postcss.config.js       ← Configuración de PostCSS
│
│   ├── 📄 index.css           ← Estilos globales
│   │
│   │   └── 📄 client.js       ← Instancia Axios centralizada
│   │
│   ├── components/            ← Componentes reutilizables
│   │   ├── 📄 CasinoCard.jsx
│   │   ├── 📄 MachineCard.jsx
│   │   └── 📄 EditProfileForm.jsx
│       ├── 📄 CasinoMachines.jsx
│       └── 📄 Profile.jsx

### Descripción de Directorios
| `src/index.css` | Estilos globales y configuración Tailwind |

---

## 3. Configuración de Build

import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
-  Proxy de desarrollo: `/api` → `http://localhost:8000`
-  HMR (Hot Module Replacement) habilitado por defecto
-  Desarrollo rápido sin bundle inicial

{
  "scripts": {
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

- **Content scanning:** Analiza archivos `.jsx` para generar CSS
- **Theme:** Usa valores por defecto de Tailwind
- **No hay plugins** instalados actualmente

---

### 4. Cliente API

### 4.1 src/api/client.js

El cliente Axios se centraliza en `src/api/client.js`. Actualmente el repositorio guarda una URL base (usada en desarrollo remoto), pero lo recomendable es usar una variable de entorno para facilitar el desarrollo local y despliegues.

Recomendación de configuración (no se hace modificación automática sobre el código del frontend en este cambio; esta documentación indica cómo configurar el proyecto):

- Usar la variable de entorno Vite `VITE_API_BASE_URL` para definir la URL del backend en desarrollo/producción.

Ejemplo de `src/api/client.js` recomendado:

```javascript
import axios from 'axios';

const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: base,
  timeout: 8000,
  headers: { 'Content-Type': 'application/json' }
});

client.interceptors.response.use(
  response => response,
  error => {
    const detail = error?.response?.data?.detail;
    if (detail) error.message = Array.isArray(detail) ? detail.join(', ') : detail;
    return Promise.reject(error);
  }
);

export default client;
```
  headers: {
    'Content-Type': 'application/json'
  (error) => {
    const detail = error?.response?.data?.detail;
    if (detail) {
```
### 4.2 Características

| Feature | Descripción |
|---------|------------|
| **Base URL** | Se recomienda apuntar a la API v1 del backend y establecerla mediante `VITE_API_BASE_URL` |
| **Timeout** | 8 segundos máximo por request |
| **Headers** | JSON por defecto |
| **Interceptor** | Extrae mensajes de error del backend |

### 4.3 Uso en Componentes

```javascript
import client from '../api/client';

// GET
const response = await client.get('/places/casino', { 
  params: { only_active: true } 

// POST
await client.post('/users', {
  username: 'user123',
  password: 'pass123',
  role: 'player'
});

// PUT
await client.put(`/places/${id}`, updatedData);

// DELETE
await client.delete(`/machines/${id}`);
```

---

## 5. Sistema de Rutas

### 5.1 React Router Configuration

**src/App.jsx** define todas las rutas de la aplicación:

```javascript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/Login'
import CasinosPage from './pages/Casinos'
import CasinoMachinesPage from './pages/CasinoMachines'
import ProfilePage from './pages/Profile'

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/casinos" element={<CasinosPage />} />
        <Route path="/casinos/:casinoId/machines" element={<CasinoMachinesPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </Router>
  )
}
```

### 5.2 Tabla de Rutas

| Ruta | Componente | Descripción | Parámetros |
|------|-----------|-------------|-----------|
| `/` | `Navigate` | Redirige a `/login` | - |
| `/login` | `Login` | Autenticación y registro de usuarios | - |
| `/casinos` | `Casinos` | Listado de casinos/lugares | - |
| `/casinos/:casinoId/machines` | `CasinoMachines` | Máquinas de un casino específico | `casinoId` (ID del casino) |
| `/profile` | `Profile` | Perfil del usuario autenticado | - |

### 5.3 Navegación entre Páginas

```javascript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();
navigate('/casinos');              // Navegar a ruta simple
navigate(`/casinos/${id}/machines`); // Navegar con parámetro
navigate(-1);                      // Volver atrás
```

---

## 6. Páginas Principales

### 6.1 Login.jsx (209 líneas)

**Propósito:** Autenticación y registro de usuarios

**Características:**
- Modo dinámico: login y registro
- Toggle entre formas con un botón
- Validación de campos requeridos
- Manejo de errores de conexión
- Limpieza de errores al escribir

**Estado Local:**
```javascript
const [isRegisterMode, setIsRegisterMode] = useState(false);
const [formData, setFormData] = useState({ 
  name: '', 
  username: '', 
  password: '' 
});
const [error, setError] = useState('');
```

**Endpoints utilizados:**
- `POST /users` - Crear nuevo usuario (registro)
- `POST /auth` o similar - Autenticar usuario (login, inferido)

**Lógica:**
1. Usuario completa formulario (login o registro)
2. Si es registro: valida campos, envía POST a `/users`
3. Si es login: envía credenciales al backend
4. En éxito: guarda sesión en `localStorage`
5. En error: muestra mensaje amigable

---

### 6.2 Casinos.jsx (177 líneas)

**Propósito:** Gestión de casinos/lugares

**Características:**
- Listado de casinos desde la API
- Buscador en tiempo real (filtrado en cliente)
- Crear nuevo casino (formulario modal)
- Editar casino existente (modal)
- Botón de logout

**Estado Local:**
```javascript
const [query, setQuery] = useState("");           // Término de búsqueda
const [casinos, setCasinos] = useState([]);       // Datos del API
const [loading, setLoading] = useState(true);     // Cargando
const [error, setError] = useState("");           // Errores
const [showCreateForm, setShowCreateForm] = useState(false); // Modal crear
const [editingCasino, setEditingCasino] = useState(null);   // Casino editando
```

**Endpoints:**
- `GET /places/casino?only_active=true` - Listar casinos activos

**Flujo:**
1. Al montar: `useEffect` llama a `fetchCasinos()`
2. Muestra estado de carga
3. Renderiza lista de tarjetas (`CasinoCard`)
4. Modal para crear/editar casinos
5. Búsqueda filtra localmente

---

### 6.3 CasinoMachines.jsx

**Propósito:** Listar máquinas de un casino específico

**Características:**
- Recibe `casinoId` por parámetro de ruta
- Listado de máquinas filtradas por casino
- Crear nueva máquina
- Editar máquina
- Botón de retorno

**Parámetros de Ruta:**
```javascript
import { useParams } from 'react-router-dom';
const { casinoId } = useParams();
```

**Endpoints:**
- `GET /machines?place_id={casinoId}` - Máquinas del casino

---

### 6.4 Profile.jsx

**Propósito:** Mostrar y editar perfil del usuario

**Características:**
- Información del usuario autenticado
- Formulario de edición de perfil
- Cambio de contraseña (opcional)
- Botón de logout

---

## 7. Componentes Reutilizables

### 7.1 CasinoCard.jsx

**Props:**
```javascript
<CasinoCard 
  casino={{ id: 1, name: "Casino Centro", address: "Calle 5" }}
  onEdit={(casino) => {}}
  onDelete={(id) => {}}
/>
```

**Características:**
- Muestra información del casino en tarjeta
- Botones de editar y eliminar
- Estilos con Tailwind

---

### 7.2 CreateCasinoForm.jsx

**Props:**
```javascript
<CreateCasinoForm 
  onSubmit={(formData) => {}}
  onCancel={() => {}}
/>
```

**Características:**
- Formulario para crear casino
- Validación de campos
- Submit con Axios
- Manejo de errores

---

### 7.3 EditCasinoForm.jsx

**Props:**
```javascript
<EditCasinoForm 
  casino={{ id: 1, name: "Casino Centro", address: "Calle 5" }}
  onSubmit={(updatedData) => {}}
  onCancel={() => {}}
/>
```

**Características:**
- Precarga datos del casino
- Permite edición
- PUT request al backend

---

### 7.4 CreateMachineForm.jsx

**Props:**
```javascript
<CreateMachineForm 
  casinoId={1}
  onSubmit={(machineData) => {}}
  onCancel={() => {}}
/>
```

**Características:**
- Formulario para crear máquina
- Validación de denominación
- POST a `/machines`

---

### 7.5 MachineCard.jsx

**Props:**
```javascript
<MachineCard 
  machine={{ 
    id: 1, 
    code: "M001", 
    denomination_value: 100,
    participation_rate: 85
  }}
  onEdit={(machine) => {}}
  onDelete={(id) => {}}
/>
```

**Características:**
- Muestra máquina en tarjeta
- Botones de acción
- Información de participación

---

### 7.6 EditProfileForm.jsx

**Props:**
```javascript
<EditProfileForm 
  user={{ id: 1, username: "user123", name: "Juan" }}
  onSubmit={(userData) => {}}
  onCancel={() => {}}
/>
```

**Características:**
- Edita datos de usuario
- Cambio de contraseña opcional
- PUT a `/users/{id}`

---

## 8. Estilos y TailwindCSS

### 8.1 Configuración

**tailwind.config.js:**
- Escanea todos los archivos `.jsx` en `src/`
- Genera clases CSS dinámicamente
- Usa tema por defecto de Tailwind

### 8.2 Estilos Globales (index.css)

Contiene:
- Importación de directivas Tailwind
- Estilos base del proyecto
- Clases personalizadas si las hay

### 8.3 Clases Tailwind Comunes

| Clase | Uso |
|-------|-----|
| `flex`, `grid` | Layouts |
| `p-4`, `m-2` | Espaciado |
| `bg-white`, `bg-blue-500` | Colores de fondo |
| `text-gray-700`, `text-lg` | Tipografía |
| `border`, `rounded-lg` | Bordes |
| `shadow-md` | Sombras |
| `hover:bg-gray-100` | Estados |
| `absolute`, `relative` | Posicionamiento |

### 8.4 Ventajas de Tailwind

CSS más pequeño (solo clases usadas)  
 Desarrollo rápido sin escribir CSS
 Consistencia de estilos  
 Responsive-first design  
 Dark mode soportado (configuración futura)

---

## 9. Arquitectura de Datos

### 9.1 Flujo de Información

```
┌─────────────────────────────┐
│  Usuario interactúa         │
│  (clicks, formularios)      │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  React Component            │
│  - useState (estado local)  │
│  - handleChange             │
│  - handleSubmit             │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Axios Client               │
│  - client.post()            │
│  - client.get()             │
│  - client.put()             │
│  - client.delete()          │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Backend API (FastAPI)      │
│  - POST /users              │
│  - GET /places              │
│  - PUT /machines/{id}       │
│  - DELETE /casinos/{id}     │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Almacenamiento (CSV)       │
│  - users.csv                │
│  - places.csv               │
│  - machines.csv             │
└─────────────────────────────┘
```

### 9.2 Modelos de Datos

#### Casino/Place
```javascript
{
  id: number,
  name: string,
  address: string,
  is_active: boolean
}
```

#### Machine
```javascript
{
  id: number,
  code: string,
  denomination_value: number,
  place_id: number,
  participation_rate: number,
  is_active: boolean
}
```

#### User
```javascript
{
  id: number,
  username: string,
  password: string,
  name: string,
  role: string,
  is_active: boolean
}
```

---

## 10. Guía de Uso

### 10.1 Instalación

```bash
cd front/
npm install
```

### 10.2 Desarrollo Local

```bash
npm run dev
```

Accede a `http://localhost:5173`

**Nota:** El backend debe estar corriendo (por ejemplo en `http://localhost:8000`) cuando desarrolles localmente. Para evitar cambiar el cliente manualmente, configura `VITE_API_BASE_URL` en un archivo `.env` dentro de `front/` (ej. `.env.local`).

Ejemplo `.env.local` (en `front/`):

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

También se puede usar la proxy de Vite (`vite.config.js`) para redirigir `/api` a `http://localhost:8000` en desarrollo.

### 10.3 Compilar para Producción

```bash
npm run build
```

Genera carpeta `dist/` lista para deploy

### 10.4 Estructura de Componentes

Nuevo componente:
```javascript
import React, { useState } from 'react';

export default function MiComponente({ prop1, prop2 }) {
  const [state, setState] = useState(null);

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      {/* JSX aquí */}
    </div>
  );
}
```

### 10.5 Mejores Prácticas

 Usar `const` y `arrow functions`  
 Componentes funcionales con hooks  
 Estado local con `useState`  
 Efectos con `useEffect` y dependencias  
 Nombres descriptivos en componentes y variables  
 Separar lógica en componentes reutilizables  
 Centralizar API calls en `client.js`  
 Manejo de errores en try/catch  
 Estilos con Tailwind, no CSS inline  

### 10.6 Troubleshooting

| Problema | Solución |
|----------|----------|
| Puerto 5173 en uso | Cambiar en `vite.config.js` o `npm run dev -- --port 3000` |
| Backend no responde | Verificar que `localhost:8000` está corriendo |
| Estilos no aplicados | Correr `npm run dev` para regenerar Tailwind CSS |
| Módulos no encontrados | Ejecutar `npm install` nuevamente |

---

##  Recursos Adicionales

- [React Documentation](https://react.dev)
- [Vite Guide](https://vitejs.dev)
- [React Router](https://reactrouter.com)
- [Axios Documentation](https://axios-http.com)
- [TailwindCSS](https://tailwindcss.com)

---

**Última actualización:** 26 de Noviembre, 2025  
**Autor:** Equipo de Desarrollo - Casino  
**Estado:** Activo y en mantenimiento
