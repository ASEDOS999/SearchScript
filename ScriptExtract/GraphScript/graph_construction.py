from .Preprocessing import TextProcessing
from TextProcessing import table

class vertice:
	def __init__(self, word, sentence):
		self.word = word
		self.sentence = sentence

class Graph:
	def __init__(self, list_files, use_sem = True):
		self.table = table(use_sem).get_table(list_files)

		# Vertices of action V_a, vertices of features V_f and edges between them E_af
		self.V_a, self.V_f, self.E_af = self.get_vertices()
		
		# Additional edges
		self.E = self.add_edges()
		
	def get_vertices(self):
		# ...
				
	
	def add_edges(self):
		# ...
		