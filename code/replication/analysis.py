import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS, FamaMacBeth
import statsmodels.api as sm
import time

"""
CRSP Daily Stock
https://wrds-web.wharton.upenn.edu/wrds/ds/crsp/stock_a/dsf.cfm?navId=128
2014-01-01 to 2015-12-31
sim_tickers.txt
Ticker, Price, Return without Dividends, Share Volume, Number of Shares Outstanding

Computstat Unrestated Quarterly
https://wrds-web.wharton.upenn.edu/wrds/ds/comph/urq/indexus.cfm?navId=93
2014 to 2015
Entire Database
Data Date, Report Date of Qtly Earnings, Unrestated Data Values, ATQ - Assets - Total - Qtly
"""

OLD_THRESHOLD = 0.6
REPRINT_RECOMBINATION_THRESHOLD = 0.8

daily_mcap = lambda row: row["price"] * row["outstanding"]
daily_turnover = lambda row: row["volume"] / (row["outstanding"] * 1000)

simulated_oldnews = lambda row: row["Old"] > OLD_THRESHOLD
simulated_span = lambda row: row["ClosestNeighbor"] / row["Old"]
simulated_reprint = lambda row: row["OldNews"] and row["span"] >= REPRINT_RECOMBINATION_THRESHOLD
simulated_recombination = lambda row: row["OldNews"] and row["span"] < REPRINT_RECOMBINATION_THRESHOLD

time_start = time.time()

### Daily ###
# PERMNO, date, TICKER, PRC, VOL, SHROUT, RETX
# date, ticker, price, volume, oustanding, return, mcap, turnover
data_daily = pd.read_csv("../data/data_daily.csv")
print("Read " + str(len(data_daily.values)) + " rows from daily data.")
daily_dates = list(set(data_daily["date"]))
print("\tFound " + str(len(daily_dates)) + " unique dates from daily data.")
data_daily = data_daily.query("RETX != 'C' & RETX != 'B'")
print("\tRemoved rows with weird RETX values. " + str(len(data_daily.values)) + " rows remain.")
data_daily["RETX"] = data_daily["RETX"].astype("float64")
# Filter and add factors
data_daily = data_daily.drop(["PERMNO"], axis=1)
data_daily = data_daily.rename(index=str, columns={"TICKER":"ticker", "OPENPRC":"price", "VOL":"volume", "SHROUT":"outstanding", "RETX":"return"})
data_daily["mcap"] = data_daily.apply(daily_mcap, axis=1)
data_daily["turnover"] = data_daily.apply(daily_turnover, axis=1)
# data_daily = data_daily.set_index(['ticker', 'date'])

### Quarterly ###
# gvkey, tic, datadate, fqtr, qtryr, rdq, atqr
# date, ticker, assets
data_quarterly = pd.read_csv("../data/data_quarterly.csv").dropna() # drop rows with null values
print("Read " + str(len(data_quarterly.values)) + " non-empty rows from quarterly data.")
# alternatively, forward-fill
# Filter and add factors
# data_quarterly = data_quarterly.drop(["gvkey", "fqtr", "qtryr", "datadate"], axis=1)
# data_quarterly = data_quarterly.rename(index=str, columns={"tic":"ticker", "rdq":"date", "atqr":"assets"})
data_quarterly = data_quarterly.drop(["gvkey", "fqtr", "qtryr", "rdq"], axis=1)
data_quarterly = data_quarterly.rename(index=str, columns={"tic":"ticker", "datadate":"date", "atqr":"assets"})
data_quarterly["date"] = data_quarterly["date"].astype("int64")
# data_quarterly = data_quarterly.set_index(['ticker'])
data_quarterly = data_quarterly.sort_values("date", ascending=False)

