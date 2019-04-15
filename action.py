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
	def __init__(self, lemma, postag, morph):
		self.lemma = lemma
		self.postag = postag
		self.morph = morph

def construct_tree(text):
	from isanlp.processor_remote import ProcessorRemote
	proc_syntax = ProcessorRemote('localhost', 3334, 'default')
	analysis_res = proc_syntax(text)
	sentences = []
	for i in analysis_res['sentences']:
		sentence = ''
		for j in range(i.begin, i.end):
			sentence = sentence + analysis_res['tokens'][j].text + ' '
		sentences.append(sentence)
	vertices_list_list = []
	for j in range(len(analysis_res['lemma'])):
		vertices_list = []
		for i in range(len(analysis_res['lemma'][j])):
			vert = tree(word(analysis_res['lemma'][j][i],
					analysis_res['postag'][j][i],
					analysis_res['morph'][j][i]))
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

class action:
	def __init__(self, verb, sentence = None, name = None):
		# self.keys = ['VERB', 'SUBJECT', 'OBJECT', 'TIME', 'PLACE', 'PURPOSE', 'WAY']
		self.keys = ['VERB', 'SUBJECT', 'OBJECT', 'OTHER']
		self.inform = dict()
		for i in range(len(self.keys)):
			self.inform[self.keys[i]] = []
		self.inform['VERB'] = verb
		self.name_action = name
		self.action_sentence = sentence

def action_verb(x):
	def is_verb():
		return x.value.postag == 'VERB'
	
	def is_modal():
		list_modal = ['быть', 'являться', 'мочь', 'уметь']
		return (x.value.lemma in list_modal)
	
	def is_indicative():
		return x.value.morph.__contains__('Mood') and x.value.morph['Mood'] == 'Ind'
	
	return is_verb() and is_indicative() and not is_modal()

def process_type(vert, act):
	not_inform = ['punct']
	if vert[1] in not_inform:
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
	act.inform[act.keys[np.array(answer).sum()]].append(vert[0].value)

def get_inform_parent(parent, act):
	return 0


def get_actions(root):
	all_actions = []
	sentence = root.sentence
	def research(parent):
		list = []
		for i in parent.kids:
			list.append(i)
			new_act(i[0], parent)
		return list
	
	def new_act(x, parent):
		if action_verb(x):
			act = action(verb = x.value, sentence = sentence, name = 'Action'+'{' + x.value.lemma +'}')
			get_inform_parent(parent, act)
			information = research(x)
			for j in information:
				process_type(j, act)
			if act is not None:
				all_actions.append(act)
		else:
			research(x)
	
	new_act(root, None)
	return all_actions
