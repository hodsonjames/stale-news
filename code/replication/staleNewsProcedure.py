"""This file should implement the procedures detailed in the stale news paper.
   Made by Christopher Gong

   Summary:
The methods below apply the stale news procedure outline in the paper "When Can the Market Identify Stale News? " by Anasteesia Fedyk and James Hodson. The procedure goes through each article in chronological order from multiple sorted nml files, checking its similarity with articles about the same company that have been previously seen by the procedure and are within the last 72 hours. If an article is about multiple companies, the article will be processed once per company. A provided similarity test is used, and key similarity information (DATE_EST, STORY_ID, TICKER, CLOSEST_ID, CLOSEST_SCORE, TOTAL_OVERLAP, IS_OLD, IS_REPRINT, IS_RECOMB) is written to a csv file. 

Optimizations:
Understanding the mere size of the number of articles published in a day, and the decade long amount of data to be processed in this way, key optimizations can be made to drastically reduce the time needed to for the procedure. First, articles are processed one at a time in a getter structure for less memory useage. Theoretically, the procedure can handle an infinite sequence of articles. Second, after an article has been processed, only important informaton is kept, in a story class. Lastly, the stories related to a company are stored in a linked list in reverse chronological order. When processing a new article, only the previous 72 hours of articles are considered, and any older articles will be removed by way of cut (or prune) of the linked list, to never have more than 72 hours of articles for a comapny to be stored. This optimization can be made because the articles are considered in chronological order. """

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
#from functionTimer import *
#ft = FunctionTimer()
import glob
fs = glob.glob('data/*.nml')

#line below needs to be run at least once.
#nltk.download('punkt')
eastern = timezone('US/Eastern')
stop_words = set(stopwords.words('english')) 
stemmer = PorterStemmer()
stemDict = dict() # dict from stem to index, for faster set comparisons
wordDict = dict() # dict from word to stem

#Key functions
def xmlTreeGetter(filename="2001_sample_10M.nml"):
    '''A getter function for each article. When next is called, it will return the next article. 
    The files are split by the </doc> tag, which is at the end of every article.'''
    nmlFile = open(filename)
    text = ""
    for i, line in enumerate(nmlFile):
        text += line
        if "</doc>" in line:
            yield ET.fromstring(text)
            text = ""

#getters for article with a given etree
def article(etree):
    '''Given etree, return article'''
    #ft.begin("article")
    art = etree.find("djnml").find("body").find("text")
    if art is None:
        return ""
    article = ""
    for element in art: #likely slow, fix later
        article += element.text
    #ft.end("article")
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
    for i in range(len(tik)):
        tickers += [tik[i].text]
    #ft.end("tickercreator")
    return tickers

def accessionNum(etree):
    '''Given etree, return acession number'''
    return etree.attrib['md5']
    #return etree.find("djnml").find("head").find("docdata").find("djn").find("djn-newswires").find("djn-mdata").attrib['accession-number']

def displayDate(etree):
    '''Given etree, reutrn display date'''
    return etree.find("djnml").find("head").find("docdata").find("djn").find("djn-newswires").find("djn-mdata").attrib['display-date']

def stem(tokenizedWords):
    """Returns a list of stemmed words."""
    #ft.begin("stem")
    #r = [stemmer.stem(word) for word in tokenizedWords]
    r = []
    for word in tokenizedWords:
        if word in wordDict:
            add = stemDict[wordDict[word]]
        else:
            w = stemmer.stem(word)
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

def intersection(lst1, lst2): 
    """returns the intersection between two lists"""
    #ft.begin("intersection")
    if (lst1 == None or lst2 == None):
        return []
    lst3 = [value for value in lst1 if value in lst2] 
    #ft.end("intersection")
    return lst3 

def similaritytest(orig, B):
    """returns a similarity score between stemmed article orig and a stemmed article (text)"""
    #ft.begin("similaritytest")
    r = len(intersection(orig.textWords, B.textWords)) / len(orig.textWords)
    #ft.end("similaritytest")
    return r

