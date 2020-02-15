import pickle
import os

def get_neighbours(j, table):
	ret = list()
	keys_table, indexes = j[1]
	for ind, key in enumerate(keys_table):
		cur = indexes[ind]
		ret.append(table[key][cur])
	return ret
def get_pairs(table):
	ret = list()
	for i in table:
		for j in table[i]:
			neigh = get_neighbours(j, table)
			for n in neigh:
				ret.append((j, n))
	return ret
import random
def make_marking(name_file):
	with open(name_file, 'rb') as f:
		samples = pickle.load(f)
		f.close()
	new = list()
	for i in samples:
		if len(i) < 3:
			print(i[0][0])
			print(i[1][0])
			k = int(input())
			if k in [0, 1]:
				new.append((i[0], i[1], k))
			elif k == -1:
				n = len(new)
				while k == -1:
					n-=1
					print(new[n][0][0])
					print(new[n][1][0])
					print(new[n][2])
					k = int(input())
				if k in [0, 1]:
					new[n] = ((i[0], i[1], k))
				else:
					break
			else:
				break
		else:
			new.append(i)
	for i in samples[len(new):]:
		new.append(i)
	print(len([i for i in new if len(i) > 2])/len(samples), len([i for i in new if len(i) > 2]))
	print('Positive ', len([i for i in new if len(i) > 2 and i[2] == 1])/len([i for i in new if len(i)>2]))
	with open(name_file, 'wb') as f:
		pickle.dump(new,f)
		f.close()


if __name__ == '__main__':
	if not 'samples.pickle' in os.listdir():
		with open('../table.pickle', 'rb') as f:
			table = pickle.load(f)
			f.close()
		pairs = get_pairs(table)
		print(len(pairs))
		with open('samples.pickle', 'wb') as f:
			pickle.dump(pairs, f)
			f.close()
	make_marking('samples.pickle')