### Simulated ###
# id,ticker,date,time,Old,ClosestNeighbor,length,closest1,closest2
# id,ticker,date,time,Old,ClosestNeighbor,length,closest1,closest2,OldNews,span,Reprint,Recombination
data_simulated = pd.read_csv("../data/data_simulated.csv")
print("Read " + str(len(data_simulated.values)) + " rows from simulated data.")
print("\tFound " + str(len(set(data_simulated["ticker"]))) + " unique tickers from simulated data.")
# Discard values which do not exist in Daily, Quarterly
daily_tickers = set(data_daily["ticker"])
data_simulated = data_simulated[data_simulated.ticker.isin(daily_tickers)]
quarterly_tickers = set(data_quarterly["ticker"])
data_simulated = data_simulated[data_simulated.ticker.isin(quarterly_tickers)]
print("\tDiscarded tickers not found in daily/quarterly. " + str(len(set(data_simulated["ticker"]))) + " unique tickers remain.")
# Filter and add factors
data_simulated["OldNews"] = data_simulated.apply(simulated_oldnews, axis=1)
data_simulated["span"] = data_simulated.apply(simulated_span, axis=1)
data_simulated["Reprint"] = data_simulated.apply(simulated_reprint, axis=1)
data_simulated["Recombination"] = data_simulated.apply(simulated_recombination, axis=1)

time_end = time.time()
print("Imported data in " + str(round(time_end - time_start, 2)) + " seconds.")

################################################################

time_start = time.time()

data_split = data_simulated.groupby(['ticker', 'date'])
data_split_agg = data_split.agg({
    "ticker": ["count"],
    "Old": ["sum"],
    "ClosestNeighbor": ["sum"],
    "OldNews": ["sum"],
    "Recombination": ["sum"],
    "length": ["mean"]
})

firms_pctold = lambda row: row["OldNews"]["sum"] / row["ticker"]["count"]
firms_pctrecombination = lambda row: row["Recombination"]["sum"] / row["ticker"]["count"]
firms_extentold = lambda row: row["Old"]["sum"] / row["ticker"]["count"]
firms_extentrecombination = lambda row: row["ExtentOld"] - row["ClosestNeighbor"]["sum"] / row["ticker"]["count"]

data_firms = data_split_agg
data_firms["PctOld"] = data_firms.apply(firms_pctold, axis=1)
data_firms["PctRecombination"] = data_firms.apply(firms_pctrecombination, axis=1)
data_firms["ExtentOld"] = data_firms.apply(firms_extentold, axis=1)
data_firms["ExtentRecombination"] = data_firms.apply(firms_extentrecombination, axis=1)
data_firms = data_firms.drop(["Old", "ClosestNeighbor", "OldNews", "Recombination"], axis=1)

# Abnormal Factors
firms_logsize = lambda row: np.log(row["ticker"]["count"])
firms_logavgunique = lambda row: np.log(row["length"]["mean"])
firms_logavguniquesq = lambda row: np.square(row["log(avg_unique)"])

data_firms["log(|S|)"] = data_firms.apply(firms_logsize, axis=1)
data_firms["log(avg_unique)"] = data_firms.apply(firms_logavgunique, axis=1)
data_firms["log(avg_unique)^2"] = data_firms.apply(firms_logavguniquesq, axis=1)
# data_firms = data_firms.drop(["ticker", "length"], axis=1)

model_extentOld = PanelOLS(data_firms["ExtentOld"], sm.add_constant(data_firms[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]])).fit()
model_extentRecombination = PanelOLS(data_firms[["ExtentRecombination"]], sm.add_constant(data_firms[["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"]])).fit()

data_firms.columns = data_firms.columns.droplevel(1)

data_firms = pd.concat([data_firms, model_extentOld.resids.rename("AbnPctOld"), model_extentRecombination.resids.rename("AbnPctRecombination")], axis=1)
data_firms = data_firms.drop(["log(|S|)", "log(avg_unique)", "log(avg_unique)^2"], axis=1)

data_firms = data_firms.rename(index=str, columns={"ticker":"count"})

# data_split.get_group('??')

time_end = time.time()
print("Created firm factors in " + str(round(time_end - time_start, 2)) + " seconds.")

################################################################

daily_dates.sort()

def date_shift(date, shift):
    assert date in daily_dates
    return daily_dates[daily_dates.index(date)+shift]

def query(db, q, val):
    result = db.query(q)
    if len(result) == 0:
        return NO_RESULT
    return result[val].values[0]

NO_RESULT = 0 #np.nan
DEBUG = True

time_start = time.time()

