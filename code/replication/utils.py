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


def abnormalReturn(firm, date, file):
    """
    #1
    Difference between firm i's return on date and return on value-weighted
    index of all firms in universe on date
    Uses decimal representation
    Returns FLOAT
    """
    return firmReturn(firm, date, file) - allFirmsReturn(date, file)


def abnormalReturn(firm, dateStart, dateEnd, file):
    """
    #2
    Cumulative abnormal returns for firm over [dateStart, dateEnd]
    Uses decimal representation
    Returns FLOAT
    """


def firmReturn(firm, date, pdatabase):
    """
    Returns firm's return on date
    Uses decimal representation
    Relies on column structure of pdatabase (crsp)
    Returns FLOAT
    """
    return pdatabase.data['RETX'][pdatabase.data['date'] == date & pdatabase.data['TICKER'] == firm]



def allFirmsReturn(date, file):
    """
    Return on value-weighted index of all firms in universe on date
    Uses decimal representation
    Returns FLOAT
    """


def abnormalVol(firm, date, file):
    """
    #1
    Abnormal trading volume for firm on date defined as difference between the
    fraction of shares turned over for firm on date, and the value-weighted average
    of the fraction of shares turned over for all firms in universe on date
    Uses decimal representation
    Returns FLOAT
    """
    return firmVolume(firm, date, file) - allFirmsVolume(date, file)


def abnormalVol(firm, dateStart, dateEnd, file):
    """
    #2
    Average abnormal trading volume for firm over [dateStart, dateEnd]
    Uses decimal representation
    Returns FLOAT
    """


def firmVolume(firm, date, file):
    """
    Firm's volume on date
    Uses decimal representation
    Returns FLOAT
    """


def allFirmsVolume(date, file):
    """
    Volume of value-weighted index of all firms in universe on date
    Uses decimal representation
    Returns FLOAT
    """


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


def marketCap(firm, date, file):
    """
    LN market capitalization of firm as of market open on date
    Returns FLOAT
    """


def bookToMarketCap(firm, date, file):
    """
    Ratio of firm's book value as of latest quarterly earnings report preceding date
    to its market capitalization as of market open on date
    Returns FLOAT
    """


def abnormalVolatility(firm, dateStart, dateEnd, file):
    """
    Difference between firm's volatility and value-weighted average volatility of all firms
    over [dateStart, dateEnd]
    Returns FLOAT
    """


def illiquidity(firm, dateStart, dateEnd, file):
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
