import json
import pandas as pd


def convert_tojson(data, file):
    data = data._asdict()
    df = pd.DataFrame(list(data.items()), columns=["property", "value"])
    df.set_index("property", inplace=True)

    val = json.loads(df.to_json())["value"]
    with open(file, "w") as file:
        json.dump(val, file)
