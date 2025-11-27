from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from back.core import settings

# OAuth2 scheme (used by FastAPI to parse the Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def decodificar_jwt(token: str) -> dict:
	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
		return payload
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")


def verificar_rol(permisos_requeridos: List[str]):
	def wrapper(token: str = Depends(oauth2_scheme)):
		data = decodificar_jwt(token)
		rol = data.get("role") or data.get("rol") or data.get("role")
		if rol is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin rol")
		if rol not in permisos_requeridos:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
		return data

	return wrapper
