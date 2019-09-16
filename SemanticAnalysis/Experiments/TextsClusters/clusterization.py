# Clusterization

import sys
sys.path.append('../../../ScriptExtract')
from TextProcessing import graph_construct as GC
from TextProcessing import research_action_tree as RAT
import action
sys.path.append('../../')
import sem_analysis as sa
import gensim
import numpy as np
# TEXT PREPROCESSING

# The following two functions are for to transform
# a list from GC.get_list to a list of  sentences with marks of instructions
def transform(sentences, instr_sentence):
	cur_list = list()
	for sentence in sentences:
		if sentence in instr_sentence:
			cur_list.append((1, sentence))
		else:
			cur_list.append((0, sentence))
	return cur_list

def cur_transform(list_):
	new_list = list()
	for i in list_:
		if not i.__contains__('Type') or i['Type'] == 'paragraph':
			_ = list()
			for j in i['Action tree']:
				_ = _ + RAT(j)
			instr_sentence = [act.sentence for act in _]
			_ = transform([_.sentence for _ in action.construct_tree(i['Text'])], instr_sentence)
			item = list()
			S = [-1] + i['Sentences']
			for ind, j in enumerate(_):
				cur = (j[0], i['Text'][(S[ind]):(S[ind+1])])
				item.append(cur)
		else:
			item = cur_transform(i['List'])
		new_list.append(item)
	return new_list

# Segmentation of text to lists, paragraphes and sentences with marking
def text_segmentation(text):
	list_ = GC(text).get_list()
		
	segments = cur_transform(list_)
	
	for i in segments:
		for j in i:
			if type(j)==type('tuple'):
				for k in j:
					if k[1] == '':
						j.remove(k)
			else:
				if j[1] == '':
					i.remove(j)
	for i in segments:
		if len(i) == 0:
			segments.remove(i)
	return segments

# Transform list to tag_ud format
def list2tag_ud(some_list, model):
	new_list = list()
	ind =0
	for i in some_list:
		_ = list()
		for j in i:
			if type(j) == type(tuple()):
				item = (j[0], sa.tag_ud(j[1]))
			else:
				item = list()
				for k in j:
					item.append((k[0], sa.tag_ud(k[1])))
			_.append(item)
		ind+=1
		new_list.append(_)
	return new_list

# SEPARATION OF TEXT TO SCRIPTS STEPS

def get_sentence_center(sentence_tag_ud, model):
	s = np.zeros(300)
	k = 0
	for i in sentence_tag_ud:
		if model.__contains__(i):
			s = s + model[i]
			k+=1
	return s/k

def distance(a, b):
	return np.linalg.norm(a - b)


def trivial_segmentation(path_file, model, table):
	def nearest(full_list_centers):
		c_prev, c_next = None, None
		eps = np.inf
		res = list()
		for _, j in enumerate(full_list_centers):
			if j[0] == 1:
				c_next = (_,j)
				break
		for ind, i in enumerate(full_list_centers):
			if i[0] == 1:
				c_prev = (ind, i)
				res.append((ind, 0.))
				c_next = None
				for _, j in enumerate(full_list_centers[ind+1:]):
					if j[0] == 1:
						c_next = (ind+1+_,j)
						break
			else:
				if not c_prev is None:
					d_prev = distance(c_prev[1][1], i[1])
				else:
					d_prev = 1000
				if not c_next is None:
					d_next = distance(c_next[1][1], i[1])
				else:
					d_next = 1000
				if np.isnan([d_next]).any():
					d_next = 1000
				if np.isnan([d_prev]).any():
					d_prev = 1000
				if d_next > eps and d_prev > eps:
					res.append((None, None))
				elif d_next > d_prev: 
					res.append((c_prev[0], d_prev))
				else:
					res.append((c_next[0], d_next))
		return res
	def segmentation(full_list_centers, sentences, res, full_list):
		prev = None
		cur_text = ''
		cur_item = None
		list_texts = list()
		TU = list()
		TT = list()
		list_tag_ud = list()
		for ind, i in enumerate(res):
			if i[0] == prev and not i[0] is None:
				cur_text = cur_text + sentences[ind]
				TU.append(full_list[ind])
				if not np.isnan(full_list_centers[ind][1]).any():
					cur_item = cur_item + full_list_centers[ind][1]
					k += 1
			else:
				if not i[0] is None:
					prev = i[0]
					if not cur_item is None:
						list_texts.append(cur_text)
						TT.append(cur_item / k)
						list_tag_ud+=(TU)
					TU = list()
					TU.append(full_list[ind])
					cur_text = sentences[ind]
					cur_item = full_list_centers[ind][1]
					k = 1
		list_texts.append(cur_text)
		TT.append(cur_item / k)
		list_tag_ud += TU
		return TT, list_texts, list_tag_ud
	table = [i for i in table if len(i[1]) > 0 and i[2] in [0,1]]
	full_list_centers = [(i[2], get_sentence_center(i[1], model)) 
		for i in table]
	sentences = [i[0] for i in table]
	full_list = [i[1] for i in table]
	res = nearest(full_list_centers)
	TT, list_texts,list_tag_ud = segmentation(full_list_centers, sentences, res, full_list)
	_ = list()
	for ind, i in enumerate(list_texts):
		m = False
		for j in i:
			if j.isalpha() or j.isnumeric():
				m = True
		if not m:
			_.append(ind)
	TT = [i for ind, i in enumerate(TT) if not ind in _]
	list_texts = [i for ind, i in enumerate(list_texts) if not ind in _]
	list_tag_ud = [i for ind, i in enumerate(list_tag_ud) if not ind in _]
	return list_texts, TT, list_tag_ud
	
# Union of texts
def union(list_texts, texts_vectors, TagUd, model, eps = 1.24):
	D = [model.wmdistance(TagUd[ind], TagUd[ind+1])
			for ind, i in enumerate(texts_vectors[:-1])]
	union_list, cur =[], [0]
	for ind, i in enumerate(D):
		if i < eps:
			cur.append(ind+1)
		else:
			union_list.append(cur)
			cur = [ind+1]
	union_list.append(cur)
	_1, _2, _3 = list(), list(), list()
	for i in union_list:
		cur_text, cur_vector, cur_TagUd = '', np.zeros((300,)), []
		for j in i:
			cur_text += list_texts[j] + ' '
			cur_vector += texts_vectors[j]
			cur_TagUd += TagUd[j]
		cur_vector /= len(i)
		_1.append(cur_text)
		_2.append(cur_vector)
		_3.append(cur_TagUd)
	list_texts, texts_vectors, TagUd = _1, _2, _3
	return list_texts, texts_vectors, TagUd
