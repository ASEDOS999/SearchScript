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

## Project's structure

* [Demonstration](https://github.com/ASEDOS999/SearchScript/blob/master/Tests.ipynb) is a file with examples of project work
* [Code](https://github.com/ASEDOS999/SearchScript/blob/master/action.py) is a main code of extracting action and information about it
* [Experiments](https://github.com/ASEDOS999/SearchScript/tree/master/Process_type) is experiments that can improve our work

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

### About syntactic tree

The tree is constructed as a modifictaion of a tree built through methods of module `isanlp` (see [Github of isanlp](https://github.com/IINemo/isanlp)).

Root of this tree and all dependences between vertices match with the root kid in `isanlp`-tree. Each vertice has two attribute: value that involves an information about postag, morph, lemma and index in sentence and list of kids and dependences.

Also all vertices have an attribute sentence. The root has initial sentence in the attribute. There is None here for the rest vertices.

### About PoS not expressing action

In current version we exclude verbs from constant list. In current version the list involves following lemmas: *быть*, *мочь*, *уметь*.

### Information Extraction

In current version we can take into consideration following cases:

* simple cases
* verbs without action - see previous point
* conjucted verbs - in this case we get one subject to all verbs
* verbs with partcicle - in this case we join particle to a verb
* adverbal participle - the subject from the main action
* participle - the task to find participle often executes unsuccessfully.

## Main functions

There are all work functions in file *action.py*.

Function `construct_tree`:

* **Input:** text with sentences
* **Output:** list of syntactic trees roots

Function `get_actions`:

* **Input:** root of syntactic tree
* **Output:** list of objects of class `action`

Function `get_actions_tree`:

* **Input:** root of syntactic tree
* **Output:** root of action tree

## Output Format

### Class `action`

Class `action` has following attributes: 

* `name_action`
* `sentence`
* `inform` is a dictionary
* `keys` is a list of dictionary `inform` keys. In current version `self.keys = ['VERB', 'SUBJECT', 'OBJECT', 'OTHER']`.
* `type_action` is string

The `name_action` is string being the action name. The action name is created by following way. Let *VERB_LEMMA* be lemma of word expressing action and *ind* is this word index in sentence. Then name for this action is following: Action*ind*{*VERB_LEMMA*}. For example, we have sentence *Мама мыла раму.* Here an action is expressed by verb *мыла* with lemma *мыть* and index *1*. Then action name for it is `Action1{мыть}`.

The `sentence` is a list of tokens from initial sentence. You can construct usual sentence through function `construct_sentence`.

The `type_action` involves information about action. Now we save in this attribute information about verb form and verb mood. In current version `type_action` can take following values: `'Indicative'`, `'Imperative'`, `'Adv_Participle'`, `'Participle'`.

In the `inform['VERB']` there is tuple from three elements. The first element is object of class `word` that involves information about postag, morph, lemma and index in sentence for verb. The second is list of indexes in sentence for this verb and its particle. The third is always None and this element is existing for symmetry.

In the other field of dictionary `inform` there is lists of similar tuple from three elements. The first element is object of class `word` that involves information about postag, morph, lemma and index in sentence for this word. The second is list of indexes in sentence for this word and depending on it words. The third is a word dependence on a verb. Through second element of tuple one can reconstruct readable form of phrase using method `get_inform` of class `action`.

Method `get_inform` has three arguments `main_word, full_inform, depend_dict` and they are default `False`. The n-st argument corresponds to the n-th element of tuples in fields of dictionary `inform`. The function returns a list. Elements of this list is lists for that corresponding arguments was `True`.

### Action Tree

The root of action tree is object from class `tree`.

This class has attributes `value` and list `kids`. In action tree `value` is an object from class `action` and the list `kids` is the list of tuples. The first element of a tuple is object `action` that is a kid of current vertice, the second is type of dependece between the current vertice and its kid.

## Example

```python
import action

text = 'Мама мыла раму. И Федя мыл раму.'

root_list = action.construct_tree(text)

action_list = []
for root in root_list:
    action_list += get_actions(root)

action_tree = []
for root in root_list:
    action_tree.append(get_actions_tree(root))
```

You can find more examples in [Demonstration](https://github.com/ASEDOS999/SearchScript/blob/master/Tests.ipynb).