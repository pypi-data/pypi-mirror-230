import os
import json
import shutil
from time import sleep
import pandas as pd
from datetime import datetime, timedelta

from ..DB import DB
from ..tg_send import tg_send
from .dwx_client import dwx_client
from ..Monitoring import Monitoring
from .equity.s3 import upload_files_to_s3
from ..wine_helpers.WineHelper import wine_helper
from .equity.calculate_equity import calculate_equity
from .equity.load_and_concat_data import load_and_concat_data


class Base:
    def __init__(
        self,
        USER,
        conf=None,
        use_dynamo=True,
        table_name=None,
        region_name="us-east-2",
        inform=True,
        should_update_equity=False,
        min_days=30,
        is_mt5=True,
    ):
        self.reset_data_folder()
        self.should_update_equity = should_update_equity
        self.data = {}
        self.inform = inform
        self.wine_helper = wine_helper
        self.is_mt5 = is_mt5

        if conf is not None:
            self.conf = conf
        if use_dynamo:
            self.conf = DB(table_name, region_name).get_DB_settings_for_user(USER)
        if self.conf is None:
            raise ValueError("Could not load a proper conf file")

        self.assets = self.conf["assets"]
        self.min_days = min_days

    def init(self):
        if self.is_mt5:
            self.healthy = self.check_health()
        else:
            self.healthy = True

        if self.healthy:
            self.dwx = dwx_client(
                self,
                self.conf["MT5_directory_path"],
                0.005,  # sleep_delay
                10,  # max_retry_command_seconds
                verbose=False,
            )
            self.reset_dwx()

            self.connect_to_terminal()
            if self.is_mt5:
                self.get_contracts()

            self.request_historical_ohlc(days=self.min_days)

    def reset_data_folder(self):
        folder_path = "./data"  # Replace with the actual path of the folder

        # Remove the folder and its contents
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            # print(f"Folder '{folder_path}' and its contents have been removed.")

        # Recreate the folder
        os.makedirs(folder_path)
        # print(f"Folder '{folder_path}' has been recreated.")

    def reset_dwx(self):
        self.dwx.subscribe_symbols_bar_data([])

    def connect_to_terminal(self):
        self.dwx.start()
        # Second sleep is needed to give it time to reload the keys
        sleep(1)

        self.completed_initial_load = False

    def check_health(self):
        monitor = Monitoring(self.conf)
        health = monitor.check_health()

        if not health["ea_trade_allowed"]:
            print("EA Trade is not allowed")
            tg_send("ERROR: EA Trade is not allowed", conf)
            return False

        if not health["dwx_attached"]:
            print("DWX is not attached to chart")
            tg_send("ERROR: DWX is not attached", conf)
            return False

        return True

    # ===================================================================== #
    #                            Event Methods                           #
    # ===================================================================== #
    def request_historic_trades(self):
        if self.healthy:
            self.dwx.get_historic_trades(1000)
        else:
            print("System is not in healthy state")

    def subscribe_to_contracts_tick(self):
        print(self.contracts)
        print([sym[0] for sym in self.contracts])
        if self.healthy:
            self.dwx.subscribe_symbols([sym[0] for sym in self.contracts])
        else:
            print("System is not in healthy state")

    def subscribe_to_contracts_ohlc(self):
        if self.healthy:
            self.dwx.subscribe_symbols_bar_data(self.contracts)
        else:
            print("System is not in healthy state")

    # ===================================================================== #
    #                            Contract Methods                           #
    # ===================================================================== #

    def read_file(self, file):
        with open(file, "r") as file:
            return json.load(file)

    def get_contract_for_symbol(self, symbol):
        response = wine_helper.get_symbol(symbol)
        if response[0] == 200:
            data = self.read_file("symbol.json")
            return data["name"]

    def get_contracts(self):
        contracts = []

        for asset in self.conf["assets"]:
            response = wine_helper.get_symbol(asset["title"])
            if response[0] == 200:
                data = self.read_file("symbol.json")
                timeframe = self.wine_helper.get_mt5_timeframe(asset["timeframe"])
                contracts.append([data["name"], timeframe])

        self.contracts = contracts
        return contracts

    # ===================================================================== #
    #                              Data Methods                             #
    # ===================================================================== #
    def log(self, msg):
        print(msg)
        tg_send(msg, self.conf)

    def on_message(self, message):
        if message["type"] == "ERROR":
            msg = (
                message["type"],
                "|",
                message["error_type"],
                "|",
                message["description"],
            )
            if self.inform:
                self.log(msg)
        elif message["type"] == "INFO":
            print(message["type"], "|", message["message"])

    # ===================================================================== #
    #                              OHLC Methods                             #
    # ===================================================================== #
    def request_historical_ohlc(self, days=30):
        for asset in self.contracts:
            self.request_single_historical_ohlc(asset, days=days)

    def request_single_historical_ohlc(self, asset, days=30):
        print(days)
        end = datetime.now()
        end = end + timedelta(days=1)  # last 30 days
        start = end - timedelta(days=days + 1)  # last 30 days
        self.dwx.get_historic_data(
            asset[0],
            asset[1],
            start.timestamp(),
            end.timestamp(),
        )

    # ===================================================================== #
    #                              TRADE Methods                            #
    # ===================================================================== #
    def on_order_event(self):
        self.dwx.open_orders

    # ===================================================================== #
    #                              Storage Methods                            #
    # ===================================================================== #
    def on_historic_trades(self):
        print("On Historic Trades")
        trades = self.dwx.historic_trades.copy()
        trades = pd.DataFrame.from_dict(trades, orient="index")
        user = self.conf["user"]
        trades.to_parquet(f"./data/{user}_trades.parquet")
        self.historical_trades = trades
        self.event_historic_trades()

    def on_historic_data(self, symbol, time_frame, data):
        print("HIST DATA | ", symbol, time_frame, f"{datetime.now()}")

        data = pd.DataFrame.from_dict(data, orient="index")
        data.index = pd.to_datetime(data.index, format="%Y.%m.%d %H:%M")
        user = self.conf["user"]
        DATA_FILE = f"data/{user}_{symbol}-{time_frame}.parquet"

        # Execution methods
        load_and_concat_data(data, DATA_FILE)
        self.data[f"{symbol}-{time_frame}"] = pd.read_parquet(DATA_FILE)

        print("Historical Data loaded and saved")

    def on_bar_data(
        self, symbol, timeframe, time, open_price, high, low, close_price, tick_volume
    ):
        print("==================================")
        print("NEW BAR | ", symbol, timeframe, datetime.utcnow(), time)
        name = f"{symbol}-{timeframe}"

        if name in self.data.keys():
            newdf = pd.DataFrame(
                {
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": close_price,
                    "tick_volume": tick_volume,
                },
                index=[time],
            )

            newdf.index = pd.to_datetime(newdf.index, format="%Y.%m.%d %H:%M")

            # Concatenate the dataframes
            df = pd.concat([self.data[name], newdf])
            duplicated_index = df.index.duplicated(keep="last")
            df = df[~duplicated_index]
            self.data[name] = df

            # save the dataframe
            user = self.conf["user"]
            DATA_FILE = f"data/{user}_{symbol}-{timeframe}.parquet"
            self.data[name].to_parquet(DATA_FILE, index=True)

            # Execute the user specified function
            self.event_new_bar(symbol, timeframe, df)

            if self.should_update_equity:
                self.update_equity()
        else:
            print(f"{name} not in self.data.keys()")

    def on_tick(self, symbol, bid, ask):
        now = datetime.utcnow()

    # ===================================================================== #
    #                              Equity Related Methods                   #
    # ===================================================================== #
    def update_equity(self):
        print("updating equity")
        user = self.conf["user"]
        for asset in self.contracts:
            trades = pd.read_parquet(f"./data/{user}_trades.parquet")
            data = pd.read_parquet(f"./data/{user}_{asset[0]}-{asset[1]}.parquet")
            equity = calculate_equity(trades, data)
            equity.to_parquet(f"./data/{user}_{asset[0]}-{asset[1]}_equity.parquet")
        upload_files_to_s3()

    # ===================================================================== #
    #                              Methods to override                            #
    # ===================================================================== #
    def event_historic_trades(self):
        print("Historic Trades fetched")
        print(self.historical_trades)

    def event_new_bar(self):
        print("New Bar Data fetched")
