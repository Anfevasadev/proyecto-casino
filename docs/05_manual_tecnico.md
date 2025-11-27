
# Manual Técnico

La operación eficiente de máquinas de casino requiere un control riguroso de los datos generados por cada equipo, especialmente aquellos relacionados con sus contadores de juego (IN, OUT, JACKPOT y BILLETERO). En muchos entornos, estos procesos aún se realizan de manera manual o con herramientas poco integradas, lo que incrementa el riesgo de errores, dificulta la trazabilidad de la información y limita la capacidad de análisis estratégico.
En respuesta a estas necesidades, se desarrolla el Sistema de Gestión y Cuadre de Máquinas de Casino, una solución automatizada e integrada diseñada para centralizar el registro de contadores, calcular la utilidad individual por máquina y generar el cuadre general por casino de forma precisa, rápida y confiable. Este sistema permite administrar máquinas ubicadas en distintos lugares, optimizando los procesos operativos y reduciendo la carga administrativa asociada al manejo de datos.
Además de mejorar la exactitud del control financiero, el sistema facilita la toma de decisiones estratégicas mediante reportes organizados, históricos de operación y una estructura de datos confiable. Con ello, las organizaciones pueden gestionar sus recursos de forma más eficiente, identificar patrones de rendimiento y garantizar la transparencia en todas las operaciones relacionadas con la actividad de las máquinas de juego.


---

## Diagramas de flujo

#Diagramas que muestran el flujo de datos y las interacciones entre módulos (API → Domain → Repositorios → CSV/DB).

## 1. Flujo de Autenticación (Login)

El proceso de login valida credenciales, genera el token y retorna los datos del usuario autenticado.



             ┌──────────────────────┐
             │ Usuario envía login  │
             │ (username/password)  │
             └───────────┬──────────┘
                         ▼
                ┌─────────────────────┐
                │ Buscar usuario por  │
                │ username en Users   │
                └───────────┬─────────┘
                            ▼
                ┌─────────────────────┐
            ¿Usuario existe y está activo?
                └───────┬─────────┬───┘
                        │         │
                       Sí         No
                        │         │
                        │         ▼
                        │   ┌───────────────────────┐
                        │   │ Retornar error 401    │
                        │   └───────────────────────┘
                        ▼
     ┌──────────────────────────────┐
     │ Validar contraseña (hash)    │
     └──────────┬──────────┬────────┘
                │          │
               Sí          No
                │          │
                ▼          ▼
 ┌────────────────┐   ┌────────────────────┐
 │ Generar token  │   │ Retornar error 401 │
 └───────┬────────┘   └────────────────────┘
         ▼
┌───────────────────────────────┐
│ Retornar token y datos usuario│
└───────────────────────────────┘
```

---

## 2. Flujo de Creación de Usuario

         ┌────────────────────────┐
         │ Admin envía datos de   │
         │ creación de usuario    │
         └──────────┬─────────────┘
                    ▼
     ┌──────────────────────────┐
     │ Validar que username no  │
     │ exista previamente       │
     └──────────┬───────────────┘
                │
                ¿Existe?
             ┌───────────────────┐
             │                   │
             Sí                  No
             │                   │
             ▼                   ▼
┌────────────────┐ ┌─────────────────────┐
│ Retornar error │ │ Hash password       │
└────────────────┘ │ Guardar usuario     │
                   └─────────┬───────────┘
                                                         ▼
┌────────────────────────────────┐
│ Retornar usuario creado OK     │
└────────────────────────────────┘




# 3. Flujo de Creación de Casino (Place)

         ┌────────────────────────┐
         │ Admin envía datos de   │
         │ creación de casino     │
         └──────────┬─────────────┘
                    ▼
     ┌──────────────────────────┐
     │ Validar código de casino │
     │ no repetido              │
     └──────────┬───────────────┘
                │
                ¿Existe?
             ┌──────────────────────┐
             │                      │
             Sí                     No
             │                      │
             ▼                      ▼
┌────────────────┐ ┌───────────────────────┐
│ Retornar error │ │ Insertar registro en  │
└────────────────┘ │ places.csv / DB       │
                   └─────────┬─────────────┘
                             ▼
┌──────────────────────────────────────────┐
│ Retornar casino creado / datos completos │
└──────────────────────────────────────────┘
```

---

## 4. Flujo de Registro de Máquina

    ┌─────────────────────────────────┐
    │ Admin selecciona casino y envía │
    │ datos de máquina                │
    └─────────────────┬───────────────┘
                      ▼
                     ┌─────────────────────────────┐
                     │ Validar serial no repetido  │
                     └───────────┬─────────────────┘
                                 │
                             ¿Existe?
                        ┌─────────────────────┐
                        │                     │
                        Sí                    No
                        │                     │
                        ▼                     ▼
        ┌─────────────────┐ ┌──────────────────────┐
        │ Retornar error  │ │ Registrar máquina en │
        └─────────────────┘ │ machines.csv / DB    │
                            └────────────┬─────────┘
                                         ▼
                ┌────────────────────────────────────────┐
                │ Retornar datos completos de la máquina │
                └────────────────────────────────────────┘




