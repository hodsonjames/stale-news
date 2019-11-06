""" 
This file should implement the procedures detailed in the stale news paper.
Code originally by Christopher Gong,
Optimized by Jonathan Bodine.

Summary:
The methods below apply the stale news procedure outline in the paper 
"When Can the Market Identify Stale News? " by Anasteesia Fedyk and James Hodson. 
The procedure goes through each article in chronological order from multiple sorted 
nml files, checking its similarity with articles about the same company that have 
been previously seen by the procedure and are within the last 72 hours. If an article 
is about multiple companies, the article will be processed once per company.
A provided similarity test is used, and key similarity information 
(DATE_EST, STORY_ID, TICKER, CLOSEST_ID, CLOSEST_SCORE, TOTAL_OVERLAP, 
IS_OLD, IS_REPRINT, IS_RECOMB) is written to a csv file. 

Optimizations:
Understanding the mere size of the number of articles published in a day, 
and the decade long amount of data to be processed in this way, key optimizations 
can be made to drastically reduce the time needed to for the procedure. First, 
articles are processed one at a time in a getter structure for less memory useage. 
Theoretically, the procedure can handle an infinite sequence of articles. Second, 
after an article has been processed, only important informaton is kept, in a story 
class. Third, the stories related to a company are stored in a linked list in reverse 
chronological order. When processing a new article, only the previous 72 hours of 
articles are considered, and any older articles will be removed by way of cut 
(or prune) of the linked list, to never have more than 72 hours of articles 
for a comapny to be stored. This optimization can be made because the articles 
are considered in chronological order.
"""

import xml.etree.ElementTree as ET
import re
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
import nltk
from nltk.stem.porter import *
from pytz import timezone
import dateutil.parser
import datetime
import heapq
import numpy as np
import csv
import sys
import os
import time
from multiprocessing import Process, Queue, Pipe, cpu_count

import glob

fs = glob.glob('data/*.nml')
eastern = timezone('US/Eastern')
stop_words = set(stopwords.words('english')) 
stemmer = PorterStemmer()
stemDict = dict()
wordDict = dict() 


def xmlTreeGetter(filename):
	'''
	A getter function for each article. When next is called, it will return the 
	next article. The files are split by the </doc> tag, which is at the end 
	of every article.
	'''
	nmlFile = open(filename)
	text = ""
	for line in nmlFile:
		text += line
		if "</doc>" in line:
			yield ET.fromstring(text)
			text = ""


def article(etree):
	'''Given etree, return article'''
	art = etree.find("djnml").find("body").find("text")
	article = ""
	if art is None:
		return article
	else:
		for element in art:
			article += element.text
		return article


def headline(etree):
	'''Given etree, return headline'''
	return etree.find("djnml").find("body").find("headline").text


def tickercreator(etree):
	'''Given etree, return ticker list'''
	#ft.begin("tickercreator")
	tik = etree.find("djnml").find("head").find("docdata").find("djn").find("djn-newswires").find("djn-mdata").find("djn-coding").find("djn-company")
	tickers = []
	if tik is None:
		return tickers
	for t in tik:
		tickers += [t.text]
	return tickers


def accessionNum(etree):
	'''Given etree, return acession number'''
	return etree.attrib['md5']


def displayDate(etree):
	'''Given etree, reutrn display date'''
	return etree.find("djnml").find("head").find("docdata").find("djn").find("djn-newswires").find("djn-mdata").attrib['display-date']


def stem(tokenizedWords):
	"""
	returns a set of stemed words.
	"""
	r = set()
	for word in tokenizedWords:
		if word in wordDict:
			add = wordDict[word]
		else:
			add = stemmer.stem(word)
			wordDict[word] = add
		r.add(add)
	return r


def stop(tokenizedWords):
	"""
	returns a set with stop words removed.
	"""
	filtered = set()
	for word in tokenizedWords:
		if word not in stop_words:
			filtered.add(word)
	return filtered


def similaritytest(orig, others):
	"""
	returns a similarity score between stemmed article orig 
	and a listed of stemmed articles.
	"""
	B = set.union(*[story.textWords for story in others])
	A = orig.textWords.intersection(B)
	return len(A) / len(orig.textWords)


