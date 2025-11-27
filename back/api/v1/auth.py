# back/api/v1/auth.py

from fastapi import APIRouter
# Importamos los modelos que definimos usando Pydantic
from back.models.auth import LoginIn, LoginOut
# Importa la función de dominio que creamos
from back.domain.users.login import login_user

# Creamos un objeto enrutador. Este objeto agrupará todas las rutas de autenticación.
router = APIRouter()


@router.post(
    "/login",
    response_model=LoginOut,
    status_code=200,  # Si el inicio fue exitoso, se devolverá el codigo 200
    description="Endpoint de Autenticación de Usuario",
)
async def login(user_data: LoginIn):
    """Recibe las credenciales, las valida usando la lógica de dominio y retorna token."""

    username = user_data.username
    password = user_data.password

    auth_result = login_user(username, password)

    return auth_result