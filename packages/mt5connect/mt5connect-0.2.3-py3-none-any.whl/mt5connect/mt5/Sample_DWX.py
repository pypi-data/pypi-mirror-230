from .Base import Base
from .Trader import Trader


class Sample_DWX(Base, Trader):
    def __init__(
        self,
        USER,
        table_name,
        inform=True,
        should_update_equity=False,
        min_days=3,
        is_mt5=True,
    ):
        super().__init__(
            USER,
            inform=inform,
            table_name=table_name,
            use_dynamo=True,
            should_update_equity=should_update_equity,
            min_days=min_days,
            is_mt5=is_mt5,
        )

    # ====================================================== #
    # DWX Client Callbacks                                   #
    # ====================================================== #

    def event_new_bar(self, symbol, timeframe, data):
        print()
        print("New Bar Data fetched")
        print(symbol, timeframe)
        print(data)
