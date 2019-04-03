# regression.py
# -------
# Functions for equations (8), (9), (10), (11), (12), (13) from Section 3
import utils as u
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np
import threading


def famaMacBethRegression8(dates, firms, mdatabase, pdatabase1, pdatabase2):
    """
    Average coefficients for daily cross-sectional regression over dates given
    dates: list of days in order from starting date to ending date
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    Returns tuple (dictionary mapping coefficients to values, dictionary mapping coefficients to their standard errors)
    """
    # running sum of coefficients as cross-sectional regressions are computed
    coefficients = {'a': 0, 'b': 0, 'g1': 0, 'g2': 0, 'g3': 0, 'g4': 0, 'g5': 0, 'g6': 0, 'g7': 0, 'g8': 0, 'g9': 0}
    standard_errrors = {'ase': 0, 'bse': 0, 'g1se': 0, 'g2se': 0, 'g3se': 0, 'g4se': 0, 'g5se': 0, 'g6se': 0,
                        'g7se': 0, 'g8se': 0, 'g9se': 0}
    # for average at end
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
            unused_dates.append(dates[i])
            continue
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": lists['absAbnRet'], "B": lists['AbnPctOld'], "G1": lists['Stories'],
                           "G2": lists['AbnStories'], "G3": lists['Terms'], "G4": lists['MCap'],
                           "G5": lists['BM'], "G6": lists['AbnRet'], "G7": lists['AbnVol'],
                           "G8": lists['AbnVolitility'], "G9": lists['Illiq']})
        # 'HAC' for heteroscedasticity and autocorrelation, statsmodels uses Newey-West SE by default
        result = sm.ols(formula="Y ~ B + G1 + G2 + G3 + G4 + G5 + G6 + G7 + G8 + G9",
                        data=df).fit(cov_type='HAC', cov_kwds={'maxlags': 1})
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
        standard_errrors['ase'] += result.bse.Intercept ** 2
        standard_errrors['bse'] += result.bse.B ** 2
        standard_errrors['g1se'] += result.bse.G1 ** 2
        standard_errrors['g2se'] += result.bse.G2 ** 2
        standard_errrors['g3se'] += result.bse.G3 ** 2
        standard_errrors['g4se'] += result.bse.G4 ** 2
        standard_errrors['g5se'] += result.bse.G5 ** 2
        standard_errrors['g6se'] += result.bse.G6 ** 2
        standard_errrors['g7se'] += result.bse.G7 ** 2
        standard_errrors['g8se'] += result.bse.G8 ** 2
        standard_errrors['g9se'] += result.bse.G9 ** 2
    print(unused_dates)
    num_dates_used = len(dates) - 1 - len(unused_dates)
    print(num_dates_used)
    return {key: coefficients[key]/num_dates_used for key in coefficients}, \
           {key: (standard_errrors[key]/(num_dates_used**2))**0.5 for key in standard_errrors}


def famaMacBethRegression8worker(dates, firms, mdatabase, pdatabase1, pdatabase2, i, unused_dates, coefficients,
                                 standard_errrors, lock):
    """
    Thread that computes a cross-sectional regression (used in parallel)
    lock: used for preventing "race conditions" or shared resource incrementation errors
    """
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
        lock.acquire()
        unused_dates.append(dates[i])
        lock.release()
        return
    # Create pandas data frame and run regression with statsmodels
    df = pd.DataFrame({"Y": lists['absAbnRet'], "B": lists['AbnPctOld'], "G1": lists['Stories'],
                       "G2": lists['AbnStories'], "G3": lists['Terms'], "G4": lists['MCap'],
                       "G5": lists['BM'], "G6": lists['AbnRet'], "G7": lists['AbnVol'],
                       "G8": lists['AbnVolitility'], "G9": lists['Illiq']})
    # 'HAC' for heteroscedasticity and autocorrelation, statsmodels uses Newey-West SE by default
    result = sm.ols(formula="Y ~ B + G1 + G2 + G3 + G4 + G5 + G6 + G7 + G8 + G9",
                    data=df).fit(cov_type='HAC', cov_kwds={'maxlags': 1})
    lock.acquire()
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
    standard_errrors['ase'] += result.bse.Intercept ** 2
    standard_errrors['bse'] += result.bse.B ** 2
    standard_errrors['g1se'] += result.bse.G1 ** 2
    standard_errrors['g2se'] += result.bse.G2 ** 2
    standard_errrors['g3se'] += result.bse.G3 ** 2
    standard_errrors['g4se'] += result.bse.G4 ** 2
    standard_errrors['g5se'] += result.bse.G5 ** 2
    standard_errrors['g6se'] += result.bse.G6 ** 2
    standard_errrors['g7se'] += result.bse.G7 ** 2
    standard_errrors['g8se'] += result.bse.G8 ** 2
    standard_errrors['g9se'] += result.bse.G9 ** 2
    lock.release()


def famaMacBethRegression8par(dates, firms, mdatabase, pdatabase1, pdatabase2):
    """
    Average coefficients for daily cross-sectional regression over dates given
    dates: list of days in order from starting date to ending date
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    Returns tuple (dictionary mapping coefficients to values, dictionary mapping coefficients to their standard errors)
    """
    # running sum of coefficients as cross-sectional regressions are computed
    coefficients = {'a': 0, 'b': 0, 'g1': 0, 'g2': 0, 'g3': 0, 'g4': 0, 'g5': 0, 'g6': 0, 'g7': 0, 'g8': 0, 'g9': 0}
    standard_errrors = {'ase': 0, 'bse': 0, 'g1se': 0, 'g2se': 0, 'g3se': 0, 'g4se': 0, 'g5se': 0, 'g6se': 0,
                        'g7se': 0, 'g8se': 0, 'g9se': 0}
    # for average at end
    unused_dates = []
    # set up for multithreading
    lock = threading.Lock()
    thread_list = []
    for i in range(len(dates) - 1):
        thread = threading.Thread(target=famaMacBethRegression8worker,
                                  args=(dates, firms, mdatabase, pdatabase1, pdatabase2,
                                        i, unused_dates, coefficients, standard_errrors, lock,))
        thread.start()
        thread_list.append(thread)
    for t in thread_list:
        t.join()
    print(unused_dates)
    num_dates_used = len(dates) - 1 - len(unused_dates)
    print(num_dates_used)
    return {key: coefficients[key]/num_dates_used for key in coefficients}, \
           {key: (standard_errrors[key]/(num_dates_used**2))**0.5 for key in standard_errrors}
