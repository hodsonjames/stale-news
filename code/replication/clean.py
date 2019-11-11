# clean.py
# -------
# Writes new CSVs that only have mutually shared tickers and are sorted by date
import pandas as pd
import numpy as np

# setup databases to read in from
compustat = pd.read_csv("compustat_full.csv", dtype={'rqd': np.object, 'naics': np.object})
crsp = pd.read_csv("crsp_full.csv",  dtype={'VOL': np.object, 'SHROUT': np.object})
news = pd.read_csv("djn_data.csv", dtype={'STORY_LENGTH': np.object})
# Find shared firms between databases
sharedTics = list(set(compustat["tic"].unique().tolist()) & set(crsp["TICKER"].unique().tolist())
                  & set(news["TICKER"].unique().tolist()))
# Keep shared and sort
compustat.dropna(inplace=True)
compustat = compustat.loc[compustat["tic"].isin(sharedTics)]
compustat.sort_values(by=["rdq"], inplace=True)
compustat.to_csv("reduced_compustat_full.csv", index=False)
# Keep shared and sort
crsp.dropna(inplace=True)
crsp = crsp.loc[crsp["TICKER"].isin(sharedTics)]
crsp.sort_values(by=["date"], inplace=True)
crsp.to_csv("reduced_crsp_full.csv", index=False)
# Keep shared
news.dropna(inplace=True)
news = news.loc[news["TICKER"].isin(sharedTics)]
news.to_csv("reduced_djn_data.csv", index=False)
