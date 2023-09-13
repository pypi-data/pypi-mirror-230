import os

import pandas as pd

from .constants import COUNTY_FIELDS, DATABASE_DESTINATION_PATH, DATABASE_SUFFIX

for file in os.listdir(DATABASE_DESTINATION_PATH):
    # if file.split(DATABASE_SUFFIX)[0] not in COUNTY_FIELDS.keys():
    #     continue
    if file.endswith(".feather"):
        df = pd.read_feather(os.path.join(DATABASE_DESTINATION_PATH, file))
        # print(df.head(), end="\n\n")
        print(file)
        print(df.shape, end="\n\n")
        print(df.columns, end="\n\n")
