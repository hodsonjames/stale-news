from article import Article
from measure_constants import MeasureConstants

import numpy as np
import datetime
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
vec = TfidfVectorizer()

class CosineSimilarity:

    def __init__(self, measure_const = MeasureConstants()):
        self.measure_const = measure_const


    def stem_and_filter(self, text):
        """
        Takes an article's text and tokenizes the article text into a set, then
        removes stop words from the set and stems all the remaining words. Returns
        a set of stemmed words in the article.
        """
        tokenized = word_tokenize(text)
        tokenized = [w for w in tokenized if w not in stop_words] # Remove stop words from tokenized text
        stemmed = " ".join([ps.stem(w) for w in tokenized])
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
        curr_article_stemmed = set(curr_article.article_text.split())
        
        stemmed_articles = [curr_article.article_text] + [s.article_text for s in article_set]
        td_matrix = vec.fit_transform(stemmed_articles)

        # Using the following method to calculate cosine similarity between documents:
        # https://stackoverflow.com/questions/8897593/how-to-compute-the-similarity-between-two-text-documents

        # The following line takes the term-document matrix (where each document is represented by a column
        # vector and each row corresponds to a term), and computes the outer product of the term-document
        # matrix with itself. The result is a symmetric matrix, the first row of which is the cosine similarity
        # between the first document and every document in stemmed_articles. Here, I take the first row, and exclude
        # the first item so we don't include curr_article's cosine similarity with itself. 
       	sim_scores = (td_matrix * td_matrix.T).A[0][1:]
        
        closest_articles_indices = np.argsort(sim_scores)[::-1][:num_closest]
        closest_articles = np.take(stemmed_articles, closest_articles_indices)
        closest_articles_words = [c.split() for c in closest_articles]
        closest_articles_union = set().union(*closest_articles_words)
        intersect_with_closest_n = curr_article_stemmed.intersection(closest_articles_union)
        
        old_score = len(intersect_with_closest_n) / len(curr_article_stemmed)
        closest_neighbor_score = self.bow_similarity_score(curr_article_stemmed, closest_articles_words[0])
        
        return old_score, closest_neighbor_score

    def is_old_news(self, old):
        return old > self.measure_const.OLD_NEWS

    def is_reprint(self, old, closest_neighbor):
        if old == 0:
            return False
        reprint = (closest_neighbor / old) >= self.measure_const.CLOSEST_NEIGHBOR_SHARE
        return (old > self.measure_const.OLD_NEWS) * reprint

    def is_recombination(self, old, closest_neighbor):
        if old == 0:
            return False
        reprint = (closest_neighbor / old) < self.measure_const.CLOSEST_NEIGHBOR_SHARE
        return (old > self.measure_const.OLD_NEWS) * reprint