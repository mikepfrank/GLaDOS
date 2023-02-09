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
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.gpt3 (GLaDOS GPT-3 interface component)


	MODULE DESCRIPTION:
	-----------------

		This module implements a convenience wrapper around OpenAI's API
		for accessing their GPT-3 language models.	The main feature that
		this wrapper provides at the moment is keeping track of the current
		values of various API parameters.  It also provides handy functions
		for things like measuring string lengths in tokens.


	PUBLIC CLASSES:

		GPT3APIConfig - Keeps track of a set of API parameter settings.
			These can also be modified dynamically.

		GPT3Core - A connection to the core GPT-3 system that maintains
			its own persistent API parameters.
			
		Completion - For objects representing results returned by the 
			core API.


	PUBLIC GLOBALS:

		Note: The following global module 'constants' can be modified 
		dynamically by the user. They will affect the properties of
		subsequently-created instances of GPT3Core, but not of the
		existing instances.	 To modify an existing instance, access
		its .conf property.

			DEF_ENGINE	- GPT-3 engine name (default 'davinci').
			DEF_TOKENS	- Max. number of tokens to output (def. 42).
			DEF_TEMP	- Default temperature (default is 0.5).
			DEF_STOP	- Stop string or strings (3 newlines).


	PUBLIC FUNCTIONS:
	
			countTokens()	- Counts tokens in a string using the
								API.  Note that this operation is
								expensive.	For most applications
								you should use the method in the
								tokenizer.tokenizer module instead.

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
		| result = gpt3.genCompletion("Mary had a little lamb, ")  |
		|														   |
		| pprint(result.complStruct)							   |
		\----------------------------------------------------------/
			|
			V 
			
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

