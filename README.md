# SearchScript
Project on searching 'scripts' in russian texts.

## The Project's Purpose

This project's purpose is to learn to search scripts from a text. Informally, the script is a set of action, their characterstics and model of steps between this actions, i.e. the rules ordering actions. The formal description of the script you can find in the file [???](???). To find the script means to find information about all actions descibed in the text and about their relationships.

Today we consider only instructive texts. This problem is easier than global problem of scripts search because such texts are simple.

## The Project's Structure

Before the start of work you have to run script start_docker.py and install library [isanlp](https://github.com/IINemo/isanlp).

A main part is a module 'ScriptExtract.Preprocessing.TextProcessing'. It allows to separate text into sentences, find all actions-instructions and process syntactic dependences and semantic relations.

Important class in this module is class 'table'. The argument 'use_sem' is bool variable that signals about processing or not processing relations. The methods 'get_table' and 'extract_one' process a list of texts or one text and return dictionary of processed data or this data. This methods input is list of files name as string or one file's name as string.

The structure of data is a list of element. Each element is dictionary with the following fields:

* "Sentence" - one processed sentence, type string.
* "Actions" is a list of found actions. Each action is a class with the several attributes and methods. The most interesting is attribute 'inform'. It is dictionary that includes key "VERB". The value in this key is tuple of three elements - (class word, list of indexes of additional words, None). The other keys mean syntactic dependences with the parent-verb and value in them are similar tuple:
    * The first element is class word. It has the following attributes:
        * 'lemma'
        * 'postag'
        * 'morph'
        * 'index' is index of word in sentence
        * 'begin' is begin of word in sentence in symbols
        * 'end' is end of word in sentence in symbols
        * 'role' is semantic role
        * 'anaphor_resolution' is field for pronouns which anaphora was resolve
    * The second element is index of additional words. For verb it is depending on it words that has not information between this word. For not verb it is depending syntactic tree.
    * The third element is a type of dependence. It matches with key of dictionary 'inform'.
* "TagUd" is a list of TagUd representation of sentence. Now we don't make it.
* "Relations" is a semantic relations. If 'use_sem' is 'False' it is an empty list.
