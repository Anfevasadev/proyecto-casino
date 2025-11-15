import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path

RUTA_DATOS = "data/users.csv"

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:  #Buscamos a un usuario por su user y retornamos un diccionario con los datos si lo encuentra o un None si no existe
    try:
        df = pd.read_csv(RUTA_DATOS) #cargamos y leemos los datos 
        
        user_data = df[df['username'] == username] #Filtramos para buscar por el usuario que le pasamos
        
        if not user_data.empty:
            user_dict = user_data.iloc[0].to_dict() #si el user existe (no está vacio) seleccionamos la primer y unica fila que encontró y convertimos a diccionario
            
            user_dict['is_active'] = str(user_dict.get('is_active', 'false')).lower() == 'true' # Convertimos la fila "is_active" a booleano para que se pueda leer 
            
            return user_dict # Retornamos el diccionario con los datos del usuario
        
        return None # Si no se encontró el user retornamos None
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {RUTA_DATOS}")
        return None
    except Exception as e:
        print(f"Error al leer el repositorio de usuarios: {e}")
        return None
CSV_PATH = Path("data/users.csv")
def load_users():
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns = ["username", "password", "role", "is_active", "created_at", "created_by"])
def save_users(df):
    df.to_csv(CSV_PATH, index = False)
def username_exists(username: str):
    df = load_users()
    return username in df["username"].values
def insert_user(user_dict: dict):
    df = load_users()

    if user_dict["username"] in df["username"].values:
        raise ValueError("Username ya existe")
    df = pd.concat([df, pd.DataFrame([user_dict])], ignore_index= True)
    save_users(df)    