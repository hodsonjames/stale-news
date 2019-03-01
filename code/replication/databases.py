# databases.py
# -------
# Database types and initialization
from collections import OrderedDict


class TextDatabase:
    """
    Stores database as a list of lists
    Each index in the base list corresponds to a row in the database
    The row found at a given index is a list that holds it indexed contents
    """

    def __init__(self, file):
        """
        Takes a file name and return a TextDatabase for the corresponding file
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
        2. self.tdMap: Dictionary mapping each (ticker, date) tuple to list of relevant news articles
        """
        super().__init__(file)
        self.dates = {}
        self.tdMap = {}
        for row in self.database:
            if row[2] not in self.dates:
                self.dates[row[2]] = None
            if (row[1], row[2]) in self.tdMap:
                self.tdMap[(row[1], row[2])].append(row)
            else:
                self.tdMap[(row[1], row[2])] = [row]
        self.dates = OrderedDict(sorted(self.dates.items(), key=lambda t: t[0]))
