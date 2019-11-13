from isanlp import PipelineCommon
from isanlp.processor_remote import ProcessorRemote
from isanlp.ru.converter_mystem_to_ud import ConverterMystemToUd
import os
import numpy as np
import pandas as pd
import time
import pickle

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class tree:
	def __init__(self, value, sentence = None):
		self.value = value
		self.kids = []
		self.sentence = None

	def add_child(self, value, mytype = None):
		self.kids.append((value, mytype))

class word:
	def __init__(self, lemma, postag, morph, begin , end, index, role = None):
		self.lemma = lemma
		self.postag = postag
		self.morph = morph
		self.index = index
		self.begin = begin
		self.end = end
		self.role = role
		self.anaphor_resolution = None
		
def get_tree(text):
	from isanlp import PipelineCommon
	from isanlp.processor_remote import ProcessorRemote
	from isanlp.ru.converter_mystem_to_ud import ConverterMystemToUd
	from Parser.some_reparser import extract_semantic_relations
	HOST = 'localhost'
	proc_morph = ProcessorRemote(HOST, 3333, 'default')
	proc_syntax = ProcessorRemote(HOST, 3334, '0')

	syntax_ppl = PipelineCommon([
		(proc_morph,
			['text'],
			{'tokens' : 'tokens', 'sentences' : 'sentences', 'postag' : 'postag', 'lemma' : 'lemma'}),
		(proc_syntax,
			['tokens','sentences'],
			{'syntax_dep_tree' : 'syntax_dep_tree'}),
		(ConverterMystemToUd(),
			['postag'],
			{'postag' : 'postag', 'morph' : 'morph'})
		])
	try:
		analysis_res = syntax_ppl(text)
	except:
		return None
	sentences = []
	for i in analysis_res['sentences']:
		sentence = []
		for j in range(i.begin, i.end):
			sentence.append(analysis_res['tokens'][j].text)
		sentences.append(sentence)
	vertices_list_list = []
	relations = extract_semantic_relations(text)
	for j in range(len(analysis_res['lemma'])):
		vertices_list = []
		for i in range(len(analysis_res['lemma'][j])):
			start, end = analysis_res['tokens'][i].begin, analysis_res['tokens'][i].end
			role_vert = []
			for rel in relations:
				if rel['child']['start'] == start and rel['child']['end'] == end:
					role_vert.append(rel['tp'])
			vert = tree(word(analysis_res['lemma'][j][i],
					analysis_res['postag'][j][i],
					analysis_res['morph'][j][i],
					start, end,
					i,
					role = role_vert))
			vertices_list.append(vert)
		vertices_list_list.append(vertices_list)
	root_list = []
	for i in range(len(vertices_list_list)):
		list_ = vertices_list_list[i]
		for j in range(len(analysis_res['syntax_dep_tree'][i])):
			_ = analysis_res['syntax_dep_tree'][i][j]
			if _.parent != -1:
				list_[_.parent].add_child(list_[j], _.link_name)
			else:
				list_[j].sentence = sentences[i]
				root_list.append(list_[j])
	return root_list

def get_subtree(root, postag = 'NOUN', res = None, parent = (None, None)):
	if res is None:
		res = list()
	lemma_list = ['он', 'она', 'они', 'оно']
	#lemma_list += ['этот', 'тот', 'такой']
	if root.value.postag == postag:
		if postag == 'PRON':
			if root.value.lemma in lemma_list:
				res.append((root, parent))
		else:
			if len(root.value.lemma) > 1:
				res.append((root, parent))
	for i in root.kids:
		res = get_subtree(i[0], postag, res, (root.value, i[1]))
	return res

def separation_to_sentences(text):
	list_points = []
	for ind,i in enumerate(text):
		if i in ['?', '.', '!', '\n']:
			list_points.append(ind)
	_, ind = [], 0
	while ind < len(list_points):
		while ind<len(list_points)-1 and list_points[ind+1] - list_points[ind] == 1:
			ind += 1
		_.append(list_points[ind])
		ind+=1
	list_points = [-1] + _
	if list_points[-1] != len(text)-1:
		list_points[-1] = len(text)
	sentences = [text[i+1:list_points[ind+1]+1] for ind, i in enumerate(list_points[:-1])]
	sentences = [(i, len(i.split())) for i in sentences]
	return sentences

