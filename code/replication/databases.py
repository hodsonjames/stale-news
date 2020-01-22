# databases.py
# -------
# Database types and initialization
from collections import OrderedDict
import pandas as pd


class PandasDatabase:
    """
    Stores database as a pandas data frame
    """

    def __init__(self, file, datatype=None):
        """
        Takes a file name and creates a data frame for the corresponding file with
        given data types
        datatype is an optional dictionary mapping column name to pandas type
        1. self.tics: list of contained tickers (initially empty)
        2. self.dates: list of contained dates (initially empty), dates are INTEGERS
        3. self.allowed_tics: list of shared tickers between this database and any others in use
        """
        self.data = pd.read_csv(file, dtype=datatype, low_memory=False)
        # Drop incomplete rows
        self.data.dropna(inplace=True)
        self.tics = []
        self.dates = []
        self.allowed_tics = []

    def recordTickers(self, colName, printWarnings=True):
        """
        Creates a list of all unique tickers in the data saved in self.tics
        colName: name of ticker column
        """
        self.tics = self.data[colName].unique().tolist()
        if printWarnings:
            print("DATABASE TICKER SETUP DONE")

    def recordDates(self, colName, printWarnings=True):
        """
        Creates a sorted list of all dates in the data saved in self.dates
        colName: name of date column
        """
        self.dates = self.data[colName].unique().tolist()
        self.dates.sort()
        if printWarnings:
            print("DATABASE DATES SETUP DONE")

    def setAllowedTics(self, allowed):
        """
        Takes in allowed tickers and saves it
        """
        self.allowed_tics = allowed

    def enforceAllowedTics(self, tickers):
        """
        Takes in a list of tickers and returns a new list where any tickers that aren't in self.allowed_tics are removed
        """
        if not self.allowed_tics:
            return tickers
        else:
            permitted = []
            for t in tickers:
                if t in self.allowed_tics:
                    permitted.append(t)
            return permitted


class CRSPDatabase(PandasDatabase):
    """
    Stores database as a pandas data frame
    """

    def __init__(self, file, datatype=None):
        """
        self.abnret: mapping (ticker, date) to abnormal return for firm on date
        self.vol: mapping (ticker, date) to volume for firm on date
        self.firmfrac: mapping (ticker, date) to fraction of shares turned over for firm on date
        self.vwret: mapping date to value-weighted average return for all firms on date
        self.vwfrac: mapping date to value-weighted average fraction of shares turnover for all firms on date
        self.abnvol: mapping (ticker, date) to firmfrac[(ticker, date)] - vwfrac[date]
        self.mcap: mapping (ticker, date) to market cap for firm on that day
        self.totmcap: mapping date to (sum market caps of all firms, firms available on date)
        self.abnvolat: mapping (ticker, date) to abnormal volatility for firm on date
        self.ill: mapping (ticker, date) to illiquidity measure for firm on date
        """
        super().__init__(file, datatype)
        self.abnret = {}
        self.vol = {}
        self.firmfrac = {}
        self.vwret = {}
        self.vwfrac = {}
        self.abnvol = {}
        self.mcap = {}
        self.totmcap = {}
        self.abnvolat = {}
        self.ill = {}


class TextDatabase:
    """
    Stores database as a list of lists
    Each index in the base list corresponds to a row in the database
    The row found at a given index is a list that holds it indexed contents
    """

    def __init__(self, file):
        """
        Takes a file name and creates a TextDatabase for the corresponding file
        """
        with open(file) as f:
            lines = [line.rstrip('\n').split(',') for line in f]
            self.database = lines
        self.rows = len(self.database)
        self.columns = len(self.database[0])

    def getNumRows(self):
        return self.rows

    def getNumCols(self):
        return self.columns

    def getMatches(self, identifier, column):
        """
        Returns a list of rows (lists) that have the given identifier in its corresponding column
        If no match is found an empty list is returned, len() == 0
        """
        return [row for row in self.database if row[column] == identifier]


