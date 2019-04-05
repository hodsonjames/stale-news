# regression.py
# -------
# Functions for equations (8), (9), (10), (11), (12), (13) from Section 3
import utils as u
import utilsp as up
import pandas as pd
import statsmodels.formula.api as sm


def famaMacBethRegression8_9(dates, firms, mdatabase, pdatabase1, pdatabase2, eight=True):
    """
    Average coefficients for daily cross-sectional regression over dates given
    dates: list of days in order from starting date to ending date, each date represents a date t used for computation
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    eight: True computes equation 8, False computes equation 9
    Returns tuple (dictionary mapping coefficients to values, dictionary mapping coefficients to their standard errors)
    """
    # append one day at the end for very last t+1 query
    if not pdatabase1.dates:
        pdatabase1.recordDates("date", False)  # "date" is a col name in crsp
    extra_day_index = pdatabase1.dates.index(int(dates[len(dates) - 1])) + 1
    dates.append(str(pdatabase1.dates[extra_day_index]))
    # running sum of coefficients as cross-sectional regressions are computed
    coefficients = {'a': 0, 'b': 0, 'g1': 0, 'g2': 0, 'g3': 0, 'g4': 0, 'g5': 0, 'g6': 0, 'g7': 0, 'g8': 0, 'g9': 0}
    standard_errrors = {'ase': 0, 'bse': 0, 'g1se': 0, 'g2se': 0, 'g3se': 0, 'g4se': 0, 'g5se': 0, 'g6se': 0,
                        'g7se': 0, 'g8se': 0, 'g9se': 0}
    # for average at end
    unused_dates = []
    # -1 to account for extra day appended
    for i in range(len(dates) - 1):
        print("DAY T: " + dates[i])
        # compute daily cross-sectional regression
        lists = {'dependent': [], 'AbnPctOld': [], 'Stories': [], 'AbnStories': [], 'Terms': [], 'MCap': [],
                 'BM': [], 'AbnRet': [], 'AbnVol': [], 'AbnVolitility': [], 'Illiq': []}
        for firm in firms:
            # skip firms where no data is available on date
            if eight:
                dependent_var = u.abnormalReturnDate(firm, dates[i + 1], pdatabase1, False)
                if dependent_var == -1:
                    continue
            else:
                dependent_var = u.abnormalVolDate(firm, dates[i + 1], pdatabase1, False)
                if dependent_var == -1:
                    continue
            abn_pct_old = u.abnormalPercentageOld(firm, dates[i], mdatabase)
            if abn_pct_old == -1:
                continue
            x = u.generateXList(firm, dates[i], mdatabase, pdatabase1, pdatabase2, False)
            if not x:
                continue
            if eight:
                lists['dependent'].append(abs(dependent_var))
            else:
                lists['dependent'].append(dependent_var)
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
        if len(lists['dependent']) == 0:
            unused_dates.append(dates[i])
            continue
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": lists['dependent'], "B": lists['AbnPctOld'], "G1": lists['Stories'],
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
    num_dates_used = len(dates) - 1 - len(unused_dates)  # -1 to account for extra day appended
    print(num_dates_used)
    return {key: coefficients[key]/num_dates_used for key in coefficients}, \
           {key: (standard_errrors[key]/(num_dates_used**2))**0.5 for key in standard_errrors}


