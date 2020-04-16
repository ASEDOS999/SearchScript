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
    for key in table:
        table_text = table[key]
        help_list = []
        help_sentences = []
        for item in table_text:
            for act in item['Actions']:
                help_sentences.append(item["Sentence"])
                help_list.append(act)
        sentences.append(help_sentences)
        full_list_actions.append(help_list)
    verb_dict = dict()
    feature_dict = dict()
    N = 0
    N_verb = 0
    for key in table:
        table_text = table[key]
        for item in table_text:
            actions = item['Actions']
            sentence = item['Sentence']
            for act in actions:
                b, e = act.inform['VERB'][0].begin, act.inform['VERB'][0].end
                N_verb += 1
                verb = sentence[b:e]
                if verb in verb_dict:
                    verb_dict[verb] += 1
                else:
                    verb_dict[verb] = 1
                for depend in act.inform:
                    if not depend in ['punct', 'VERB']:
                        for w in act.inform[depend]:
                            N += 1
                            lemma = w[0].lemma
                            if key_word == "lemma":
                                if lemma in feature_dict:
                                    feature_dict[lemma] += 1
                                else:
                                    feature_dict[lemma] = 1
                            if key_word == "depend_lemma":
                                if (depend, lemma) in feature_dict:
                                    feature_dict[(depend, lemma)] += 1
                                else:
                                    feature_dict[(depend, lemma)] = 1
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

def construct_graph(table, key_word = "depend_lemma", with_next = False):
    full_list_actions, verb_dict, feature_dict = get_feature_dict(table, key_word)
    table = create_table_of_sets(feature_dict, full_list_actions)
    V = [i for j in table for i in j]
    V.sort(key = lambda x: x[0])
    E = {v:[] for v in V}
    if with_next:
        for ind, v in enumerate(V):
            if ind+1 < len(V) and V[ind+1][0] > v[0]:
                E[v].append(V[ind+1])
    for i in table:
        for v in i:
            for v_ in i:
                if v_ != v and not v_ in E[v]:
                    E[v].append(v_) 
    docs = np.unique(np.array([i[0] for i in V]))
    start_docs = [min([i[1] for i in V if i[0] == j]) for j in docs]
    end_docs = [max([i[1] for i in V if i[0] == j]) for j in docs]
    start = (-1, -1)
    end = (-2, -2)
    V.append(start)
    V.append(end)
    E[start] = []
    E[end] = []
    for ind, i in enumerate(start_docs):
        v = docs[ind], i
        E[start].append(v)
    for ind, i in enumerate(end_docs):
        v = docs[ind], i
        if not v in E[start]:
            E[v].append(end)
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