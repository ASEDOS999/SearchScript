import pandas as pd
def test(root_list):
	import sys
	sys.path.append('..')
	from action import construct_sentence as cs
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

class participle_process:
	def __init__(self, x, depend, postag):
		self.x, self.depend, self.postag = x, depend, postag
	
	def participle_list_feat(self):
		x, depend, postag = self.x, self.depend, self.postag
		parent_postag = 'Non' if parent_postag is None else parent_postag
		if x.value.morph.__contains__('VerbForm') and x.value.morph['VerbForm'] == 'Part':
			new_list = x.kids.copy()
			return (cs(root.sentence),
				x.value.lemma,
				root.sentence[x.value.index],
				new_list,
				parent_postag)

	def get_participle_data(self):
		x, depend, postag = self.x, self.depend, self.postag
		tuple_ = self.participle_list_feat()
		def sub(name, list_):
			if name in list_:
				return 1
			return 0

		dict_ = dict()
		keys_1 = ['case', 'punct', 'nmod', 'advmod', 'parataxis', 'obl', 'nsubj', 'obj', 'ccomp', 'nsubj:pass', 'cc', 'det', 'iobj', 'advcl', 'aux:pass', 'mark', 'conj', 'discourse', 'acl:relcl']
		keys_2 = ['ADJ', 'SCONJ', 'AUX', 'ADP', 'DET', 'PUNCT', 'NOUN', 'CCONJ', 'ADV', 'PROPN', 'VERB', 'PRON', 'PART', 'NUM']
		keys_3 = ['ParentPROPN', 'ParentNUM', 'ParentNOUN', 'ParentVERB', 'ParentNon', 'ParentAUX', 'ParentPUNCT', 'ParentPRON']

		dict_['Sentence'], dict_['Lemma'], dict_['Token'] = [], [], []
		for i in (keys_1 + keys_2 + keys_3):
			dict_[i] = []
		i = tuple_
		dict_['Sentence'].append(i[0])
		dict_['Lemma'].append(i[1])
		dict_['Token'].append(i[2])
		for j in keys_1:
			dict_[j].append(sub(j, [k[1] for k in i[3]]))
		for j in keys_2:
			dict_[j].append(sub(j, [k[0].value.postag for k in i[3]]))
		for j in keys_3:
			dict_[j].append(sub('Parent' + i[4], [j]))
		return pd.DataFrame(dict_)

	def classificate(self):
		with open('../participle_classifier.pkl', 'rb') as fid:
			clf = cPickle.load(fid)
		return 1 == clf.predict(self.get_participle_data())[0]
