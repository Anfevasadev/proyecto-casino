<!--
README.md
Función:
  Documento de bienvenida y guía rápida del proyecto.
  Aquí cualquier integrante entiende el "qué", "cómo correr" y "dónde tocar".

Qué va aquí:
  - Descripción corta del proyecto.
  - Requisitos (Python, dependencias).
  - Cómo instalar y ejecutar (API FastAPI).
  - Cómo está organizada la estructura.
  - Notas sobre la "BD" en CSV (carpeta data/).
  - Reglas livianas de colaboración (ramas, PRs).
  - Enlaces útiles (endpoints base).
-->

# Cuadre Casino — Proyecto Académico (Back en Python + FastAPI)

## 1) ¿Qué es esto?
Aplicación para gestionar **máquinas de casino**, registrar **contadores** (IN, OUT, JACKPOT, BILLETERO) y calcular **cuadres** por máquina y por lugar (casino).  
**Base de datos**: archivos **CSV** en `data/` (se usan como fuente de verdad).

## 2) Requisitos básicos
- Python 3.10+ (recomendado)
- `pip` para instalar dependencias

## 3) Instalación
```bash
# (opcional) crear entorno virtual
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# instalar dependencias
pip install -r requirements.txt

# generar CSVs (si hace falta)
python init_csvs.py
```

## 4) Ejecutar la API

```bash
uvicorn back.main:app --reload
```

* Healthcheck: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
* API v1: [http://127.0.0.1:8000/api/v1](http://127.0.0.1:8000/api/v1)

> **Hora local**: las fechas/horas se manejan en formato `YYYY-MM-DD HH:MM:SS` en **hora local**.

## 5) Estructura (resumen)

```
.
├─ front/                 # (pendiente definir framework)
├─ back/
│  ├─ api/               # Rutas FastAPI (capa HTTP)
│  ├─ domain/            # Reglas de negocio (funciones puras)
│  ├─ storage/           # Lectura/escritura CSV (pandas)
│  ├─ models/            # Esquemas Pydantic (request/response)
│  ├─ core/              # Config mínima (paths, time fmt)
│  └─ tests/             # Pruebas básicas
├─ data/                 # CSV = "BD" del proyecto
├─ .gitignore
├─ README.md
├─ requirements.txt
└─ init_csvs.py
```

## 6) CSV como BD (carpeta `data/`)

* Los **CSV** son nuestros datos persistentes (no usar DB tradicional).
* **No** se versionan archivos temporales; **sí** se versionan los CSV oficiales.
* Archivos clave: `users.csv`, `places.csv`, `machines.csv`, `counters.csv`, `machine_balances.csv`, `casino_balances.csv`, `logs.csv`.

## 7) Flujo de trabajo (light)

* Ramas principales: `main` y `desarrollo`.
* Cambios entran por **Pull Request** hacia `desarrollo` o `main`.
* Cada PR requiere **2 aprobaciones** (regla de protección activada).

## 8) Pruebas (muy básico por ahora)

Ejecuta pruebas cuando existan:

```bash
pytest
```

## 9) Notas para el equipo

* Si no sabes dónde poner algo: **API** (rutas), **domain** (reglas/operaciones), **storage** (CSV/pandas).
* Mantén funciones pequeñas y comentadas.
* Si un archivo te abruma, divídelo (pero evita sobre-arquitectura).


## LOGIN

El proceso de autenticación o login se realiza mediante el siguiente endpoint:

### POST /api/v1/login

Este endpoint recibe las credenciales o datos del usuario y retorna un token o la información básica si son válidas y el usuario está activo.

| Campo | Tipo | Descripción |
| :---: | :---: | :--- |
| `username` | `str` | Nombre de usuario. |
| `password` | `str` | Contraseña del usuario. |

Respuestas de Error:

* **401 Unauthorized:** Credenciales inválidas.
* **403 Forbidden:** Usuario encontrado, pero está inactivo.

---

## GESTIÓN DE MÁQUINAS (CRUD)

### POST /api/v1/machines (Crear Máquina)

Este endpoint crea una máquina validando reglas de negocio complejas.

| Validación de Negocio | Respuesta de Error |
| :---: | :---: |
| El `code` es único. | **409 Conflict** |
| `place_id` existe. | **404 Not Found** |
| `place_id` está activo. | **403 Forbidden** |

### GET /api/v1/machines (Listar Máquinas)

Permite listar máquinas con filtros y paginación.

| Query Param | Tipo | Propósito |
| :---: | :---: | :--- |
| `place_id` | `int` | Filtra por el lugar. |
| `active` | `bool` | Si es `True`, solo devuelve máquinas activas. |
| `sort_by` | `str` | Campo de ordenamiento (`id` o `code`). |

### GET /api/v1/machines/{id} (Obtener Máquina)

Obtiene una máquina por ID o lanza **404 Not Found** si no existe o está desactivada.

### PUT /api/v1/machines/{id} (Actualizar Máquina)

Actualiza los campos suministrados. Valida unicidad de `code` y Place activo si estos campos son modificados.

### DELETE /api/v1/machines/{id} (Borrado Lógico)

* **Acción:** Marca la máquina como inactiva (`is_active=false`).
* **Respuesta:** `{"deleted": true, "id": <id>}` si es exitoso.

---