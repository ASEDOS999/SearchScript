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
		self.result = []
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


from action import construct_sentence as CS

def start_proc(vertice):
	act = vertice[0].value
	if act.name_action == 'ROOT':
		return True
	if CS(act.sentence)[-2] != '.':
		return True

def there_is_inf(act):
	for i in act.keys:
		if i != 'VERB':
			for j in act.inform[i]:
				morph = j[0].morph
				if morph.__contains__('VerbForm') and morph['VerbForm'] == 'Inf':
					return True
	return False

def instructions(vertice):
	act = vertice[0].value
	if start_proc(vertice):
		return False
	if act.type_action in ['Imperative', 'Modal']:
		return True
	if len(act.inform['SUBJECT']) == 0:
		morph = act.inform['VERB'][0].morph
		if ((morph.__contains__('Person') and morph['Person'] == '3' and 
			morph.__contains__('Number') and morph['Number'] == 'Sing')):
				return lemma != 'быть' and there_is_inf(act)
	if len(act.inform['SUBJECT']) == 1:
		morph = act.inform['VERB'][0].morph
		if morph.__contains__('Person') and morph['Person'] == '2':
			lemma = act.inform['VERB'][0].lemma
			if morph.__contains__('Aspect') and morph['Aspect'] == 'Imp':
				return lemma != 'быть' and there_is_inf(act)
			if morph.__contains__('Aspect') and morph['Aspect'] == 'Perf':
				return True
	return False

def DFS(graph, test = instructions, print_name = False):
	list_ = []
	for i in graph.kids:
		if test(i):
			list_.append(i[0].value)
			if print_name:
				print(i[0].value.name_action)
		list_ += DFS(i[0])
	if type(graph) == FAT:
		for i in graph.in_kids:
			if test(i):
				list_.append(i[0].value)
			if print_name:
				print(i[0].value.name_action)
			list_ += DFS(i[0])
		for i in graph.out_kids:
			if test(i):
				list_.append(i[0].value)
				if print_name:
					print(i[0].value.name_action)
			list_ += DFS(i[0])
	return list_
