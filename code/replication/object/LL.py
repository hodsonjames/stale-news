"""
Specialized linked list for use in the simularity project.
"""

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