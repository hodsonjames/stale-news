# utilsp.py
# -------
# Parallelized helper functions for arguments to regression.py
# WILL result in floating point arithmetic discrepancies (as floating point arithmetic is not associative)
import utils as u
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np
import threading
import queue


def abnormalPercentageOldParallel(firm, date, mdatabase):
    """
    PARALLEL implementation MAY be faster for larger mdatabase
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
        # set up for parallel (pctOld, lnStories, lnTerms, lnTermsSq) "data point" computations
        dpoint_queue = queue.Queue()  # thread safe
        thread_list = []
        for t in tickers:
            if (t, date) in mdatabase.tdMap:
                thread = threading.Thread(target=lambda q, arg1, arg2, arg3: q.put(
                    [u.percentageOld(arg1, arg2, arg3), np.log(u.stories(arg1, arg2, arg3)),
                     np.log(u.terms(arg1, arg2, arg3)), np.log(u.terms(arg1, arg2, arg3))**2]),
                                          args=(dpoint_queue, t, date, mdatabase))
                thread.start()
                thread_list.append(thread)
        for t in thread_list:
            t.join()
        while not dpoint_queue.empty():
            data_point = dpoint_queue.get()
            pctOldList.append(data_point[0])
            lnStoriesList.append(data_point[1])
            lnTermsList.append(data_point[2])
            lnTermsSqList.append(data_point[3])
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": pctOldList, "B": lnStoriesList, "C": lnTermsList, "D": lnTermsSqList})
        result = sm.ols(formula="Y ~ B + C + D", data=df).fit()
        mdatabase.putAPOReg(date, result)
    firmPctOld = u.percentageOld(firm, date, mdatabase)
    firmStories = u.stories(firm, date, mdatabase)
    firmTerms = u.terms(firm, date, mdatabase)
    regression = mdatabase.aporeg[date]
    # Get coefficients from regression
    regIntercept = regression.params.Intercept
    regB = regression.params.B
    regC = regression.params.C
    regD = regression.params.D
    # Return signed residual
    regEst = regIntercept + regB * np.log(firmStories) + regC * np.log(firmTerms) + regD * (np.log(firmTerms) ** 2)
    return firmPctOld - regEst


def abnormalPercentageRecombinationsParallel(firm, date, mdatabase):
    """
    PARALLEL implementation MAY be faster for larger mdatabase
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
        # set up for parallel (pctRecombinations, lnStories, lnTerms, lnTermsSq) "data point" computations
        dpoint_queue = queue.Queue()  # thread safe
        thread_list = []
        for t in tickers:
            if (t, date) in mdatabase.tdMap:
                thread = threading.Thread(target=lambda q, arg1, arg2, arg3: q.put(
                    [u.percentageRecombinations(arg1, arg2, arg3), np.log(u.stories(arg1, arg2, arg3)),
                     np.log(u.terms(arg1, arg2, arg3)), np.log(u.terms(arg1, arg2, arg3))**2]),
                                          args=(dpoint_queue, t, date, mdatabase))
                thread.start()
                thread_list.append(thread)
        for t in thread_list:
            t.join()
        while not dpoint_queue.empty():
            data_point = dpoint_queue.get()
            pctRecombinationsList.append(data_point[0])
            lnStoriesList.append(data_point[1])
            lnTermsList.append(data_point[2])
            lnTermsSqList.append(data_point[3])
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": pctRecombinationsList, "B": lnStoriesList, "C": lnTermsList, "D": lnTermsSqList})
        result = sm.ols(formula="Y ~ B + C + D", data=df).fit()
        mdatabase.putAPRReg(date, result)
    firmPctRec = u.percentageRecombinations(firm, date, mdatabase)
    firmStories = u.stories(firm, date, mdatabase)
    firmTerms = u.terms(firm, date, mdatabase)
    regression = mdatabase.aprreg[date]
    # Get coefficients from regression
    regIntercept = regression.params.Intercept
    regB = regression.params.B
    regC = regression.params.C
    regD = regression.params.D
    # Return signed residual
    regEst = regIntercept + regB * np.log(firmStories) + regC * np.log(firmTerms) + regD * (np.log(firmTerms) ** 2)
    return firmPctRec - regEst


