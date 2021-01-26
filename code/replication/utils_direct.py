# utils_direct.py
# -------
# Sequential helper functions that take direct input
import numpy as np
import datetime
import calendar


def marketCap(price, shares, sharesUnit=1000):
    """
    Market capitalization
    Returns FLOAT
    """
    # SHROUT in thousands
    shares_out = shares * sharesUnit
    return price * shares_out


def marketCapLN(mcap):
    """
    LN market capitalization
    Returns FLOAT
    """
    return np.log(mcap)


def firmVolumeFrac(volume, shares, sharesUnit=1000):
    """
    Fraction of shares turned over
    Returns FLOAT
    """
    # SHROUT in thousands
    shares_out = shares * sharesUnit
    return volume / shares_out


def illiquidityMeasureDate(ret, vol):
    """
    ln(10**6 * |Ret(firm,date)| / Volume(firm,date))
    Returns FLOAT
    """
    return np.log(10**6 * abs(ret) / vol)


def abnormalReturnDate(fret, aret):
    """
    Difference between firm i's return on date and return on value-weighted
    index of all firms in universe on date
    Returns FLOAT
    """
    return fret - aret


def abnormalVolDate(fVolFrac, afVolFrac):
    """
    Abnormal trading volume for firm on date defined as difference between the
    fraction of shares turned over for firm on date, and the value-weighted average
    of the fraction of shares turned over for all firms in universe on date
    Returns FLOAT
    """
    return fVolFrac - afVolFrac


def firm_size_quintile(firm_mcap, mcap_list):
    """
    Quintile number (1-5) of firm_mcap within sorted mcap_list
    Returns INTEGER
    """
    firm_mcap_index = mcap_list.index(firm_mcap)
    quintile_number = 1
    boundary_index = (len(mcap_list) * quintile_number) // 5
    while quintile_number < 5:
        if firm_mcap_index < boundary_index:
            return quintile_number
        quintile_number += 1
        boundary_index = (len(mcap_list) * quintile_number) // 5
    return quintile_number


def day_of_week(YYYYMMDD):
    """
    Takes date string and returns day of week as number. Monday:0, Tuesday:1, Wednesday:2, Thursday:3, Friday:4
    Saturday and Sunday throw error
    Returns INTEGER
    """
    options = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
    dtday = datetime.datetime.strptime(YYYYMMDD, '%Y%m%d').weekday()
    if calendar.day_name[dtday] in options:
        return options[calendar.day_name[dtday]]
    raise RuntimeError("SUNDAY AND SUNDAY NEWS UNACCOUNTED FOR")

