# Configuración de Infraestructura (Backend)

Este documento describe la infraestructura necesaria para ejecutar el backend del proyecto casino, incluyendo dependencias, estructura de archivos, configuración local y propuesta de variables de entorno.

---

# 1. Entorno de Ejecución

El sistema está diseñado para ejecutarse **localmente**, sin despliegue en la nube por el momento.

### Requisitos principales:
- Python 3.10+
- Uvicorn (servidor ASGI)
- FastAPI
- Librerías del archivo `requirements.txt`
- CSV como almacenamiento persistente

El backend no depende de una base de datos relacional ni NoSQL; toda la persistencia se maneja mediante archivos `.csv`.

---

# 2. Estructura de Carpetas (Backend)

```markdown
back/
├── api/ # Endpoints y routers
│ ├── v1/
│ └── dependencies.py
├── core/ # Configuración central
├── domain/ # Casos de uso y lógica de negocio
├── infrastructure/ # Repositorios, servicios y persistencia
├── models/ # Modelos Pydantic y entidades
├── static/ # CSV de ejemplo / archivos del sistema
├── storage/ # CSV donde se guarda la información real
├── utils/ # Funciones auxiliares
├── main.py # Punto de entrada de la API
└── ...
```
---

# 3. Requerimientos Técnicos del Sistema

### Procesador:
Cualquier CPU moderno (Intel/AMD)  
### Memoria:
512 MB mínimo  
### Almacenamiento:
50 MB libres para CSV y logs  
### Sistema Operativo:
- Windows 10/11  
- Linux (cualquier distro reciente)  
- macOS (opcional)

### Lenguaje:
Python 3.10+  

### Servidor:
Uvicorn (ASGI)

---

# 4. Dependencias del Proyecto

Se instalan automáticamente con:

'pip install -r requirements.txt'

Dependencias principales:

- fastapi
- uvicorn
- python-multipart
- pydantic
- python-dotenv (opcional)
- pandas 
- rich (logs)
- datetime / pathlib / csv (estándar)

---

# 5. Configuración y Ejecución Local

### 1) Crear entorno virtual (opcional)

`python -m venv .venv`
`source .venv/bin/activate # En Windows: .venv\Scripts\activate`

### 2) Instalar dependencias

`pip install --upgrade pip`
`pip install -r requirements.txt`

### 3) Generar CSV iniciales (opcional)

`python init_csvs.py`

### 4) Ejecutar el backend

`uvicorn back.main:app --reload`

La API se ejecutará en:

http://localhost:8000

Y la documentación automática estará disponible en:

http://localhost:8000/docs
http://localhost:8000/redoc

---

# 6. Uso de CSV como Base de Datos

El sistema utiliza archivos CSV dentro de la carpeta `/data` como almacenamiento.

Ventajas:
- Simplicidad
- No se requiere servidor adicional
- Fácil portabilidad

Limitaciones:
- No apto para alta concurrencia
- No existen transacciones reales
- Riesgo de corrupción del archivo ante cortes inesperados

Estrategias implementadas:
- Bloqueos lógicos (`locked`)
- Timestamps
- Registros de auditoría (logs.csv)

---

# 7. Flujo de Inicialización del Sistema

Cargar variables de entorno (si existen)

Validar existencia de CSV en storage/

Cargar repositorios de infraestructura

Inicializar servicios de dominio

Montar routers FastAPI

Exponer API vía Uvicorn

# 8. Consideraciones de Seguridad

CSV protegidos mediante permisos del sistema operativo

Logs de auditoría por cada modificación relevante

Control de roles en endpoints (admin, user)

Hash de contraseñas (no texto plano)

Tokens de acceso para cada usuario autenticado

# 9. Estado Actual del Entorno

Actualmente implementado:

- Ejecución local
- Persistencia por CSV
- API modular en FastAPI
- Sistema de logs
- Validación de usuarios y roles
- Control de inactivaciones
- Módulo de balances y contadores
- Manejo de máquinas y lugares

Futuras mejoras:

- Migrar a base de datos SQL
- Dockerización
- Variables de entorno completas
- Despliegue a nube (Railway/Render/VPS)

