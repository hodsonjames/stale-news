# utils.py
# -------
# Helper functions for arguments to regression.py

"""
Functions that interface with measures directory in repo
"""
import databases as db


def percentageOld(firm, date, mdatabase):
    """
    PctOld for firm on given data
    Uses decimal representation
    Relies on column structure of mdatabase
    If no match is found return -1 otherwise
    Returns FLOAT
    """
    firmMatches = mdatabase.tickerMap.get(firm, [])
    if len(firmMatches) == 0:
        return -1
    firmNews = [row for row in firmMatches if row[2] == date]
    if len(firmNews) == 0:
        return -1
    oldCount = len([row for row in firmNews if float(row[4]) >= 0.6])
    return oldCount / len(firmNews)



def percentageRecombinations(firm, date, mdatabase):
    """
    PctRecombinations for firm on given data
    Uses decimal representation
    Relies on column structure of mdatabase
    If no match is found return -1 otherwise
    Returns FLOAT
    """
    firmMatches = mdatabase.tickerMap.get(firm, [])
    if len(firmMatches) == 0:
        return -1
    firmNews = [row for row in firmMatches if row[2] == date]
    if len(firmNews) == 0:
        return -1
    recomCount = len([row for row in firmNews if (float(row[4]) >= 0.6) and ((float(row[5]) / float(row[4])) < 0.8)])
    return recomCount / len(firmNews)



"""
Additional functions for regression
"""


def abnormalPercentageOld(firm, date, file):
    """
    AbnPctOld for firm on given data
    Uses decimal representation
    Returns FLOAT
    """


def abnormalPercentageRecombinations(firm, date, file):
    """
    AbnPctRecombinations for firm on given data
    Uses decimal representation
    Returns FLOAT
    """


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


def firmReturn(firm, date, file):
    """
    Returns firm's return on date
    Uses decimal representation
    Returns FLOAT
    """


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
    return firmVolume(firm, data, file) - allFirmsVolume(date, file)


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
    Return -1 if firm not in database otherwise
    Returns INTEGER
    """
    firmMatches = mdatabase.tickerMap.get(firm, [])
    if len(firmMatches) == 0:
        return -1
    return len([row for row in firmMatches if row[2] == date])


def abnormalStories(firm, date, mdatabase):
    """
    Difference between the average number of stories over [date-5, date-1] and
    the average number of stories over [date-60, date-6] for firm
    Return -1 if firm not in database or date not compatible
    Returns FLOAT
    """
    dates = list(mdatabase.dateMap.keys())
    if (date not in dates) or (dates.index(date) - 60) < 0 or (firm not in mdatabase.tickerMap):
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
    Return -1 if firm not in database otherwise
    Returns FLOAT
    """
    firmMatches = mdatabase.tickerMap.get(firm, [])
    if len(firmMatches) == 0:
        return -1
    firmNews = [row for row in firmMatches if row[2] == date]
    if len(firmNews) == 0:
        return 0
    return sum([float(row[6]) for row in firmNews]) / len(firmNews)


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
