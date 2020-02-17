# SearchScript
Project on searching 'scripts' in russian texts.

## The Project's Purpose

This project's purpose is to learn to search scripts from a text. Informally, the script is a set of action, their characterstics and model of steps between this actions, i.e. the rules ordering actions. The formal description of the script you can find in the file [???](???). To find the script means to find information about all actions descibed in the text and about their relationships.

Today we consider only instructive texts. This problem is easier than global problem of scripts search because such texts are simple.


## How Action Is Described

The action may be expressed by way of using following parts of speech (PoS):

* verb
* participle
* verbal participle.

*Important remark:* presence of any written above PoS in text is not equivalent to action presence in text.


Examples of texts with and without actions
 
1. *Являясь директором завода, он приказал сделать это.* There is only one action expressed by a verb *приказал*. Also there is a verbal participle *Являясь* not expressing some action.
2. *Федор пытался разбудить глубоко спящего Ивана.* There are two actions: the action expressed by a verb *пытался* and the action expressed by a participle *спящего*.
3. *Он был не очень умным и не очень.* There is not action but there is a verb *был*.
4. *Он обратился к являвшемуся специалисту в этой области Михаилу.* There is only one action expressed by verb *обратился*. Also there is participle *являвшемуся* not expressing some action.

The main characteristics of the actions are the information about:

* semantic children
* syntactic children

The information about children may be following:

* word of child
* semantic/syntactic role
* some word embedding
* sense group (for example, the group of documents, the group of cars details and etc.)

## Algorithm Description

### Algorithm
Let's describe method that we use for to solve it. This method can be devided into three steps:

1. Find all verbs in the different verbs
2. Separate all found verbs into three groups

    * **The First Level:** the verbs that express call for action, i.e. verbs in imperative form, modal verbs of the second person
    * **The Second Level:** modal verbs that were not included into the First Level
    * **The Third Level:** other verbs

3. For the all verbs from the first and second level find all semantic/syntactic children and required information about them.
4. Constuct script's graph

### Children Information

...

### Script's Graph

...

## Project's Structure

...
