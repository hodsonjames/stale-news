import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS, FamaMacBeth
import statsmodels.api as sm
import time
import math
from bisect import bisect
from queue import Queue as queue
from datetime import date
import pickle
from scipy.linalg.blas import dgemm

"""
CRSP Daily Stock
https://wrds-web.wharton.upenn.edu/wrds/ds/crsp/stock_a/dsf.cfm?navId=128
2000-01-01 to 2015-12-31
Entire Database
Ticker, Price, Return without Dividends, Share Volume, Number of Shares Outstanding

Computstat Unrestated Quarterly
https://wrds-web.wharton.upenn.edu/wrds/ds/comph/urq/indexus.cfm?navId=93
2000 to 2018
Entire Database
Data Date, Report Date of Qtly Earnings, Unrestated Data Values, CEQQ
"""

# PHILOSOPHY: preprocess AS MUCH AS POSSIBLE

# TODO: optimize dictionary references

time_start = time.time()
def log_time(msg):
    global time_start
    time_end = time.time()
    print(msg + " in " + str(round(time_end - time_start, 2)) + " sec", flush=True)
    time_start = time.time()

_int = int
def int(val):
    try:
        return _int(val)
    except ValueError:
        return math.nan

_float = float
def float(val):
    try:
        return _float(val)
    except ValueError:
        return math.nan

def anynan(*argv):
    for arg in argv:
        if math.isnan(arg):
            return True
    return False

def div(a, b):
    if b == 0:
        return math.nan
    return a / b

def log(val):
    try:
        return math.log(val)
    except ValueError:
        return math.nan

def lstsq(a, b):
    """
    Fast least-squares solver, from https://gist.github.com/aldro61/5889795
    Returns the least-squares solution to a linear matrix equation.
    Solves the equation `a x = b` by computing a vector `x` that
    minimizes the Euclidean 2-norm `|| b - a x ||^2`.  The equation may
    be under-, well-, or over- determined (i.e., the number of
    linearly independent rows of `a` can be less than, equal to, or
    greater than its number of linearly independent columns).  If `a`
    is square and of full rank, then `x` (but for round-off error) is
    the "exact" solution of the equation.
    Parameters
    ----------
    a : (M, N) array_like
        "Coefficient" matrix.
    b : (M,) array_like
        Ordinate or "dependent variable" values.
    residuals : bool
        Compute the residuals associated with the least-squares solution
    Returns
    -------
    x : (M,) ndarray
        Least-squares solution. The shape of `x` depends on the shape of
        `b`.
    residuals : int
        Residuals: ``b - a*x``.
    """
    a = np.asarray(a, order='c')
    i = dgemm(alpha=1.0, a=a.T, b=a.T, trans_b=True)
    x = np.linalg.solve(i, dgemm(alpha=1.0, a=a.T, b=b)).flatten()
    return x, np.dot(a, x) - b

EMPTY = math.nan

###########################
#########  DAILY  #########
###########################

data_date_firm = {}
trading_days = set()
tickers = set()

with open("../data/daily.csv") as f:
    for line in f:
        #PERMNO,date,TICKER,PRC,VOL,SHROUT,RETX
        vals = line.split(",")
        if not math.isnan(int(vals[0])):
            valDate = int(vals[1])
            valTicker = str(vals[2])
            valPrc = float(vals[3])
            valVol = int(vals[4])
            valShrout = 1e3 * int(vals[5])
            valRetx = float(vals[6])
            valMcap = valPrc * valShrout
            valTurnover = div(valVol, valShrout)
            if not anynan(valDate, valPrc, valVol, valShrout, valRetx, valMcap, valTurnover):
                trading_days.add(valDate)
                tickers.add(valTicker)
                if valDate not in data_date_firm:
                    data_date_firm[valDate] = {}
                data_date_firm[valDate][valTicker] = {
                    "price": valPrc,
                    "volume": valVol,
                    "outstanding": valShrout,
                    "return": valRetx,
                    "mcap": valMcap,
                    "mcaplog": log(valMcap),
                    "turnover": valTurnover,
                    "volatility": EMPTY,
                    "illiqpw": EMPTY,
                    "pctold": EMPTY,
                    "pctrecombination": EMPTY,
                    "abnpctold": EMPTY,
                    "abnpctrecombination": EMPTY,
                    "stories": 0,
                    "terms": EMPTY,
                    "abnstoriespw": EMPTY,
                    "abnret": EMPTY,
                    "abnvol": EMPTY,
                    "abnvolatility": EMPTY,
                    "abnretpw": EMPTY,
                    "abnvolpw": EMPTY,
                    "abnvolatilitypw": EMPTY,
                    "_prevBV": EMPTY,
                    "_illiqday": div(1e6 * abs(valRetx), (valVol * valPrc)),
                    "_weightedreturn": valMcap * valRetx,
                    "_weightedturnover": valMcap * valTurnover,
                    "_weightedvolatility": EMPTY,
                    "_numOldStories": 0,
                    "_numRecombinationStories": 0,
                    "_numTerms": 0,
                    "_logstories": EMPTY,
                    "_logterms": EMPTY,
                }

