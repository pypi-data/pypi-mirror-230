import os
import json
import MetaTrader5 as mt5
from datetime import datetime, date
from w_convert_tojson import convert_tojson


# Custom JSON encoder that handles datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class Symbol:
    def __init__(self):
        if not mt5.initialize():
            print("Failed to initialize MetaTrader!")
            return None
        pass

    def find_symbols_for_contract(self, contract):
        # Retrieve the CME contract codes from the MetaTrader terminal
        symbols = []
        for symbol in mt5.symbols_get():
            if contract in symbol.name:
                dt = datetime.fromtimestamp(symbol.expiration_time)
                symbols.append(
                    {
                        "name": symbol.name,
                        "expiration_time": dt,
                        "is_active": self.is_datetime_after_today(dt),
                        "contract": symbol,
                    }
                )

        return symbols

    def is_datetime_after_today(self, dt):
        current_date = date.today()
        return dt.date() > current_date

    # ================================================================================ #
    # ================================================================================ #
    def get_active_contract(self, contract):
        contracts = sym.find_symbols_for_contract(contract)
        for contract in contracts:
            if contract["is_active"]:
                return contract["contract"]


SYMBOL = os.getenv("SYMBOL")
sym = Symbol()

data = sym.get_active_contract(SYMBOL)

convert_tojson(data, "symbol.json")