def stale(origStory, neighborStories, simtest):
	'''
	Determines the staleness of news given origStory and neighborStories.
	''' 
	r = [False, False, False, 0]
	if (len(neighborStories) == 0):
		return r
	else:
		others = [story_tuple[1] for story_tuple in neighborStories]
		stale_score = simtest(origStory, others)
		stale_max = neighborStories[0][0]
		r[3] = stale_score
		if (stale_score >= 0.6):
			r[0] = True
			if (stale_max >= 0.8):
				r[1] = True
			else:
				r[2] = True
		return r


def staleNewsProcedure(ticker, story, companies, simtest):
	'''
	Performs the stalen news procedure for one article. Returns the similarity 
	information for this article compared to the articles up to 72 hours prior.
	'''
	companyLL = companies[ticker]
	companyLL.resetCurr()
	compStory = companyLL.nextNode()
	maxpq = []
	while (compStory != None):
		if story.displayDate - compStory.displayDate > 259200:
			companyLL.cut();
			break;
		sim = simtest(story, [compStory])
		heapq.heappush(maxpq, (sim, compStory))
		compStory = companyLL.nextNode()
	largestFive = heapq.nlargest(5, maxpq)
	old_reprint_recomb = stale(story, largestFive, simtest)
	companies[ticker].addFront(story)
	if (largestFive != []):
		largestacc = largestFive[0][1].accessionNumber
		largestsim = largestFive[0][0]
	else:
		largestacc = None
		largestsim = None
	if (len(largestFive) > 1):
		secondlargestacc = largestFive[1][1].accessionNumber
	else:
		secondlargestacc = None
	return [story.displayDate, story.accessionNumber, ticker, len(story.textWords), largestacc, secondlargestacc, largestsim, old_reprint_recomb[3], old_reprint_recomb[0], old_reprint_recomb[1], old_reprint_recomb[2]]


class Story:
	'''A story class. Contains all of the information useful from each story.'''
	accessionNumber = 0
	displayDate = 0
	tickers = []
	headline = ""
	text = "";
	textWords = set()
	sim = -1
	def __init__(self, et=None):
		self.accessionNumber = accessionNum(et)
		self.displayDate = dateutil.parser.parse(displayDate(et)).timestamp()
		self.tickers = tickercreator(et)
		self.text = article(et)
		self.textWords = stop(stem(word_tokenize(article(et))))
		self.headline = headline(et)

	def from_other(self, number, date, tick, txt, s):
		self.acessionNumber = number
		self.displayDate = date
		self.tickers = tick
		self.text = txt
		self.sim = s


	def __lt__ (self, other):
		if (type(other) == int):
			return self.sim < other
		return self.sim < other.sim


class myLinkedList:
	'''
	A linked list. One key property of this LL is that the next node can be 
	called with nextNode.If cut is called, the LL will be pruned (or cut) at 
	the location of nextNode, so that unnecessary information can be easily 
	removed.
	'''
	head = None
	end = None
	curr = None
	def __init__(self):
		self.head = LLNode("sentinel")
		self.end = self.head

	def addFront(self, val):
		self.head.nextNode = LLNode(val, self.head.nextNode)

	def resetCurr(self):
		self.curr = self.head

	def nextNode(self):
		self.curr = self.curr.nextNode
		if (self.curr == None):
			return None
		t = self.curr.val
		return t

	def cut(self):
		self.curr.nextNode = None

class LLNode():
	val = None;
	nextNode = None;
	def __init__(self, val=None, nextNode=None):
		self.val = val
		self.nextNode = nextNode


