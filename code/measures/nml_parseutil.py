import datetime
import xml.etree.ElementTree as ET
from dateutil import parser
import sys

class Article:
    
    def __init__(self, company, timestamp, headline, article_text):
        self.company = company
        self.timestamp = parser.parse(timestamp)
        self.headline = headline
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

def filter_old_articles(company_article_map, curr_article, k_hours=72):
    """
    Check the set of articles mapped to curr_article.company, and 
    filter out articles that are at least k_hours older than curr_article. 
    
    Arguments:
        curr_article: An Article object, used to compare time stamps with all other
            articles in company_article_map[curr_article.company]. 
        k_hours: An int, default 72. All articles in company_article_map[curr_article.company] 
            that have at least k_hours elapsed time between that article and 
            curr_article.timestamp will be filtered from the map.
            
    Returns:
        company_article_set: A new set to map to curr_article.company, with 
            old articles filtered out, with "old" specified as k_hours.
    """
    
    k_seconds = k_hours * 60 * 60
    curr_company = curr_article.company
    curr_timestamp = curr_article.timestamp
    
    company_article_set = company_article_map.get(curr_company, "No articles for this company")
    
    if company_article_set == "No articles for this company":
        return set([curr_article])
    
    articles_to_remove = set()
    for article in company_article_set:
        if curr_article.elapsed_time_between(article) >= k_seconds:
            articles_to_remove.add(article)
            
    company_article_set.difference_update(articles_to_remove)
    company_article_set.add(curr_article)
    
    return company_article_set  

def create_article_map(filename, k_hours=72):
    """
    Main parsing function. Takes in a file with .nml extension
    and returns a dictionary with keys that correspond to company symbols,
    and values that are sets of Article objects whose articles are about
    that company. 
    
    Arguments:
        filename: .nml file to parse
        k_hours: Argument passed in to filter_old_articles(). Determines
            article filtering. Default is 72, so articles mapped to any
            given company which are at least 72 hours older than the
            current article being parsed will be filtered from the map.
    
    Returns:
        company_article_map: Map from companies to sets of Articles about
            those companies. The set for each company will contain articles that
            were published within k_hours hours of each other. 
    """
    company_article_map = {}
    curr_file_str = ""
    with open(filename) as myfile:
        while True:
            next_line = next(myfile, "EOF")
            if next_line == "EOF":
                break
            curr_file_str += next_line
            if next_line == "</doc>\n":

                xml_elem = ET.fromstring(curr_file_str)
                company = xml_elem.find(".//djn-company-sig")
                if company is None:
                    curr_file_str = ""
                    continue
                if company[0].attrib.get('about', 'no about value') != 'Y':
                    curr_file_str = ""
                    continue
                company = company[0].text
                timestamp = xml_elem.find(".//djn-mdata").attrib['display-date']
                headline = xml_elem.find(".//headline").text
                all_text = xml_elem.find(".//text")
                article_text = "".join(all_text.itertext())

                new_article = Article(company, timestamp, headline, article_text)
                company_articles = filter_old_articles(company_article_map, new_article, k_hours)
                company_article_map[company] = company_articles

                curr_file_str = ""
    return company_article_map


# Running parser from command line

# if __name__ == "__main__":
# 	filename = sys.argv[1]
# 	company = sys.argv[2]
# 	print(create_article_map(filename)[company])