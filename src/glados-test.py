#!/usr/bin/python3

from pprint 	import pprint
from gpt3.api	import GPT3Core

gpt3 = GPT3Core()	# Create a new instance with default parameter values.

result = gpt3.genCompletion("Mary had a little lamb, ")

pprint(result)



