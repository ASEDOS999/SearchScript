import action

class text_separation():
	def __init__(self, text):
		self.text = text

	def find_cite(text):
		segm = [i.split(' ') for i in text.split('\n')]
		sites = list()
		for ind_p, p in enumerate(segm):
			for ind, word in  enumerate(p):
				if word.count('.')>1 or ('.' in word and word[-1]!= '.'):
					if word[-1] == '.':
							segm[ind_p][ind] = 'САЙТ.'
					else:
						segm[ind_p][ind] = 'САЙТ'
					sites.append(word)
		text = '\n'.join([' '.join(i) for i in segm])
		return text, sites

	def PartOfList(self, cur_text, all = True):
		def start_analyse():
			i = 0
			# Trash spaces
			while i < len(cur_text) and cur_text[i] == ' ':
				i+= 1
			if i == len(cur_text):
				return False
			# Bulleted List
			mark = cur_text[i] in ['*']
			# Numbered list
			while i < len(cur_text) and cur_text[i].isnumeric():
				i += 1
			if i == len(cur_text):
				return False
			mark = mark or cur_text[i] == '.' or cur_text[i] == ')'
			return mark
		def end_analyse():
			i = len(cur_text) - 1
			while i > -1 and cur_text[i] == ' ':
				i -= 1
			if i == -1:
				return False
			if cur_text[i] in [';', ',']:
				return True
			return False
		def one_sent():
			list_end = ['!', '.', '?']
			indexes = [0] + [ind for ind, i in enumerate(cur_text) if i in list_end]
			sentences = [cur_text[i, indexes[ind+1]] for ind,i in enumerate(indexes[-1])]
			sentences = [i for i in sentences if not i.isnumeric(i)]
			return len(sentences) > 1
		return (end_analyse() or start_analyse()) and (all or one_sent())

	def separate_to_paragraphes(self):
		text = self.text
		list_n = [0]
		for i in range(len(text)):
			if text[i] == '\n':
				list_n.append(i)
		list_n.append(len(text) + 1)
		results = []
		for idx, i in enumerate(list_n):
			if idx < len(list_n) - 1:
				if list_n[idx + 1] - i > 1:
					if text[i] == '\n' and i < len(text) + 1:
						results.append(i+1)
					else:
						results.append(i)
			else:
				if i - list_n[idx - 1] > 1:
					results.append(i)
		return results

	def separate_to_sentence(self, cur_text):
		list_ = []
		N = 0
		num_sent = 0
		for i in range(len(cur_text)):
			if cur_text[i] in ['.', '!', '?', '\n']:
				last = i
				if i + 2 < len(cur_text) and cur_text[i:i+2] == '...':
					last = i + 2
					i += 2
				list_.append(last+1)
				num_sent += 1
		list_.append(len(cur_text) + 1)
		return list_

	def get_structure(self):
		text = self.text
		list_n = self.separate_to_paragraphes()
		results = []
		j = 0
		section_name = None
		while j < len(list_n) - 1:
			cur_text = text[list_n[j] : list_n[j + 1]]
			if list_n[j] != list_n[j + 1]:
				if self.PartOfList(cur_text):
					res = list()
					while self.PartOfList(cur_text):
						res.append(cur_text)
						cur_text = text[list_n[j] : list_n[j+1]]
						j += 1
					item = {
						'Type' : 'list',
						'Elements':res,
						'Sentences': [self.separate_to_sentence(i) for i in res],
						'Text' : ' '.join(res)
					}
					results.append(item)
				else:
					list_sentence = self.separate_to_sentence(cur_text)
					item = {
						'Type' : 'paragraph',
						'Section' : section_name,
						'Text' : cur_text,
						'Sentences' : list_sentence
					}
					results.append(item)
					j += 1
		return results

	def get_advanced_structure(self):
		structure = self.get_structure(self.text)
		list_indexes = list()
		for ind, i in enumerate(structure[:-1]):
			if structure[ind+1]['Type'] == 'list':
				structure[ind]['Text'] += structure[ind+1]['Text']
				structure[ind]['Sentences'][-1] += structure[ind+1]['Text']
				list_indexes.append(ind+1)
		structure = [i for ind,i in enumerate(structure) if not ind in list_indexes]
		return structure

	def get_list_of_tree(self):
		self.structure = self.get_structure()
		for i in self.structure:
			print('TEXT', i['Text'])
			root_list = action.construct_tree(i['Text'])
			i['Synt tree'] = root_list
		# Transform syntactic tree to action tree
		for i in self.structure:
			i['Action tree'] = []
			for root in i['Synt tree']:
				i['Action tree'].append(action.get_actions_tree(root))

		return self.structure














