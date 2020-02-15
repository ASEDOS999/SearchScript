from preproc import process
from ufal.udpipe import Model, Pipeline
import os
import re
import sys

def tag_ud(text, modelfile='udpipe_syntagrus.model'):
	udpipe_model_url = 'https://rusvectores.org/static/models/udpipe_syntagrus.model'
	udpipe_filename = udpipe_model_url.split('/')[-1]

	if not os.path.isfile(modelfile):
		print('UDPipe model not found. Downloading...', file=sys.stderr)
		wget.download(udpipe_model_url)

	model = Model.load(modelfile)
	process_pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
	s = ''
	for i in text:
		if isalpha(i) and i == ' ':
			s = s + i
	text = s
	output = process(process_pipeline, text=text)
	return output

import numpy as np

def distance_center_cos(phrase1, phrase2, type_distance = 'cos', model = None):
	def get_center(list_words):
		vectors = [model[i] for i in list_words]
		center = np.zeros(vectors.shape)
		for i in vectors:
			center += vectors
		return center / len(vectors)
	c1, c2 = get_center(phrase1), get_center(phrase2)
	if type_distance == 'cos':
		return c1.dot(c2)/ (np.linalg.norm(c1) * np.linalg.norm(c2))
	if type_distance == 'l2':
		return np.linalg.norm(c1-c2)

def get_max(first_list_of_sentence, second_list_of_sentence, model = None, calc_distance = None):
	if model is None:
		model = gensim.models.KeyedVectors.load_word2vec_format('model.bin', binary=True)
	if calc_distance is None:
		calc_distance = model.wmdistance
	l1, l2 = first_list_of_sentence, second_list_of_sentence
	def transform(some_list):
		new_list = list()
		for i in some_list:
			new_list.append(tag_ud(i))
		return new_list
	research1, research2 = transform(l1), transform(l2)
	list_ = dict()
	n = 0
	for idx1, i in enumerate(research1):
		for idx2, j in enumerate(research2):
			cur = model.wmdistance(i, j)
			#print(float(n) / (len(research1) * len(research2)))
			if i != j and cur != 'Unknown':
				if not list_.__contains__(cur):
					list_[cur] =  []
				list_[cur].append((l1[idx1], l2[idx2]))
			n+=1
	return list_