# DAILY & DAY CALCULATIONS
# Day: ValueWeightedReturn, ValueWeightedTurnover
# Daily: date, ticker, price, volume, oustanding, return, mcap, turnover,
#        WeightedReturn, WeightedTurnover, AbnRet, AbnVol

daily_wr = lambda row: row["mcap"] * row["return"]
daily_wt = lambda row: row["mcap"] * row["turnover"]
data_daily["WeightedReturn"] = data_daily.apply(daily_wr, axis=1)
data_daily["WeightedTurnover"] = data_daily.apply(daily_wt, axis=1)

data_day = data_daily.groupby(["date"]).agg({
    "mcap": ["sum"],
    "WeightedReturn": ["sum"],
    "WeightedTurnover": ["sum"]
})
day_vwr = lambda row: row["WeightedReturn"]["sum"] / row["mcap"]["sum"]
day_vwt = lambda row: row["WeightedTurnover"]["sum"] / row["mcap"]["sum"]
data_day["ValueWeightedReturn"] = data_day.apply(day_vwr, axis=1)
data_day["ValueWeightedTurnover"] = data_day.apply(day_vwt, axis=1)
data_day.columns = data_day.columns.droplevel(1)

def daily_abnret(row):
    if (row["date"] == daily_dates[0]):
        return 0
    return row["return"] - data_day.filter(items=[date_shift(row["date"], -1)], axis=0)["ValueWeightedReturn"].values[0]
def daily_abnvol(row):
    if (row["date"] == daily_dates[0]):
        return 0
    return row["return"] - data_day.filter(items=[row["date"]], axis=0)["ValueWeightedTurnover"].values[0]
def daily_volatility(row):
    abnReturns = []
    for i in range(-20, 1):
        abnReturns.append(query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)), "AbnRet"))
    return np.std(abnReturns)
data_daily["AbnRet"] = data_daily.apply(daily_abnret, axis=1)
data_daily["AbnVol"] = data_daily.apply(daily_abnvol, axis=1)
# print("Calculated Abnormal, elapsed " + str(time.time() - time_start))
# data_daily["Volatility"] = data_daily.apply(daily_volatility, axis=1)
def volatility(ticker, date):
    abnReturns = []
    for i in range(-20, 1):
        abnReturns.append(query(data_daily, "ticker == '" + ticker + "' & date == " + str(date_shift(date, i)), "AbnRet"))
    return np.std(abnReturns)
def abnVolatility(ticker, date):
    pastWeek = 0
    print("AbnVolatility")
    ori = volatility(ticker, date)
    print("\tVolatility", ori)
    for i in range(-5, 0):
        val = volatility(ticker, date_shift(date, i))
        pastWeek += val
        print("\tVolatility[t" + str(i) + "]", date_shift(date, i), val)
    print("\tDifference", ori - pastWeek / 5)
    return ori - pastWeek / 5

time_end = time.time()
print("Calculated daily variables in " + str(round(time_end - time_start, 2)) + " seconds.")
# time_start = time.time()

# REGRESSION/VECTOR CALCULATIONS

data_daily.to_csv("../data/output_daily.csv")
data_quarterly.to_csv("../data/output_quarterly.csv")
data_simulated.to_csv("../data/output_simulated.csv")
data_day.to_csv("../data/output_indivDay.csv")
data_firms.to_csv("../data/output_firms.csv")

data_firms = pd.read_csv("../data/output_firms.csv")

time_start = time.time()
data_vector = pd.read_csv("../data/output_firms.csv")
data_vector = data_vector[data_vector.date.isin(daily_dates)]
data_vector.set_index(["ticker", "date"])
# data_vector = data_firms.query()

def vector_abnret(row):
    return query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(row["date"]), "AbnRet")
    """
    q = data_daily.query("ticker == '" + row["ticker"] + "' & date == " + str(row["date"]))
    if len(q) == 0:
        return NO_RESULT
    return q["AbnRet"].values[0]
    """

def vector_absabnret(row):
    return abs(row["AbnRet"])

def vector_abnvol(row):
    return query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(row["date"]), "AbnVol")
    """
    q = data_daily.query("ticker == '" + row["ticker"] + "' & date == " + str(row["date"]))
    if len(q) == 0:
        return NO_RESULT
    return q["AbnVol"].values[0]
    """

