"""
Class that can compare two different Articles. 
"""

from collections import Counter
import numpy as np
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
import nltk
import heapq
from nltk.stem.porter import *


class Similarity:

	def __init__(self, num_closest = 5, old_news = 0.6, reprint = 0.8, look_back_days = 3):
		self.old_news = old_news
		self.reprint = reprint
		self.num_closest = num_closest
		self.look_back = 86400 * look_back_days

	def staleNewsProcedure(self, ticker, story, companyLL):
		'''
		Performs the stalen news procedure for one article. Returns the similarity 
		information for this article compared to the articles up to 72 hours prior.
		'''
		companyLL.resetCurr()
		compStory = companyLL.nextNode()
		maxpq = []
		while (compStory != None):
			if story.displayDate - compStory.displayDate > self.look_back:
				companyLL.cut();
				break;
			sim = self.similaritytest(story, [compStory])
			heapq.heappush(maxpq, (sim, compStory))
			compStory = companyLL.nextNode()
		largestN = heapq.nlargest(self.num_closest, maxpq)
		old_reprint_recomb = self.stale(story, largestN)
		companyLL.addFront(story)
		if (largestN != []):
			largestacc = largestN[0][1].accessionNumber
			largestsim = largestN[0][0]
		else:
			largestacc = None
			largestsim = None
		if (len(largestN) > 1):
			secondlargestacc = largestN[1][1].accessionNumber
		else:
			secondlargestacc = None
		return [story.displayDate, story.accessionNumber, ticker, len(story.pre), largestacc, secondlargestacc, largestsim, old_reprint_recomb[3], old_reprint_recomb[0], old_reprint_recomb[1], old_reprint_recomb[2]]

	def stale(self, origStory, neighborStories):
		'''
		Determines the staleness of news given origStory and neighborStories.
		''' 
		r = [False, False, False, 0]
		if (len(neighborStories) == 0):
			return r
		else:
			others = [story_tuple[1] for story_tuple in neighborStories]
			stale_score = self.similaritytest(origStory, others)
			stale_max = neighborStories[0][0]
			r[3] = stale_score
			if (stale_score >= self.old_news):
				r[0] = True
				if (stale_max >= self.reprint):
					r[1] = True
				else:
					r[2] = True
			return r

	def preprocessing(self, article):
		"""
		Function that gets run once on every article.
		"""
		raise NotImplementedError

	def similaritytest(self, orig, others):
		"""
		Function used to compare an article to a set of articles, can asume that preprocessing 
		has already ben run on the article.
		"""
		raise NotImplementedError


class BoWSimularity(Similarity):

	def __init__(self, num_closest = 5, old_news = 0.6, reprint = 0.8, look_back_days = 5):
		super().__init__(num_closest, old_news, reprint, look_back_days)
		self.stop_words = set(stopwords.words('english'))
		self.wordDict = dict()
		self.stemmer = PorterStemmer()

	def stem(self, tokenizedWords):
		"""
		returns a set of stemed words.
		"""
		r = set()
		for word in tokenizedWords:
			if word in self.wordDict:
				add = self.wordDict[word]
			else:
				add = self.stemmer.stem(word)
				self.wordDict[word] = add
			r.add(add)
		return r
	
	def stop(self, tokenizedWords):
		"""
		returns a set with stop words removed.
		"""
		filtered = set()
		for word in tokenizedWords:
			if word not in self.stop_words:
				filtered.add(word)
		return filtered

	def preprocessing(self, article):
		article.pre = self.stop(self.stem(word_tokenize(article.text)))

	def similaritytest(self, orig, others):
		"""
		returns a similarity score between stemmed article orig 
		and a listed of stemmed articles.
		"""
		B = set.union(*[story.pre for story in others])
		A = orig.pre.intersection(B)
		return len(A) / len(orig.pre)

class CosineSimilarity(Similarity):
	def __init__(self, num_closest = 5, old_news = 0.6, reprint = 0.8, look_back_days = 5):
		super().__init__(num_closest, old_news, reprint, look_back_days)
		self.stop_words = set(stopwords.words('english'))
		self.wordDict = dict()
		self.stemmer = PorterStemmer()

	def stem(self, tokenizedWords):
		"""
		returns a set of stemed words.
		"""
		r = list()
		for word in tokenizedWords:
			if word in self.wordDict:
				add = self.wordDict[word]
			else:
				add = self.stemmer.stem(word)
				self.wordDict[word] = add
			r.append(add)
		return r
	
	def stop(self, tokenizedWords):
		"""
		returns a set with stop words removed.
		"""
		filtered = Counter()
		for word in tokenizedWords:
			if word not in self.stop_words:
				filtered[word] += 1
		return filtered

	def preprocessing(self, article):
		article.pre = self.stop(self.stem(word_tokenize(article.text)))
		article.norm = np.sqrt(np.sum([np.square(article.pre[key]) for key in article.pre]))

	def similaritytest(self, orig, others):
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


		if len(others) > 1:
			new = Counter()
			[new.update(art.pre) for art in others]
			temp2 = np.sqrt(np.sum([np.square(new[key]) for key in new]))
		else:
			new = others[0].pre
			temp2 = others[0].norm
			
		sim = 0
		for key in orig.pre:
			if key in new:
				sim += new[key]*orig.pre[key]

		temp1 = orig.norm
		

		return sim / (temp1 * temp2)