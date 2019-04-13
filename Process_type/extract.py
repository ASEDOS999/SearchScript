import sys
sys.path.append(',,')
from action import action_verb
import numpy as np
import pandas as pd

def get_objects(root_list):
	# Function for to extract list of kids and parent of verb from syntactic tree
	# Input is a list of tree roots
	# Output is a lists of kids and parents
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
	# Extract required information from all information about one word
	feat = []
	feat.append(i[1])
	x = i[0]
	if x.value.morph.__contains__('Case'):
		feat.append(x.value.morph['Case']+'_'+x.value.postag)
	else:
		feat.append(x.value.postag)
	return feat

def extract_data(root_list):
	# Extract data from list of tree for each tree each tree, return dataframe
	list_, parent_verb = get_objects(root_list)
	list_feat_ = []
	for i in list_:
		list_feat_.append(get_feat(i))
	list_feat_ = [i for i in list_feat_ if i[1] != 'PUNCT']
	df = pd.DataFrame(data = 
			{'c%d'%(i): [list_feat_[j][i] for j in range(len(list_feat_))] 
				for i in range(len(list_feat_[0]))})
	return df

def extract_feat_from_dataframe(df):
	list_ = [[] for i in range(len(df.columns.values.tolist()))]
	for j in range(len(df.columns.values.tolist())):
		for i in df[df.columns.values[j]]:
			if not i in list_[j]:
				list_[j].append(i)

	N = len(list_[0]) + len(list_[1])

	array = None
	for i in range(len(df)):
		x = [0] * N
		sum_ = 0
		for j in range(len(df.columns.values.tolist())):
			x[list_[j].index(df[df.columns.values[j]][i]) + sum_] = 1
			sum_ += len(list_[j])
		if array is None:
			array = np.array(x)
		else:
			array = np.vstack((array, x))
	return array

def create_dataframe(root_list, name = 'features.csv'):
	# Create and save dataframe as *.csv
	df = extract_data(root_list)
	df.to_csv(name, sep = '\t', encoding = 'utf')
	return df
