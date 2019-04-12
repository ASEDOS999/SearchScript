import sys
sys.path.append(',,')
from action import action_verb

def get_objects(root_list):
	list_ = []
	parent_verb = []
	def research(parent, mytype = None):
		ret = False
		for i in parent.kids:
			if action_verb(parent):
				list_.append(i)
				ret = True
			if research(i[0], i[1]):
				parent_verb.append((parent, mytype))
		return ret
	for root in root_list:
		research(root, None)
	return list_, parent_verb

def get_feat(i):
	feat = []
	feat.append(i[1])
	x = i[0]
	if x.value.morph.__contains__('Case'):
		feat.append(x.value.morph['Case']+'_'+x.value.postag)
	else:
		feat.append(x.value.postag)
	return feat

import pandas as pd
def extract(root_list):
	list_, parent_verb = get_objects(root_list)
	list_feat_ = []
	for i in list_:
		list_feat_.append(get_feat(i))
	list_feat_ = [i for i in list_feat_ if i[1] != 'PUNCT']
	df = pd.DataFrame(data = 
			{'c%d'%(i): [list_feat_[j][i] for j in range(len(list_feat_))] 
				for i in range(len(list_feat_[0]))})
	df.to_csv('features.csv', sep='\t', encoding='utf-8')
	return df