def processor(q, simtest, temp_save):
	"""
	Worker that will process a que of stories.
	"""
	with open(temp_save, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(['DATE_EST', 'STORY_ID', 'TICKER', 'STORY_LENGTH', 'CLOSEST_ID', 'SECOND_CLOSEST_ID', 'CLOSEST_SCORE', 'TOTAL_OVERLAP', 'IS_OLD', 'IS_REPRINT', 'IS_RECOMB'])
		companies = dict()
		while True:
			story, ticker = q.get(block=True)
			if ticker == "ad mortem":
				break
			if ticker not in companies:
				companies[ticker] = myLinkedList()
			p = staleNewsProcedure(ticker, story, companies, simtest)
			writer.writerow(p)


def supplier(pipe, Story):
	"""
	Worker that cleanes stories.
	"""
	while True:
		et = pipe.recv()
		if et == "ad mortem":
			break
		else:
			pipe.send(Story(et))


def merge(endlocation, temp_files):
	"""
	Merges together sorted files into one laregr file.  Deletes the temo_files
	after the megre.
	"""
	files = [open(file, 'r') for file in temp_files]
	filedata = {i: csv.reader(file, delimiter=',') for i, file in enumerate(files)}
	temp = list()
	for i in range(len(temp_files)):
		next(filedata[i])
		newline = next(filedata[i])
		heapq.heappush(temp, (newline[0], i, newline))
	with open(endlocation, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(['DATE_EST', 'STORY_ID', 'TICKER', 'STORY_LENGTH', 'CLOSEST_ID', 'SECOND_CLOSEST_ID', 'CLOSEST_SCORE', 'TOTAL_OVERLAP', 'IS_OLD', 'IS_REPRINT', 'IS_RECOMB'])
		while temp:
			_, f, data = heapq.heappop(temp)
			writer.writerow(data)
			try:
				newline = next(filedata[f])
			except StopIteration:
				newline = None
			if newline:
				heapq.heappush(temp, (newline[0], f, newline))
	[file.close() for file in files]
	[os.remove(file) for file in temp_files]


def worker_init(count, t, simtest=None):
	"""
	starts up the worker processes.
	"""
	workers, worker_processes = list(), list()
	for i in range(count):
		if t == "supplier":
			a, b = Pipe()
			worker = Process(target=supplier, args=((b), (Story)))
			worker.start()
			workers.append(a)
			worker_processes.append(worker)
		elif t == "processor":
			temp_save = f"temp_file_{i}.csv"
			queue = Queue()
			worker = Process(target=processor, args=((queue), (simtest), (temp_save)))
			worker_processes.append(worker)
			worker.start()
			workers.append(queue)
	return workers, worker_processes


def procedure(startlocation = 'data', endlocation='export_dataframe.csv', simtest=similaritytest, worker_count=-1):
	'''
	Performs the procedure for the specified amount of articles. Uses 
	all nml files from startlocation, and exports a csv file at endlocation.
	'''

	if worker_count < 0:
		worker_count += cpu_count() + 1

	worker_count = worker_count * 2

	location = sorted(glob.glob(startlocation + '/*.nml'))
	companies = dict()
	suppliers, supplier_processes = worker_init(worker_count, "supplier")
	processors, processor_processes = worker_init(worker_count, "processor", simtest)
	for f in location:
		print("File processing...",f)
		xtg = xmlTreeGetter(f)
		
		for supplier in suppliers:
			try:
				et = next(xtg)
			except:
				continue
			supplier.send(et)

		checks, load = 0, 0
		while checks < len(suppliers):
			for supplier in suppliers:
				if checks >= len(suppliers):
					break

				story = supplier.recv() 

				try:
					et = next(xtg)
					supplier.send(et)
				except:
					checks += 1
				
				if not (story.tickers == []):
					for ticker in story.tickers:
						if '.' in ticker:
							continue
						if ticker not in companies:
							companies[ticker] = load
							load = (load + 1) % worker_count
						processors[companies[ticker]].put((story, ticker))

	[a.send("ad mortem") for a in suppliers]
	[w.join() for w in supplier_processes]

	[q.put((None, "ad mortem")) for q in processors]
	[w.join() for w in processor_processes]

	merge(endlocation, [f"temp_file_{i}.csv" for i in range(worker_count)])
	print('Procedure finished')

if __name__ == '__main__':
	start = time.time()
	if len(sys.argv) == 3:
		procedure(sys.argv[1], sys.argv[2])
		print(time.time() - start)
	else:
		print(time.time() - start)
		sys.exit(1)