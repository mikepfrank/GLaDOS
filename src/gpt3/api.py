#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|						TOP OF FILE:	gpt3/api.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	MODULE NAME:	gpt3.api								[Python 3 module]

	IN PACKAGE:		gpt3
	FULL PATH:		$GIT_ROOT/GLaDOS/src/gpt3/api.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GladOS (Gladys' Lovely and Dynamic Operating System)
	APP NAME:		GLaDOS.server (GladOS server application)
	SW COMPONENT:	GLaDOS.gpt3 (GladOS GPT interface component)


	MODULE DESCRIPTION:
	===================

		This module implements a convenience wrapper around OpenAI's API
		for accessing their GPT language models.  The main feature that
		this wrapper provides at the moment is keeping track of the current
		values of various API parameters.  It also provides handy functions
		for things like measuring string lengths in tokens.


	PUBLIC CLASSES:
	===============

	For the regular completions API, the following classes are defined:

		GPT3APIConfig - Keeps track of a set of API parameter settings.
			These can also be modified dynamically.
		
		GPT3Core - A connection to the core GPT system that maintains
			its own persistent API parameters.

		Completion - For objects representing results returned by the 
			core API.


	For the chat completions endpoint, the following classes are defined:

		GPT3ChatAPIConfig - Keeps track of a set of API parameter settings
			for the chat API.  These can also be modified dynamically.

		GPT3ChatCore - A connection to the chat GPT system that maintains
			its own persistent API parameters, including a persistent list
			of in-context chat messages.
		
		ChatMessages - This object maintains a list of chat messages that 
			can be used as context for a chat API call.  It also provides
			methods for adding new messages to the list and counting the
			number of tokens in the message list.
		
		ChatCompletion - For objects representing results returned by the
			chat API.


	Exception classes:

		PromptTooLargeException - Exception raised when a prompt is too
			large for the API to handle. The caller may want to respond
			by reducing the number of tokens in the prompt and retrying.


	PUBLIC GLOBALS:
	===============

		Note: The following global module parameters can be modified 
		dynamically by the user. They will affect the properties of
		subsequently-created instances of GPT3Core, but not of the
		existing instances.	 To modify an existing instance, access
		its .conf property.

			DEF_ENGINE	- GPT engine name (default 'davinci').
			DEF_TOKENS	- Max. number of tokens to output (def. 42).
			DEF_TEMP	- Default temperature (default is 0.5).
			DEF_STOP	- Stop string or strings (3 newlines).

		The following constants are for use with the chat API:

			CHAT_ROLE_SYSTEM	- Role of the system in a chat.
			CHAT_ROLE_USER		- Role of the user in a chat.
			CHAT_ROLE_AI		- Role of the AI in a chat.
			
		New in the functions interface:

			CHAT_ROLE_FUNCALL	- Role for a "function call"
									message (normally issued
									by the AI itself).

			CHAT_ROLE_FUNCRET		- Role for a "function return"
									message (usually created
									by an application in response
									to a function call by the AI.


	PUBLIC FUNCTIONS:
	=================
	
			countTokens()	- Counts tokens in a string using the API.  Note 
				that this operation is expensive since it calls the subscription-
				based REST service from OpenAI.	For most applications, you should
				use one of the below two functions instead. [DEPRECATED]

			createAPIConfig() - Creates a new GPT3APIConfig or GPT3ChatAPIConfig
				object, depending on the value of the 'engineId' parameter.

			createCoreConnection() - Creates a new GPT3Core or GPT3ChatCore
				object, depending on the value of the 'engineId' parameter.

			isChatEngine() - Returns True if the specified engine ID is
				one of the chat engines, False otherwise.

			local_countTokens() - Counts tokens in a string using the local
				tokenizer.  This is much faster than the above function, but
				requires GPT-2 to be installed locally.  It is also not as
				accurate as the below function in all cases, since it does 
				not use the correct tokenizer encoding for all GPT models.
				[DEPRECATED]
			
			tiktokenCount() - Counts tokens in a string using the local
				tiktoken library.  This is much faster than the above functions,
				and allows specifying the tokenizer encoding to use.  It is
				highly recommended that you use this function instead of the
				above two functions.

			loadStatsIfNeeded() - Loads the usage statistics from the
				filesystem, if they have not already been loaded.

			stats() - Returns a human-readable table of usage statistics, as
				a string. Example table appearance:

									 	  Token Counts
									 ~~~~~~~~~~~~~~~~~~~~~~~
					Engine Name      Input   Output  Total    USD Cost
					================ ======= ======= ======= =========
								 ada       0       0       0 $  0.0000
							 babbage       0       0       0 $  0.0000
							   curie 7410900    6146 7417046 $ 44.5023
							 davinci       0       0       0 $  0.0000
						text-ada-001       0       0       0 $  0.0000
					text-babbage-001       0       0       0 $  0.0000
					  text-curie-001       0       0       0 $  0.0000
					text-davinci-001       0       0       0 $  0.0000
					text-davinci-002       0       0       0 $  0.0000
					~~~~~~~~~~~~~~~~ ~~~~~~~ ~~~~~~~ ~~~~~~~ ~~~~~~~~~
					TOTALS:          7410900    6146 7417046 $ 44.5023

				NOTE: The table formatting algorithm used is currently very 
				brittle, and needs significant improvement.

				
	EXAMPLES:

		/----------------------------------------------------------\
		| #!/usr/bin/python3									   |
		|														   |
		| from pprint	import pprint							   |
		| from gpt3.api import GPT3Core							   |
		|														   |
		| gpt3 = GPT3Core()										   |
		|	# Makes a new instance w. default parameter values.	   |
		|														   |
		| result = gpt3.genCompletion("Mary had a little lamb,")   |
		|														   |
		| pprint(result.complStruct)							   |
		\----------------------------------------------------------/
			|
			V 
			
		{'choices': [{'finish_reason': 'length',
					  'index': 0,
					  'logprobs': None,
					  'text': '\n'
							  'Its fleece was white as snow,\n'
							  'And everywhere that Mary went,\n'
							  'The lamb was sure to go.\n'
							  '\n'
							  'It followed her to school one day,\n'
							  'That was against the'}],
		 'created': 1601615096,
		 'id': 'cmpl-fTJ18hALZLAlQCvPOxFRrjQL',
		 'model': 'davinci:2020-05-03',
		 'object': 'text_completion'}

"""


#/==============================================================================
#|
#|	 1. Module imports.								   	   [module code section]
#|
#|			Load and import names of (and/or names from) various
#|			other python modules and pacakges for use from within
#|			the present module.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	#/==========================================================================
	#|	1.1. Imports of standard python modules.		[module code subsection]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#from	sys			import	stderr	# Not currently used.

import	random

import	re	# Regex

from	os			import	path, rename, makedirs, getenv
	# Manipulate filesystem path strings, create directories.

from	pprint		import	pformat #,pprint	# Pretty-print complex objects.

import	json		# We use this to save/restore the API usage statistics.

from	datetime	import	date, datetime
	# We use datetime to tag new messages with the current time.
	# We use date to determine when to switch stats files.

from	curses.ascii	import	RS #, STX, ETX	# We use these to delimit messages.
			# We previously assumed [STX][ETX] delimiters surrounded each message.
			# We new assume that an [RS] token terminates each message.

	#/==========================================================================
	#|	1.2. Imports of modules to support GPT-3.		[module code subsection]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import	openai		# OpenAI's Python bindings for their REST API to GPT-3.
from	openai	import	OpenAI	# Client constructor.

import	tiktoken	# A fast standalone tokenizer module for GPT-3.
import	backoff		# Utility module for exponential backoff on failures.

	#/==========================================================================
	#|	1.3. Imports of custom application modules. 	[module code subsection]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	1.3.1.  The following modules, although custom, are generic
		#|		utilities, not specific to the present application.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from	infrastructure.decorators	import	singleton

			#-------------------------------------------------------------------
			#  The logmaster module defines our logging framework; we import 
			#  specific definitions we need from it. (This is a little cleaner 
			#  stylistically than "from ... import *".)

from	infrastructure				import	logmaster	# For doDebug
from	infrastructure.logmaster	import	getComponentLogger, sysName

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Use our package name.
_logger = getComponentLogger(_component)			# Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	1.3.2. The below modules are specific to the present application.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Comment this out eventually.
from	tokenizer.tokenizer		import	countTokens as local_countTokens
	# Method to count tokens without a remote API call.
	# (NOTE: This is now superseded by the tiktokenCount() function
	# defined in this module.)

from	config.configuration	import	TheAIPersonaConfig
	# This allows us to access configuration information for the specific
	# AI persona that we are using.


#/==============================================================================
#|	2. Module-level global constants.							[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	__all__			[special module attribute / global constant structure]
	#|
	#|		These are the names that will be imported if you do 
	#|		'from gpt3.api import *'.  This in effect declares what
	#|		the public interface to this module consists of.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__
__all__ = [


		#|~~~~~~~~~~~~~~~~~~~~~~~
		#| Module public globals.

			# Module public global parameters. (May be modified by user.)

		'DEF_ENGINE',		# Parameter: Default GPT-3 engine name ('davinci').
		'DEF_TOKENS',		# Parameter: Default number of tokens to return (100).
		'DEF_TEMP',			# Parameter: Default temperature value (normally 0.75).
		'DEF_STOP',			# Parameter: Default stop string ("\n\n\n") or list of strings.

			# Module public global constants.

		'CHAT_ROLE_SYSTEM',	# Constant: Role name for the system in a chat session.
		'CHAT_ROLE_USER',	# Constant: Role name for the user in a chat session.
		'CHAT_ROLE_AI',		# Constant: Role name for the AI in a chat session.
		
		'CHAT_ROLE_FUNCALL',	# Constant: Role name for function calls issues by the AI.
		'CHAT_ROLE_FUNCRET',	# Constant: Role name for function results returned to the AI.


		#|~~~~~~~~~~~~~~~~~~~~~~~
		#| Module public classes.

			# Module public classes for the regular GPT-3 completions API.

		'GPT3APIConfig',	# Class: A collection of API parameter settings.
		'GPT3Core',			# Class: Instance of the API that remembers its config.
		'Completion',		# Class: An object for a result returned by the API.

			# Module public classes for the GPT chat API.

		'GPT3ChatAPIConfig',	# Class: A collection of chat API parameter settings.
		'ChatMessages',			# Class: Maintains a list of chat messages.
		'GPT3ChatCore',			# Class: Instance of the chat API that remembers its config & messages.
		'ChatCompletion',		# Class: An object for a result returned by the chat API.
	
			# Exception classes.

		'PromptTooLargeException',	# Exception: Prompt is too long to fit in GPT-3's receptive field.
		

		#|~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Module public functions.

		'countTokens',			# Function: Counts tokens in a string. (Costs!)
			# NOTE: This function is deprecated; use the local_countTokens()
			# or preferably the tiktokenCount() function instead.
		
		'createAPIConfig',		# Function: Creates a GPT-3 API configuration object.
			# NOTE: This could return either a GPT3APIConfig or a 
			# GPT3ChatAPIConfig object, depending on the selected engine type.

		'createCoreConnection',	# Function: Creates a GPT-3 API connection object.
			# NOTE: This could return either a GPT3Core or a GPT3ChatCore object,
			# depending on the selected engine type.

		'isChatEngine',			# Function: Returns True if the engine is a chat engine.

		'loadStatsIfNeeded',	# Function: Loads the GPT-3 usage statistics file 
			# if not already loaded.

#		'local_countTokens',	# Function: Counts tokens in a string. (No cost.)
			# NOTE: This function is deprecated since it creates a dependency on
			# GPT-2 having been installed; use the tiktokenCount() function instead.

		'messageRepr',			# Function: Returns a string representation of a chat message.

		'tiktokenCount',		# Function: Counts tokens in a string. (No cost, fast.)
			# NOTE: This is the recommended token-counting function.

		'stats',				# Function: Returns the GPT-3 usage statistics.

		'genImage',				# Function: Generate an image from a description.
		'transcribeAudio',		# Function: Transcribe an audio file to text.
		'describeImage',		# Function: Generate a text description of an image.

	]


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|  _ENGINE_ATTRIBS				[module global private constant structure]
	#|
	#|	    This is a dictionary mapping GPT-3 engine names to their 
	#|		associated attributes.  So far, we mainly care about the
	#|		'field-size' attribute, which is the number of tokens in
	#|		the GPT-3 receptive field, and the 'price' attribute,
	#|		which is the cost (per 1,000 tokens) to use the engine.
	#|		A few other attributes are also documented below.
	#|
	#|		Later on, we may add more attributes to this structure,
	#|		and use the individual sub-dictionaries to represent the
	#|		engine we are currently working with.
	#|
	#|	Attributes:
	#|	-----------
	#|		'engine-name'	- The name of the engine.
	#|		'field-size'	- The number of tokens in the GPT-3 receptive field.
	#|							(This is also often called the context window.)
	#|		'price'			- The cost (per 1,000 tokens) to use the engine.
	#|		'is-chat'		- True if the engine is a chat engine.
	#|		'encoding'		- The token encoding used by the engine. [DEPRECATED]
	#|			These are defined by the tiktoken library, and are:
	#|				'gpt2'	- Used by most GPT-3 engines.
	#|				'p50k_base'	- Used by the code models and GPT-3.5 engines.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

_ENGINES = [
		# OG GPT-3 models; data through Oct. 2019.

    {'model-family': 'GPT-3',	'engine-name': 'ada', 					'field-size': 2048, 'price': 0.0004,	'is-chat': False,	'encoding': 'gpt2'},
    {'model-family': 'GPT-3',	'engine-name': 'babbage',				'field-size': 2048, 'price': 0.0005,	'is-chat': False,	'encoding': 'gpt2'},
    {'model-family': 'GPT-3',	'engine-name': 'curie',	    			'field-size': 2048, 'price': 0.002,		'is-chat': False,	'encoding': 'gpt2'},
    {'model-family': 'GPT-3',	'engine-name': 'davinci',				'field-size': 2048, 'price': 0.02,		'is-chat': False,	'encoding': 'gpt2'},
    {'model-family': 'GPT-3',	'engine-name': 'davinci:2020-05-03',	'field-size': 2048, 'price': 0.02,		'is-chat': False,	'encoding': 'gpt2'},
    
		# Early InstructGPT models. (RLHF trained; data through Oct. 2019.)

    {'model-family': 'GPT-3/Instruct',	'engine-name': 'text-ada-001',		'field-size': 2048, 'price': 0.0004,	'is-chat': False,	'encoding': 'gpt2'},
    {'model-family': 'GPT-3/Instruct',	'engine-name': 'text-babbage-001',	'field-size': 2048, 'price': 0.0005,	'is-chat': False,	'encoding': 'gpt2'},
    {'model-family': 'GPT-3/Instruct',	'engine-name': 'text-curie-001',	'field-size': 2048, 'price': 0.002,		'is-chat': False,	'encoding': 'gpt2'},
    {'model-family': 'GPT-3/Instruct',	'engine-name': 'text-davinci-001',	'field-size': 2048, 'price': 0.02,		'is-chat': False,	'encoding': 'gpt2'},

		# GPT-3.5 models. (Increased context length; data through June 2021.)

    {'model-family': 'GPT-3.5',	'engine-name': 'text-davinci-002', 'field-size': 4000, 'price': 0.06,		'is-chat': False,	'encoding': 'p50k_base'},
    {'model-family': 'GPT-3.5',	'engine-name': 'code-davinci-002', 'field-size': 8001, 'price': 0,			'is-chat': False,	'encoding': 'p50k_base'},
    {'model-family': 'GPT-3.5',	'engine-name': 'text-davinci-003', 'field-size': 4000, 'price': 0.02,		'is-chat': False,	'encoding': 'p50k_base'},
		# GPT-3.5-turbo-instruct. (Speed & pricing like GPT-3.5 Turbo, trained like GPT-3 Instruct.)
	{'model-family': 'GPT-3.5', 'engine-name': 'gpt-3.5-turbo-instruct', 'field-size': 4000, 'prompt-price': 0.0015, 'price': 0.002, 'is-chat': False,  'encoding': 'p50k_base'},
    
		# ChatGPT-3.5 models. (These use the chat API. Data through Sep. 2021.)

    {'model-family': 'ChatGPT',	'engine-name': 'gpt-3.5-turbo', 		'field-size': 4096, 	'prompt-price': 0.0015,	'price': 0.002,		'is-chat': True,	'encoding': 'p50k_base'},
	{'model-family': 'ChatGPT',	'engine-name': 'gpt-3.5-turbo-0301', 	'field-size': 4096, 	'prompt-price': 0.0015,	'price': 0.002,		'is-chat': True,	'encoding': 'p50k_base'},
		# To be discontinued on 9/13/23. Switch to gpt-3.5-turbo-0613.
	{'model-family': 'ChatGPT',	'engine-name': 'gpt-3.5-turbo-0613', 	'field-size': 4096, 	'prompt-price': 0.0015,	'price': 0.002,		'is-chat': True,	'encoding': 'p50k_base'},
    
		# 16k ChatGPT-3.5 models. (Context window size increased to 16,384.)

	{'model-family': 'ChatGPT',	'engine-name': 'gpt-3.5-turbo-16k', 		'field-size': 16384, 	'prompt-price': 0.003,	'price': 0.004,		'is-chat': True,	'encoding': 'p50k_base'},
	{'model-family': 'ChatGPT',	'engine-name': 'gpt-3.5-turbo-16k-0613', 	'field-size': 16384, 	'prompt-price': 0.003,	'price': 0.004,		'is-chat': True,	'encoding': 'p50k_base'},
	{'model-family': 'ChatGPT',	'engine-name': 'gpt-3.5-turbo-0125',	 	'field-size': 16384, 	'prompt-price': 0.0005,	'price': 0.0015,	'is-chat': True,	'encoding': 'p50k_base'},

		# GPT-4 models.  (These also use the chat API. Data through Sep. 2021.)

	{'model-family': 'GPT-4',	'engine-name': 'gpt-4',			'field-size': 8192, 'price': 0.06,	'prompt-price': 0.03,	'is-chat': True,	'encoding': 'p50k_base'},
	{'model-family': 'GPT-4',	'engine-name': 'gpt-4-0314',	'field-size': 8192, 'price': 0.06,	'prompt-price': 0.03,	'is-chat': True,	'encoding': 'p50k_base'},
		# To be discontinued on 9/13/23. Switch to gpt-4-0613.
	{'model-family': 'GPT-4',	'engine-name': 'gpt-4-0613',	'field-size': 8192, 'price': 0.06,	'prompt-price': 0.03,	'is-chat': True,	'encoding': 'p50k_base'},
		# NOTE: In these models, prompt tokens are discounted, so there's a new field 'prompt-price'.

		# 32k GPT-4 models. (Context window size increased to 32,768 tokens.)
	{'model-family': 'GPT-4',	'engine-name': 'gpt-4-32k',			'field-size': 32768, 'price': 0.12,	'prompt-price': 0.06,	'is-chat': True,	'encoding': 'p50k_base'},
	{'model-family': 'GPT-4',	'engine-name': 'gpt-4-32k-0613',	'field-size': 32768, 'price': 0.12,	'prompt-price': 0.06,	'is-chat': True,	'encoding': 'p50k_base'},

		# 128k GPT-4 models. (Context window size increased to 128,000 tokens; data through Apr. 2023.)
	{'model-family': 'GPT-4', 'engine-name': 'gpt-4-turbo-preview',  'field-size': 128000, 'prompt-price': 0.01, 'price': 0.03, 'is-chat': True, 'has-vision': False, 'encoding': 'p50k_base'},
	{'model-family': 'GPT-4', 'engine-name': 'gpt-4-1106-preview',   'field-size': 128000, 'prompt-price': 0.01, 'price': 0.03, 'is-chat': True, 'has-vision': False, 'encoding': 'p50k_base'},
	{'model-family': 'GPT-4', 'engine-name': 'gpt-4-0125-preview',   'field-size': 128000, 'prompt-price': 0.01, 'price': 0.03, 'is-chat': True, 'has-vision': True, 'encoding': 'p50k_base'},
	
		# 128k GPT-4V models. (Vision capability added.)
	{'model-family': 'GPT-4V', 'engine-name': 'gpt-4-vision-preview',      'field-size': 128000, 'prompt-price': 0.01, 'price': 0.03, 'is-chat': True, 'has-vision': True, 'encoding': 'p50k_base'},
	{'model-family': 'GPT-4V', 'engine-name': 'gpt-4-1106-vision-preview', 'field-size': 128000, 'prompt-price': 0.01, 'price': 0.03, 'is-chat': True, 'has-vision': True, 'encoding': 'p50k_base'},

] # End _ENGINES constant module global data structure.

# Set of models that support the functions interface.
# TO DO: Change this to a field in _ENGINES.
_FUNCTION_MODELS = [
	'gpt-3.5-turbo',			# Supports functions as of 6/13/'23.
	'gpt-3.5-turbo-0613',
	'gpt-3.5-turbo-16k',
	'gpt-3.5-turbo-16k-0613',
	'gpt-3.5-turbo-0125',
	'gpt-4',					# Supports functions as of 6/13/'23.
	'gpt-4-0613',
	'gpt-4-32k',				# Supports functions as of 6/13/'23.
	'gpt-4-32k-0613',
	'gpt-4-turbo-preview',
	'gpt-4-1106-preview',
	'gpt-4-0125-preview',
	'gpt-4-vision-preview',
	'gpt-4-1106-vision-preview',
]
def _has_functions(engine_name):
	"""Return True if the named engine supports the functions interface."""
	return engine_name in _FUNCTION_MODELS

# Generate the _ENGINE_ATTRIBS fast lookup table for engine attributes by engine name.
_ENGINE_ATTRIBS = dict()
for _engine_dict in _ENGINES:
	_engine_name = _engine_dict['engine-name']
	_engine_dict['has-functions'] = _has_functions(_engine_name)
	_ENGINE_ATTRIBS[_engine_name] = _engine_dict


		#----------------------------------------------------------------------
		#  The following are private convenience functions for retrieving
		#  information from the _ENGINE_ATTRIBS data structure.

# Given an engine name, return the entire engine attribute dictionary.
def _get_engine_attribs(engine_name):
	"""Given an engine name string, return the corresponding engine 
		attribute dictionary."""
	return _ENGINE_ATTRIBS[engine_name]

# Given an engine name and an attribute name, return the attribute value.
def _get_engine_attr(engine_name, attr_name):
	return _get_engine_attribs(engine_name)[attr_name]

# Given an engine name, return the model-family attribute value.
def _get_model_family(engine_name):
	"""Given an engine name string, return the corresponding model-family 
		attribute value."""
	return _get_engine_attr(engine_name, 'model-family')

# Given an engine name, return the field-size attribute value.
def _get_field_size(engine_name):
	"""Given an engine name string, return the corresponding field-size 
		attribute value."""
	return _get_engine_attr(engine_name, 'field-size')

# Given an engine name, return the price attribute value.
def _get_price(engine_name):
	"""Given an engine name string, return the corresponding price 
		attribute value."""
	return _get_engine_attr(engine_name, 'price')

# Given an engine name, return the prompt-price attribute value,
# or None if the engine doesn't have a prompt-price attribute.
def _get_prompt_price(engine_name):
	"""Given an engine name string, return the corresponding prompt-price 
		attribute value, or None if the engine doesn't have a prompt-price 
		attribute."""
	try:
		return _get_engine_attr(engine_name, 'prompt-price')
	except KeyError:
		return None

# Given an engine name, return whether it's a chat engine.
def _is_chat(engine_name):
	"""Given an engine name string, return the corresponding is-chat 
		attribute value."""
	return _get_engine_attr(engine_name, 'is-chat')

# Expose _is_chat() as a public function.
def isChatEngine(engineId:str):
	"""Given an engine name string, return a Boolean value which is
		True if and only if the engine uses the ChatCompletion API."""
	return _is_chat(engineId)

# Given an engine name, return the encoding attribute value.
# DEPRECATED; use tiktoken.encoding_for_model() instead.
def _get_encoding(engine_name):
	"""Given an engine name string, return the corresponding encoding 
		attribute value. [DEPRECATED]"""
	return _get_engine_attr(engine_name, 'encoding')


	# The following private constants are initialized based on the above.

global			_ENGINE_NAMES		# List of engine names.
# Retrieve this from the keys of the '_ENGINE_ATTRIBS' dictionary.
_ENGINE_NAMES	= list(_ENGINE_ATTRIBS.keys())

global 			_STATS_FILENAME		# Name of file for saving/loading API usage statistics.
_STATS_FILENAME = 'api-stats.json'	# This file is saved in the AI's data directory.
	# Note this is just hardcoded for now; eventually we may want to
	# make this configurable through the AI's configuration file.


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	These 'constants' provide default values for GPT-3's
	#|	parameters; but, note they can be overridden by the user.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global				DEF_ENGINE				# Default GPT-3 engine name.
#DEF_ENGINE			= 'davinci'				# This is the original largest (175B-parameter) model. Origin of Gladys.
DEF_ENGINE			= 'text-davinci-003'	# This is currently the recommended model for text generation.

global				DEF_CHAT_ENGINE		# Default engine when using the chat interface.
DEF_CHAT_ENGINE		= 'gpt-3.5-turbo'	# OpenAI updates this model periodically.

global			DEF_TOKENS	# Default minimum space (in tokens) provided for the return.
#DEF_TOKENS		= 42		# Of course.
DEF_TOKENS  	= 100		# Gladys requested this.

global			DEF_TEMP	# Default temperature value.
#DEF_TEMP		= 0.5		# Is this reasonable?
#DEF_TEMP		= 0.75		# I think this makes repeats less likely.
#DEF_TEMP		= 0.8		# Current default value, for a bit more creativity.
DEF_TEMP		= None		# This says to just use the API's default value.
# The default value in the GPT-3 API is just 1. Should we just use that value?

global			DEF_STOP	# Default stop string (or list of up to 4).
DEF_STOP		= None		# Let's try no stop. (This is the chat default anyway.)
#DEF_STOP		= "\n\n\n"	# Use 3 newlines (two blank lines) as stop.
	# Note this is anyway the default stop string used by the OpenAI API.
	# NOTE: IF YOU SET THIS TO '\n', IT BREAKS THE CHAT MODELS.


	# Constants for the chat interface (values are defined by OpenAI).

global				CHAT_ROLE_SYSTEM
CHAT_ROLE_SYSTEM	= 'system'

global				CHAT_ROLE_USER
CHAT_ROLE_USER		= 'user'

global				CHAT_ROLE_AI
CHAT_ROLE_AI		= 'assistant'

global				CHAT_ROLE_FUNCALL
CHAT_ROLE_FUNCALL	= 'function_call'

global				CHAT_ROLE_FRET
CHAT_ROLE_FUNCRET	= 'function'

	# TODO: Implement explicit support for function calling in this interface.


#|==============================================================================
#|	Module-level global variables.							  	[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| Recent versions of the API (incl. 1.2.3) require constructing a 
	#| "client" object and passing the API calls through that.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global		_client			# The OpenAI API client object.
_client		= OpenAI()		# Creates the client (we only need 1).


global 		_aiPath		# Path to the AI's data directory.
_aiPath 	= None		# Not yet initialized.


	#--------------------------------------------------------------
	# The following globals are used for tracking usage statistics.

global 			_statFile	# File object for saving/loading API usage statistics.
_statFile 		= None		# Not yet initialized.

global 			_statsLoaded	# Have we attempted to load stats from the file?
_statsLoaded 	= False			# We haven't tried to load stats from the file yet.

global 			_inputLength	# Length of the input string.
_inputLength 	= 0				# Will be modified when processing a query.


# Initialize two separate dicts to hold cumulative input & output token counts.

global _inputToks, _outputToks	# These are dictionaries of token counts.
	# (Cumulative tokens used for each engine since last reset.)

# Meanwhile, this dict will keep track of the cumulative estimated
# expenditures in dollars for each engine.

global _expenditures

# This global variable tracks the total cost in dollars across all engines.
global 			_totalCost

# String containing a formatted multi-line table showing the current statistics.
global 			_statStr		

# Function to reinitialize the stats variables. We do this daily.
def _clearStats():

	global _inputToks, _outputToks, _expenditures, _totalCost, _statStr

	_logger.info("Initializing engine usage statistics...")

	# Initialize all the various stats dictionaries to all-zero values.

	_inputToks = {}
	_outputToks = {}
	_expenditures = {}
	for engId in _ENGINE_NAMES:
		_inputToks[engId] = 0
		_outputToks[engId] = 0
		_expenditures[engId] = 0

	_totalCost 		= 0				# Initialize at stats load/save time.

	_statStr 		= ""		# Will be modified after processing a query.

_clearStats()	# Initialize the stats variables.

#|==============================================================================
#|	Module-level global objects.								  [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# This object represents an API connection to the GPT-3 core
	# system that is used for counting tokens.  It is not actually
	# created unless/until the GPT3Core.countTokens() method is 
	# called. Note that method is currently deprecated.

global	_theTokenCounterCore	# A core connection for counting tokens.
_theTokenCounterCore = None		# Initially not yet created.

	# IMPLEMENTATION NOTE: Since this API wrapper module may be used by multiple
	# threads, we need to protect the global variables & objects above with a 
	# mutex. We can do this easily by using the 'threading' module's 'Lock' 
	# class. A 'Lock' instance is a mutex that can be acquired and released.

import threading
global _lock
_lock = threading.RLock()	# Reentrant mutex lock for thread-safe operations.

	# NOTE: Any manipulation of the global variables in the previous section 
	# (in a way that needs to be effectively atomic) must be protected with 
	# the above '_lock' mutex. This can be done via the 'with' statement:
	#
	#		with _lock:
	#			...


#|==============================================================================
#|	Module public classes.										[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	gpt3.api.GPT3APIConfig							   [module public class]
	#|
	#|		This class provides an abstraction for a 'configuration' of
	#|		GPT-3 API parameter values.	 These can be modified dynamically
	#|		at runtime (i.e., in between different API calls).
	#|
	#|
	#|	Public interface:
	#|	=================
	#|
	#|		conf = GPT3AIConfig(params)					  [instance constructor]
	#|
	#|			Create a new configuration object with specified parameters.
	#|			Others not provided revert to defaults.
	#|
	#|
	#|		conf.modify(params)								   [instance method]
	#|
	#|			Modify the specified parameters of the configuration.
	#|
	#|
	#|		str(inst)								   [special instance method]
	#|
	#|			Converts the configuration to a human-readable string
	#|			representation.
	#|
	#|
	#|	Special methods:
	#|	----------------
	#|
	#|		__init__	- Instance initializer.
	#|		__str__		- Display as a human-readable string.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3APIConfig:

	"""This class gathers together a set of parameter values for passing to the
		'completions' and/or 'completions/browser_stream' API calls."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Instance public data members for class GPT3APIConfig. (See API docs.)
	#|
	#|	API parameters:		(See initializer header below for details.)
	#|
	#|		.engineId			 [string]
	#|		.suffix				 [string]
	#|		.maxTokens			 [intger]
	#|		.temperature		 [number]
	#|		.topP				 [number]
	#|		.nCompletions		 [integer]
	#|		.stream				 [boolean]
	#|		.logProbs			 [integer]
	#|		.echo				 [boolean]
	#|		.stop				 [string or array]
	#|		.presencePenalty	 [number]
	#|		.frequencyPenalty	 [number]
	#|		.bestOf				 [integer]
	#|
	#|	Other instance parameters:
	#|
	#|		.name [string] - Human-readable name for this configuration.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	Initializer for class GPT3APIConfig.	   [special instance method]
		#|
		#|	Arguments:
		#|	==========
		#|		
		#|		engineId											[string]
		#|
		#|			The name of the specific GPT-3 model/engine to use.
		#|			Choices as of 10/11/2020 are:  ada, ada-beta, babbage,
		#|			babbage-beta, content-filter-alpha-c4, curie, 
		#|			curie-beta, davinci, davinci-beta.	Earlier names
		#|			alphabetically are smaller models.	The default value
		#|			is currently text-davinci-003 (unless changed by user).
		#|
		#|		suffix												[string]
		#|
		#|			A text suffix to append to each completion. Defaults
		#|			to None.
		#|
		#|		maxTokens											[integer]
		#|
		#|			The maximum number of tokens to return in the response.
		#|			Defaults to 100 (unless changed by user).
		#|
		#|		temperature											[number]
		#|
		#|			A floating-point number between 0 and 1 that roughly
		#|			indicates the degree of randomness in the response.
		#|			Default value: 0.8 (unless changed by user).
		#|
		#|		topP												[number]
		#|
		#|			A floating point number between 0 and 1 that restricts
		#|			answers to the top percentage of probability mass.
		#|			Do not use this and temperature in the same query.
		#|			Default value: None (unless changed by user).
		#|
		#|			NOTE: topP is yet supported by this module.
		#|
		#|		nCompletions										[integer]
		#|
		#|			How many completions to return.	 Default value is 1.
		#|
		#|			NOTE: nCompletions values other than 1 are not 
		#|			currently supported by this module.
		#|
		#|		stream												[boolean]
		#|
		#|			If true, then the result will be streamed back incre-
		#|			mentally as a sequence of server-sent events.
		#|			Default value: False (unless changed by user).
		#|
		#|			NOTE: stream=true is yet supported by this module.
		#|			Anyway, it is only useful for very large responses.
		#|
		#|		logProbs											[integer]
		#|
		#|			Return the log-probabilities of this many of the top
		#|			most likely tokens, in addition to the sampled token
		#|			(which may or may not be in this set). Default: None.
		#|			(Meaning, don't return log-probabilities.)
		#|
		#|		echo												[boolean]
		#|
		#|			Includes the prompt in the response. Default: False.
		#|
		#|		stop												[object]
		#|
		#|			A string or an array of up to 4 strings, such that
		#|			the first occurrence of any of these strings in the 
		#|			output will terminate the response just before it.
		#|			Default value: Three newlines (two blank lines).
		#|
		#|		presPen												[number]
		#|
		#|			Number between 0 and 1 that penalizes new tokens
		#|			based on whether they appear in the text so far.
		#|			Default value: 0 (no penalty).
		#|
		#|		freqPen												[number]
		#|
		#|			Number between 0 and 1 that penalizes new tokens
		#|			based on how often they appear in the text so far.
		#|			Default value: 0 (no penalty).
		#|
		#|		bestOf												[integer]
		#|
		#|			Number of candidate completions to generate 
		#|			server-side; the best nCompletions ones of those 
		#|			are returned.  Default: Not set (i.e., don't do).
		#|
		#|			NOTE: Setting bestOf>1 increases generation cost.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(inst, 
					engineId:str=DEF_ENGINE,	maxTokens:int=DEF_TOKENS,	# API's default value for maxTokens is 16 (if not set here).
					temperature:float=DEF_TEMP, topP:float=None, 	# API's default temperature would be 1 (if not set here).
					nCompletions:int=None,		stream:bool=None,	# Defaults used to be: nCompletions=1, stream=False. (API defaults anyway.)
					logProbs:int=None,			echo:bool=False,	# I believe these values are the API default values anyway.
					stop=DEF_STOP,				presPen:float=None, # Used to set presPen to 0 here, but that's the default anyway, I think?
					freqPen:float=None,			bestOf:int=None,	# Used to set freqPen to 0 here, but that's the default anyway, I think?
					name=None,					suffix:str=None):

		"""Initialize a GPT-3 API configuration, reverting to
			default values for any un-supplied parameters."""
		
			# Save the values of the supplied configuration parameters.

		inst.engineId			= engineId
		inst.suffix				= suffix
		inst.maxTokens			= maxTokens
		inst.temperature		= temperature
		inst.topP				= topP
		inst.nCompletions		= nCompletions
		inst.stream				= stream
		inst.logProbs			= logProbs
		inst.echo				= echo
		inst.stop				= stop
		inst.presencePenalty	= presPen
		inst.frequencyPenalty	= freqPen
		inst.bestOf				= bestOf
		
		inst.name				= name		# Optional name for this config.
			# Note: The name is not used by the GPT-3 API, but it is
			# useful for the user to be able to identify a configuration
			# by name, rather than by its object ID.
	
	#__/ End instance initializer for class GPT3APIConfig,
	
	
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.modify(params)								[public instance method]
		#|
		#|		Modify the specified parameters of the configuration to
		#|		the given values. Any parameters not specified are left
		#|		unchanged.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def modify(self, 
				engineId:str=None,		maxTokens:int=None, 
				temperature:float=None, topP:float=None, 
				nCompletions:int=None,	stream:bool=None,	
				logProbs:int=None,		echo:bool=None,			
				stop=None,				presPen:float=None, 
				freqPen:float=None,		bestOf:int=None,
				suffix:str=None):

		"""Modify one or more parameter values in the configuration."""
		
		if engineId		!= None:	self.engineId			= engineId
		if suffix		!= None:	self.suffix				= suffix
		if maxTokens	!= None:	self.maxTokens			= maxTokens
		if temperature	!= None:	self.temperature		= temperature
		if topP			!= None:	self.topP				= topP
		if nCompletions != None:	self.nCompletions		= nCompletions
		if stream		!= None:	self.stream				= stream
		if logProbs		!= None:	self.logProbs			= logProbs
		if echo			!= None:	self.echo				= echo
		if stop			!= None:	self.stop				= stop
		if presPen		!= None:	self.presencePenalty	= presPen
		if freqPen		!= None:	self.frequencyPenalty	= freqPen
		if bestOf		!= None:	self.bestOf				= bestOf

	#__/ End instance method GPT3APIConfig.modify().

	
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	String converter.						   [special instance method]
		#|
		#|		Generates a human-readable string representation of this
		#|		API configuration.	This shows all the parameter values.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __str__(self):
	
		"""A human-readable string description of the parameter values."""
		
		if self.name == None:
			namestr = ""
		else:
			namestr = f" \"{self.name}\""
		
		return f"""
			GPT3 Configuration{namestr}:
				engine_id		  = {self.engineId}
				suffix			  = {self.suffix}
				max_tokens		  = {self.maxTokens}
				temperature		  = {self.temperature}
				top_p			  = {self.topP}
				n				  = {self.nCompletions}
				stream			  = {self.stream}
				logprobs		  = {self.logProbs}
				echo			  = {self.echo}
				stop			  = {repr(self.stop)}
				presence_penalty  = {self.presencePenalty}
				frequency_penalty = {self.frequencyPenalty}
				best_of			  = {self.bestOf}"""[1:]	# [1:] removes the leading newline.
		# NOTE: .stop is printed using repr() in order to show the 
		# 	escape codes for any special characters.
	
	#__/ End string conversion method for class GPT3APIConfig.

