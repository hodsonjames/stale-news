# clean.py
# -------
# Writes new CSVs that only have mutually shared tickers and are sorted by date
import pandas as pd
import numpy as np
import os
import datetime as dt

# setup databases to read in from
compustat = pd.read_csv("compustat_full.csv", dtype={'datadate': np.object, 'naics': np.object})
crsp = pd.read_csv("crsp_full.csv",  dtype={'VOL': np.object, 'SHROUT': np.object})
news = pd.read_csv("djn_data.csv", dtype={'STORY_LENGTH': np.object})
crsp_dates = crsp["date"].unique().tolist()
crsp_dates.sort()
# Find shared firms between databases
sharedTics = list(set(compustat["tic"].unique().tolist()) & set(crsp["TICKER"].unique().tolist())
                  & set(news["TICKER"].unique().tolist()))
# Keep shared and sort
# compustat.dropna(inplace=True)
compustat = compustat.drop_duplicates(subset=['tic', 'datadate'], keep=False)
compustat = compustat.loc[compustat["tic"].isin(sharedTics)]
compustat.sort_values(by=["datadate"], inplace=True)
compustat.to_csv("reduced_compustat_full.csv", index=False)
# Keep shared and sort
# crsp.dropna(inplace=True)
crsp = crsp.drop_duplicates(subset=['TICKER', 'date'], keep=False)
crsp = crsp.loc[crsp["TICKER"].isin(sharedTics)]
crsp.sort_values(by=["date"], inplace=True)
crsp = crsp[['PERMNO', 'date', 'TICKER', 'PRC', 'VOL', 'SHROUT', 'OPENPRC', 'RET', 'vwretx']]  # For code compatibility
crsp.to_csv("reduced_crsp_full.csv", index=False)
# Keep shared
news = news.loc[news["TICKER"].isin(sharedTics)]
news.sort_values(by=["DATE_EST"], inplace=True)
news.to_csv("delete_temp.csv", index=False)
# Move weekend stories to Monday using crsp
crsp_date_index = 0
g = open("reduced_djn_data.csv", "w+")
header = "DATE,STORY_ID,TICKER,STORY_LENGTH,CLOSEST_ID,SECOND_CLOSEST_ID,CLOSEST_SCORE,TOTAL_OVERLAP,IS_OLD,IS_REPRINT,IS_RECOMB\n"
g.write(header)
with open("delete_temp.csv") as f:
    skip = True
    for line in f:
        if skip:
            skip = False
            continue
        # line of: DATE_EST, ... ,IS_RECOMB
        date = dt.datetime.utcfromtimestamp(float(line[:line.index(",")])).strftime("%Y%m%d")
        while date > str(crsp_dates[crsp_date_index]):
            crsp_date_index += 1
        if date < str(crsp_dates[crsp_date_index]):
            g.write(str(crsp_dates[crsp_date_index]) + line[line.index(","):])
        else:
            g.write(date + line[line.index(","):])
g.close()
os.remove("delete_temp.csv")

