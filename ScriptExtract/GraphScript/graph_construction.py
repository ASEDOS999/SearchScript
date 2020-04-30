#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 06:06:57 2020

@author: elias
"""

import numpy as np

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