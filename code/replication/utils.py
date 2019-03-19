# utils.py
# -------
# Helper functions for arguments to regression.py
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
    if (firm, date) in mdatabase.pctold:
        return mdatabase.pctold[(firm, date)]
    matches = mdatabase.tdMap.get((firm, date), [])
    if len(matches) == 0:
        return -1
    oldCount = len([row for row in matches if float(row[4]) >= oldthreshold])
    pold = oldCount / len(matches)
    mdatabase.pctold[(firm, date)] = pold
    return pold


def percentageRecombinations(firm, date, mdatabase, oldthreshold=0.6, reprintthresh=0.8):
    """
    PctRecombinations for firm on given data (with adjustable threshold for old and reprint)
    Uses decimal representation
    Relies on column structure of mdatabase
    If no match is found for specified firm on given date return -1 otherwise
    Returns FLOAT
    """
    if (firm, date) in mdatabase.pctrec:
        return mdatabase.pctrec[(firm, date)]
    matches = mdatabase.tdMap.get((firm, date), [])
    if len(matches) == 0:
        return -1
    recomCount = len([row for row in matches if (float(row[4]) >= oldthreshold)
                      and ((float(row[5]) / float(row[4])) < reprintthresh)])
    prec = recomCount / len(matches)
    mdatabase.pctrec[(firm, date)] = prec
    return prec


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
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    if (firm, date) in pdatabase.abnret:
        return pdatabase.abnret[(firm, date)]
    fret = firmReturn(firm, date, pdatabase, printWarnings)
    aret = allFirmsReturn(date, pdatabase, printWarnings)
    if fret == -1 or aret == -1:
        return -1
    abnret = fret - aret
    pdatabase.abnret[(firm, date)] = abnret
    return abnret