def vector_stories(row):
    return row["count"]

def helper_stories(firm, date):
    return query(data_firms, "ticker == '" + firm + "' & date == " + str(date), "count")
    """
    q = data_firms.filter(items=[(firm, date)], axis=0)
    if len(q) == 0:
        return NO_RESULT
    return q["count"].values[0]
    """

# throw out zeroes

def vector_abnstories(row):
    storiesPastWeek, storiesPast3Mo = 0, 0
    for i in range(-5, 0):
        storiesPastWeek += helper_stories(row["ticker"], date_shift(row["date"], i))
    for i in range(-60, -5):
        storiesPast3Mo += helper_stories(row["ticker"], date_shift(row["date"], i))
    storiesPastWeek /= 5.
    storiesPast3Mo /= 55.
    return storiesPastWeek - storiesPast3Mo

def vector_terms(row):
    return row["length"]

def vector_mcap(row):
    mcap = 1000 * query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(row["date"]), "mcap")
    if mcap != 0:
        mcap = np.log(mcap)
    return mcap
    """
    q = data_daily.query("ticker == '" + row["ticker"] + "' & date == " + str(row["date"]))
    if len(q) == 0:
        return NO_RESULT
    return q["mcap"].values[0]
    """

def vector_bm(row):
    q = data_quarterly.where(data_quarterly["ticker"] == row["ticker"]).where(data_quarterly["date"] < row["date"]).dropna()
    if len(q) == 0:
        return NO_RESULT
    mcap = 1000 * query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(row["date"]), "mcap")
    if mcap == NO_RESULT:
        return NO_RESULT
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("BM", q["assets"].values[0], mcap)
    return q["assets"].values[0]/mcap

def vector_abnretprev5(row):
    pastWeek = 0
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("AbnRet")
    for i in range(-5, 0):
        val = query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)), "AbnRet")
        pastWeek += val
        ## DEBUG ## pastWeek += query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)), "AbnRet")
        if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
            print("\tAbnRet[t" + str(i) + "]", date_shift(row["date"], i), val)
        # pastWeek += data_daily.query("ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)))["AbnRet"].values[0]
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("\tSum", pastWeek)
    return pastWeek

def vector_abnvolprev5(row):
    pastWeek = 0
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("AbnVol")
    for i in range(-5, 0):
        val = query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)), "AbnVol")
        pastWeek += val
        ## DEBUG ## pastWeek += query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)), "AbnVol")
        if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
            print("\tAbnVol[t" + str(i) + "]", date_shift(row["date"], i), val)
        # pastWeek += data_daily.query("ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)))["AbnVol"].values[0]
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("\tAverage", pastWeek / 5)
    return pastWeek / 5

"""
def vector_volatility(row):
    abnReturns = []
    for i in range(-20, 1):
        abnReturns.append(query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)), "AbnRet"))
        # abnReturns.append(data_daily.query("ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)))["AbnRet"].values[0])
    return np.std(abnReturns)
"""

def vector_abnvolatility(row):
    pastWeek = 0
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("AbnVolatility")
        print("\tVolatility", row["Volatility"])
    for i in range(-5, 0):
        val = query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)), "Volatility")
        pastWeek += val
        ## DEBUG ## pastWeek += query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)), "Volatility")
        if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
            print("\tVolatility[t" + str(i) + "]", date_shift(row["date"], i), val)
        # pastWeek += data_vector.query("ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)))["Volatility"].values[0]
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("\tDifference", row["Volatility"] - pastWeek / 5)
    return row["Volatility"] - pastWeek / 5

