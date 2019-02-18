"""This file should implement the procedures detailed in the stale news paper.
   This file is still a work in progress. Made by Christopher Gong"""

import xml.etree.ElementTree as ET
import re

with open("../data/data.nml") as f:
    xml = f.read()

q = re.sub(r"(<\?xml[^>]+\?>)", "", xml)
q = re.sub(r"<!DOCTYPE[^>]+>", "", q)
q = "<root>" + q + "</root>"

root = ET.fromstring(q)

from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize

import nltk
nltk.download('stopwords')

stop_words = set(stopwords.words('english')) 

import nltk
nltk.download('punkt')
from nltk.stem.porter import *

stemmer = PorterStemmer()
def stopandstem(text):
    word_tokens = [stemmer.stem(word) for word in word_tokenize(text)]
    filtered_sentence = set() 
  
    for w in word_tokens: 
        if w not in stop_words: 
            filtered_sentence.add(w) 
            
    return filtered_sentence

def article(number):
    art = root[number].find("djnml").find("body").find("text")
    if art is None:
        return ""
    article = ""
    for element in art: #likely slow, fix later
        article += element.text
    return article

def ticker(number):
    tik = root[number].find("djnml").find("head").find("docdata").find("djn").find("djn-newswires").find("djn-mdata").find("djn-coding").find("djn-company")
    tickers = set()
    if tik is None:
        return tickers
    for t in tik:
        tickers.add(t.text)
    return tickers

def tickersandarticle(number):
    return ticker(number), article(number)

#-------------------------------------------------------
#Procedure
## given an article and ticker, classify as old news

articlenumber = 130
tic = ""

# find article and related tickers
t, a = tickersandarticle(articlenumber)

# stem and stop article into set
a = stopandstem(a)

t.remove(tic)

for i in range(1000):
    N = ticker(i).intersection(t)
    if (len(N) > 0):
        #update PQ?
        print("match")