# 5. Flujo de Registro de Contadores

         ┌──────────────────────────────────────────┐
         │ Usuario selecciona casino y máquina      │
         │ luego ingresa contadores (in/out/jp/etc) │
         └──────────────────┬───────────────────────┘
                            ▼
             ┌──────────────────────────────────────┐
             │ Verificar que la máquina esté activa │
             └──────────────────┬───────────────────┘
                                │
                             ¿Activa?
                         ┌────────────────────────┐
                         │                        │
                         No                       Sí
                         │                        │
                         ▼                        ▼
     ┌────────────────────────┐ ┌──────────────────────────┐
     │ Retornar error         │ │ Registrar contadores en  │
     └────────────────────────┘ │ counters.csv / DB        │
                                └──────────────┬───────────┘
                                               ▼
                                 ┌─────────────────────────────────────────────┐
                                 │ Registrar log de conteo (logs.csv)          │
                                 └───────────────────────┬─────────────────────┘
                                                         ▼
                                ┌──────────────────────────────────────────────┐
                                │ Retornar datos del contador registrado       │
                                └──────────────────────────────────────────────┘




## 6. Flujo de Generación de Balance por Máquina

            ┌───────────────────────────────────────┐
            │ Usuario solicita generar balance      │
            │ para una máquina                      │
            └───────────────────┬───────────────────┘
                                ▼
         ┌────────────────────────────────────────┐
         │ Obtener contadores del período         │
         └───────────────────┬────────────────────┘
                             ▼
            ┌───────────────────────────────────────┐
            │ Calcular totales (in/out/jp/bill/etc) │
            └───────────────────┬───────────────────┘
                                ▼
             ┌────────────────────────────────────┐
             │ Guardar máquina_balance en CSV/DB  │
             └───────────────────┬────────────────┘
                                 ▼
         ┌─────────────────────────────────────────┐
         │ Retornar balance final y utilidad       │
         └─────────────────────────────────────────┘


## 7. Flujo de Generación de Balance por Casino (Global)

    ┌─────────────────────────────────────────────────┐
    │ Usuario solicita generar balance global casino  │
    └─────────────────────────┬───────────────────────┘
                              ▼
     ┌─────────────────────────────────────────┐
     │ Reunir balances de todas las máquinas   │
     └──────────────┬──────────────────────────┘
                    ▼
 ┌────────────────────────────────────────────┐
 │ Sumar totales: in/out/jp/bill/utilidad     │
 └──────────────┬─────────────────────────────┘
                ▼
┌───────────────────────────────────────────────────┐
│ Guardar casino_balance en CSV/DB                  │
└──────────────────┬────────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────────┐
│ Retornar balance total del casino                 │
└───────────────────────────────────────────────────┘


## Modelos de base de datos

 - **Contexto:** El proyecto actualmente persiste en CSV; se describen aquí los modelos y sus campos principales.

- `users.csv`:
    - `id`, `username`, `password`, `role` ,`is_active`, `is_deleted`,`created_at`,`created_by`,`updated_at`,`updated_by`,`deleted_at`,`deleted_by` 

- `places.csv`:
    - `id`, `name`, `address`,`is_active`, `created_at`,`created_by`, `updated_at`, `updated_by`

- `machines.csv`:
    - `id`, `machine_id`, `denomination_value`, `place_id`, `participation_rate`, `is_active`,`created_at`,`created_by`,`updated_at`,`updated_by`

- `counters.csv`:
    - `id`, `machine_id`, `in_amount`, `out_amount`, `jackpot_amount`, `billetero_amount`,`created_at`,`created_by`,`created_by`,`updated_at`,`updated_by`

- `machine_balances.csv`:
    - `id`, `machine_id`, `period_start`, `period_end`, `in_total`, `out_total`,`jackpot_total`,`billetero_total`,`utilidad_total`,`generated_at`,`generated_by`

- `casino_balances.csv`:
    - `id`, `place_id`, `period_start`, `period_end`,`in_total`,`out_total`,`jackpot_total`,`billetero_total`,`utilidad_total`,`generated_at`,`generated_by`,`locked`

Para cada CSV incluye encabezado consistente y tipos de dato esperados. Mantener un `id` único en formato UUID o string seguro.

---

## Configuraciones de infraestructura

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

El backend no depende de una base de datos relacional ni SQL; toda la persistencia se maneja mediante archivos `.csv`.

