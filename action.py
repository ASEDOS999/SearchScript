import numpy as np
import sys
sys.path.append('Participle')
from test import participle_process as PP

class tree:
	def __init__(self, value, sentence = None):
		self.value = value
		self.kids = []
		self.sentence = None

	# The arguments of this function is a value of new vertices
	# and type of relationship between parent and kid
	def add_child(self, value, mytype = None):
		self.kids.append((value, mytype))

class word:
	def __init__(self, lemma, postag, morph, index):
		self.lemma = lemma
		self.postag = postag
		self.morph = morph
		self.index = index

def construct_tree(text):
	from isanlp.processor_remote import ProcessorRemote
	proc_syntax = ProcessorRemote('localhost', 3334, 'default')
	analysis_res = proc_syntax(text)
	sentences = []
	for i in analysis_res['sentences']:
		sentence = []
		for j in range(i.begin, i.end):
			sentence.append(analysis_res['tokens'][j].text)
		sentences.append(sentence)
	vertices_list_list = []
	for j in range(len(analysis_res['lemma'])):
		vertices_list = []
		for i in range(len(analysis_res['lemma'][j])):
			vert = tree(word(analysis_res['lemma'][j][i],
					analysis_res['postag'][j][i],
					analysis_res['morph'][j][i],
					i))
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

def construct_sentence(list_word):
	sentence = ''
	for i in list_word:
		sentence = sentence + i + ' '
	return sentence

class action:
	def __init__(self, verb, sentence = None, name = None, type_action = None):
		# self.keys = ['VERB', 'SUBJECT', 'OBJECT', 'TIME', 'PLACE', 'PURPOSE', 'WAY']
		self.keys = ['VERB', 'SUBJECT', 'OBJECT', 'OTHER']
		self.inform = dict()
		for i in self.keys:
			self.inform[i] = []
		self.inform['VERB'] = verb
		self.name_action = name
		self.sentence = sentence
		self.type_action = type_action
	
	def phrase(self, list_index):
		list_index.sort()
		list_word = [self.sentence[i] for i in list_index]
		return construct_sentence(list_word)
	
	def extract_data_from_dict(self, list_):
		ret_list = []
		for j in range(len(list_)):
			if list_[j]:
				dict_ = dict()
				for i in self.keys:
					if i != 'VERB':
						dict_[i] = []
						for k in self.inform[i]:
							if j == 1:
								dict_[i].append(self.phrase(k[j]))
							else:
								dict_[i].append(k[j])
					else:
						if j == 1:
							dict_[i] = self.phrase(self.inform[i][j])
						else:
							dict_[i] = self.inform[i][j]
				ret_list.append(dict_)
		return ret_list
	
	def get_inform(self, main_word = False, full_inform = False, depend_dict = False):
		list_ = [main_word, full_inform, depend_dict]
		return self.extract_data_from_dict(list_)

class action_verb():
	def __init__(self, x, parent = None, dependence = None, with_participle = True):
		self.x, self.parent, self.dependence = x, parent, dependence
		self.with_participle = with_participle
	
	def is_verb(self):
		return self.x.value.postag == 'VERB'
	
	def is_modal(self):
		list_modal = ['быть', 'мочь', 'уметь', 'умея', 'умев']
		return (self.x.value.lemma in list_modal)
	
	def is_indicative(self):
		ret, sum_ = [], False
		ret.append(self.x.value.morph.__contains__('Mood') and self.x.value.morph['Mood'] == 'Ind')
		for i in ret:
			sum_ = sum_ or i
		return sum_
	
	def adv_participle(self):
		return (self.x.value.postag == 'VERB' and
			self.x.value.morph.__contains__('VerbForm') and
			self.x.value.morph['VerbForm'] == 'Conv')
	
	def is_participle(self):
		parent_postag = None if self.parent is None else self.parent.value.postag
		depend  = None if self.dependence is None else self.dependence
		return PP(self.x, depend, parent_postag).classificate()
	
	def test(self):
		return (((self.is_verb() and self.is_indicative()) or 
			self.adv_participle() or
			(self.with_participle and self.is_participle())) and 
			not self.is_modal())

