import pickle
import sys
import clusterization
import os

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

"""
if __name__ == '__main__':
	path = '../../../Texts/'
	list_files = [path+i for i in os.listdir(path) if '.txt' in i and '2_' in i]
	import gensim
	model = gensim.models.KeyedVectors.load_word2vec_format('../../model.bin', binary=True) 
	model.init_sims(replace=True)
	transform_list(list_files, model)
"""