---

# 2. Estructura de Carpetas 

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

## 1) Crear entorno virtual (opcional)

`python -m venv .venv`
`source .venv/bin/activate # En Windows: .venv\Scripts\activate`

## 2) Instalar dependencias

`pip install --upgrade pip`
`pip install -r requirements.txt`

## 3) Generar CSV iniciales (opcional)

`python init_csvs.py`

## 4) Ejecutar el backend

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

## Manual técnico: configuración del sistema y requerimientos técnicos

 - **Instalación básica (entorno virtual):**

     1. Crear entorno: `python -m venv .venv`
     2. Activar: `source .venv/bin/activate`
     3. Instalar dependencias: `pip install -r requirements.txt`

 - **Archivos de configuración:**
     - `back/core/settings.py`: configuración principal (puertos, paths)
     - Variables de entorno para endpoints y rutas de datos

 - **Ejecución local:** `uvicorn back.main:app --reload --port 8000`

 - **Requerimientos técnicos:**
     - Python 3.11+
     - Memoria: mínimo 1 GB para pruebas, 2+ GB recomendado en producción
     - Disco: espacio suficiente para CSV (depende del volumen de registros)

---

## Guía para la solución de problemas y mantenimiento

 - **Problemas comunes y pasos de diagnóstico:**
     - API no responde: comprobar `uvicorn` logs y `LOG_LEVEL`; verificar que `DATA_PATH` exista.
     - Error al leer CSV: validar encodings (UTF-8) y encabezados; revisar permisos de archivo.
     - Inconsistencias en balances: revisar logs en `logs.csv` y comparar timestamps.

 - **Mantenimiento periódico:**
     - Respaldos diarios/semanales de la carpeta `data/` o `back/storage/`.
     - Validación de integridad: scripts para comprobar IDs duplicados y formatos de fecha.
     - Compactación: archivar CSV antiguos mensualmente.

---

## Requerimientos mínimos de instalación

 - Sistema operativo: Linux (probado), macOS o Windows (con WSL)
 - Python 3.11+
 - `pip` actualizado
 - Espacio: 100 MB al inicio (más según datos)
 - Puerto libre: 8000 por defecto

---

## Librerías necesarias

 - Dependencias principales (ver `requirements.txt`):
     - `fastapi`
     - `uvicorn`
     - `pydantic`
     - `python-dotenv` (si se usa `.env`)
     - `pytest` (para tests)

 Incluir versiones concretas en `requirements.txt` para reproducibilidad.

---

## Usuario y contraseña por defecto

 - **Usuario por defecto:** user1
 - **Contraseña por defecto:** pass123


---

## Diagrama general de la arquitectura del sistema

                     ┌──────────────────────────────┐
                     │          USUARIO             │
                     │  (Operador / Admin / Viewer) │
                     └───────────────┬──────────────┘
                                     │
                                     ▼
                     ┌──────────────────────────────┐
                     │        FRONTEND WEB          │
                     │   (React / HTML / JS / UI)   │
                     └───────────────┬──────────────┘
                                     │ Peticiones HTTP (REST)
                                     ▼
          ┌────────────────────────────────────────────────────────┐
          │                       BACKEND API                      │
          │                 (Python – FastAPI/Flask)               │
          │                                                        │
          │  ┌─────────────────────────┬────────────────────────┐  │
          │  │  Módulo de Usuarios     │   Módulo de Casinos    │  │
          │  ├─────────────────────────┼────────────────────────┤  │
          │  │  Autenticación JWT      │   CRUD Lugares         │  │
          │  │  Roles y Permisos       │   Validación códigos   │  │
          │  └─────────────────────────┴────────────────────────┘  │
          │  ┌─────────────────────────┬────────────────────────┐  │
          │  │  Módulo de Máquinas     │ Módulo de Contadores   │  │
          │  │  Registro/validaciones  │ Registro IN/OUT/JP/BILL│  │
          │  │  Asignación por casino  │ Logs de capturas       │  │
          │  └─────────────────────────┴────────────────────────┘  │
          │  ┌──────────────────────────────────────────────────┐  │
          │  │       Módulo de Balances y Cálculos              │  │
          │  │       (Máquina / Casino General)                 │  │
          │  └──────────────────────────────────────────────────┘  │
          └───────────────┬────────────────────────────────────────┘
                          │ Lectura/Escritura
                          ▼
       ┌────────────────────────────────────────────────────────────┐
       │                   CAPA DE PERSISTENCIA                     │
       │             (CSV o Base de Datos Relacional)               │
       │                                                            │
       │ users.csv / places.csv / machines.csv / counters.csv       │
       │ balances_machines.csv / balances_casino.csv / logs.csv     │
       └────────────────────────────────────────────────────────────┘

 ```

---