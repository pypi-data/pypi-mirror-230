import os
import pandas as pd


def load_and_concat_data(dataframe, filename):
    # print()
    # print(filename)
    # print()
    if os.path.exists(filename):
        # Load the existing data from the parquet file
        existing_data = pd.read_parquet(filename)

        # Concatenate the existing data with the new dataframe, removing duplicates
        concatenated_data = pd.concat([existing_data, dataframe])

        # Check for duplicate index values
        duplicated_index = concatenated_data.index.duplicated(keep="last")

        # Drop duplicate rows based on the index
        df_no_duplicates = concatenated_data[~duplicated_index]

        # Save the concatenated data back to the parquet file
        df_no_duplicates.to_parquet(filename, index=True)

        # print(existing_data)
        # print(concatenated_data)
        # print(df_no_duplicates)
        # print(dataframe)
    else:
        # Save the dataframe as a new parquet file
        dataframe.to_parquet(filename, index=True)
