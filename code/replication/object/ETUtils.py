"""
Utilities for using an ElemmentTree.
"""

import xml.etree.ElementTree as ET

def textGetter(filename):
	'''
	A getter function for each article. When next is called, it will return the 
	next article as an XML string. The files are split by the </doc> tag, which is at the end 
	of every article.
	'''
	with open(filename, errors='replace') as nmlFile:
		text = ""
		for line in nmlFile:
			text += line
			if "</doc>" in line:
				yield text
				text = ""


def article(etree):
	'''Given etree, returns the article's text'''
	art = etree.find("djnml").find("body").find("text")
	article = ""
	if art is None:
		return article
	else:
		for element in art:
			article += element.text
		return article


def headline(etree):
	'''Given etree, returns headline'''
	return etree.find("djnml").find("body").find("headline").text


def tickercreator(etree):
	'''Given etree, returns ticker list'''
	tik = etree.find("djnml").find("head").find("docdata").find("djn").find("djn-newswires").find("djn-mdata").find("djn-coding").find("djn-company")
	tickers = []
	if tik is None:
		return tickers
	for t in tik:
		tickers += [t.text]
	return tickers


def accessionNum(etree):
	'''Given etree, returns acession number'''
	return etree.attrib['md5']


def displayDate(etree):
	'''Given etree, returns display date'''
	return etree.find("djnml").find("head").find("docdata").find("djn").find("djn-newswires").find("djn-mdata").attrib['display-date']
