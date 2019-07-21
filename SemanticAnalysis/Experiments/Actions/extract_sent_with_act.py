import sys
sys.path.append('../../../ScriptExtract')
from TextProcessing import graph_construct as GC
from TextProcessing import research_action_tree as RAT
from TextProcessing import research_list
from action import construct_sentence as CS
import os

from collections import OrderedDict
def extract(name_file):
	def internal_extract(res):
		ret = list()
		for i in res:
			cur_list = res[i]
			for j in cur_list:
				if j['Type'] == 'paragraph':
					list_ = j['Action List']
					for act in list_:
						ret.append(CS(act.sentence)) 
				if j['Type'] == 'list':
					for key in j['Action List']:
						for _ in j['Action List'][key]:
							for act in _:
								ret.append(CS(act.sentence))
		return ret
	f = open(name_file, 'r')
	text = f.read()
	f.close()
	list_ = GC(text).get_list()
	res = research_list(list_)
	ret = internal_extract(res)
	return ret
def create_file(name_file, action_list):
	f = open('Sections' + name_file, 'w')
	new = OrderedDict()
	for i in action_list:
		new[i] = None
	print(len(new))
	for i in new:
		f.write(i + '\n')
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
path = '../../../Texts/'
l = len(os.listdir(path))
n = 0
for i in os.listdir(path):
	n += 1
	print(i, float(n) / l * 100, '%')
	if '.txt' in i and try_(i):
		cur = extract(path + i)
		create_file(i, cur)