#__/ End class GPT3APIConfig.

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	Subclass GPT3ChatAPIConfig.				   	   [module public class]
		#|
		#|		This class extends the normal GPT-3 API configuration class
		#|		to add parameters needed for the chat completions endpoint.
		#|
		#|		See the API documentation for details on the parameters:
		#|		https://platform.openai.com/docs/api-reference/chat
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3ChatAPIConfig(GPT3APIConfig): pass
class GPT3ChatAPIConfig(GPT3APIConfig):
	"""This class extends the normal GPT-3 API configuration class to add
		parameters needed for the chat completions endpoint."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Instance public data members for class GPT3APIConfig. (See API docs.)
	#|
	#|	API parameters inherited from GPT3APIConfig:
	#|	--------------------------------------------
	#|		.engineId			[string]			'model' parameter
	#|		.maxTokens			[integer]			'max_tokens' parameter
	#|		.temperature		[number]			'temperature' parameter
	#|		.topP				[number]			'top_p' parameter
	#|		.nCompletions		[integer]			'n' parameter
	#|		.stream				[boolean]			'stream' parameter
	#|		.stop				[string or array]	'stop' parameter
	#|		.presencePenalty	[number]			'presence_penalty' parameter
	#|		.frequencyPenalty	[number]			'frequency_penalty' parameter
	#|
	#|	API parameters added by chat interface:
	#|	----------------------------------------
	#|		.messages			[array]				'messages' parameter
	#|		.logitBias			[dictionary]		'logit_bias' parameter
	#|		.user				[string]			'user' parameter
	#|
	#|	NOTE: Instead of setting up .messages and .user in the GPT3ChatAPIConfig,
	#|	applications may wish to pass them in individual calls to appropriate
	#|	GPT3ChatCore methods.
	#|
	#|
	#|	Other attributes:
	#|	-----------------
	#|		.name [string] - Human-readable name for this configuration.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	Initializer for class GPT3APIChatConfig.   [special instance method]
		#|
		#|		Note that this implementation extends the initializer for
		#|		GPT3APIConfig, so that we can inherit its parameter settings
		#|		as needed.
		#|
		#|	Arguments:	(Selected ones from our parent class, plus:)
		#|
		#|		.messages											[list]
		#|
		#|			List of message objects to be passed to the API.
		#|			(This might not be set yet at configuration time,
		#|			however.)
		#|
		#|		.logitBias											[dictionary]
		#|
		#|			Map from token IDs to biases from -100 to 100;
		#|			affects generation probabilities.
		#|
		#|		.user												[string]
		#|
		#|			A unique ID representing the end-user of the
		#|			application.  Used by OpenAI for enforcement.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(newGPT3ChatAPIConf:GPT3ChatAPIConfig, 
					engineId:str=DEF_CHAT_ENGINE,	maxTokens:int=None,		# Used to set maxTokens=DEF_TOKENS. But the API's default value for maxTokens is float('inf').
					temperature:float=DEF_TEMP, 	topP:float=None, 
					nCompletions:int=None,			stream:bool=None,		# Used to set nCompletions=1, stream=False here. But default anyway.
					stop=DEF_STOP,					presPen:float=None, 	# Used to set presPen=0 here, but default anyway.
					freqPen:float=None,				messages:list=None,		# Used to set freqPen=0 here, but default anyway.
					logitBias:dict=None,			user:str=None,
					name=None):
			# NOTE: logProbs, echo, and bestOf args from parent class are
			# not supported in this subclass.

		chatConf = newGPT3ChatAPIConf	# For convenience.

		# First, let's make sure that the engineId we were given is the
		# ID of an engine that supports the chat API; otherwise, it doesn't
		# make sense to create a GPT3ChatAPIConfig instance for it, and we
		# should report an error and throw an exception.

		if not _is_chat(engineId):

			_logger.error(f"GPT3ChatAPIConfig.__init__():  The engine ID '{engineId}' "
				"is not the ID of an engine that supports the chat API.")
		
			raise ValueError(f"Invalid engine ID '{engineId}' for chat API.")
		

		# Our parent class's initializer can take care of initialization for
		# everything but the 3 new arguments: messages, logitBias, and user.

		super().__init__(engineId=engineId, maxTokens=maxTokens,
		   temperature=temperature, topP=topP, nCompletions=nCompletions,
		   stream=stream, stop=stop, presPen=presPen, freqPen=freqPen,
		   name=name)
		
		# Save our special chat-related arguments.

		chatConf.messages	= messages
		chatConf.logitBias	= logitBias
		chatConf.user		= user

	#__/ End GPT3ChatAPIConfig instance initializer.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.modify(params)								[public instance method]
		#|
		#|		Modify the specified parameters of the chat configuration 
		#|		to the given values.  Note that this implementation extends
		#|		the .modify() method of GPT3APIConfig, so that we can inherit
		#|		its parameter settings as needed.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def modify(thisGPT3ChatAPIConf:GPT3ChatAPIConfig, 
				engineId:str=None,		maxTokens:int=None, 
				temperature:float=None, topP:float=None, 
				nCompletions:int=None,	stream:bool=None,	
				stop=None,				presPen:float=None, 
				freqPen:float=None,		messages:list=None,
				logitBias:dict=None,	user:str=None):

		"""Modify one or more parameter values in the chat configuration."""
		
		chatConf = thisGPT3ChatAPIConf	# For convenience.

		# Let our parent class handle most of the changes.

		super().modify(engineId=engineId, maxTokens=maxTokens,
			temperature=temperature, topP=topP, nCompletions=nCompletions,
			stream=stream, stop=stop, presPen=presPen, freqPen=freqPen)

		# Now we handle changes for our special chat-related arguments.

		# If the 'messages' keyword argument was provided, and it
		# is a ChatMessages object, then we need to convert it to
		# a list of message dictionaries before storing it in the
		# chat API configuration object.  This is because the chat 
		# API expects a list of message dictionaries, not a 
		# ChatMessages object.

		if messages != None:
			if isinstance(messages, ChatMessages):
				messages = messages.messageList

		# Now we can store the new values for our special chat-related
		# arguments.

		if messages		!= None:	chatConf.messages		= messages
		if logitBias	!= None:	chatConf.logitBias		= logitBias
		if user			!= None:	chatConf.user			= user

	#__/ End instance method GPT3APIConfig.modify().

	
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	String converter.						   [special instance method]
		#|
		#|		Generates a human-readable string representation of this
		#|		chat API configuration.	This shows all the parameter values.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __str__(thisGPT3ChatConf:GPT3ChatAPIConfig):
	
		"""A human-readable string description of the parameter values."""
		
		chatConf = thisGPT3ChatConf		# For convenience.

		if chatConf.name == None:
			namestr = ""
		else:
			namestr = f" \"{chatConf.name}\""
		
		return f"""
			GPT3 Chat Configuration{namestr}:
				engine_id         = {chatConf.engineId}
				max_tokens        = {chatConf.maxTokens}
				temperature       = {chatConf.temperature}
				top_p             = {chatConf.topP}
				n                 = {chatConf.nCompletions}
				stream            = {chatConf.stream}
				stop              = {repr(chatConf.stop)}
				presence_penalty  = {chatConf.presencePenalty}
				frequency_penalty = {chatConf.frequencyPenalty}
				messages          = {chatConf.messages}
				logitBias         = {chatConf.logitBias}
				user              = {chatConf.user}"""[1:]	# [1:] removes the leading newline.
		# NOTE: .stop is printed using repr() in order to show the 
		# escape codes for any special characters.

	#__/ End string conversion method for class GPT3ChatAPIConfig.

#__/ End class GPT3ChatAPIConfig.


class PromptTooLargeException(Exception):

	"""An exception raised when a prompt is too large to be processed."""

	def __init__(e, promptToks:int, maxToks:int):

		"""Initialize the exception with the number of tokens in the
			prompt and the maximum number of tokens allowed."""

		byHowMuch = promptToks - maxToks	# The prompt is too large by this many tokens.

		# Store the above values in the exception object for later reference.
		e.promptToks 	= promptToks
		e.maxToks 		= maxToks
		e.byHowMuch 	= byHowMuch

		# Generate a human-readable error message.
		msg = (f"GPT-3 API prompt string is {promptToks} tokens," +
			   f" max is {promptToks}, too large by {byHowMuch}.")

		super(PromptTooLargeException, e).__init__(msg)
			# Call the base class constructor with the generated message.

	# Forward declaration of GPT3Core so we can reference its name 
	# in type hints from within the Completion class definition.
class GPT3Core:
	pass
	
#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|	gpt3.api.Completion									[module public class]
#|
#|		This class is a wrapper for the completion data structure 
#|		returned by the underlying GPT-3 API.  The constructor calls
#|		the API to create this structure.  Various properties allow
#|		easy access to information contained in the structure.
#|
#|	Usage:
#|
#|		compl = Completion(prompt, core)			   [polymorphic constructor]
#|
#|			Creates a completion of the given prompt string using 
#|			the given GPT3Core instance.
#|
#|		compl = Completion(complStruct)				   [polymorphic constructor]
#|
#|			Creates a Completion object wrapping the given 
#|			completion structure, previously generated.
#|
#|		text = compl.text					[read-only instance public property]
#|
#|			Returns the text of the completion as a single string.
#|
#|		nTok = compl.nTokens				[read-only instance public property]
#|
#|			Returns the total number of tokens in the completion.
#|			(Note that this property only works if the core had
#|			'logprobs=0' at the time that the completion was 
#|			generated.)
#|
#|		promptLen = compl.promptLen			[read-only instance public property]
#|
#|			Returns the length of the prompt in tokens. Note that 
#|			this property only works if the core had 'echo=True' 
#|			and 'logprobs=0' set at the time that the completion 
#|			was generated.
#|		
#|		complLen = compl.resultLen			[read-only instance public property]
#|
#|			Returns the length of the result (not including the 
#|			prompt) in tokens. Note that this property only works
#|			if 'logprobs=0' and is only useful if 'echo=True'
#|			since otherwise you could just use .nTokens.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Completion: pass
class Completion:

	"""An instance of this class represents a result returned from the
		GPT-3 API's completion creation call."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Public data members.							   [class documentation]
	#|
	#|		.prompt [string]
	#|
	#|			The prompt string from which this completion was
	#|			generated, if available. (Otherwise None.)
	#|
	#|		.core [GPT3Core]
	#|
	#|			The connection to the core API that was used to 
	#|			generate this completion, if available.
	#|
	#|		.complStruct [dict]
	#|
	#|			The raw completion data structure returned by 
	#|			the core API.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| Instance initializer.						[special instance method]
	#|		
	#|		This takes a general argument list, and parses it to extract
	#|		the text of a prompt and the GPT3Core object that is provided.
	#|		Then are then used to call the underlying API to create the
	#|		actual completion data structure.  (Alternatively, if a 
	#|		structure is already provided, we just remember it.)
	#|
	#|	Usage:
	#|
	#|		compl = Completion(prompt, core)
	#|
	#|			Creates a completion of the given prompt string using 
	#|			the given GPT3Core instance.
	#|
	#|		compl = Completion(complStruct)
	#|
	#|			Creates a completion object wrapping the given 
	#|			completion structure, previously generated.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(inst, *args, **kwargs):
		
		"""Instance initializer for class Completion."""
		
			# These are things we are going to try to find in our arguments,
			# or generate ourselves.
		
		prompt			= None		# The prompt string to pass to the API.
		core			= None		# The core engine connection that should be used to generate this completion.
		complStruct		= None		# A raw completion data structure returned by the core API.
		
			# Scan our positional arguments looking for strings, core objects,
			# or pre-existing compleition structures.
		
		for arg in args:
		
				# If there's a string, add it to our growing prompt.
		
			if isinstance(arg,str):
				if prompt == None:
					prompt = arg
				else:
					prompt = prompt + arg

				# If there's a GPT3Core instance, remember it.

			if isinstance(arg,GPT3Core):
				core = arg
		
				# If there's a dict, assume it's a completion object.
		
			if isinstance(arg,dict):
				complStruct = arg
			
		#__/ End for arg in args.

			# Also check any keyword arguments to see if a prompt, core, 
			# and/or struct are there.	If they are, we'll just override
			# any that were already extracted from positional arguments.

		if 'prompt' in kwargs:
			prompt = kwargs['prompt']
			
		if 'core' in kwargs:
			core = kwargs['core']
			
		if 'struct' in kwargs:
			complStruct = kwargs['struct']
		
			# Remember the prompt and the core that we found, for later use.
		
		inst.prompt = prompt
		inst.core = core
		
			# If we have no completion struct yet, we have to create it by 
			# calling the actual API.  Use an internal instance method for 
			# this purpose.
		
		if complStruct == None and core != None:	  
		
				# First generate the argument list for passing to the API.
			apiArgs = core.genArgs(prompt)
			
				# This actually calls the API, with any needed retries.
			complStruct = inst._createComplStruct(apiArgs)

		#__/ End if we will generate the completion structure.
		
		inst.complStruct = complStruct		# Remember the completion structure.
	
	#__/ End of class gpt3.api.Completion's instance initializer.
	

		#|---------------------------------------------------------------
		#| String converter: Just return the value of our .text property.
	
	def __str__(self):
		"""Converts a Completion instance to a human-readable string."""
		return self.text
	

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| completion.text							[public instance property]
		#|
		#|		Returns the text of this completion, as a single string.
		#|
		#|		At present, if there are multiple completitions present
		#|		in the completion structure, this only returns the text
		#|		of the first one.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	@property
	def text(self):
		"""Returns the text of this completion, as a single string."""
		return ''.join(self.complStruct.choices[0].text)


	# Return the value of the 'finish_reason' field of the completion.
	@property
	def finishReason(self):
		"""Returns the finish reason of this completion, which is a string.
			Possible results include:

				'length' - The completion finished because the engine 
							generated max_tokens tokens.

				'stop' - The completion finished because the engine
							generated a stop sequence.
		"""
		return self.complStruct.choices[0].finish_reason


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| .nTokens									[public instance property]
		#|
		#|		Returns the total number of tokens making up this 
		#|		completion.	 For this information to be available, 
		#|		the completion has to have been created using the
		#|		'logprobs=0' parameter setting.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	@property	
	def nTokens(self):	# This is only defined if logprobs attribute is present.
	
		"""Returns the total number of tokens in this completion."""
	
			# Do some error checking. Really we should be doing 
			# something more sophisticated here.
	
		if self.core != None:
			if self.core.conf.logProbs != 0:
				_logger.warn("WARNING: .nTokens only works when logprobs=0!")
				
		return len(self.complStruct.choices[0].logprobs.tokens)

	#__/ End of class gpt3.api.Completion's .nTokens property.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| .promptLen								[public instance property]
		#|
		#|		Returns the length of the prompt string, in tokens.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@property
	def promptLen(self):
	
		"""Returns the length of the prompt in tokens."""
		
		if self.prompt == None:
			_logger.error("ERROR: .promptLen: Prompt not available.")
			return None
			
		if self.core == None:
			_logger.error("ERROR: .promptLen: Core not available.")
			return None
			
		if self.core.conf.echo != True:
			_logger.error("ERROR: .promptLen: Echo not set.")
			return None
			
		if self.core.conf.logProbs != 0:
			_logger.error("WARNING: .promptLen: Logprobs is not 0.")
			
		resultPos = len(self.prompt)
		resultTokIndex = self.textPosToTokIndex(resultPos)
		return resultTokIndex
	
	#__/ End of class gpt3.api.Completion's .promptLen property.


	@property
	def resultLen(self):
		"""Returns the length of the result in tokens."""
		return self.nTokens - self.promptLen
			# Length of result is the total number of tokens in the response
			# (assuming echo was set) minus the length of the prompt.


	def textPosToTokIndex(self, pos:int):
	
		"""Given a position in the completion text, returns the index 
			of the token that is at that position."""
			
		text_offsets = self.complStruct.choices[0].logprobs.text_offset

			# We could make this more efficient by doing a binary
			# search, but it's probably overkill at the moment.
		
		for tok_index in range(0, len(text_offsets)):
			if text_offsets[tok_index] > pos:
				return tok_index-1
				
		return len(text_offsets)-1
			# If we get here, we're at the end of the text.
			# Return the last token index.
	
	#__/ End of class gpt3.api.Completion's .textPosToTokIndex method.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| completion._createComplStruct(apiArgs)	   [private instance method]
		#|
		#|		This internal method is what actually calls the core API
		#|		to retrieve the raw completion data structure.	We use the
		#|		backoff package (pypi.org/project/backoff) to handle retries
		#|		in case of REST failures.
		#|
		#|	Arguments:
		#|
		#|		apiArgs [dict] - API arguments as a single dict structure.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# This decorator performs automatic exponential backoff on certain REST failures.

	@backoff.on_exception(backoff.expo, (openai.APIError), max_tries=6)
	def _createComplStruct(thisCompletion:Completion, apiArgs, minRepWin:int=DEF_TOKENS):
			# By default, don't accept shortening the space for the response to less than 100 tokens.
	
		"""Private instance method to retrieve a completion from the
			core API, with automatic exponential backoff and retry."""
		
		compl = thisCompletion	# Just to make the code below more readable.

		if minRepWin is None:		# Just in case caller explicitly sets this to None,
			minRepWin = DEF_TOKENS	# revert back to the default of 100 tokens.

		# If the core is not set, we can't do anything.
		if compl.core == None:
			_logger.error("ERROR: completion._createComplStruct(): Core not available.")
			return None
			
		# The below code needs to be wrapped in the module's mutex lock, because
		# it manipulates the global record of API usage statistics, and this is
		# not thread-safe unless we make it atomic by grabbing the lock.

		with _lock:

			# If the usage statistics file hasn't been loaded already, do it now.
			loadStatsIfNeeded()

			# This measures the length of the prompt in tokens, and updates
			# the global record of API usage statistics accordingly.
			compl._accountForInput(apiArgs)
				# Note: The global variable _inputLength is updated by this method.

			# Retrieve the engine's receptive field size; this is the maximum number
			# of tokens that can be accommodated in the query + response together.
			fieldSize = _get_field_size(compl.core.conf.engineId)

			# For some reason, the engines that supposedly can only handle
			# 2,048 tokens in their query + response together actually are
			# able to handle 2,049 tokens. So, we'll adjust the value of
			# fieldSize in that case.
			if fieldSize == 2048:
				fieldSize = 2049

			# NOTE: Still need to research whether the engines that supposedly
			# can only handle 4,000 tokens can similarly handle 4,001 tokens.

			# Check to make sure that input+result length is not greater than
			# the size of the receptive field; if so, then we need to request 
			# a smaller result (but not too small).

			if _inputLength + apiArgs['max_tokens'] > fieldSize:

					# See how much space there is right now for our query result.
				availSpace = fieldSize - _inputLength

					# If there isn't enough space left even for our minimum result,
					# then we need to raise an exception, because whoever prepared
					# our prompt made it too large for this engine.

				if availSpace < minRepWin:

						# Calculate the effective maximum prompt length, in tokens.
					effMax = fieldSize - minRepWin

					_logger.debug(f"[GPT-3 API] Prompt length of {_inputLength} exceeds"
								  f" our effective maximum of {effMax}. Requesting field shrink.")

					e = PromptTooLargeException(_inputLength, effMax)
					raise e		# Complain to our caller hierarchy.

					# If we get here, we have enough space for our minimum result length,
					# so we can shrink the maximum result length accordingly.
				origMax = apiArgs['max_tokens']	# Save the original value.
				apiArgs['max_tokens'] = maxTok = fieldSize - _inputLength

				_logger.warn(f"[GPT-3 API] Trimmed max_tokens from {origMax} to {maxToks}.")

			# If we get here, we know we have enough space for our query + result,
			# so we can proceed with the request to the actual underlying API.
			complStruct = openai.Completion.create(**apiArgs)

			# This measures the length of the response in tokens, and updates
			# the global record of API usage statistics accordingly.			
			compl._accountForOutput(apiArgs['model'], complStruct)

			# This updates the cost data and the human-readable table of API
			# usage statistics, and saves the updated data to the _statsFile.
			_saveStats()

		return complStruct		# Return the low-level completion data structure.
			# Note, this is the actual data structure that the completion object 
			# uses to populate itself.
			
	#__/ End of class gpt3.api.Completion's ._createComplStruct method.


	# Make these regular functions? 
	# 	-- No, because they're different for the chat API.
	
	def _accountForInput(self, apiArgs):

		"""This method measures the number of tokens in the prompt, and
			updates the global record of input tokens processed by the API."""
		
			# NOTE: It's dangerous to make _inputLength a global variable,
			# because it's possible that multiple threads will interleave
			# their processing of different queries. To be safe, DO NOT 
			# CALL THIS METHOD unless you have the module's mutex _lock 
			# acquired.

		global _inputLength

		engine = apiArgs['model']	# The engine ID. (Note we're using OpenAI's new name for this parameter.)
		prompt = apiArgs['prompt']

			# This function counts the number of tokens in the prompt
			# without having to do an API call (since calls cost $$).
		nToks = tiktokenCount(prompt, model=engine)

		_inputLength = nToks

		_logger.debug(f"Counted {nToks} tokens in input text [{prompt}]")

		# If stats structures are out of date, expand them as needed.
		if not engine in _inputToks:
			_inputToks[engine] = 0
			_outputToks[engine] = 0
			_expenditures[engine] = 0

			# Update the global record of API usage statistics.
		_inputToks[engine] = _inputToks[engine] + nToks
	
	#__/ End of class gpt3.api.Completion's ._accountForInput method.


	def _accountForOutput(self, engine, complStruct):

		"""This method measures the number of tokens in the response, and
			updates the global record of output tokens processed by the API."""

		# NOTE: We can't just use the .text property of the completion
		# object, because we call this method from the initializer,
		# before the completion object has been fully initialized.

		text = ''.join(complStruct.choices[0].text)
			# This syntax concatenates the list of strings returned by
			# the underlying API together into a single string.

			# This function counts the number of tokens in the response
			# without having to do an API call (since calls cost $$).
		nToks = tiktokenCount(text, model=engine)

		_logger.debug(f"Counted {nToks} tokens in output text [{text}].")

			# Update the global record of API usage statistics.
		_outputToks[engine] = _outputToks[engine] + nToks

	#__/ End of class gpt3.api.Completion's ._accountForOutput method.