"""
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	#|==========================================================================
	#|
	#|	 1. Module imports.								   [module code section]
	#|
	#|			Load and import names of (and/or names from) various
	#|			other python modules and pacakges for use from within
	#|			the present module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	os			import	path	# Manipulate filesystem path strings.
from	pprint		import	pprint, pformat		# Pretty-print complex objects.
import	json	# We use this to save/restore the API usage statistics.

		#|======================================================================
		#|	1.2. Imports of modules to support GPT-3.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import openai		# OpenAI's Python bindings for their REST API to GPT-3.
import backoff		# Utility module for exponential backoff on failures.

		#|======================================================================
		#|	1.3. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster import getComponentLogger, ThreadActor, sysName

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component


			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from tokenizer.tokenizer import countTokens as local_countTokens
	# Method to count tokens without an API call.

from config.configuration import TheAIPersonaConfig


#|==============================================================================
#|	Global constants.											[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	#|--------------------------------------------------------------------------
	#|	__all__										[special module attribute]
	#|
	#|		These are the names that will be imported if you do 
	#|		'from gpt3.api import *'.  This in effect declares what
	#|		the public interface to this module consists of.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__
__all__ = [

			# Module public global constants.
		'DEF_ENGINE',		# Default GPT-3 engine name ('davinci').
		'DEF_TOKENS',		# Default number of tokens to return (42).
		'DEF_TEMP',			# Default temperature value (normally 0.75).
		'DEF_STOP',			# Default stop string or list of strings.
		
			# Module public classes.
		'GPT3APIConfig',	# Class: A collection of API parameter settings.
		'Completion',		# Class: An object for a result returned by the API.
		'GPT3Core',			# Class: Instance of the API that remembers its config.
			# Exception classes.
		'PromptTooLargeException',	# Exception: Prompt is too long to fit in GPT-3's receptive field.
		
			# Module public functions.
		'countTokens'		# Function to count tokens in a string. (Costs!)
	
	]


	#|--------------------------------------------------------------------------
	#|  _ENGINE_ATTRIBS				[module global private constant structure]
	#|
	#|	    This is a dictionary mapping GPT-3 engine names to their 
	#|		associated attributes.  So far, we only care about the
	#|		'field-size' attribute, which is the number of tokens in
	#|		the GPT-3 receptive field, and the 'price' attribute,
	#|		which is the cost (per 1,000 tokens) to use the engine.
	#|
	#|		Later on, we may add more attributes to this structure,
	#|		and use the individual sub-dictionaries to represent the
	#|		engine we are currently working with.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#	NOTE: Current Model Pricing Per 1 million tokens (as of 12/24/'20):
	#	-------------------------------------------------------------------
	#		Ada:		$ 0.80	(1.3B params?)					$0.61/Bparam/Mtoken
	#		Babbage:	$ 1.20	(2.7B params? - or maybe 6.7B)	$0.44/Bparam/Mtoken
	#		Curie:		$ 6.00	(13B params?)					$0.46/Bparam/Mtoken
	#		DaVinci:	$60.00	(175B params?)					$0.34/Bparam/Mtoken

# Initialize a dictionary of dictionaries called '_ENGINE_ATTRIBS', keyed by the engine
# name, whose entries are dictionaries of attribute-value pairs, which respectively
# contain the data from corresponding rows of this table:
#
#    engine-name        field-size    price	(per 1,000 tokens)
#    ----               ----------    -----
#    ada                2048          0.0008	# = $0.80 / 1M tokens
#    babbage            2048          0.0012	# = $1.20 / 1M tokens
#    curie              2048          0.006		# = $6.00 / 1M tokens
#    davinci            2048          0.06		# = $60.00 / 1M tokens
#    text-ada-001       2048          0.0008
#    text-babbage-001   2048          0.0012
#    text-curie-001     2048          0.006
#    text-davinci-001   2048          0.06
#    text-davinci-002   4096          0.06

# The below statement was written by Codex, with format adjustments by MPF.

_ENGINE_ATTRIBS = {
    'ada':				{'engine-name': 'ada', 		    	'field-size': 2048, 'price': 0.0008},
    'babbage':			{'engine-name': 'babbage',	    	'field-size': 2048, 'price': 0.0012},
    'curie':			{'engine-name': 'curie',	    	'field-size': 2048, 'price': 0.006},
    'davinci':			{'engine-name': 'davinci',	    	'field-size': 2048, 'price': 0.06},
    'text-ada-001':		{'engine-name': 'text-ada-001',	    'field-size': 2048, 'price': 0.0008},
    'text-babbage-001': {'engine-name': 'text-babbage-001', 'field-size': 2048, 'price': 0.0012},
    'text-curie-001':	{'engine-name': 'text-curie-001',   'field-size': 2048, 'price': 0.006},
    'text-davinci-001': {'engine-name': 'text-davinci-001', 'field-size': 2048, 'price': 0.06},
    'text-davinci-002': {'engine-name': 'text-davinci-002', 'field-size': 4096, 'price': 0.06}
}

# Given an engine name and an attribute name, return the attribute value.
def _get_engine_attr(engine_name, attr_name):
	return _ENGINE_ATTRIBS[engine_name][attr_name]

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


	#|------------------------------------------------------------------
	#|	These constants provide default values for GPT-3's parameters.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global		DEF_ENGINE				# Default GPT-3 engine name.
DEF_ENGINE	= 'davinci'				# This is the original largest (175B-parameter) model. Origin of Gladys.
#DEF_ENGINE	= 'text-davinci-002'	# New "best" (4000-token field) model.

global		DEF_TOKENS	# Default number of tokens to return.
#DEF_TOKENS	= 42		# Of course.
DEF_TOKENS  = 100

global		DEF_TEMP	# Default temperature value.
#DEF_TEMP	= 0.5		# Is this reasonable?
DEF_TEMP	= 0.75		# I think this makes repeats less likely.

global		DEF_STOP	# Default stop string (or list of up to 4).
DEF_STOP	= "\n\n\n"	# Use 3 newlines (two blank lines) as stop.

global		_ENGINE_NAMES		# List of engine names.
# Retrieve this from the keys of the '_ENGINE_ATTRIBS' dictionary.
_ENGINE_NAMES = list(_ENGINE_ATTRIBS.keys())

global 		_STATS_FILENAME		# Name of file for saving/loading API usage statistics.
_STATS_FILENAME = 'api-stats.json'

global 		_aiPath		# Path to the AI's data directory.
_aiPath 	= None		# Not yet initialized.


#|==============================================================================
#|	Global variables.											  [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#--------------------------------------------------------------
	# The following globals are used for tracking usage statistics.

global 		_statFile	# File object for saving/loading API usage statistics.
_statFile 	= None		# Not yet initialized.

global 			_statsLoaded	# Have we attempted to load stats from the file?
_statsLoaded 	= False			# We haven't tried to load stats from the file yet.

global 			_inputLength	# Length of the input string.
_inputLength 	= 0				# Will be modified when processing a query.

global inputToks, outputToks	# These are dictionaries of token counts.
	# (Cumulative tokens used for each engine since last reset.)

# Initialize two separate dicts to hold cumulative input & output token counts.

inputToks = {
		'ada':					0,
		'babbage':				0,
		'curie':				0,
		'davinci':				0,
		'text-ada-001':			0,
		'text-babbage-001':		0,
		'text-curie-001':		0,
		'text-davinci-001':		0,
		'text-davinci-002':		0,
	}

outputToks = {
		'ada':					0,
		'babbage':				0,
		'curie':				0,
		'davinci':				0,
		'text-ada-001':			0,
		'text-babbage-001':		0,
		'text-curie-001':		0,
		'text-davinci-001':		0,
		'text-davinci-002':		0,
	}

# Meanwhile, this dict will keep track of the cumulative expenditures
# in dollars for each engine.

global expenditures
expenditures = {
		'ada':					0,
		'babbage':				0,
		'curie':				0,
		'davinci':				0,
		'text-ada-001':			0,
		'text-babbage-001':		0,
		'text-curie-001':		0,
		'text-davinci-001':		0,
		'text-davinci-002':		0,
	}

# This global variable tracks the total cost in dollars across all engines.

global 			totalCost
totalCost 		= 0				# Initialize at stats load/save time.

# String containing a formatted multi-line table showing the current statistics.
global 			_statStr		
_statStr 		= ""		# Will be modified after processing a query.


#|==============================================================================
#|	Global objects.												  [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	_theTokenCounterCore	# A core connection for counting tokens.
_theTokenCounterCore = None		# Initially not yet created.

# IMPLEMENTATION NOTE: Since this API wrapper module may be used by multiple
# threads, we need to protect the global variables & objects above with a mutex.
# We can do this easily by using the 'threading' module's 'Lock' class.
# The 'Lock' class is a mutex that can be acquired and released.

import threading
global _lock
_lock = threading.Lock()

# NOTE: Any manipulation of the global variables above (in a way that needs 
# to be effectively atomic) must be protected with the '_lock' mutex. This 
# can be done via the 'with' statement:
#
#		with _lock:
#			...


#|==============================================================================
#|	Module public classes.										[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|---------------------------------------------------------------------------
	#|
	#|	gpt3.api.GPT3APIConfig							   [module public class]
	#|
	#|		This class provides an abstraction for a 'configuration' of
	#|		GPT-3 API parameter values.	 These can be modified dynamically
	#|		at runtime (i.e., in between different API calls).
	#|
	#|	Public interface:
	#|
	#|		conf = GPT3AIConfig(params)					  [instance constructor]
	#|
	#|			Create a new configuration object with specified parameters.
	#|			Others not provided revert to defaults.
	#|
	#|		conf.modify(params)								   [instance method]
	#|
	#|			Modify the specified parameters of the configuration.
	#|
	#|		str(inst)								   [special instance method]
	#|
	#|			Converts the configuration to a human-readable string
	#|			representation.
	#|
	#|	Special methods:
	#|
	#|		__init__	- Instance initializer.
	#|		__str__		- Display as a human-readable string.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3APIConfig:

	"""This class gathers together a set of parameter values for passing to the
		'completions' and/or 'completions/browser_stream' API calls."""

	#/--------------------------------------------------------------------------
	#|	Instance public data members for class GPT3APIConfig. (See API docs.)
	#|
	#|	API parameters:
	#|		.engineId			 [string]
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
	#|	Other attributes:
	#|		.name [string] - Human-readable name for this configuration.
	#|
	#\--------------------------------------------------------------------------

		#|----------------------------------------------------------------------
		#|	Initializer for class GPT3APIConfig.	   [special instance method]
		#|
		#|	Arguments:
		#|		
		#|		engineId											[string]
		#|
		#|			The name of the specific GPT-3 model/engine to use.
		#|			Choices as of 10/11/2020 are:  ada, ada-beta, babbage,
		#|			babbage-beta, content-filter-alpha-c4, curie, 
		#|			curie-beta, davinci, davinci-beta.	Earlier names
		#|			alphabetically are smaller models.	The default value
		#|			is davinci.
		#|
		#|		maxTokens											[integer]
		#|
		#|			The maximum number of tokens to return in the response.
		#|			Defaults to 42.
		#|
		#|		temperature											[number]
		#|
		#|			A floating-point number between 0 and 1 that roughly
		#|			indicates the degree of randomness in the response.
		#|			Default value: 0.5.
		#|
		#|		topP												[number]
		#|
		#|			A floating point number between 0 and 1 that restricts
		#|			answers to the top percentage of probability mass.
		#|			Do not use this and temperature in the same query.
		#|			Default value: None.
		#|			[NOTE: This parameter is yet supported by this module.]
		#|
		#|		nCompletions										[integer]
		#|
		#|			How many completions to return.	 Default value is 1.
		#|
		#|		stream												[boolean]
		#|
		#|			If true, then the result will be streamed back incre-
		#|			mentally as a sequence of server-sent events.
		#|			Default: False.
		#|			[NOTE: This parameter is yet supported by this module.
		#|			 Anyway, it is only useful for very large responses.]
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
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(inst, 
					engineId:str=DEF_ENGINE,	maxTokens:int=DEF_TOKENS, 
					temperature:float=DEF_TEMP, topP:float=None, 
					nCompletions:int=1,			stream:bool=False,
					logProbs:int=None,			echo:bool=False, 
					stop=DEF_STOP,				presPen:float=0, 
					freqPen:float=0,			bestOf:int=None,
					name=None):

		"""Initialize a GPT-3 API configuration, reverting to
			default values for any un-supplied parameters."""
					
		inst.engineId			= engineId
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
		
		inst.name				= name
	
	#__/ End instance initializer for class GPT3APIConfig,
	
	
		#|----------------------------------------------------------------------
		#|	.modify(params)								[public instance method]
		#|
		#|		Modify the specified parameters of the configuration to
		#|		the given values.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def modify(self, 
				engineId:str=None,		maxTokens:int=None, 
				temperature:float=None, topP:float=None, 
				nCompletions:int=None,	stream:bool=None,	
				logProbs:int=None,		echo:bool=None,			
				stop=None,				presPen:float=None, 
				freqPen:float=None,		bestOf:int=None):

		"""Modify one or more parameter values in the configuration."""
		
		if engineId		!= None:	self.engineId			= engineId
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

	
		#|----------------------------------------------------------------------
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
		# Note: .stop is printed using repr() in order to show the 
		# escape codes for any special characters.

#__/ End class GPT3APIConfig.


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
	
#|------------------------------------------------------------------------------
#|	gpt3.api.Completion									[module public class]
#|
#|		This class is a wrapper for the completion data structure 
#|		returned by the underlying GPT-3 API.  The constructor calls
#|		the API to create this structure.  Various properties allow
#|		easy access to information contained in the structure.
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
#|			Creates a Completion object wrapping the given 
#|			completion structure, previously generated.
#|
#|		text = compl.text
#|
#|			Returns the text of the completion as a single string.
#|
#|		nTok = compl.nTokens
#|
#|			Returns the total number of tokens in the completion.
#|			(Note that this property only works if the core had
#|			'logprobs=0' at the time that the completion was 
#|			generated.)
#|
#|		promptLen = compl.promptLen
#|
#|			Returns the length of the prompt in tokens. Note that 
#|			this property only works if the core had 'echo=True' 
#|			and 'logprobs=0' set at the time that the completion 
#|			was generated.
#|		
#|		complLen = compl.resultLen
#|
#|			Returns the length of the result (not including the 
#|			prompt) in tokens. Note that this property only works
#|			if 'logprobs=0' and is only useful if 'echo=True'
#|			since otherwise you could just use .nTokens.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Completion:

	"""An instance of this class represents a result returned from the
		GPT-3 API's completion creation call."""

	#/--------------------------------------------------------------------------
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
	#\--------------------------------------------------------------------------

	#|--------------------------------------------------------------------------
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
	

		#|----------------------------------------------------------------------
		#| .text									[public instance property]
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
		return ''.join(self.complStruct['choices'][0]['text'])
	
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
		return self.complStruct['choices'][0]['finish_reason']

		#|----------------------------------------------------------------------
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
				
		return len(self.complStruct['choices'][0]['logprobs']['tokens'])

	#__/ End of class gpt3.api.Completion's .nTokens property.


		#|----------------------------------------------------------------------
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
			
		text_offsets = self.complStruct['choices'][0]['logprobs']['text_offset']

			# We could make this more efficient by doing a binary
			# search, but it's probably overkill at the moment.
		
		for tok_index in range(0, len(text_offsets)):
			if text_offsets[tok_index] > pos:
				return tok_index-1
				
		return len(text_offsets)-1
			# If we get here, we're at the end of the text.
			# Return the last token index.
	
	#__/ End of class gpt3.api.Completion's .textPosToTokIndex method.


		#|----------------------------------------------------------------------
		#| ._createComplStruct(apiArgs)				   [private instance method]
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

		# This decorator performs automatic exponential backoff on REST failures.
	@backoff.on_exception(backoff.expo,
						  (openai.error.APIError))
						  
	def _createComplStruct(self, apiArgs, minQueryToks:int=DEF_TOKENS):
			# By default, don't accept shortening the space for the response to less than 42 tokens.
	
		"""Private instance method to retrieve a completion from the
			core API, with automatic exponential backoff and retry."""
			
		if minQueryToks is None:		# Just in case caller explicitly sets this to None,
			minQueryToks = DEF_TOKENS	# revert back to the default of 42 tokens.

		# If the core is not set, we can't do anything.
		if self.core == None:
			_logger.error("ERROR: completion._createComplStruct(): Core not available.")
			return None
			
		# The below code needs to be wrapped in the module's mutex lock, because
		# it manipulates the global record of API usage statistics, and this is
		# not thread-safe unless we make it atomic by grabbing the lock.

		with _lock:

			# If the usage statistics file hasn't been loaded already, do it now.
			if not _statsLoaded:
				loadStats()

			# This measures the length of the prompt in tokens, and updates
			# the global record of API usage statistics accordingly.
			self._accountForInput(apiArgs)
				# Note: The global variable _inputLength is updated by this method.

			# Retrieve the engine's receptive field size; this is the maximum number
			# of tokens that can be accommodated in the query + response together.
			fieldSize = _get_field_size(self.core.conf.engineId)

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
				querySpace = fieldSize - _inputLength

					# If there isn't enough space left even for our minimum result,
					# then we need to raise an exception, because whoever prepared
					# our prompt made it too large for this engine.

				if querySpace < minQueryToks:

						# Calculate the effective maximum prompt length, in tokens.
					effMax = fieldSize - minQueryToks

					_logger.warn(f"[GPT-3 API] Prompt length of {_inputLength} exceeds"
								 f" our effective maximum of {effMax}. Requesting field shrink.")

					e = PromptTooLargeException(_inputLength, effMax)
					raise e		# Complain to our caller hierarchy.

					# If we get here, we have enough space for our minimum result length,
					# so we can shrink the maximum result length accordingly.
				origMax = apiArgs['max_tokens']	# Save the original value.
				apiArgs['max_tokens'] = maxTok = fieldSize - _inputLength

				_logger.warn(f"[GPT-3 API] Trimmed max_tokens from {origMax} to {maxTok}.")

			# If we get here, we know we have enough space for our query + result,
			# so we can proceed with the request to the actual underlying API.
			complStruct = openai.Completion.create(**apiArgs)

			# This measures the length of the response in tokens, and updates
			# the global record of API usage statistics accordingly.			
			self._accountForOutput(apiArgs['engine'], complStruct)

			# This updates the cost data and the human-readable table of API
			# usage statistics, and saves the updated data to the _statsFile.
			saveStats()

		return complStruct		# Return the low-level completion data structure.
			# Note, this is the actual data structure that the completion object 
			# uses to populate itself.
			
	#__/ End of class gpt3.api.Completion's ._createComplStruct method.


	# Make these regular functions?
	
	def _accountForInput(self, apiArgs):

		"""This method measures the number of tokens in the prompt, and
			updates the global record of input tokens processed by the API."""
		
			# NOTE: It's dangerous to make _inputLength a global variable,
			# because it's possible that multiple threads will interleave
			# their processing of different queries. To be safe, DO NOT 
			# CALL THIS METHOD unless you have the module's mutex _lock 
			# acquired.

		global _inputLength

		engine = apiArgs['engine']
		prompt = apiArgs['prompt']

			# This function counts the number of tokens in the prompt
			# without having to do an API call (since calls cost $$).
		nToks = local_countTokens(prompt)

		_inputLength = nToks

		_logger.debug(f"Counted {nToks} tokens in input text [{prompt}]")

			# Update the global record of API usage statistics.
		inputToks[engine] = inputToks[engine] + nToks
	
	#__/ End of class gpt3.api.Completion's ._accountForInput method.


	def _accountForOutput(self, engine, complStruct):

		"""This method measures the number of tokens in the response, and
			updates the global record of output tokens processed by the API."""

		# NOTE: We can't just use the .text property of the completion
		# object, because we call this method from the initializer,
		# before the completion object has been fully initialized.

		text = ''.join(complStruct['choices'][0]['text'])
			# This syntax concatenates the list of strings returned by
			# the underlying API together into a single string.

			# This function counts the number of tokens in the response
			# without having to do an API call (since calls cost $$).
		nToks = local_countTokens(text)

		_logger.debug(f"Counted {nToks} tokens in output text [{text}].")

			# Update the global record of API usage statistics.
		outputToks[engine] = outputToks[engine] + nToks

	#__/ End of class gpt3.api.Completion's ._accountForOutput method.