class MeasuresDatabase(TextDatabase):
    """
    News measures database
    Columns:
    [0] ID of news story
    [1] Stock ticker
    [2] Date YYYYMMDD
    [3] Time 24 hours HH:MM:SS
    [4] Old(s) in decimal
    [5] ClosestNeighbor(s) in decimal
    [6] Length in number of unique terms
    [7] ID closest neighbor story
    [8] ID 2nd closest neighbor story
    """

    def __init__(self, file):
        """
        Populates the measures database and creates:
        1. self.dates: Ordered Dictionary of all dates where key = date, value = None, dates are STRINGS
        2. self.tics: Dictionary of all tickers where key = ticker, value = None
        3. self.tdMap: Dictionary mapping each (ticker, date) tuple to list of relevant news articles
        4. self.aporeg: Empty dictionary for saving AbnPctOld regressions, maps date to regression
        5. self.aprreg: Empty dictionary for saving AbnPctRecombination regressions, maps date to regression
        6. self.pctold: Maps (ticker, date) to percentage old for firm on date
        7. self.pctrec: Maps (ticker, date) to percentage recombinations for firm on date
        8. self.stor: Maps (ticker, date) to count stories for firm on date
        9. self.term: Maps (ticker, date) to average number of terms for firm on date
        """
        super().__init__(file)
        self.dates = OrderedDict()
        self.tics = {}
        self.tdMap = {}
        self.aporeg = {}
        self.aprreg = {}
        self.pctold = {}
        self.pctrec = {}
        self.stor = {}
        self.term = {}
        for row in self.database:
            if row[1] not in self.tics:
                self.tics[row[1]] = None
            if row[2] not in self.dates:
                self.dates[row[2]] = None
            if (row[1], row[2]) in self.tdMap:
                self.tdMap[(row[1], row[2])].append(row)
            else:
                self.tdMap[(row[1], row[2])] = [row]
        self.dates = OrderedDict(sorted(self.dates.items(), key=lambda t: t[0]))

    def putAPOReg(self, date, ols):
        """
        puts date: ols entry in self.aporeg
        """
        self.aporeg[date] = ols

    def removeAPOReg(self, date):
        """
        removes entry for date in self.aporeg
        """
        del self.aporeg[date]

    def putAPRReg(self, date, ols):
        """
        puts date: ols entry in self.aprreg
        """
        self.aprreg[date] = ols

    def removeAPRReg(self, date):
        """
        removes entry for date in self.aprreg
        """
        del self.aprreg[date]


class AdjustableMeasuresDatabase(TextDatabase):
    """
    News measures database
    Columns:
    [0] Date
    [1] Story ID
    [2] Stock ticker
    [3] Length in number of unique terms
    [4] ID closest neighbor story
    [5] ID 2nd closest neighbor story
    [6] ClosestNeighbor(s) in decimal
    [7] Old(s) in decimal
    [8] Old Status
    [9] Reprint Status
    [10] Recombination Status
    """

    def __init__(self, file):
        """
        Populates the measures database and creates:
        1. self.dates: Ordered Dictionary of all dates where key = date, value = None, dates are STRINGS
        2. self.tics: Dictionary of all tickers where key = ticker, value = None
        3. self.tdMap: Dictionary mapping each (ticker, date) tuple to list of relevant news articles
        4. self.aporeg: Empty dictionary for saving AbnPctOld regressions, maps date to regression
        5. self.aprreg: Empty dictionary for saving AbnPctRecombination regressions, maps date to regression
        6. self.pctold: Maps (ticker, date) to percentage old for firm on date
        7. self.pctrec: Maps (ticker, date) to percentage recombinations for firm on date
        8. self.stor: Maps (ticker, date) to count stories for firm on date
        9. self.term: Maps (ticker, date) to average number of terms for firm on date
        8. self.recstor: Maps (ticker, date) to count recombination stories for firm on date
        """
        super().__init__(file)
        self.dates = OrderedDict()
        self.tics = {}
        self.tdMap = OrderedDict()
        self.aporeg = {}
        self.aprreg = {}
        self.pctold = {}
        self.pctrec = {}
        self.stor = {}
        self.term = {}
        self.recstor = {}

        # Skip header row
        skip = True
        for row in self.database:
            if skip:
                skip = False
                continue
            if row[2] not in self.tics:
                self.tics[row[2]] = None
            date = row[0]
            if date not in self.dates:
                self.dates[date] = None
            if (row[2], date) in self.tdMap:
                self.tdMap[(row[2], date)].append(row)
                # another recombination story
                if eval(row[10]):
                    self.recstor[(row[2], date)] += 1
            else:
                self.tdMap[(row[2], date)] = [row]
                if eval(row[10]):
                    self.recstor[(row[2], date)] = 1
                else:
                    self.recstor[(row[2], date)] = 0
        self.dates = OrderedDict(sorted(self.dates.items(), key=lambda t: t[0]))

    def putAPOReg(self, date, ols):
        """
        puts date: ols entry in self.aporeg
        """
        self.aporeg[date] = ols

    def removeAPOReg(self, date):
        """
        removes entry for date in self.aporeg
        """
        del self.aporeg[date]

    def putAPRReg(self, date, ols):
        """
        puts date: ols entry in self.aprreg
        """
        self.aprreg[date] = ols

    def removeAPRReg(self, date):
        """
        removes entry for date in self.aprreg
        """
        del self.aprreg[date]


