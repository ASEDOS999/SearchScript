import action
# Full Action Tree
# It is syntactic tree for all text
# It is constucted through a list of old action trees
class FAT:
	def __init__(self, value = None, old_vert = None, sentence = None):
		self.value = value
		self.sentence = sentence
		self.kids = []
		if not old_vert is None:
			self.value = old_vert.value
			self.kids = old_vert.kids
			self.sentence = old_vert.sentence
		self.out_kids = []
		self.in_kids = []

	# Children from the next paragraph
	def add_out_child(self, value, mytype = 'OUT'):
		self.out_kids.append((value, mytype))

	# Children from the current paragraph
	def add_in_child(self, value, mytype = 'IN'):
		self.in_kids.append((value, mytype))

class text_structure:
	def PartOfList(self, cur_text):
		def start_analyse():
			i = 0
			while i < len(cur_text) and cur_text[i] == ' ':
				i+= 1
			if i == len(cur_text):
				return False
			# Bulleted List
			if cur_text[i] == '*':
				return True
			# Numbered list
			while i < len(cur_text) and cur_text[i].isnumeric():
				i += 1
			if i == len(cur_text):
				return False
			if cur_text[i] == '.':
				return True
			return False
		def end_analyse():
			i = len(cur_text) - 1
			while i > -1 and cur_text[i] == ' ':
				i -= 1
			if i == -1:
				return False
			if not cur_text[i] in ['.', '!', '?']:
				return True
			return False
		return end_analyse() or start_analyse()

	def extract_name_of_POL(self, cur_text):
		name = cur_text
		i = 0
		while i < len(cur_text) and cur_text[i] == ' ':
			i+= 1
		if name[i] == '*':
			i+=1
			start = i
			while i < len(name) and not name[i] in ['.', '!', '?']:
				i += 1
			return name[start : i + 1]
		prev = i
		while i < len(cur_text) and cur_text[i].isnumeric():
			i += 1
		if cur_text[i] == '.':
			i+= 1
			start = i
			while i < len(name) and not name[i] in ['.', '!', '?']:
				i += 1
			return name[start : i + 1]
		else:
			start = prev
			while i < len(name) and not name[i] in ['.', '!', '?']:
				i += 1
			return name[start : i + 1]

	def title_processing(self, cur, cur_text, sections, num_sent):
		# It has to be rewritten
		from isanlp.processor_remote import ProcessorRemote
		proc_syntax = ProcessorRemote('localhost', 3334, 'default')
		tokens_limit = 10
		if num_sent <= 1:
			i = 0
			while i < len(cur_text) and cur_text[i] in ['\n', ' ', '\t']:
				i+= 1
			cur_text = cur_text[i:]
			if len(cur_text) > 0 and cur_text[-1] == '\n':
				cur_text = cur_text[:-1]
			if len(cur_text) > 0 and not self.PartOfList(cur_text):
				analysis_res = proc_syntax(cur_text)
				if len(analysis_res['tokens']) <= tokens_limit:
					cur = dict()
					cur['title'] = cur_text
					sections.append(cur)
					cur['tree'] = []
		if cur is None:
			cur = dict()
			cur['title'] = ''
			sections.append(cur)
			cur['tree'] = []
		return cur


class text_separation(text_structure):
	def __init__(self, text):
		self.text = text

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
			if cur_text[i] in ['.', '!', '?']:
				last = i
				num_sent += 1
			N += 1
			if i + 2 < len(cur_text) and cur_text[i:i+2] == '...':
				last = i + 2
				i += 2
				N += 2
				num_sent += 1
			if N > 1000:
				list_.append(last)
				N = 0
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
					item = {
						'Type' : 'list',
						'MainWord' : None,
						'Section' : section_name,
						'List': []
					}
					mark = self.PartOfList(text[list_n[j+1]: list_n[j+2]])
					local_section_name = None
					while self.PartOfList(cur_text) or (mark and prev):
						prev = self.PartOfList(cur_text)
						list_sentence = self.separate_to_sentence(cur_text)
						if prev == True:
							local_section_name = self.extract_name_of_POL(cur_text)
						cur = {
							'Section' : local_section_name,
							'Text' : cur_text,
							'Sentences' : list_sentence
						}
						item['List'].append(cur)
						j += 1
						if j < len(list_n) - 1:
							cur_text = text[list_n[j]:list_n[j+1]]
						else:
							break
					results.append(item)
				else:
					list_sentence = self.separate_to_sentence(cur_text)
					if self.title_processing(cur, cur_text, sections, num_sent):
						section_name = cur_text
						item = {
							'Type' : 'paragraph',
							'Section' : section_name,
							'Text' : cur_text,
							'Sentences' : list_sentence
						}
						results.append(item)
						j += 1
					else:
						item = {
							'Type' : 'paragraph',
							'Section' : section_name,
							'Text' : cur_text,
							'Sentences' : list_sentence
						}
						results.append(item)
						j += 1
		return results