def get_antecedents(root, ind, s, s1, sent):
	nouns_subtrees = get_subtree(root, postag = 'NOUN')
	cur_res = []
	for root_subtree in nouns_subtrees:
		root_subtree, parent = root_subtree
		cur_res.append({'subtree' : root_subtree,
			'sent_num' : ind,
			'index_text' : s + root_subtree.value.index,
			'index_sent' : root_subtree.value.index,
			'start_symb' : s1 + root_subtree.value.begin,
			'end_symb' : s1 + root_subtree.value.end,
			'parent_value' : parent[0],
			'dependence' : parent[1],
			'role' : root_subtree.value.role,
			'context' : sent,
			})
	return cur_res

def get_anaphors(root, ind, s, s1, sent):
	pron_subtrees = get_subtree(root, postag = 'PRON')
	cur_res = []
	for root_subtree in pron_subtrees:
		root_subtree, parent = root_subtree
		cur_res.append({'subtree' : root_subtree,
			'sent_num' : ind,
			'index_text' : s + root_subtree.value.index,
			'index_sent' : root_subtree.value.index,
			'start_symb' : s1 + root_subtree.value.begin,
			'end_symb' : s1 + root_subtree.value.end,
			'parent_value' : parent[0],
			'dependence' : parent[1],
			'role' : root_subtree.value.role,
			'context' : sent
			})
	return cur_res

def get_antecedent_anaphor(text):
	sentences = separation_to_sentences(text)
	antecedents, anaphors = [], []
	s, s1 = 0, 0
	for ind, item in enumerate(sentences):
		sentence, num_token = item
		root = get_tree(sentence)
		if not root is None and len(root) > 0:
			root = root[0]
			sent = (root.sentence)
			antecedents = antecedents + get_antecedents(root, ind, s, s1, sent)
			anaphors = anaphors + get_anaphors(root, ind, s, s1, sent)
		s += num_token
		s1 += len(sentence)
	return antecedents, anaphors

def get_antecedents_(text, with_tree = False):
	sentences = separation_to_sentences(text)
	antecedents = []
	s, s1 = 0, 0
	roots = []
	for ind, item in enumerate(sentences):
		sentence, num_token = item
		root = get_tree(sentence)
		if not root is None and len(root) > 0:
			root = root[0]
			sent = (root.sentence)
			roots.append(root)
			antecedents = antecedents + get_antecedents(root, ind, s, s1, sent)
		else:
			roots.append(None)
		s += num_token
		s1 += len(sentence)
	return antecedents, roots, sentences
import time
def anaphora_resolution(text):
	antecedents, roots, sentences = get_antecedents_(text)
	antecedents = [transform_elem(i) for i in antecedents]
	s, s1 = 0, 0
	global __location__
	path = os.path.join(__location__, 'Model/model.pickle')
	f = open(path, 'rb')
	model = pickle.load(f)
	f.close()
	for ind, root in enumerate(roots):
		if not root is None:
			sent = root.sentence
			anaphors = get_anaphors(root, ind, s, s1, sent)
			for anaphor in anaphors:
				anaphor_root = anaphor['subtree'].value
				anaphor_transformed = transform_elem(anaphor)
				cand = get_candidates_for_anaphor(anaphor_transformed, antecedents)
				pairs = cand
				pairs = [binarize_pair(pair) for pair in pairs]
				df = process_pairs(pairs)
				try:
					res = anaphora_resolve(df, model)
					ant = cand[res][0]
					anaphor_root.anaphor_resolution = ant.copy()
				except:
					print('Bad anaphor', anaphor)
		s += sentences[ind][1]
		s1 += len(sentences[ind][0])
	return roots, sentences

def transform_elem(elem):
	new_elem = {}
	attention = ['subtree', 'parent_value']
	for i in elem:
		if not i in attention:
			new_elem[i] = elem[i]
	new_elem['TokenLemma'] = elem['subtree'].value.lemma
	morph = elem['subtree'].value.morph
	for i in morph:
		new_elem['TokenMorph:'+i] = morph[i]
	parent = elem['parent_value']
	if not parent is None:
		morph = parent.morph
		for i in morph:
			new_elem['ParentMorph:'+i] = morph[i]
	return new_elem

