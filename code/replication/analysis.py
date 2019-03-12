import math
import datetime
import numpy as np
import pandas as pd
from datascience import *
from linearmodels.panel import FamaMacBeth, PanelOLS

# TODO: directly use pandas instead of using datascience wrapper
# TODO: collect garbage (optimize memory)

####### I. Import data #######
headers = ("id", "ticker", "date", "time", "Old", "ClosestNeighbor", "length", "closest1", "closest2")
data = pd.read_csv("../data/simulated_data.txt", names=headers)
data = Table.from_pd(data)

# Quarterly Book Value: Compustat Unrestated Quarterly (TIC: Data Date, ATQ, Unrestated Data Values)
quarterly = Table.read_table("../data/quarterly.csv")
quarterly = quarterly.with_column("atqr_exists", np.isnan(quarterly.column("atqr")))
quarterly = quarterly.where("atqr_exists", False).drop("atqr_exists")
quarterly = quarterly.select("tic","datadate","atqr").relabel("tic", "ticker").relabel("datadate", "date").relabel("atqr","BVal")
quarterly.sort("date")

# Daily Market Cap: Compustat Daily Updates - Security Daily (TIC: CSHOC, CSHTRD, PRCOD, PRCCD, PRCHD?, PRCLD?)
    # CRSP Daily Stock??
daily = Table.read_table("../data/daily.csv") # TODO: Only 2015??
daily = daily.with_column("MCap", daily.column("cshoc") * daily.column("prcod"))
daily = daily.with_column("return", (daily.column("prcod") - daily.column("prccd"))/daily.column("prcod"))
daily = daily.with_column("frac", daily.column("cshtrd")/daily.column("cshoc"))
daily = daily.with_column("volatility", daily.column("prchd") - daily.column("prcld"))
# TODO: ERROR - Data N/A?
daily = daily.with_column("MCap_exists", np.isnan(daily.column("MCap")))
daily = daily.where("MCap_exists", False).drop("MCap_exists")
daily = daily.drop("gvkey", "iid").relabel("datadate", "date").relabel("tic", "ticker")


####### II. Construct individual story factors #######
OLD_THRESHOLD = 0.6
REPRINT_RECOMBINATION_THRESHOLD = 0.8
data = data.with_column("OldNews", data.column("Old") > OLD_THRESHOLD)
data = data.with_column("share_spanned", data.column("ClosestNeighbor") / data.column("Old"))
data = data.with_column("Reprint", data.apply(lambda row: row[9] and row[10] >= REPRINT_RECOMBINATION_THRESHOLD))
data = data.with_column("Recombination", data.apply(lambda row: row[9] and row[10] < REPRINT_RECOMBINATION_THRESHOLD))
data = data.relabel("length", "unique")


####### III. Construct firm factors #######

# main factors
groupCount = data.group(["ticker", "date"])
groupSum = data.group(["ticker", "date"], np.sum)
firms = Table().with_columns("ticker", groupCount.column("ticker"),
                             "date", groupCount.column("date"),
                             "PctOld", groupSum.column("OldNews sum")/groupCount.column("count"),
                             "PctRecombination", groupSum.column("Recombination sum")/groupCount.column("count"),
                             "ExtentOld", groupSum.column("Old sum")/groupCount.column("count"),
                             "ExtentRecombination", (groupSum.column("Old sum")-groupSum.column("ClosestNeighbor sum"))/groupCount.column("count"))

# abnormal factors
avg_unique_data = data.group(["date"], np.average)
def avg_unique(date):
    return avg_unique_data.where("date", date).column("unique average").item(0)
firms = firms.with_columns("log(|S|)", np.log(groupCount.column("count")),
                          "log(avg_unique)", np.log(firms.apply(avg_unique, "date")),
                          "log(avg_unique)^2", np.square(np.log(firms.apply(avg_unique, "date"))))

firms_df = firms.to_df().set_index(['ticker', 'date'])

extentOldModel = PanelOLS(firms_df[["ExtentOld"]], firms_df[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]]).fit()
extentRecombinationModel = PanelOLS(firms_df[["ExtentRecombination"]], firms_df[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]]).fit()