class BookDatabase:
    """
    Used for cleaned COMPUSTAT
    """

    def __init__(self, file):
        """
        Takes a file name and creates a BookDatabase for the corresponding file
        self.data: maps ticker to list of its relevant data rows
        self.report_date: maps ticker to set of its report dates (datadate)
        self.industry: maps ticker to 2-digit prefix of industry code from NAICS
        """
        self.data = {}
        self.report_date = {}
        self.industry = {}
        with open(file) as f:
            skip = True
            for line in f:
                if skip:
                    # skip header
                    skip = False
                    continue
                # split line of: 0:gvkey,1:datadate,2:fyearq,3:fqtr,4:tic,5:rdq,6:ceqq,7:naics
                current = line.rstrip('\n').split(',')
                if current[4] in self.data:
                    self.data[current[4]].append(current)
                    self.report_date[current[4]].add(current[1])  # updates when self.data updates
                else:
                    self.data[current[4]] = [current]
                    self.report_date[current[4]] = set()
                    self.report_date[current[4]].add(current[1])
                if current[4] not in self.industry:
                    self.industry[current[4]] = current[7]

    def getBookValue(self, firm, date, bookUnit=1000000):
        """
        Firm's book value as of latest quarterly earnings report preceding date
        Performs modified binary search, no integer cast needed as YYYYMMDD format can be sorted as strings
        Returns -1 if no data available
        Returns FLOAT
        """
        if firm not in self.data:
            return -1
        rows = self.data[firm]
        low_ind = 0
        low_date = rows[low_ind][1]  # uses datadate
        high_ind = len(rows) - 1
        high_date = rows[high_ind][1]
        unadjusted = -1
        if date > high_date:
            unadjusted = float(rows[high_ind][6])
        elif date <= low_date:
            # no data
            return unadjusted
        else:
            mid_ind = (low_ind + high_ind) // 2
            mid_date = rows[mid_ind][1]
            while mid_ind != low_ind:
                if mid_date <= date:
                    low_ind = mid_ind
                    low_date = mid_date
                else:
                    high_ind = mid_ind
                mid_ind = (low_ind + high_ind) // 2
                mid_date = rows[mid_ind][1]
            if low_date == date:
                unadjusted = float(rows[low_ind - 1][6])
            else:
                unadjusted = float(rows[low_ind][6])
        return unadjusted * bookUnit

    def isReportDate(self, firm, date):
        """
        Date is an earnings report date for the firm
        Returns Boolean
        """
        return date in self.report_date[firm]

    def getIndustryCode(self, firm):
        """
        Returns industry code for firm
        Returns String
        """
        two_dig_prefix = self.industry[firm][0:2]
        # 31-33 Manufacturing: map all to 31
        if two_dig_prefix == "32" or two_dig_prefix == "33":
            two_dig_prefix = "31"
        # 44-45 Retail Trade: map all to 44
        if two_dig_prefix == "45":
            two_dig_prefix = "44"
        # 48-49 Transportation and Warehousing: map all to 48
        if two_dig_prefix == "49":
            two_dig_prefix = "48"
        return two_dig_prefix