def ignore_word(vert, parent = None, depend = None):
	def not_inform():
		list_postag = ['PUNCT', 'CCONJ', 'SCONJ']
		return vert[0].value.postag in list_postag
	return not_inform() or action_verb(vert[0], parent, depend).test()

def extract_inform(vert, parent, depend, sentence):
	list_index = []
	def search(root, my_depend):
		for i in root.kids:
			j = i[0]
			if not ignore_word(vert, j, depend):
				if i[1] != 'punct':
					list_index.append(j.value.index)
				search(j, i[1])
	if not ignore_word(vert, parent, depend):
		if vert[1] != 'punct':
			list_index.append(vert[0].value.index)
		search(vert[0], vert[1])
	list_index.sort()
	return (vert[0].value, list_index, depend)

def process_type(vert, parent = None, depend = None, act = None):
	if ignore_word(vert):
		return 0
	if vert[0].value.postag == 'PART':
		act.inform['VERB'][1].append(vert[0].value.index)
		return 0
	subject_type = ['agent', 'nsubj', 'xsubj']
	object_type = ['dobj', 'iobj', 'obj']
	array = [subject_type, 
		object_type]
	answer = [0] * (len(array) + 1)
	for i in range(len(array)):
		answer[i] = i + 1 if vert[1] in array[i] else 0
	if np.array(answer).sum() == 0:
		answer[-1] = len(array) + 1
	act.inform[act.keys[np.array(answer).sum()]].append(extract_inform(vert, parent, depend, act.sentence))

def get_inform_parent(parent, dependence, act, x = None):
	if parent is None or act is None or x is None:
		return 0
	if (dependence == 'conj' or action_verb(x, parent, dependence).adv_participle()) and action_verb(parent).test():
		if len(act.inform['SUBJECT']) == 0:
			act_new = action(verb = (parent.value, [parent.value.index], None), sentence = act.sentence)
			for i in parent.kids:
				process_type(i, parent, i[1], act_new)
			act.inform['SUBJECT'] = act_new.inform['SUBJECT']
	if action_verb(x, parent, dependence).is_participle() and parent.value.postag in ['NOUN', 'PRON']:
			act.inform['SUBJECT'].append(extract_inform((parent, None), None, None, act.sentence))

def get_actions(root):
	all_actions = []
	sentence = root.sentence
	
	def new_act(x, parent, dependence):
		if action_verb(x, parent, dependence).test():
			name = 'Action%d{%s}'%(x.value.index, x.value.lemma)
			act = action(verb = (x.value, [x.value.index], None),  sentence = sentence, name = name)
			for i in x.kids:
				process_type(i, x, i[1], act)
				new_act(i[0], x, i[1])
			get_inform_parent(parent, dependence, act, x)
			if act is not None:
				all_actions.append(act)
		else:
			for i in x.kids:
				new_act(i[0], x, i[1])
	
	new_act(root, None, None)
	return all_actions

def process_path(dependence, marks):
	mytype = ''
	if len(dependence) == 1:
		mytype = dependence[0]
		if mytype == 'ROOT':
			return mytype
		if len(marks) >= 1:
			add = marks[0][0] if len(marks) == 1 else 'nondet_marks'
		else:
			add = 'without_marks'
		mytype = mytype + '{' + add + '}'
		return mytype
	return 'nondet'

def get_actions_tree(root):
	action_list = get_actions(root)
	list_depend = ['mark', 'cc']
	list_postag = ['CCONJ', 'SCONJ']
	def research(x, parent = None, dependence = None, cur_action = None):
		if action_verb(x, parent, dependence[-1]).test():
			act = [i for i in action_list if i.name_action == 'Action%d{%s}'%(x.value.index, x.value.lemma)][0]
			marks = []
			for i in x.kids:
				if (i[1] in list_depend) or (i[0].value.postag in list_postag):
					marks.append((i[0].value.lemma, i[0].value.postag, i[1]))
			vert = tree(act)
			mytype = process_path(dependence, marks)
			cur_action.add_child(value = vert, mytype = mytype)
			cur_action = vert
			dependence = []
		for i in x.kids:
			research(i[0], x, dependence + [i[1]], cur_action)
	action_root = tree(action(verb = None, name = 'ROOT'))
	research(root, cur_action = action_root, dependence = ['ROOT'])
	action_root.sentence = root.sentence
	return action_root
