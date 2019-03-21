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
    coefficients = {'a': 0, 'b': 0, 'g1': 0, 'g2': 0, 'g3': 0, 'g4': 0, 'g5': 0, 'g6': 0, 'g7': 0, 'g8': 0, 'g9': 0}
    # for average at end
    num_dates_used = len(dates) - 1
    unused_dates = []
    for i in range(len(dates) - 1):
        print("DAY T: " + dates[i])
        # compute daily cross-sectional regression
        lists = {'absAbnRet': [], 'AbnPctOld': [], 'Stories': [], 'AbnStories': [], 'Terms': [], 'MCap': [],
                 'BM': [], 'AbnRet': [], 'AbnVol': [], 'AbnVolitility': [], 'Illiq': []}
        for firm in firms:
            # skip firms where no data is available on date
            abn_ret = u.abnormalReturnDate(firm, dates[i + 1], pdatabase1, False)
            if abn_ret == -1:
                continue
            abn_pct_old = u.abnormalPercentageOld(firm, dates[i], mdatabase)
            if abn_pct_old == -1:
                continue
            x = u.generateXList(firm, dates[i], mdatabase, pdatabase1, pdatabase2, False)
            if not x:
                continue
            lists['absAbnRet'].append(abs(abn_ret))
            lists['AbnPctOld'].append(abn_pct_old)
            lists['Stories'].append(x[0])
            lists['AbnStories'].append(x[1])
            lists['Terms'].append(x[2])
            lists['MCap'].append(x[3])
            lists['BM'].append(x[4])
            lists['AbnRet'].append(x[5])
            lists['AbnVol'].append(x[6])
            lists['AbnVolitility'].append(x[7])
            lists['Illiq'].append(x[8])
        # Invalid date
        if len(lists['absAbnRet']) == 0:
            num_dates_used -= 1
            unused_dates.append(dates[i])
            continue
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": lists['absAbnRet'], "B": lists['AbnPctOld'], "G1": lists['Stories'],
                           "G2": lists['AbnStories'], "G3": lists['Terms'], "G4": lists['MCap'],
                           "G5": lists['BM'], "G6": lists['AbnRet'], "G7": lists['AbnVol'],
                           "G8": lists['AbnVolitility'], "G9": lists['Illiq']})
        result = sm.ols(formula="Y ~ B + G1 + G2 + G3 + G4 + G5 + G6 + G7 + G8 + G9", data=df).fit()
        coefficients['a'] += result.params.Intercept
        coefficients['b'] += result.params.B
        coefficients['g1'] += result.params.G1
        coefficients['g2'] += result.params.G2
        coefficients['g3'] += result.params.G3
        coefficients['g4'] += result.params.G4
        coefficients['g5'] += result.params.G5
        coefficients['g6'] += result.params.G6
        coefficients['g7'] += result.params.G7
        coefficients['g8'] += result.params.G8
        coefficients['g9'] += result.params.G9
    print(unused_dates)
    print(num_dates_used)
    return {key: coefficients[key]/num_dates_used for key in coefficients}


def neweyWestStdErrors():
    """
    Newey-West standard errors
    """
