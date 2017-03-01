class Dictionary:
	term = ""
	doc_frequency = 0

	def __init__(self, term):
		self.term = term
		# self.doc_frequency = df

	def __hash__(self):
		return hash(self.term)

	def __eq__(self, other):
		return self.term == other.term

	def __ne__(self, other):
		# Not strictly necessary, but to avoid having both x==y and x!=y
		# True at the same time
		return not(self == other)

class Postings:
	docID = 0
	term_frequency = 0
	tf_idf = 0.0

	def __init__(self, docId, tf):
		self.docID = docId
		self.term_frequency = tf