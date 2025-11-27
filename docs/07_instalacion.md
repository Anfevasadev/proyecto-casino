# Requerimientos e Instalación del Sistema

Este documento describe los requerimientos mínimos, las dependencias del backend, el proceso de instalación, los archivos necesarios y la configuración básica para ejecutar el sistema en un entorno local.

---

# 1. Requerimientos Mínimos del Sistema

## 1.1 Hardware
- **CPU:** 2 núcleos (mínimo)
- **RAM:** 4 GB (mínimo), recomendado 8 GB
- **Almacenamiento:** 500 MB libres para proyecto + CSVs

## 1.2 Software
- **Python 3.10+**
- **Pip 22+**
- **Git**
- **Sistema Operativo:**  
  - Windows 10+  
  - Ubuntu 20+  
  - macOS 12+

---

# 2. Dependencias Principales (Backend)

El backend usa FastAPI como framework base, junto a otras librerías importantes.

Las dependencias están definidas en `requirements.txt`.  
Entre las más relevantes:

- **fastapi**
- **uvicorn**
- **python-dotenv**
- **pandas** (manejo de CSV)
- **bcrypt** (hashing de contraseñas)
- **passlib**
- **python-multipart**
- **pydantic**
- **typing-extensions**

> Todas se instalan automáticamente con `pip install -r requirements.txt`.

---

# 3. Estructura de Archivos Importantes
```md
back/
├── api/ # Routers y endpoints
├── core/ # Configuración, seguridad, utilidades
├── models/ # Modelos Pydantic
├── services/ # Lógica de negocio
├── storage/ # Manejo de persistencia en CSV
├── data/ # Archivos CSV del sistema
├── main.py # Punto de entrada de la API
└── requirements.txt # Dependencias
```
---

# 4. Instalación del Entorno

## 4.1 Clonar el repositorio

```bash
git clone https://github.com/JoseDavidDev/proyecto-casino2.git
cd proyecto-casino2/back
```

# 5. (Opcional) Crear un entorno virtual
## Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

## Linux / Mac
```bash
python -m venv .venv
source .venv/bin/activate
```

# 6. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

# 7. Archivos CSV (datos)

Los archivos CSV están en la carpeta `data/`. Si alguno falta o se corrompe, las opciones habituales son:

- Recuperar desde una copia de seguridad o el historial de Git.
- Crear el archivo manualmente siguiendo el esquema en `docs/02_modelo_datos.md`.

No existe un script `init_csvs.py` en este repo — la restauración es manual o desde backups.

# 8. Configuración del archivo .env

Crear un archivo ``.env`` en ``/back/`` con este contenido como ejemplo:
```env
APP_ENV=development
SECRET_KEY=changeme

CSV_BASE_PATH=data

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs.csv
```

> No subir el ``.env`` al repositorio.`

# 9. Ejecutar el servidor local
```bash
uvicorn back.main:app --reload
```

La API estará disponible en:
```cpp
http://127.0.0.1:8000
```

Documentación interactiva:
```arduino
http://127.0.0.1:8000/docs
```

# 10. Verificación del estado del sistema

El proyecto incluye un endpoint de salud:
```bash
GET /health
```
Debe responder:
```json
{ "status": "ok" }
```

# 11. Notas importantes

- Todos los datos se almacenan en CSV, no hay base de datos SQL todavía.

- No se requiere Docker, servicios externos ni redes.

- El proyecto está diseñado para funcionar completamente offline.

- Cambios manuales en los CSV deben hacerse con cuidado.