def famaMacBethRegression10_11(dates, firms, mdatabase, pdatabase1, pdatabase2, ten=True):
    """
    Average coefficients for daily cross-sectional regression over dates given
    dates: list of days in order from starting date to ending date, each date represents a date t used for computation
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    ten: True computes equation 10, False computes equation 11
    equation (13) uses equation 10 computation, calling this function for each year
    Returns tuple (dictionary mapping coefficients to values, dictionary mapping coefficients to their standard errors)
    """
    # append one day at the end for very last t+1 query
    if not pdatabase1.dates:
        pdatabase1.recordDates("date", False)  # "date" is a col name in crsp
    extra_day_index = pdatabase1.dates.index(int(dates[len(dates) - 1])) + 1
    dates.append(str(pdatabase1.dates[extra_day_index]))
    # running sum of coefficients as cross-sectional regressions are computed
    coefficients = {'a': 0, 'b1': 0, 'b2': 0, 'g1': 0, 'g2': 0, 'g3': 0, 'g4': 0, 'g5': 0, 'g6': 0, 'g7': 0, 'g8': 0, 'g9': 0}
    standard_errrors = {'ase': 0, 'b1se': 0, 'b2se': 0, 'g1se': 0, 'g2se': 0, 'g3se': 0, 'g4se': 0, 'g5se': 0, 'g6se': 0,
                        'g7se': 0, 'g8se': 0, 'g9se': 0}
    # for average at end
    unused_dates = []
    # -1 to account for extra day appended
    for i in range(len(dates) - 1):
        print("DAY T: " + dates[i])
        # compute daily cross-sectional regression
        lists = {'dependent': [], 'AbnPctOld': [], 'AbnPcrRecombinations': [], 'Stories': [], 'AbnStories': [],
                 'Terms': [], 'MCap': [], 'BM': [], 'AbnRet': [], 'AbnVol': [], 'AbnVolitility': [], 'Illiq': []}
        for firm in firms:
            # skip firms where no data is available on date
            if ten:
                dependent_var = u.abnormalReturnDate(firm, dates[i + 1], pdatabase1, False)
                if dependent_var == -1:
                    continue
            else:
                dependent_var = u.abnormalVolDate(firm, dates[i + 1], pdatabase1, False)
                if dependent_var == -1:
                    continue
            abn_pct_old = u.abnormalPercentageOld(firm, dates[i], mdatabase)
            if abn_pct_old == -1:
                continue
            abn_pct_rec = u.abnormalPercentageRecombinations(firm, dates[i], mdatabase)
            if abn_pct_rec == -1:
                continue
            x = u.generateXList(firm, dates[i], mdatabase, pdatabase1, pdatabase2, False)
            if not x:
                continue
            if ten:
                lists['dependent'].append(abs(dependent_var))
            else:
                lists['dependent'].append(dependent_var)
            lists['AbnPctOld'].append(abn_pct_old)
            lists['AbnPcrRecombinations'].append(abn_pct_rec)
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
        if len(lists['dependent']) == 0:
            unused_dates.append(dates[i])
            continue
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": lists['dependent'], "B1": lists['AbnPctOld'], "B2": lists['AbnPcrRecombinations'],
                           "G1": lists['Stories'], "G2": lists['AbnStories'], "G3": lists['Terms'],
                           "G4": lists['MCap'], "G5": lists['BM'], "G6": lists['AbnRet'],
                           "G7": lists['AbnVol'], "G8": lists['AbnVolitility'], "G9": lists['Illiq']})
        # 'HAC' for heteroscedasticity and autocorrelation, statsmodels uses Newey-West SE by default
        result = sm.ols(formula="Y ~ B1 + B2 + G1 + G2 + G3 + G4 + G5 + G6 + G7 + G8 + G9",
                        data=df).fit(cov_type='HAC', cov_kwds={'maxlags': 1})
        coefficients['a'] += result.params.Intercept
        coefficients['b1'] += result.params.B1
        coefficients['b2'] += result.params.B2
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
        standard_errrors['b1se'] += result.bse.B1 ** 2
        standard_errrors['b2se'] += result.bse.B2 ** 2
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
    num_dates_used = len(dates) - 1 - len(unused_dates)  # -1 to account for extra day appended
    print(num_dates_used)
    return {key: coefficients[key]/num_dates_used for key in coefficients}, \
           {key: (standard_errrors[key]/(num_dates_used**2))**0.5 for key in standard_errrors}


