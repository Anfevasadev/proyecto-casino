import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path

CSV_PATH = Path("data/users.csv")

EXPECTED_COLUMNS = [
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


def _read_df() -> pd.DataFrame:
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
    # Asegurar columnas completas
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[EXPECTED_COLUMNS]


def _write_df(df: pd.DataFrame) -> None:
    df.to_csv(CSV_PATH, index=False)


def next_id() -> int:
    df = _read_df()
    if df.empty:
        return 1
    # Tomar solo ids válidos numéricos
    ids = [int(x) for x in df["id"].dropna().tolist() if str(x).strip() != ""]
    return (max(ids) + 1) if ids else 1


def username_exists(username: str) -> bool:
    df = _read_df()
    subset = df[(df["username"] == username) & (df["is_deleted"].astype(str).str.lower() != "true")]
    return not subset.empty


def insert_user(row: Dict[str, Any]) -> Dict[str, Any]:
    df = _read_df()
    if username_exists(row["username"]):
        raise ValueError("Username ya existe")
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _write_df(df)
    return row


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    df = _read_df()
    subset = df[df["username"] == username]
    if subset.empty:
        return None
    user = subset.iloc[0].to_dict()
    # Normalizar tipos
    user["id"] = int(user["id"]) if str(user.get("id", "")).strip() else None
    user["is_active"] = str(user.get("is_active", "false")).lower() == "true"
    return user
