class action:
	name_action = 'Action'
	
	def __init__(self, verb, object = [], subject = [], time = [], place = [], way = []):
		self.verb = verb
		self.object = object
		self.subject = subject
		self.time = time
		self.place = place
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
	
	def get_way(self):
		return self.way

def is_verb(x):
	return True

def action_verb(x)
	def is_not_modal():
		return True
	
	def is_indicative():
		return True
	
	return is_not_modal() and is_indicative()

class tree:
	def __init__(self, value):
		self.value = value
		self.kids = []

	# The arguments of this function is a value of new vertices
	# and type of relationship between parent and kid
	def add_child(self, value, type is None):
		self.kids.append((value, type))

def process_type(vert, act):
	object_type = []
	subject_type = []
	time_type = []
	place_type = []
	way_type = []
	array = [object_type, subject_type, time_type, place_type, way_type]
	answer = [False, False, False, False, False]
	for i in range(len(array)):
		answer[i] = True if vert[1] in array[i]:
	def _(i):
		ret = False
		for j in range(len(answer)):
			ret = ret or answer[j] if i != j
		return ret
	act.object.append(vert[0]) if answer[0] and _(0)
	act.subject.append(vert[0]) if answer[1] and _(1)
	act.time.append(vert[0]) if answer[2] and _(2)
	act.place.append(vert[0]) if answer[3] and _(3)
	act.way.append(vert[0]) if answer[4] and _(4)

def get_actions(sentence, root):
	all_actions = []
	
	def research(parent):
		list = []
		for i in parent.children:
			list.append(i)
			if is_verb(i[0]) and action_verb(i[0]):
				obj = parent[0]
				information = research(i)
				act = action(verb = i[0], object = obj)
				for j in information:
					process_type(j, act)
				all_actions.append(act)
			else:
				research(i)
		return list
	
	research(root)
	return all_actions
