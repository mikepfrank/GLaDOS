#!/usr/bin/python3
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#|	FILE NAME:	glados-test.py								[Python 3 script]
#|
#|	DESCRIPTION:
#|
#|		This is just a throwaway script created for purposes of testing
#|		parts of the GLaDOS system, currently under development.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from pprint 	import pprint
from gpt3.api	import GPT3Core

gpt3 = GPT3Core()	# Create a new instance with default parameter values.

result = gpt3.genCompletion("Mary had a little lamb, ")

pprint(result)

#/-------------------------------------------------------------------------
#| Example output:
#|      {'choices': [{'finish_reason': 'length',
#|                    'index': 0,
#|                    'logprobs': None,
#|                    'text': '\n'
#|                            'Its fleece was white as snow, \n'
#|                            'And everywhere that Mary went, \n'
#|                            'The lamb was sure to go.\n'
#|                            '\n'
#|                            'It followed her to school one day, \n'
#|                            'That was against the'}],
#|       'created': 1601615096,
#|       'id': 'cmpl-fTJ18hALZLAlQCvPOxFRrjQL',
#|       'model': 'davinci:2020-05-03',
#|       'object': 'text_completion'}
#\-------------------------------------------------------------------------


