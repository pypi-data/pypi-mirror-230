import os
from mt5connect import Sample_DWX


# from mt5connect import Base, Trader, enums
#

USER = "Demo"
table_name = "RocketTable"


class TestCalculate:
    def __init__(self):
        self.st = Sample_DWX(USER, table_name)
        self.st.init()
        pass

    def test_health(self):
        assert self.st.healthy == True

    def test_open_orders(self):
        orders = self.st.get_all_orders()
        assert len(orders) == 0


TestCalculate().test_health()
TestCalculate().test_open_orders()
