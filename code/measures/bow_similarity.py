import nml_parseutil

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

company_article_map = nml_parseutil.create_article_map("2001_sample_10M.nml")

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

def stem_and_filter(article):
    """
    Takes an Article object and tokenizes the article text into a list, then
    removes stop words from the list and stems all the remaining words. Returns
    a list of stemmed words in the article.
    """
    text = article.article_text
    tokenized = word_tokenize(text)
    no_stop_words = [w for w in tokenized if w not in stop_words]
    stemmed = [ps.stem(w) for w in no_stop_words]
    return stemmed

def bow_similarity_score(s1, s2):
    """
    Returns the bag-of-words similarity score between an article s1 and article s2.
    Specifically, measures percentage of words in s1 that are also in s2. 
    s1, s2 must be tokenized and stemmed articles.
    """
    return len(set(s1).intersection(s2)) / len(set(s1))

def articles_older_than(article, article_set):
    """
    Takes in a list or set of articles pertaining to the same company
    as article, and returns a new list containing all articles in 
    article_set which were published earlier than article.
    """
    return list(filter(lambda x: x < article, article_set))

def old_and_closest_neighbor_score(curr_article, article_set, num_closest=5):
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
    
    article_list = articles_older_than(curr_article, article_set)

    sim_scores = []
    stemmed_articles = []
    
    curr_article_stemmed = stem_and_filter(curr_article)
    
    for article in article_list:
        stemmed_and_filtered = stem_and_filter(article)
        stemmed_articles.append(stemmed_and_filtered)
        sim_scores.append(bow_similarity_score(curr_article_stemmed, stemmed_and_filtered))
    
    curr_article_stemmed_unique = set(curr_article_stemmed)
    closest_articles_indices = np.argsort(sim_scores)[::-1][:num_closest]
    closest_articles = [stemmed_articles[i] for i in closest_articles_indices]
    closest_articles_union = set().union(*closest_articles)
    intersect_with_closest_n = curr_article_stemmed_unique.intersection(closest_articles_union)
    
    old_score = len(intersect_with_closest_n) / len(curr_article_stemmed_unique)
    closest_neighbor_score = bow_similarity_score(curr_article_stemmed, closest_articles[0])
    
    return old_score, closest_neighbor_score

def is_old_news(article, article_set, num_closest=5):
    old, closest_neighbor = old_and_closest_neighbor_score(article, article_set, num_closest)
    return old > 0.6

def is_reprint(article, article_set, num_closest=5):
    old, closest_neighbor = old_and_closest_neighbor_score(article, article_set, num_closest)
    reprint = (closest_neighbor / old) >= 0.8
    return (old > 0.6) * reprint

def is_recombination(article, article_set, num_closest=5):
    old, closest_neighbor = old_and_closest_neighbor_score(article, article_set, num_closest)
    recomb = (closest_neighbor / old) < 0.8
    return (old > 0.6) * recomb

def precomputed_is_reprint(old, closest_neighbor):
    reprint = (closest_neighbor / old) >= 0.8
    return (old > 0.6) * reprint

def precomputed_is_recombination(old, closest_neighbor):
    reprint = (closest_neighbor / old) < 0.8
    return (old > 0.6) * reprint