#__/ End class Completion.


	#|--------------------------------------------------------------------------
	#|	
	#|	gpt3.api.GPT3Core								  [module public class]
	#|
	#|		This class abstracts a connection to the core GPT-3 system.	 
	#|		An instance of this class remembers its API configuration 
	#|		options.
	#|
	#|	Public interface:
	#|
	#|		.conf									[instance property]
	#|
	#|			Current API configuration of this core connection.
	#|
	#|		.adjustConf(params)						[instance method]
	#|
	#|			Modify one or more API parameters of the connection.
	#|
	#|		.genCompletion(prompt)					[instance method]
	#|
	#|			Generate a completion object from the given prompt.
	#|
	#|		.genString(prompt)						[instance method]
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

	#|--------------------------------------------------------------------------
	#|	Instance private data members for class GPT3Core.
	#|
	#|		._configuration	[GPT3APIConfig]		- Current API configuration.
	#|
	#|--------------------------------------------------------------------------

		#|----------------------------------------------------------------------
		#| Initializer for class GPT3Core.
		#|
		#|	USAGE:
		#|
		#|		core = GPT3Core()			# Uses default parameter values.
		#|		core = GPT3Core(config)		# Use this GPT3APIConfig object.
		#|		core = GPT3Core(params)		# List of keyword arguments.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(inst, *args, **kwargs):

			# If keyword arg 'config=' is present, use that as the config.
		
		if 'config' in kwargs:
			config = kwargs['config']
		else:
			config = None

			# Otherwise, if the first argument is a GPT3APIConfig, use that as the config.
	
		if config == None and len(args) > 0:
			if args[0] != None and isinstance(args[0],GPT3APIConfig):
				config = args[0]

			# If no config was provided, then create one from the arguments.
			# (In future, this should be changed to otherwise modify the provided
			# config based on the remaining arguments.)

		if config == None:
			config = GPT3APIConfig(*args, **kwargs)

		_logger.info("Creating new GPT3Core connection with configuration:\n" + str(config))

		inst._configuration = config		# Remember our configuration.
	
	#__/ End GPT3Core instance initializer.


		#|----------------------------------------------------------------------
		#|	.conf									[instance public property]
		#|
		#|		Returns the API configuration object (instance of class
		#|		GPT3AIConfig) that is associated with this connection to
		#|		the core GPT-3 system.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@property
	def conf(self):
		"""Get our current API configuration."""
		return self._configuration


		#|----------------------------------------------------------------------
		#|	.adjustConf(params)						[instance public method]
		#|
		#|		Adjusts the API parameter values of this connection to 
		#|		the core GPT-3 system as specified by the argument list.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def adjustConf(self, *args, **kwargs):
		"""Adjust the API configuration as specified."""
		self.conf.modify(*args, **kwargs)


		# Generate the argument list for calling the core API.
	def genArgs(self, prompt=None):
   
		kwargs = dict() 	# Initially empty dict for building up argument list.
		
		conf = self.conf	# Get our current configuration.

		kwargs['engine'] = conf.engineId	# This API arg. is required. Can't skip it.
				
		# Note here we have to match the exact keyword argument names supported by OpenAI's API.

		if prompt					!= None:	kwargs['prompt']			= prompt
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
	
	def genString(self, prompt):
		"""Generate a single completion string for the given prompt."""
		resultCompletion = self.genCompletion(prompt)
		text = resultCompletion.text
		_logger.debug("[GPT-3/API] Server returned result string: [" + text + ']')
		return text
	#__/ End instance method GPT3Core.genString().

