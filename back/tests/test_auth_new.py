# -------------------------------------------
# back/tests/test_auth.py
# Propósito:
#   - Definir pruebas unitarias para el módulo de autenticación (login).
#   - Estas pruebas usan TestClient de FastAPI para simular peticiones HTTP.
#
# Qué debe probar:
#   1) Login (POST /api/v1/auth/login):
#       - Caso feliz: autenticar un usuario existente con credenciales correctas. 
#         Se espera status_code 200 y datos del usuario en el cuerpo de la respuesta.
#       - Caso usuario no existe: enviar credenciales de usuario inexistente. 
#         Se espera status_code 401 y mensaje de error.
#       - Caso contraseña incorrecta: usuario existe pero contraseña incorrecta. 
#         Se espera status_code 401 y mensaje de error.
#       - Caso usuario inactivo: usuario existe y contraseña correcta pero está inactivo. 
#         Se espera status_code 403 y mensaje de error.
#
# Entradas:
#   - Todas las pruebas envían JSON en el cuerpo con campos "username" y "password".
#   - Usar TestClient para hacer requests.
#   - Las pruebas se basan en datos reales del archivo data/users.csv.
#
# Salidas:
#   - Assert de status_code.
#   - Verificar que en el caso exitoso el JSON devuelto contiene las claves esperadas (id, username, role).
#   - En errores, verificar que se retorna un mensaje de error adecuado.
#
# Notas:
#   - Seguir el mismo patrón de comentarios y estructura que en los otros tests.
#   - Las pruebas NO modifican el CSV de usuarios.
# -------------------------------------------

import pytest
from fastapi.testclient import TestClient
from back.main import app


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def client():
    """Proporciona un cliente de prueba para hacer requests a la API."""
    return TestClient(app)


# ============================================
# PRUEBAS DE LOGIN
# ============================================

class TestLogin:
    """Pruebas unitarias para el endpoint POST /api/v1/auth/login"""

    def test_login_caso_feliz(self, client):
        """
        Caso feliz: Autenticar un usuario existente con credenciales correctas.
        
        Entrada:
            - username: usuario válido que existe en data/users.csv
            - password: contraseña correcta
        
        Salida esperada:
            - status_code: 200
            - body contiene: id (int), username (str), role (str)
        """
        # Arrange: preparar datos de entrada
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        # Act: hacer el request al endpoint
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert: validar la respuesta
        assert response.status_code == 200, f"Se esperaba 200, se obtuvo {response.status_code}. Response: {response.text}"
        
        data = response.json()
        assert "id" in data, "El response debe contener 'id'"
        assert "username" in data, "El response debe contener 'username'"
        assert "role" in data, "El response debe contener 'role'"
        assert data["username"] == "admin", "El username debe ser 'admin'"
        assert isinstance(data["id"], int), "El id debe ser un entero"

    def test_login_usuario_no_existe(self, client):
        """
        Caso de error: Intentar autenticar con un usuario que no existe.
        
        Entrada:
            - username: usuario que NO existe en data/users.csv
            - password: cualquier contraseña
        
        Salida esperada:
            - status_code: 401 (Unauthorized)
            - body contiene mensaje de error
        """
        # Arrange: preparar datos de entrada con usuario inexistente
        login_data = {
            "username": "usuario_que_no_existe",
            "password": "password123"
        }
        
        # Act: hacer el request al endpoint
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert: validar la respuesta de error
        assert response.status_code == 401, f"Se esperaba 401, se obtuvo {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "El response debe contener 'detail' con el mensaje de error"
        assert "Usuario inválido" in data["detail"] or "no está registrado" in data["detail"]

    def test_login_contraseña_incorrecta(self, client):
        """
        Caso de error: Usuario existe pero la contraseña es incorrecta.
        
        Entrada:
            - username: usuario válido que existe
            - password: contraseña incorrecta
        
        Salida esperada:
            - status_code: 401 (Unauthorized)
            - body contiene mensaje de error sobre contraseña
        """
        # Arrange: preparar datos con usuario correcto pero contraseña incorrecta
        login_data = {
            "username": "admin",
            "password": "contraseña_incorrecta"
        }
        
        # Act: hacer el request al endpoint
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert: validar la respuesta de error
        assert response.status_code == 401, f"Se esperaba 401, se obtuvo {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "El response debe contener 'detail' con el mensaje de error"
        assert "Contraseña" in data["detail"] or "incorrecta" in data["detail"]

    def test_login_usuario_inactivo(self, client):
        """
        Caso de error: Usuario existe y contraseña es correcta, pero usuario está inactivo.
        
        Entrada:
            - username: usuario inactivo que existe
            - password: contraseña correcta
        
        Salida esperada:
            - status_code: 403 (Forbidden)
            - body contiene mensaje de error sobre usuario inactivo
        """
        # Arrange: preparar datos con usuario inactivo
        login_data = {
            "username": "user_inactive",
            "password": "pass456"
        }
        
        # Act: hacer el request al endpoint
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert: validar que es un error 403
        assert response.status_code == 403, f"Se esperaba 403, se obtuvo {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        assert "inactivo" in data["detail"].lower()

    def test_login_campos_requeridos(self, client):
        """
        Caso de validación: Verificar que Pydantic rechaza requests sin campos requeridos.
        
        Entrada:
            - JSON sin el campo 'password'
        
        Salida esperada:
            - status_code: 422 (Unprocessable Entity)
        """
        # Arrange: preparar datos incompletos
        login_data = {
            "username": "admin"
            # Falta el campo 'password'
        }
        
        # Act: hacer el request al endpoint
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert: validar que Pydantic rechaza la solicitud
        assert response.status_code == 422, f"Se esperaba 422, se obtuvo {response.status_code}"
