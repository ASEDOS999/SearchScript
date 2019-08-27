# Clusterization

import sys
sys.path.append('../../../ScriptExtract')
from TextProcessing import graph_construct as GC
from TextProcessing import research_list, show
from TextProcessing import research_action_tree as RAT
import action

# The following two functions are for to transform
# a list from GC.get_list to a list of  sentences with marks of instructions
def transform(sentences, instr_sentence):
    cur_list = list()
    for sentence in sentences:
        if sentence in instr_sentence:
            cur_list.append((1, sentence))
        else:
            cur_list.append((0, sentence))
    return cur_list

def cur_transform(list_):
    new_list = list()
    for i in list_:
        if not i.__contains__('Type') or i['Type'] == 'paragraph':
            _ = list()
            for j in i['Action tree']:
                _ = _ + RAT(j)
            instr_sentence = [act.sentence for act in _]
            _ = transform([_.sentence for _ in action.construct_tree(i['Text'])], instr_sentence)
            item = list()
            S = [-1] + i['Sentences']
            for ind, j in enumerate(_):
                cur = (j[0], i['Text'][(S[ind]):(S[ind+1])])
                item.append(cur)
        else:
            item = cur_transform(i['List'])
        new_list.append(item)
    return new_list

# Segmentation of text to lists, paragraphes and sentences with marking
def text_segmentation(path_file):
	handle = open(path_file, "r")
	text = handle.read()
	handle.close()
	
	list_ = GC(text).get_list()
	    
	segments = cur_transform(list_)
	
	for i in segments:
		for j in i:
			if type(j)==type('tuple'):
				for k in j:
					if k[1] == '':
						j.remove(k)
			else:
				if j[1] == '':
					i.remove(j)
	for i in segments:
		if len(i) == 0:
			segments.remove(i)
	return segments
