# back/domain/users/login.py

from datetime import datetime, timedelta
from typing import Union, Dict

from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException, status

from back.storage.users_repo import get_user_by_username, update_user_row
from back.models.auth import LoginOut
from back.core import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _verify_password(plain: str, hashed: str) -> bool:
    # Try bcrypt verify first if the stored looks like a hash
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        # Fallback: compare raw strings (migration support for existing CSVs)
        return plain == hashed


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _create_access_token(data: Dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + settings.ACCESS_TOKEN_EXPIRE
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def login_user(username: str, password: str) -> Union[LoginOut, HTTPException]:
    user = get_user_by_username(username)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inválido. El usuario no está registrado")

    # Validate password: support hashed and plain (migration)
    stored_pw = user.get("password", "")
    if not _verify_password(password, stored_pw):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta. Intente nuevamente")

    # Check active
    if not user.get('is_active', False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo. Contacte al administrador.")

    # If stored password was plain (not hashed) re-hash and persist
    if not str(stored_pw).startswith("$2"):
        try:
            new_hash = _hash_password(password)
            update_user_row(int(user["id"]), {"password": new_hash, "updated_at": datetime.now().strftime(settings.TIME_FMT), "updated_by": "system"})
        except Exception:
            # best-effort, do not block login if update fails
            pass

    token_data = {"sub": str(int(user["id"])), "username": user["username"], "role": user.get("role")}
    access_token = _create_access_token(token_data)

    return LoginOut(id=int(user['id']), username=user['username'], role=user.get('role'), access_token=access_token)