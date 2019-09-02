import pickle
import clusterization
import gensim

if __name__=='__main__':
	with open('data_dict.pickle', 'rb') as f:
		d = pickle.load(f)
		f.close()
	list_files = list(d.keys())
	model = gensim.models.KeyedVectors.load_word2vec_format('../../model.bin', binary=True) 
	model.init_sims(replace=True)
	for i in list_files:
		print(i)
		list_texts, TT, TagUd = clusterization.trivial_segmentation(i, model, d)
		list_texts, texts_vectors = clusterization.union(list_texts, TT)
		with open('SegmentTexts/'+i.split('/')[-1].split('.')[0]+'.md','w') as f:
			for j in list_texts:
				f.write('**NEW SEGMENT**\n\n'+j+'\n\n')
			f.close()