class ProcessedNewsDatabase:
    """
    Used for extracted NEWS
    """

    def __init__(self, file):
        """
        Takes a file name and creates a ProcessedNewsDatabase for the corresponding file
        self.data: maps each ticker to a dictionary mapping date to stories
        self.dates: Ordered Dictionary of all dates where key = date, value = None, dates are STRINGS
        """
        self.data = {}
        self.dates = OrderedDict()
        with open(file) as f:
            skip = True
            for line in f:
                if skip:
                    # skip header
                    skip = False
                    continue
                # split line of: 0:DATE,1:TICKER,2:STORIES,3:TERMS,4:ABN_PCT_OLD,5:ABN_PCT_REC,6:RECOMB_STORIES
                current = line.rstrip('\n').split(',')
                if current[1] in self.data:
                    self.data[current[1]][current[0]] = int(current[2])
                else:
                    self.data[current[1]] = OrderedDict()
                    self.data[current[1]][current[0]] = int(current[2])
                if current[0] not in self.dates:
                    self.dates[current[0]] = None
            self.dates = OrderedDict(sorted(self.dates.items(), key=lambda t: t[0]))

    def abnormalStories(self, firm, date):
        """
        Difference between the average number of stories over [date-5, date-1] and
        the average number of stories over [date-60, date-6] for firm
        Return -1 if date not compatible
        Returns FLOAT
        """
        dates = list(self.dates.keys())
        if (date not in dates) or (dates.index(date) - 60) < 0:
            return -1
        dateLess60 = dates.index(date) - 60
        stories5to1 = 0
        stories60to6 = 0
        for i in range(60):
            if i < 55:
                if dates[dateLess60 + i] not in self.data[firm]:
                    continue
                stories60to6 += self.data[firm][dates[dateLess60 + i]]
            else:
                if dates[dateLess60 + i] not in self.data[firm]:
                    continue
                stories5to1 += self.data[firm][dates[dateLess60 + i]]
        return (stories5to1 / 5) - (stories60to6 / 55)