#__/ End class Completion.


#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|	gpt3.api.ChatMessages								[module public class]
#|
#|		This class is a simple wrapper for the 'messages' list that gets
#|		passed to the chat API.  Maybe we'll add more functionality to it
#|		later.
#|
#|	Public interface to class ChatMessages:
#|	=======================================
#|
#|
#|		chatMsgs = ChatMessages()							 [class constructor]
#|
#|			Create a new ChatMessages object.  Initially empty.
#|
#|
#|		chatMsgs.messageList			 	[read-only instance public property]
#|
#|			Return the underlying list of individual message dicts.
#|
#|
#|		chatMsgs.totalTokens				[read-only instance public property]
#|
#|			Return the total number of tokens in all messages.
#|
#|
#|		chatMsgs.addMessage(role, content)				[instance public method]
#|
#|			Add a new message with the given role and content to the
#|			end of the message list.  The <role> must be one of the
#|			following global constants (defined earlier):
#|
#|				CHAT_ROLE_SYSTEM	- Represents the system as a whole.
#|
#|				CHAT_ROLE_USER		- Represents messages from a human user.
#|
#|				CHAT_ROLE_AI		- Represents messages from the AI.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def oaiMsgObj_to_msgDict(message: openai.types.chat.ChatCompletionMessage):
	return {
		'content':			message.content,
		'role':				message.role,
		'function_call':	message.function_call
	}

