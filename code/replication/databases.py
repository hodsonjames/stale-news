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
        1. Ordered Dictionary mapping each date to list of relevant news articles
        2. Dictionary mapping each ticker to list of relevant news articles
        """
        super().__init__(file)
        self.dateMap = {}
        self.tickerMap = {}
        for row in self.database:
            if row[2] in self.dateMap:
                self.dateMap.get(row[2]).append(row)
            else:
                self.dateMap[row[2]] = [row]
            if row[1] in self.tickerMap:
                self.tickerMap.get(row[1]).append(row)
            else:
                self.tickerMap[row[1]] = [row]
        self.dateMap = OrderedDict(sorted(self.dateMap.items(), key=lambda t: t[0]))
        # Populate sub-databases for reprints and recombinations
        # self.reprints, self.recombinations = self.generateReprintsRecombinations()

    def generateReprintsRecombinations(self):
        """
        First return value is sub-database with rows corresponding to articles
        classified as reprints, ClosestNeighbor(s)/Old(s) >= 0.8
        Second return value is sub-database with rows corresponding to articles
        classified as recombinations, ClosestNeighbor(s)/Old(s) < 0.8
        """
        reprints = []
        recombinations = []
        for row in self.database:
            if (float(row[4]) >= 0.6) and ((float(row[5]) / float(row[4])) >= 0.8):
                reprints.append(row)
            elif float(row[4]) >= 0.6:
                recombinations.append(row)
        return reprints, recombinations

    def getMatchesReprint(self, identifier, column):
        """
        Returns a list of rows (lists) that have the given identifier in its corresponding column
        from the reprint database
        If no match is found an empty list is returned, len() == 0
        """
        return [row for row in self.reprints if row[column] == identifier]

    def getMatchesRecombination(self, identifier, column):
        """
        Returns a list of rows (lists) that have the given identifier in its corresponding column
        from the recombinations database
        If no match is found an empty list is returned, len() == 0
        """
        return [row for row in self.recombinations if row[column] == identifier]

