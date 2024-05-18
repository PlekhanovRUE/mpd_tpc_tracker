import os

import pandas as pd


def load_csv(ml_params_fname):
    # Open input params file
    with open(ml_params_fname) as f:
        content = f.read()

    # Change separator
    content = content.replace(" ", "")

    # Save temp.csv file with correct sep
    with open("temp.csv", "w") as f:
        f.write(content)

    df = pd.read_csv("temp.csv")

    # Delete temp file
    os.remove("temp.csv")

    return df