def stale(origStory, neighborStories, simtest):
    '''Determines the staleness of news given origStory and neighborStories. '''
    #ft.begin("stale")
    if (len(neighborStories) == 0):
        return [False, False, False, 0]
    origWords = set(origStory.text)

    #neighborWords = ""
    #for storyTuple in neighborStories:
    #    neighborWords += " " + storyTuple[1].text
    #print(neighborWords)
    neighborWords = ''.join([storyTuple[1].text for storyTuple in neighborStories])
    intersectionall = simtest(origStory, Story(neighbor = neighborWords))
    intersectionmax = neighborStories[0][0] #first element of storyTuple
    #print(intersectionall, intersectionmax)
    r = [False, False, False, intersectionall]
    if (intersectionall >= 0.6):
        #print("old.")
        r[0] = True
        if (intersectionmax >= 0.8):
            #print("reprint.")
            r[1] = True
        else:
            #print("recombination.")
            r[2] = True
    #ft.end("stale")
    return r

def staleNewsProcedure(ticker, story, companies, simtest):
    '''Performs the stalen news procedure for one article. Returns the similarity information for this
    article compared to the articles up to 72 hours prior. '''
    #ft.begin("staleNewsProcedure")
    companyLL = companies[ticker]
    companyLL.resetCurr()
    compStory = companyLL.nextNode()
    maxpq = []
    while (compStory != None):
        if story.displayDate - compStory.displayDate > 259200:
            companyLL.cut();
            break;
        sim = simtest(story, compStory)
        heapq.heappush(maxpq, (sim, compStory)) #optimize here by limiting five? but already cut
        compStory = companyLL.nextNode()

    largestFive = heapq.nlargest(5, maxpq)
    #print(largestFive)
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
    #ft.end("staleNewsProcedure")
    return [story.displayDate, story.accessionNumber, ticker, len(story.textWords), largestacc, secondlargestacc, largestsim, old_reprint_recomb[3], old_reprint_recomb[0], old_reprint_recomb[1], old_reprint_recomb[2]]

#Key classes

class Story:
    '''A story class. Contains all of the information useful from each story.'''
    accessionNumber = 0
    displayDate = 0
    tickers = []
    headline = ""
    text = "";
    textWords = []
    sim = -1
    def __init__(self, et=None, neighbor=None):
        #ft.begin("storyinit")
        if (neighbor != None):
            self.text = neighbor
            self.textWords = stop(stem(word_tokenize(neighbor)))
        else:
            self.accessionNumber = accessionNum(et)
            self.displayDate = dateutil.parser.parse(displayDate(et)).timestamp()
            self.tickers = tickercreator(et)
            self.text = article(et)
            self.textWords = stop(stem(word_tokenize(article(et))))
            self.headline = headline(et)
        #ft.end("storyinit")

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
    '''A linked list. One key property of this LL is that the next node can be called with nextNode.
    If cut is called, the LL will be pruned (or cut) at the location of nextNode, so that unnecessary 
    information can be easily removed.'''
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

#actual procedure fn
def procedure(startlocation = 'data', endlocation='export_dataframe.csv', simtest=None, all=True, quiet=True, count=1000):
    '''Performs the procedure for the specified amount of articles. Uses all nml files from startlocation, and exports a csv file
    at endlocation.'''
    #ft.begin("procedure")
    location = sorted(glob.glob(startlocation + '/*.nml'))
    if (all):
        count = -1
    if (simtest == None):
        simtest = similaritytest
    companies = dict()
    mydata = []
    with open(endlocation, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['DATE_EST', 'STORY_ID', 'TICKER', 'STORY_LENGTH', 'CLOSEST_ID', 'SECOND_CLOSEST_ID', 'CLOSEST_SCORE', 'TOTAL_OVERLAP', 'IS_OLD', 'IS_REPRINT', 'IS_RECOMB'])
        for f in location:
            if (not quiet):
                print("File processing...",f)
            xtg = xmlTreeGetter(f)
            c = 0
            while True:
                if (c == count):
                    break
                elif (not quiet and c!= 0 and c % 100 == 0):
                    print(c)
                try:
                    et = next(xtg)
                except:
                    break
                story = Story(et)
                if (story.tickers == []):
                    continue;
                for ticker in story.tickers:
                    if ticker not in companies:
                        companies[ticker] = myLinkedList()
                    p = staleNewsProcedure(ticker, story, companies, simtest)
                    writer.writerow(p)
                c = c + 1
    if (not quiet):
        print("Procedure finished.")
    #ft.end("procedure")
    #print("Procedure Time: ", ft.info["procedure"])
    #ft.revealInfo("infomod.csv")
    #ft.clear()

if __name__ == '__main__':
    procedure(sys.argv[1], sys.argv[2], sys.argv[3])
