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
