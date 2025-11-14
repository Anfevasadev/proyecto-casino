# back/domain/users/login.py

from back.storage.users_repo import get_user_by_username # Importamos la función que creamos para acceder a los datos

from back.models.auth import LoginOut # Importamos el modelo de salida de Pydantic
from typing import Union
from fastapi import HTTPException, status # Importamos herramientas de FastAPI para manejar errores HTTP

def login_user(username: str, password: str) -> Union[LoginOut, HTTPException]: # Creamos una funcion para que valide las credenciales y si el usuario está activo, En caso de que exista un error, lo manejará el HTTPException que importamos de FastAPI 

    user = get_user_by_username(username) # Buscamos el usuario 

    # --- REGLA 1: Existencia y Credenciales (401 Unauthorized) ---
    
    if not user:  # si el usuario no se encontró lanzamos el error 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inválido. El usuario no está registrado"
        )

    # --- REGLA 2: Validación de Contraseña (401 Unauthorized) ---
    
    if user['password'] != password: # Verificamos la contraseña. En un caso donde el usuario exista pero la contraseña no sea correcta también se lanza el error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta. Intente nuevamente"
        )

    # --- REGLA 3: Validación de Estado Activo (403 Forbidden) ---
    
    if not user.get('is_active', False): # Verificamos si el usuario está activo o no con ayuda de los booleanos obtenidos del diccionario en la fila de is_active
        raise HTTPException( #En un caso donde el usuario y contraseña sean correctos pero el usuario esté inactivo se lanzará el error 403
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador."
        )

    # --- Construimos la Respuesta ---

    return LoginOut(
        # Aseguramos que el id sea un entero antes de pasarlo al modelo
        id=int(user['id']), 
        username=user['username'],
        role=user['role']
    )