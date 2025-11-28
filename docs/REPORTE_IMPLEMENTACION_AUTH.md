# Reporte de implementación: Autenticación y Autorización (JWT + Bcrypt)

Fecha: 2025-11-27
Autor: Cambios aplicados por el equipo (resumen generado automáticamente)

---

## Resumen ejecutivo

Se implementó autenticación basada en JWT y hashing de contraseñas con bcrypt (passlib). Además se añadió una dependencia/utility para la verificación de roles y se protegieron endpoints clave usando dicha dependencia. También se añadió un middleware que decodifica el token en cada request y deja el payload en `request.state.user` (uso interno).

Objetivos cumplidos:
- Login con email/username + password (actualmente username). Generación de token JWT que incluye el rol.
- Hash seguro de contraseñas (bcrypt) al crear usuarios y migración "best-effort" para contraseñas planas existentes.
- Dependency `verificar_rol(permisos_requeridos)` para proteger endpoints y devolver 401/403 según el caso.
- CORS habilitado (modo desarrollo) para conectar con el frontend.

Archivos creados/modificados (principal)
- `requirements.txt`  
  - Añadidos: `python-jose[cryptography]`, `passlib[bcrypt]`.

- `back/core/settings.py`  
  - Implementadas constantes: `BASE_DIR`, `DATA_DIR`, `TIME_FMT`, `ROLES_PERMITIDOS`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.

- `back/models/auth.py`  
  - `LoginOut` ahora incluye `access_token` y `token_type`.

- `back/api/deps.py`  
  - `oauth2_scheme` (OAuth2PasswordBearer), `decodificar_jwt(token)` y `verificar_rol(permisos_requeridos)` implementados.

- `back/domain/users/login.py`  
  - Verificación de password con `passlib` (bcrypt).  
  - Generación de token JWT con `python-jose`.  
  - Re-hashing (migración) de contraseñas planas al iniciar sesión (accion best-effort).

- `back/domain/users/create.py`  
  - Nuevo hashing de contraseñas al crear usuarios.

- `back/main.py`  
  - Añadido `AuthMiddleware` para decodificar token si viene en Authorization Bearer y dejar payload en `request.state.user`.

- Endpoints protegidos:  
  - `back/api/v1/machines.py` → crear/actualizar/activar/inactivar: `admin`  
  - `back/api/v1/counters.py` → crear contador: `admin`, `operador`  
  - `back/api/v1/balances.py` → generar cuadre casino: `admin`,`soporte`; cuadre máquina: `admin`,`soporte`,`operador`  
  - `back/api/v1/users.py` → crear/actualizar/eliminar: `admin`

---

## Detalle técnico por archivo

### `requirements.txt`
- Se agregaron bibliotecas necesarias para JWT y hashing:
  - `python-jose[cryptography]` — decodificar y crear JWT.
  - `passlib[bcrypt]` — hashing y verificación de contraseñas con bcrypt.

### `back/core/settings.py`
- Nuevas constantes (valores para dev incluidos):
  - `BASE_DIR`, `DATA_DIR`, `TIME_FMT`.
  - `ROLES_PERMITIDOS = {"admin","operador","soporte"}`
  - `SECRET_KEY` (hardcodeado para desarrollo; mover a env en prod), `ALGORITHM = "HS256"`.
  - `ACCESS_TOKEN_EXPIRE_MINUTES` y `ACCESS_TOKEN_EXPIRE` (timedelta).

### `back/models/auth.py`
- `LoginOut` ahora devuelve:
  - `id`, `username`, `role`, `access_token`, `token_type`.

### `back/api/deps.py`
- Implementaciones principales:
  - `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")` — lectura de header Authorization.
  - `decodificar_jwt(token)` — decodifica y valida JWT con `SECRET_KEY` y `ALGORITHM`, lanza 401 si inválido o expirado.
  - `verificar_rol(permisos_requeridos)` — retorna dependencia para FastAPI que verifica si el `role` del payload está en la lista; lanza 401/403 según sea necesario.

