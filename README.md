# SearchScript
Project on searching 'scripts' in russian text

## The Project's Purpose

This project's purpose is to learn to search scripts in a text.

The script is a set of action described in the text. To find the script means to find information about all action:

* who do this action
* what is action object
* other action conditions

Examples of other conditions are action place, time, etc.

In current model we separate following information about action:

* action verb
* action subject
* action object
* other

## How Action Is Described

The action may be expressed by way of using following parts of speech (PoS):

* verb
* participle
* verbal participle.

*Important remark:* presence of any written above PoS in text is not equivalent to action presence in text.

## Examples of texts with and without scripts
 
1. *Являясь директором завода, он приказал сделать это.* There is only one action expressed by a verb *приказал*. Also there is a verbal participle *Являясь* not expressing some action.
2. *Федор пытался разбудить глубоко спящего Ивана.* There are two actions: the action expressed by a verb *пытался* and the action expressed by a participle *спящего*.
3. *Он был не очень умным и не очень.* There is not action but there is a verb *был*.
4. *Он обратился к являвшемуся специалисту в этой области Михаилу.* There is only one action expressed by verb *обратился*. Also there is participle *являвшемуся* not expressing some action.

## Algorithm description

### Simple algorithm description

1. Built syntactic tree
2. Find all verb, particple and verbal participle
3. Exclude all PoS not expressing action
4. Extract all information from their environment

### About syntectic tree

The tree is constructed as a modifictaion of a tree built through methods of module `isanlp` (see [Github of isanlp](https://github.com/IINemo/isanlp)).

Root of this tree and all dependences between vertices mathe with the root kid in `isanlp`-tree. Each vertice has two attribute: value that involves an information about postag, morph, lemma and index in sentence and list of kids and dependences.

Also all vertices have an attribute sentence. The root has initial sentence in the attribute. There is None here for the rest vertices.

## Project's structure

* [Demonstration](https://github.com/ASEDOS999/SearchScript/blob/master/Tests.ipynb) is a file with examples of project work
* [Code](https://github.com/ASEDOS999/SearchScript/blob/master/action.py) is a main code of extracting action and information about it
* [Experiments](https://github.com/ASEDOS999/SearchScript/tree/master/Process_type) is experiments that can improve our work