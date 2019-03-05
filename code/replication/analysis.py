import numpy as np
import pandas as pd
from linearmodels.panel import FamaMacBeth # FamaMacBeth(dependent, exogenous)

##### I. Import data #####
headers = ("id", "ticker", "date", "time", "Old", "ClosestNeighbor", "length", "closest1", "closest2")
data = pd.read_csv("../data/simulated_data.txt", names=headers)

def format_date(row):
    s = str(row["date"])
    return pd.to_datetime(s[:4] + "-" + s[4:6] + "-" + s[6:])
data["date"] = data.apply(format_date, axis=1)


##### II. Construct individual story factors #####
OLD_THRESHOLD = 0.6
REPRINT_RECOMBINATION_THRESHOLD = 0.8
data["OldNews"] = data["Old"] > OLD_THRESHOLD
data["share_spanned"] = data["ClosestNeighbor"] / data["Old"]
data["Reprint"] = data.apply(lambda row: row["share_spanned"] >= REPRINT_RECOMBINATION_THRESHOLD if row["OldNews"] else False, axis=1) # 4
data["Recombination"] = data.apply(lambda row: row["share_spanned"] < REPRINT_RECOMBINATION_THRESHOLD if row["OldNews"] else False, axis=1) # 5 
data["unique"] = data.apply(lambda row: (1 - row["Old"])*row["length"], axis=1) # TODO: make sure this is correct


##### III. Construct firm factors #####

# pct factors
dataGroup = data.groupby(['ticker', 'date'])
S = dataGroup['id'].count().rename("|S|")
pctOld = (dataGroup['OldNews'].sum()/S).rename("PctOld") # 6
pctRecombination = (dataGroup['Recombination'].sum()/S).rename("PctRecombination") # 7

# extent factors
avgUnique = (dataGroup['unique'].sum()/S).rename("avg_unique")
extentOld = (dataGroup['Old'].sum()/S).rename("ExtentOld") # 16
extentRecombination = (dataGroup['Old'].sum() - dataGroup['ClosestNeighbor'].sum()).rename("ExtentRecombination") # 17

# construction
firms = pd.concat([S, pctOld, pctRecombination, avgUnique, extentOld, extentRecombination], axis=1)

# abnormal factors
"""
Construct abnormal firm factors (pg17):
    residuals from daily cross-sectional regressions of the measure on 
    the log of the number of stories for ﬁrm i on date t, 
    the log of the average number of unique terms per story, and 
    the square of the log average number of unique terms per story
pg17
- (What was pctOld / pctRecombination for?)
- This is also Fama MacBeth, right?
- How to deal with 0 values?

abnPctOld = extentOld - predicted extentOld
"""
firms["log(|S|)"] = np.log(firms[["|S|"]])
firms["log(avg_unique)"] = np.log(firms[["avg_unique"]])
firms["log(avg_unique)^2"] = np.square(np.log(firms[["avg_unique"]]))

# extentOldModel = FamaMacBeth(firms[["date", "ticker", "ExtentOld"]],  firms[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]]).fit('heteroskedastic', 'bartlett')
# print(extentOldModel)
# extentOldPredictions = extentOldModel.predict(np.log(firms[["|S|"]]) + np.log(firms[["avg_unique"]]) + np.square(np.log(firms[["avg_unique"]])))
# firms["abnPctOld"] = firms["ExtentOld"] - extentOldPredictions
"""
firms["abnPctOld"] = firms.apply(lambda row: row["ExtentOld"] - extentOldModel.predict([np.log(row["|S|"]), 
                                                                                        np.log(row["avg_unique"]), 
                                                                                        np.square(np.log(row["avg_unique"]))]
                                                                                        ), axis=1)
"""
# extentRecombinationModel = FamaMacBeth().fit('heteroskedastic', 'bartlett')


##### IV. Regressions #####

# Regression for old news vs. market reaction (8, 9)
# nextDayAbnRetModel = FamaMacBeth(AbtRet, exog)

# Regression for recombination vs. market reaction (10, 11)

# Regression for reversal (12)


##### V. Output #####

print(firms)