def famaMacBethRegression12(dates, firms, mdatabase, pdatabase1, pdatabase2, t1, t2):
    """
    Average coefficients for daily cross-sectional regression over dates given
    dates: list of days in order from starting date to ending date, each date represents a date t used for computation
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    t1, t2: used for AbnRet date range [t+t1, t+t2] where t is current reference day
    Returns tuple (dictionary mapping coefficients to values, dictionary mapping coefficients to their standard errors)
    """
    # append t2 additional days at the end for last few dependent variable queries
    if not pdatabase1.dates:
        pdatabase1.recordDates("date", False)  # "date" is a col name in crsp
    extra_day_start_index = pdatabase1.dates.index(int(dates[len(dates) - 1])) + 1
    for i in range(t2):
        dates.append(str(pdatabase1.dates[extra_day_start_index + i]))
    # running sum of coefficients as cross-sectional regressions are computed
    coefficients = {'a': 0, 'b1': 0, 'b2': 0, 'b3': 0, 's1': 0, 's2': 0, 'g1': 0, 'g2': 0, 'g3': 0, 'g4': 0, 'g5': 0,
                    'g6': 0, 'g7': 0, 'g8': 0, 'g9': 0}
    standard_errrors = {'ase': 0, 'b1se': 0, 'b2se': 0, 'b3se': 0, 's1se': 0, 's2se': 0, 'g1se': 0, 'g2se': 0,
                        'g3se': 0, 'g4se': 0, 'g5se': 0, 'g6se': 0, 'g7se': 0, 'g8se': 0, 'g9se': 0}
    # for average at end
    unused_dates = []
    # -t2 to account for extra days appended
    for i in range(len(dates) - t2):
        print("DAY T: " + dates[i])
        # compute daily cross-sectional regression
        lists = {'dependent': [], 'AbnPcrOld': [],  'AbnPcrOldXAbnRet': [], 'AbnRet': [], 'AbnPcrRecombinations': [],
                 'AbnPcrRecombinationsXAbnRet': [], 'Stories': [], 'AbnStories': [], 'Terms': [], 'MCap': [], 'BM': [],
                 'AbnRetVect': [], 'AbnVol': [], 'AbnVolitility': [], 'Illiq': []}
        for firm in firms:
            # skip firms where no data is available on date
            dependent_var = u.abnormalReturn(firm, dates[i + t1], dates[i + t2], pdatabase1, False)
            if dependent_var == -1:
                continue
            abn_pcr_old = u.abnormalPercentageOld(firm, dates[i], mdatabase)
            if abn_pcr_old == -1:
                continue
            abn_ret_next = u.abnormalReturnDate(firm, dates[i + 1], pdatabase1, False)
            if abn_ret_next == -1:
                continue
            abn_pcr_rec = u.abnormalPercentageRecombinations(firm, dates[i], mdatabase)
            if abn_pcr_rec == -1:
                continue
            x = u.generateXList(firm, dates[i], mdatabase, pdatabase1, pdatabase2, False)
            if not x:
                continue
            lists['dependent'].append(dependent_var)
            lists['AbnPcrOld'].append(abn_pcr_old)
            lists['AbnPcrOldXAbnRet'].append(abn_pcr_old * abn_ret_next)
            lists['AbnRet'].append(abn_ret_next)
            lists['AbnPcrRecombinations'].append(abn_pcr_rec)
            lists['AbnPcrRecombinationsXAbnRet'].append(abn_pcr_rec * abn_ret_next)
            lists['Stories'].append(x[0])
            lists['AbnStories'].append(x[1])
            lists['Terms'].append(x[2])
            lists['MCap'].append(x[3])
            lists['BM'].append(x[4])
            lists['AbnRetVect'].append(x[5])
            lists['AbnVol'].append(x[6])
            lists['AbnVolitility'].append(x[7])
            lists['Illiq'].append(x[8])
        # Invalid date
        if len(lists['dependent']) == 0:
            unused_dates.append(dates[i])
            continue
        # Create pandas data frame and run regression with statsmodels
        df = pd.DataFrame({"Y": lists['dependent'], "B1": lists['AbnPcrOld'], "B2": lists['AbnPcrOldXAbnRet'],
                           "B3": lists['AbnRet'], "S1": lists['AbnPcrRecombinations'],
                           "S2": lists['AbnPcrRecombinationsXAbnRet'], "G1": lists['Stories'],
                           "G2": lists['AbnStories'], "G3": lists['Terms'], "G4": lists['MCap'],
                           "G5": lists['BM'], "G6": lists['AbnRetVect'],  "G7": lists['AbnVol'],
                           "G8": lists['AbnVolitility'], "G9": lists['Illiq']})
        # 'HAC' for heteroscedasticity and autocorrelation, statsmodels uses Newey-West SE by default
        result = sm.ols(formula="Y ~ B1 + B2 + B3 + S1 + S2 + G1 + G2 + G3 + G4 + G5 + G6 + G7 + G8 + G9",
                        data=df).fit(cov_type='HAC', cov_kwds={'maxlags': 1})
        coefficients['a'] += result.params.Intercept
        coefficients['b1'] += result.params.B1
        coefficients['b2'] += result.params.B2
        coefficients['b3'] += result.params.B3
        coefficients['s1'] += result.params.S1
        coefficients['s2'] += result.params.S2
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
        standard_errrors['b1se'] += result.bse.B1 ** 2
        standard_errrors['b2se'] += result.bse.B2 ** 2
        standard_errrors['b3se'] += result.bse.B3 ** 2
        standard_errrors['s1se'] += result.bse.S1 ** 2
        standard_errrors['s2se'] += result.bse.S2 ** 2
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
    num_dates_used = len(dates) - t2 - len(unused_dates)  # -t2 to account for extra days appended
    print(num_dates_used)
    return {key: coefficients[key]/num_dates_used for key in coefficients}, \
           {key: (standard_errrors[key]/(num_dates_used**2))**0.5 for key in standard_errrors}