class ChatMessages: pass
class ChatMessages:

	"""An instance of this class represents a list of messages for use
		with the chat API."""
	
	def __init__(self, msgList=None):

		"""Create a new ChatMessages object.  Initially empty unless
			<msgList> is specified, in which case it must be a list of
			message dicts, each of which must have the following fields:
			
				role		- One of the global constants CHAT_ROLE_SYSTEM,
							  CHAT_ROLE_USER, or CHAT_ROLE_AI.
							
				content		- The text of the message.

				name [optional]	- The name of the user or AI.  If 
							  specified, the API will use it in the
							  place of the default name for that role.
				
			Note that the <msgList> is NOT copied, so if you modify it
			after passing it to this constructor, the changes will be
			reflected in the ChatMessages object."""
		
		if msgList is None:
			msgList = []

		# Convert messages from OpenAI's new object representation back
		# to the legacy dict representation that we use in our code.
		newList = []
		for msg in msgList:
			if isinstance(msg, openai.types.chat.ChatCompletionMessage):
				newMsg = oaiMsgObj_to_msgDict(msg)
			else:
				newMsg = msg
			newList.append(newMsg)
		msgList = newList

		# NOTE: It would be a good idea to check the validity of the message 
		# dicts here, so that we can give a more informative and immediate 
		# error message if the caller passes in an invalid list of messages,
		# compared to the error message that the API would return later.  
		# But we'll leave that for a future version.

		self._messages = msgList		# The underlying list of message dicts.

	#__/ End of class gpt3.api.ChatMessages's constructor.


	@property
	def messageList(self):

		"""Return the underlying list of message dicts."""
		
		msgList = self._messages

		#_logger.debug(f"In ChatMessages.messageList(): The current messageList is: {msgList}")

		return msgList
	

	def totalTokens(self, model=None):
		
		"""Return the total number of tokens in all messages. Note that
			we include the tokens in the 'role' and 'content' fields of
			each message dict, as well as an estimate of the tokens in
			whatever behind-the-scenes formatting the API backend uses 
			to represent the messages before passing them to the 
			underlying language model."""
		
		totalToks = 0	# Accumulates the total number of tokens in all messages.

		for msg in self.messageList:

			msgToks = _msg_tokens(msg, model=model)	
				# This function counts the number of tokens in the message.

				# This is too verbose for normal operation. Comment it out after testing.
			#if logmaster.doDebug: _logger.debug(f"Message {msg} has {msgToks} tokens.")

			totalToks += msgToks
			
		# Extra "slop tokens" to reduce API errors.
		if model == 'gpt-4':
			_slopTokens = 5
		else:
			_slopTokens = 1

		totalToks += _slopTokens

		return totalToks

	#__/ End instance method ChatMessages.totalTokens().


	def addMessage(self, role, content, name=None):

		"""Add a new message with the given role and content (and name, if
			provided) to the end of the message list.  The <role> must be 
			one of:
			
				CHAT_ROLE_SYSTEM	- Represents the system as a whole.

				CHAT_ROLE_USER		- Represents messages from a human user.

				CHAT_ROLE_AI		- Represents messages from the AI."""

		# We commented out this error check temporarily earlier to 
		# confirm that the chat API can't handle arbitrary names in 
		# place of the predefined roles.

		if role not in [self.CHAT_ROLE_SYSTEM, self.CHAT_ROLE_USER, self.CHAT_ROLE_AI]:
			raise ValueError(f"Invalid role '{role}' for chat message.")

		# Construct the message dict.
		msgDict = {'role': role, 'content': content}
		if name is not None:
			msgDict['name'] = name

		# Add it to the list.
		self._messages.append(msgDict)

	#__/ End instance method ChatMessages.addMessage().


#__/ End class ChatMessages.


