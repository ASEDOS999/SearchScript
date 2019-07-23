import sys
sys.path.append('../../../ScriptExtract')
from TextProcessing import graph_construct as GC
from TextProcessing import get_file_actions_inform as GFIA
import os
import pickle

def try_(i):
	list_ = ['text3_13.txt', 'text2_9.txt', 'text2_16.txt', 'text1_4.txt', 'text3_15.txt', 'text3_16.txt', 'text2_17.txt']
	if i in list_:
		return False
	for j in os.listdir():
		if i[4:-4] in j:
			return False
	return True

def get_inform(name_file = 'README.md'):
	keys = [0., 0., 0., 0.]
	length = [0., 0., 0., 0.]
	num = [0, 0, 0, 0]
	dict_ = dict()
	for i in os.listdir():
		if '.pickle' in i and i != 'attr.pickle':
			with open(i, 'rb') as f:
				cur = pickle.load(f)
				f.close()
			length[3] += len(cur)
			num[3] += 1
			for j in cur:
				keys[3] += len(j[0].keys())
				for key in j[0].keys():
					dict_[key] = None
			if '1_' in i:
				length[0] += len(cur)
				num[0] += 1
				for j in cur:
					keys[0] += len(j[0].keys())
			if '2_' in i:
				length[1] += len(cur)
				num[1] += 1
				for j in cur:
					keys[1] += len(j[0].keys())
			if '3_' in i:
				length[2] += len(cur)
				num[2] += 1
				for j in cur:
					keys[2] += len(j[0].keys())
	f = open(name_file, 'w')
	f.write('# Information about files\n\n## Actions Number\n\n')
	for i in range(4):
		if i < 3:
			f.write('- Actions' + str(i+1) + '_\n\n')
		else:
			f.write('- Full Inform\n\n')
		f.write('-- Actions Number: ' + str(length[i]) + '\n\n')
		f.write('-- Documents Number: ' + str(num[i]) + '\n\n')
		f.write('-- Mean Actions Number: ' + str(length[i]/num[i]) + '\n\n')
		f.write('-- Mean Attributes Number: ' + str(keys[i]/length[i]) + '\n\n')
	f.write('Number of unique keys in attributes: ' + str(len(dict_.keys())) + '\n\n')
	keys = list(dict_.keys())
	keys.sort()
	attr = list()
	list_ = ['VERB', 'punct']
	for i in keys:
		for j in keys:
			if not(i in list_ or j in list_):
				if not (j, i) in attr:
					attr.append((i, j))
	f.write('Number of unique keys for pair-attributes: ' + str(len(dict_.keys())) + '\n\n')
	f.close()
	with open('attr.pickle', 'wb') as f:
		pickle.dump(attr, f)
		f.close()


results = []
path = '../../../Texts/'
l = len(os.listdir(path))
n = 0
for i in os.listdir(path):
	n += 1
	print(i, float(n) / l * 100, '%')
	if '.txt' in i and try_(i):
		handle = open(path + i, "r")
		text = handle.read()
		handle.close()
		list_ = GC(text).get_list()
		GFIA(list_, 'Actions' + i[4:-4] + '.pickle')
get_inform()