#__/ End class GPT3Core.


#|==============================================================================
#| Module object initialization.								[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# This object represents an API connection to the GPT-3 core
	# system that is used for counting tokens.  It is not created
	# unless/until the GPT3Core.countTokens() method is called.

_theTokenCounterCore = None		# Don't create this until needed.
#_theTokenCounterCore = GPT3Core(engineId='ada', echo=True, maxTokens=0, logProbs=0)
	# This connection provides functionality needed to count tokens.
	# Note we use the 'ada' engine because it is cheapest ($0.80/1M tokens).


#|==============================================================================
#| Module function definitions.									[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def statsPathname():

	"""Constructs and returns the pathname to the api-stats.json file."""

	global _aiPath

		#----------------------------------------------------------
		# First, get the AI persona configuration, because it 
		# contains key information we need, such as the location
		# of the AI's data directory.

	aiConf = TheAIPersonaConfig()
		# Note this retrieves the singleton instance 
		# of the TheAIPersonaConfig class.

		#------------------------------------------------------
		# Next, get the location of the AI's data directory,
		# which is in the AI persona configuration object.
				
	aiDataDir = aiConf.aiDataDir

	_aiPath = aiDataDir
		
	_logger.debug(f"Got AI data directory = {aiDataDir}.")

		#-----------------------------------------------------
		# Next, we need to get the name of the stats json file
		# (relative to that directory). At the moment, this
		# comes from a module constant, defined above.
				
	statsFilename = _STATS_FILENAME
		
		#------------------------------------------------------
		# Next, we need to construct the full pathname of the
		# API statistics JSON file.
		
	statsPathname = path.join(aiDataDir, statsFilename)
		
		#-------------------------
		# Return it to the caller.

	return statsPathname

