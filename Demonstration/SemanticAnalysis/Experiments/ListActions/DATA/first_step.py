import gensim
from scipy.linalg import block_diag
import time
import sys
sys.path.append('../../..')
import sem_analysis as sa
import pickle
import os
import numpy as np

def first_step(list_files, 
			save_transform = True, name_transform = 'data_transform.pickle', use_old_transform = True,
			save_matrix = True, name_matrix = 'matrix_distance_sentence.pickle', use_old_matrix = True):
	dict_inform = dict()
	dict_sentence = dict()
	for i in list_files:
		with open(i, 'rb') as f:
			cur = pickle.load(f)
			f.close()
		dict_inform[i] = cur
		dict_sentence[i] = [i[1] for i in cur]

	if not use_old_transform or not name_transform in os.listdir():
		dict_sentence_transform = transform_phrases(dict_sentence)
		if save_transform:
			with open(name_transform, 'wb') as f:
				pickle.dump(dict_sentence_transform, f)
				f.close
	else:
		with open(name_transform, 'rb') as f:
			dict_sentence_transform = pickle.load(f)
	print('Phrases were transformed.')

	if not use_old_matrix or not name_matrix in os.listdir():
		D = get_matrix_distance(dict_sentence_transform)
		if save_matrix:
			with open(name_matrix, 'wb') as f:
				pickle.dump(D, f)
				f.close
	else:
		with open(name_matrix, 'rb') as f:
			D = pickle.load(f)
	print('Matrix was gotten.')

	table = create_table(dict_inform, dict_sentence, D)
	return table

def create_table(dict_inform, dict_sentence, D, eps = 1.0):
	keys = list(dict_inform.keys())
	keys.sort()
	table = dict()
	for i in keys:
		table[i] = list()
		for ind, act in enumerate(dict_inform[i]):
			list_ = list()
			for num, d in enumerate(list(D[ind, :])):
				if d < eps:
					list_.append(num)
			neighbours = get_neighbours(list_, dict_inform)
			table[i].append((act, neighbours))
	return table

def get_neighbours(num, dict_inform):
	keys = list(dict_inform.keys())
	keys.sort()
	n = 0
	input_keys = list()
	input_act = list()
	for i in keys:
		for ind, j in enumerate(dict_inform[i]):
			n += 1
			if n in num:
				input_keys.append(i)
				input_act.append(ind)
	return input_keys, input_act

def transform_phrases(dict_phrases):
	new_dict = dict()
	for j in dict_phrases:
		if len(dict_phrases[j]) == 0:
			dict_phrases.pop(j)
		else:
			new_dict[j] = list()
			for i in dict_phrases[j]:
				new_dict[j].append(sa.tag_ud(i))
	return new_dict

def initialize_matrix(dict_phrases):
	list_ = list()
	keys = list(dict_phrases.keys()).copy()
	keys.sort()
	for j in dict_phrases.keys():
		list_.append(np.inf * np.ones((len(dict_phrases[j]), len(dict_phrases[j]))))
	D = block_diag(*np.array(list_))
	phrases = list()
	for j in keys:
		phrases = phrases + dict_phrases[j]
	print(len(phrases))
	return phrases, D

def get_matrix_distance(dict_phrases):
	model = gensim.models.KeyedVectors.load_word2vec_format('../../../model.bin', binary=True) 
	model.init_sims(replace=True)
	phrases, D = initialize_matrix(dict_phrases)
	t = time.time()
	for i in range(D.shape[0]):
		for j in range(i+1, D.shape[1]):
			if D[i, j] != np.inf:
				D[i,j] = model.wmdistance(phrases[i], phrases[j])
				D[j, i] = D[i, j]
			if i == 0 and j == 100:
				print((time.time() - t)/100*D.shape[0]*D.shape[0] * 0.9 * 0.5)
	return D
