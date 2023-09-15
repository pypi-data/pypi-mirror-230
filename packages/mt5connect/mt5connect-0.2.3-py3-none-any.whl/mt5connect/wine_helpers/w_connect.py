import MetaTrader5 as mt5
import json
import os

login = os.getenv("LOGIN")
server = os.getenv("SERVER")
password = os.getenv("PASSWORD")

if not mt5.initialize(server=server, login=int(login), password=password):
    print("login failed")
else:
    print(login)
