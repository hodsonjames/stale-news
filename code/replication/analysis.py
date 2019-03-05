import numpy as np
import pandas as pd
from linearmodels.panel import FamaMacBeth # FamaMacBeth(dependent, exogenous)

# TODO: collect garbage (optimize memory)

####### I. Import data #######
headers = ("id", "ticker", "date", "time", "Old", "ClosestNeighbor", "length", "closest1", "closest2")
data = pd.read_csv("../data/simulated_data.txt", names=headers)

def format_date(row):
    s = str(row["date"])
    return pd.to_datetime(s[:4] + "-" + s[4:6] + "-" + s[6:])
data["date"] = data.apply(format_date, axis=1)


####### II. Construct individual story factors #######
OLD_THRESHOLD = 0.6
REPRINT_RECOMBINATION_THRESHOLD = 0.8
data["OldNews"] = data["Old"] > OLD_THRESHOLD
data["share_spanned"] = data["ClosestNeighbor"] / data["Old"]
data["Reprint"] = data.apply(lambda row: row["share_spanned"] >= REPRINT_RECOMBINATION_THRESHOLD if row["OldNews"] else False, axis=1) # 4
data["Recombination"] = data.apply(lambda row: row["share_spanned"] < REPRINT_RECOMBINATION_THRESHOLD if row["OldNews"] else False, axis=1) # 5 
data["unique"] = data.apply(lambda row: (1 - row["Old"])*row["length"], axis=1) # TODO: make sure this is correct


####### III. Construct firm factors #######

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

This is also Fama-MacBeth, right?
"""
firms["log(|S|)"] = np.log(firms[["|S|"]])
firms["log(avg_unique)"] = np.log(firms[["avg_unique"]]) # ERROR: What do we do about 0 values?
firms["log(avg_unique)^2"] = np.square(np.log(firms[["avg_unique"]]))

extentOldModel = FamaMacBeth(firms[["ExtentOld"]], firms[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]]).fit('heteroskedastic', 'bartlett')
firms["abnPctOld"] = firms[["ExtentOld"]] - extentOldModel.predict(firms[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]])

extentRecombinationModel = FamaMacBeth(firms[["ExtentRecombination"]], firms[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]]).fit('heteroskedastic', 'bartlett')
firms["abnPctRecombination"] = firms[["ExtentRecombination"]] - extentOldModel.predict(firms[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]])


####### IV. Regressions #######

# TODO: Calculate full data, import (filtered to necessary) data
# AbnRet[i,t+1]
# AbnVol[i,t+1]
# Controls:
"""
Stories: |S| (relevance..? is that 1-old)
AbnStories: calculated    # What does average stories mean? (per day?)
Terms: avg_unique
MCap: FROM DATA
BM: FROM DATA
AbnRet: calculated
AbnVol: calculated
Illiq: calculated
"""

# Regressions for Market Reactions to Old News (pg18) 
    # dependent: Abn___[i,t+1]
    # exogenous: 1, AbnPctOld, Controls
abnRetModel_OldNews = FamaMacBeth().fit('heteroskedastic', 'bartlett') # 8
abnVolModel_OldNews = FamaMacBeth().fit('heteroskedastic', 'bartlett') # 9

# Regressions for Market Reactions to Recombinations (pg20)
    # dependent: Abn___[i,t+1]
    # exogenous: 1, AbnPctOld, AbnPctRecombination, Controls
abnRetModel_Recombination = FamaMacBeth().fit('heteroskedastic', 'bartlett') # 10
abnVolModel_Recombination = FamaMacBeth().fit('heteroskedastic', 'bartlett') # 11

# Regressions for Market Reversal Reactions to Recombinations (pg21)
    # dependent: AbnRet[i,[t+t1,t+t2]]
    # exogenous: 1, AbnPctOld, AbnPctOld*AbnRet, AbnRet, AbnPctRecombination, AbnPctRecombination*AbnRet, Controls
abnRetModel_Reversal = FamaMacBeth().fit('heteroskedastic', 'bartlett') # 12


####### V. Output #######

print(abnRetModel_OldNews)
print(abnVolModel_OldNews)
print(abnRetModel_Recombination)
print(abnVolModel_Recombination)
print(abnRetModel_Reversal)
