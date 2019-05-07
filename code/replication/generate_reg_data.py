# generate_reg_data.py
# -------
# Functions to write out file with data to run for equations (8), (9), (10), (11), (12), (13) from Section 3
import utils as u
import utilsp as up
import databases as d
import pandas as pd


def generate_csv8_9(dates, firms, mdatabase, pdatabase1, pdatabase2, eight=True):
    """
    Writes csv file for computation over dates given
    dates: list of days in order from starting date to ending date, each date represents a date t used for computation
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    eight: True computes equation 8, False computes equation 9
    """
    # append one day at the end for very last t+1 query
    if not pdatabase1.dates:
        pdatabase1.recordDates("date", False)  # "date" is a col name in crsp
    extra_day_index = pdatabase1.dates.index(int(dates[len(dates) - 1])) + 1
    dates.append(str(pdatabase1.dates[extra_day_index]))
    # store data
    lists = {'dependent': [], 'AbnPctOld': [], 'Stories': [], 'AbnStories': [], 'Terms': [], 'MCap': [],
             'BM': [], 'AbnRet': [], 'AbnVol': [], 'AbnVolitility': [], 'Illiq': [], 'date': []}
    entries = 0
    # -1 to account for extra day appended
    for i in range(len(dates) - 1):
        print("DAY T: " + dates[i])
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
            lists['date'].append(dates[i])
            entries += 1
    # Create pandas data frame and to write out
    df = pd.DataFrame({"date": lists['date'], "dependent": lists['dependent'], "AbnPctOld": lists['AbnPctOld'],
                       "Stories": lists['Stories'], "AbnStories": lists['AbnStories'], "Terms": lists['Terms'],
                       "MCap": lists['MCap'], "BM": lists['BM'], "AbnRet": lists['AbnRet'], "AbnVol": lists['AbnVol'],
                       "AbnVolitility": lists['AbnVolitility'], "Illiq": lists['Illiq']})
    print("ENTRIES: " + str(entries))
    print("COLUMNS: " + str(len(lists.keys())))
    if eight:
        # output fm_data_8_start_end.csv
        df.to_csv('fm_data_8_' + str(dates[0]) + "_" + str(dates[len(dates) - 2]) + ".csv", index=False)
    else:
        # output fm_data_9_start_end.csv
        df.to_csv('fm_data_9_' + str(dates[0]) + "_" + str(dates[len(dates) - 2]) + ".csv", index=False)


def generate_csv10_11(dates, firms, mdatabase, pdatabase1, pdatabase2, ten=True):
    """
    Writes csv file for computation over dates given
    dates: list of days in order from starting date to ending date, each date represents a date t used for computation
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    ten: True computes equation 10, False computes equation 11
    equation (13) uses equation 10 computation, calling this function for each year
    """
    # append one day at the end for very last t+1 query
    if not pdatabase1.dates:
        pdatabase1.recordDates("date", False)  # "date" is a col name in crsp
    extra_day_index = pdatabase1.dates.index(int(dates[len(dates) - 1])) + 1
    dates.append(str(pdatabase1.dates[extra_day_index]))
    # store data
    lists = {'dependent': [], 'AbnPctOld': [], 'AbnPcrRecombinations': [], 'Stories': [], 'AbnStories': [],
             'Terms': [], 'MCap': [], 'BM': [], 'AbnRet': [], 'AbnVol': [], 'AbnVolitility': [], 'Illiq': [],
             'date': []}
    entries = 0
    # -1 to account for extra day appended
    for i in range(len(dates) - 1):
        print("DAY T: " + dates[i])
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
            lists['date'].append(dates[i])
            entries += 1
    # Create pandas data frame and to write out
    df = pd.DataFrame({"date": lists['date'], "dependent": lists['dependent'], "AbnPctOld": lists['AbnPctOld'],
                       "AbnPcrRecombinations": lists['AbnPcrRecombinations'], "Stories": lists['Stories'],
                       "AbnStories": lists['AbnStories'], "Terms": lists['Terms'], "MCap": lists['MCap'],
                       "BM": lists['BM'], "AbnRet": lists['AbnRet'], "AbnVol": lists['AbnVol'],
                       "AbnVolitility": lists['AbnVolitility'], "Illiq": lists['Illiq']})
    print("ENTRIES: " + str(entries))
    print("COLUMNS: " + str(len(lists.keys())))
    if ten:
        # output fm_data_10_start_end.csv
        df.to_csv('fm_data_10_' + str(dates[0]) + "_" + str(dates[len(dates) - 2]) + ".csv", index=False)
    else:
        # output fm_data_11_start_end.csv
        df.to_csv('fm_data_11_' + str(dates[0]) + "_" + str(dates[len(dates) - 2]) + ".csv", index=False)


def generate_csv12(dates, firms, mdatabase, pdatabase1, pdatabase2, t1, t2):
    """
    Writes csv file for computation over dates given
    dates: list of days in order from starting date to ending date, each date represents a date t used for computation
    firms: list of tickers of interest
    mdatabase: database of news measures
    pdatabase1: crsp data frame
    pdatabase2: compustat data frame
    t1, t2: used for AbnRet date range [t+t1, t+t2] where t is current reference day
    """
    # append t2 additional days at the end for last few dependent variable queries
    if not pdatabase1.dates:
        pdatabase1.recordDates("date", False)  # "date" is a col name in crsp
    extra_day_start_index = pdatabase1.dates.index(int(dates[len(dates) - 1])) + 1
    for i in range(t2):
        dates.append(str(pdatabase1.dates[extra_day_start_index + i]))
    # store data
    lists = {'dependent': [], 'AbnPcrOld': [],  'AbnPcrOldXAbnRet': [], 'AbnRet': [], 'AbnPcrRecombinations': [],
             'AbnPcrRecombinationsXAbnRet': [], 'Stories': [], 'AbnStories': [], 'Terms': [], 'MCap': [], 'BM': [],
             'AbnRetVect': [], 'AbnVol': [], 'AbnVolitility': [], 'Illiq': [], 'date': []}
    entries = 0
    # -t2 to account for extra days appended
    for i in range(len(dates) - t2):
        print("DAY T: " + dates[i])
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
            lists['date'].append(dates[i])
            entries += 1
    # Create pandas data frame and to write out
    df = pd.DataFrame({"date": lists['date'], "dependent": lists['dependent'], "AbnPcrOld": lists['AbnPcrOld'],
                       "AbnPcrOldXAbnRet": lists['AbnPcrOldXAbnRet'], "AbnRet": lists['AbnRet'],
                       "AbnPcrRecombinations": lists['AbnPcrRecombinations'],
                       "AbnPcrRecombinationsXAbnRet": lists['AbnPcrRecombinationsXAbnRet'],
                       "Stories": lists['Stories'], "AbnStories": lists['AbnStories'], "Terms": lists['Terms'],
                       "MCap": lists['MCap'], "BM": lists['BM'], "AbnRetVect": lists['AbnRetVect'],
                       "AbnVol": lists['AbnVol'], "AbnVolitility": lists['AbnVolitility'], "Illiq": lists['Illiq']})
    print("ENTRIES: " + str(entries))
    print("COLUMNS: " + str(len(lists.keys())))
    # output fm_data_12_start_end_t1_t2.csv
    df.to_csv('fm_data_10_' + str(dates[0]) + "_" + str(dates[len(dates) - t2 - 1])
              + "_" + str(t1) + "_" + str(t2) + ".csv", index=False)