# Different conditions for FAT's DFS
from action import construct_sentence as CS

# Test for roots
def start_proc(act):
	if act.name_action == 'ROOT':
		return True

def there_is_inf(act):
	for i in act.inform.keys():
		if i != 'VERB':
			for j in act.inform[i]:
				morph = j[0].morph
				if morph.__contains__('VerbForm') and morph['VerbForm'] == 'Inf':
					return True
	return False

# Tests for instuctions
def cond_instr(act):
	if start_proc(act):
		return False
	if act.type_action in ['Imperative', 'Modal']:
		return True
	lemma = act.inform['VERB'][0].lemma
	morph = act.inform['VERB'][0].morph
	subj = [i for k in act.inform.keys() for i in act.inform[k] if k in ['agent', 'xsubj', 'nsubj', 'subj'] ]
	if (len(subj) == 0):
			if (morph.__contains__('Person') and morph['Person'] == '3' and 
			morph.__contains__('Number') and morph['Number'] == 'Sing'):
				return lemma != 'быть' and there_is_inf(act)
			if (morph.__contains__('Person') and morph['Person'] == '2' and
			morph.__contains__('Aspect') and morph['Aspect'] == 'Perf'
			and morph.__contains__('Tense') and morph['Tense'] == 'Imp'):
				return True
	if (len(subj) == 1 and 
		morph.__contains__('Person') and morph['Person'] == '2'):
		if morph.__contains__('Aspect') and morph['Aspect'] == 'Imp':
			return lemma != 'быть' and there_is_inf(act)
		if morph.__contains__('Aspect') and morph['Aspect'] == 'Perf':
			return True
	return False

def instructions(act):
	return cond_instr(act)

def research_action_tree(root, test = instructions, list_ = None):
	if list_ is None:
		list_ = []
	if test(root.value):
		list_.append(root.value)
	for i in root.kids:
		list_ = research_action_tree(i[0], test, list_)
	return list_

from collections import OrderedDict
def research_list(list_tree, test = instructions):
	result = OrderedDict()
	for i in list_tree:
		if i['Type'] == 'paragraph':
			new_list = []
			for root in i['Action tree']:
				new_list = new_list + research_action_tree(root, test)
			if not result.__contains__(i['Section']):
				result[i['Section']] = []
			result[i['Section']].append({
					'Type':'paragraph', 
					'Action List' : new_list.copy()
					})
		if i['Type'] == 'list':
			cur = OrderedDict()
			for k in i['List']:
				new_list = []
				for root in k['Action tree']:
					new_list = new_list + research_action_tree(root, test)
				if not cur.__contains__(k['Section']):
					cur[k['Section']] = []
				cur[k['Section']].append(new_list.copy())
			if not result.__contains__(i['Section']):
				result[i['Section']] = []
			result[i['Section']].append({
					'Type':'list', 
					'Action List' : cur.copy()
					})
	return result


def show(result):
	ret = []
	result = research_list(result)
	for i in result.keys():
		print('\n\nSection', i)
		for j in result[i]:
			if j['Type'] == 'paragraph':
				for act in j['Action List']:
					print('Action', act.name_action)
					print('Sentence', CS(act.sentence))
			if j['Type'] == 'list':
				for key in j['Action List'].keys():
					print('\nSection list', key)
					for list_ in j['Action List'][key]:
						for act in list_:
							print('Action', act.name_action)
							print('Sentence', CS(act.sentence))

