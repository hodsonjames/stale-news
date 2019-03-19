# regression.py
# -------
# Functions for equations (8), (9), (10), (11), (12), (13) from Section 3
import utils as u
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np


def famaMacBethRegression8(dates, firms, mdatabase, pdatabase1, pdatabase2):
    """
    Average coefficients for daily cross-sectional regression over dates given
    dates: list of days in order from starting date to ending date
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    Returns dictionary mapping coefficients to values
    """
    # running sum of coefficients as cross-sectional regressions are computed
    a = 0
    b = 0
    g1 = 0
    g2 = 0
    g3 = 0
    g4 = 0
    g5 = 0
    g6 = 0
    g7 = 0
    g8 = 0
    g9 = 0
    for date in dates:
        # compute daily cross-sectional regression
        absAbnRet = []
        AbnPctOld = []
        Stories = []
        AbnStories = []
        Terms = []
        MCap = []
        BM = []
        AbnRet = []
        AbnVol = []
        AbnVolitility = []
        Illiq = []
        for firm in firms:
            absAbnRet.append(abs(u.abnormalReturnDate(firm, date, pdatabase1, False)))
            AbnPctOld.append(u.abnormalPercentageOld(firm, date, mdatabase))
            X = u.generateXList(firm, date, mdatabase, pdatabase1, pdatabase2, False)
            Stories.append(X[0])
            AbnStories.append(X[1])
            Terms.append(X[2])
            MCap.append(X[3])
            BM.append(X[4])
            AbnRet.append(X[5])
            AbnVol.append(X[6])
            AbnVolitility.append(X[7])
            Illiq.append(X[8])
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": absAbnRet, "B": AbnPctOld, "G1": Stories, "G2": AbnStories, "G3": Terms,
                           "G4": MCap, "G5": BM, "G6": AbnRet, "G7": AbnVol, "G8": AbnVolitility, "G9": Illiq})
        result = sm.ols(formula="Y ~ B + G1 + G2 + G3 + G4 + G5 + G6 + G7 + G8 + G9", data=df).fit()
        a += result.params.Intercept
        b += result.params.B
        g1 += result.params.G1
        g2 += result.params.G2
        g3 += result.params.G3
        g4 += result.params.G4
        g5 += result.params.G5
        g6 += result.params.G6
        g7 += result.params.G7
        g8 += result.params.G8
        g9 += result.params.G9
    num_regressions = len(dates)
    return {'a': a/num_regressions, 'b': b/num_regressions, 'g1': g1/num_regressions, 'g2': g2/num_regressions,
            'g3': g3/num_regressions, 'g4': g4/num_regressions, 'g5': g5/num_regressions, 'g6': g1/num_regressions,
            'g7': g7/num_regressions, 'g8': g8/num_regressions, 'g9': g9/num_regressions}


def generateFMDataFrame(XLists, AbnPctOldList, DependentList):
    """
    Returns pandas data frame organized for ols
    XLists: list of XList corresponding to available firms on given day
    AbnPctOldList: list of AbnPctOld corresponding to available firms on given day
    DependentList: list of dependent variable corresponding to available firms on given day
    """


def neweyWestStdErrors():
    """
    Newey-West standard errors
    """
