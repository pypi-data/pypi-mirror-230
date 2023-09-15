import pandas as pd
from time import sleep
from .enums import ErrorCodes


class Trader:
    def __init__(
        self,
    ):
        pass

    def get_positions_by_symbol(self, symbol):
        df = pd.DataFrame.from_dict(self.dwx.open_orders, orient="index")
        if len(df) == 0:
            return df
        df = df[(df["type"] == "buy") | (df["type"] == "sell")]
        return df[df["symbol"] == symbol]

    def get_short_positions(self, symbol=None):
        df = pd.DataFrame.from_dict(self.dwx.open_orders, orient="index")
        if len(df) == 0:
            return df
        df = df[(df["type"] == "sell")]
        if symbol is None:
            return df
        else:
            return df[df["symbol"] == symbol]

    def get_long_positions(self, symbol=None):
        df = pd.DataFrame.from_dict(self.dwx.open_orders, orient="index")
        if len(df) == 0:
            return df
        df = df[(df["type"] == "buy")]
        if symbol is None:
            return df
        else:
            return df[df["symbol"] == symbol]

    def get_all_positions(self):
        df = pd.DataFrame.from_dict(self.dwx.open_orders, orient="index")
        if len(df) == 0:
            return df
        return df[(df["type"] == "buy") | (df["type"] == "sell")]

    def get_all_orders(self):
        df = pd.DataFrame.from_dict(self.dwx.open_orders, orient="index")
        if len(df) == 0:
            return df
        return df[(df["type"] != "buy") & (df["type"] != "sell")]

    def has_position(self, symbol, direction):
        df = pd.DataFrame.from_dict(self.dwx.open_orders, orient="index")
        if len(df) == 0:
            return False
        df = df[(df["symbol"] == symbol) & (df["type"] == direction)]
        return len(df) > 0

    # ======================================================================== #
    #                           Order Cancelling                               #
    # ======================================================================== #
    def cancel_all_pending_orders(self, df=None):
        if df is None:
            df = pd.DataFrame.from_dict(self.dwx.open_orders, orient="index")
            if len(df) == 0:
                return

        df = df[(df["type"] != "sell") & (df["type"] != "buy")]

        if len(df) > 0:
            for magic in df.index:
                self.dwx.close_order(magic)
                sleep(0.1)
        return df

    def cancel_symbol_pending_orders(self, symbol):
        df = pd.DataFrame.from_dict(self.dwx.open_orders, orient="index")
        if len(df) == 0:
            return
        df = df[df["symbol"] == symbol]
        self.cancel_all_pending_orders(df)

    # ======================================================================== #
    #                          Position Closing                                #
    # ======================================================================== #
    def close_position_by_ticket(self, ticket, lots=None):
        self.dwx.close_order(ticket, lots)

    def close_positions_by_symbol(self, symbol, lots=None):
        positions = self.get_positions_by_symbol(symbol)
        for ticket in positions.index:
            self.dwx.close_order(ticket, lots)

    def close_all_positions(self):
        positions = self.get_all_positions()
        for ticket in positions.index:
            self.dwx.close_order(ticket)

    # ======================================================================== #
    #                         Order Modifications                              #
    # ======================================================================== #
    def modify_order(self, ticket, *args):
        self.dwx.modify_order(ticket, *args)

    # ======================================================================== #
    #                         DWX Client Callbacks                             #
    # ======================================================================== #
    def go_long(self, **args):
        self.place_order(order_type="buy", **args)

    def go_short(self, **args):
        self.place_order(order_type="sell", **args)

    def place_limit(self, direction, price=0, **args):
        last = self.dwx.market_data[args["symbol"]]
        error = None
        if direction == "long":
            order_type = "buylimit"
            # Limit Long 'price' cannot be higher than the current bid price
            if last["bid"] < price:
                error = "ERR_1"
        elif direction == "short":
            order_type = "selllimit"
            # Limit Short 'price' cannot be lower than the current ask price
            if last["ask"] > price:
                error = "ERR_2"
        else:
            # Direction must be provided
            error = "ERR_3"

        if price == 0:
            # Price for a Limit order cannot be 0
            error = "ERR_4"

        if error is None:
            return self.place_order(order_type=order_type, price=price, **args)
        else:
            self.log(f"Error {error}: {ErrorCodes[error].value}")
            return error

    def place_stop(self, direction, price=0, **args):
        last = self.dwx.market_data[args["symbol"]]
        error = None
        if direction == "long":
            order_type = "buystop"
            # Stop Long 'price' cannot be lower than the current bid price
            if last["bid"] > price:
                error = "ERR_5"
        elif direction == "short":
            order_type = "sellstop"
            # Stop Short 'price' cannot be higher than the current ask price
            if last["ask"] < price:
                error = "ERR_6"
        else:
            # Direction must be provided
            error = "ERR_3"

        if price == 0:
            # Price for a Limit order cannot be 0
            error = "ERR_4"

        if error is None:
            return self.place_order(order_type=order_type, price=price, **args)
        else:
            self.log(f"Error {error}: {ErrorCodes[error].value}")
            return error

    def place_order(
        self,
        symbol="",
        order_type="",
        lots=1,
        price=0,
        stop_loss=None,
        take_profit=None,
    ):
        return self.dwx.open_order(
            symbol,
            order_type=order_type,
            lots=lots,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    # ====================================================== #
    # DWX Client Callbacks                                   #
    # ====================================================== #
    def trading(self, symbol):
        print("The default trading method")
        return
        # 1. Remove all pending orders
        self.close_pending_orders(symbol)

        # Generate signal
        data = ohlc[-100:]
        ind = don.run(data.open, data.high, data.low, data.close, 33, 1)
        orders = ind.pending_orders
        # =======================

        order = orders[-1]
        if order > 0:
            lots = 1
            if self.has_position(symbol, "sell"):
                lots = 2
            if not self.has_position(symbol, "buy"):
                print("PLACING LONGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                self.dwx.open_order(
                    symbol, order_type="buystop", lots=lots, price=order
                )
        elif order < 0:
            lots = 1
            if self.has_position(symbol, "buy"):
                lots = 2
            if not self.has_position(symbol, "sell"):
                print("GOING SHOOORRTTTTTTTTTTTTTTTTTTTT")
                self.dwx.open_order(
                    symbol, order_type="sellstop", lots=lots, price=math.fabs(order)
                )
        print(orders.index[-1], orders[-1])
        print("==========================")
        print()
        print()