#__/ End module function statsPathname().


def textPath():
	"""Constructs and returns the pathname to the text file to store the API stats table."""
	return path.join(_aiPath, 'api-stats.txt')


# NOTE: This function is not currently used. It is here for future reference.
# We current prefer to use the local_countTokens() function, which is imported
# from the tokenizer/tokenizer.py module.

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

#__/ End module function countTokens().


def loadStatsIfNeeded():

	"""If the stats file hasn't been loaded from the filesystem yet,
		this loads it."""

	if not _statsLoaded:
		loadStats()

#__/ End module function loadStatsIfNeeded().


def loadStats():

	"""Loads the api-stats.json file from the AI's data directory."""

	global _statsLoaded, inputToks, outputToks, expenditures, totalCost

		# This constructs the full filesystem pathname to the stats file.
	statsPath = statsPathname()

	try:
		with open(statsPath) as inFile:

			stats 			= json.load(inFile)

			inputToks 		= stats['input-tokens']
			outputToks 		= stats['output-tokens']
			expenditures 	= stats['expenditures']
			totalCost 		= stats['total-cost']
		
		#_logger.normal(f"Loaded API usage stats from {statsPath}: \n{pformat(stats, width=25)}")

	# Ignore file doesn't exist errors.
	except:
		_logger.warn(f"Couldn't open API usage statistics file {statsPath}--it might not exist yet.")
		pass

	finally:
		_statsLoaded = True		# Hey, we tried at least!

	displayStats()