trading_days
tdays_lst = list(trading_days)
tdays_lst.sort()

log_time("Read CRSP Daily into data_date_firm")
# VECTOR: mcaplog
# HELPER: price, volume, outstanding, return, mcap, turnover, _illiqDay, _wreturn, _wturnover


###########################
#######  QUARTERLY  #######
###########################

with open("../data/quarterly.csv") as f:
    for line in f:
        #gvkey,tic,datadate,fqtr,qtryr,rdq,ceqqr
        vals = line.split(",")
        if not math.isnan(int(vals[0])):
            valDate = int(vals[2])
            valTicker = str(vals[1])
            valEquity = 1e6 * float(vals[6])
            if not anynan(valDate, valEquity):
                if valEquity > 0: # ..what..
                    # find first date in tdays that is < valDate
                    i = bisect(tdays_lst, valDate) - 1
                    if i <= 1:
                        print("this should never happen")
                    if tdays_lst[i] == valDate:
                        i -= 1
                    curDate = tdays_lst[i]
                    canContinue = True
                    # storing in data_date_firm instead of developing a range query
                    # becaues of philosophy: preprocess as much as possible
                    while canContinue and "_prevBV" not in data_date_firm[curDate][valTicker]:
                        data_date_firm[curDate][valTicker]["_prevBV"] = valEquity
                        i -= 1
                        if i < 0:
                            canContinue = False
                        else:
                            curDate = tdays_lst[i]

log_time("Read Compustat Quarterly into data_date_firm")
# VECTOR: 
# HELPER: _prevBV

###########################
#######  NEWS DATA  #######
###########################

# TODO: deal with news on weekends

news_dates = set()
news_tickers = set()

with open("../data/djn_01-07.csv") as f:
    for line in f:
        #DATE_EST,STORY_ID,TICKER,STORY_LENGTH,CLOSEST_ID,SECOND_CLOSEST_ID,CLOSEST_SCORE,TOTAL_OVERLAP,IS_OLD,IS_REPRINT,IS_RECOMB
        vals = line.split(",")
        if not math.isnan(int(vals[0])):
            valDate = int(vals[0])
            valTicker = str(vals[2])
            valLength = int(vals[3])
            valClosestNeighbor = float(vals[6])
            valOld = float(vals[7])
            valOldNews = bool(int(vals[8]))
            valReprint = bool(int(vals[9]))
            valRecombination = bool(int(vals[10]))
            if not anynan(valDate, valLength, valClosestNeighbor, valOld):
                if valDate in trading_days and valTicker in tickers:
                    news_dates.add(valDate)
                    news_tickers.add(valTicker)
                    data_date_firm[valDate][valTicker]["stories"] += 1
                    data_date_firm[valDate][valTicker]["_numTerms"] += valLength
                    if valOldNews:
                        data_date_firm[valDate][valTicker]["_numOldStories"] += 1
                    if valRecombination:
                        data_date_firm[valDate][valTicker]["_numRecombinationStories"] += 1

news_tickers_list = list(news_tickers)

log_time("Read news data into data_date_firm")
# VECTOR: stories
# HELPER: _numTerms, _numOldStories, _numRecombinationStories

###########################
#######  SOLO VARS  #######
###########################

