# back/storage/casino_balance_repo.py
# Repositorio encargado de acceder a la base de datos/CSV para guardar el cuadre general.

from decimal import Decimal
from .machines_repo import MachinesRepo
from .counters_repo import CountersRepo
from ..models.casino_balance import CasinoCuadre

class CasinoBalanceRepo:
    """
    Repositorio encargado de obtener contadores y máquinas,
    y guardar el cuadre consolidado.
    """

    def __init__(self):
        # Repositorio de máquinas
        self.machines_repo = MachinesRepo()
        # Repositorio de contadores (acceso a CSV/BD)
        self.counters_repo = CountersRepo()

    def obtener_maquinas_por_casino(self, casino_id):
        """
        Devuelve todas las máquinas asociadas a un casino.
        """
        return self.machines_repo.get_machines_by_casino(casino_id)

    def obtener_contadores(self, maquina_id, fecha):
        """
        Devuelve los contadores de una máquina en una fecha específica.
        Si no existen datos exactos, la implementación puede aproximar
        al registro más cercano o lanzar error.
        """
        return self.counters_repo.get_counters_by_date(maquina_id, fecha)

    def guardar_cuadre(self, cuadre: CasinoCuadre):
        """
        Guarda el cuadre general en un archivo CSV o en la BD.
        Aquí solo se deja espacio para la implementación.
        """
        # Ejemplo para CSV:
        # with open("cuadres_casino.csv", "a") as file:
        #     file.write(...)
        pass
