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
        2. self.dates: list of contained dates (initially empty)
        """
        self.data = pd.read_csv(file, dtype=datatype, low_memory=False)
        # Drop incomplete rows
        self.data.dropna(inplace=True)
        self.tics = []
        self.dates = []

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


class CRSPDatabase(PandasDatabase):
    """
    Stores database as a pandas data frame
    """

    def __init__(self, file, datatype=None):
        """
        self.abnret: mapping (ticker, date) to abnormal return for firm on date
        self.vol: mapping (ticker, date) to volume for firm on date
        self.firmfrac: mapping (ticker, date) to fraction of shares turned over for firm on date
        self.vwfrac: mapping date to value-weighted average fraction of shares turnover for all firms on date
        self.abnvol: mapping (ticker, date) to firmfrac[(ticker, date)] - vwfrac[date]
        self.mcap: mapping (ticker, date) to market cap for firm on that day
        self.totmcap: mapping date to (sum market caps of all firms, firms available on date)
        self.abnvolit: mapping (ticker, date) to abnormal volatility for firm on date
        self.ill: mapping (ticker, date) to illiquidity measure for firm on date
        """
        super().__init__(file, datatype)
        self.abnret = {}
        self.vol = {}
        self.firmfrac = {}
        self.vwfrac = {}
        self.abnvol = {}
        self.mcap = {}
        self.totmcap = {}
        self.abnvolit = {}
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
    New measures database
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
        1. self.dates: Ordered Dictionary of all dates where key = date, value = None
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


