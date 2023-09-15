import pandas as pd


def calculate_equity(trades, data):
    values = []

    for index, trade in trades.iterrows():
        if (
            trade["type"] == "buy"
            or trade["type"] == "sell"
            or trade["type"] == "correction"
        ):
            values.append(
                [
                    trade["deal_time"],
                    trade["symbol"],
                    trade["deal_price"],
                    trade["type"],
                    trade["pnl"],
                    trade["commission"],
                    trade["lots"],
                    trade["comment"],
                ]
            )
        # print(type)

    column_types = {
        "date": str,
        "symbol": str,
        "price": float,
        "type": str,
        "pnl": float,
        "commission": float,
        "lots": float,
        "comment": str,
    }

    trades_df = pd.DataFrame(values, columns=column_types.keys()).astype(column_types)
    trades_df["date"] = pd.to_datetime(trades_df["date"]).dt.floor("Min")
    trades_df["date"] = pd.to_datetime(trades_df["date"], format="%Y.%m.%d %H:%M:%S")
    trades_df.set_index("date", inplace=True)
    trades_df

    price_df = data.copy()

    price_df["date"] = pd.to_datetime(price_df.index)
    filtered_df = price_df[price_df["date"] > "2023-06-30"]
    price_df = filtered_df
    filtered_df

    price_df["position"] = 0
    price_df["price"] = 0
    for index, row in trades_df.iterrows():
        if index in price_df.index:
            trade_type = row["type"]
            volume = row["lots"]
            price_df.loc[index, "position"] += (
                volume if trade_type == "buy" else -volume
            )
            price_df.loc[index, "price"] = row["price"]
            price_df.loc[index, "pnl"] = row["pnl"]
            price_df.loc[index, "commission"] = row["commission"]

    price_df["net_position"] = price_df["position"].cumsum()
    # Identify rows where any column value changes from the previous row
    mask = price_df["net_position"].ne(price_df["net_position"].shift())

    entry_price = 0
    position = 0
    entry_size = 0
    MULTIPLIER = 2
    INITIAL_EQUITY = 5000
    equity = INITIAL_EQUITY
    running_equity = equity
    position = 0
    trades = 0

    _equity = []
    for index, row in price_df.iterrows():
        if index in price_df.index[mask]:
            entry_price = row["price"]

            position += row["position"]
            entry_size = position
            if abs(row["pnl"]) > 0:
                equity = equity + row["pnl"] + row["commission"]
            if trades == 0 and entry_size != 0:
                trades += 1
                trade_start = index

        if entry_size > 0:  # we are long
            pnl = (row["close"] - entry_price) * abs(entry_size) * MULTIPLIER
        else:  # we are short
            pnl = (entry_price - row["close"]) * abs(entry_size) * MULTIPLIER

        running_equity = equity + pnl
        _equity.append(running_equity)
        # price_df.loc[index, "equity"] = running_equity

    price_df["equity"] = _equity

    # Use this to calculate other impacts on equity such as paying market data fees
    others = trades_df[trades_df["price"] == 0]

    price_df["commission"] = 0
    bootstrap = 0
    for index, row in others.iterrows():
        if index in price_df.index:
            price_df.loc[index, "commission"] = row["pnl"]
        else:
            bootstrap += row["pnl"]

    price_df["commission"].iloc[0] = bootstrap
    price_df["equity"] = price_df["equity"] + price_df["commission"].cumsum()

    # Make sure the Buy and Hold starts from when we had our first ever trade
    price_df = price_df[price_df.index > trade_start]

    # Get the Buy And Hold Value
    close = price_df["close"]
    initial_price = close.iloc[0]
    price_df["buy_and_hold"] = (price_df["close"] - initial_price) * 2 + INITIAL_EQUITY

    # Combine the values we need
    equity = pd.DataFrame(
        price_df[["buy_and_hold", "equity"]],
        columns=["buy_and_hold", "equity"],
    )
    return equity


# data = pd.read_parquet("./data/Bilel_MNQU23-M1.parquet")
# trades = pd.read_parquet("./data/Bilel_trades.parquet")
#
#
# equity = calculate_equity(trades, data)
