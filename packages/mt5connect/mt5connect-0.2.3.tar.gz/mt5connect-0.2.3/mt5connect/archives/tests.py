from lib.mt5 import Connect
import os
from time import sleep

account = os.environ.get("ACCOUNT") or "demo"
config = f"{os.getcwd()}/config.json"

# |%%--%%| <ArujImm4JZ|d9x16De3lW>

if Connect(config=config, account=account) == 200:
    print("Connected")
else:
    print(f"Failed to connect to MT5 on account {account}")


# |%%--%%| <d9x16De3lW|qT6WzB4Q7b>
from lib.mt5 import Trader
from strategies.S_bilel import BilelStrategy

trader = BilelStrategy(config=config, account=account)


from datetime import datetime, timedelta

# request historic data:
end = datetime.now()
start = end - timedelta(days=30)  # last 30 days
# trader.dwx.get_historic_data("EURUSD", "M1", start.timestamp(), end.timestamp())
trader.dwx.get_historic_data("MNQM23", "M1", start.timestamp(), end.timestamp())
trader.dwx.get_historic_data("MNQM23", "M3", start.timestamp(), end.timestamp())
trader.dwx.get_historic_data("MYMM23", "M1", start.timestamp(), end.timestamp())
trader.dwx.get_historic_data("MYMM23", "M3", start.timestamp(), end.timestamp())
trader.dwx.get_historic_data("MESM23", "M1", start.timestamp(), end.timestamp())
trader.dwx.get_historic_data("MESM23", "M3", start.timestamp(), end.timestamp())
# trader.data["MNQM23"]
# trader.data["MYMM23"]
# trader.data["MESM23"]


# while trader.dwx.ACTIVE:
#     sleep(1)
multiplier = {
    "MNQM23-M1": 2,
    "MNQM23-M3": 2,
    "MYMM23-M1": 0.5,
    "MYMM23-M3": 0.5,
    "MESM23-M1": 5,
    "MESM23-M3": 5,
}


# |%%--%%| <qT6WzB4Q7b|OLLcWWK70c>
import numpy as np
import pandas as pd
from strategies.S_don import don
from Simulator import Simulator


for key in trader.data:
    print(key)
    print(multiplier[key])


data = trader.data["MYMM23-M1"]
# data = trader.data["MESM23"]
# data = trader.data["MNQM23"]
data

donchians = [21, 33, 55, 89]
offsets = [1, 8, 17]

df = pd.DataFrame()

for key in trader.data:
    print(key)
    data = trader.data[key]
    sim = Simulator(data, "M1")

    for donchian in donchians:
        for offset in offsets:
            Don = don.run(data.open, data.high, data.low, data.close, donchian, offset)

            (pf, pf_all) = sim.simulate(
                init_cash=10000,
                size=1,
                multiplier=multiplier[key],
                long_entries=Don.entry,
                long_exits=Don.exit,
                short_entries=Don.exit,
                short_exits=Don.entry,
                price=np.abs(Don.pending_orders),
                fixed_fees=0.6,
                freq="M1",
                # slippage=0.004,
            )
            stats = pf_all.stats(settings=dict(risk_free=0.004))
            newdf = pd.DataFrame(
                {
                    "key": key,
                    "value": stats["End Value"],
                    "donchian": donchian,
                    "offset": offset,
                    "trades": stats["Total Trades"],
                },
                index=[0],
            )
            df = pd.concat([df, newdf])

# |%%--%%| <OLLcWWK70c|sVqyFmxqsf>

df.to_csv("simulations.csv", index=False)

df = df.sort_values(by="value", ascending=False)
df
MES = pd.concat([df[df["key"] == "MESM23-M3"], df[df["key"] == "MESM23-M1"]])
MNQ = pd.concat([df[df["key"] == "MNQM23-M3"], df[df["key"] == "MNQM23-M1"]])
MYM = pd.concat([df[df["key"] == "MYMM23-M3"], df[df["key"] == "MYMM23-M1"]])
MES
MNQ
MYM

# |%%--%%| <sVqyFmxqsf|w62YdB6Tip>

from strategies.S_don import don
from Simulator import Simulator
import numpy as np

data = trader.data["MYMM23-M3"]
Don = don.run(data.open, data.high, data.low, data.close, 89, 1)
key = "MYMM23-M3"
sim = Simulator(data, "M3")

(pf, pf_all) = sim.simulate(
    init_cash=10000,
    size=1,
    multiplier=multiplier[key],
    long_entries=Don.entry,
    long_exits=Don.exit,
    short_entries=Don.exit,
    short_exits=Don.entry,
    price=np.abs(Don.pending_orders),
    fixed_fees=0.6,
    # slippage=0.004,
)
pf_all.stats()

# |%%--%%| <w62YdB6Tip|OCqBuZz4DD>
trades = pf_all.trades.records_readable
trades.drop(
    columns=[
        # "Size",
        "Position Id",
        "Status",
        # "Entry Fees",
        # "Exit Fees",
        "Return",
        "Exit Order Id",
        "Exit Trade Id",
        "Column",
        "Entry Order Id",
    ],
    inplace=True,
)
trades.set_index("Entry Index", inplace=True)
trades["Equity"] = trades["PnL"].cumsum()
trades["Equity"].plot()
plt.show()

# |%%--%%| <OCqBuZz4DD|P6s403spns>

import pandas as pd

df = pd.read_csv("simulations.csv")
df
MES = pd.concat([df[df["key"] == "MESM23-M3"], df[df["key"] == "MESM23-M1"]])
MNQ = pd.concat([df[df["key"] == "MNQM23-M3"], df[df["key"] == "MNQM23-M1"]])
MYM = pd.concat([df[df["key"] == "MYMM23-M3"], df[df["key"] == "MYMM23-M1"]])
MES
MYM
MNQ
