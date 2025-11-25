# -------------------------------------------
# back/storage/balances_repo.py
# Propósito:
#   - Persistir y consultar balances (cuadres) en:
#       * data/machine_balances.csv
#       * data/casino_balances.csv
# -------------------------------------------

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List

# Rutas a los archivos CSV
DATA_DIR = Path(__file__).parent.parent.parent / "data"
MACHINE_BALANCES_CSV = DATA_DIR / "machine_balances.csv"
CASINO_BALANCES_CSV = DATA_DIR / "casino_balances.csv"


class BalancesRepo:
    """Repositorio para gestionar balances de máquinas y casinos"""
    
    def __init__(self):
        self._ensure_files()
    
    def _ensure_files(self):
        """Crea los archivos CSV si no existen"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Crear machine_balances.csv si no existe
        if not MACHINE_BALANCES_CSV.exists():
            df = pd.DataFrame(columns=[
                'id', 'machine_id', 'period_start', 'period_end',
                'in_total', 'out_total', 'jackpot_total', 'billetero_total',
                'utilidad_total', 'generated_at', 'generated_by', 'locked'
            ])
            df.to_csv(MACHINE_BALANCES_CSV, index=False)
        
        # Crear casino_balances.csv si no existe
        if not CASINO_BALANCES_CSV.exists():
            df = pd.DataFrame(columns=[
                'id', 'place_id', 'period_start', 'period_end',
                'in_total', 'out_total', 'jackpot_total', 'billetero_total',
                'utilidad_total', 'generated_at', 'generated_by', 'locked'
            ])
            df.to_csv(CASINO_BALANCES_CSV, index=False)
    
    # ============ FUNCIONES PARA MACHINE BALANCES ============
    
    def listar_machine_balances(
        self,
        machine_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lista balances de máquinas con filtros opcionales"""
        df = pd.read_csv(MACHINE_BALANCES_CSV, dtype=str)
        
        if df.empty:
            return []
        
        # Filtrar por machine_id
        if machine_id is not None:
            df = df[df['machine_id'] == str(machine_id)]
        
        # Filtrar por rango de fechas
        if date_from is not None:
            df = df[df['period_start'] >= date_from]
        
        if date_to is not None:
            df = df[df['period_end'] <= date_to]
        
        # Ordenar por fecha de generación
        df = df.sort_values(by='generated_at', ascending=False)
        
        # Aplicar paginación
        if limit is not None:
            df = df.iloc[offset:offset + limit]
        else:
            df = df.iloc[offset:]
        
        # Convertir a lista de diccionarios
        results = []
        for _, row in df.iterrows():
            results.append(self._normalize_machine_balance(row.to_dict()))
        
        return results
    
    def insertar_machine_balance(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Inserta un nuevo balance de máquina"""
        df = pd.read_csv(MACHINE_BALANCES_CSV, dtype=str)
        
        # Generar ID si no existe
        if 'id' not in row or row['id'] is None:
            row['id'] = self._next_machine_balance_id()
        
        # Agregar fila
        new_row = pd.DataFrame([row])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(MACHINE_BALANCES_CSV, index=False)
        
        return self.obtener_machine_balance_por_id(int(row['id']))
    
    def obtener_machine_balance_por_id(self, balance_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un balance de máquina por ID"""
        df = pd.read_csv(MACHINE_BALANCES_CSV, dtype=str)
        
        if df.empty:
            return None
        
        rows = df[df['id'] == str(balance_id)]
        
        if rows.empty:
            return None
        
        return self._normalize_machine_balance(rows.iloc[0].to_dict())
    
    def lock_machine_balance(self, balance_id: int, actor: str, clock) -> bool:
        """Bloquea un balance de máquina"""
        df = pd.read_csv(MACHINE_BALANCES_CSV, dtype=str)
        
        idx = df.index[df['id'] == str(balance_id)]
        
        if len(idx) == 0:
            return False
        
        i = idx[0]
        df.at[i, 'locked'] = 'True'
        df.at[i, 'generated_by'] = actor
        df.at[i, 'generated_at'] = clock().strftime("%Y-%m-%d %H:%M:%S")
        
        df.to_csv(MACHINE_BALANCES_CSV, index=False)
        return True
    
    def _next_machine_balance_id(self) -> int:
        """Calcula el siguiente ID para machine_balances"""
        df = pd.read_csv(MACHINE_BALANCES_CSV, dtype=str)
        
        if df.empty:
            return 1
        
        ids = [int(x) for x in df['id'].dropna() if str(x).strip() != '']
        return (max(ids) + 1) if ids else 1
    
    def _normalize_machine_balance(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza tipos de datos de un balance de máquina"""
        try:
            row['id'] = int(row['id'])
        except (ValueError, TypeError):
            row['id'] = None
        
        try:
            row['machine_id'] = int(row['machine_id'])
        except (ValueError, TypeError):
            row['machine_id'] = None
        
        for field in ['in_total', 'out_total', 'jackpot_total', 'billetero_total', 'utilidad_total']:
            try:
                row[field] = float(row.get(field, 0))
            except (ValueError, TypeError):
                row[field] = 0.0
        
        # Normalizar locked a booleano
        locked_val = row.get('locked', 'False')
        if isinstance(locked_val, str):
            row['locked'] = locked_val.lower() == 'true'
        else:
            row['locked'] = bool(locked_val)
        
        return row
    
    # ============ FUNCIONES PARA CASINO BALANCES ============
    
    def listar_casino_balances(
        self,
        place_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lista balances de casinos con filtros opcionales"""
        df = pd.read_csv(CASINO_BALANCES_CSV, dtype=str)
        
        if df.empty:
            return []
        
        # Filtrar por place_id
        if place_id is not None:
            df = df[df['place_id'] == str(place_id)]
        
        # Filtrar por rango de fechas
        if date_from is not None:
            df = df[df['period_start'] >= date_from]
        
        if date_to is not None:
            df = df[df['period_end'] <= date_to]
        
        # Ordenar por fecha de generación
        df = df.sort_values(by='generated_at', ascending=False)
        
        # Aplicar paginación
        if limit is not None:
            df = df.iloc[offset:offset + limit]
        else:
            df = df.iloc[offset:]
        
        # Convertir a lista de diccionarios
        results = []
        for _, row in df.iterrows():
            results.append(self._normalize_casino_balance(row.to_dict()))
        
        return results
    
    def insertar_casino_balance(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Inserta un nuevo balance de casino"""
        df = pd.read_csv(CASINO_BALANCES_CSV, dtype=str)
        
        # Generar ID si no existe
        if 'id' not in row or row['id'] is None:
            row['id'] = self._next_casino_balance_id()
        
        # Agregar fila
        new_row = pd.DataFrame([row])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CASINO_BALANCES_CSV, index=False)
        
        return self.obtener_casino_balance_por_id(int(row['id']))
    
    def obtener_casino_balance_por_id(self, balance_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un balance de casino por ID"""
        df = pd.read_csv(CASINO_BALANCES_CSV, dtype=str)
        
        if df.empty:
            return None
        
        rows = df[df['id'] == str(balance_id)]
        
        if rows.empty:
            return None
        
        return self._normalize_casino_balance(rows.iloc[0].to_dict())
    
    def get_casino_balance_by_period(
        self,
        place_id: int,
        period_start: str,
        period_end: str
    ) -> Optional[Dict[str, Any]]:
        """Obtiene un balance de casino por periodo"""
        df = pd.read_csv(CASINO_BALANCES_CSV, dtype=str)
        
        if df.empty:
            return None
        
        rows = df[
            (df['place_id'] == str(place_id)) &
            (df['period_start'] == period_start) &
            (df['period_end'] == period_end)
        ]
        
        if rows.empty:
            return None
        
        return self._normalize_casino_balance(rows.iloc[0].to_dict())
    
    def update_casino_balance(self, balance_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un balance de casino existente"""
        df = pd.read_csv(CASINO_BALANCES_CSV, dtype=str)
        
        idx = df.index[df['id'] == str(balance_id)]
        
        if len(idx) == 0:
            return None
        
        i = idx[0]
        
        # Actualizar campos permitidos
        allowed_fields = [
            'in_total', 'out_total', 'jackpot_total', 'billetero_total',
            'utilidad_total', 'generated_at', 'generated_by', 'locked'
        ]
        
        for field, value in cambios.items():
            if field in allowed_fields:
                df.at[i, field] = str(value)
        
        df.to_csv(CASINO_BALANCES_CSV, index=False)
        
        return self.obtener_casino_balance_por_id(balance_id)
    
    def lock_casino_balance(self, balance_id: int, actor: str, clock) -> bool:
        """Bloquea un balance de casino"""
        df = pd.read_csv(CASINO_BALANCES_CSV, dtype=str)
        
        idx = df.index[df['id'] == str(balance_id)]
        
        if len(idx) == 0:
            return False
        
        i = idx[0]
        df.at[i, 'locked'] = 'True'
        df.at[i, 'generated_by'] = actor
        df.at[i, 'generated_at'] = clock().strftime("%Y-%m-%d %H:%M:%S")
        
        df.to_csv(CASINO_BALANCES_CSV, index=False)
        return True
    
    def _next_casino_balance_id(self) -> int:
        """Calcula el siguiente ID para casino_balances"""
        df = pd.read_csv(CASINO_BALANCES_CSV, dtype=str)
        
        if df.empty:
            return 1
        
        ids = [int(x) for x in df['id'].dropna() if str(x).strip() != '']
        return (max(ids) + 1) if ids else 1
    
    def _normalize_casino_balance(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza tipos de datos de un balance de casino"""
        try:
            row['id'] = int(row['id'])
        except (ValueError, TypeError):
            row['id'] = None
        
        try:
            row['place_id'] = int(row['place_id'])
        except (ValueError, TypeError):
            row['place_id'] = None
        
        for field in ['in_total', 'out_total', 'jackpot_total', 'billetero_total', 'utilidad_total']:
            try:
                row[field] = float(row.get(field, 0))
            except (ValueError, TypeError):
                row[field] = 0.0
        
        # Normalizar locked a booleano
        locked_val = row.get('locked', 'False')
        if isinstance(locked_val, str):
            row['locked'] = locked_val.lower() == 'true'
        else:
            row['locked'] = bool(locked_val)
        
        return row

