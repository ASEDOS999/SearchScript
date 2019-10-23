from . import action
from string import punctuation as punct
from .action import construct_sentence as CS
import time
import sys
from ..SemanticAnalysis import sem_analysis as sa
import time

class text_separation():
	def __init__(self, text, base_preproc = True):
		self.text = text
		if base_preproc:
			self.text, sites = self.find_site(text)

	def find_site(self, text):
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

	def PartOfList(self, cur_text, all = False):
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
			while i > -1 and cur_text[i] in ' \n':
				i -= 1
			if i == -1:
				return False
			return  not cur_text[i] in '.?!'
		def one_sent():
			list_end = ['!', '.', '?']
			indexes = [0] + [ind for ind, i in enumerate(cur_text) if i in list_end]
			if len(indexes) == 1:
				return True
			if indexes[-1] != len(cur_text)-1:
				indexes += [len(cur_text)]
			sentences = [cur_text[i:indexes[ind+1]] for ind,i in enumerate(indexes[:-1])]
			sentences = [i for i in sentences if not i.isnumeric()]
			k = 0
			for i in sentences:
				mark = False
				for j in i:
					mark = mark or j.isalpha()
				if mark:
					k += 1
			return not k > 1
		return (end_analyse() and start_analyse()) and (all or one_sent())

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
		i = cur_text[-1]
		ind = len(cur_text)-1
		while not (i.isnumeric() or i.isalpha() or i in punct):
			ind -= 1
			i = cur_text[ind]
		cur_text = cur_text[:ind+1]
		for i in range(len(cur_text)):
			if cur_text[i] in ['.', '!', '?']:
				last = i
				if i + 2 < len(cur_text) and cur_text[i:i+2] == '...':
					last = i + 2
					i += 2
				list_.append(last+1)
				num_sent += 1
		list_.append(len(cur_text))
		if len(list_) > 1 and list_[-1] == list_[-2]:
			list_ = list_[:-1]
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
					while self.PartOfList(cur_text) and j + 2 < len(list_n):
						res.append(cur_text)
						j += 1
						cur_text = text[list_n[j] : list_n[j+1]]
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
						'Sentences' : self.separate_to_sentence(cur_text)
					}
					results.append(item)
					j += 1
		return results

	def remove_markers(self, text):
		i = 0
		# Trash spaces
		while i < len(text) and text[i] == ' ':
			i+= 1
		if i == len(text):
			return False
		# Bulleted List
		if text[i] in ['*']:
			return text[i+1:]
		# Numbered list
		while i < len(text) and text[i].isnumeric():
			i += 1
		return text[i+1:]
				
	def get_advanced_structure(self):
		structure = self.get_structure()
		list_indexes = list()
		for ind, i in enumerate(structure[:-1]):
			if structure[ind+1]['Type'] == 'list':
				text = structure[ind+1]['Elements']
				res = list()
				for i in text:
					res.append(self.remove_markers(i))
				add = ' '.join(res)
				structure[ind]['Text'] += add
				structure[ind]['Sentences'][-1] += len(add)
				list_indexes.append(ind+1)
		for i in structure:
			i['Text'] = ''.join([j for j in i['Text'] if j!='\n'])
		structure = [i for ind,i in enumerate(structure) if not ind in list_indexes]
		return structure

	def get_list_of_tree(self):
		self.structure = self.get_advanced_structure()
		for i in self.structure:
			root_list = action.construct_tree(i['Text'])
			i['Synt tree'] = root_list
		# Transform syntactic tree to action tree
		for i in self.structure:
			i['Action tree'] = []
			for root in i['Synt tree']:
				i['Action tree'].append(action.get_actions_tree(root))
		return self.structure


class table:
	def get_table(self, list_files):
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

		for key in keys:
			print(key)
			table[key], t = self.extract_one(texts[key])
			print('Time',t/60, 'min')
			print('Processed: %d/%d'%(len(table.keys()), l))
			with open('table.pickle', 'wb') as f:
				pickle.dump(res, f)
				f.close()
		return table
		
	def extract_one(self, text):
		RAT = research_action_tree
		s = time.time()
		res = list()
		new_text = []
		list_ = text_separation(text).get_list_of_tree()
		for i in list_:
			end = [0] + i['Sentences']
			new_text += [{'Sent':i['Text'][j:end[ind+1]], 'Action tree' : i['Action tree'][ind]} 
					for ind,j in enumerate(end[:-1])]
		for sent in new_text:
			new_list = list()
			_ = list()
			for j in i['Action tree']:
				_ = _ + RAT(j)
			# ONE NEEDS MODIFICATION THERE
			instr_sentence = [act.sentence for act in _]
			is_instr = 0
			if len(instr_sentence) > 0 and sent[-1]!= '?':
				is_instr = 1
			try:
				sent_tag_ud = sa.tag_ud(sent['Sent'])
			except Exception:
				sent_tag_ud = list()
			elem = {
				"Sentence" : sent['Sent'],
				"TagUd" : sent_tag_ud,
				"IsInstr" : is_instr
			}
			res.append(elem)
		return res, time.time()-s 

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
