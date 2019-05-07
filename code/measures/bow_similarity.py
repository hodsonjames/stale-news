from article import Article
from measure_constants import MeasureConstants

import numpy as np
import datetime
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

stemDict = dict() # dict from stem to index, for faster set comparisons
wordDict = dict() # dict from word to stem

def stem(tokenizedWords):
    """
    Returns a list of stemmed words.
    """
    #ft.begin("stem")
    #r = [stemmer.stem(word) for word in tokenizedWords]
    r = []
    for word in tokenizedWords:
        if word in wordDict:
            add = stemDict[wordDict[word]]
        else:
            w = ps.stem(word)
            add = stemDict.get(w)
            if (add == None):
                add = len(stemDict)
                stemDict[w] = add
            wordDict[word] = w
        r += [add]
    #ft.end("stem")
    return r

def stop(tokenizedWords):
    """Returns a list of with stop words removed."""
    #ft.begin("stop")
    filtered_sentence = set() 
    for w in tokenizedWords: 
        if w not in stop_words: 
            filtered_sentence.add(w) 
    #ft.end("stop")
    return list(filtered_sentence)

class BOWSimilarity:

    def __init__(self, measure_const = MeasureConstants()):
        self.measure_const = measure_const

    def stem_and_filter(self, text):
        """
        Takes an article's text and tokenizes the article text into a set, then
        removes stop words from the set and stems all the remaining words. Returns
        a set of stemmed words in the article.
        """
        tokenized = stop(stem(word_tokenize(text.lower())))
        # stemmed = {ps.stem(w) for w in tokenized}
        # stemmed.difference_update(stop_words) # Remove stop words from tokenized text
        return set(tokenized)

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
        stemmed_articles = list(article_set)
        sim_scores = [self.bow_similarity_score(curr_article_stemmed, s.article_text) 
                      for s in stemmed_articles]
        
        closest_articles_indices = np.argsort(sim_scores)[::-1][:num_closest]
        closest_articles = np.take(stemmed_articles, closest_articles_indices)
        closest_articles_union = set().union(*[s.article_text for s in closest_articles])
        intersect_with_closest_n = curr_article_stemmed.intersection(closest_articles_union)
        
        old_score = len(intersect_with_closest_n) / len(curr_article_stemmed)
        closest_neighbor_score = self.bow_similarity_score(curr_article_stemmed, closest_articles[0].article_text)
        closest_neighbor_id = closest_articles[0].md5_id
        
        return old_score, closest_neighbor_score, closest_neighbor_id

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