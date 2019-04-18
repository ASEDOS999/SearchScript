import sys
sys.path.append('..')
from action import construct_sentence as cs
def test(root_list):
	list_ = []
	for root in root_list:
		def research(x, depend):
			if x.value.morph.__contains__('VerbForm') and x.value.morph['VerbForm'] == 'Part':
				new_list = x.kids.copy()
				list_.append((cs(root.sentence),
					x.value.lemma,
					root.sentence[x.value.index],
					new_list))
			for i in x.kids:
				research(i[0], i[1])
		research(root, None)
	return list_
