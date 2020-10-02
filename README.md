# GLaDOS
The Generic Lifeform and Domicile Operating System - An operating environment for text-based AI systems.

## Purpose

The ultimate purpose of GLaDOS is to experiment with giving text-based AIs a "user environment" that 
they can manipulate, as an experiment to see if the right environment can get them to exhibit some
higher-level degree of intentionality and cognition.

## Usage

So far there is only a simple API wrapper and a very simple test script.  To run it, do the following:

    $ export OPENAI_API_KEY=<YourAPIKeyGoesHere>
    $ pip3 install openai
    $ pip3 install backoff
    $ cd src
    $ python3 glados-test.py

and if all goes well, you will see output something like the following:

    {'choices': [{'finish_reason': 'length',
                    'index': 0,
                    'logprobs': None,
                    'text': '\n'
                            'Its fleece was white as snow, \n'
                            'And everywhere that Mary went, \n'
                            'The lamb was sure to go.\n'
                            '\n'
                            'It followed her to school one day, \n'
                            'That was against the'}],
       'created': 1601615096,
       'id': 'cmpl-fTJ18hALZLAlQCvPOxFRrjQL',
       'model': 'davinci:2020-05-03',
       'object': 'text_completion'}

I plan to add many more features to this system over the coming weeks and months.