def abnormalReturnParallel(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    PARALLEL implementation IS faster for representative workloads
    Cumulative abnormal returns for firm over [dateStart, dateEnd]
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Slow to reject very large and plausible invalid date ranges (should not occur in practice)
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
    # set up for parallel abnormalReturnDate computations
    ard_queue = queue.Queue()  # thread safe
    thread_list = []
    for i in range(dateEndInd - dateStartInd + 1):
        thread = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(
            u.abnormalReturnDate(arg1, arg2, arg3, arg4)),
                                  args=(ard_queue, firm, str(pdatabase.dates[dateStartInd + i]), pdatabase,
                                        printWarnings))
        thread.start()
        thread_list.append(thread)
    for t in thread_list:
        t.join()
    while not ard_queue.empty():
        aretdate = ard_queue.get()
        if aretdate == -1:
            if printWarnings:
                print("DATE NOT COMPATIBLE: " + dateStart + ", " + dateEnd)
            return -1
        sumAbRet += aretdate
    return sumAbRet


def abnormalVolParallel(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    PARALLEL implementation MAY be faster for larger pdatabase
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
    # set up for parallel abnormalVolDate computations
    avd_queue = queue.Queue()  # thread safe
    thread_list = []
    for i in range(dateEndInd - dateStartInd + 1):
        thread = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(
            u.abnormalVolDate(arg1, arg2, arg3, arg4)),
                                  args=(avd_queue, firm, str(pdatabase.dates[dateStartInd + i]), pdatabase,
                                        printWarnings))
        thread.start()
        thread_list.append(thread)
    for t in thread_list:
        t.join()
    while not avd_queue.empty():
        avoldate = avd_queue.get()
        if avoldate == -1:
            if printWarnings:
                print("DATE NOT COMPATIBLE: " + dateStart + ", " + dateEnd)
            return -1
        sumAbVol += avoldate
    return sumAbVol / (dateEndInd - dateStartInd + 1)


def allFirmsVolumeFracParallel(date, pdatabase, printWarnings=True):
    """
    PARALLEL implementation IS faster for representative workloads
    Value-weighted average of the fraction of shares turnover for all firms in our sample
    Uses decimal representation
    Relies on naming of pdatabase (crsp)
    Returns -1 if no data available
    Returns FLOAT
    """
    if date in pdatabase.vwfrac:
        return pdatabase.vwfrac[date]
    tmcapTuple = u.totalMarketCap(date, pdatabase, printWarnings)
    totMCap = tmcapTuple[0]
    relevantFirms = tmcapTuple[1]
    if totMCap == -1:
        return -1
    weightedVolumeTot = 0.0
    # set up for parallel weightedVolumeTot computation
    wv_queue = queue.Queue()  # thread safe
    thread_list = []
    for tic in relevantFirms:
        # marketCap is constant time lookup (saved from totalMarketCap)
        thread = threading.Thread(target=lambda q, arg1, arg2, arg3: q.put(
            u.marketCap(arg1, arg2, arg3)*u.firmVolumeFrac(arg1, arg2, arg3)),
                                  args=(wv_queue, tic, date, pdatabase,))
        thread.start()
        thread_list.append(thread)
    for t in thread_list:
        t.join()
    while not wv_queue.empty():
        weightedVolumeTot += wv_queue.get()
    weightedVolumeFrac = weightedVolumeTot/totMCap
    # save the computation for repeated use
    pdatabase.vwfrac[date] = weightedVolumeFrac
    return weightedVolumeFrac


