from pydantic import BaseModel  # Se importa la libreria pydantic para validar los datos del Login

class LoginIn(BaseModel):   #Solo tomamos el user y la contraseña para el inicio de sesión y los tomará en formato string
    username: str
    password: str

class LoginOut(BaseModel):  #devolvemos los datos necesarios tales como el id, el user y el rol que tiene el usuario 
    id: int
    username: str
    role: str
    access_token: str
    token_type: str = "bearer"