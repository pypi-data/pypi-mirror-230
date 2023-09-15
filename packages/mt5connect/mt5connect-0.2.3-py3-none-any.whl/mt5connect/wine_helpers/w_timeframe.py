def convert_string_to_mt5_timeframe(timeframe):
    timeframe_mapping = {
        "1min": "M1",
        "2min": "M2",
        "3min": "M3",
        "4min": "M4",
        "5min": "M5",
        "6min": "M6",
        "10min": "M10",
        "12min": "M12",
        "15min": "M15",
        "20min": "M20",
        "30min": "M30",
        "1hr": "H1",
        "2hr": "H2",
        "3hr": "H3",
        "4hr": "H4",
        "6hr": "H6",
        "8hr": "H8",
        "12hr": "H12",
        "1day": "D1",
        "1week": "W1",
        "1mon": "MN1",
    }
    return timeframe_mapping.get(timeframe, None)


# Example usage
import MetaTrader5 as mt5  # Assuming you've imported the MetaTrader5 library
import os

timeframe = os.getenv("TIMEFRAME")
mt5_timeframe = convert_string_to_mt5_timeframe(timeframe)
if mt5_timeframe is not None:
    print(mt5_timeframe)
# else:
#     print(f"{timeframe} is not a supported timeframe.")