for valDate in news_dates:
    for valTicker in news_tickers:
        valTerms = div(data_date_firm[valDate][valTicker]["_numTerms"], data_date_firm[valDate][valTicker]["stories"])
        data_date_firm[valDate][valTicker]["bm"] = div(data_date_firm[valDate][valTicker]["_prevBV"], data_date_firm[valDate][valTicker]["mcap"])
        data_date_firm[valDate][valTicker]["pctold"] = div(data_date_firm[valDate][valTicker]["_numOldStories"], data_date_firm[valDate][valTicker]["stories"])
        data_date_firm[valDate][valTicker]["pctrecombination"] = div(data_date_firm[valDate][valTicker]["_numRecombinationStories"], data_date_firm[valDate][valTicker]["stories"])
        data_date_firm[valDate][valTicker]["terms"] = valTerms
        data_date_firm[valDate][valTicker]["_logstories"] = log(data_date_firm[valDate][valTicker]["stories"])
        data_date_firm[valDate][valTicker]["_logterms"] = log(valTerms)

log_time("Calculated solo vars for NEWS firms/days into data_date_firm")
# VECTOR: bm, terms
# HELPER: pctold, pctrecombination, _logstories, _logterms

###########################
####  CROSS-SEC REGS  #####
###########################

for valDate in news_dates:
    depOld = [] # 1 x n
    depRcm = [] # 1 x n
    explan = [] # n x 4
    for valTicker in news_tickers_list:
        data = data_date_firm[valDate][valTicker]
        depOld.append(data["pctold"])
        depRcm.append(data["pctrecombination"])
        explan.append([1, data["_logstories"], data["_logterms"], data["_logterms"] * data["_logterms"]])
    depOld = np.array(depOld).T # m x 1
    depRcm = np.array(depRcm).T # m x 1
    explan = np.matrix(explan) # m x 4
    residualsOld = lstsq(explan, depOld)[1]
    residualsRcm = lstsq(explan, depRcm)[1]
    for i in range(len(news_tickers_list)):
        valTicker = news_tickers_list[i]
        data_date_firm[valDate][valTicker]["abnpctold"] = residualsOld[i]
        data_date_firm[valDate][valTicker]["abnpctrecombination"] = residualsRcm[i]
    del depOld
    del depRcm
    del explan
log_time("Calculated cross-sectional regressions for NEWS firms/days into data_date_firm")
# VECTOR: abnpctold, abtnpctrecombination
# HELPER: 

###########################
#######  MULTI DAY  #######
###########################

for valTicker in tickers:
    running_returns = queue(maxsize=21)
    running_illiqday = queue(maxsize=6)
    running_stories_week = queue(maxsize=6)
    running_stories_months = queue(maxsize=56)
    for i in range(len(tdays_lst) - 1):
        valDate = tdays_lst[i]
        running_returns.put(data_date_firm[valDate][valTicker]["return"])
        if running_returns.full():
            running_returns.get()
        running_illiqday.put(data_date_firm[valDate][valTicker]["_illiqday"])
        if running_illiqday.full():
            running_illiqday.get()
        running_stories_week.put(data_date_firm[valDate][valTicker]["stories"])
        if running_stories_week.full():
            running_stories_months.put(running_stories_week.get())
            if running_stories_months.full():
                running_stories_months.get()
        valVolatility = np.std(running_returns)
        valIlliqPW = log(np.average(running_illiqday))
        valAbnStoriesPW = np.average(running_stories_week) - np.average(running_stories_months)
        valDate = tdays_lst[i+1]
        if not anynan(valVolatility, valIlliq, valAbnStories):
            data_date_firm[valDate][valTicker]["volatility"] = valVolatility
            data_date_firm[valDate][valTicker]["illiqpw"] = valIlliqPW
            data_date_firm[valDate][valTicker]["abnstoriespw"] = valAbnStoriesPW
            data_date_firm[valDate][valTicker]["_weightedvolatility"] = valVolatility * data_date_firm[valDate][valTicker]["mcap"]
    del running_returns
    del running_illiqday
    del running_stories_week
    del running_stories_months

log_time("Calculated cross-day variables for each firm/day into data_date_firm")
# VECTOR: abnstoriespw, illiqpw
# HELPER: volatility, _wvolatility

