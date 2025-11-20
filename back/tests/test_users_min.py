INFORME DE ERROR EN ENDPOINT DE CREACIÓN DE USUARIO

Descripción del error:
Actualmente, el endpoint POST /api/v1/users no captura la excepción ValueError que se lanza cuando se intenta crear un usuario con un username ya existente. Esto provoca que la excepción se propague sin control, resultando en un error interno del servidor y haciendo que las pruebas unitarias fallen.

Evidencia:
Durante la ejecución de las pruebas unitarias, se obtiene el siguiente error:
ValueError: El username ya está en uso.

Ubicación:
Archivo: back/api/v1/users.py
Función: create_user_endpoint

Causa:
El endpoint llama directamente a la función create_user, la cual lanza un ValueError si el username ya existe, pero este error no es capturado ni transformado en una respuesta HTTP adecuada.

Recomendación de corrección:
Modificar el endpoint para capturar la excepción ValueError y devolver una respuesta HTTP 400 (Bad Request) usando HTTPException de FastAPI. Ejemplo sugerido:

from fastapi import HTTPException

@router.post("/api/v1/users", response_model=UserOut)
def create_user_endpoint(user: UserIn):
    try:
        new_user = create_user(user, created_by="system")
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

Impacto:
Esto permitirá que el endpoint devuelva un mensaje de error claro al cliente y que las pruebas unitarias pasen correctamente, mejorando la robustez y mantenibilidad del código.
