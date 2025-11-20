from fastapi.testclient import TestClient
from back.api.v1.users import router
from fastapi import FastAPI

# Crea una app temporal para pruebas
app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_create_user_exitoso(monkeypatch):
    # Mock de la función create_user para evitar efectos reales
    def mock_create_user(user, created_by="system"):
        return {
            "id": 1,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active
        }
    monkeypatch.setattr("back.domain.users.create.create_user", mock_create_user)

    payload = {
        "username": "usuario_prueba",
        "password": "123456",
        "role": "operador",
        "is_active": True
    }
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["username"] == "usuario_prueba"
    assert data["role"] == "operador"
    assert data["is_active"] is True
    assert "password" not in data

def test_create_user_username_duplicado(monkeypatch):
    # Mock para simular username duplicado
    def mock_create_user(user, created_by="system"):
        raise ValueError("Username duplicado")
    monkeypatch.setattr("back.domain.users.create.create_user", mock_create_user)

    payload = {
        "username": "usuario_prueba",
        "password": "123456",
        "role": "operador",
        "is_active": True
    }
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 500 or response.status_code == 400