abnPctOld = Table.from_df(firms_df).column("ExtentOld") - Table.from_df(extentOldModel.predict(firms_df[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]])).column("predictions")
abnPctRecombination = Table.from_df(firms_df).column("ExtentOld") - Table.from_df(extentRecombinationModel.predict(firms_df[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]])).column("predictions")

firms = firms.with_columns("AbnPctOld", abnPctOld,
                           "AbnPctRecombination", abnPctRecombination)


####### IV. Regressions #######

def dateSubtract(d, minusDays):
    new_date = datetime.date(d//10000, d//100%100, d%100) - datetime.timedelta(minusDays)
    return new_date.year*10000+new_date.month*100+new_date.day

# TODO: ERROR - Ticker DNE
tickerDNE = []
# """
for ticker in firms.group("ticker").column("ticker"):
    if daily.where("ticker", ticker).num_rows == 0:
        tickerDNE.append(ticker)
# """

dailyAverage = daily.group("date", np.average)

# TODO: how do we calculate 'return'? close-open? percentage or pts?
# assuming: (close - open)/open (%)
# value-weighted..?
def abnRet(row):
    if row[0] in tickerDNE:
        return None
    prevDayAvgReturn = dailyAverage.where("date", dateSubtract(row[1], 1)).column("return average").item(0)
    return daily.where("ticker", row[0]).where("date", row[1]).column("return").item(0) - prevDayAvgReturn

# 'shares turned over' = trading volume?
# assuming: frac for day t+1, avg frac for all firms on day t
def abnVol(row):
    if row[0] in tickerDNE:
        return None
    prevDayAvgFrac = dailyAverage.where("date", dateSubtract(row[1], 1)).column("frac average").item(0)
    return daily.where("ticker", row[0]).where("date", row[1]).column("frac").item(0) - prevDayAvgFrac

firms = firms.with_column("AbnRet", groupCount.apply(abnRet))
firms = firms.with_column("AbnVol", groupCount.apply(abnVol))

# calculate X

def abn_stories(row):
    forFirm = groupCount.where("ticker", row[0])
    oneWeekAgo = dateSubtract(row[1], 5)
    twoMonthsAgo = dateSubtract(row[1], 60)
    pastWeek = np.average(forFirm.where("date", are.between(oneWeekAgo, row[1])).column("count"))
    pastTwoMonths = np.average(forFirm.where("date", are.between(twoMonthsAgo, oneWeekAgo)).column("count"))
    return pastWeek - pastTwoMonths

def m_cap(row):
    return daily.where("ticker", row[0]).where("date", row[1]).column("MCap").item(0)

def recent_quarter_bval(row):
    return quarterly.where("ticker", row[0]).where("date", are.below_or_equal_to(row[1])).sort("date").column("BVal").item(0)

def bm(row):
    return recent_quarter_bval(row)/m_cap(row)

def abn_ret_pweek(row):
    return np.sum(firms.where("ticker", row[0]).where("date", are.between(dateSubtract(row[1], 5), row[1])).column("AbnRet"))

def abn_vol_pweek(row):
    return np.average(firms.where("ticker", row[0]).where("date", are.between(dateSubtract(row[1], 5), row[1])).column("AbnVol"))

# TODO: how do we calculate 'volatility'? 
# assuming: high-low
def abn_volatility_pweek(row):
    prevDaysAvgVolatility = dailyAverage.where("date", are.between(dateSubtract(row[1], 5), row[1])).column("frac volatility").item(0)
    return daily.where("ticker", row[0]).where("date", row[1]).column("volatility").item(0) - prevDayAvgVolatility

# volume = closing * trading vol
def illiq_pweek(row):
    prior_week = daily.where("ticker", row[0]).where("date", are.between(dateSubtract(row[1], 5), row[1]))
    prior_week_illiq = 10e6 * prior_week.column("return") / (prior_week.column("cshtrd") * prior_week.column("prccd"))
    return np.log(np.average(prior_week_illiq))

Stories = groupCount.column("count") # all stories in data are relevant, each row is a story
AbnStories = groupCount.apply(abn_stories)
Terms = groupSum.column("unique sum")/groupCount.column("count")
MCap = groupCount.apply(m_cap)
BM = groupCount.apply(bm)
# TODO: business days?
AbnRetPW = groupCount.apply(abn_ret_pweek)
AbnVolPW = groupCount.apply(abn_vol_pweek)
AbnVolatilityPW = groupCount.apply(abn_volatility_pweek)
IlliqPW = groupCount.apply(illiq_pweek)

firms = firms.with_columns("Stories", Stories,
                           "AbnStories", AbnStories,
                           "Terms", Terms,
                           "MCap", MCap,
                           "BM", BM,
                           "AbnRetPW", AbnRetPW,
                           "AbnVolPW", AbnVolPW,
                           "AbnVolatilityPW", AbnVolatilityPW,
                           "IlliqPW", IlliqPW)

firms = firms.with_column("a", 1)
firms_df = firms.take().to_df().set_index(['ticker', 'date'])

# Regressions for Market Reactions to Old News (pg18) 
    # dependent: Abn___[i,t+1]
    # exogenous: 1, AbnPctOld, Controls
params = ["a", "AbnPctOld", "Stories", "AbnStories", "Terms", "MCap", "BM", "AbnRetPW", "AbnVolPW", "AbnVolatilityPW", "IlliqPW"]
# Do we need to shift AbnRet and AbnVol by a day? Yes.
abnRetModel_OldNews = FamaMacBeth(firms_df[["AbnRet"]][1:], firms_df[params][:-1]).fit('heteroskedastic', 'bartlett')
abnVolModel_OldNews = FamaMacBeth(firms_df[["AbnVol"]][1:], firms_df[params][:-1]).fit('heteroskedastic', 'bartlett')

# Regressions for Market Reactions to Recombinations (pg20)
    # dependent: Abn___[i,t+1]
    # exogenous: 1, AbnPctOld, AbnPctRecombination, Controls
params = ["a", "AbnPctOld", "AbnPctRecombinations", "Stories", "AbnStories", "Terms", "MCap", "BM", "AbnRetPW", "AbnVolPW", "AbnVolatilityPW", "IlliqPW"]
abnRetModel_Recombination = FamaMacBeth(firms_df[["AbnRet"]][1:], firms_df[params][:-1]).fit('heteroskedastic', 'bartlett')
abnVolModel_Recombination = FamaMacBeth(firms_df[["AbnVol"]][1:], firms_df[params][:-1]).fit('heteroskedastic', 'bartlett')

# Regressions for Market Reversal Reactions to Recombinations (pg21)
    # dependent: AbnRet[i,[t+t1,t+t2]]
    # exogenous: 1, AbnPctOld, AbnPctOld*AbnRet, AbnRet, AbnPctRecombination, AbnPctRecombination*AbnRet, Controls
firms = firms.with_columns("AbnPctOld*AbnRet", firms.column("AbnPctOld")*firms.column("AbnRet"),
                           "AbnPctRecombination*AbnRet", firms.column("AbnPctRecombination")*firms.column("AbnRet"))
firms_df = firms.take().to_df().set_index(['ticker', 'date'])
# Typo on pg21, last paragraph?
params = ["a", "AbnPctOld", "AbnPctOld*AbnRet", "AbnRet", "AbnPctRecombination", "AbnPctRecombination*AbnRet", "Stories", "AbnStories", "Terms", "MCap", "BM", "AbnRetPW", "AbnVolPW", "AbnVolatilityPW", "IlliqPW"]
# TODO: Switch this to [t+t1, t+t2] instead of just [t+1]
abnRetModel_Reversal = FamaMacBeth(firms_df[["AbnRet"]][1:], firms_df[params][:-1]).fit('heteroskedastic', 'bartlett')


####### V. Output #######

print(abnRetModel_OldNews.params)
print(abnVolModel_OldNews.params)
print(abnRetModel_Recombination.params)
print(abnVolModel_Recombination.params)
print(abnRetModel_Reversal.params)
