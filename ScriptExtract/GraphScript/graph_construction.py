#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 06:06:57 2020

@author: elias
"""

import numpy as np
import copy
from ScriptExtract.Preprocessing.TextProcessing import table
from ScriptExtract.GraphScript import graph_construction

def get_feature_dict(table, key_word = "depend_lemma"):
    full_list_actions = []
    sentences = []
    relations = []
    for key in table:
        table_text = table[key]
        help_list = []
        help_sentences = []
        help_relations = []
        for item in table_text:
            for act in item['Actions']:
                help_sentences.append(item["Sentence"])
                help_relations.append(item['Relations'])
                help_list.append(act)
        sentences.append(help_sentences)
        relations.append(help_relations)
        full_list_actions.append(help_list)
    verb_dict = dict()
    feature_dict = dict()
    N = 0
    N_verb = 0
    for ind, l in enumerate(full_list_actions):
        for ind1, act in enumerate(l):
            sentence = sentences[ind][ind1]
            if act.inform['VERB'] is not None:
                act.inform['SEM_REL'] = relations[ind][ind1]
                b, e = act.inform['VERB'][0].begin, act.inform['VERB'][0].end
                N_verb += 1
                verb = sentence[b:e]
                if verb in verb_dict:
                    verb_dict[verb][(ind,ind1)] = 0
                else:
                    verb_dict[verb] = {(ind,ind1):0}
                for depend in act.inform:
                    if not depend in ['punct', 'VERB', 'SEM_REL']:
                        for w in act.inform[depend]:
                            N += 1
                            lemma = w[0].lemma
                            if not w[0].postag in ['CONJ', 'PRON', 'VERB']:
                                if key_word == "lemma":
                                    if lemma in feature_dict:
                                        feature_dict[lemma][(ind,ind1)] = 0
                                    else:
                                        feature_dict[lemma] = {(ind,ind1):0}
                                if key_word == "depend_lemma":
                                    if (depend, lemma) in feature_dict:
                                        feature_dict[(depend, lemma)][(ind,ind1)] = 0
                                    else:
                                        feature_dict[(depend, lemma)] = {(ind,ind1):0}     
                if key_word == 'sem_rel':
                    rel = relations[ind][ind1]
                    for r in rel:
                        parent, child = r['parent'], r['child']
                        if (act.inform['VERB'][0].begin == parent['start'] and
                            act.inform['VERB'][0].end == parent['end']):
                            for j in act.inform:
                                if j != 'VERB' and j != 'SEM_REL':
                                    for word in act.inform[j]:
                                        if (word[0].begin == child['start'] and
                                            word[0].end == child['end']):
                                            lemma = word[0].lemma
                                            tp = r['tp']
                                            if lemma in feature_dict:
                                                feature_dict[lemma][(ind,ind1)] = tp
                                            else:
                                                feature_dict[lemma] = {(ind,ind1):tp}
    return full_list_actions, verb_dict, feature_dict

def create_table_of_sets(feature_dict, full_list_actions):
    list_of_set = []
    for i in feature_dict:
        ind_actions = feature_dict[i].keys()
        set_cup = []
        for ind in ind_actions:
            for ind_s, s in enumerate(list_of_set):
                if ind in s:
                    set_cup.append(ind_s)
        if len(set_cup) == 0:
            list_of_set.append(set(ind_actions))
        else:
            new_set = set([i for j in set_cup for i in list_of_set[j]])
            list_of_set = [i for ind, i in enumerate(list_of_set) if not ind in set_cup]
            list_of_set.append(new_set)
    return [[(ind,ind1) for ind,ind1 in j] for j in list_of_set]

def _add_start(E, V, start, docs):
    V.append(start)
    E[start] = []
    start_docs = [min([i[1] for i in V if i[0] == j]) for j in docs]
    for ind, i in enumerate(start_docs):
        v = docs[ind], i
        E[start].append(v)
            
def _add_end(E, V, end, docs):
    V.append(end)
    E[end] = []
    end_docs = [max([i[1] for i in V if i[0] == j]) for j in docs]
    for ind, i in enumerate(end_docs):
        v = docs[ind], i
        E[v].append(end)

def construct_graph(table, # The result of ScriptExtract.Preprocessing.TextProcessing.table().get_table
                    key_word = "depend_lemma", # The type of abalysed verb argument
                    with_next = False, # If True Construct edges between neibourghood in one document
                    start = (-1,-1), end = (-2,-2), # Start and end vertices
                    min_set = 2, max_set = np.infty
                    ):
    
    full_list_actions, verb_dict, feature_dict = get_feature_dict(table, key_word)
    table = create_table_of_sets(feature_dict, full_list_actions)
    table = [i for i in table if max_set>len(i) >= min_set]
    
    # Vertices list
    V = [i for j in table for i in j]
    V.sort(key = lambda x: x[0])
    
    # Dictionary for edges (adjacency list)
    E = {v:[] for v in V}
    
    # Edges between neibourghood in one document
    if with_next:
        for ind, v in enumerate(V):
            if ind+1 < len(V) and V[ind+1][0] > v[0]:
                E[v].append(V[ind+1])
    
    # Edges between action with same arguments
    for i in table:
        for v in i:
            for v_ in i:
                if v_ != v and not v_ in E[v]:
                    E[v].append(v_) 
                    
    # Adding start and end vertices
    docs = np.unique(np.array([i[0] for i in V]))
    if start is None:
        start = (-1, -1)
    if end is None:
        end = (-2, -2)
    _add_start(E, V, start, docs)
    _add_end(E, V, end, docs)
    return (E, V), (start, end), (full_list_actions, verb_dict, feature_dict)

def graph_inform(V, E):
    s = 0
    s1 = 0
    for i in E:
        s+=len(E[i])
        s1 += len([j for j in E[i] if not(j[0] == i[0] and j[1] == i[1]+1)])
    print("The edges number", s)
    print("The out-edges number", s1)
    print("The vertices number", len(V))
    print("The number of document", len(np.unique(np.array([i[0] for i in V]))))
	
	

def equal_word(word, word1):
    return word.begin == word1['start'] and word.end == word1['end']

class script:
    def __init__(self, V, E, full_list_actions, start = (-1,-1), end = (-2,-2)):
        self.V, self.E = V, E
        self.start = start
        self.end = end
        self.V_inform, self.E_inform = self._reconstruct(V, E, full_list_actions)
        self.V_descr = {}
        self.bad_BFS()

    def _reconstruct(self, V, E, full_list_actions):
        E = E
        V = {v: self._get_inform(v, full_list_actions) for v in V}
        return V, E
    
    def bad_BFS(self):
        start, end = self.start, self.end
        self.V.sort(key = lambda x: x[0])
        self.V = [i for i in self.V if i!= start and i!=end]
        self.V = [start] + self.V + [end]
        self.V_descr[start] = {}
        previous = start
        for v in self.V[1:]:
            if v in self.E and len(self.E[v]) >0 or v == end:
                self.V_descr[v] = copy.deepcopy(self.V_descr[previous])
                self.update(v)
                previous = v
        return None
    
    def update(self, v):
        inform = self.V_inform[v]
        if 'Sentence' in inform:
            sentence = inform['Sentence']
            self.V_descr[v]['Sentence'] = sentence
        else:
            self.V_descr[v]['Sentence'] = ''
        if 'локатив' in inform:
            self.V_descr[v]['локатив'] = {'локатив':inform['локатив'],
                                          'Sentence':sentence}
        if 'объект' in inform:
            obj = {'объект':inform['объект'],
                    'verb':inform['VERB'],
                  'Sentence':sentence}
            if 'объект' in self.V_descr[v]:
                self.V_descr[v]['объект'].append(obj)
            else:
                self.V_descr[v]['объект'] = [obj]
        if 'субъект' in inform:
            subj = {'субъект':inform['субъект'],
                    'verb':inform['VERB'],
                   'Sentence':sentence}
            if 'субъект' in self.V_descr[v]:
                self.V_descr[v]['субъект'].append(subj)
            else:
                self.V_descr[v]['субъект'] = [subj]
        if 'темпоратив' in inform:
            self.V_descr[v]['темпоратив'] = {'темпоратив':inform['темпоратив'],
                                          'Sentence':sentence}
        
    def _get_inform(self, v, full_list_actions):
        if v == self.start or v == self.end:
            return {}
        act = full_list_actions[v[0]][v[1]]
        inform = {}
        inform['Sentence'] = act.sentence
        inform['VERB'] = act.inform['VERB']
        for j in act.inform['SEM_REL']:
            type_rel = j['tp']
            parent = j['parent']
            child = j['child']
            if equal_word(act.inform['VERB'][0], parent):
                for key in act.inform:
                    if not key in ['VERB', 'SEM_REL']:
                        for word, list_depend, _ in act.inform[key]:
                            if equal_word(word, child):
                                if type_rel in inform:
                                    inform[type_rel].append((word, list_depend))
                                else:
                                    inform[type_rel] = [(word, list_depend)]
        return inform
    
    def GetNext(self, v):
        return self.E[v]
	
def get_srcipt(list_files, name_table = "1.pickle"):
	table_ = table().get_table(list_files, test = lambda act: True, name_table = name_table)
	(E, V), (start, end), (full_list_actions, verb_dict, feature_dict) = graph_construction.construct_graph(table_, key_word = 'sem_rel')
	script_ = script(V,E, full_list_actions)
	return script_

def union(sentence, list_):
    q = list(np.array(sentence)[list_])
    return ' '.join(q)

def print_dict(v_desr):
    if 'Sentence' in v_desr:
        print(' '.join(v_desr['Sentence']))
    if 'локатив' in v_desr:
        print('\nлокатив:'.upper())
        print("%s (%s)"%(v_desr['локатив']['локатив'][0][0].lemma,
                         union(v_desr['локатив']['Sentence'], v_desr['локатив']['локатив'][0][1])))
    if 'темпоратив' in v_desr:
        print('\nтемпоратив:'.upper())
        print("%s (%s)"%(v_desr['темпоратив'][0].lemma, union(v_desr['Sentence'], v_desr['темпоратив'][1])))
    if 'объект' in v_desr:
        print('\nобъект'.upper())
        obj = v_desr['объект']
        for i in obj:
            for j in i['объект']:
                print("%s (%s) - %s (%s)"%(j[0].lemma, union(i['Sentence'], j[1]),
                                           i['verb'][0].lemma, union(i['Sentence'], i['verb'][1])))
    if 'субъект' in v_desr:
        print('\nсубъект'.upper())
        obj = v_desr['субъект']
        for i in obj:
            for j in i['субъект']:
                print("%s (%s) - %s (%s)"%(j[0].lemma, union(i['Sentence'], j[1]),
                                           i['verb'][0].lemma, union(i['Sentence'], i['verb'][1])))