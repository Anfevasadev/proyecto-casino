import csv
import os

class CuadreMaquinaRepo:

    def __init__(self):
        base = os.path.dirname(__file__)
        self.path = os.path.join(base, "..", "..", "data", "cuadre_maquina.csv")
        self.path = os.path.abspath(self.path)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "maquina_id","fecha_inicio","fecha_fin",
                    "total_in","total_out","total_jackpot",
                    "total_billetero","utilidad"
                ])

    def save(self, row: dict):
        with open(self.path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                row["maquina_id"],
                row["fecha_inicio"],
                row["fecha_fin"],
                row["total_in"],
                row["total_out"],
                row["total_jackpot"],
                row["total_billetero"],
                row["utilidad"]
            ])