#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|	gpt3.api.ChatCompletion								[module public class]
#|
#|		This class is a wrapper for the completion data structure 
#|		returned by the underlying GPT chat API.  The constructor 
#|		calls the API to create this structure.  Various properties 
#|		allow easy access to information contained in the structure.
#|
#|
#|	Public interface to class ChatCompletion:
#|	=========================================
#|
#|
#|		chatCompl = ChatCompletion(chatCore)		   [polymorphic constructor]
#|
#|			Creates a chat completion object based on the current
#|			messages for the given GPT3ChatCore connection.
#|
#|
#|		chatCompl = ChatCompletion(chatComplStruct)	   [polymorphic constructor]
#|
#|			Creates a ChatCompletion object wrapping the given 
#|			completion structure, previously generated.
#|
#|
#|		msg = chatCompl.message					   [read-only instance property]
#|
#|			Returns the message that was generated by the chat API.
#|			This is usable as a dict with the following keys:
#|
#|				role		- The role of the message (one of the
#|						  		CHAT_ROLE_* constants defined above).
#|
#|				content		- The text of the message.
#|
#|
#|		text = chatCompl.text				   	   [read-only instance property]
#|
#|			Returns just the text of the completion as a single
#|			string.
#|
#|
#|		nToks = chatCompl.nTokens			   	   [read-only instance property]
#|
#|			Returns the total number of tokens in the completion,
#|			including the prompt.
#|
#|
#|		promptLen = chatCompl.promptLen		   	   [read-only instance property]
#|
#|			Returns the length of the prompt in tokens.
#|		
#|
#|		complLen = chatCompl.resultLen	   	   	   [read-only instance property]
#|
#|			Returns the length of the result message content text
#|			(i.e., not including the prompt) in tokens.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class ChatCompletion: pass
class ChatCompletion(Completion):
	# NOTE: We are subclassing this class from Completion mainly just so that
	# we can inherit miscellaneous methods that are unchanged.  However, we need
	# to be careful to override any methods that really do need to be overridden.
	#
	# The following is a list of methods we are inheriting from Completion and
	# that we are intentionally NOT overriding here, and why not:
	#
	#		.__str__()		- This just retrieves our .text property.
	#
	#		.finishReason 	- This part of the completion structure is not
	#						  any different for chat completions.
	#
	# And the following methods from Completion are simply not relevant for chat
	# completions, so we don't need to override them:
	#
	#

	"""An instance of this class represents a completion object returned
		by the GPT chat API.  It wraps the underlying completion structure
		provided by the API."""
	
	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Public data members.							   [class documentation]
	#|
	#|		.prompt [string]
	#|
	#|			The prompt string from which this completion was
	#|			generated, if available. (Otherwise None.)
	#|
	#|		.core [GPT3Core]
	#|
	#|			The connection to the core API that was used to 
	#|			generate this completion, if available.
	#|
	#|		.complStruct [dict]
	#|
	#|			The raw completion data structure returned by 
	#|			the core API.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| Instance initializer.						[special instance method]
	#|		
	#|		This takes a general argument list, and parses it to extract
	#|		the text of a prompt and the GPT3ChatCore object that is 
	#|		provided.  Then are then used to call the underlying chat API 
	#|		to create the actual completion data structure.  (Alternatively, 
	#|		if a structure is already provided, we just remember it.)
	#|
	#|	Usage:
	#|
	#|		compl = ChatCompletion(core)
	#|
	#|			Creates a completion of the given prompt string using 
	#|			the given GPT3ChatCore instance.
	#|
	#|		compl = ChatCompletion(chatComplStruct)
	#|
	#|			Creates a completion object wrapping the given 
	#|			chat completion structure, previously generated.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(newChatCompletion:ChatCompletion, *args, **kwargs):
		
		"""Instance initializer for class ChatCompletion."""
		
		#if 'messages' in kwargs:
		#	_logger.info(f"In ChatCompletion.__init__() with messages=[list of {len(kwargs['messages'])} messages]")

		chatCompl = newChatCompletion	# For convenience.

			# These are things we are going to try to find in our arguments,
			# or generate ourselves.
		
		chatCore		= None		# The core chat engine connection that should be used to generate this completion.
		chatComplStruct	= None		# A raw chat completion data structure returned by the chat core API.
		otherArgs		= []		# Any other arguments that we don't recognize.

			# Scan our positional arguments looking for strings, chat-core objects,
			# or pre-existing chat completion structures.
		
		for arg in args:
		
				# If there's a GPT3ChatCore instance, remember it.

			if isinstance(arg, GPT3ChatCore):
				chatCore = arg
		
				# If there's a dict, assume it's a completion object.
		
			elif isinstance(arg, dict):
				chatComplStruct = arg

				# Remember any other arguments that we don't recognize.

			else:
				otherArgs.append(arg)
			
		#__/ End for arg in args.

			# Also check any keyword arguments to see if a <core>, 
			# and/or <struct> are there.	If they are, we'll just override
			# any that were already extracted from positional arguments.

		if 'core' in kwargs:
			chatCore = kwargs['core']
			del kwargs['core']			# genChatArgs() doesn't need this.
			
		if 'struct' in kwargs:
			chatComplStruct = kwargs['struct']
			del kwargs['struct']		# genChatArgs() doesn't need this.

			# If a <minRepWin> (minimum reply window size) argument is present,
			# we'll pass it through as a kwarg to ._createChatComplStruct().

		if 'minRepWin' in kwargs:
			minRepWin =	kwargs['minRepWin']
			del kwargs['minRepWin']		# genChatArgs() doesn't need this.
		else:
			minRepWin = None

			# Remember the core that we found, for later use.
		
		chatCompl.chatCore = chatCore
		
			# If we have no completion struct yet, we have to create it by 
			# calling the actual API.  Use an internal instance method for 
			# this purpose.
		
		if chatComplStruct == None and chatCore != None:	  
		
				# First generate the argument list for passing to the API.
			apiArgs = chatCore.genChatArgs(*otherArgs, **kwargs)
			
			#prettyArgs = pformat(apiArgs)
			#_logger.debug("In ChatCompletion.__init__() with apiArgs:\n" + prettyArgs)

				# This actually calls the API, with any needed retries.
			chatComplStruct = chatCompl._createChatComplStruct(apiArgs, 
				minRepWin=minRepWin) # Pass this thru to set min reply window.
		
		#__/ End if we will generate the completion structure.
		
		chatCompl.chatComplStruct = chatComplStruct		# Remember the completion structure.
	
		chatCompl._gotMsg = False	# For a stream, haven't yet gathered the whole message.
		chatCompl._msg = None

	#__/ End of class gpt3.api.ChatCompletion's instance initializer.


	def _msgFromGen(thisChatCompletion:ChatCompletion):

		tcc = thisChatCompletion
		if not tcc._gotMsg:
			
			role = None
			response = ""
			
			for chunk in tcc.complStruct:
				delta = chunk.choices[0].delta
				if 'role' in delta:
					role = delta.role
					_logger.debug("Got role: {role}")
				if 'content' in delta:
					chunkText = delta.content
					_logger.debug("Got text chunk: {chunkText}")
					response += chunkText

			msg = {
				'role': role,
				'content': response
			}

			tcc._gotMsg = True
			tcc._msg = msg
		
		return tcc._msg


	@property
	def firstChoice(thisChatCompletion:ChatCompletion):
		"""Returns the first choice dict of this chat completion."""
		return thisChatCompletion.chatComplStruct.choices[0]

	@property
	def message(thisChatCompletion:ChatCompletion):

		"""Returns the result message dict of this chat completion."""

		return thisChatCompletion.firstChoice.message

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| chatCompletion.text						  [public instance property]
		#|
		#|		Returns the text of this chat completion, as a single 
		#|		string.
		#|
		#|		At present, if there are multiple completions present
		#|		in the completion structure, this only returns the text
		#|		of the first one.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	@property
	def text(thisChatCompletion:ChatCompletion):
		
		"""Returns the text of this chat completion, as a single string."""

		# Note the following code differs from the code in the Completion class.
		return thisChatCompletion.message.content

	@text.setter
	def text(thisChatCompletion:ChatCompletion, newText:str):
		"""Sets the value of the chat completion text content."""
		thisChatCompletion.message.content = newText

	@property
	def finishReason(thisChatCompletion:ChatCompletion):
		"""Returns the value of the finish_reason field of the result."""
		return thisChatCompletion.firstChoice.finish_reason

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| chatCompletion.nTokens					  [public instance property]
		#|
		#|		Returns the total number of tokens making up this 
		#|		completion.	 The chat API makes this very easy.
		#|		NOTE: This includes BOTH the prompt and the result.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	@property	
	def nTokens(thisChatCompletion:ChatCompletion):
	
		"""Returns the total number of tokens in this completion.
			Note this includes BOTH the prompt and the result."""
	
		return thisChatCompletion.chatComplStruct\
				.usage.total_tokens

	#__/ End of class gpt3.api.ChatCompletion's .nTokens property.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| chatCompletion.promptLen					  [public instance property]
		#|
		#|		Returns the length of the completion's prompt string, in 
		#|		tokens.  The chat API makes this very easy.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@property
	def promptLen(thisChatCompletion:ChatCompletion):
	
		"""Returns the length of the prompt in tokens."""
		
		return thisChatCompletion.chatComplStruct\
				.usage.prompt_tokens
	
	#__/ End of class gpt3.api.ChatCompletion's .promptLen property.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| chatCompletion.resultLen					  [public instance property]
		#|
		#|		Returns the length of the completion's result string, in 
		#|		tokens.  The chat API makes this very easy.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@property
	def resultLen(thisChatCompletion:ChatCompletion):
	
		"""Returns the length of the result in tokens."""
		
		return thisChatCompletion.chatComplStruct \
				['usage']['completion_tokens']
	
	#__/ End of class gpt3.api.ChatCompletion's .promptLen property.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| chatCompletion.textPosToTokIndex()			[public instance method]
		#|
		#|		Given a position in the completion text, returns the index
		#|		of the token that is at that position.
		#|
		#|		We need to override the version of this method that is 
		#|		defined in the Completion class, because in the chat API
		#|		the 'logprobs' field is not present, so instead we have to
		#|		use the tiktoken library to do the conversion.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def textPosToTokIndex(thisChatCompletion:ChatCompletion, pos:int):
	
		"""Given a position in the completion text, returns the index 
			of the token that is at that position."""
		
		chatCompl = thisChatCompletion	# For convenience.

			# First, let's retrieve our engine name.
		engineName = chatCompl.chatCore.chatConf.engineId
			# (Should we make this easier to access?)

			# Now let's get the name of the encoding used by this engine.
		#encodingName = _get_encoding(engineName)

			# Now we can ask the tiktoken library to give us the corresponding
			# encoding object.
		#encoding = tiktoken.get_encoding(encodingName)	# obsolete
		encoding = tiktoken.encoding_for_model(engineName)

			# Now we can use the encoding object to convert the text to a list
			# of tokens.
		tokens = encoding.encode(chatCompl.text)

			# Next, we'll construct a list of the offsets of each token.
		text_offsets = [0]
		for tok in tokens:
				# First, decode the token to a string, so we can measure its length
				# in characters.
			tok = encoding.decode([tok])[0]

				# Now append the offset of the next token to the list of offsets.
			text_offsets.append(text_offsets[-1] + len(tok))

		#text_offsets = self.complStruct['choices'][0]['logprobs']['text_offset']
		# ^^^ This is what we would have done instead if the 'logprobs' field were present.

			# We could make this more efficient by doing a binary
			# search, but it's probably overkill at the moment.
		
		for tok_index in range(0, len(text_offsets)):
			if text_offsets[tok_index] > pos:
				return tok_index-1
				
		return len(text_offsets)-1
			# If we get here, we're at the end of the text.
			# Return the last token index.
	
	#__/ End of class gpt3.api.ChatCompletion's .textPosToTokIndex method.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| chatCompletion._createChatComplStruct(apiArgs)	[private instance method]
		#|
		#|		This internal method is what actually calls the core chat API
		#|		to retrieve the raw completion data structure.	We use the
		#|		backoff package (pypi.org/project/backoff) to handle retries
		#|		in case of REST failures.
		#|
		#|	Arguments:
		#|
		#|		apiArgs [dict] - API arguments as a single dict structure.
		#|
		#|		minRepWin [int] (OPTIONAL) - Requested space, in tokens, 
		#|			for the completion result.  Note that if the prompt 
		#|			takes up too much of the context window, the actual 
		#|			available result space is less than this value, and
		#|			currently this is handled by raising a PromptTooLarge-
		#|			Exception.  If no value is provided, the default of
		#|			100 tokens will be used.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# This decorator performs automatic exponential backoff on REST failures.

	#@backoff.on_exception(backoff.expo,
	#					  (openai.error.APIError))
						  
	def _createChatComplStruct(thisChatCompletion:ChatCompletion, apiArgs:dict, 
				minRepWin:int=DEF_TOKENS):
			# By default, we'll throw an exception if the estimated result space
			# is less than 100 tokens.  This can be overridden by the caller
			# by explicitly setting the minRepWin argument to a different value.

		"""Private instance method to retrieve a chat completion from the core
			chat API, with automatic exponential backoff and retry."""
		
		if 'messages' in apiArgs:
			_logger.debug(f"In _createChatComplStruct(), apiArgs['messages']="
						  f"[list of {len(apiArgs['messages'])} messages]")

		chatCompl = thisChatCompletion	# For convenience.

		if minRepWin is None:		# Just in case caller explicitly sets this to None,
			minRepWin = DEF_TOKENS	# revert back to the default of 100 tokens.

		#_logger.debug(f"In ._createChatComplStruct(), minRepWin={minRepWin}.")

		# If the core is not set, we can't do anything.
		if chatCompl.chatCore == None:
			_logger.error("ERROR: chatCompletion._createChatComplStruct(): Chat core not available.")
			return None
			
		# Get the model name of our chat engine. We'll use this later.
		engineId = apiArgs['model']

			# Estimate the length in tokens of the input prompt -
			# but don't actually update our usage statistics yet!

		estInputLen = chatCompl._estimateInputLen(apiArgs)

		#_logger.debug(f"In ._createChatComplStruct(), estInputLen={estInputLen}.")

			# Retrieve the engine's receptive field size; this is the maximum number
			# of tokens that can be accommodated in the query + response together.

		fieldSize = _get_field_size(engineId)

			# For some reason, the engines that supposedly can only handle
			# 2,048 tokens in their query + response together actually are
			# able to handle 2,049 tokens. So, we'll adjust the value of
			# fieldSize in that case. Likewise for field sizes 4096 & 16384.

		if fieldSize == 2048 or fieldSize == 4096 or fieldSize == 16384:
			fieldSize += 1

			# (NOTE: Still need to research whether the engines that supposedly
			# can only handle 4,000 tokens can similarly handle 4,001 tokens,
			# if whether the engines that supposedly can only handle 4,096
			# tokens can similarly handle 4,097 tokens, etc.)

			# UPDATE: ChatGPT-3.5 can indeed handle 4,097, it seems.

		#_logger.debug(f"In ._createChatComplStruct(), fieldSize={fieldSize}.")


		# Get a numeric equivalent for 'max_tokens'.
		if 'max_tokens' not in apiArgs or apiArgs['max_tokens'] is None:
			maxToks = float('inf')
		else:
			maxToks = apiArgs['max_tokens']

		#_logger.debug(f"In ._createChatComplStruct(), maxToks={maxToks}.")


			# Check to make sure that input+result window is not greater than
			# the size of the receptive field; if so, then we need to request 
			# a smaller result (but not too small). Exception: If maxToks is
			# infinity (no limit), just keep it like that.

		if maxToks < float('inf') and estInputLen + maxToks > fieldSize:

				# See how much space there is right now for our query result.
			availSpace = fieldSize - estInputLen

			#_logger.debug(f"In ._createChatComplStruct(), availSpace={availSpace}.")

				# If there isn't enough space left even for our minimum requested
				# reply window size, then we need to raise an exception, because 
				# whoever prepared our message list made it too large to provide
				# sufficient space for the AI's response..

			if availSpace < minRepWin:

					# Calculate the effective maximum prompt length, in tokens.
				effMax = fieldSize - minRepWin

				#_logger.debug(f"In ._createChatComplStruct(), effMax={effMax}.")

				_logger.debug("[GPT chat API] Prompt length of "
							  f"{estInputLen} exceeds our effective "
							  f"maximum of {effMax}. Requesting "
							  "message list shrink.")

				e = PromptTooLargeException(_inputLength, effMax)
				raise e		# Complain to our caller hierarchy.

			#__/ End if too little space left.

				# If we get here, we have enough space for our minimum result length,
				# so we can shrink the maximum result length accordingly.

			origMax = maxToks	# Save the original value.
			apiArgs['max_tokens'] = maxToks = fieldSize - estInputLen

			#_logger.debug(f"In ._createChatComplStruct(), maxToks={maxToks}.")

			_logger.warn(f"[GPT chat API] Trimmed max_tokens window from {origMax} to {maxToks}.")

		#__/ End if result window too big.

		# Temporary hack to try to max out the output length.
		#apiArgs['max_tokens'] = None

		# This code *should* allow the output to fill up to the entire remaining context window? Will it work?
		if 'max_tokens' in apiArgs:

			if apiArgs['max_tokens'] is None:
				apiArgs['max_tokens'] = float('inf')

			_logger.debug(f"[GPT chat API] Requesting up to {apiArgs['max_tokens']} tokens.")

			if apiArgs['max_tokens'] == float('inf'):
				del apiArgs['max_tokens']	# Equivalent to float('inf')?

		prettyArgs = pformat(apiArgs)
		_logger.debug("Calling openai.ChatCompleton.create() with these keyword args:\n" + prettyArgs)

			# If we get here, we know we have enough space for our query + result,
			# so we can proceed with the request to the actual underlying API.

		#try:

		# New style chat completion call:
		chatComplObj = _client.chat.completions.create(**apiArgs)

		# Old style:
		#chatComplStruct = openai.ChatCompletion.create(**apiArgs)

		# This exception type seems to have disappeared in 1.x
		# except openai.InvalidRequestError as e:
		# 	errStr = str(e)		# Get the error as a string.

		# 	_logger.error(f"Got an OpenAI InvalidRequestError: [{errStr}].")

		# 	# Example error string format:
		# 	#	"This model's maximum context length is 8192 tokens.
		# 	#	 However, you requested 8194 tokens (7244 in the
		# 	#	 messages, 950 in the completion). Please reduce the
		# 	#	 length of the messages or completion."

		# 	# Extract the substrings that are numbers.
		# 	numStrs = re.findall(r'\d+', errStr)

		# 	# Convert them to actual numbers.
		# 	numbers = [int(n) for n in numStrs]

		# 	_logger.error(f"Extracted the following numbers: {numbers}")

		# 	if len(numbers) == 4:
		# 		maxConLen, reqToks, msgsLen, compLen = numbers
			
		# 		maxPrompt = maxConLen - reqToks

		# 		e = PromptTooLargeException(msgsLen, maxPrompt)

		# 		raise e

		# 	elif len(numbers) == 5:
		# 		maxConLen, reqToks, msgsLen, funcsLen, compLen = numbers
			
		# 		_logger.error(f"maxConLen={maxConLen}, reqToks={reqToks}, msgsLen={msgsLen}, funcsLen={funcsLen}, compLen={compLen}")
		# 		_logger.error(f"NOTE: msgsLen+funcsLen = {msgsLen+funcsLen}, but we estimated {estInputLen}.")

		# 		maxPrompt = maxConLen - reqToks

		# 		e = PromptTooLargeException(msgsLen, maxPrompt)

		# 		raise e

		# 	else:	# Maybe this isn't a length issue at all?
		# 		_logger.error("I don't know what to do with that.")
		# 		raise e

		# If we get here, there was a successful return from the API call.
		_logger.debug("ChatCompletion._createChatComplStruct(): Got raw chat completion struct:"
					  + '\n' + pformat(chatComplObj))

		#----------------------------------------------------------
		# If we get here, then the API call succeeded, and we need
		# to account for its costs that we'll be charged for.
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			# The below code needs to be wrapped in the module's mutex
			# lock, because it manipulates the global record of API usage
			# statistics, and this is not thread-safe unless we make it
			# atomic by grabbing the lock.

		with _lock:

				# If the usage statistics file hasn't been loaded already,
				# do it now, because we'll need to update the stats soon.

			loadStatsIfNeeded()

				# This accounts for the length of the prompt in tokens, and
				# updates the global record of API usage statistics accordingly.

			chatCompl._accountForChatInput(engineId, chatComplObj)

				# This accounts for the length of the response in tokens, and 
				# updates the global record of API usage statistics accordingly.

			chatCompl._accountForChatOutput(engineId, chatComplObj)

				# This updates the cost data and the human-readable table of API
				# usage statistics, and saves the updated data to the _statsFile.

			_saveStats()

		return chatComplObj		# Return the low-level completion data structure.
			# Note, this is the actual data structure that the completion object 
			# uses to populate itself.
			
	#__/ End of class gpt3.api.ChatCompletion's ._createChatComplStruct method.


	def _estimateInputLen(thisChatCompl:ChatCompletion, apiArgs):

		"""This method estimates the number of tokens in the input messages,
			and returns the estimate. This may be done prior to calling the
			API, since it does not use the completion result."""

		if 'messages' in apiArgs:
			_logger.debug(f"In _estimateInputLen(), apiArgs['messages']="
						  f"[list of {len(apiArgs['messages'])} messages]")
		else:
			_logger.error("Missing 'messages' API argument in _estimateInputLen()!")

		chatCompl = thisChatCompl	# For convenience.
		
		engine = apiArgs['model']	# Get the engine ID. 
			# (Note we're using OpenAI's new name for this parameter, 'model'.)

			# Get the raw message list.
		messages = ChatMessages(apiArgs['messages'])

		if _has_functions(engine) and 'functions' in apiArgs:
			funcToks = tiktokenCount(json.dumps(apiArgs['functions']), model=engine)
		else:
			funcToks = 0

			# This function counts the number of tokens in the prompt
			# without having to do an API call (since calls cost $$).
		inToks = messages.totalTokens(model=engine) + funcToks

		_logger.debug(f"Counted {inToks} tokens in input text [{messages}]")

		return inToks


	def _accountForChatInput(thisChatCompl:ChatCompletion, engine:str, chatComplObj:openai.ChatCompletion):

		"""This method measures the number of tokens in the input messages, and
			updates the global record of input tokens processed by the API.

			NOTE: ONLY RUN THIS AFTER THE API CALL HAS SUCCEEDED."""
		
			# NOTE: It's dangerous to make _inputLength a global variable,
			# because it's possible that multiple threads will interleave
			# their processing of different queries. To be safe, DO NOT 
			# CALL THIS METHOD unless you have the module's mutex _lock 
			# acquired.

		global _inputLength

		chatCompl = thisChatCompl		# For convenience.
		usage = chatComplObj.usage		# Sub-dict of usage data.

			# This gets the "official" count of tokens in the prompt
			# (what we'll be charged for).

		inToks = usage.prompt_tokens

		_logger.debug(f"Accounting for {inToks} tokens in input text.")

		# If stats structures are out of date, expand them as needed.
		if not engine in _inputToks:
			_inputToks[engine] = 0
			_outputToks[engine] = 0
			_expenditures[engine] = 0

			# Update the global record of API usage statistics.
		_inputLength = inToks	# Do we even need this any more?
		_inputToks[engine] += inToks
	
	#__/ End of class gpt3.api.Completion's ._accountForInput method.


	def _accountForChatOutput(thisChatCompl:ChatCompletion, engine:str, chatComplObj:openai.ChatCompletion):

		"""This method measures the number of tokens in the chat response, and
			updates the global record of output tokens processed by the API."""

		chatCompl = thisChatCompl		# For convenience.
		usage = chatComplObj.usage		# Sub-dict of usage data.

			# This gets the "official" count of tokens in the result
			# (what we'll be charged for).

		outToks = usage.completion_tokens

			# Extract the message from the raw chat compl struct (for debugging).

		result_msg = chatComplObj.choices[0].message.content
		_logger.debug(f"Accounting for {outToks} tokens in output message [{result_msg}].")

			# Update the global record of API usage statistics.
		_outputToks[engine] += outToks

	#__/ End of class gpt3.api.Completion's ._accountForOutput method.


