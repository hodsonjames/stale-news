# utils.py
# -------
# Helper functions for arguments to regression.py

def abnormalReturn(firm, date, file):
	"""
        Difference between firm i's return on date and return on value-weighted
        index of all firms in universe on date
        Uses decimal representation
        Returns FLOAT
    """
    return firmReturn(firm, data, file) - allFirmsReturn(date, file)


def abnormalReturn(firm, dateStart, dateEnd, file):
	"""
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
        Abnormal trading volume for firm on date defined as difference between the
        fraction of shares turned over for firm on date, and the value-weighted average 
        of the fraction of shares turned over for all firms in universe on date
        Uses decimal representation
        Returns FLOAT
    """
    return firmVolume(firm, data, file) - allFirmsVolume(date, file)

def abnormalVol(firm, dateStart, dateEnd, file):
	"""
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

def stories(firm, date, file):
	"""
        Number of articles published on date tagged with firm that have 
        relevance score greater than 70%
        Returns INTEGER
    """

def abnormalStories(firm, date, file):
	"""
        Difference between the average number of stories over [date-5, date-1] and 
        the average number of stories over [date-60, date-6] for firm
        Returns FLOAT
    """

def terms(firm, date, file):
	"""
        Average number of unique terms in stories published on date, tagged with firm
        Returns FLOAT
    """

def marketCap(firm, date, file):
	"""
        LOG market capitalization of firm as of market open on date
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
		LOG of the illiquidity measure from Amihud, computed as the prior-week average of 
		10**6 * |Ret(firm,date)| / Volume(firm,date)
	"""