def abnormalReturn(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    Cumulative abnormal returns for firm over [dateStart, dateEnd]
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Return -1 if dates not compatible or if no data available
    Returns FLOAT
    """
    if not pdatabase.dates:
        pdatabase.recordDates("date", printWarnings)  # "date" is a col name in crsp
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
    if (firm, date) in pdatabase.abnvol:
        return pdatabase.abnvol[(firm, date)]
    fVolFrac = firmVolumeFrac(firm, date, pdatabase, printWarnings)
    if fVolFrac == -1:
        return -1
    afVolFrac = allFirmsVolumeFrac(date, pdatabase, printWarnings)
    if afVolFrac == -1:
        return -1
    abnFrac = fVolFrac - afVolFrac
    pdatabase.abnvol[(firm, date)] = abnFrac
    return abnFrac


def abnormalVol(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    Average abnormal trading volume (fraction) for firm over [dateStart, dateEnd]
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Return -1 if dates not compatible or if no data available
    Returns FLOAT
    """
    if not pdatabase.dates:
        pdatabase.recordDates("date", printWarnings)  # "date" is a col name in crsp
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
    if (firm, date) in pdatabase.vol:
        return pdatabase.vol[(firm, date)]
    volQuery = pdatabase.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")')
    if volQuery.empty:
        if printWarnings:
            print("NO VOLUME DATA: " + firm + ", " + date)
        return -1
    volume = float(volQuery["VOL"].iat[0])
    pdatabase.vol[(firm, date)] = volume
    return volume


def firmVolumeFrac(firm, date, pdatabase, printWarnings=True, sharesUnit=1000):
    """
    Fraction of shares turned over for firm on date
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    if (firm, date) in pdatabase.firmfrac:
        return pdatabase.firmfrac[(firm, date)]
    dateQuery = pdatabase.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")')
    if dateQuery.empty:
        if printWarnings:
            print("NO SHARES AND VOLUME DATA: " + firm + ", " + date)
        return -1
    # faster to get volume directly instead of calling firmVolume
    volume = float(dateQuery["VOL"].iat[0])
    # save for reuse
    pdatabase.vol[(firm, date)] = volume
    # SHROUT in thousands
    sharesOutstanding = float(dateQuery["SHROUT"].iat[0]) * sharesUnit
    frac = volume/sharesOutstanding
    pdatabase.firmfrac[(firm, date)] = frac
    return frac


def allFirmsVolumeFrac(date, pdatabase, printWarnings=True):
    """
    Value-weighted average of the fraction of shares turnover for all firms in our sample
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    if date in pdatabase.vwfrac:
        return pdatabase.vwfrac[date]
    tmcapTuple = totalMarketCap(date, pdatabase, printWarnings)
    totMCap = tmcapTuple[0]
    relevantFirms = tmcapTuple[1]
    if totMCap == -1:
        return -1
    weightedVolumeTot = 0.0
    for tic in relevantFirms:
        ticMCap = marketCap(tic, date, pdatabase)  # constant time lookup
        ticVolFrac = firmVolumeFrac(tic, date, pdatabase)
        weightedVolumeTot += ticMCap*ticVolFrac
    weightedVolumeFrac = weightedVolumeTot/totMCap
    # save the computation for repeated use
    pdatabase.vwfrac[date] = weightedVolumeFrac
    return weightedVolumeFrac


def stories(firm, date, mdatabase):
    """
    Number of articles published on date tagged with firm that have
    relevance score greater than 70%
    Relies on column structure of mdatabase
    Returns INTEGER
    """
    if (firm, date) in mdatabase.stor:
            return mdatabase.stor[(firm, date)]
    matches = len(mdatabase.tdMap.get((firm, date), []))
    mdatabase.stor[(firm, date)] = matches
    return matches


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
    if (firm, date) in mdatabase.term:
        return mdatabase.term[(firm, date)]
    matches = mdatabase.tdMap.get((firm, date), [])
    if len(matches) == 0:
        return -1
    trms = sum([float(row[6]) for row in matches]) / len(matches)
    mdatabase.term[(firm, date)] = trms
    return trms


def marketCap(firm, date, pdatabase, printWarnings=True, sharesUnit=1000):
    """
    Market capitalization of firm as of market open on date
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    if (firm, date) in pdatabase.mcap:
        return pdatabase.mcap[(firm, date)]
    dateQuery = pdatabase.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")')
    if dateQuery.empty:
        if printWarnings:
            print("NO PRICE AND SHARES DATA: " + firm + ", " + date)
        return -1
    price = float(dateQuery["OPENPRC"].iat[0])
    # SHROUT in thousands
    sharesOutstanding = float(dateQuery["SHROUT"].iat[0]) * sharesUnit
    # print(price)
    # print(sharesOutstanding)
    mc = price * sharesOutstanding
    pdatabase.mcap[(firm, date)] = mc
    return mc


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
    if date in pdatabase.totmcap:
        return pdatabase.totmcap[date]
    totalMarketCaps = 0.0
    ticsQuery = pdatabase.data.query('date == "' + date + '"')
    if ticsQuery.empty:
        if printWarnings:
            print("NO MARKET DATA: " + date)
        return -1, []
    tics = ticsQuery["TICKER"].unique().tolist()
    for tic in tics:
        totalMarketCaps += marketCap(tic, date, pdatabase, False)
    pdatabase.totmcap[date] = (totalMarketCaps, tics)
    return totalMarketCaps, tics


def bookToMarketCap(firm, date, pdatabase1, pdatabase2, printWarnings=True):
    """
    Ratio of firm's book value as of latest quarterly earnings report preceding date
    to its market capitalization as of market open on date
    Relies on contents of databases
    pdatabase1: crsp
    pdatabase2: compustat
    Returns -1 if no data available
    Returns FLOAT
    """
    book = bookValue(firm, date, pdatabase2, printWarnings)
    mcap = marketCap(firm, date, pdatabase1, printWarnings)
    if book == -1 or mcap == -1:
        return -1
    return book / mcap


def bookValue(firm, date, pdatabase, printWarnings=True, bookUnit=1000000):
    """
    Firm's book value as of latest quarterly earnings report preceding date
    Relies on naming of pdatabase (compustat) and chronological data for each firm
    Returns -1 if no data available
    Returns FLOAT
    """
    bookQuery = pdatabase.data.query('(tic == "' + firm + '") & (datadate < ' + date + ')')
    # print(bookQuery)
    if bookQuery.empty:
        if printWarnings:
            print("NO BOOK DATA: " + firm + ", " + date)
        return -1
    bookSeries = bookQuery["ceqq"]
    return float(bookSeries.iat[bookSeries.size - 1] * bookUnit)


def abnormalVolatilityDate(firm, date, pdatabase, printWarnings=True):
    """
    Population standard deviation of abnormal returns for 20 business days prior (ending on and including date given)
    Relies on naming of pdatabase (crsp)
    Return -1 if dates not compatible or if no data available
    Returns FLOAT
    """
    if (firm, date) in pdatabase.abnvolit:
        return pdatabase.abnvolit[(firm, date)]
    if not pdatabase.dates:
        pdatabase.recordDates("date", printWarnings)  # "date" is a col name in crsp
    if (int(date) not in pdatabase.dates) or (pdatabase.dates.index(int(date)) - 19) < 0:
        if printWarnings:
            print("DATE NOT COMPATIBLE: " + date)
        return -1
    dateInd = pdatabase.dates.index(int(date))
    dateLess19 = dateInd - 19
    abnRets = []
    for i in range(dateInd - dateLess19 + 1):
        abnRet = abnormalReturnDate(firm, str(pdatabase.dates[dateLess19 + i]), pdatabase, printWarnings)
        if abnRet == -1:
            return -1
        abnRets.append(abnRet)
    # print(abnRets)
    volit = np.std(abnRets)
    pdatabase.abnvolit[(firm, date)] = volit
    return volit


def abnormalVolatility(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    Average of AbnVolitility for days in [dateStart, dateEnd]
    Relies on naming of pdatabase (crsp)
    Return -1 if dates not compatible or if no data available
    Returns FLOAT
    """
    if not pdatabase.dates:
        pdatabase.recordDates("date", printWarnings)  # "date" is a col name in crsp
    if (int(dateStart) not in pdatabase.dates) or (int(dateEnd) not in pdatabase.dates) or (dateStart > dateEnd):
        if printWarnings:
            print("DATE NOT COMPATIBLE: " + dateStart + ", " + dateEnd)
        return -1
    dateStartInd = pdatabase.dates.index(int(dateStart))
    dateEndInd = pdatabase.dates.index(int(dateEnd))
    sumAbVolit = 0.0
    for i in range(dateEndInd - dateStartInd + 1):
        avolitdate = abnormalVolatilityDate(firm, str(pdatabase.dates[dateStartInd + i]), pdatabase, printWarnings)
        if avolitdate == -1:
            return -1
        sumAbVolit += avolitdate
    return sumAbVolit / (dateEndInd - dateStartInd + 1)


def illiquidityMeasureDate(firm, date, pdatabase, printWarnings=True):
    """
    ln(10**6 * |Ret(firm,date)| / Volume(firm,date))
    Relies on naming of pdatabase (crsp)
    Return -1 if no data available
    Returns FLOAT
    """
    if (firm, date) in pdatabase.ill:
        return pdatabase.ill[(firm, date)]
    ret = firmReturn(firm, date, pdatabase, printWarnings)  # constant time lookup when used in generateXList
    vol = firmVolume(firm, date, pdatabase, printWarnings)  # constant time lookup when used in generateXList
    if ret == -1 or vol == -1:
        return -1
    measure = np.log(10**6 * abs(ret) / vol)
    pdatabase.ill[(firm, date)] = measure
    return measure


def illiquidity(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    Average of illiquidity measure from Amihud over [dateStart, dateEnd]
    Relies on naming of pdatabase (crsp)
    Return -1 if dates not compatible or if no data available
    Returns FLOAT
    """
    if not pdatabase.dates:
        pdatabase.recordDates("date", printWarnings)  # "date" is a col name in crsp
    if (int(dateStart) not in pdatabase.dates) or (int(dateEnd) not in pdatabase.dates) or (dateStart > dateEnd):
        if printWarnings:
            print("DATE NOT COMPATIBLE: " + dateStart + ", " + dateEnd)
        return -1
    dateStartInd = pdatabase.dates.index(int(dateStart))
    dateEndInd = pdatabase.dates.index(int(dateEnd))
    illMeaSum = 0.0
    for i in range(dateEndInd - dateStartInd + 1):
        illMea = illiquidityMeasureDate(firm, str(pdatabase.dates[dateStartInd + i]), pdatabase, printWarnings)
        if illMea == -1:
            return -1
        illMeaSum += illMea
    return illMeaSum / (dateEndInd - dateStartInd + 1)


def generateXList(firm, date, mdatabase, pdatabase1, pdatabase2, printWarnings=True):
    """
    Relies on contents of all databases
    pdatabase1: crsp
    pdatabase2: compustat
    Returns list of controls for a firm including:
        0: Storiesi,t
        1: AbnStoriesi,[t-5,t-1]
        2: Termsi,t
        3: MCapi,t
        4: BMi,t
        5: AbnReti,[t-5,t-1]
        6: AbnVoli,[t-5,t-1]
        7: AbnVolitilityi,[t-5,t-1]
        8: Illiqi,[t-5,t-1]
    Return -1 if dates not compatible or if no data available
    """
    xlist = []
    # 0
    if printWarnings:
        print("Entry 0 Computing...")
    xstories = stories(firm, date, mdatabase)
    xlist.append(xstories)
    # 1
    if printWarnings:
        print("Entry 1 Computing...")
    xabnstories = abnormalStories(firm, date, mdatabase)
    if xabnstories == -1:
        return -1
    xlist.append(xabnstories)
    # 2
    if printWarnings:
        print("Entry 2 Computing...")
    xterms = terms(firm, date, mdatabase)
    if xterms == -1:
        return -1
    xlist.append(xterms)
    # 3
    if printWarnings:
        print("Entry 3 Computing...")
    xmcap = marketCapLN(firm, date, pdatabase1, printWarnings)
    if xmcap == -1:
        return -1
    xlist.append(xmcap)
    # 4
    if printWarnings:
        print("Entry 4 Computing...")
    xbm = bookToMarketCap(firm, date, pdatabase1, pdatabase2, printWarnings)
    if xbm == -1:
        return -1
    xlist.append(xbm)
    # 5
    if printWarnings:
        print("Entry 5 Computing...")
    if not pdatabase1.dates:
        pdatabase1.recordDates("date", printWarnings)  # "date" is a col name in crsp
    if (int(date) not in pdatabase1.dates) or (pdatabase1.dates.index(int(date)) - 5) < 0:
        if printWarnings:
            print("DATE NOT COMPATIBLE: " + date)
        return -1
    dateLess1 = pdatabase1.dates.index(int(date)) - 1
    dateLess5 = dateLess1 - 4
    dateStartLess5 = str(pdatabase1.dates[dateLess5])
    dateEndLess1 = str(pdatabase1.dates[dateLess1])
    xabnret = abnormalReturn(firm, dateStartLess5, dateEndLess1, pdatabase1, printWarnings)
    if xabnret == -1:
        return -1
    xlist.append(xabnret)
    # 6
    if printWarnings:
        print("Entry 6 Computing...")
    xabnvol = abnormalVol(firm, dateStartLess5, dateEndLess1, pdatabase1, printWarnings)
    if xabnvol == -1:
        return -1
    xlist.append(xabnvol)
    # 7
    if printWarnings:
        print("Entry 7 Computing...")
    xabnvolit = abnormalVolatility(firm, dateStartLess5, dateEndLess1, pdatabase1, printWarnings)
    if xabnvolit == -1:
        return -1
    xlist.append(xabnvolit)
    # 8
    if printWarnings:
        print("Entry 8 Computing...")
    xilliq = illiquidity(firm, dateStartLess5, dateEndLess1, pdatabase1, printWarnings)
    if xilliq == -1:
        return -1
    xlist.append(xilliq)
    # Return
    return xlist





