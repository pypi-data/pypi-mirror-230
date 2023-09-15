import subprocess
from ..tg_send import tg_send
import os

current_file_path = os.path.abspath(__file__)
BASE_PATH = os.path.dirname(current_file_path)


class WineHelper:
    def __init__(self):
        pass

    def run_command(self, command):
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                timeout=5,
            )
            return 200, result.stdout.decode()
        except subprocess.TimeoutExpired:
            return 408, "TimeoutExpired"

    def initialize(self, path):
        result = self.run_command(
            f"mt5_path={path} wine python {BASE_PATH}/w_initialize.py"
        )
        return result

    def account_info(self):
        result = self.run_command(f"wine python {BASE_PATH}/w_account_info.py")
        return result

    def login(self, server, login, password):
        print("Connecting to {login} on {server}".format(login=login, server=server))

        result = self.run_command(
            f"SERVER={server} LOGIN={login} PASSWORD={password} wine python {BASE_PATH}/w_connect.py"
        )
        return result

    def get_symbol(self, symbol):
        result = self.run_command(
            f"SYMBOL={symbol} wine python {BASE_PATH}/w_symbol.py"
        )
        return result

    def get_mt5_timeframe(self, timeframe):
        result = self.run_command(
            f"TIMEFRAME={timeframe} wine python {BASE_PATH}/w_timeframe.py"
        )
        return result[1].split("\r")[0]


wine_helper = WineHelper()
# helper.initialize()
# helper.account_info()
# helper.login()
