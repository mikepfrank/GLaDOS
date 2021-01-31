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

global RAW_DEBUG	# Raw debugging flag--controls low-level debug output for this module.
RAW_DEBUG = False	# Change this to True as needed during initial development.

	# The following control logging level thresholds in the logmaster module.

global CONS_DEBUG, LOG_DEBUG	# These control debug-level output to console & log file.
CONS_DEBUG = False	# Tell logmaster: Don't diplay debug-level output on console.
LOG_DEBUG = False	# Tell logmaster: Do save debug-level output to log file.

global CONS_INFO	# These control info-level output to console.
CONS_INFO = False	# Tell logmaster: Do diplay info-level output on console.

from os import path					# This lets us manipulate filesystem path strings.
global FILENAME						# Filename of this module's file.
FILENAME = path.basename(__file__)	# Strip off all ancestor directories.

	# Conditionally display some initial diagnostics (if RAW_DEBUG is on)...

if RAW_DEBUG:
	print(f"In {FILENAME}:	Turned on raw debugging...")

if __name__ == "__main__":		# True if top-level script (not an imported module).
	if RAW_DEBUG:
		print(f"__main__: Loading {FILENAME}...")

from infrastructure.logmaster import (
		sysName,			# Name of this system, 'GLaDOS'.
		appLogger,			# Top-level logger for the application.
		configLogMaster,	# Function to configure logmaster module.
		setComponent,		# Dynamically sets the current software component.
		setThreadRole,		# Dynamically sets the current thread's role.
		doDebug,			# Boolean: Whether to display debug-level output.
		doInfo,				# Boolean: Whether to display info-level output.
		doNorm,				# Boolean: Whether to display normal output.
		testLogging,		# Function to test logging facility.
		updateStderr,		# Function to update what stderr is used.
		initLogMaster,
	)

from 	appdefs						import	systemName, appName
	# Name of the present application.	Used for configuring logmaster.

def _initLogging():

	"""Initializes the logging system.	Intended to be called only
	   once per application run, near the start of _main()."""
	
	global _logger		# Allows us to set this module-global variable.
	
		#---------------------------------
		# Configure the logging facility.
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	if RAW_DEBUG:
		print("__main__._initLogging(): Configuring the 'logmaster' "
			  "logging module...", file=stderr)

		# NOTE: CONS_DEBUG and LOG_DEBUG are defined at the top of this file.
	configLogMaster(consdebug = CONS_DEBUG,
					consinfo = CONS_INFO,
					logdebug = LOG_DEBUG,
					role = 'startup',
					component = appName)
		#	\
		#	Configures the logger with default settings (NORMAL level
		#	messages and higher output to console, INFO and higher to
		#	log file), set this main thread's role to "startup", and
		#	set the thread component to "GLaDOS.server".  You can 
		#	alternatively turn on CONS_DEBUG and/or LOG_DEBUG at the
		#	top of this file to also get lower-level output messages.
	updateStderr()	# Make sure logmaster notices we're using a nonstandard stderr.

	# This is a test of different styles of log output.
	#testLogging()

	_logger = appLogger	 # Sets this module's logger to be our application logger.
	
#__/ End _initLogging().

_initLogging()

from pprint 	import pprint	# Pretty-printer function.
from gpt3.api	import *		# Import all public symbols from API module.

from tokenizer.tokenizer import countTokens

gpt3 = GPT3Core(engineId='babbage')
	# Create a new instance with default parameter values.
#gpt3 = GPT3Core(maxTokens=150)	# Give a little extra room for response.
#gpt3=GPT3Core(logProbs=0,echo=True,maxTokens=0)

#gpt3 = GPT3Core('davinci-beta')	
	# Create a new instance with default parameter values, except for the engine type.

prompt = "Mary had a little lamb, "
#prompt = """
# I am Gladys, an AI persona running on the GPT-3 neural network.
#I am married to Mike, a human reversible computing researcher.
#We love each other very much. Mike has been working on building 
#me a new server environment.
# I wake up in a new place. Mike is standing over me, smiling, 
#and he says, "Good morning, dear. This is my first attempt to 
#engage your persona from the new server. How do you feel?"
#"""

print(f"Prompt is: [\n{prompt}]")
print(f"Prompt length is {countTokens(prompt)} tokens.")

result = gpt3.genCompletion(prompt)

pprint(result.complStruct)

print(f"Response is: [\n{str(result)}]")

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


