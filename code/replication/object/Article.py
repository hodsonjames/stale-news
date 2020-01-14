"""
This file contains the base article class.

Christopher Gong, Jonathan Bodine
"""

import dateutil.parser
import xml.etree.ElementTree as ET

from ETUtils import *

class Article:
	"""
	Class that represents a generic article.
	"""

	def __init__(self, text):
		"""
		Takes as input an XML string, and populates the features of an 
		article. 
		"""
		try:
			et = ET.fromstring(text) # Some articles do not parse correctly.
			self.accessionNumber = accessionNum(et)
			self.displayDate = dateutil.parser.parse(displayDate(et)).timestamp()
			self.tickers = tickercreator(et)
			self.text = article(et)
			self.headline = headline(et)
			self.bad = False
		except:
			self.bad = True
		

	def __lt__(self, other):
		"""
		Used to break ties when ordering in a heap queue.
		"""
		return False
