# utils.py
# -------
# Helper functions for arguments to regression.py

"""
Functions that interface with measures directory in repo
"""
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np


def percentageOld(firm, date, mdatabase, oldthreshold=0.6):
    """
    PctOld for firm on given data (with adjustable threshold for old)
    Uses decimal representation
    Relies on column structure of mdatabase
    If no match is found for specified firm on given date return -1 otherwise
    Returns FLOAT
    """
    matches = mdatabase.tdMap.get((firm, date), [])
    if len(matches) == 0:
        return -1
    oldCount = len([row for row in matches if float(row[4]) >= oldthreshold])
    return oldCount / len(matches)


def percentageRecombinations(firm, date, mdatabase, oldthreshold=0.6, reprintthresh=0.8):
    """
    PctRecombinations for firm on given data (with adjustable threshold for old and reprint)
    Uses decimal representation
    Relies on column structure of mdatabase
    If no match is found for specified firm on given date return -1 otherwise
    Returns FLOAT
    """
    matches = mdatabase.tdMap.get((firm, date), [])
    if len(matches) == 0:
        return -1
    recomCount = len([row for row in matches if (float(row[4]) >= oldthreshold)
                      and ((float(row[5]) / float(row[4])) < reprintthresh)])
    return recomCount / len(matches)


"""
Additional functions for regression
"""


def abnormalPercentageOld(firm, date, mdatabase):
    """
    AbnPctOld for firm on given data
    Uses decimal representation
    If no match is found for specified firm on given date return -1 otherwise
    Returns FLOAT
    """
    if (firm, date) not in mdatabase.tdMap:
        return -1
    if date not in mdatabase.aporeg:
        # Run ols regression with all available firms on this date and store result in mdatabase.aporeg
        pctOldList = []
        lnStoriesList = []
        lnTermsList = []
        lnTermsSqList = []
        tickers = list(mdatabase.tics.keys())
        for t in tickers:
            if (t, date) in mdatabase.tdMap:
                pctOldList.append(percentageOld(t, date, mdatabase))
                lnStoriesList.append(np.log(stories(t, date, mdatabase)))
                lnTermsList.append(np.log(terms(t, date, mdatabase)))
                lnTermsSqList.append(np.log(terms(t, date, mdatabase)) ** 2)
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": pctOldList, "B": lnStoriesList, "C": lnTermsList, "D": lnTermsSqList})
        result = sm.ols(formula="Y ~ B + C + D", data=df).fit()
        mdatabase.putAPOReg(date, result)
    firmPctOld = percentageOld(firm, date, mdatabase)
    firmStories = stories(firm, date, mdatabase)
    firmTerms = terms(firm, date, mdatabase)
    regression = mdatabase.aporeg[date]
    # Get coefficients from regression
    regIntercept = regression.params.Intercept
    regB = regression.params.B
    regC = regression.params.C
    regD = regression.params.D
    # Return signed residual
    regEst = regIntercept + regB * np.log(firmStories) + regC * np.log(firmTerms) + regD * (np.log(firmTerms) ** 2)
    return firmPctOld - regEst


