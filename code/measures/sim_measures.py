from measure_constants import MeasureConstants
from cosine_similarity import CosineSimilarity
from bow_similarity import BOWSimilarity

class SimiliarityMeasure:

	def __init__(self, measure, measure_const = MeasureConstants()):
		self.measure = None
		if measure == "cosine":
			self.measure = CosineSimilarity()
		if measure == "bag_of_words":
			self.measure = BOWSimilarity()