class ProcessedMarketDatabase:
    """
    Used for merged COMPUSTAT and CRSP
    """

    def __init__(self, file):
        """
        Takes a file name and creates a ProcessedMarketDatabase for the corresponding file
        self.abn_ret: maps each ticker to a dictionary mapping date to ABN_RET
        self.abn_vol: maps each ticker to a dictionary mapping date to ABN_VOLUME
        self.illiq: maps each ticker to a dictionary mapping date to ILLIQ
        self.abn_volat: maps each ticker to a dictionary mapping date to ABN_VOLATILITY
        self.dates: Ordered Dictionary of all dates where key = date, value = None, dates are STRINGS
        """
        self.abn_ret = {}
        self.abn_vol = {}
        self.illiq = {}
        self.abn_volat = {}
        self.dates = OrderedDict()
        with open(file) as f:
            skip = True
            for line in f:
                if skip:
                    # skip header
                    skip = False
                    continue
                # split line of: 0:DATE,1:TICKER,2:LN_MCAP,3:ILLIQ,4:BM,5:ABN_RET,6:ABN_VOLUME,7:ABN_VOLATILITY,8:EARNINGS,
                #  9:INDUSTRY,10:FIRM_SIZE
                current = line.rstrip('\n').split(',')
                if current[1] in self.abn_ret:
                    self.abn_ret[current[1]][current[0]] = float(current[5])
                else:
                    self.abn_ret[current[1]] = OrderedDict()
                    self.abn_ret[current[1]][current[0]] = float(current[5])
                if current[1] in self.abn_vol:
                    self.abn_vol[current[1]][current[0]] = float(current[6])
                else:
                    self.abn_vol[current[1]] = OrderedDict()
                    self.abn_vol[current[1]][current[0]] = float(current[6])
                if current[1] in self.illiq:
                    self.illiq[current[1]][current[0]] = float(current[3])
                else:
                    self.illiq[current[1]] = OrderedDict()
                    self.illiq[current[1]][current[0]] = float(current[3])
                if current[1] in self.abn_volat:
                    self.abn_volat[current[1]][current[0]] = float(current[7])
                else:
                    self.abn_volat[current[1]] = OrderedDict()
                    self.abn_volat[current[1]][current[0]] = float(current[7])
                if current[0] not in self.dates:
                    self.dates[current[0]] = None
            self.dates = OrderedDict(sorted(self.dates.items(), key=lambda t: t[0]))

    def abnormalReturn(self, firm, date, t1_offset, t2_offset):
        """
        Cumulative abnormal returns for firm over [date + t1_offset, date + t2_offset]
        Return -1 if dates not compatible or if no data available
        Returns FLOAT
        """
        dates = list(self.dates.keys())
        if (date not in dates) or (dates.index(date) + t1_offset) < 0 or (dates.index(date) + t2_offset) >= len(dates):
            return -1
        start_ind = dates.index(date) + t1_offset
        end_ind = dates.index(date) + t2_offset
        ar_sum = 0.0
        for i in range(end_ind - start_ind + 1):
            if dates[start_ind + i] not in self.abn_ret[firm]:
                return -1
            ar_sum += self.abn_ret[firm][dates[start_ind + i]]
        return ar_sum

    def abnormalVol(self, firm, date, t1_offset, t2_offset):
        """
        Average abnormal trading volume (fraction) for firm over [date + t1_offset, date + t2_offset]
        Return -1 if dates not compatible or if no data available
        Returns FLOAT
        """
        dates = list(self.dates.keys())
        if (date not in dates) or (dates.index(date) + t1_offset) < 0 or (dates.index(date) + t2_offset) >= len(dates):
            return -1
        start_ind = dates.index(date) + t1_offset
        end_ind = dates.index(date) + t2_offset
        av_sum = 0.0
        for i in range(end_ind - start_ind + 1):
            if dates[start_ind + i] not in self.abn_vol[firm]:
                return -1
            av_sum += self.abn_vol[firm][dates[start_ind + i]]
        return av_sum / (end_ind - start_ind + 1)

    def illiquidity(self, firm, date, t1_offset, t2_offset):
        """
        Average of illiquidity measure from Amihud over [date + t1_offset, date + t2_offset]
        Return -1 if dates not compatible or if no data available
        Returns FLOAT
        """
        dates = list(self.dates.keys())
        if (date not in dates) or (dates.index(date) + t1_offset) < 0 or (dates.index(date) + t2_offset) >= len(dates):
            return -1
        start_ind = dates.index(date) + t1_offset
        end_ind = dates.index(date) + t2_offset
        ill_sum = 0.0
        for i in range(end_ind - start_ind + 1):
            if dates[start_ind + i] not in self.illiq[firm]:
                return -1
            ill_sum += self.illiq[firm][dates[start_ind + i]]
        return ill_sum / (end_ind - start_ind + 1)

    def abnormalVolatility(self, firm, date, t1_offset, t2_offset):
        """
        Average of AbnVolatility for days in [date + t1_offset, date + t2_offset]
        Return -1 if dates not compatible or if no data available
        Returns FLOAT
        """
        dates = list(self.dates.keys())
        if (date not in dates) or (dates.index(date) + t1_offset) < 0 or (dates.index(date) + t2_offset) >= len(dates):
            return -1
        start_ind = dates.index(date) + t1_offset
        end_ind = dates.index(date) + t2_offset
        avo_sum = 0.0
        for i in range(end_ind - start_ind + 1):
            if dates[start_ind + i] not in self.abn_volat[firm]:
                return -1
            avo_sum += self.abn_volat[firm][dates[start_ind + i]]
        return avo_sum / (end_ind - start_ind + 1)

