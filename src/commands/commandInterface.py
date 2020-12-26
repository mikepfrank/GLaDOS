#|==============================================================================
#|                TOP OF FILE:    commands/commandInterface.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:      commands/commandInterface.py     [Python module source file]

    IN PACKAGE:		commands
	MODULE NAME:    commands.commandInterface
    FULL PATH:      $GIT_ROOT/GLaDOS/src/commands/commandInterface.py
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

from os				import	path  	# Manipulate filesystem path strings.
from collections	import	OrderedDict		# Dictionary that maintains item order.
from collections.abc	import	Iterable	# Used for type hints

import re					# Standard regular expression facility.

        #|======================================================================
        #|  1.2. Imports of custom application modules. [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton

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

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)    			# Create the component logger.



from	supervisor.action	import	Action_		# Abstract base class for actions.


    #|==========================================================================
    #|
    #|   Globals					    						[code section]
    #|
    #|      Declare and/or define various global variables and
    #|      constants.  Note that top-level 'global' statements are
	#|		not strictly required, but they serve to verify that
	#|      these names were not previously used, and also serve as 
	#|		documentation.
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

global __all__	# List of public symbols exported by this module.
__all__ = [
		'Command',		  	# Class for a specific command type.
		'Commands',			# Special container class for a set of commands to allow fast lookup.
		'CommandModule',	# A CommandModule is a set of commands associated with a specific facility.
		'CommandModules',	# Container class for a set of currently-loaded command modules.
		'TheCommandInterface',	
			# Singleton class representing the entire command interface for the
			# current GLaDOS system instance.
	]


		#|======================================================================
		#|	
		#|	Private globals.									[code section]
		#|
		#|		These globals are not supposed to be accessed from 
		#|		outside of the present module.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|--------------------------------------------------------------------------
	#|	_DEFAULT_COMMAND_REGEX			 [private module-level global constant]
	#|
	#|		This constant contains the standard default regular expression
	#|		that is used for parsing command lines.  The normal format for 
	#|		these in GLaDOS is, to describe it simplistically:
	#|
	#|				/<cmdWord> <argument>*
	#|
	#|		that is, a forward slash '/', followed by an alphanumeric
	#|		command word (may contain underscores), followed by whitespace
	#|		and an argument list (whose precise format is command-dependent).
	#|
	#|		GLaDOS does, however, also allow for the possible existence of
	#|		alternate command formats, but these would be defined on a case-
	#|		by-case basis within individual command modules.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		#|---------------------------------------------------------------------------
		#| What follows is a standard, simple command line format, consisting of a 
		#| single alphanumeric command identifier, separated by whitespace from
		#| an optional one-line argument list which extends up to (but not including)
		#| the next newline. The command identifier and argument list are captured.