#__/ End class ChatCompletion.


#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|	
#|	gpt3.api.GPT3Core								  [module public class]
#|
#|		This class abstracts a connection to the core GPT-3 system.	 
#|		An instance of this class remembers its API configuration 
#|		options.
#|
#|	Public interface:
#|
#|		.conf : GPT3APIConfig							[instance property]
#|
#|			Current API configuration of this core connection.
#|
#|		.modelFamily : str								[instance property]
#|
#|			The model family of this core connection's engine.
#|
#|		.isChat	: bool								[instance property]
#|
#|			True if this core connection is a chat connection.
#|
#|		.fieldSize : int							[instance property]
#|
#|			Maximum span in tokens of the receptive field a.k.a.
#|			context window that can be processed by this core
#|			connection. (This is a property of the back-end LLM
#|			engine being used, not of the connection per se.)
#|
#|		.adjustConf(params)	-> None					[instance method]
#|
#|			Modify one or more API parameters of the connection.
#|
#|		.genCompletion(prompt) -> Completion		[instance method]
#|
#|			Generate a completion object from the given prompt.
#|
#|		.genString(prompt) -> str					[instance method]
#|
#|			Generate a single out string from the given prompt.
#|		
#|	Special methods:
#|
#|		.__init__(*args, **kwargs)	- Instance initializer.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3Core:

	"""An instance of this class represents a connection to the core GPT-3 
		API that remembers its parameter settings."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Instance private data members for class GPT3Core.
	#|
	#|		._configuration	[GPT3APIConfig]		- Current API configuration.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Initializer for class GPT3Core.
		#|
		#|	USAGE:
		#|
		#|		core = GPT3Core()			# Uses default parameter values.
		#|		core = GPT3Core(config)		# Use this GPT3APIConfig object.
		#|		core = GPT3Core(params)		# List of keyword arguments.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(inst, *args, **kwargs) -> None:

			# If keyword arg 'config=' is present, use that as the config.
		
		if 'config' in kwargs:
			config = kwargs['config']
			del kwargs['config']	# Remove from keyword args since absorbed.
		else:
			config = None

			# Otherwise, if the first argument is a GPT3APIConfig, use that as the config.
	
		if config == None and len(args) > 0:
			if args[0] != None and isinstance(args[0],GPT3APIConfig):
				config = args[0]
				args = args[1:]		# Remove from arglist since absorbed.

			# If no config was provided, then create one from the arguments.
			# (In future, this should be changed to otherwise modify the provided
			# config based on the remaining arguments.)

		if config == None:
			config = GPT3APIConfig(*args, **kwargs)

		_logger.info("Creating new GPT3Core connection with configuration:\n" + str(config))

		inst._configuration = config		# Remember our configuration.

	#__/ End GPT3Core instance initializer.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.conf									[instance public property]
		#|
		#|		Returns the API configuration object (instance of class
		#|		GPT3APIConfig) that is associated with this connection to
		#|		the core GPT-3 system.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@property
	def conf(self) -> GPT3APIConfig:
		"""Get our current API configuration."""
		return self._configuration


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.modelFamily							[instance public property]
		#|
		#|		Returns the model family of this core connection's engine.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	@property
	def modelFamily(self) -> str:
		"""Returns the model family of this core connection's engine."""
		return _get_model_family(self.conf.engineId)


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.isChat									[instance public property]
		#|
		#|		Returns True if this connection is a chat connection.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@property
	def isChat(self) -> bool:
		"""Returns True if this connection is a chat connection."""
		return isinstance(self, GPT3ChatCore)


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.fieldSize								[instance public property]
		#|
		#|		Returns the maximum span in tokens of the receptive field
		#|		a.k.a. context window that can be processed by this core
		#|		connection. (This is a property of the back-end LLM engine
		#|		being used, not of the connection per se.)
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	@property
	def fieldSize(self) -> int:
		"""Returns the maximum span in tokens of the receptive field."""
		return _get_field_size(self.conf.engineId)


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.adjustConf(params)						[instance public method]
		#|
		#|		Adjusts the API parameter values of this connection to 
		#|		the core GPT-3 system as specified by the argument list.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def adjustConf(self, *args, **kwargs) -> None:
		"""Adjust the API configuration as specified."""
		self.conf.modify(*args, **kwargs)


		# Generate the argument list for calling the core API.
	def genArgs(self, prompt=None) -> dict:
   
		kwargs = {} 	# Initially empty dict for building up argument list.
		
		conf = self.conf	# Get our current configuration.

		kwargs['model'] = conf.engineId		# This API arg. is required. Can't skip it.
			# NOTE: OpenAI used to call this parameter 'engine' but now calls it 'model'.
			# The old name still works, but is deprecated; we use the new name here in
			# case they ever remove the old name.
				
		# Note here we have to match the exact keyword argument names supported by OpenAI's API.

		if prompt					!= None:	kwargs['prompt']			= prompt
		if conf.suffix				!= None:	kwargs['suffix']			= conf.suffix
		if conf.maxTokens			!= None:	kwargs['max_tokens']		= conf.maxTokens
		if conf.temperature			!= None:	kwargs['temperature']		= conf.temperature
		if conf.topP				!= None:	kwargs['top_p']				= conf.topP
		if conf.nCompletions		!= None:	kwargs['n']					= conf.nCompletions
		if conf.stream				!= None:	kwargs['stream']			= conf.stream
		if conf.logProbs			!= None:	kwargs['logprobs']			= conf.logProbs
		if conf.echo				!= None:	kwargs['echo']				= conf.echo
		if conf.stop				!= None:	kwargs['stop']				= conf.stop
		if conf.presencePenalty		!= None:	kwargs['presence_penalty']	= conf.presencePenalty
		if conf.frequencyPenalty	!= None:	kwargs['frequency_penalty'] = conf.frequencyPenalty
		if conf.bestOf				!= None:	kwargs['best_of']			= conf.bestOf
		
		if conf.temperature != None and conf.topP != None:
			# Do some better error handling here. Warning and/or exception.
			_logger.warn(f"WARNING: temp={conf.temperature}, topP={conf.topP}: Setting both temperature and top_p is not recommended.")

		return kwargs

	#__/ End GPT3Core.genArgs() instance method.


		#|----------------------------------------------------------------------
		#|	.genCompletion(prompt:string)			[instance public method]
		#|
		#|		This method returns the raw completion of the given prompt,
		#|		using the core's present API configuration.	 We do graceful
		#|		backoff and retry in case of REST call failures.
		#|
		#|		To do: Provide the option to do a temporary modification of
		#|		one or more API parameters in the argument list.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def genCompletion(self, prompt=None):
	
		"""With automatic exponential backoff, query the server
			for a completion object for the given prompt using the
			connection's current API configuration."""
		
		return Completion(self, prompt)
			# Calls the Completion constructor with the supplied prompt. This
			# constructor does all the real work of calling the API.
		
	#__/ End instance method GPT3Core.genCompletion().


		#|----------------------------------------------------------------------
		#|	.genString(prompt:string)				[instance public method]
		#|
		#|		This method returns a completion of the given prompt
		#|		as a single string.	 Uses .genCompletion() internally.
		#|
		#|		To do: Provide the option to do a temporary modification of
		#|		one or more API parameters in the argument list.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def genString(self, prompt) -> str:
		"""Generate a single completion string for the given prompt."""
		resultCompletion = self.genCompletion(prompt)
		text = resultCompletion.text
		_logger.debug("[GPT-3/API] Server returned result string: [" + text + ']')
		return text
	#__/ End instance method GPT3Core.genString().

