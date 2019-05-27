import action
# Full Action Tree
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

	def add_out_child(self, value, mytype = 'OUT'):
		self.out_kids.append((value, mytype))

	def add_in_child(self, value, mytype = 'IN'):
		self.in_kids.append((value, mytype))

class graph_construct:
	def __init__(self, text):
		self.text = text
		self.results = []
		self.main_tree = None

	def get_list_of_tree(self):
		text = self.text
		list_n = [0]
		text = text
		for i in range(len(text)):
			if text[i] == '\n':
				list_n.append(i)
		list_n.append(len(text) + 1)
		root_list = []
		results = []
		for i in range(len(list_n) - 1):
			root_list = []
			if list_n[i+1] - list_n[i] > 1000:
				cur_text = text[list_n[i] : list_n[i + 1]]
				list_ = []
				N = 0
				for i in range(len(cur_text)):
					if cur_text[i] == '.':
						last = i
					N += 1
					if N > 1000:
						list_.append(last)
						N = 0
				list_.append(len(text) + 1)
				for j in range(len(list_) - 1):
					root_list = root_list + action.construct_tree(text[list_[j] : list_[j + 1]])
			else:
				if list_n[i] != list_n[i + 1]:
					root_list = action.construct_tree(text[list_n[i] : list_n[i + 1]])
			list_act = []
			for root in root_list:
				list_act.append(action.get_actions_tree(root))
			results.append(list_act)
		self.results = results
		return results

	def process_paragraph(self, list_tree):
		cur_vert = None
		ret = None
		for i in list_tree:
			new_vert = FAT(old_vert = i)
			if not cur_vert is None:
				cur_vert.add_in_child(new_vert)
			else:
				ret = new_vert
			cur_vert = new_vert
		return ret

	def transform_treelist_to_tree(self):
		cur_vert = None
		ret = None
		for i in self.results:
			j = self.process_paragraph(i)
			if not j is None:
				if not cur_vert is None:
					cur_vert.add_out_child(j)
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


class graph_construct_title(graph_construct):
	def __init__(self, text):
		graph_construct.__init__(self, text)

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
			if cur_text[i] == ';':
				return True
			return False
		return end_analyse() or start_analyse()

	def title_processing(self, cur, cur_text, sections, num_sent):
		from isanlp.processor_remote import ProcessorRemote
		proc_syntax = ProcessorRemote('localhost', 3334, 'default')
		tokens_limit = 10
		if num_sent <= 1:
			if cur_text[0] == '\n':
				cur_text = cur_text[1:]
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

	def get_list_of_tree(self):
		text = self.text
		list_n = [0]
		text = text
		# Separate to paragraphes
		for i in range(len(text)):
			if text[i] == '\n':
				list_n.append(i)
		list_n.append(len(text) + 1)
		root_list = []
		results = []
		sections = []
		cur = None
		# Separate to sentence
		for j in range(len(list_n) - 1):
			root_list = []
			cur_text = text[list_n[j] : list_n[j + 1]]
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
				list_.append(len(text) + 1)
			if list_n[j] != list_n[j + 1]:
				cur = self.title_processing(cur, cur_text, sections, num_sent)
				root_list = []
				# Constructing syntactic tree
				if len(cur_text[list_n[j]:list_n[j+1]]) > 1000:
					for i in range(len(list_) - 1):
						root_list = root_list + action.construct_tree(text[list_[i] : list_[i + 1]])
				else:
					root_list = action.construct_tree(text[list_n[j] : list_n[j + 1]])
				cur['tree'].append(root_list)
		# Transform syntactic tree to action tree
		for cur in sections:
			cur['action_tree'] = []
			for i in cur['tree']:
				list_act = []
				for root in i:
					list_act.append(action.get_actions_tree(root))
				cur['action_tree'].append(list_act)
				self.results.append(list_act)
				for root in list_act:
					root = self.add_section(root, cur['title'])
		return results

	def add_section(self, root, name):
		root.value.section = name
		for i in root.kids:
			self.add_section(i[0], name)
		return root

from action import construct_sentence as CS
def start_proc(vertice):
	act = vertice[0].value
	if act.name_action == 'ROOT':
		return True

def there_is_inf(act):
	for i in act.keys:
		if i != 'VERB':
			for j in act.inform[i]:
				morph = j[0].morph
				if morph.__contains__('VerbForm') and morph['VerbForm'] == 'Inf':
					return True
	return False

def instructions(vertice, current_list):
	act = vertice[0].value
	def condition():
		if start_proc(vertice):
			return False
		if act.type_action in ['Imperative', 'Modal']:
			return True
		lemma = act.inform['VERB'][0].lemma
		morph = act.inform['VERB'][0].morph
		if (len(act.inform['SUBJECT']) == 0 and
			morph.__contains__('Person') and morph['Person'] == '3' and 
			morph.__contains__('Number') and morph['Number'] == 'Sing'):
				return lemma != 'быть' and there_is_inf(act)
		if (len(act.inform['SUBJECT']) == 1 and 
			morph.__contains__('Person') and morph['Person'] == '2'):
			if morph.__contains__('Aspect') and morph['Aspect'] == 'Imp':
				return lemma != 'быть' and there_is_inf(act)
			if morph.__contains__('Aspect') and morph['Aspect'] == 'Perf':
				return True
		return False
	if condition():
		if current_list is None:
			current_list = []
		current_list.append(vertice[0].value)
	return current_list

def DFS(graph, test = instructions, list_ = None):
	for i in graph.kids:
		list_ = test(i, list_)
		list_ = DFS(i[0], test, list_)
	if type(graph) == FAT:
		for i in graph.in_kids:
			list_ = test(i, list_)
			list_ = DFS(i[0], test, list_)
		for i in graph.out_kids:
			list_ = test(i, list_)
			list_ = DFS(i[0], test, list_)
	return list_
