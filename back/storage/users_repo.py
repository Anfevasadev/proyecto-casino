import pandas as pd
from typing import Optional, Dict, Any

RUTA_DATOS = "data/users.csv"


def _read_df() -> pd.DataFrame:
    try:
        df = pd.read_csv(RUTA_DATOS)
    except FileNotFoundError:
        # Crear DF vacío con columnas esperadas si no existe
        cols = [
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
        df = pd.DataFrame(columns=cols)
    return df


def _write_df(df: pd.DataFrame) -> None:
    df.to_csv(RUTA_DATOS, index=False)


def _to_bool(value: Any) -> bool:
    return str(value).lower() == "true"


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    try:
        df = _read_df()
        user_data = df[df["username"] == username]
        if not user_data.empty:
            user_dict = user_data.iloc[0].to_dict()
            user_dict["id"] = int(user_dict["id"]) if str(user_dict.get("id", "")).strip() else None
            user_dict["is_active"] = _to_bool(user_dict.get("is_active", False))
            return user_dict
        return None
    except Exception as e:
        print(f"Error al leer el repositorio de usuarios: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    df = _read_df()
    rows = df[df["id"] == user_id]
    if rows.empty:
        return None
    row = rows.iloc[0].to_dict()
    row["id"] = int(row["id"]) if str(row.get("id", "")).strip() else None
    row["is_active"] = _to_bool(row.get("is_active", False))
    return row


def username_exists(username: str, exclude_id: Optional[int] = None) -> bool:
    df = _read_df()
    mask = df["username"] == username
    if exclude_id is not None:
        mask &= df["id"] != exclude_id
    return not df[mask].empty


def update_user_row(user_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    df = _read_df()
    idx = df.index[df["id"] == user_id]
    if len(idx) == 0:
        return None
    i = idx[0]

    allowed_cols = {"username", "password", "role", "is_active", "updated_at", "updated_by"}
    for k, v in cambios.items():
        if k in allowed_cols:
            df.at[i, k] = v

    _write_df(df)

    updated = df.loc[i].to_dict()
    updated["id"] = int(updated["id"]) if str(updated.get("id", "")).strip() else None
    updated["is_active"] = _to_bool(updated.get("is_active", False))
    return updated