#__/ End class GPT3Core.


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	
	#|	gpt3.api.GPT3ChatCore							  [module public class]
	#|
	#|		This class abstracts a connection to the core GPT-3 system, in
	#|		the case of chat-based engines.	 An instance of this class 
	#|		remembers its API configuration options, and the current list
	#|		of messages.  We provide methods to manage the message list.
	#|
	#|	Public interface:
	#|	=================
	#|
	#|		Includes the public interface of GPT3Core, plus:
	#|
	#|		.chatConf										[instance property]
	#|
	#|			Current API configuration of this chat core connection.
	#|
	#|
	#|		.adjustConf(params)								[instance method]
	#|
	#|			Modify one or more API parameters of the connection.
	#|
	#|
	#|		.messages										[instance property]
	#|
	#|			The current list of messages being maintained for this
	#|			connection.
	#|
	#|
	#|		.addMessage(role, content)						[instance method]
	#|
	#|			Add a new message with role ID <role> and message
	#|			content <content> to the end of the current list of
	#|			messages.
	#|
	#|
	#|		.genChatCompletion()							[instance method]
	#|
	#|			Generate a chat completion object from the current messages.
	#|
	#|
	#|		.genMessage()									[instance method]	
	#|
	#|			Generate a new message dict from the current messages.
	#|			Uses .genChatCompletion() internally.
	#|
	#|
	#|		.genString()									[instance method]
	#|
	#|			Generate a single out string from the current messages.
	#|			Uses .genMessage() internally.
	#|
	#|		
	#|	Special methods:
	#|	----------------
	#|
	#|		.__init__(*args, **kwargs)	- Instance initializer.
	#|
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3ChatCore: pass
class GPT3ChatCore(GPT3Core):

	"""An instance of this class represents a connection to the core GPT-3 
		chat API that remembers its parameter settings."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Instance private data members for class GPT3ChatCore:
	#|
	#|		._chatConfiguration	[GPT3APIChatConfig]	- Current API configuration.
	#|
	#|		._messages			[ChatMessages]		- Current list of messages.	
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Initializer for class GPT3ChatCore.
		#|
		#|	USAGE:
		#|
		#|		core = GPT3ChatCore()							
		#|
		#|			Creates and returns a new instance of class GPT3ChatCore 
		#|			using the default parameter values.
		#|
		#|		core = GPT3ChatCore([config=]chatConfig)
		#|
		#|			Creates and returns a new GPT3ChatCore instance using the
		#|			given GPT3ChatAPIConfig object.
		#|
		#|		core = GPT3ChatCore(*args, **kwarms)			
		#|
		#|			Creates and returns a new GPT3ChatCore instance, passing
		#|			the given arguments through to the GPT3ChatAPIConfig()
		#|			constructor. Note this is the same as:
		#|
		#|				core = GPT3ChatCore(GPT3ChatAPIConfig(*args, **kwargs))
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(newGPT3ChatCore:GPT3ChatCore, *args, **kwargs):

		chatCore = newGPT3ChatCore	# For convenience.

			# If keyword arg 'chatConf=' is present, use that as the chatConf.
		
		if 'chatConf' in kwargs:
			chatConf = kwargs['chatConf']
			del kwargs['chatConf']	# Removed it since we absorbed it.
		else:
			chatConf = None

			# Otherwise, if the first argument is a GPT3ChatAPIConfig, use that as the config.
	
		if chatConf == None and len(args) > 0:
			if args[0] != None and isinstance(args[0],GPT3ChatAPIConfig):
				chatConf = args[0]
				args = args[1:]		# Remove it from the args, since we absorbed it.

			# If no chatConf was provided, then create one from the arguments.
			# (In future, this should be changed to otherwise modify the provided
			# chatConf based on the remaining arguments.)

		if chatConf == None:
			chatConf = GPT3ChatAPIConfig(*args, **kwargs)

		_logger.info("Creating new GPT3ChatCore connection with configuration:\n" + str(chatConf))

		chatCore._chatConfiguration = chatConf		# Remember our chat configuration.
		chatCore._configuration = chatConf			# Also remember it as our configuration.
			# (This allows us to inherit properties from GPT3Core, even though
			# the underlying data is different.)
	
			# Create our ChatMessages object to manage the list of messages.

		# First, see if the user provided a list of messages to start with as part of
		# the configuration.  If so, use that list.  Otherwise, specify no messages.

		msgList = None	# Default to no messages.
		if chatConf.messages != None:
			msgList = chatConf.messages

		chatCore.messages = ChatMessages(msgList)		# Create our message list.
			# Note:  We use the property setter here to ensure the list is a ChatMessages 
			# object and perform other necessary bookkeeping.

	#__/ End GPT3Core instance initializer.


	# Property to retrieve the current list of messages.
	@property
	def messages(self): return self._messages

	# Setter for the current list of messages.
	@messages.setter
	def messages(self, newMessages:ChatMessages):
		
		"""Set the current list of messages."""
		
		# Do some error checking.
		if newMessages == None:
			raise ValueError("Cannot set messages to None.")
		if not isinstance(newMessages,ChatMessages):
			raise ValueError("Cannot set messages to a non-ChatMessages object.")
		
		self._messages = newMessages

			# Here, we need to also update the chatConf object to reflect the new
			# list of messages.  This is because the chatConf object is what is
			# used to generate the JSON request to the API, and the API requires
			# that the list of messages be included in the request.
		
		self._update_chatconf_msgs()

	#__/ End gpt3ChatCore.messages instance property setter.

	def _update_chatconf_msgs(self):
		"""Update the chatConf object to reflect the current list of messages."""
		self._chatConfiguration.messages = self.messages.messageList
			# Note this is a raw list of messages, not a ChatMessages object.

	def addMessage(self, newMessage:dict):
		"""Add the given message to our list of messages."""

		# If the message is a new-style message object, change it to a message dict.
		if isinstance(newMessage, openai.types.chat.ChatCompletionMessage):
			newMessage = oaiMsgObj_to_msgDict(newMessage)

		self.messages.addMessage(newMessage)
		self._update_chatconf_msgs()			# Also update the chatConf object.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.chatConf									[instance public property]
		#|
		#|		Returns the API configuration object (instance of class
		#|		GPT3ChatAPIConfig) that is associated with this connection 
		#|		to the core GPT-3 system.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@property
	def chatConf(self):
		"""Get our current API configuration."""
		return self._chatConfiguration


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.adjustConf(params)						[instance public method]
		#|
		#|		Adjusts the API parameter values of this connection to 
		#|		the core GPT chat system as specified by the argument 
		#|		list.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def adjustConf(self, *args, **kwargs):
		"""Adjust the chat API configuration as specified."""
		self.chatConf.modify(*args, **kwargs)


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.genChatArgs()								[instance public method]
		#|
		#|		Generate the argument list for calling the core chat API.
		#|
		#|		This gets called by the ChatCompletion constructor to
		#|		generate the argument list for the API call.
		#|
		#|		Any keyword arguments provided will override the current 
		#|		values in the chat configuration.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def genChatArgs(thisChatCore:GPT3ChatCore, *args, **kwargs):
			# Note that any extra positional arguments (collected in args) are ignored.
			# Additionally, any keyword arguments that are not recognized as valid chat 
			# API parameters are also ignored.

		"""Generate the argument list for calling the core chat API.
			Any keyword arguments provided will override the current values
			in the chat configuration."""
   
		#if 'messages' in kwargs:
		#	_logger.info(f"In genChatArgs() with messages=[list of {len(kwargs['messages'])} messages]")

		chatCore = thisChatCore		# For convenience.

		apiargs = {} 	# Initially empty dict for building up API argument list.
		
		chatConf = chatCore.chatConf	# Get our current chat configuration.

		apiargs['model'] = chatConf.engineId	# This API arg. is required. Can't skip it.
			# NOTE: OpenAI used to call this parameter 'engine' but now calls it 'model'.
			# The old name still works, but is deprecated; we use the new name here in
			# case they ever remove the old name.

		# If the 'messages' keyword argument is provided, and it
		# is a ChatMessages object, then we need to convert it to
		# a list of message dictionaries.  This is because the
		# chat API expects a list of message dictionaries, not
		# a ChatMessages object.

		if 'messages' in kwargs:
			msgs = kwargs['messages']
			if isinstance(msgs, ChatMessages):
				kwargs['messages'] = msgs.messageList

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Select the parameter values to use from either the chat configuration
		#| or the keyword arguments provided to this method, as appropriate.

		maxTokens 			= kwargs.get('maxTokens',			chatConf.maxTokens)
		temperature 		= kwargs.get('temperature',			chatConf.temperature)
		topP 				= kwargs.get('topP',				chatConf.topP)
		nCompletions		= kwargs.get('nCompletions',		chatConf.nCompletions)
		stream 				= kwargs.get('stream',				chatConf.stream)
		stop 				= kwargs.get('stop',				chatConf.stop)
		presencePenalty 	= kwargs.get('presencePenalty',		chatConf.presencePenalty)
		frequencyPenalty 	= kwargs.get('frequencyPenalty',	chatConf.frequencyPenalty)

			# Unique to chat API:
		messages 			= kwargs.get('messages',	chatConf.messages)
		logitBias 			= kwargs.get('logitBias',	chatConf.logitBias)
		user 				= kwargs.get('user',		chatConf.user)

			# Available only in 0613 (June 13, 2023) or later releases of chat models.
		functionList		= kwargs.get('functionList')			# Default is None.
		if functionList:
			functionCall		= kwargs.get('functionCall', 'auto')	# Default is 'auto'
		else:
			functionCall		= kwargs.get('functionCall', None)	# Default is 'auto'

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Now, add the selected (non-None) parameter values to the argument list.
		#| (Note below we have to match the exact keyword argument names supported 
		#| by OpenAI's API.

		if maxTokens		!= None:	apiargs['max_tokens']			= maxTokens
		if temperature		!= None:	apiargs['temperature']			= temperature
		if topP				!= None:	apiargs['top_p']				= topP
		if nCompletions		!= None:	apiargs['n']					= nCompletions
		if stream			!= None:	apiargs['stream']				= stream
		#apiargs['stop'] = chr(ETX)
		if stop				!= None:	apiargs['stop']					= stop
			# Don't set stop at all for chat models. It breaks things.
		if presencePenalty	!= None:	apiargs['presence_penalty']		= presencePenalty
		if frequencyPenalty	!= None:	apiargs['frequency_penalty']	= frequencyPenalty

			# The following parameters are new in the chat API.
		if messages			!= None:	apiargs['messages']			= messages
		if logitBias		!= None:	apiargs['logit_bias']		= logitBias
		if user				!= None:	apiargs['user']				= user

			# Available only in 0613 (June 13, 2023) or later releases of chat models.
		if functionList		!= None:	apiargs['functions']		= functionList
		if functionCall		!= None:	apiargs['function_call']	= functionCall

		#if 'messages' in apiargs:
		#	_logger.info(f"In genChatArgs(), set apiargs['messages']=[list of {len(apiargs['messages'])} messages]")

			# Make sure we don't set both temperature and top_p.		
		if temperature != None and topP != None:
			# Do some better error handling here. Warning and/or exception.
			_logger.warn(f"WARNING: temp={temperature}, topP={topP}: Setting both temperature and top_p is not recommended.")

		return apiargs

	#__/ End GPT3ChatCore.genArgs() instance method.


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.genChatCompletion()						[instance public method]
		#|
		#|		This method returns the raw completion of the current 
		#|		messages, using the core's present API configuration.	 
		#|		We do graceful backoff and retry in case of REST call 
		#|		failures.
		#|
		#|		NOTE: This method does not update the messages object!  It
		#|		only returns the completion object.  The caller is
		#|		responsible for updating the messages object if and when
		#|		they wish to do so.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def genChatCompletion(self, *args, **kwargs):
	
		"""With automatic exponential backoff, query the server
			for a completion object for the given prompt using the
			connection's current API configuration."""
		
		#prettyArgs = pformat(kwargs)
		#_logger.debug(f"In GPT3ChatCore.genChatCompletion() with args={args}, keyword args:\n" + prettyArgs)

		#if 'messages' in kwargs:
		#	_logger.info(f"In genChatCompletion() with messages=[list of {len(kwargs['messages'])} messages]")

		return ChatCompletion(self, *args, **kwargs)
			# Calls the ChatCompletion constructor; this does all the real work 
			# of calling the API.
		
	#__/ End instance method GPT3Core.genChatCompletion().


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.genMessage()							[instance public method]
		#|
		#|		This method returns a new message based on the current 
		#|		messages, using the chat core's present API configuration.
		#|		The message is returned as a dictionary with the following
		#|		attributes:
		#|
		#|			'role':			This is always 'assistant'.
		#|			'content':		<text of the new message>
		#|			'created_at':	<timestamp of the new message>
		#|
		#|		Note this calls .genChatCompletion() internally.
		#|
		#|		To do: Provide the option to do a temporary modification of
		#|		one or more API parameters in the argument list.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def genMessage(self:GPT3ChatCore, messages=None):
		"""Generate a new message based on the current messages."""

		#_logger.debug(f"In GPT3ChatCore.genMessage() with {len(messages)} messages...")

		resultCompletion = self.genChatCompletion(messages=messages)

		newMessage = resultCompletion.message

		_logger.debug("[GPT-3/API] Server returned new message: [" + str(newMessage) + ']')

			# The newMessage object returned from the completion object is 
			# already a dict with role and content, so just add the timestamp.

		newMessage['created_at'] = datetime.now().isoformat()
		return newMessage
		
	#__/ End instance method GPT3Core.genMessage().


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	.genString()							[instance public method]
		#|
		#|		This method returns a completion of the current messages,
		#|		or the messages argument (if provided), using the chat 
		#|		core's present API configuration, and returns it as a 
		#|		single string.	 Uses .genMessage() internally.
		#|
		#|		To do: Provide the option to do a temporary modification of
		#|		one or more API parameters in the call's argument list.
		#|
		#|		NOTE: This method does not update the messages object!  It
		#|		only returns the completion content.  The caller is
		#|		responsible for updating the messages object if and when
		#|		they wish to do so.
		#|
		#|		Also note: If you want the result message to be 
		#|		automatically timestamped, you should just use
		#|		.genMessage() directly instead.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def genString(self:GPT3ChatCore, messages=None):

		"""Generate a single completion string for the current messages
			or the messages argument (if provided)."""

		_logger.debug(f"In GPT3ChatCore.genString() with {len(messages)} messages...")

		newMessage = self.genMessage(messages=messages)
		return newMessage['content']

	#__/ End instance method GPT3Core.genString().

#__/ End class GPT3ChatCore.


#|==============================================================================
#| Module object initialization.								[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Commented out; don't create this unless/until it is actually needed.
#_theTokenCounterCore = GPT3Core(engineId='ada', echo=True, maxTokens=0, logProbs=0)
	# This connection provides functionality needed to count tokens.
	# Note we use the 'ada' engine because it is cheapest ($0.80/1M tokens).


#/==============================================================================
#|	Module function definitions.								[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#/==========================================================================
	#|	Module public functions.								[code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


# NOTE: The below function is currently only used by some early test scripts. It 
# is deprecated, but we are leaving it here for future reference.  We currently 
# prefer to use the local_countTokens() function, which is imported from the 
# tokenizer/tokenizer.py module, or the tiktokenCount() function, which is
# defined below (the latter is the recommended function to use now).

def countTokens(text:str=None):

	"""Counts tokens in the given text using the online Ada model (pretty cheap)."""

	if text == None or text == "":
		return 0
	else:

		global _theTokenCounterCore

		if _theTokenCounterCore is None:
			_theTokenCounterCore = GPT3Core(engineId='ada', echo=True, maxTokens=0, logProbs=0)
				# This connection provides functionality needed to count tokens.
				# Note we use the 'ada' engine because it is cheapest ($0.80/1M tokens).

			# Please note this is not free! It uses probably 2*text of quota.
		inputComplObj = _theTokenCounterCore.genCompletion(text)
		return inputComplObj.nTokens

#__/ End module public function countTokens().


def createAPIConfig(engineId:str=None, **kwargs):

	"""Creates a new GPT3APIConfig object and returns it. We need to define 
		this factory function because the choice of which class to 
		instantiate depends on the engine ID. If the ID denotes a chat 
		engine, we instantiate a GPT3ChatAPIConfig object; otherwise we 
		instantiate a GPT3APIConfig object. Keyword arguments are passed
		through to the constructor of the appropriate class."""

	# If no engine ID was specified, try to get it from the AI persona's config file.
	if engineId == None:
		engineId = _aiEngine()	# Gets the AI persona's default engine ID from the config file.
		if engineId != None:
			_logger.warning("[GPT-3/API] No engine ID was specified, so we are using the default engine ID for the current AI persona, which is [" + engineId + "].")

	# If we still don't have an engine ID, use the default engine ID.
	if engineId == None:
		engineId = DEF_ENGINE
		_logger.warning("[GPT-3/API] No engine ID specified; using default engine ID [" + engineId + "].")

	# If the engine ID is for a chat engine, create a GPT3ChatAPIConfig object;
	# otherwise create a GPT3APIConfig object.
	if _is_chat(engineId):
		return GPT3ChatAPIConfig(engineId=engineId, **kwargs)
	else:
		return GPT3APIConfig(engineId=engineId, **kwargs)

#__/ End module public function createAPIConfig().


def createCoreConnection(engineId:str=None, conf:GPT3APIConfig=None, **kwargs):

	"""Creates a new GPT3Core object and returns it.  We need to define 
		this factory function because the choice of which class to 
		instantiate depends on the engine ID. If the ID denotes a chat 
		engine, we instantiate a GPT3ChatCore object; otherwise we 
		instantiate a GPT3Core object. Keyword arguments are passed
		through to the constructor of the appropriate class."""

	# If no engine ID was specified, get it from the conf object, if provided.
	if engineId == None and conf != None:
		engineId = conf.engineId
	
	# If we still don't have an engineId, try to get it from the AI persona's config file.
	if engineId == None:
		engineId = _aiEngine()	# Gets the AI persona's default engine ID from the config file.
		if engineId != None:
			_logger.warning("[GPT-3/API] No engine ID specified; using AI persona's engine ID [" + engineId + "].")

	# If we still don't have an engine ID, use the default engine ID.
	if engineId == None:
		engineId = DEF_ENGINE
		_logger.warning("[GPT-3/API] No engine ID specified; using default engine ID [" + engineId + "].")

	# Instantiate the appropriate type of core object.
	if _is_chat(engineId):
		newCore = GPT3ChatCore(engineId=engineId, chatConf=conf, **kwargs)
	else:
		newCore = GPT3Core(engineId=engineId, config=conf, **kwargs)

	return newCore

#__/ End module public function createCoreConnection().


def tiktokenCount(text:str=None, encoding:str='gpt2', model:str=None):

	"""Counts tokens in the given text using the tiktoken library.
		This is our currently preferred token-counting function
		due to its low cost (free), its speed, its accuracy, and
		its lack of dependence on GPT-2 having been installed."""

	# If the model argument is provided, use it to get the encoding.

	if model != None:
		encodingObj = tiktoken.encoding_for_model(model)
	else:
		encodingObj = tiktoken.get_encoding(encoding)
		
	num_tokens = len(encodingObj.encode(text, disallowed_special=()))
		# Note: Setting the disallowed_special keyword argument to the
		# empty tuple causes special tokens like '<|endoftext|>' to be
		# encoded as normal text. This could inflate our token count,
		# but it's better to estimate it a bit too high than too low.
		# (But, we don't know how the actual API will handle this text
		# yet...)

	return num_tokens

#__/ End module public function tiktokenCount().


def loadStatsIfNeeded():

	"""If the stats file hasn't been loaded from the filesystem yet,
		this loads it."""

	# NOTE: We now just load stats unconditionally, because if it's 
	# a new day, we'll need to do housekeeping like renaming the stats
	# file and resetting the stats.

	#if not _statsLoaded:
	_loadStats()

#__/ End module public function loadStatsIfNeeded().


def stats():
	"""After using the API, this returns a human-readable table of usage statistics."""
	return _statStr
#__/ End module public function stats().


def genImage(desc:str, dims:str=None, style:str=None):
	"""Generate an image from the given description string with given dimensions.
		Returns the URL of the generated image."""
	
	if dims is None:
		dims = "1024x1024"

	if style is None:
		style = 'vivid'

	_logger.info(f"Generating a {style} {dims} image with description [{desc}].")

	# This was the old API call for the Dall-E 2 image generator (now deprecated):
	#response = openai.Image.create(
	#	prompt = desc,
	#	n = 1,					# Can range from 1-10.
	#	size = "1024x1024"		# Other options include 512x512 and 256x256.
	#)

	# This is the new API call for the Dall-E 3 image generator.
	response = _client.images.generate(
		model	= 'dall-e-3',		# Other options include: 'dall-e-2'
		prompt	= desc,				# max length: 4000 characters for dall-e-3
		size	= dims,				# Options include: 1024x1024 (square, default), 1792x1024 (landscape) and 1024x1792 (portrait).
		quality = 'hd',				# Other options include: 'standard'
		style	= style,			# Options include: 'vivid', 'natural'
	)

	_logger.debug(f"Got response: [{response}]")

	#image_url = response['data'][0]['url']

	image_url		= response.data[0].url
	revised_prompt	= response.data[0].revised_prompt

	return (image_url, revised_prompt)
#__/ End module public function genImage().
	

def genSpeech(text:str, user:str = None, response_format=None):
	"""Generates spoken voice audio for the given text.
		Returns the filename of the generated (.mp3) file.
		The <user> argument, if provided, is used in the
		output filename to distinguish speech responding
		to different users."""

	_logger.info(f"Generating speech for the following text: [{text}]")

	if response_format is None:
		response_format = "mp3"	# Do this by default

	speechDir = _speechDirname()	# Creates dir if it doesn't exist.

	# Construct the filename using the username (if provided) and a random number.
	randnum = random.randint(0, 999999)
	filename = str(randnum).zfill(6)		# Format with leading 0s
	if user:
		filename = user + '--' + filename
	filename += '.' + response_format

	speech_filepath = path.join(speechDir, filename)

	response = _client.audio.speech.create(
		model = "tts-1",	# Optimized for speed. Other choices include: tts-1-hd (optimized for quality).
		voice = "echo",		# Other choices include alloy, fable, onyx, nova, shimmer.
		input = text,
		response_format = response_format
	)

	response.stream_to_file(speech_filepath)

	return speech_filepath


def transcribeAudio(filename:str):
	"""Given the path to an MP3 audio file, use the transcriptions endpoint
		to convert the audio to text, and return the text."""
	
	_logger.info(f"Passing {filename} to the OpenAI transcription endpoint...")
	audio_file = open(filename, 'rb')

	transcript = _client.audio.transcriptions.create(
		model	= "whisper-1",
		file	= audio_file
	)

	# Legacy API
	#transcript = openai.Audio.transcribe("whisper-1", audio_file)

	_logger.info(f"\tGot back this transcript: {transcript}")

	text = transcript.text
	#text = transcript['text']	# Legacy API

	return text
#__/ End module public function transcribeAudio();


import base64
import requests

api_key = getenv('OPENAI_API_KEY')

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def describeImage(filename:str, verbosity:str='medium', query:str=None):
	"""Given the path to a JPEG image, use the GPT-4V model
		to generate a text description of the image, and return
		the text."""

	_logger.info(f"Passing {filename} to the OpenAI GPT-4V model...")

	# Select description type.
	if verbosity == 'none' or verbosity is None:
		which_kind = None
	elif verbosity == 'concise' or verbosity == 'low':
		which_kind = 'concise description'
	elif verbosity == 'detailed' or verbosity == 'high':
		which_kind = 'detailed description'
	else:	# Default level = medium verbosity.
		which_kind = 'description'

	# If a description was requested, construct an appropriate prompt.
	if which_kind:
		# Compose the prompt.
		prompt = f"Please provide a {which_kind} of the following image."

		# Specifically ask for text if generating a detailed description.
		if verbosity == 'detailed':
			prompt += " If the image includes text, please include it in your response."

		# Include the query, if provided.
		if query:
			prompt += " Also, after the image description, please repeat and then answer the following question about the image: " + query

	# If only a query was requested, construct an appropriate prompt.
	elif query:
		prompt = "Please answer the following question about the image: " + query

	# Default prompt if no description was requested and no query was provided.
	else:
		prompt = "Please respond to the following image."

	# Load the image to base64.
	base64_image = encode_image(filename)

	# Construct POST headers.
	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {api_key}"
	}

	# Construct POST payload.
	payload = {
		"model": "gpt-4-vision-preview",
		"messages": [
			{
				"role": "user",
				"content": [
					{
						"type": "text",
						"text": prompt
					},
					{
						"type": "image_url",
						"image_url": {
							"url": f"data:image/jpeg;base64,{base64_image}"
						}
					}
				]
			}
		],
		"max_tokens": 500
	}
	
	# Stream the image to the API via an https POST.
	response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

	# Parse the response.

	response_json = response.json()
	#print(response.json())

	description = response_json['choices'][0]['message']['content']
	_logger.info(f"Got image description: [{description}]")

	#return "[to be implemented]"
	return description


	#/==========================================================================
	#|	Module private functions.								[code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


