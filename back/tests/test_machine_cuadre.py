from datetime import datetime

from back.domain.balances.machine_balance import calcular_cuadre_maquina


def test_calcular_cuadre_maquina_simple():
    """Prueba básica que calcula el cuadre de una máquina usando stubs en memoria."""

    class CountersStub:
        def list_counters(self, machine_id, date_from, date_to, sort_by, ascending, limit):
            # Devuelve dos contadores: inicio y fin del mismo día
            return [
                {
                    "id": "1",
                    "machine_id": machine_id,
                    "at": "2025-11-25 00:00:00",
                    "in_amount": "1000",
                    "out_amount": "200",
                    "jackpot_amount": "10",
                    "billetero_amount": "5",
                    "casino_id": "1",
                },
                {
                    "id": "2",
                    "machine_id": machine_id,
                    "at": "2025-11-25 23:59:59",
                    "in_amount": "1500",
                    "out_amount": "300",
                    "jackpot_amount": "20",
                    "billetero_amount": "7",
                    "casino_id": "1",
                },
            ]

    class MachinesStub:
        def get_by_id(self, machine_id):
            return {"id": machine_id, "denominacion": "1", "estado": "True"}

    class BalancesStub:
        def __init__(self):
            self.saved = None
            self._next = 1

        def get_machine_balance_by_period(self, machine_id, period_start, period_end):
            return None

        def insertar_machine_balance(self, row):
            row = dict(row)
            row["id"] = self._next
            self._next += 1
            self.saved = row
            return row

        def update_machine_balance(self, balance_id, cambios):
            if self.saved and self.saved.get("id") == balance_id:
                self.saved.update(cambios)
            return self.saved


    counters = CountersStub()
    machines = MachinesStub()
    balances = BalancesStub()

    clock = lambda: datetime(2025, 11, 26, 0, 0, 0)

    result = calcular_cuadre_maquina(
        machine_id=1,
        period_start="2025-11-25",
        period_end="2025-11-25",
        counters_repo=counters,
        machines_repo=machines,
        balances_repo=balances,
        clock=clock,
        actor="tester",
        persist=True,
        lock=False,
    )

    # Diferencias: in 500, out 100, jackpot 10, billetero 2
    assert result["in_total"] == 500.0
    assert result["out_total"] == 100.0
    assert result["jackpot_total"] == 10.0
    assert result["billetero_total"] == 2.0
    # Utilidad = IN - (OUT + JACKPOT) = 500 - (100 + 10) = 390
    assert result["utilidad_total"] == 390.0
    assert result["machine_id"] == 1
    assert "id" in result
