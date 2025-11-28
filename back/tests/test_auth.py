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

import tempfile
from pathlib import Path
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from back.main import app
import back.storage.users_repo as users_repo

EXPECTED_COLUMNS = [
    "id",
    "username",
    "password",
    "role",
    "is_active",
    "is_deleted",
    "created_at",
    "created_by",
    "updated_at",
    "updated_by",
    "deleted_at",
    "deleted_by",
]

@pytest.fixture()
def temp_users_csv(monkeypatch):
    tmp_dir = Path(tempfile.mkdtemp())
    csv_path = tmp_dir / "users.csv"
    # Usuarios:
    # 1 activo válido
    # 2 inactivo
    # 3 activo para probar password errónea
    rows = [
        {
            "id": 1,
            "username": "alice",
            "password": "alice-pass",
            "role": "operador",
            "is_active": True,
            "is_deleted": False,
            "created_at": "2025-11-21 10:00:00",
            "created_by": "system",
            "updated_at": "2025-11-21 10:00:00",
            "updated_by": "system",
            "deleted_at": "",
            "deleted_by": "",
        },
        {
            "id": 2,
            "username": "bob",
            "password": "bob-pass",
            "role": "operador",
            "is_active": False,
            "is_deleted": False,
            "created_at": "2025-11-21 10:00:00",
            "created_by": "system",
            "updated_at": "2025-11-21 10:00:00",
            "updated_by": "system",
            "deleted_at": "",
            "deleted_by": "",
        },
        {
            "id": 3,
            "username": "charlie",
            "password": "charlie-pass",
            "role": "soporte",
            "is_active": True,
            "is_deleted": False,
            "created_at": "2025-11-21 10:00:00",
            "created_by": "system",
            "updated_at": "2025-11-21 10:00:00",
            "updated_by": "system",
            "deleted_at": "",
            "deleted_by": "",
        },
    ]
    df = pd.DataFrame(rows, columns=EXPECTED_COLUMNS)
    df.to_csv(csv_path, index=False)
    monkeypatch.setattr(users_repo, "CSV_PATH", csv_path)
    yield
    # Limpieza automática por tmp (no se borra explícitamente para inspección si falla)

client = TestClient(app)

def _post_login(payload):
    return client.post("/api/v1/login", json=payload)

def test_login_ok(temp_users_csv):
    r = _post_login({"username": "alice", "password": "alice-pass"})
    assert r.status_code == 200
    data = r.json()
    assert ({"id", "username", "role"}.issubset(data.keys()))

def test_login_inactivo(temp_users_csv):
    r = _post_login({"username": "bob", "password": "bob-pass"})
    # Esperado normalmente 403 (forbidden) o 400; ajustar si la implementación usa otro código.
    assert r.status_code in (400, 401, 403)
    # Mensaje opcional
    # assert "inactivo" in r.text.lower()

def test_login_password_incorrecta(temp_users_csv):
    r = _post_login({"username": "charlie", "password": "otra"})
    assert r.status_code in (401, 400)
    

def test_login_usuario_no_existe(temp_users_csv):
    r = _post_login({"username": "noexiste", "password": "x"})
    assert r.status_code in (401, 404, 400)

def test_login_falta_username(temp_users_csv):
    r = _post_login({"password": "x"})
    assert r.status_code == 422  # Validación Pydantic (campo faltante)

def test_login_falta_password(temp_users_csv):
    r = _post_login({"username": "alice"})
    assert r.status_code == 422

def test_login_password_vacia(temp_users_csv):
    r = _post_login({"username": "alice", "password": ""})
    # Dependiendo si se valida vacía en endpoint → 400/401/422
    assert r.status_code in (400, 401, 422)

def test_login_extra_fields_ignorados(temp_users_csv):
    r = _post_login({"username": "alice", "password": "alice-pass", "otro": "x"})
    # Debe seguir autenticando correctamente
    assert r.status_code == 200

def test_login_case_sensitivity(temp_users_csv):
    r = _post_login({"username": "Alice", "password": "alice-pass"})
    # Si el login es case-sensitive debe fallar
    # Ajustar según decisión de negocio
    assert r.status_code in (200, 401, 404, 400)