def _aiEngine() -> str:
	
	"""Returns the AI engine ID, as a string."""

	return TheAIPersonaConfig().modelVersion


def _speechDirname():

	"""Constructs and returns the pathname to the $AI_DATADIR/speech/
		directory. Assumes the global _aiPath has already been
		initialized to $AI_DATADIR. Creates the speech/ subdirectory
		if it doesn't already exist."""

	_initAiPath()

	speech_dir = path.join(_aiPath, 'speech')

	_logger.debug(f"Got AI speech directory = {speech_dir}.")

	if not path.exists(speech_dir):
		makedirs(speech_dir)

	return speech_dir


def _initAiPath():
	global _aiPath

	if _aiPath is not None:
		return	# Already initialized

		#----------------------------------------------------------
		# First, get the AI persona configuration, because it 
		# contains key information we need, such as the location
		# of the AI's data directory.

	aiConf = TheAIPersonaConfig()

		#------------------------------------------------------
		# Next, get the location of the AI's data directory,
		# which is in the AI persona configuration object.
				
	aiDataDir = aiConf.aiDataDir

	_aiPath = aiDataDir
		
	_logger.debug(f"Got AI data directory = {aiDataDir}.")


def _statsPathname(prefix:str=None):

	"""Constructs and returns the pathname to the api-stats.json file."""

	_initAiPath()

	stats_dir = path.join(_aiPath, 'stats')
	if not path.exists(stats_dir):
		makedirs(stats_dir)

		#-----------------------------------------------------
		# Next, we need to get the name of the stats json file
		# (relative to that directory). At the moment, this
		# comes from a module constant, defined above.
				
	statsFilename = _STATS_FILENAME
	if prefix:
		statsFilename = prefix + '-' + _STATS_FILENAME
		
		#------------------------------------------------------
		# Next, we need to construct the full pathname of the
		# API statistics JSON file.
		
	statsPathname = path.join(stats_dir, statsFilename)
		
		#-------------------------
		# Return it to the caller.

	return statsPathname

#__/ End module function _statsPathname().


def _textPath():
	"""Constructs and returns the pathname to the text file to store the API stats table."""

	_initAiPath()

	return path.join(_aiPath, 'stats', 'api-stats.txt')


def _loadStats():

	"""Loads the api-stats.json file from the AI's data directory.
		We also notice if today's date is different from the last-
		modified date on the file, and if so, we archive the old
		file and reset the stats to zero."""

	global _statsLoaded, _inputToks, _outputToks, _expenditures, _totalCost

		# This constructs the full filesystem pathname to the stats file.
	statsPath = _statsPathname()

	# Do the following in a thread-safe way.
	with _lock:

		newDay = False

		# Get today's date.
		today = date.today()

		_logger.debug(f"In _loadStats(): Today's date is: {today}.")

		# Get the last-modified date of the stats file.
		try:
			lastModDate = date.fromtimestamp(path.getmtime(statsPath))
			_logger.debug(f"In _loadStats(): {statsPath} last modified: {lastModDate}.")
		except:
			_logger.error(f"In _loadStats(): Couldn't get date of {statsPath}! Danger, Will Robinson.")
			lastModDate = None
			newDay = True

		# If the last-modified date is different from today's date,
		# archive the old file and reset the stats to zero.
		if lastModDate is not None and lastModDate != today:
			
			# It's a new day!
			newDay = True

			_logger.info(f"Today's date is {today}, but the last-modified date of the API usage statistics file {statsPath} is {lastModDate}.")
			_logger.normal("\nStats file loader: Starting a new day!")

			# Construct the name of the archive file.
			archivePath = _statsPathname(prefix = str(lastModDate))
			#archivePath = lastModDate.strftime('%Y-%m-%d') + '.' + statsPath

			# Rename the old file to the archive file.
			try:
				rename(statsPath, archivePath)
				_logger.normal(f"\tNOTE: Archived old API usage statistics data file {statsPath}\n\t\tto {archivePath}.")
			except:
				_logger.warn(f"Couldn't rename {statsPath} to {archivePath}.")

			# Reset the stats to zero.
			_clearStats()

			# If it's actually a new day, we also need to create a new
			# api-stats.txt file to store the API stats table.
			_displayStats()

		else:

			_logger.info(f"Loading usage statistics from {statsPath}...")

			try:
				with open(statsPath) as inFile:
					
					stats 			= json.load(inFile)

					_inputToks 		= stats['input-tokens']
					_outputToks 	= stats['output-tokens']
					_expenditures 	= stats['expenditures']
					_totalCost 		= stats['total-cost']
			
					#_logger.normal(f"Loaded API usage stats from {statsPath}: \n{pformat(stats, width=25)}")

				# Ignore file doesn't exist errors.
			except:
				_logger.warn(f"Couldn't open API usage statistics file {statsPath}--it might not exist yet.")
				pass

			finally:

				# If this was our first time (trying to) load the stats, display them.
				if not _statsLoaded:
					# In this case, we don't need to save the stats (redundant),
					# but we do want to display them:
					_displayStats(doWrite=False)
						# Note: These could actually be yesterday's stats if the clock JUST clicked 
						# past midnight, but this hardly matters.

				_statsLoaded = True		# Hey, we tried at least!


#__/ End module function _loadStats().


def _statLine(doWrite:bool, line:str):

	"""This quick-and-dirty utility method saves a line of
		the API statistics table to several places."""

	global _statStr

		# Log this line as an INFO-level log message.
	_logger.info(line)
	
		# Append this line to the api-stats.txt file.
	if doWrite:
		print(line, file=_statFile)

		# Also accumulate it in this global string.
	_statStr = _statStr + line + '\n'

#__/ End module function _statLine().


def _displayStats(doWrite:bool=True):
		# If called with doWrite=False, this function will not
		# actually write the stats table to the api-stats.txt file.

	"""Displays usage statistics in an easily-readable format.
		Also saves them to a file api-stats.txt."""

	global _statFile, _statStr

	with _lock:		# Grab this module's mutex lock.
		# (We do this because we want this function to be thread-safe.)

		# Before we write the new stats table, we want to make sure
		# that we are writing a new file for each day. We do this as
		# follows, if the api-stats.txt file already exists:
		#	1. Get today's date.
		#	2. Get the date of the last modification to the file.
		#	3. If the dates are different, rename the file to
		#		api-stats-YYYY-MM-DD.txt, where YYYY-MM-DD is the
		#		date of the last modification.

		if doWrite:		# (We only need to bother if actually writing to a file.)

			# Get today's date.
			today = date.today()

			_logger.debug(f"In _displayStats(): Today's date is {today}.")

			# Get the date of the last modification to the file.
			try:
				lastMod = date.fromtimestamp(path.getmtime(_textPath()))
				_logger.debug(f"In _displayStats(): {_textPath()} last modified: {lastMod}.")
			except:
				lastMod = None

			# If the dates are different, rename the file to
			# api-stats-YYYY-MM-DD.txt, where YYYY-MM-DD is the
			# date of the last modification.
			if lastMod and lastMod != today:
		
				_logger.info(f"Today's date is {today}, but the last-modified date of the API usage statistics file {_textPath()} is {lastMod}.")
				_logger.normal("Stats display: Starting a new day!")
				
				oldPath = _textPath()
				_initAiPath()
				newPath = path.join(_aiPath, 'stats', f"api-stats-{lastMod}.txt")
				try:
					rename(oldPath, newPath)
					_logger.normal(f"\tNOTE: Archived old API usage statistics text file {oldPath}\n\t\tto {newPath}.")
				except:
					_logger.error(f"Couldn't rename {oldPath} to {newPath}. Old stats will get stomped!")

		# Start generating a new stats string.
		_statStr = ""

		# If doWrite=True, then open the file for writing.
		if doWrite: 
			try:
				_statFile = open(_textPath(), 'w')
			except:
				_logger.warn(f"Couldn't open API usage statistics file {_textPath()} for writing.")
				doWrite = False

		# NOTE: We may need to widen some of the columns in this table
		#  if the contents start to overflow.

		_statLine(doWrite, "")
		_statLine(doWrite, "                       |         Token Counts          |")
		_statLine(doWrite, "                       | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ |")
		_statLine(doWrite, "Engine Name            |    Input |  Output |    Total |  USD Cost")
		_statLine(doWrite, "=======================|==========|=========|==========|==========")
		
		# Cumulative input, output, and total token counts.
		cumIn = cumOut = cumTot = 0
		
		# Generate a table row for each engine.
		for engine in _ENGINE_NAMES:
			
			engStr 	= "%22s" % engine

			# If stats structures are out of date, expand them as needed.
			if not engine in _inputToks:
				_inputToks[engine] = 0
				_outputToks[engine] = 0
				_expenditures[engine] = 0

			inToks 	= _inputToks[engine]
			outToks = _outputToks[engine]
			total 	= inToks + outToks
	
			inTokStr  = "%8d" % inToks
			outTokStr = "%7d" % outToks
			totStr 	  = "%8d" % total
	
			cost = "$%8.4f" % _expenditures[engine]
	
			_statLine(doWrite, f"{engStr} | {inTokStr} | {outTokStr} | {totStr} | {cost}")
	
			cumIn  = cumIn  + inToks
			cumOut = cumOut + outToks
			cumTot = cumTot + total
		
		#__/ End loop over engine names.
	
		# Generate a table row for the accumulated totals.
		cumInStr  = "%8d" % cumIn
		cumOutStr = "%7d" % cumOut
		cumTotStr = "%8d" % cumTot
	
		totStr = "$%8.4f" % _totalCost
	
		_statLine(doWrite,  "~~~~~~~~~~~~~~~~~~~~~~~|~~~~~~~~~~|~~~~~~~~~|~~~~~~~~~~|~~~~~~~~~~")
		_statLine(doWrite, f"TOTALS:                | {cumInStr} | {cumOutStr} | {cumTotStr} | {totStr}")
		_statLine(doWrite, "")
	
		# If doWrite=True, then we were writing to the file, and we need to close it.
		if doWrite:
			_statFile.close()

	#__/ End with statement.

#__/ End module function _displayStats().


def _saveStats():

	"""Saves cumulative API usage statistics to the api-stats.json file
		in the AI's data directory."""

	global _expenditures, _totalCost

		# This constructs the full filesystem pathname to the stats file.
	statsPath = _statsPathname()

	_logger.info(f"Saving API usage stats to {statsPath}...")

	with open(statsPath, 'w') as outFile:

		(costs, dollars) = _recalcDollars()

		_expenditures = costs
		_totalCost = dollars

		stats = {
				'input-tokens': _inputToks,
				'output-tokens': _outputToks,
				'expenditures': costs,
				'total-cost': dollars
			}

		
		_logger.debug(f"Saving API usage stats to {statsPath}: \n{pformat(stats, width=25)}")

		json.dump(stats, outFile)

			# Pretty-print it to the file.
		#pprint(stats, width=25, stream=outFile)
	
	#__/ End with statement.

	_displayStats()		# Displays and saves a text format version.

#__/ End module function _saveStats().


def _recalcDollars():

	"""This recalculates per-engine and total dollar costs
		from the per-engine token counts."""

	costs = {}		# This is a dictionary mapping engine names to cumulative costs (in dollars).
	dollars = 0		# Total cost of all API calls, in dollars.
	for engine in _ENGINE_NAMES:

		inToks = _inputToks[engine]		# Tokens in the input text (prompt).
		outToks = _outputToks[engine]	# Tokens in the output text (response).
		nToks = inToks + outToks		# Total number of tokens used.

			# If the engine has a prompt-price attribute, then price the input
			# tokens at that price. Otherwise, price them at the default price.
			# Note: all prices are per 1000 tokens.
			
		promptPrice = _get_prompt_price(engine)
		if promptPrice:				
			engCost = (inToks/1000) * promptPrice
			engCost += (outToks/1000) * _get_price(engine)
		else:
			engCost = (nToks/1000) * _get_price(engine)

		costs[engine] = engCost
		dollars = dollars + engCost

	#__/ End loop over engine names.
		
	return (costs, dollars)

#__/ End module function _recalcDollars().


def _msg_repr(msg:dict) -> str:

	"""Return a string representation of the given message dict.
		Note that this is an educated guess about how the API backend
		actually represents the messages to the underlying language
		model. It's not documented anywhere, but we're guessing that
		(for GPT-4, at least) it's probably something like this:

			<role> ':' [ <name> ':' ] '\n'
			<content> [RS] '\n

		where <role>, <name> (if present), and <content> are the values
		of the 'role', 'name' and 'content' fields of the message dict,
		respectively, and [RS] is a message separator token used by the
		API back-end to separate messages."""
	
	# If message is in the new object type, convert it.
	if isinstance(msg, openai.types.chat.ChatCompletionMessage):
		msg = oaiMsgObj_to_msgDict(msg)

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| NOTE: Our current best guess as to the back-end message
	#| representation is as follows:
	#|
	#|
	#|		<role_token> ':' [ <name_tokens> ':' ] '\n'
	#|		<content_tokens> <end_msg_token> '\n'
	#|
	#| where <role_token> is one of 'system', 'user', or 'assistant';
	#| <name_tokens> is the value of the 'name' field, if present;
	#| ':' and '\n' are the single tokens for colon and newline; and
	#| <end_msg_token> is some unknown token; we'll assume [RS], the
	#| ASCII Record Separator control character (ctrl-^, 0x1e).
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	#_logger.debug(f"gpt3.api._msg_repr(): Generating representation for message: {pformat(msg)}.")

	# Make sure there's a non-empty 'role' field in the message; if so, start with it.

	if 'role' in msg and msg['role'] != None:
		role = msg['role'] + ':'	# Append a colon.

	else:	# Role is missing or None.
		# This should never happen, but just in case...
		_logger.error("gpt3.api._msg_repr(): Missing 'role' field in message:\n" + pformat(msg))
		role = ""

	# If the message has a 'name' field, then this is appended to the
	# 'role' field. NOTE: In chat GPT-3.5, it may take the place of 'role'.
	if 'name' in msg:
		role += msg['name'] + ':'

	# Get the message content.
	content = msg['content']

	# Get the 'function_call' value, if present.
	fcall = msg.get('function_call', None)

	# Make sure role isn't still None at this point
	if role is None:
		_logger.error("gpt3.api._msg_repr(): Somehow role is None at this "
					  "line, and it shouldn't be.")
		role = ""

	# Ditto with content
	if content is None and fcall is None:
		_logger.error("gpt3.api._msg_repr(): Message content and function call "
					  "are both None; this is unexpected.")

	if content is not None:
		rep = role + '\n' + \
			  content + chr(RS) + '\n'

	elif fcall is not None:		# This is just a damn guess as to how function
		#calls *might* be formatted at the back end. It's probably wrong.

		# This shtuff is so annoying...

		from openai.types.chat.chat_completion_assistant_message_param import FunctionCall

		if fcall.__class__.__name__ == "FunctionCall":	# Sooo stupid...
			fname = fcall.name
			fargs = fcall.arguments
		else:
			fname = fcall['name']
			fargs = fcall['arguments']

		rep = role + '\n' + \
			  '@' + fname + '(' + fargs + ')' \
			  + chr(RS) + '\n'

	return rep

#__/ End module function _msg_repr().


# Expose the message representation function as a module-level public function.
def messageRepr(message:dict) -> str:
	return _msg_repr(message)


def _msg_tokens(msg:dict, model:str=None) -> int:
	"""Return the number of tokens in the given message dict. Note that
		we include the tokens in the 'role' and 'content' fields of
		the message dict, as well as an estimate of the tokens in
		whatever behind-the-scenes formatting the API backend uses 
		to represent the messages before passing them to the 
		underlying language model."""
		
	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| NOTE: Our current best guess as to the back-end message
	#| representation is as follows:
	#|
	#|
	#|		<role_token> ':' [ <name_tokens> ':' ] '\n'
	#|		<content_tokens> <end_msg_token> '\n'
	#|
	#| where <role_token> is one of 'system', 'user', or 'assistant';
	#| <name_tokens> is the value of the 'name' field, if present;
	#| ':' and '\n' are the single tokens for colon and newline; and
	#| <end_msg_token> is some unknown token; we'll assume [RS], the
	#| ASCII Record Separator control character (ctrl-^, 0x1e).
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	msgToks = tiktokenCount(_msg_repr(msg), model=model)

	# This is too verbose for normal operation. Comment it out after testing.
	#if logmaster.doDebug: _logger.debug(f"Message {msg} has {msgToks} tokens.")

	return msgToks


#|==============================================================================
#| Module main load-time execution.								  [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# We now postpone loading the API usage stats till they are first needed.
#loadStats()


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|	END FILE:	gpt3/api.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
