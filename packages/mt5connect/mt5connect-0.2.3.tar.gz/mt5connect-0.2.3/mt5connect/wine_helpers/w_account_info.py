import MetaTrader5 as mt5
from w_convert_tojson import convert_tojson


if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

convert_tojson(mt5.account_info(), "account_info.json")
