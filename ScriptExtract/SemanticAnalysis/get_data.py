import sys
sys.path.append('../ScriptExtract')
from TextProcessing import graph_construct as GC
from TextProcessing import research_action_tree as RAT
import action
sys.path.append('../')
import sem_analysis as sa
import gensim
import numpy as np
import os
import pickle
def find_cite(text):
	_ = text.split('\n')
	segm = [i.split(' ') for i in _]
	sites = list()
	for ind_p, p in enumerate(segm):
		for ind, word in  enumerate(p):
			if word.count('.')>1 or ('.' in word and word[-1]!= '.'):
				if word[-1] == '.':
						segm[ind_p][ind] = 'САЙТ.'
				else:
					segm[ind_p][ind] = 'САЙТ'
				sites.append(word)
	text = ''
	for i in segm:
		cur = i[0]
		for j in i[1:]:
			cur += ' ' + j
		text += '\n' + cur
	text = text[1:]
	return text, sites

def clear(sentences):
	res = list()
	for i in sentences:
		cond = False
		for j in i:
			cond = cond or j.isalpha() or j.isnumeric()
		if cond:
			res.append(i)
	return res

def splitting_text(text):
	def mysplit(paragraph):
		cur = [paragraph]
		mylist = ['?','.','!']
		for sym in mylist:
			cur = [i.split(sym) for i in cur]
			_ = list()
			for i in cur:
				for ind,j in enumerate(i):
					if ind < len(i) - 1 and len(j) > 0:
						j += sym
						_.append(j)
					elif ind == len(i)-1:
						_.append(j)
			cur = _
		return cur
	paragraphes = text.split('\n')
	sentences = list()
	for i in paragraphes:
		sentences += mysplit(i)
	sentences = [i for ind,i in enumerate(sentences) if len(i) > 0]
	return clear(sentences)

import time
def get_table(list_files):
	l = len(list_files)
	if 'table.pickle' in os.listdir():
		with open('table.pickle', 'rb') as f:
			table = pickle.load(f)
			f.close()
	else:
		table = dict()

	list_files = [i for i in list_files if not i in table]
	keys = [i.split('/')[-1] for i in list_files if not i.split('/')[-1] in table]
	texts = dict()
	for i in list_files:
		f = open(i, 'r')
		texts[i.split('/')[-1]] = f.read()
		f.close()
	texts = {key:find_cite(texts[key])[0] for key in texts}
	texts = {key:splitting_text(texts[key]) for key in texts}

	for key in keys:
		print(key)
		s = time.time()
		text = texts[key]
		res = list()
		for sent in text:
			list_ = GC(sent).get_list()
			new_list = list()
			for i in list_:
				if not i.__contains__('Type') or i['Type'] == 'paragraph':
					_ = list()
					for j in i['Action tree']:
						_ = _ + RAT(j)
					instr_sentence = [act.sentence for act in _]
			is_instr = 0
			if len(instr_sentence) > 0 and sent[-1]!= '?':
				is_instr = 1
			try:
				sent_tag_ud = sa.tag_ud(sent)
			except Exception:
				sent_tag_ud = list()
			res.append((sent, sent_tag_ud, is_instr))
		table[key] = res
		print('Time',(time.time()-s)/60, 'min')
		print('Processed: %d/%d'%(len(table.keys()), l))
		with open('table.pickle', 'wb') as f:
			pickle.dump(res, f)
			f.close()
	return table


path = '../Texts/'
list_files = [path+i for i in os.listdir(path) if '.txt' in i]
list_files.sort()
list_files = [i for i in list_files if '2_' in i] + [i for i in list_files if not '2_' in i]
res = get_table(list_files)
with open('table.pickle', 'wb') as f:
	pickle.dump(res, f)
	f.close()
