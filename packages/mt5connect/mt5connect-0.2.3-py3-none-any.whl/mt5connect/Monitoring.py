import os
import json
from datetime import datetime
from .wine_helpers.WineHelper import WineHelper


class Monitoring:
    def __init__(self, conf):
        self.conf = conf
        self.wine_helper = WineHelper()

    # ==================================================================================== #
    #                                Helper Functions                                      #
    # ==================================================================================== #
    def read_file(self, file):
        with open(file, "r") as file:
            return json.load(file)

    def clean_files(self):
        for file in ["account_info.json", "symbol.json", "terminal_info"]:
            if os.path.exists(file):
                os.remove(file)

    # ==================================================================================== #
    #                               MT5 Functions                                          #
    # ==================================================================================== #
    def mt5_login(self):
        server = self.conf["server"]["title"]
        login = self.conf["login"]
        password = self.conf["password"]

        return not self.wine_helper.login(server, login, password)[1] == ""

    def mt5_init(self):
        original_path = self.conf["MT5_directory_path"]
        components = original_path.split("/")
        path = "/".join(components[:-3])
        path = path + "/terminal64.exe"
        print("Initializing MT5 on path: ", path)

        initialized = self.wine_helper.initialize(path)
        print("Initialized: ", initialized)

        if initialized[0] != 200:
            print("Failed to initialize, trying to login")
            self.mt5_login()
            initialized = self.wine_helper.initialize(path)
        return True if initialized[0] == 200 else False

    def mt5_get_account(self):
        account = self.wine_helper.account_info()
        print(account)
        if account[0] == 200:
            return self.read_file("account_info.json")
        else:
            print("Failed to get account")
            return None

    # ==================================================================================== #
    #                               DWX Functions                                          #
    # ==================================================================================== #
    def is_dwx_attached(self):
        print("DWX attached still not implemented")
        return True
        path = self.conf["MT5_directory_path"] + "DWX/Status_Time"
        with open(path, "r") as file:
            now = datetime.utcnow()
            date_format = "%Y.%m.%d %H:%M:%S"
            first_line = file.readline().rstrip("\n")
            # Convert the string to datetime
            date_object = datetime.strptime(first_line, date_format)

            diff = now - date_object
            if diff.seconds > 5:
                return False
            return True

    # ================================================================================ #
    #                                Health Check                                      #
    # ================================================================================ #
    def check_health(self):
        print("Checking the HEALTH")
        status = {}

        # ================================================================================ #
        # Initialize
        # ================================================================================ #
        initialized = self.mt5_init()
        print("Initialized")

        # ================================================================================ #
        # Login
        # ================================================================================ #
        logged_in = self.mt5_login()
        print("Login")

        terminal_info = self.read_file("terminal_info.json")

        status["terminal_info"] = terminal_info
        status["ea_trade_allowed"] = terminal_info["trade_allowed"]
        status["initialized"] = initialized
        status["logged_in"] = logged_in
        status["account_info"] = "Failed to get account info"
        print(logged_in)

        # ================================================================================ #
        # ================================================================================ #
        if logged_in:
            # Get Account Info
            account = self.mt5_get_account()
            status["account_info"] = account
        print("Account")

        # ================================================================================ #
        # Check EA Status
        # ================================================================================ #
        status["dwx_attached"] = self.is_dwx_attached()

        # Remove the created json files
        self.clean_files()

        self.status = status
        return status
