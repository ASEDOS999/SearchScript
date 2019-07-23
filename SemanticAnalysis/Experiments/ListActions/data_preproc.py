import pickle
import os

class sample:
	def __init__(self, attr):
		self.samples = {i:list() for i in attr}

	def get_keys(self, act1, act2):
		keys = list()
		for i in act1[0].keys():
			for j in act2[0].keys():
				keys.append((i, j))
		return keys

	def add(self, cur_list):
		l = len(cur_list)
		print((l+1)*l/2)
		for ind, i in enumerate(cur_list):
			if ind % 100 == 0:
				print(float(ind)/l)
			for j in cur_list[ind:]:
				for key in self.get_keys(i, j):
					if self.samples.__contains__(key):
						self.samples[key].append((i, j))
		return self.samples

def create_samples():
	with open('attr.pickle', 'rb') as f:
		attr = pickle.load(f)
		f.close()

	actions_list = list()
	for i in os.listdir():
		if '.pickle' in i and i != 'attr.pickle' and i != 'samples.pickle':
			f = open(i, 'rb')
			actions_list = actions_list + pickle.load(f)
			f.close()
	samples = sample(attr).add(actions_list)
	with open('samples.pickle', 'wb') as f:
		pickle.dump(samples, f)
		f.close

if __name__ == '__main__':
	create_samples()
