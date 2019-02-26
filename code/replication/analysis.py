import numpy as np
import pandas as pd

# Import data
headers = ("id", "ticker", "date", "time", "Old", "ClosestNeighbor", "length", "closest1", "closest2")
data = pd.read_csv("../data/simulated_data.txt", names=headers)
# TODO: parse datetime better

# Construct individual story factors (4, 5)
OLD_THRESHOLD = 0.6
REPRINT_RECOMBINATION_THRESHOLD = 0.8
data["OldNews"] = data["Old"] > OLD_THRESHOLD
data["share_spanned"] = data["ClosestNeighbor"] / data["Old"]
data["Reprint"] = data.apply(lambda row: row["share_spanned"] >= REPRINT_RECOMBINATION_THRESHOLD if row["OldNews"] else False, axis=1)
data["Recombination"] = data.apply(lambda row: row["share_spanned"] < REPRINT_RECOMBINATION_THRESHOLD if row["OldNews"] else False, axis=1)

# Construct firm factors (6, 7)
dataGroup = data.groupby(['ticker', 'date'])
S = dataGroup['id'].count()
pctOld = (dataGroup['OldNews'].sum()/S).rename("PctOld")
pctRecombination = (dataGroup['Recombination'].sum()/S).rename("PctRecombination")
firms = pd.concat([pctOld, pctRecombination], axis=1)
print(firms)

# Construct abnormal firm factors

# Regression for old news vs. market reaction (8, 9)

# Regression for recombination vs. market reaction (10, 11)

# Regression for reversal (12)

# Output..?
# print(data[["id", "OldNews", "Reprint", "Recombination"]])