#__/ End module function loadStats().


def statLine(line):

	"""This quick-and-dirty utility method saves a line of
		the API statistics table to several places."""

	global _statStr

		# Log this line as an INFO-level log message.
	_logger.info(line)
	
		# Append this line to the api-stats.txt file.
	print(line, file=_statFile)

		# Also accumulate it in this global string.
	_statStr = _statStr + line + '\n'

#__/ End module function statLine().


def stats():
	"""After using the API this returns a human-readable table of usage statistics."""
	return _statStr


def displayStats():

	"""Displays usage statistics in an easily-readable format.
		Also saves them to a file api-stats.txt."""

	global _statFile, _statStr

	_statStr = ""

	with open(textPath(), 'w') as _statFile:

		# NOTE: We may need to widen some of the columns in this table
		#  if the contents start to overflow.

		statLine("")
		statLine("                      Token Counts")
		statLine("                 ~~~~~~~~~~~~~~~~~~~~~~~          ")
		statLine("Engine Name      Input   Output  Total    USD Cost")
		statLine("================ ======= ======= ======= =========")
		
		# Cumulative input, output, and total token counts.
		cumIn = cumOut = cumTot = 0
		
		# Generate a table row for each engine.
		for engine in _ENGINE_NAMES:
			
			engStr 	= "%16s" % engine

			inToks 	= inputToks[engine]
			outToks = outputToks[engine]
			total 	= inToks + outToks
	
			inTokStr  = "%7d" % inToks
			outTokStr = "%7d" % outToks
			totStr 	  = "%7d" % total
	
			cost = "$%8.4f" % expenditures[engine]
	
			statLine(f"{engStr} {inTokStr} {outTokStr} {totStr} {cost}")
	
			cumIn  = cumIn  + inToks
			cumOut = cumOut + outToks
			cumTot = cumTot + total
		
		#__/ End loop over engine names.
	
		# Generate a table row for the accumulated totals.
		cumInStr  = "%7d" % cumIn
		cumOutStr = "%7d" % cumOut
		cumTotStr = "%7d" % cumTot
	
		totStr = "$%8.4f" % totalCost
	
		statLine( "~~~~~~~~~~~~~~~~ ~~~~~~~ ~~~~~~~ ~~~~~~~ ~~~~~~~~~")
		statLine(f"TOTALS:          {cumInStr} {cumOutStr} {cumTotStr} {totStr}")
		statLine("")
	
	#__/ End with statement.