def abnormalPercentageRecombinations(firm, date, mdatabase):
    """
    AbnPctRecombinations for firm on given data
    Uses decimal representation
    If no match is found for specified firm on given date return -1 otherwise
    Returns FLOAT
    """
    if (firm, date) not in mdatabase.tdMap:
        return -1
    if date not in mdatabase.aprreg:
        # Run ols regression with all available firms on this date and store result in mdatabase.aprreg
        pctRecombinationsList = []
        lnStoriesList = []
        lnTermsList = []
        lnTermsSqList = []
        tickers = list(mdatabase.tics.keys())
        for t in tickers:
            if (t, date) in mdatabase.tdMap:
                pctRecombinationsList.append(percentageRecombinations(t, date, mdatabase))
                lnStoriesList.append(np.log(stories(t, date, mdatabase)))
                lnTermsList.append(np.log(terms(t, date, mdatabase)))
                lnTermsSqList.append(np.log(terms(t, date, mdatabase)) ** 2)
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": pctRecombinationsList, "B": lnStoriesList, "C": lnTermsList, "D": lnTermsSqList})
        result = sm.ols(formula="Y ~ B + C + D", data=df).fit()
        mdatabase.putAPRReg(date, result)
    firmPctRec = percentageRecombinations(firm, date, mdatabase)
    firmStories = stories(firm, date, mdatabase)
    firmTerms = terms(firm, date, mdatabase)
    regression = mdatabase.aprreg[date]
    # Get coefficients from regression
    regIntercept = regression.params.Intercept
    regB = regression.params.B
    regC = regression.params.C
    regD = regression.params.D
    # Return signed residual
    regEst = regIntercept + regB * np.log(firmStories) + regC * np.log(firmTerms) + regD * (np.log(firmTerms) ** 2)
    return firmPctRec - regEst


def abnormalReturnDate(firm, date, pdatabase, printWarnings=True):
    """
    Difference between firm i's return on date and return on value-weighted
    index of all firms in universe on date
    Uses decimal representation
    Returns -1 if no data available
    Returns FLOAT
    """
    fret = firmReturn(firm, date, pdatabase, printWarnings)
    aret = allFirmsReturn(date, pdatabase, printWarnings)
    if fret == -1 or aret == -1:
        return -1
    return fret - aret