def abnormalStoriesParallel(firm, date, mdatabase):
    """
    PARALLEL implementation MAY be faster for larger mdatabase
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
    # set up for parallel stories computation
    s5to1_queue = queue.Queue()  # thread safe
    thread_list_5to1 = []
    s60to6_queue = queue.Queue()  # thread safe
    thread_list_60to6 = []
    for i in range(60):
        if i < 55:
            thread = threading.Thread(target=lambda q, arg1, arg2, arg3: q.put(
                u.stories(arg1, arg2, arg3)), args=(s60to6_queue, firm, dates[dateLess60 + i], mdatabase,))
            thread.start()
            thread_list_60to6.append(thread)
        else:
            thread = threading.Thread(target=lambda q, arg1, arg2, arg3: q.put(
                u.stories(arg1, arg2, arg3)), args=(s5to1_queue, firm, dates[dateLess60 + i], mdatabase,))
            thread.start()
            thread_list_5to1.append(thread)
    for t in thread_list_5to1:
        t.join()
    for t in thread_list_60to6:
        t.join()
    while not s5to1_queue.empty():
        stories5to1 += s5to1_queue.get()
    while not s60to6_queue.empty():
        stories60to6 += s60to6_queue.get()
    return (stories5to1 / 5) - (stories60to6 / 55)


def totalMarketCapParallel(date, pdatabase, printWarnings=True):
    """
    PARALLEL implementation IS faster for representative workloads
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
    # set up for parallel market cap computation
    mc_queue = queue.Queue()  # thread safe
    thread_list = []
    for tic in tics:
        thread = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(u.marketCap(arg1, arg2, arg3, arg4)),
                                  args=(mc_queue, tic, date, pdatabase, printWarnings))
        thread.start()
        thread_list.append(thread)
    for t in thread_list:
        t.join()
    while not mc_queue.empty():
        totalMarketCaps += mc_queue.get()
    pdatabase.totmcap[date] = (totalMarketCaps, tics)
    return totalMarketCaps, tics


def abnormalVolatilityDateParallel(firm, date, pdatabase, printWarnings=True):
    """
    PARALLEL implementation IS faster for representative workloads
    Population standard deviation of abnormal returns for 20 business days prior (ending on and including date given)
    Relies on naming of pdatabase (crsp)
    Return -1 if dates not compatible or if no data available
    Returns FLOAT
    """
    if (firm, date) in pdatabase.abnvolat:
        return pdatabase.abnvolat[(firm, date)]
    if not pdatabase.dates:
        pdatabase.recordDates("date", printWarnings)  # "date" is a col name in crsp
    if (int(date) not in pdatabase.dates) or (pdatabase.dates.index(int(date)) - 19) < 0:
        if printWarnings:
            print("DATE NOT COMPATIBLE: " + date)
        return -1
    dateInd = pdatabase.dates.index(int(date))
    dateLess19 = dateInd - 19
    abnRets = []
    # if we have saved values sequential is likely to be faster
    if (firm, str(pdatabase.dates[dateLess19])) in pdatabase.abnret:
        for i in range(dateInd - dateLess19 + 1):
            abnRet = u.abnormalReturnDate(firm, str(pdatabase.dates[dateLess19 + i]), pdatabase, printWarnings)
        if abnRet == -1:
            if printWarnings:
                print("DATE NOT COMPATIBLE: " + date)
            return -1
        abnRets.append(abnRet)
    else:
        # set up for parallel abnormalReturnDate computation
        ard_queue = queue.Queue()  # thread safe
        thread_list = []
        for i in range(dateInd - dateLess19 + 1):
            thread = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(u.abnormalReturnDate(arg1, arg2, arg3, arg4)),
                                      args=(ard_queue, firm, str(pdatabase.dates[dateLess19 + i]), pdatabase, printWarnings))
            thread.start()
            thread_list.append(thread)
        for t in thread_list:
            t.join()
        while not ard_queue.empty():
            abnRet = ard_queue.get()
            if abnRet == -1:
                if printWarnings:
                    print("DATE NOT COMPATIBLE: " + date)
                return -1
            abnRets.append(abnRet)
    volat = np.std(abnRets)
    pdatabase.abnvolat[(firm, date)] = volat
    return volat


