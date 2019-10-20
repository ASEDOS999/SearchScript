# SearchScript
Project on searching 'scripts' in russian text

## The Project's Purpose

This project's purpose is to learn to search scripts in a text. The script is a set of action described in the text. To find the script means to find information about all action descibed in the text abd about their relationships.

Today we consider only instructive texts. This problem is easier than global problem of scripts search because such texts are simple.

## Project's structure

...


## How Action Is Described

The action may be expressed by way of using following parts of speech (PoS):

* verb
* participle
* verbal participle.

*Important remark:* presence of any written above PoS in text is not equivalent to action presence in text.

## Examples of texts with and without actions
 
1. *Являясь директором завода, он приказал сделать это.* There is only one action expressed by a verb *приказал*. Also there is a verbal participle *Являясь* not expressing some action.
2. *Федор пытался разбудить глубоко спящего Ивана.* There are two actions: the action expressed by a verb *пытался* and the action expressed by a participle *спящего*.
3. *Он был не очень умным и не очень.* There is not action but there is a verb *был*.
4. *Он обратился к являвшемуся специалисту в этой области Михаилу.* There is only one action expressed by verb *обратился*. Also there is participle *являвшемуся* not expressing some action.

## Algorithm description

### Simple algorithm description

Let's describe method that we use for to solve it. This method can be devided into three steps:

1. Segmentation. One separates    full text into a sequence of such litle texts as each segment include only one action and all information about it.
2. ...
