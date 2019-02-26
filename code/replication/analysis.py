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
data["Reprint"] = data["share_spanned"] >= REPRINT_RECOMBINATION_THRESHOLD if data["OldNews"] else False
data["Recombination"] = data["share_spanned"] < REPRINT_RECOMBINATION_THRESHOLD if data["OldNews"] else False

# Construct firm factors (6, 7)

# Regression for old news vs. market reaction (8, 9)

# Regression for recombination vs. market reaction (10, 11)

# Regression for reversal (12)

# Output..?
print(data)