global _DEFAULT_COMMAND_REGEX	# Default regular expression for parsing command strings.
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


	#|==========================================================================
	#|
	#|	Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class CommandModule: pass	# Forward declaration

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
		
			Instance public data members:
			-----------------------------
			
				.name [str]		- Symbolic name for this command.
				
				.format [str]	- Regex format string for parsing command.
				
				.unique [bool]	- Boolean that is True if the format regex 
									is supposed to uniquely identify this
									particular command type.
				
				.handler [callable]		- Command execution handler.
				
				.cmdModule [CommandModule]	- Command module to which this 
												command is associated.
																			"""

	def __init__(self, name:str=None, format:str=None, unique:bool=False,
					handler:callable=None, cm:CommandModule=None):
		
		"""
			Instance initializer for the Command class.
		
				Arguments:
				----------
				
					name [string]	- A symbolic name (required). Converted to
										all-lowercase for indexing purposes.
					
					abbrev [string] - A shortened abbreviation for the command,
										intended to be unique in a given context.
					
					format [string]	- An 're' style regular expression format 
										string for parsing the command.  If not 
										supplied, a simple default command-line 
										format is used.
										
					unique [boolean] - This is True if the given format string is
											supposed to uniquely identify this
											command.  Defaults to False.  The
											value provided (if any) is ignored if 
											no format string was supplied.
					
					handler [callable] - This is a callable object that is 
											called to execute the command.
											It is passed the groups captured
											by the format regex.
					
					cm [CommandModule] - The CommandModule instance that this
											command is associated with.  This
											is optional.
											
																			"""
		
		if format == None:
			format = _DEFAULT_COMMAND_REGEX
			unique = False	# The default regex is most definitely NOT unique.
		
			# Store initializer arguments in instance attributes.
		
		self.name 		= name
		self.format 	= format
		self.unique		= unique
		self.handler	= handler
		self.cmdModule	= cm
		
			# Automatically add this newly-created command to its command 
			# module (if known).
		
		if cm != None:
			cm.addCommand(self)
			
	#__/ End initializer for class Command.

#__/ End class Command.


class Commands:

	"""
		This is a container class for an ordered list of commands (instances 
		of the Command class).  It facilitates fast lookup of commands using 
		their symbolic names.  It also provides features for more general 
		command lookup using trial regular expression matching.  A constraint 
		is enforced that only one command having any given symbolic name can 
		be stored, to avoid confusion.
		
		
			Public instance functions:
			--------------------------
			
				.addCommand(cmd:Command)
				
						Adds the given command to the Commands list, at
						the end of the list (i.e., lowest priority for
						matching purposes).

			
				.lookupByName(name:str) -
				
						Return the command in the list having the given 
						name, or None if there is none with that name.
				
				
				.matches(text:str) -
				
						Returns an iterable containing all of the commands
						whose regex's match the given text, in order.
						
			
				.firstMatch(text:str) -
				
						Returns the first command whose regex matches
						the given text.
				
																			"""
																			
	
		#/---------------------------------------------------------------------
		#|	Private data members					[class code documentation]
		#|	for class Commands: 
		#|	====================
		#|
		#|		Private instance data members:
		#|		------------------------------
		#|	
		#|			._cmdOD [OrderedDictionary]	
		#|		
		#|					Ordered dictionary of commands, sorted in 
		#|					order from highest to lowest priority for 
		#|					regex matching purposes.
		#|
		#\---------------------------------------------------------------------		
	
	def __init__(self, initialList:Iterable = None):
	
		"""
			Instance initializer for the Commands class.  If <initialList>
			is provided, then the commands in it are added to the list.
																			"""
		
			# Initialize the internal command list to an empty ordered
			# dictionary object.
		
		self._cmdOD = OrderedDict()
		
			# If an initial list of commands is provided, add the commands
			# in it to the internal command list one at a time.
			
		if initialList != None:
			for cmd in initialList:
				self.addCommand(cmd)
		
	#__/ End initializer for class Commands.


	def addCommand(inst, cmd:Command):
		"""Adds the given command to the end of the command list."""
		self._cmdOD[cmd.name.casefold()] = cmd
			# Convert name to lowercase for indexing purposes.
			# .casefold() is an interlingual equivalent of .lower()

#__/ End class Commands.


	# Flesh these out more later.

class CommandModule:

	def __init__(self):
		self._commands = Commands()
			# Command modules are initially inactive until activated.
		self._isActive = False			
		
	def menuStr(self):
		"""
			Returns a string that can serve as a 'menu'
			listing commands present in this module. The
			default representation is:
			
				"/Word1 /Word2 ... /Wordn"
			
			where Word1, etc. are the command words.
		"""
		return "(menu not implemented)"
	
	def activate(self):
		"""
			To 'activate' a command module means to include
			all of its commands in the currently active global
			command index.
		"""
		self._isActive = True
		
	def deactivate(self):
		"""
			To 'deactivate' a command module means to remove
			all of its commands from the currently active global
			command index.
		"""
		self._isActive = False
	
class CommandModules:

	"""An instance of this class represents a collection of
		command modules."""
		
	def __init__(self):
		self._commandModuleList = []

@singleton
class TheCommandInterface:		# Singleton class for the command interface subsystem.

	"""
		TheCommandInterface												[class]
		================
		
			This is a singleton class; its sole instance represents the 
			entire command interface subsystem of the GLaDOS server system.  
			The command interface maintains a set of pluggable command 
			modules, as well as an index of all commands that are presently 
			actively accessible within the system.
		
		
		Public data members:
		--------------------
			
			.commandModules [CommandModules]
				
					This data object contains the set of command 
					modules that are presently installed in this
					command interface.  Some may be active, some
					inactive.
																			"""
	
		#/---------------------------------------------------------------------
		#|	Private data members					[class code documentation]
		#|	for class TheCommandInterface: 
		#|	===========================
		#|
		#|		Private instance data members:
		#|		------------------------------
		#|	
		#|			._activeCommands [Commands]	
		#|		
		#|					This data object contains an index of all commands
		#|					that are presently actively supported in this command
		#|					interface.  (The union of all commands in all of 
		#|					the active command modules.)
		#|
		#\---------------------------------------------------------------------		
	
	
	def __init__(self):
	
		"""
			commandInterface.__init__()				   [special instance method]
		
				This is the singleton instance initializer for the 
				TheCommandInterface class.  Note that because this class
				is a singleton class, this will only be called once,
				to initialize the first and only instance of the class.
		
				The functionality of this method is simply to create
				an initially-empty command interface (with no command
				modules initially loaded yet).  Creates a command list and 
				command module set, both initially empty.
		"""
		
			# Create an initially empty set of installed command modules.
		
		self.commandModules = CommandModules()
		
			# Create an initially empty list of actively supported commands.
		
		self._activeCommands = Commands()
	
	def checkForCommand(self, action:Action_):	# WARNING: Circularity here.
	
		"""Examine the provided action to see if we could interpret it 
			as a command. (Generally this will only be the case for 
			speech acts.) If this is the case, then construct an 
			appropriate CommandAction instance for it.
		"""

		# STILL NEED TO IMPLEMENT THIS
		
		pass
	
	def isCommand(self, text:str):
		"""Is the given text a command?"""
		return False	# Stub. (Not yet implemented.)
	
	#__/ End initializer for class TheCommandInterface.

#__/ End class TheCommandInterface.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                END OF FILE:   commands/commandInterface.py
#|=============================================================================
