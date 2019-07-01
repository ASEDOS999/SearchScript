import numpy as np

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
#	from isanlp.processor_remote import ProcessorRemote
#	proc_syntax = ProcessorRemote('localhost', 3334, 'default')
#	analysis_res = proc_syntax(text)
	from isanlp import PipelineCommon
	from isanlp.processor_remote import ProcessorRemote
	from isanlp.ru.converter_mystem_to_ud import ConverterMystemToUd
	
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
	analysis_res = syntax_ppl(text)
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
		self.test_inform = dict()
		for i in self.keys:
			self.inform[i] = []
		self.inform['VERB'] = verb
		self.name_action = name
		self.sentence = sentence
		self.type_action = type_action
		self.section = ''
	
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
	
	def get_test_inform(self):
		dict_ = dict()
		i = 'VERB'
		j = 1
		dict_[i] = self.phrase(self.inform[i][j])
		for i in self.test_inform.keys():
			dict_[i] = []
			for k in self.test_inform[i]:
				dict_[i].append(self.phrase(k[j]))
		return dict_
class action_verb():
	def __init__(self, x, parent = None, dependence = None, with_participle = True):
		self.x, self.parent, self.dependence = x, parent, dependence
		self.with_participle = with_participle
	
	def is_verb(self):
		return self.x.value.postag == 'VERB'
	
	def is_infin(self):
		return self.x.value.morph.__contains__('VerbForm') and self.x.value.morph['VerbForm'] == 'Inf'

	def process_infin(self):
		#print(self.x.value.lemma, self.parent)
		#if not self.parent is None:
		#	print(self.parent.value.lemma, self.parent.value.postag)
		mark = (not self.parent is None and self.parent.value.postag != 'VERB') and self.dependence == 'xcomp'
		#print(mark)
		return mark
	
	def is_indicative(self):
		return (self.x.value.morph.__contains__('Tense') and 
			(self.x.value.morph.__contains__('VerbForm') and self.x.value.morph['VerbForm'] == 'Fin'))
	
	def is_imperative(self):
		return (not self.x.value.morph.__contains__('Tense') and 
			(self.x.value.morph.__contains__('VerbForm') and self.x.value.morph['VerbForm'] == 'Fin') and
			(self.x.value.morph.__contains__('Person') and self.x.value.morph['Person'] == '2'))
	
	def is_advparticiple(self):
		return (self.x.value.postag == 'VERB' and
			self.x.value.morph.__contains__('VerbForm') and
			self.x.value.morph['VerbForm'] == 'Ger')
	
	def is_participle(self):
		return (self.x.value.postag == 'VERB' and
			self.x.value.morph.__contains__('VerbForm') and
			self.x.value.morph['VerbForm'] == 'Part')
	
	def test(self):
		if not self.is_verb():
			return False
		if self.is_infin():
			if self.process_infin():
				return 'Modal'
			else:
				return False
		if self.is_indicative():
			return 'Indicative'
		if self.is_imperative():
			return 'Imperative'
		if self.is_advparticiple():
			return 'Adv_Participle'
		if self.with_participle and self.is_participle():
			return 'Participle'
		return 'Verb'

def ignore_word(vert, parent = None, depend = None):
	def not_inform():
		list_postag = ['PUNCT', 'CCONJ', 'SCONJ']
		return vert[0].value.postag in list_postag
	return not_inform() or action_verb(vert[0], parent, vert[1]).test()

def extract_inform(vert, parent, sentence):
	list_index = []
	def search(root, my_depend):
		for i in root.kids:
			j = i[0]
			if not ignore_word(i, root):
				if i[1] != 'punct':
					list_index.append(j.value.index)
				search(j, i[1])
	if not ignore_word(vert, parent):
		if vert[1] != 'punct':
			list_index.append(vert[0].value.index)
		search(vert[0], vert[1])
	list_index.sort()
	return (vert[0].value, list_index, vert[1])

def process_type(vert, parent = None, act = None):
	if ignore_word(vert, parent):
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
	act.inform[act.keys[np.array(answer).sum()]].append(extract_inform(vert, parent, act.sentence))
	if act.test_inform.__contains__(vert[1]):
		act.test_inform[vert[1]].append(extract_inform(vert, parent, act.sentence))
	else:
		act.test_inform[vert[1]] = [extract_inform(vert, parent, act.sentence)]
def get_inform_parent(parent, dependence, act, x = None):
	if parent is None or act is None or x is None:
		return 0
	if (dependence == 'conj' or action_verb(x, parent, dependence).is_advparticiple()) and action_verb(parent).test():
		if len(act.inform['SUBJECT']) == 0:
			act_new = action(verb = (parent.value, [parent.value.index], None), sentence = act.sentence)
			for i in parent.kids:
				process_type(i, parent, act_new)
			act.inform['SUBJECT'] = act_new.inform['SUBJECT']
	if action_verb(x, parent, dependence).is_participle() and parent.value.postag in ['NOUN', 'PRON']:
			act.inform['SUBJECT'].append(extract_inform((parent, None), None, act.sentence))

def get_actions(root):
	all_actions = []
	sentence = root.sentence
	
	def new_act(x, parent, dependence):
		type_ = action_verb(x, parent, dependence).test()
		if type_:
			name = 'Action%d{%s}'%(x.value.index, x.value.lemma)
			act = action(verb = (x.value, [x.value.index], None),  sentence = sentence, name = name, type_action = type_)
			for i in x.kids:
				process_type(i, x, act)
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
