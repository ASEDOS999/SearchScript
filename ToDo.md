# Search Script

## The Project's Purpose

This project's purpose is to learn to search scripts in a text.

The script is some action. To find script means to find information about this action such as

* who do this action
* when this action is done
* where this action is done
* how this action is done
* etc.

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

## Possible algorithm

1. **Tokenization**
2. **Lemmatization**
3. **Finding** all verb, particple and verbal participle
4. **Excluding** all PoS not expressing action
5. **Extracting** all information from their environment

## Open Questions

1. Modal verbs (*быть*, *являться*, *мочь*, etc.)
2. Verbs mood