def illiquidityParallel(firm, dateStart, dateEnd, pdatabase, printWarnings=True):
    """
    PARALLEL implementation IS faster for representative workloads
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
    # set up for parallel illiquidityMeasureDate computation
    imd_queue = queue.Queue()  # thread safe
    thread_list = []
    for i in range(dateEndInd - dateStartInd + 1):
        thread = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(
            u.illiquidityMeasureDate(arg1, arg2, arg3, arg4)),
                                  args=(imd_queue, firm, str(pdatabase.dates[dateStartInd + i]), pdatabase,
                                        printWarnings))
        thread.start()
        thread_list.append(thread)
    for t in thread_list:
        t.join()
    while not imd_queue.empty():
        illMea = imd_queue.get()
        if illMea == -1:
            if printWarnings:
                print("DATE NOT COMPATIBLE: " + dateStart + ", " + dateEnd)
            return -1
        illMeaSum += illMea
    return illMeaSum / (dateEndInd - dateStartInd + 1)


def generateXListParallel(firm, date, mdatabase, pdatabase1, pdatabase2, printWarnings=True):
    """
    PARALLEL implementation MAY be faster for larger pdatabase1
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
        7: AbnVolatilityi,[t-5,t-1]
        8: Illiqi,[t-5,t-1]
    Return [] (empty list) if dates not compatible or if no data available
    """
    xlist = []
    # 0
    if printWarnings:
        print("Entry 0 Computing...")
    xstories = u.stories(firm, date, mdatabase)
    xlist.append(xstories)
    # 1
    if printWarnings:
        print("Entry 1 Computing...")
    xabnstories = u.abnormalStories(firm, date, mdatabase)
    if xabnstories == -1:
        return []
    xlist.append(xabnstories)
    # 2
    if printWarnings:
        print("Entry 2 Computing...")
    xterms = u.terms(firm, date, mdatabase)
    if xterms == -1:
        return []
    xlist.append(xterms)
    # 3
    if printWarnings:
        print("Entry 3 Computing...")
    xmcap = u.marketCapLN(firm, date, pdatabase1, printWarnings)
    if xmcap == -1:
        return []
    xlist.append(xmcap)
    # 4
    if printWarnings:
        print("Entry 4 Computing...")
    xbm = u.bookToMarketCap(firm, date, pdatabase1, pdatabase2, printWarnings)
    if xbm == -1:
        return []
    xlist.append(xbm)
    # determine date bounds
    if not pdatabase1.dates:
        pdatabase1.recordDates("date", printWarnings)  # "date" is a col name in crsp
    if (int(date) not in pdatabase1.dates) or (pdatabase1.dates.index(int(date)) - 5) < 0:
        if printWarnings:
            print("DATE NOT COMPATIBLE: " + date)
        return []
    dateLess1 = pdatabase1.dates.index(int(date)) - 1
    dateLess5 = dateLess1 - 4
    dateStartLess5 = str(pdatabase1.dates[dateLess5])
    dateEndLess1 = str(pdatabase1.dates[dateLess1])
    # set up for parallel #5 - #8 computations
    five_eight_dict = {}  # thread safe for single operations
    thread_list = []
    # 5
    if printWarnings:
        print("Entry 5 Computing...")
    thread = threading.Thread(target=lambda d, arg1, arg2, arg3, arg4, arg5: d.update({5: u.abnormalReturn(arg1, arg2, arg3, arg4, arg5)}),
                              args=(five_eight_dict, firm, dateStartLess5, dateEndLess1, pdatabase1, printWarnings))
    thread.start()
    thread_list.append(thread)
    # 6
    if printWarnings:
        print("Entry 6 Computing...")
    thread = threading.Thread(target=lambda d, arg1, arg2, arg3, arg4, arg5: d.update({6: u.abnormalVol(arg1, arg2, arg3, arg4, arg5)}),
                              args=(five_eight_dict, firm, dateStartLess5, dateEndLess1, pdatabase1, printWarnings))
    thread.start()
    thread_list.append(thread)
    # 7
    if printWarnings:
        print("Entry 7 Computing...")
    thread = threading.Thread(target=lambda d, arg1, arg2, arg3, arg4, arg5: d.update({7: u.abnormalVolatility(arg1, arg2, arg3, arg4, arg5)}),
                              args=(five_eight_dict, firm, dateStartLess5, dateEndLess1, pdatabase1, printWarnings))
    thread.start()
    thread_list.append(thread)
    # 8
    if printWarnings:
        print("Entry 8 Computing...")
    thread = threading.Thread(target=lambda d, arg1, arg2, arg3, arg4, arg5: d.update({8: u.illiquidity(arg1, arg2, arg3, arg4, arg5)}),
                              args=(five_eight_dict, firm, dateStartLess5, dateEndLess1, pdatabase1, printWarnings))
    thread.start()
    thread_list.append(thread)
    for t in thread_list:
        t.join()
    for i in range(5, 9):
        val = five_eight_dict[i]
        if val == -1:
            return []
        xlist.append(val)
    # Return
    return xlist





