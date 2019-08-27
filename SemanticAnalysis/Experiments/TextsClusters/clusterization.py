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

def trivial_segmentation(path_file, model):
	def deploy_list(some_list):
		full_list = list()
		for i in some_list:
			cur_list = [j for j in i]
			if len(cur_list) >0 and type(cur_list[0]) != type(tuple()):
				_ = list()
				for j in cur_list:
					_ = _ + j
				cur_list = _
			full_list = full_list + (cur_list)
			return full_list
	def nearest(full_list_centers):
		c_prev, c_next = None, None
		eps = 0.9
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
				if d_next > eps and d_prev > eps:
					res.append((None, None))
				elif d_next > d_prev: 
					res.append((c_prev[0], d_prev))
				else:
					res.append((c_next[0], d_next))
		return res
	def segmentation(full_list_centers, sentences, res):
		prev = None
		cur_text = ''
		cur_item = None
		list_texts = list()
		TT = list()
		for ind, i in enumerate(res):
			if i[0] == prev:
				cur_text = cur_text + sentences[ind][1]
				cur_item = cur_item + full_list_centers[ind][1]
				k += 1
			else:
				if not i[0] is None:
					prev = i[0]
					if not cur_item is None:
						list_texts.append(cur_text)
						TT.append(cur_item / k)
					cur_text = sentences[ind][1]
					cur_item = full_list_centers[ind][1]
					k = 1
		list_texts.append(cur_text)
		TT.append(cur_item / k)
		return TT, list_texts
	handle = open(path_file, "r")
	text = handle.read()
	handle.close()
	new = text_segmentation(text)
	newest = list2tag_ud(new, model)
	full_list = deploy_list(new)
	sentences = deploy_list(newest)
	full_list_centers = [(i[0], get_sentence_center(i[1], model)) 
		for i in full_list]
	res = nearest(full_list_centers)
	TT, list_texts = segmentation(full_list_centers, sentences, res)
	return list_texts, TT
	
