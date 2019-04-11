# SearchScript
Project on searching 'scripts' in russian text

## The Project's Purpose

This project's purpose is to learn to search scripts in a text.

The script is a set of action described in the text. To find the script means to find information about all action:

* who do this action
* when this action is done
* where this action is done
* how this action is done
* etc.

In current model we consider following information about action:

* actions subject
* actions object
* time
* place
* purpose
* actions way

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
3. Find all verb, particple and verbal participle
4. Exclude all PoS not expressing action
5. Extract all information from their environment

### Algorithm steps

...

## Project's structure

...