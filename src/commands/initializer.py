#|==============================================================================
#|                   TOP OF FILE:    commands/initializer.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:      commands/initializer.py       	[Python module source file]

    IN PACKAGE:		commands
	MODULE NAME:    commands.initializer
    FULL PATH:      $GIT_ROOT/GLaDOS/src/commands/initializer.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.commands (command interface component)


	MODULE DESCRIPTION:
	-------------------

		This module initializes the GLaDOS command interface. This is the
		interface that allows the AI to type commands to the GLaDOS system
		and have them be executed by the system.
		
		The command interface is organized into "command modules" associated
		with specific facilities or processes within the GLaDOS system.  New
		command modules can be added dynamically into the interface.  In the
		main loop of the system, when the A.I. generates a text event, it is
		parsed to see if it matches a command template, and if so, then 
		control is dispatched to an appropriate command handler.

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------

    #|==========================================================================
    #|
    #|   1. Module imports.                                [module code section]
    #|
    #|          Load and import names of (and/or names from) various
    #|          other python modules and pacakges for use from within
    #|          the present module.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|  1.1. Imports of standard python modules.    [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from os		import	path  	# Manipulate filesystem path strings.
import re					# Standard regular expression facility.

        #|======================================================================
        #|  1.2. Imports of custom application modules. [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|  The following modules, although custom, are generic utilities,
			#|  not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.  (This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster	import getComponentLogger

	# Go ahead and create or access the logger for this module.

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)    			# Create the component logger.


    #|==========================================================================
    #|
    #|   Globals					    						[code section]
    #|
    #|      Declare and/or define various global variables and
    #|      constants.  Top-level global declarations are not
    #|      strictly required, but they serve to verify that
    #|      these names were not previously used, and also
    #|      serve as documentation.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|
        #|  Special globals.                              	[code subsection]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global  __all__         # List of public symbols exported by this module.
__all__ = [
	'Command',		  	# Class for a specific command type.
	'Commands',			# Special container class for a set of commands to allow fast lookup.
	'CommandModule',	# A CommandModule is a set of commands associated with a specific facility.
	'CommandModules',	# Container class for a set of currently-loaded command modules.
	'CommandInterface',	# Class representing the entire command interface for a GLaDOS system instance.
	'commandInterface',	# Module object which is the most recently created command interface.
	'CommandInterfaceInitializer',	# Initializer class to initialize the whole command facility.
	]


		#|======================================================================
		#|	
		#|	Private globals.									[code section]
		#|
		#|		These globals are not supposed to be accessed from 
		#|		outside of the present module.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
global _DEFAULT_COMMAND_REGEX		# Default regular expression for parsing command strings.

	#/---------------------------------------------------------------------------
	#| What follows is a standard, simple command line format, consisting of a 
	#| single alphanumeric command identifier, separated by whitespace from
	#| an optional one-line argument list which extends up to (but not including)
	#| the next newline. The command identifier and argument list are captured.

_DEFAULT_COMMAND_REGEX = '^/([a-zA-Z_]\w*)(?:\s+(\S.*)?)?$'
	# This means: 
	#	(1) Beginning of string.
	#	(2) A single slash character ('/').
	#	(3) A command identifier consisting of:
	#			(a) A single alphabetic character (upper- or lowercase A-Z) or underscore.
	#			(b) Zero or more word characters (alphabetic, numeric, or underscore).
	#	(4) An optional 'rest of command line', consisting of:
	#			(a) One or more whitespace characters, to separate the command identifier from the argument list (if present).
	#			(b) An optional 'argument list', consisting of:
	#					(i) One non-whitespace character.
	#					(ii) Zero or more non-newline characters.
	#	(5) The end of the line, or the end of the string.


        #|======================================================================
        #|
        #|  Public globals.                              		[code section]
        #|
        #|      These globals are specific to the present module
        #|      and exported publicly to other modules that use it.
        #|
		#|      User modules should do "from appdefs import *"
		#|      to get immediate copies of these globals.
		#|
		#|      If users wish to modify these globals, they must also
		#|      do "import appdefs" and then "appdefs.<global> = ..."
		#|      (Warning: This will not affect the values of these
		#|      globals seen by other modules that have already
		#|      imported this module!)
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global commandInterface		# The most recently created CommandInterface instance.
commandInterface = None		# None created yet at initial import time.


	#|==========================================================================
	#|
	#|	Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class CommandModule: pass	# Forward declaration.

class Command:

	"""
		An object of this class represents a specific type of command.
		A command type has an associated symbolic name (identifier).
		It also has a command format, which is a regular expression used
		to parse the command text.  Normally this consists of a command
		escape character like '/' to denote that this text constitutes a
		command to the GLaDOS system, followed by the command name, 
		followed by whitespace and the command's parameters.  However,
		divergenses from this standard format are possible.
																			"""

	def Command(self, name:str=None, format:re=_DEFAULT_COMMAND_REGEX, cm:CommandModule=None):
		
		"""Instance initializer for the Command class."""
	

# commands/initializer.py

# Classes:
#	
#	* Command
#	* CommandList
#	* CommandModule
#	* CommandModules
#	* CommandInterface
#	* CommandInterfaceInitializer
#