def get_file(result, name_file = 'out.md'):
	f = open(name_file, 'w')
	ret = []
	result = research_list(result)
	for i in result.keys():
		if not i is None:
			f.write('# Section ' + i)
		for j in result[i]:
			if j['Type'] == 'paragraph':
				for act in j['Action List']:
					f.write('\n\n**' + act.name_action + '**')
					f.write('\n\n*Sentence* ' + CS(act.sentence))
			if j['Type'] == 'list':
				f.write('\n\n## Start Of List')
				for key in j['Action List'].keys():
					f.write('\n\n * **Section list** ' + key)
					for list_ in j['Action List'][key]:
						for act in list_:
							f.write('\n\n**' + act.name_action + '**')
							f.write('\n\n*Sentence*' + CS(act.sentence))
				f.write('\n\n## End Of List')
		f.write('\n'*5)

def print_attributes(f, act):
	f.write('\n\n**' + act.name_action + '**')
	dict_ = act.get_inform(False, True, False)[0]
	keys = list(dict_.keys())
	keys.sort()
	for i in keys:
		f.write('\n\n' + descript_role(i).upper())
		if i != 'VERB':
			for j in dict_[i]:
				f.write('\n\n--' + j)
		else:
			f.write('\n\n--' + dict_[i])

from action import descript_role
def get_file_attributes(result, name_file = 'out.md'):
	f = open(name_file, 'w')
	ret = []
	result = research_list(result)
	for i in result.keys():
		if not i is None:
			f.write('# Section ' + i)
		for j in result[i]:
			if j['Type'] == 'paragraph':
				for act in j['Action List']:
					f.write('\n\n**' + act.name_action + '**')
					f.write('\n\n*Sentence* ' + CS(act.sentence))
					print_attributes(f, act)
			if j['Type'] == 'list':
				f.write('\n\n## Start Of List')
				for key in j['Action List'].keys():
					f.write('\n\n * **Section list** ' + key)
					for list_ in j['Action List'][key]:
						for act in list_:
							f.write('\n\n**' + act.name_action + '**')
							f.write('\n\n*Sentence*' + CS(act.sentence))
							print_attributes(f, act)

def get_file(result, name_file = 'out.md'):
	f = open(name_file, 'w')
	ret = []
	result = research_list(result)
	for i in result.keys():
		if not i is None:
			f.write('# Section ' + i)
		for j in result[i]:
			if j['Type'] == 'paragraph':
				for act in j['Action List']:
					f.write('\n\n**' + act.name_action + '**')
					f.write('\n\n*Sentence* ' + CS(act.sentence))
			if j['Type'] == 'list':
				f.write('\n\n## Start Of List')
				for key in j['Action List'].keys():
					f.write('\n\n * **Section list** ' + key)
					for list_ in j['Action List'][key]:
						for act in list_:
							f.write('\n\n**' + act.name_action + '**')
							f.write('\n\n*Sentence*' + CS(act.sentence))
				f.write('\n\n## End Of List')
		f.write('\n'*5)
import pickle
def get_file_actions_inform(result, name_file = 'data.pickle'):
	def extract(act):
		inform = act.inform
		sent = act.sentence
		s = str()
		dict_ = dict()
		for key in act.inform.keys():
			s = str()
			if key == 'VERB':
				for i in act.inform[key][1]:
					s += ' ' + sent[i]
				dict_[key] = s
			else:
				dict_[key] = list()
				for j in act.inform[key]:
					s= str()
					for i in j[1]:
						s += ' ' + sent[i]
					dict_[key].append(s)
		return (dict_, CS(sent))
	f = open(name_file, 'w')
	ret = []
	result = research_list(result)
	for i in result.keys():
		for j in result[i]:
			if j['Type'] == 'paragraph':
				ret = ret + [extract(act) for act in j['Action List']]
			if j['Type'] == 'list':
				for key in j['Action List'].keys():
					for list_ in j['Action List'][key]:
						ret = ret + [extract(act) for act in list_]
	with open(name_file, 'wb') as f:
		pickle.dump(ret, f)
		f.close()