# CLass for constructing FAT
class graph_construct(text_structure):
	def __init__(self, text):
		self.structure = text_separation(text).get_structure()
		self.results = []
		self.main_tree = None

	def get_list_of_tree(self):
		for i in self.structure:
			if i['Type'] == 'paragraph':
				root_list = action.construct_tree(i['Text'])
				i['Synt tree'] = root_list
			if i['Type'] == 'list':
				for j in i['List']:
					root_list = action.construct_tree(j['Text'])
					j['Synt tree'] = root_list
		# Transform syntactic tree to action tree
		for i in self.structure:
			if i['Type'] == 'paragraph':
				i['Action tree'] = []
				for root in i['Synt tree']:
					i['Action tree'].append(action.get_actions_tree(root))
			if i['Type'] == 'list':
				for j in i['List']:
					j['Action tree'] = []
					for root in j['Synt tree']:
						j['Action tree'].append(action.get_actions_tree(root))

	def process_paragraph(self, item_paragraph):
		cur_vert = None
		ret = None
		list_tree = item_paragraph['Action tree']
		for i in list_tree:
			new_vert = FAT(old_vert = i)
			if not cur_vert is None:
				cur_vert.add_in_child(new_vert)
			else:
				ret = new_vert
			cur_vert = new_vert
		return ret

	def process_list(self, item_list):
		cur_vert = None
		ret = None
		list_paragraph = item_list['List']
		for i in list_paragraph:
			j = self.process_paragraph(i)
			if not j is None:
				if not cur_vert is None:
					cur_vert.add_out_child(j, mytype = 'next')
				else:
					ret = j
				cur_vert = j
		return ret

	def transform_treelist_to_tree(self):
		cur_vert = None
		ret = None
		for i in self.structure:
			if i['Type'] == 'paragraph':
				j = self.process_paragraph(i)
				if not j is None:
					if not cur_vert is None:
						cur_vert.add_out_child(j)
					else:
						ret = j
					cur_vert = j
			if i['Type'] == 'list':
				j = self.process_list(i)
				if not j is None:
					if not cur_vert is None:
						cur_vert.add_out_child(j, mytype = 'list')
					else:
						ret = j
					cur_vert = j
		self.main_tree = ret

	def construct(self):
		self.get_list_of_tree()
		self.transform_treelist_to_tree()

	def get_graph(self):
		if self.main_tree is None:
			self.construct()
		return self.main_tree
# Different conditions for FAT's DFS
from action import construct_sentence as CS

# Test for roots
def start_proc(vertice):
	act = vertice[0].value
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
def cond_instr(vertice):
	if start_proc(vertice):
		return False
	act = vertice[0].value
	if act.type_action in ['Imperative', 'Modal']:
		return True
	lemma = act.inform['VERB'][0].lemma
	morph = act.inform['VERB'][0].morph
	subj = [i for k in act.inform.keys() for i in act.inform[k] if k in ['agent', 'xsubj', 'nsubj', 'subj'] ]
	if (len(subj) == 0 and
		morph.__contains__('Person') and morph['Person'] == '3' and 
		morph.__contains__('Number') and morph['Number'] == 'Sing'):
			return lemma != 'быть' and there_is_inf(act)
	if (len(subj) == 1 and 
		morph.__contains__('Person') and morph['Person'] == '2'):
		if morph.__contains__('Aspect') and morph['Aspect'] == 'Imp':
			return lemma != 'быть' and there_is_inf(act)
		if morph.__contains__('Aspect') and morph['Aspect'] == 'Perf':
			return True
	return False

def instructions(vertice, current_result):
	if cond_instr(vertice):
		if current_result is None:
			current_result = []
		current_result.append(vertice[0].value)
	return current_result

# Deep-First Search specially for FAT
def DFS(graph, test = instructions, result = None):
	for i in graph.kids:
		result = test(i, result)
		result = DFS(i[0], test, result)
	if type(graph) == FAT:
		for i in graph.in_kids:
			result = test(i, result)
			result = DFS(i[0], test, result)
		for i in graph.out_kids:
			result = test(i, result)
			result = DFS(i[0], test, result)
	return result
