class tree:
	def __init__(self, value):
		self.value = value
		self.kids = []

	# The arguments of this function is a value of new vertices
	# and type of relationship between parent and kid
	def add_child(self, value, type = None):
		self.kids.append((tree(value), type))

def construct_tree(tree, sentence):
	root = tree(tree[0], sentence[0])
	return root

class action:
	name_action = 'Action'
	
	def __init__(self, verb, subject = [], object = [], time = [], place = [], purpose = [], way = []):
		self.verb = verb
		self.object = object
		self.subject = subject
		self.time = time
		self.place = place
		self.purpose = purpose
		self.way = way
	
	def get_verb(self):
		return self.verb
	
	def get_object(self):
		return self.object
	
	def get_subject(self):
		return self.subject
	
	def get_time(self):
		return self.time
	
	def get_place(self):
		return self.place
	
	def get_purpose(self):
		return self.purpose
	
	def get_way(self):
		return self.way

def is_verb(x):
	return True

def action_verb(x):
	def is_not_modal():
		return True
	
	def is_indicative():
		return True
	
	return is_not_modal() and is_indicative()

def process_type(vert, act):
	object_type = ['dobj', 'iobj', 'xcomp']
	subject_type = ['agent', 'nsubj', 'xsubj']
	time_type = ['tmod']
	place_type = ['advcl']
	purpose_type = ['advcl']
	way_type = ['acomp']
	array = [object_type, 
		subject_type, 
		time_type, 
		place_type, 
		purpose_type,
		way_type]
	answer = [False] * len(array)
	for i in range(len(array)):
		answer[i] = True if vert[1] in array[i] else False
	def _(i):
		ret = False
		for j in range(len(answer)):
			ret = ret or answer[j] if i != j else ret
		return ret
	act.object.append(vert[0]) if answer[0] and _(0) else None
	act.subject.append(vert[0]) if answer[1] and _(1) else None
	act.time.append(vert[0]) if answer[2] and _(2) else None
	act.place.append(vert[0]) if answer[3] and _(3) else None
	act.purpose.append(vert[0]) if answer[4] and _(4) else None
	act.way.append(vert[0]) if answer[5] and _(5) else None

def get_inform_parent(parent, act):
	return 0


def get_actions(sentence, root):
	all_actions = []
	
	def research(parent):
		list = []
		for i in parent.kids:
			list.append(i)
			if is_verb(i[0]) and action_verb(i[0]):
				act = action(verb = i[0].value)
				get_inform_parent(parent, act)
				information = research(i[0])
				for j in information:
					process_type(j, act)
				all_actions.append(act)
			else:
				research(i[0])
		return list
	
	research(root)
	return all_actions

act = action("verb")
process_type([0, "s"], act)
