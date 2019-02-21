# utils.py
# -------
# Helper functions for arguments to regression.py

"""
Functions that interface with measures directory in repo
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
    
"""
Additional functions for regression
"""
def abnormalReturn(firm, date, file):
	"""
        #1
        Difference between firm i's return on date and return on value-weighted
        index of all firms in universe on date
        Uses decimal representation
        Returns FLOAT
    """
    return firmReturn(firm, data, file) - allFirmsReturn(date, file)


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


