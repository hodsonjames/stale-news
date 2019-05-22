# utils_direct.py
# -------
# Sequential helper functions that take direct input
import numpy as np


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