Errores definidos:
- 401: token inválido/expirado o token sin rol
- 403: rol no permitido

### `back/domain/users/login.py`
- Lógica:
  1. Buscar usuario por `username` desde `users_repo`.
  2. Verificar contraseña con `passlib` (bcrypt). Si falla la verificación con bcrypt, compara texto plano (para migración desde CSV existente).
  3. Si contraseña almacenada parece plana (no empieza con `$2`), re-hashear y actualizar la fila en CSV (best-effort).
  4. Validar `is_active`.
  5. Generar JWT que incluye `sub` (user id), `username` y `role`. El token contiene `exp`.
  6. Retornar `LoginOut` con `access_token`.

Notas:
- Si la actualización del CSV falla al re-hashear, el login sigue permitiéndose (no bloquea al usuario).

### `back/domain/users/create.py`
- Al crear usuario se guarda `password` hasheado con bcrypt (passlib).

### `back/main.py`
- `AuthMiddleware` intenta decodificar el token Bearer de `Authorization` y, si se puede, asigna el payload a `request.state.user`. Esto facilita acceder a información del usuario desde cualquier handler o middleware sin depender de `Depends`.
- CORS configurado con `allow_origins=["*"]` para desarrollo.

### Protecciones en Endpoints
- Se usó `Depends(verificar_rol([...]))` para forzar permisos según la tabla solicitada. Esto retorna 401/403 según corresponda y deja el payload (decoded JWT) como el valor de dependecia si se necesita dentro del endpoint.

---

## Cómo probar los cambios (paso a paso)

1) Instalar dependencias (recomendado en entorno virtual):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Levantar la API:

```bash
uvicorn back.main:app --reload
```

3) Probar login:

```bash
curl -s -X POST "http://127.0.0.1:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}' | jq
```
- Respuestas esperadas:
  - `200`: JSON con `access_token`.
  - `401`: usuario inválido o contraseña incorrecta.
  - `403`: usuario inactivo.

4) Llamada a endpoint protegido (ejemplo: crear máquina — `admin` requerido):

```bash
TOKEN=<access_token_obtenido>
curl -X POST "http://127.0.0.1:8000/api/v1/machines" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...payload...}'
```
- Respuesta:
  - `200`/`201` si autorizado y datos válidos.
  - `403` si rol no permitido.
  - `401` si token inválido/expirado.

---

## Recomendaciones y próximos pasos

1. Mover `SECRET_KEY` fuera del código fuente (usar variables de entorno o un .env para desarrollo).
2. Añadir tests que cubran: login (200/401/403), endpoints protegidos (200/403/401), y migración de contraseñas.
3. Considerar endpoint para refrescar tokens (refresh tokens) si es necesario mantener sesiones largas.
4. Añadir logging de accesos/errores relacionados a autenticación (para auditoría).
5. Revisar CSVs y normalizar valores booleanos y formatos de fecha para evitar inconsistencias al parsear con pandas.
6. (Opcional) Crear script `migrate_hash_passwords.py` para convertir todas las contraseñas planas en `data/users.csv` a bcrypt en lote.

---

## Checklist (estado)
- [x] Generación JWT con rol incluido
- [x] Hash de contraseñas al crear usuario
- [x] Re-hash en login (migración)
- [x] Dependencia `verificar_rol` implementada
- [x] Middleware opcional para exponer `request.state.user`
- [x] Protecciones aplicadas a endpoints principales
- [ ] Tests ejecutados y validados
- [ ] Migración masiva de contraseñas (opcional)

---

## Ruta del archivo
- Documento generado: `docs/REPORTE_IMPLEMENTACION_AUTH.md`

---

Si quieres, puedo:
- Generar también un PDF del reporte.
- Ejecutar `pytest` y adjuntar los resultados.
- Crear el script de migración para hashear todas las contraseñas en `data/users.csv`.

Dime qué más necesitas y lo hago.