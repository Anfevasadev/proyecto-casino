# Arquitectura general del sistema — Backend Proyecto Casino

Este documento describe la arquitectura general del backend del sistema de control de casinos. Incluye los componentes principales, la organización del proyecto, la comunicación interna, los procesos esenciales y un diagrama general de arquitectura.

---

## 1. Visión general

El backend del sistema está construido con **Python 3.10+** y **FastAPI** como framework principal para la creación de servicios REST.  
La persistencia se maneja mediante archivos **CSV**, los cuales funcionan como una base de datos ligera para almacenamiento estructurado.

La arquitectura se basa en tres capas principales:

1. **API** — Manejo de solicitudes HTTP, rutas y validación inicial.
2. **Lógica de negocio (Domain)** — Reglas del negocio, validaciones, cálculos y procesos.
3. **Persistencia (Storage + data (CSV))** — Lectura, escritura y gestión de datos en archivos CSV.

---

## 2. Estructura del proyecto

La carpeta `back/` contiene los siguientes módulos:

```markdown
back/
├── api/
│ ├── v1/
│ │ ├── auth.py
│ │ ├── users.py
│ │ ├── places.py
│ │ ├── machines.py
│ │ ├── counters.py
│ │ ├── balances.py
│ │ ├── health.py
│ │ └── init.py
│ └── init.py
│
├── core/
│ ├── config.py
│ ├── constants.py
│ ├── date_utils.py
│ └── init.py
│
├── domain/
│ ├── auth/
│ ├── balances/
│ ├── counters/
│ ├── logs/
│ ├── machines/
│ ├── places/
│ ├── users/
│ └── init.py
│
├── models/
│ ├── auth.py
│ ├── balances.py
│ ├── counters.py
│ ├── machines.py
│ ├── places.py
│ ├── users.py
│ └── init.py
│
├── storage/
│ ├── csv_manager.py
│ ├── file_paths.py
│ └── init.py
│
├── data/ (archivos CSV)
│
├── init_csvs.py
├── main.py
└── init.py
```

### Rol de cada módulo

| Módulo        | Descripción |
|---------------|-------------|
| **api/**      | Contiene los endpoints REST organizados por recursos. |
| **domain/**   | Implementa la lógica de negocio: validaciones, cálculos y reglas internas. |
| **models/**   | Esquemas de entrada y salida (Pydantic), usados para validar datos. |
| **storage/**  | Gestión de archivos CSV: lectura, escritura, manejo de paths. |
| **core/**     | Configuraciones globales, constantes, utilidades de fecha/hora. |
| **data/**     | “Base de datos” del sistema: archivos CSV generados por `init_csvs.py`. |

---

## 3. Endpoints principales

El router principal incluye los siguientes módulos:

| Recurso | Ruta | Descripción |
|--------|------|-------------|
| **Auth** | `/auth` | Login, manejo de credenciales. |
| **Users** | `/users` | CRUD de usuarios, activación, inactivación. |
| **Places** | `/places` | Crear, inactivar, activar, listar y editar casinos (lugares). |
| **Machines** | `/machines` | Registro, activación, inactivación, consulta de máquinas. |
| **Counters** | `/counters` | Manejo de contadores, historial y registros. |
| **Balances** | `/balances` | Registro de balances y cálculo de cuadres. |
| **Health** | `/health` | Endpoint para verificación del estado del sistema. |

---

## 4. Procesos principales del sistema

El backend implementa las siguientes funcionalidades:

### Usuarios
- Crear usuarios
- Actualizar usuarios
- Eliminar usuarios
- Activar / Inactivar usuarios
- Listar usuarios
- Manejo de roles (admin, operador, etc.)

### Autenticación
- Login con validación de credenciales
- Generación de tokens o respuestas autorizadas
- Registro en logs de los accesos

### Lugares (casinos)
- Crear lugar
- Editar lugar
- Eliminar lugar
- Activar / Inactivar lugar
- Listar lugares activos/inactivos

### Máquinas
- Registrar máquina
- Obtener máquinas por lugar
- Activar / Inactivar máquina
- Modificar datos
- Listar máquinas

### Contadores
- Registrar contadores
- Obtener historial
- Actualizar contadores
- Validaciones de integridad
- Manejo de logs

### Balances / Cuadres
- Registrar balance diario
- Cálculo automático del cuadre del día
- Comparación entre contador inicial / final
- Cálculo de faltantes o sobrantes
- Almacenamiento en CSV

### Sistema de logs
- Registro de eventos
- Auditoría de acciones clave
- Incidencias

---

## 5. Flujo general de una solicitud

A continuación se muestra cómo fluye una petición típica dentro del backend:

1. **Cliente** envía solicitud HTTP (ej. `/api/v1/login`)
2. **API** (FastAPI) recibe la solicitud y valida el esquema (Pydantic)
3. La solicitud se envía al componente correspondiente en **domain/**
4. La lógica de negocio procesa la acción:
   - Validaciones
   - Cálculos
   - Verificaciones de reglas del sistema
5. Si requiere persistencia:
   - Se lee/escribe el CSV correspondiente desde `storage/`
6. Se retorna una **respuesta JSON** al cliente

---

## 6. Ejecución del sistema

### Instalación

# crear entorno virtual
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# instalar dependencias
pip install -r requirements.txt

# actualizar pip (opcional)
pip install --upgrade pip

# generar CSVs iniciales
python init_csvs.py

# Ejecutar API
uvicorn back.main:app --reload


## 7. Diagrama general de arquitectura
```pgsql
                 ┌────────────────────────┐
                 │        Cliente         │
                 │(Frontend, Postman, etc)│
                 └─────────────┬──────────┘
                               │ HTTP Requests
                               ▼
                  ┌─────────────────────────┐
                  │          API            │
                  │      (FastAPI)          │
                  └───────┬─────────────────┘
                          │ Llama funciones del dominio
                          ▼
        ┌──────────────────────────────────────────────┐
        │                Lógica de Negocio             │
        │                  (domain/)                   │
        │  Validaciones, cálculos, reglas del sistema  │
        └──────────────┬───────────────────────────────┘
                       │ Opera sobre datos
                       ▼
         ┌──────────────────────────────────────────┐
         │               Persistencia               │
         │        (storage/ + archivos CSV)         │
         └────────────┬─────────────────────────────┘
                      │ Lectura/Escritura
                      ▼
            ┌──────────────────────────┐
            │         data/            │
            │   CSV como BD liviana    │
            └──────────────────────────┘
```
## 8. Descripción del diagrama

El sistema sigue un enfoque de arquitectura en capas:

# 1) Capa Cliente

Consume los servicios del backend usando HTTP.

# 2) Capa API

Define endpoints, controla acceso y realiza validaciones iniciales.

# 3) Capa Domain

Ejecuta la lógica del negocio:

Validaciones

Reglas internas

Cálculos de cuadres

Procesamiento de balances

Manejo de roles/usuarios

# 4) Capa Storage

Administra la lectura/escritura de datos en archivos CSV.

# 5) Capa de Datos

Archivos CSV que funcionan como la base de datos del sistema.

## 9. Conclusión

La arquitectura está diseñada para ser modular, fácil de mantener y escalable.
La separación en capas permite modificar la lógica, la API o la persistencia sin afectar las demás partes del sistema.

