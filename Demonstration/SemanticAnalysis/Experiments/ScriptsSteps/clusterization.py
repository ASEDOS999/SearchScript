import numpy as np
def get_nearest(clusters, vector):
	return np.array([np.linalg.norm(i[0] - vector) for i in clusters]).argmin()

def update_centers(clusters):
	for ind, i in enumerate(clusters):
		_ = [j[0] for j in i]
		new_center = sum(_)/len(_)
		clusters[ind] = (new_center, i[1])
	return clusters

def clusterization(text_vectors, eps = 0.12, clusters = None):
	if clusters is None:
		cur_list = text_vectors[0]
		clusters = [(i,list()) for i in cur_list]
	for ind_text, cur_list in enumerate(text_vectors):
		for ind_vector, vector in enumerate(cur_list):
			new_item = (vector, (ind_text, ind_vector))
			ind, rho = get_nearest(clusters, vector)
			if rho < eps:
				clusters[ind][1].append(new_item)
			else:
				clusters.append((vector, list()))
				clusters[-1][1].append(new_item)
		clusters = update_centers(clusters)
	return clusters