#__/ End module function displayStats().


def saveStats():

	"""Saves cumulative API usage statistics to the api-stats.json file
		in the AI's data directory."""

	global expenditures, totalCost

		# This constructs the full filesystem pathname to the stats file.
	statsPath = statsPathname()

	with open(statsPath, 'w') as outFile:

		(costs, dollars) = recalcDollars()

		expenditures = costs
		totalCost = dollars

		stats = {
				'input-tokens': inputToks,
				'output-tokens': outputToks,
				'expenditures': costs,
				'total-cost': dollars
			}

		
		_logger.debug(f"Saving API usage stats to {statsPath}: \n{pformat(stats, width=25)}")

		json.dump(stats, outFile)

			# Pretty-print it to the file.
		#pprint(stats, width=25, stream=outFile)
	
	#__/ End with statement.

	displayStats()

#__/ End module function saveStats().


def recalcDollars():

	"""This recalculates per-engine and total dollar costs
		from the per-engine token counts."""

	costs = dict()	# This is a dictionary mapping engine names to cumulative costs (in dollars).
	dollars = 0		# Total cost of all API calls, in dollars.
	for engine in _ENGINE_NAMES:
		nToks = inputToks[engine] + outputToks[engine]	# Total number of tokens used.
		engCost = (nToks/1000) * _get_price(engine)		# Price is per 1000 tokens.
		costs[engine] = engCost
		dollars = dollars + engCost
	#__/ End loop over engine names.
		
	return (costs, dollars)

#__/ End module function recalcDollars().


#|==============================================================================
#| Module main load-time execution.								  [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# We now postpone loading the API usage stats till they are first needed.
#loadStats()


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|	END FILE:	gpt3/api.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
