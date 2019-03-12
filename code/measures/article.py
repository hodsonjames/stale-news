import datetime
from dateutil import parser

class Article:
    
    def __init__(self, company, timestamp, headline, article_text):
        self.company = company
        self.timestamp = parser.parse(timestamp)
        self.headline = headline

        # article_text should be stemmed and filtered articles
        self.article_text = article_text
    
    def __repr__(self):
        return self.company + "; " + str(self.timestamp) + "; " + self.headline
    
    def __eq__(self, other):
        if isinstance(other, Article):
            return (self.company == other.company and self.timestamp == other.timestamp and
                self.headline == other.headline)
        return False
    
    def __lt__(self, other):
        """
        Comparison operator for sorting Articles by timestamp. 
        """
        return self.timestamp < other.timestamp
    
    def __hash__(self):
        return hash(self.__repr__())
    
    def elapsed_time_between(self, other):
        """
        Returns the amount of time, in seconds, between the publishing 
        of this Article and another Article, other. 
        """
        elapsed_time = self.timestamp - other.timestamp
        return abs(elapsed_time.total_seconds())