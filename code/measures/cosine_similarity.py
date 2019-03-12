import nml_parseutil
from article import Article
from measure_constants import MeasureConstants

import numpy as np
import datetime
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import ngrams, FreqDist

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

class CosineSimilarity:

    def __init__(self, measure_const = MeasureConstants()):
        self.measure_const = measure_const

    def term_frequency(article_text):
    	"""
    	Arguments:
    		article_text: A set containing all of the stemmed words in an article.

    	Returns: a vector representing term frequencies for each word in the article.


    	"""

    def stem_and_filter(article):
        """
        Takes an Article object and tokenizes the article text into a list, then
        removes stop words from the list and stems all the remaining words. Returns
        a set of stemmed words in the article.
        """
        text = article.article_text
        tokenized = set(text.split())
        tokenized.difference_update(stop_words) # Remove stop words from tokenized text
        stemmed = {ps.stem(w) for w in tokenized}
        return stemmed

    def old_and_closest_neighbor_score(curr_article, article_set, num_closest=measure_const.NUM_CLOSEST):
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
        
        curr_article_stemmed = curr_article.article_text
        stemmed_articles = [s.article_text for s in article_set]
        sim_scores = [bow_similarity_score(curr_article_stemmed, s) 
                      for s in stemmed_articles]
        
        closest_articles_indices = np.argsort(sim_scores)[::-1][:num_closest]
        closest_articles = np.take(stemmed_articles, closest_articles_indices)
        closest_articles_union = set().union(*closest_articles)
        intersect_with_closest_n = curr_article_stemmed.intersection(closest_articles_union)
        
        old_score = len(intersect_with_closest_n) / len(curr_article_stemmed)
        closest_neighbor_score = bow_similarity_score(curr_article_stemmed, closest_articles[0])
        
        return old_score, closest_neighbor_score

    def is_old_news(old):
        return old > measure_const.OLD_NEWS

    def is_reprint(old, closest_neighbor):
        reprint = (closest_neighbor / old) >= measure_const.CLOSEST_NEIGHBOR_SHARE
        return (old > measure_const.OLD_NEWS) * reprint

    def is_recombination(old, closest_neighbor):
        reprint = (closest_neighbor / old) < measure_const.CLOSEST_NEIGHBOR_SHARE
        return (old > measure_const.OLD_NEWS) * reprint