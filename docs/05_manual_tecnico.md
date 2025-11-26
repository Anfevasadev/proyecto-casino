# Manual Técnico del Backend

Este manual describe en detalle la arquitectura interna del backend del proyecto Casino, incluyendo estructura del sistema, funcionamiento de módulos, ciclo de vida de una solicitud, sistema de persistencia basado en CSV, e instrucciones para mantenimiento y extensibilidad.

---

# 1. Arquitectura del Sistema

El backend sigue una arquitectura en **capas**, lo que permite mantener separado:

- La API (endpoints expuestos)
- La lógica de negocio
- La infraestructura de persistencia
- Los modelos de datos

A continuación se presenta un diagrama conceptual:
```pgsql
               ┌────────────────────────────────┐
               │         Presentación           │
               │             (API)              │
               │   FastAPI → Routers/Endpoints  │
               └─────────────────┬──────────────┘
                                 │
               ┌─────────────────▼─────────────────┐
               │          Lógica de Negocio        │
               │               (Domain)            │
               │  Servicios, casos de uso, reglas  │
               └─────────────────┬─────────────────┘
                                 │
               ┌─────────────────▼──────────────────┐
               │         Infraestructura            │
               │  Repositorios CSV, servicios base  │
               │  conectores, manejo de archivos    │
               └─────────────────┬──────────────────┘
                                 │
               ┌─────────────────▼───────────────────┐
               │              Persistencia           │
               │                  CSV                │
               └─────────────────────────────────────┘
```
---

# 2. Estructura del Backend
```markdown
back/
├── api/
│ ├── v1/ # Routers de FastAPI
│ └── dependencies.py # Dependencias comunes
├── core/ # Configuración y constantes
├── domain/ # Lógica de negocio
├── infrastructure/ # Repositorios CSV + servicios
├── models/ # Modelos Pydantic / entidades
├── storage/ # CSV con datos reales
├── static/ # CSV de ejemplo
├── utils/ # Funciones auxiliares
└── main.py # Punto de entrada
```
---

# 3. Funcionamiento por Capas

## 3.1 Capa API (Presentación)

Aquí se definen los **endpoints**, organizados en routers como:

- `/auth`
- `/users`
- `/places`
- `/machines`
- `/counters`
- `/balances`

Ejemplo de endpoint:

```python
@router.get("/users")
def list_users(service: UserService = Depends(get_user_service)):
    return service.list()
```

La API no contiene lógica de negocio, solo delega todo a los servicios de dominio.

## 3.2 Capa de Dominio (Domain)

Aquí viven:

- Servicios

- Casos de uso

- Reglas de validación

- Cálculo de balances

- Lógica de activación/inactivación

- Operaciones sobre contadores

Ejemplo de servicio:

```python
class UserService:
    def __init__(self, repo):
        self.repo = repo

    def list(self):
        return self.repo.get_all()

    def create(self, data):
        user = User(**data)
        user.password = hash_password(user.password)
        return self.repo.insert(user)
```
El dominio no debe conocer detalles de CSV.
Solo llama a repo.

## 3.3 Capa de Infraestructura

Aquí se implementan los repositorios y adaptadores que sí conocen:

- Dónde viven los CSV

- Cómo se leen

- Cómo se guardan

- Cómo se controlan las actualizaciones

Ejemplo básico:

```python
class CsvUserRepository:
    PATH = "back/storage/users.csv"

    def get_all(self):
        with open(self.PATH, "r") as f:
            return list(csv.DictReader(f))

    def insert(self, user):
        with open(self.PATH, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=user.keys())
            writer.writerow(user)
        return user
```
Esta capa traduce objetos → CSV y CSV → objetos.

# 4. Persistencia con CSV

El sistema usa archivos CSV como base de datos.

Carpeta: back/data

**CSV principales:**

- users.csv

- places.csv

- machines.csv

- counters.csv

- machine_balances.csv

- casino_balances.csv

- logs.csv

## 4.1 Lectura

Se hace con ``csv.DictReader``:

```python
with open(self.PATH, "r") as f:
    rows = list(csv.DictReader(f))
```
## 4.2 Escritura

Para insertar:

```python
with open(self.PATH, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=row.keys())
    writer.writerow(row)
```
## 4.3 Actualización
Para actualizar se reemplaza todo el archivo:

```python
rows = self.get_all()
for r in rows:
    if r["id"] == target_id:
        r.update(data)

with open(self.PATH, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
```

## 4.4 Borrado

Normalmente se usa borrado lógico `(is_deleted = true)`.

# 5. Sistema de Logs Internos

Cada acción crítica se registra en ``logs.csv``.

Ejemplo de registro:

``timestamp,action,machine_id,serial,inactivation_token,motivo,actor,note``

Se registran acciones como:

- Inactivación de máquina

- Cambio de serial

- Registro de contadores

- Errores importantes

# 6. Ciclo de Vida de una Solicitud

Ejemplo: registrar contadores

```csharp
[1] Usuario llama al endpoint → /counters
[2] API recibe datos → validate schema
[3] ServiceCounter.process(data)
[4] RepoCounter.insert(data) → CSV
[5] ServiceLogs.create_entry(...)
[6] API retorna éxito
```

Se sigue este mismo flujo en máquinas, balances y usuarios.

# 7. Seguridad

- Contraseñas con hash

- Tokens de autenticación

- Roles: admin / user

- Inactivación lógica (no borrar datos sensibles)

- Registros de auditoría

# 8. Ejemplos de Código Importantes

## 8.1 Hash de contraseña

```python
import hashlib

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()
```

## 8.2 Validación de usuario y login

```python
user = repo.get_by_username(username)
if not user:
    raise HTTPException(401)

if hash_password(password) != user.password:
    raise HTTPException(401)
```

# 9. Buenas Prácticas del Proyecto

- Mantener separadas las capas API, Domain e Infraestructura

- Reutilizar servicios

- Nunca escribir lógica de negocio en los endpoints

- CSV siempre deben tener encabezados consistentes

- Respaldar CSV antes de grandes cambios

- Registrar todo en logs.csv

# 10. Extensibilidad futura

El sistema está preparado para:

- Migrar a base de datos SQL (solo cambiando repositorios)

- Montar Docker

- Separar servicios en microservicios

- Implementar JWT real

- Agregar reportes automáticos

- Integración con dashboards externos