def vector_illiq(row):
    pastWeek = 0
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("Illiq")
    for i in range(-5, 0):
        it = data_daily.query("ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], i)))
        if len(it) == 0:
            pastWeek += NO_RESULT
            continue
        Ret = np.abs(it["return"].values[0])
        Vol = it["volume"].values[0] * it["price"].values[0]
        if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
            print("\t[t" + str(i) + "]", date_shift(row["date"], i), Ret, Vol)
        pastWeek += 10**6 * np.abs(Ret) / Vol
    if DEBUG and row["ticker"] == "AAPL" and row["date"] == 20150721:
        print("\tAverage", pastWeek / 5)
    return pastWeek / 5

data_vector["AbnRet"] = data_vector.apply(vector_abnret, axis=1)
data_vector["|AbnRet|"] = data_vector.apply(vector_absabnret, axis=1)
data_vector["AbnVol"] = data_vector.apply(vector_abnvol, axis=1)
data_vector["Stories"] = data_vector.apply(vector_stories, axis=1)
data_vector["AbnStories"] = data_vector.apply(vector_abnstories, axis=1)
data_vector["Terms"] = data_vector.apply(vector_terms, axis=1)
data_vector["MCap"] = data_vector.apply(vector_mcap, axis=1)
data_vector["BM"] = data_vector.apply(vector_bm, axis=1)
data_vector["AbnRetPrev5"] = data_vector.apply(vector_abnretprev5, axis=1)
data_vector["AbnVolPrev5"] = data_vector.apply(vector_abnvolprev5, axis=1)
# data_vector["Volatility"] = data_vector.apply(vector_volatility, axis=1)
# data_vector["AbnVolatility"] = data_vector.apply(vector_abnvolatility, axis=1)
abnVolatility("AAPL", 20150721)
data_vector["Illiq"] = data_vector.apply(vector_illiq, axis=1)

time_end = time.time()
print("Calculated regression variables in " + str(round(time_end - time_start, 2)) + " seconds.")

data_vector = data_vector.dropna()
data_vector.to_csv("../data/output_vector.csv")

################################################################

time_start = time.time()

params = ["AbnPctOld", "Stories", "AbnStories", "Terms", "MCap", "BM", "AbnRetPrev5", "AbnVolPrev5", "AbnVolatility", "Illiq"]

data_model = data_vector[["ticker", "date"]]
depAbnRet = lambda row: query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], -1)), "AbnRet")
depAbnVol = lambda row: query(data_daily, "ticker == '" + row["ticker"] + "' & date == " + str(date_shift(row["date"], -1)), "AbnVol")
data_model["AbnRet+1"] = data_model.apply(depAbnRet, axis=1)
data_model["AbnVol+1"] = data_model.apply(depAbnVol, axis=1)

data_model = data_model.set_index(['ticker', 'date'])
data_vector = data_vector.set_index(['ticker', 'date'])

abnRetModel_OldNews = FamaMacBeth(data_model[["AbnRet+1"]], sm.add_constant(data_vector[params])).fit('heteroskedastic', 'bartlett')
abnVolModel_OldNews = FamaMacBeth(data_model[["AbnVol+1"]], sm.add_constant(data_vector[params])).fit('heteroskedastic', 'bartlett')

print("Market Reactions to Old News")
print(abnRetModel_OldNews)
print(abnVolModel_OldNews)

"""
# this shifting is not proper 

abnRetModel_OldNews = FamaMacBeth(data_vector[["AbnRet"]][1:], sm.add_constant(data_vector[params][:-1])).fit('heteroskedastic', 'bartlett')
abnRetModel_OldNews = FamaMacBeth(data_vector[["AbnVol"]][1:], sm.add_constant(data_vector[params][:-1])).fit('heteroskedastic', 'bartlett')

params = ["AbnPctOld", "AbnPctRecombinations", "Stories", "AbnStories", "Terms", "MCap", "BM", "AbnRetPrev5", "AbnVolPrev5", "AbnVolatility", "Illiq"]

abnRetModel_Recombination = FamaMacBeth(data_vector[["AbnRet"]][1:], sm.add_constant(data_vector[params][:-1])).fit('heteroskedastic', 'bartlett')
abnRetModel_Recombination = FamaMacBeth(data_vector[["AbnVol"]][1:], sm.add_constant(data_vector[params][:-1])).fit('heteroskedastic', 'bartlett')

print("Market Reactions to Old News")
print(abnRetModel_OldNews)
print(abnRetModel_OldNews)

print("Market Reactions to Recombinations")
print(abnRetModel_Recombination)
print(abnRetModel_Recombination)
"""

time_end = time.time()
print("Calculated regressions in " + str(round(time_end - time_start, 2)) + " seconds.")

"""
Confusion:
Quarterly Data, Line 4712
For shifting days, using the days within Daily, not from Simulated Data
"""