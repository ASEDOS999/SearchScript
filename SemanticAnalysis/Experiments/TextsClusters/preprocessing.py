import pickle
import sys
import clusterization
import os
import gensim

# DICT OF TAG_UD

def preproc_one_text(path_file, model):
	handle = open(path_file, "r")
	text = handle.read()
	handle.close()
	new = clusterization.text_segmentation(text)
	newest = clusterization.list2tag_ud(new, model)
	return text, new, newest

from time import sleep
def transform_list(list_files, model):
	if 'data_dict.pickle' in os.listdir():
		with open('data_dict.pickle', 'rb') as f:
			data_dict = pickle.load(f)
			f.close()
	else:
		data_dict = {}
	print(data_dict.keys())
	for i in list_files:
		if not data_dict.__contains__(i):
			try:
				data_dict[i] = preproc_one_text(i, model)
			except Exception:
				print(i, 'no')
		print(i, len(list(data_dict.keys()))/len(list_files))
		with open('data_dict.pickle', 'wb') as f:
			pickle.dump(data_dict, f)
			f.close()
	return data_dict

# EXTRACTING MARKS

def extract(path_file):
	try:
		f = open(path_file, 'r')
	except Exception:
		return None
	res = list()
	for i in f.readlines():
		if 'NEW SEGMENT' in i:
			try:
				mark = float(i[len('**NEW SEGMENT**'):])
			except Exception:
				print(path_file, i[len('**NEW SEGMENT**'):])
				mark = None
			res.append(mark)
	f.close()
	return res

def full_extracting(path = 'MarkedTexts/'):
	d = dict()
	for i in os.listdir(path):
		if '.md' in i:
			res = extract(path+i)
			d[i.split('.')[0]] = res
	with open(path+'Marks.pickle', 'wb') as f:
		pickle.dump(d, f)
		f.close()
	return d

# FULL DATA

def get_full_data():
	with open('data_dict.pickle', 'rb') as f:
		d = pickle.load(f)
		f.close()
	with open('MarkedTexts/Marks.pickle', 'rb') as f:
		marks = pickle.load(f)
		f.close()
	list_files = list(d.keys())
	model = gensim.models.KeyedVectors.load_word2vec_format('../../model.bin', binary=True) 
	model.init_sims(replace=True)
	res = list()
	for i in list_files:
		list_texts, TT, TagUd = clusterization.trivial_segmentation(i, model, d)
		list_texts, texts_vectors, TagUd = clusterization.union(list_texts, TT, TagUd)
		key = i.split('/')[-1].split('.')[0]
		cur_marks = marks[key]
		cur_list = [(i, texts_vectors[ind], cur_marks[ind], TagUd[ind])
			for ind, i in enumerate(list_texts)]
		res.append(cur_list)
	with open('MarkedTexts.pickle', 'wb') as f:
		pickle.dump(res, f)
		f.close()
	return res
		
