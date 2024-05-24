import os
import uuid

import pandas as pd


def load_csv(ml_params_fname):
    # Open input params file
    with open(ml_params_fname) as f:
        content = f.read()

    # Change separator
    uniq_fname = "/tmp/" + str(uuid.uuid4().hex)

    content = content.replace(" ", "")

    # Save temp.csv file with correct sep
    with open(uniq_fname, "w") as f:
        f.write(content)

    df = pd.read_csv(uniq_fname)

    # Delete temp file
    os.remove(uniq_fname)

    return df
