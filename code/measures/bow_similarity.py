from article import Article
from measure_constants import MeasureConstants

import numpy as np
import datetime
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

class BOWSimilarity:

    def __init__(self, measure_const = MeasureConstants()):
        self.measure_const = measure_const

    def stem_and_filter(self, text):
        """
        Takes an article's text and tokenizes the article text into a set, then
        removes stop words from the set and stems all the remaining words. Returns
        a set of stemmed words in the article.
        """
        tokenized = set(text.split())
        tokenized.difference_update(stop_words) # Remove stop words from tokenized text
        stemmed = {ps.stem(w) for w in tokenized}
        return stemmed

    def bow_similarity_score(self, s1, s2):
        """
        Returns the bag-of-words similarity score between an article s1 and article s2.
        Specifically, measures percentage of words in s1 that are also in s2. 
        s1, s2 must be sets representing tokenized and stemmed articles.
        """
        return len(s1.intersection(s2)) / len(s1)

    def compute_sim_measure(self, curr_article, article_set):
        """
        Calculates Old(s) and ClosestNeighbor(s), where s is curr_article. 
        
        Arguments:
            curr_article: An Article object for which to calculate the scores
            article_set: A set of Article objects with the same company as curr_article.company
            num_closest: The number of closest (by similarity score) stories to look at 
                to calculate Old(s)
        
        Returns:
            old_score: Old(s)
            closest_neighbor_score: ClosestNeighbor(s)
        """
        num_closest = self.measure_const.NUM_CLOSEST 
        
        curr_article_stemmed = curr_article.article_text
        stemmed_articles = [s.article_text for s in article_set]
        sim_scores = [self.bow_similarity_score(curr_article_stemmed, s) 
                      for s in stemmed_articles]
        
        closest_articles_indices = np.argsort(sim_scores)[::-1][:num_closest]
        closest_articles = np.take(stemmed_articles, closest_articles_indices)
        closest_articles_union = set().union(*closest_articles)
        intersect_with_closest_n = curr_article_stemmed.intersection(closest_articles_union)
        
        old_score = len(intersect_with_closest_n) / len(curr_article_stemmed)
        closest_neighbor_score = self.bow_similarity_score(curr_article_stemmed, closest_articles[0])
        
        return old_score, closest_neighbor_score

    def is_old_news(self, old):
        return old > self.measure_const.OLD_NEWS

    def is_reprint(self, old, closest_neighbor):
        reprint = (closest_neighbor / old) >= self.measure_const.CLOSEST_NEIGHBOR_SHARE
        return (old > self.measure_const.OLD_NEWS) * reprint

    def is_recombination(self, old, closest_neighbor):
        reprint = (closest_neighbor / old) < self.measure_const.CLOSEST_NEIGHBOR_SHARE
        return (old > self.measure_const.OLD_NEWS) * reprint