def condition_gender(ant, anaph):
	key = 'TokenMorph:Gender'
	_ = ['Mask', 'Neut']
	if key in ant and key in anaph and anaph['TokenMorph:fPOS'] == 'PRON':
		mark = ant[key] == anaph[key]
		if anaph[key] in _ and ant[key] in _:
			mark = True
		if anaph['TokenLemma'] == 'свой':
			mark = True
	else:
		mark = True
	return mark

def condition_number(ant, anaph):
	key = 'TokenMorph:Number'
	return ant[key]==anaph[key]

def condition_match(ant,anaph):
	return condition_number(ant,anaph) and condition_gender(ant, anaph)

def get_candidates_for_anaphor(anaphor, antecedents, lim = 3):
	start = 0
	candidates = []
	sent_num = anaphor['sent_num']
	while sent_num - antecedents[start]['sent_num'] > lim:
		start += 1
	if sent_num-antecedents[start]['sent_num'] < 0:
		if condition_match(antecedents[ind], anaphor):
			candidates.append((antecedents[start], anaphor))
	ind = start
	while ind < len(antecedents) and 0 <= sent_num - antecedents[ind]['sent_num'] <= lim:
		if condition_match(antecedents[ind], anaphor):
			candidates.append((antecedents[ind], anaphor))
		ind += 1
	return candidates

def binarize_pair(pair):
	def transform_elem(elem , features):
		new_elem = dict()
		for i in features:
			if i in elem:
				if len(features[i]) == 0:
					new_elem[i] = elem[i]
				else:
					for j in features[i]:
						new_elem[i+':'+j] = int(elem[i]==j)
			else:
				if len(features[i]) == 0:
					new_elem[i] = 0
				else:
					for j in features[i]:
						new_elem[i+':'+j] = 0
		return new_elem
	global __location__
	path = os.path.join(__location__, 'Model/binarizator.pickle')
	f = open(path, 'rb')
	feat_ant, feat_anaph = pickle.load(f)
	f.close()
	ant, anaph = pair
	new_ant = transform_elem(ant, feat_ant)
	new_anaph = transform_elem(anaph, feat_anaph)
	return new_ant, new_anaph

def process_pairs(pairs):
	global __location__
	path = os.path.join(__location__, 'Model/keys.pickle')
	try:
		f = open(path, 'rb')
		keys_ant, keys_anaph = pickle.load(f)
		f.close()
	except:
		keys_ant = pairs[0][0]
		keys_anaph = pairs[0][1]
		keys_ant = ['Ant:'+i for i in keys_ant]
		keys_anaph = ['Anaph:'+i for i in keys_anaph]
		keys_ant.sort()
		keys_anaph.sort()
		f = open(path, 'wb')
		pickle.dump((keys_ant, keys_anaph), f)
		f.close()
	keys = keys_ant + keys_anaph
	df = {i:[] for  i in keys}
	for i in pairs:
		anaph, ant = i[1], i[0]
		for key in keys_anaph:
			key_ = ':'.join(key.split(':')[1:])
			df[key].append(anaph[key_])
		for key in keys_ant:
			key_ = ':'.join(key.split(':')[1:])
			df[key].append(ant[key_])
	return pd.DataFrame.from_dict(df)[keys]
	
def anaphora_resolve(df, model):
	X = preprocess(df)
	return np.argmax(model.predict_proba(X)[:,1])

def preprocess(df):
	X = df
	keys = ['sent_num', 'index_text', 'index_sent', 'start_symb', 'end_symb']
	for key in keys:
		X['diff_'+key] = X['Anaph:'+key]-X['Ant:'+key]
	X['index'] = X['Anaph:index_text']
	for key in keys:
		del X['Anaph:' + key], X['Ant:'+key]
	index, dist = X['index'].values, X['diff_' + 'index_sent'].values
	res = {i:[] for i in index}
	for ind, i in enumerate(index):
		res[i].append((dist[ind],ind))
	def transform(res):
		list_ = []
		u = []
		for i in res:
			cur = res[i]
			cur.sort(key = lambda x: x[0])
			u.append(len(cur))
			list_ += [(ind, i[1]) for ind,i in enumerate(cur)]
		res = list_.copy()
		for i in list_:
			res[i[1]] = i[0]
		return res
	X['Distance'] = transform(res)
	del X['index']
	return X.values
