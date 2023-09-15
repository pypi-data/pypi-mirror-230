import os
import MetaTrader5 as mt5
from w_convert_tojson import convert_tojson


# establish MetaTrader 5 connection to a specified trading account
# path = "/home/alpha/workspace/rocket-bot/bot-monitoring/metatrader-instances/AMP-USD"

path = os.getenv("mt5_path")
print(path)
# path = "/home/alpha/workspace/cultivating-alpha/mt5connect/metatrader-instances/AMP-USD/terminal64.exe"

if not mt5.initialize(path):
    # if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())

convert_tojson(mt5.terminal_info(), "terminal_info.json")
