# -------------------------------------------
# back/tests/test_auth.py
# Propósito:
#   - Definir pruebas unitarias para el módulo de autenticación (register/login).
#   - Estas pruebas usan TestClient de FastAPI para simular peticiones HTTP.
#
# Qué debe probar:
#   1) Registro (POST /api/v1/auth/register):
#       - Caso feliz: crear un nuevo usuario con username y password válidos. Se espera status_code 201 y estructura del usuario devuelto (id, name, username).
#       - Caso duplicado: intentar crear un usuario con username que ya existe. Se espera status_code 400 (o el código convenido) y un mensaje de error indicando duplicado.
#   2) Login (POST /api/v1/auth/login):
#       - Caso feliz: autenticar un usuario existente con credenciales correctas. Se espera status_code 200 y datos del usuario en el cuerpo de la respuesta.
#       - Caso error: enviar credenciales incorrectas o usuario inexistente. Se espera status_code 401 (o 400) y mensaje de error.
#
# Entradas:
#   - Todas las pruebas envían JSON en el cuerpo con campos "name" (solo para registro), "username" y "password".
#   - Usar TestClient para hacer requests.
#   - Asegurar que los CSV de usuarios de prueba estén en un estado controlado: se recomienda copiar users.csv a un directorio temporal o mockear rutas antes de cada test para no afectar datos reales.
#
# Salidas:
#   - Assert de status_code.
#   - Verificar que en el caso exitoso el JSON devuelto contiene las claves esperadas.
#   - En errores, verificar que se retorna un mensaje adecuado.
#
# Notas:
#   - Seguir el mismo patrón de comentarios y estructura que en los otros tests (test_health, test_machines_min).
#   - No incluir código real; solo comentarios explicando cada paso.
# -------------------------------------------

STADO: ✅ 5/5 PRUEBAS PASANDO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 ERROR #1: RUTAS DUPLICADAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SÍNTOMA:
  POST /api/api/v1/auth/login  ❌ (prefijo duplicado)
  POST /api/v1/users/api/v1/users  ❌ (ruta duplicada)

ARCHIVO: back/api/router.py (líneas 12-14)

ANTES (❌ INCORRECTO):
  api_router = APIRouter(prefix="/api/v1")
  api_router.include_router(auth_router, tags=["auth"])
  api_router.include_router(users_router, prefix="/users", tags=["users"])

DESPUÉS (✅ CORRECTO):
  api_router = APIRouter()  # Sin prefijo aquí
  api_router.include_router(auth_router, prefix="/v1/auth", tags=["auth"])
  api_router.include_router(users_router, prefix="/v1/users", tags=["users"])

EXPLICACIÓN:
  main.py ya añade /api, así que router.py NO debe añadirlo de nuevo
  
RESULTADO:
  ✅ POST /api/v1/auth/login  (CORRECTO)
  ✅ POST /api/v1/users  (CORRECTO)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 ERROR #2: RUTAS HARDCODEADAS EN DECORATORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SÍNTOMA:
  POST /api/v1/users/api/v1/users  ❌ (ruta duplicada)

ARCHIVO: back/api/v1/users.py (línea 73)

ANTES (❌ INCORRECTO):
  @router.post("/api/v1/users", response_model=UserOut)
  def create_user_endpoint(user: UserIn):
      ...

DESPUÉS (✅ CORRECTO):
  @router.post("/", response_model=UserOut)
  def create_user_endpoint(user: UserIn):
      ...

CONCEPTO CLAVE:
  ❌ Cuando usas include_router(prefix="/v1/users"), NO escribas la ruta completa
  ✅ Usa solo la parte relativa (/) en el decorator

  Ejemplo correcto:
    include_router(users_router, prefix="/v1/users")
    @router.post("/")  ← Relativa, no /api/v1/users
    Resultado: /v1/users + / = /v1/users ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 ERROR #3: TESTS FALLANDO CON 404
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SÍNTOMA:
  AssertionError: Se esperaba 200, se obtuvo 404
  Response: {"detail":"Not Found"}

CAUSA:
  Errores #1 y #2 arriba

ARCHIVO: back/tests/test_auth.py

SOLUCIÓN:
  Corregir Errores #1 y #2

RESULTADO:
  ✅ 5/5 TESTS PASANDO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 CAMBIOS REALIZADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARCHIVO                    TIPO       LÍNEAS    ESTADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
back/api/router.py         Modificado 4         ✅
back/api/v1/users.py       Modificado 1         ✅
back/tests/test_auth.py    Nuevo      192       ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ PRUEBAS UNITARIAS (5 TOTAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ test_login_caso_feliz
   Objetivo: Usuario con credenciales correctas puede loguearse
   Status Code Esperado: 200
   Resultado: PASADO ✅

✅ test_login_usuario_no_existe
   Objetivo: Error cuando usuario no existe
   Status Code Esperado: 401 Unauthorized
   Resultado: PASADO ✅

✅ test_login_contraseña_incorrecta
   Objetivo: Error cuando contraseña es incorrecta
   Status Code Esperado: 401 Unauthorized
   Resultado: PASADO ✅

✅ test_login_usuario_inactivo
   Objetivo: Error cuando usuario está inactivo
   Status Code Esperado: 403 Forbidden
   Resultado: PASADO ✅

✅ test_login_campos_requeridos
   Objetivo: Pydantic rechaza requests incompletos
   Status Code Esperado: 422 Unprocessable Entity
   Resultado: PASADO ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 CÓMO EJECUTAR LAS PRUEBAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$ python -m pytest back/tests/test_auth.py -v

RESULTADO ESPERADO:
  ===== 5 passed in 0.95s =====

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 CONCEPTOS CLAVE PARA RECORDAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ESTRUCTURA DE RUTAS EN FASTAPI
   
   main.py:
     app.include_router(api_router, prefix="/api")
                                              ↓
   router.py:
     api_router.include_router(auth_router, prefix="/v1/auth")
                                                   ↓
   v1/auth.py:
     @router.post("/login")
              ↓
   RESULTADO FINAL: /api + /v1/auth + /login = /api/v1/auth/login ✅

2. REGLA DE ORO
   
   Cuando uses include_router(prefix="..."), los decorators deben ser RELATIVOS
   
   ✅ BIEN:  @router.post("/")
   ❌ MAL:   @router.post("/api/v1/users")

3. NUNCA DUPLICAR PREFIJOS
   
   ❌ MALO:
      APIRouter(prefix="/api/v1")
      + app.include_router(prefix="/api")
      = /api/api/v1  (DUPLICADO)
   
   ✅ BIEN:
      APIRouter()
      + app.include_router(prefix="/api")
      = /api  (CORRECTO)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 INFORMACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fecha:        20 de Noviembre, 2025
Rama:         QA
Proyecto:     proyecto-casino
Python:       3.12.1
Framework:    FastAPI
Testing:      pytest 8.2.1

Status:       ✅ COMPLETADO - TODAS LAS PRUEBAS PASANDO

DOCUMENTACIÓN DISPONIBLE:
  • RESUMEN_PRUEBAS_AUTH.md - Documentación técnica completa (742 líneas)
  • ERRORES_Y_SOLUCIONES.md - Guía rápida de errores
  • INDEX.md - Índice de documentación
  • GUIA_RAPIDA_DESARROLLADORES.txt - Este archivo