###########################
########  EACHDAY  ########
###########################

for valDate in tdays_lst:
    valTotalMcap = 0
    valTotalWeightedReturn = 0
    valTotalWeightedTurnover = 0
    valTotalWeightedVolatility = 0
    for data in data_date_firm[valDate].values():
        valTotalMcap += data["mcap"]
        valTotalWeightedReturn += data["_weightedreturn"]
        valTotalWeightedTurnover += data["_weightedturnover"]
        valTotalWeightedVolatility += data["_weightedvolatility"]
    data_date_firm[valDate]["*"] = {
        "return": div(valTotalWeightedReturn, valTotalMcap),
        "turnover": div(valTotalWeightedTurnover, valTotalMcap),
        "volatility": div(valTotalWeightedVolatility, valTotalMcap),
        # "_totalmcap": valTotalMcap,
        # "_totalweightedreturn": valTotalWeightedReturn,
        # "_totalweightedturnover": valTotalWeightedTurnover,
        # "_totalweightedvolatility": valTotalWeightedVolatility
    }

log_time("Calculated sums for each day into data_date_firm")
# VECTOR: 
# HELPER: _totalmcap, _totalwreturn, _totalwturnover, _totalwvolatility

###########################
####  WEIGHTDEPENDENT  ####
###########################

for valDate in tdays_lst:
    for valTicker in tickers:
        valAbnRet = data_date_firm[valDate][valTicker]["return"] - data_date_firm[valDate]["*"]["return"]
        valAbnVol = data_date_firm[valDate][valTicker]["turnover"] - data_date_firm[valDate]["*"]["turnover"]
        valAbnVolatility = data_date_firm[valDate][valTicker]["volatility"] - data_date_firm[valDate]["*"]["volatility"]
        data_date_firm[valDate][valTicker]["abnret"] = valAbnRet
        data_date_firm[valDate][valTicker]["abnvol"] = valAbnVol
        data_date_firm[valDate][valTicker]["abnvolatility"] = valAbnVolatility

log_time("Calculated weighted-dependent variables for each firm/day into data_date_firm")
# VECTOR: abnret, abnvol
# HELPER: abnvolatility

###########################
##  WEIGHTDEP MULTI DAY  ##
###########################

for valTicker in tickers:
    running_abnret = queue(maxsize=6)
    running_abnvol = queue(maxsize=6)
    running_abnvolatility = queue(maxsize=6)
    for i in range(len(tdays_lst) - 1):
        valDate = tdays_lst[i]
        running_abnret.put(data_date_firm[valDate][valTicker]["abnret"])
        if running_abnret.full():
            running_abnret.get()
        running_abnvol.put(data_date_firm[valDate][valTicker]["abnvol"])
        if running_abnvol.full():
            running_abnvol.get()
        running_abnvolatility.put(data_date_firm[valDate][valTicker]["abnvolatility"])
        if running_abnvolatility.full():
            running_abnvolatility.get()

        valAbnRetPW = np.sum(running_abnret)
        valAbnVolPW = np.average(running_abnvol)
        valAbnVolatilityPW = np.average(running_abnvolatility)
        valDate = tdays_lst[i+1]
        if not anynan(valAbnRetPW, valAbnVolPW, valAbnVolatilityPW):
            data_date_firm[valDate][valTicker]["abnretpw"] = valAbnRetPW
            data_date_firm[valDate][valTicker]["abnvolpw"] = valAbnVolPW
            data_date_firm[valDate][valTicker]["abnvolatilitypw"] = valAbnVolatilityPW
    del running_abnret
    del running_abnvol
    del running_abnvolatility

log_time("Calculated weighted-dependent cross-day variables (AbnRetPW, AbnVolPW, AbnVolatilityPW) for each firm/day into data_date_firm")
# VECTOR: abnretpw, abnvolpw, abnvolatilitypw
# HELPER: 

pickle.dump(data_date_firm, "../data/data.pickle")
log_time("Dumped data to data.pickle")

# FINAL 'VECTOR': abnret, abnvol, abnpctold, abtpctrecombination, stories, abnstoriespw, terms, mcaplog, bm, abnretpw, abnvolpw, abnvolatilitypw, illiqpw
