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
    status_code=200, #Si el inicio fue exitoso, se devolverá el codigo 200 
    description="Endpoint de Autenticación de Usuario"
)
async def login(user_data: LoginIn): #  Recibe las credenciales, las valida usando la lógica de dominio y retorna la información básica del usuario si son correctas y está activo.

# Acá los datos ya han sido validados por Pydantic usando la funcion de LoginIn
    username = user_data.username 
    password = user_data.password
    
   #Llamamos al dominio para verificar las credenciales, si todo sale bien el estado de codigo será 200, si lanza aalgun error, se lanza el 401 o 403 segun sea el caso
    auth_result = login_user(username, password)
    
    # Se retorna el resultado de toda la verificacion
    return auth_result