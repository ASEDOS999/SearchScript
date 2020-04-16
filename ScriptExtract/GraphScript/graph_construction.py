#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 06:06:57 2020

@author: elias
"""

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
