import sys
sys.path.append('..')
from action import construct_sentence as cs
def test(root_list):
	list_ = []
	for root in root_list:
		def research(x, depend, parent_postag):
			parent_postag = 'Non' if parent_postag is None else parent_postag
			if x.value.morph.__contains__('VerbForm') and x.value.morph['VerbForm'] == 'Part':
				new_list = x.kids.copy()
				list_.append((cs(root.sentence),
					x.value.lemma,
					root.sentence[x.value.index],
					new_list,
					parent_postag))
			for i in x.kids:
				research(i[0], i[1], x.value.postag)
		research(root, None, None)
	return list_
