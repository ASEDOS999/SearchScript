import sys
sys.path.append('../ScriptExtract')
from TextProcessing import graph_construct as GC

import os

from collections import OrderedDict
def extract_sections(list_result):
	result = OrderedDict()
	for i in list_result:
		name = i['Section']
		if not name is None and not result.__contains__(name):
			result[name] = None
	return result

def extract(name_file):
	f = open(name_file, 'r')
	text = f.read()
	f.close()
	list_ = GC(text).get_list()
	return extract_sections(list_)

def create_file(name_file, list_sections):
	f = open('Sections' + name_file, 'w')
	for i in list(list_sections.keys()):
		f.write(i)
	f.close()

def try_(i):
	list_ = ['text3_13.txt', 'text2_9.txt', 'text2_16.txt', 'text1_4.txt', 'text3_15.txt', 'text3_16.txt', 'text2_17.txt']
	if i in list_:
		return False
	for j in os.listdir():
		if i in j:
			return False
	return True
results = []
l = len(os.listdir('../Texts'))
n = 0
for i in os.listdir('../Texts'):
	n += 1
	print(i, float(n) / l * 100, '%')
	if '.txt' in i and try_(i):
		cur = extract('../Texts/' + i)
		create_file(i, cur)