def abnormalReturn(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    Cumulative abnormal returns for firm over [dateStart, dateEnd]
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Return -1 if dates not compatible or if no data available
    Returns FLOAT
    """
    if not pdatabase.dates:
        pdatabase.recordDates("date")  # "date" is a col name in crsp
    if (int(dateStart) not in pdatabase.dates) or (int(dateEnd) not in pdatabase.dates) or (dateStart > dateEnd):
        if printWarnings:
            print("DATE NOT COMPATIBLE: " + dateStart + ", " + dateEnd)
        return -1
    dateStartInd = pdatabase.dates.index(int(dateStart))
    dateEndInd = pdatabase.dates.index(int(dateEnd))
    sumAbRet = 0.0
    for i in range(dateEndInd - dateStartInd + 1):
        aretdate = abnormalReturnDate(firm, str(pdatabase.dates[dateStartInd + i]), pdatabase, printWarnings)
        if aretdate == -1:
            return -1
        sumAbRet += aretdate
    return sumAbRet


def firmReturn(firm, date, pdatabase, printWarnings=True):
    """
    Returns firm's return on date
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    retQuery = pdatabase.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")')
    if retQuery.empty:
        if printWarnings:
            print("NO RETURN DATA: " + firm + ", " + date)
        return -1
    return float(retQuery["RETX"].iat[0])


def allFirmsReturn(date, pdatabase, printWarnings=True):
    """
    Return on value-weighted index of all firms in universe on date
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    aRetQuery = pdatabase.data.query('date == "' + date + '"')
    if aRetQuery.empty:
        if printWarnings:
            print("NO WEIGHTED RETURN DATA: " + date)
        return -1
    return float(aRetQuery["vwretx"].iat[0])


def abnormalVolDate(firm, date, pdatabase, printWarnings=True):
    """
    Abnormal trading volume for firm on date defined as difference between the
    fraction of shares turned over for firm on date, and the value-weighted average
    of the fraction of shares turned over for all firms in universe on date
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    fVolFrac = firmVolumeFrac(firm, date, pdatabase, printWarnings)
    afVolFrac = allFirmsVolumeFrac(date, pdatabase, printWarnings)
    if fVolFrac == -1 or afVolFrac == -1:
        return -1
    return fVolFrac - afVolFrac


def abnormalVol(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    Average abnormal trading volume (fraction) for firm over [dateStart, dateEnd]
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Return -1 if dates not compatible or if no data available
    Returns FLOAT
    """
    if not pdatabase.dates:
        pdatabase.recordDates("date")  # "date" is a col name in crsp
    if (int(dateStart) not in pdatabase.dates) or (int(dateEnd) not in pdatabase.dates) or (dateStart > dateEnd):
        if printWarnings:
            print("DATE NOT COMPATIBLE: " + dateStart + ", " + dateEnd)
        return -1
    dateStartInd = pdatabase.dates.index(int(dateStart))
    dateEndInd = pdatabase.dates.index(int(dateEnd))
    sumAbVol = 0.0
    for i in range(dateEndInd - dateStartInd + 1):
        avoldate = abnormalVolDate(firm, str(pdatabase.dates[dateStartInd + i]), pdatabase, printWarnings)
        if avoldate == -1:
            return -1
        sumAbVol += avoldate
    return sumAbVol / (dateEndInd - dateStartInd + 1)


def firmVolume(firm, date, pdatabase, printWarnings=True):
    """
    Firm's volume on date
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    volQuery = pdatabase.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")')
    if volQuery.empty:
        if printWarnings:
            print("NO VOLUME DATA: " + firm + ", " + date)
        return -1
    return float(volQuery["VOL"].iat[0])


def firmVolumeFrac(firm, date, pdatabase, printWarnings=True, sharesUnit=1000):
    """
    Fraction of shares turned over for firm on date
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    volume = firmVolume(firm, date, pdatabase, printWarnings)
    sharesQuery = pdatabase.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")')
    if sharesQuery.empty or volume == -1:
        if sharesQuery.empty and printWarnings:
            print("NO SHARES DATA: " + firm + ", " + date)
        return -1
    # SHROUT in thousands
    sharesOutstanding = float(sharesQuery["SHROUT"].iat[0])
    return volume/(sharesOutstanding * sharesUnit)


def allFirmsVolumeFrac(date, pdatabase, printWarnings=True):
    """
    Value-weighted average of the fraction of shares turnover for all firms in our sample
    Uses decimal representation
    Relies on naming of pdatabase (crsp), auxiliaryMap with date:value_weighted_volume
    Returns -1 if no data available
    Returns FLOAT
    """
    if date in pdatabase.auxiliaryMap:
        return pdatabase.auxiliaryMap[date]
    tmcapTuple = totalMarketCap(date, pdatabase, printWarnings)
    totMCap = tmcapTuple[0]
    relevantFirms = tmcapTuple[1]
    if totMCap == -1:
        return -1
    weightedVolumeFrac = 0.0
    for tic in relevantFirms:
        ticMCap = marketCap(tic, date, pdatabase)
        ticVolFrac = firmVolumeFrac(tic, date, pdatabase)
        weightedVolumeFrac += (ticMCap / totMCap) * ticVolFrac
    # save the computation for repeated use
    pdatabase.auxiliaryMap[date] = weightedVolumeFrac
    return weightedVolumeFrac


def stories(firm, date, mdatabase):
    """
    Number of articles published on date tagged with firm that have
    relevance score greater than 70%
    Relies on column structure of mdatabase
    Returns INTEGER
    """
    matches = mdatabase.tdMap.get((firm, date), [])
    return len(matches)


def abnormalStories(firm, date, mdatabase):
    """
    Difference between the average number of stories over [date-5, date-1] and
    the average number of stories over [date-60, date-6] for firm
    Return -1 if date not compatible
    Returns FLOAT
    """
    dates = list(mdatabase.dates.keys())
    if (date not in dates) or (dates.index(date) - 60) < 0:
        return -1
    dateLess60 = dates.index(date) - 60
    stories5to1 = 0
    stories60to6 = 0
    for i in range(60):
        if i < 55:
            stories60to6 += stories(firm, dates[dateLess60 + i], mdatabase)
        else:
            stories5to1 += stories(firm, dates[dateLess60 + i], mdatabase)
    return (stories5to1 / 5) - (stories60to6 / 55)


def terms(firm, date, mdatabase):
    """
    Average number of unique terms in stories published on date, tagged with firm
    Relies on column structure of mdatabase
    Return -1 if no stories for firm on date
    Returns FLOAT
    """
    matches = mdatabase.tdMap.get((firm, date), [])
    if len(matches) == 0:
        return -1
    return sum([float(row[6]) for row in matches]) / len(matches)


def marketCap(firm, date, pdatabase, printWarnings=True, sharesUnit=1000):
    """
    Market capitalization of firm as of market open on date
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    priceQuery = pdatabase.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")')
    sharesQuery = pdatabase.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")')
    if priceQuery.empty or sharesQuery.empty:
        if printWarnings:
            if priceQuery.empty:
                print("NO PRICE DATA: " + firm + ", " + date)
            if sharesQuery.empty:
                print("NO SHARES DATA: " + firm + ", " + date)
        return -1
    price = float(priceQuery["OPENPRC"].iat[0])
    # SHROUT in thousands
    sharesOutstanding = float(sharesQuery["SHROUT"].iat[0])
    # print(price)
    # print(sharesOutstanding)
    return price * sharesOutstanding * sharesUnit


def marketCapLN(firm, date, pdatabase, printWarnings=True):
    """
    LN market capitalization of firm as of market open on date
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    mcap = marketCap(firm, date, pdatabase, printWarnings)
    if mcap == -1:
        return -1
    return np.log(mcap)


def totalMarketCap(date, pdatabase, printWarnings=True):
    """
    Sum market capitalization of all firms available in data as of market open on date
    Relies on naming of pdatabase (crsp)
    Returns (-1, []) if no data available
    Returns (FLOAT, includedTickers)
    """
    totalMarketCaps = 0.0
    includedTickers = []
    missingTickers = []
    if not pdatabase.tics:
        pdatabase.recordTickers("TICKER")  # "TICKER" is a col name in crsp
    for tic in pdatabase.tics:
        ticMCap = marketCap(tic, date, pdatabase, False)
        if ticMCap == -1:
            missingTickers.append(tic)
        else:
            includedTickers.append(tic)
            totalMarketCaps += ticMCap
    if printWarnings:
        print("TICKERS MISSING IN TOTAL: " + str(missingTickers))
        if not includedTickers:
            return -1, []
    return totalMarketCaps, includedTickers


def bookToMarketCap(firm, date, file):
    """
    Ratio of firm's book value as of latest quarterly earnings report preceding date
    to its market capitalization as of market open on date
    Returns FLOAT
    """


def abnormalVolatilityDate(firm, date, pdatabase, printWarnings=True):
    """
    Standard Deviation of abnormal returns for 20 business days prior (ending on and including date given)
    Returns FLOAT
    """


def abnormalVolatility(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    Average of AbnVolitility for each date in [dateStart, dateEnd]
    Returns FLOAT
    """


def illiquidityDate(firm, date, pdatabase, printWarnings=True):
    """
    LN of the illiquidity measure from Amihud, computed as the prior-week average of
    10**6 * |Ret(firm,date)| / Volume(firm,date)
    Returns FLOAT
    """


def illiquidity(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    LN of the illiquidity measure from Amihud, computed as the prior-week average of
    10**6 * |Ret(firm,date)| / Volume(firm,date)
    Returns FLOAT
    """


def generateXVector(firm, data, file):
    """
    Creates 9 x 1 vector of controls for a firm including:
        1. Storiesi,t
        2. AbnStoriesi,[t-5,t-1]
        3. Termsi,t
        4. MCapi,t
        5. BMi,t
        6. AbnReti,[t-5,t-1]
        7. AbnVoli,[t-5,t-1]
        8. AbnVolitilityi,[t-5,t-1]
        9. Illiqi,[t-5,t-1]
    """
