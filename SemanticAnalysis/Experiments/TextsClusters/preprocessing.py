import pickle
import sys
import clusterization
import os

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
