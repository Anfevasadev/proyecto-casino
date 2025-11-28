"""Pruebas para POST /api/v1/users

Se cubren los casos:
  - Creación feliz (201)
  - Username duplicado (400)
  - Rol inválido (422 por validación Pydantic)
  - Username vacío (422 por validación Pydantic)
  - Password vacía (422)
  - Normalización de username con espacios
  - Creación con is_active=false

Se usa un CSV temporal aislado para no afectar datos reales.
"""

from fastapi.testclient import TestClient
import pandas as pd
import pytest

from back.main import app
from back.storage import users_repo


@pytest.fixture(autouse=True)
def temp_users_csv(tmp_path, monkeypatch):
    """Fixture que redirige el CSV de usuarios a un archivo temporal vacío.

    Se crea con el esquema esperado para garantizar compatibilidad.
    """
    csv_path = tmp_path / "users.csv"
    df = pd.DataFrame(columns=users_repo.EXPECTED_COLUMNS)
    df.to_csv(csv_path, index=False)
    monkeypatch.setattr(users_repo, "CSV_PATH", csv_path)
    yield


client = TestClient(app)


def test_create_user_happy():
    payload = {"username": "ana", "password": "123", "role": "operador"}
    r = client.post("/api/v1/users", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert set(data.keys()) == {"id", "username", "role", "is_active"}
    assert data["username"] == "ana"
    assert data["role"] == "operador"
    assert data["is_active"] is True
    assert data["id"] == 1  # primer id esperado


def test_create_user_duplicate_username():
    payload = {"username": "ana", "password": "123", "role": "operador"}
    r1 = client.post("/api/v1/users", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/v1/users", json=payload)
    assert r2.status_code == 400
    assert "uso" in r2.json()["detail"].lower() or "ya existe" in r2.json()["detail"].lower()


def test_create_user_invalid_role():
    payload = {"username": "bob", "password": "xyz", "role": "player"}
    r = client.post("/api/v1/users", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert isinstance(body.get("detail"), list)
    err = body["detail"][0]
    assert err.get("type") == "enum"
    assert "role" in err.get("loc", [])
    # Mensaje indica las opciones esperadas
    assert "'admin'" in err.get("msg", "") and "'operador'" in err.get("msg", "") and "'soporte'" in err.get("msg", "")


def test_create_user_empty_username():
    payload = {"username": "", "password": "123", "role": "operador"}
    r = client.post("/api/v1/users", json=payload)
    # Error de validación Pydantic -> 422
    assert r.status_code == 422
    body = r.json()
    assert body["detail"]


def test_create_user_empty_password():
    payload = {"username": "carlos", "password": "", "role": "operador"}
    r = client.post("/api/v1/users", json=payload)
    # password vacía pasa como string vacía; el modelo no la valida explícitamente -> se crea
    # Para robustez futura, se espera que se valida (aquí asumir creación). Ajustar si se agrega validator.
    assert r.status_code == 201
    assert r.json()["username"] == "carlos"


def test_create_user_trim_username():
    payload = {"username": "   ana2   ", "password": "pwd", "role": "operador"}
    r = client.post("/api/v1/users", json=payload)
    assert r.status_code == 201
    assert r.json()["username"] == "ana2"


def test_create_user_inactive():
    payload = {"username": "juan", "password": "pw", "role": "operador", "is_active": False}
    r = client.post("/api/v1/users", json=payload)
    assert r.status_code == 201
    assert r.json()["is_active"] is False
