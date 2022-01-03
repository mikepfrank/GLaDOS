#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|				  TOP OF FILE:	  commands/commandInterface.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		commands/commandInterface.py	 [Python module source file]

	MODULE NAME:	commands.commandInterface
	IN PACKAGE:		commands
	FULL PATH:		$GIT_ROOT/GLaDOS/src/commands/commandInterface.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.commands (Command interface component)


	MODULE DESCRIPTION:
	-------------------

		This module initializes the GLaDOS command interface. This is the
		interface that allows the AI to type commands to the GLaDOS system
		and have them be executed by the system.
		
		The command interface is organized into "command modules" associated
		with specific facilities, processes, or apps within the GLaDOS system.	
		New command modules can be added dynamically into the interface.  In 
		the main loop of the system, when the A.I. generates a text event, it 
		is parsed to see if it matches a command template, and if so, then 
		control is dispatched to an appropriate command handler.

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#|==========================================================================
	#|
	#|	0. Module exports.								   [module code section]
	#|
	#|		Here we define the list of public names that are exported from
	#|		this module to any other modules that do
	#|
	#|					from commands.commandInterface import *
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__	# List of public symbols exported by this module.
__all__ = [

			#|~~~~~~~~~~
			#| Classes.

		'TheCommandInterface',	
			# Singleton class representing the entire command interface for the
			# current GLaDOS system instance.
			
		'CommandModules',
			# Container class for a set of currently-loaded command modules.
			
		'CommandModule',	
			# A CommandModule is a set of commands associated with a specific facility.
		
		'Commands',			
			# Special container class for a set of commands to allow fast lookup.
		
		'Command',		# Class for a specific named command type.

	]


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

from os					import	path			# Manipulate filesystem path strings.
from collections		import	OrderedDict		# Dictionary that maintains item order.
from collections.abc	import	Iterable		# Used in type hints.

import re					# Standard regular expression facility.


		#|======================================================================
		#|	1.2. Imports of optional python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|======================================================================
		#|	1.3. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton

			#|==================================================================
			#|	1.3.1. The following modules, although custom, are generic 
			#|		utilities, not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				#| 1.3.1.1. The logmaster module defines our logging framework.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.logmaster	import	getLoggerInfo	# Used just below.

	#----------------------------------------------------------
	# Go ahead and create or access the logger for this module,
	# and obtain the software component name for our package.

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	1.3.2. These modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	supervisor.action	import	Action_		# Abstract base class for actions.


	#|==========================================================================
	#|
	#|	 2. Globals										   [module code section]
	#|
	#|		Declare and/or define various global variables and
	#|		constants.	Note that top-level 'global' statements are
	#|		not strictly required, but they serve to verify that
	#|		these names were not previously used, and also serve as 
	#|		documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	
		#|	2.1. Private globals.						[module code subsection]
		#|
		#|		These globals are not supposed to be accessed from 
		#|		outside of the present module.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|--------------------------------------------------------------------------
	#|	_DEFAULT_COMMAND_REGEX			 [private module-level global constant]
	#|
	#|		This constant contains the standard default regular expression
	#|		that is used for parsing command lines.	 The normal format for 
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
		
		#|----------------------------------------------------------------------
		#| What follows is a standard, simple command line format, consisting 
		#| of a single alphanumeric command identifier, separated by whitespace 
		#| from an optional one-line argument list which extends up to (but not
		#| including) the next newline. The command identifier and argument 
		#| list are captured groups.

global _DEFAULT_COMMAND_REGEX	
	# This will be our default regular expression for parsing command strings.
	
_DEFAULT_COMMAND_REGEX = '^/([a-zA-Z_]\\w*)(?:\\s+(\\S.*)?)?$'
	#|
	#| This means: 
	#|
	#|	(1) '^' = Beginning of string.
	#|			[NOTE: Consider also allowing any junk before the '/'.]
	#|
	#|	(2) '/' = A single slash character ('/').
	#|
	#|	(3) '([a-zA-Z_]\\w*)' = (Group 1) A command identifier consisting of:
	#|
	#|			(a) '[a-zA-Z_]' = A single *alphabetic* character (upper- or
	#|					lowercase A-Z) or underscore.
	#|
	#|			(b) '\\w*' = Zero or more word characters (alphabetic, numeric, 
	#|					or underscore).
	#|
	#|	(4) '(?:\\s+(\\S.*)?)?' = An optional 'rest of command line', consisting of:
	#|
	#|			(a) '\\s+' = One or more whitespace characters, to separate the 
	#|					command identifier from the argument list (if present).
	#|
	#|			(b) '(\\S.*)?' = An optional 'argument list', consisting of:
	#|
	#|					(i) '\\S' = One non-whitespace character.
	#|					(ii) '.*' = Zero or more non-newline characters.
	#|
	#|	(5) '$' = The end of the line, or the end of the string.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#|==========================================================================
	#|
	#|	3. Class forward declarations.					   [module code section]
	#|
	#|		These are really only useful as documentation in type hints.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class	TheCommandInterface:	pass	# Singleton anchor for this module.
class	CommandModules:			pass	# A set of command modules.
class	CommandModule:			pass	# A pluggable command module.
class	Commands:				pass	# A list of commands.
class	Command:				pass	# A single command type.
class	SubCommand:				pass	# A special case of another command.

	#|==========================================================================
	#|
	#|	4. Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Command:

	"""commandInterface.Command									  [public class]
		
			An object of this class represents a specific type of command.
			A command type has an associated symbolic name (identifier).
			It also has a command format, which is a regular expression 
			used to parse the command text.	 Normally this consists of a 
			command escape character like '/' to denote that this text 
			constitutes a command to the GLaDOS system, followed by the 
			command name, followed by whitespace and the command's 
			argument list.	However, divergences from this standard format 
			are possible.
		
		Instance public data members:
		-----------------------------
			
			.name [str]		- 
			
				Symbolic name for this command pattern.
				
			.format [str]	- 
			
				Regex format string for parsing this command pattern.
				
			.unique [bool]	- 
			
				Boolean that is True if the format regex is supposed to 
				uniquely identify this particular command type.	 That is,
				matching command lines should not match any other command 
				types.
				
			.handler [callable]	- 
			
				Command execution handler.
				
			.cmdModule [CommandModule]	- 
			
				Command module to which this command is associated.
	"""

	def __init__(newCmd:Command,	# Newly-created command object to be initialized.
				name:str=None,		# Symbolic name of this command pattern.
				cmdFmt:str=None,	# Format string for parsing this command.
				unique:bool=False,		# True if format is supposed to be unique.
				handler:callable=None,		# Callable to execute the command.
				module:CommandModule=None	# Command module this command is in.
			):
		
		"""
			Instance initializer for the Command class.
		
				Arguments:
				----------
				
					name [string]	- A symbolic name (required). Converted to
										all-lowercase for indexing purposes.
					
					abbrev [string] - A shortened abbreviation for the command,
										intended to be unique in a given context.
										[NOT YET IMPLEMENTED; DELETE THIS?]
					
					cmdFmt [string]	- An 're' style regular expression format 
										string for parsing the command.	 If not 
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
					
					cmdModule [CommandModule] - The CommandModule instance that this
											command is associated with.	 This
											is optional.
											
																			"""
		
		cmd = newCmd	# Shorter name for the new command.
		
		# If command format is not provided, revert to the default pattern.
		if cmdFmt == None:
			cmdFmt = _DEFAULT_COMMAND_REGEX
			unique = False	# The default regex is most definitely NOT unique.
		
			# Store initializer arguments in instance attributes.
		
		cmd.name		= name
		cmd.cmdFmt		= cmdFmt
		cmd.unique		= unique
		cmd.handler		= handler
		cmd.cmdModule	= module
		
			# Automatically add this newly-created command to its command 
			# module (if known).
		
		if module != None:
			module.addCommand(cmd)
			
	#__/ End initializer for class Command.

#__/ End class Command.


class Subcommand(Command):

	"""A subcommand is a type of command that is really just a special
		case of a more general command. For example, in the Goals app,
		the command module includes a '/goal' command whose overall
		format descriptor looks something like this:

			/goal (add|change|delete|insert|move) [<N> [to <M>]] ["<desc>"]

		Each of the command words that may appear after '/goal' denotes
		a subcommand; for example, one of the subcommands is:

			/goal add ["<description>"]

		which is considered a special case of the '/goal' command.

		Detailed documentation for how to use commands and subcommands
		is provided by means of the Help system; although individual apps
		may also provide hints about their commands in their on-screen text.

	"""

	pass	# TODO: Finish subcommand implementation!

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Commands:

	"""commandInterface.Commands								  [public class]
	
			This is a container class for an ordered list of commands
			(i.e., instances of the Command class).	 It facilitates fast 
			lookup of commands using their symbolic names.	It also 
			provides features for more general command lookup using trial 
			regular expression matching.  A constraint is enforced that 
			only one command having any given symbolic name can be stored, 
			to avoid confusion.
		
		
		Public instance methods:
		------------------------
			
			.addCommand(cmd:Command) -
				
				Adds the given command to the Commands list, at the end of 
				the list (i.e., lowest priority for matching purposes). Any
				existing command in the list with the same name is deleted.
				[TO DO]
			
			.lookupByName(name:str) -
				
				Return the command in the list having the given name, or 
				None if there is none with that name.
				
			.matches(text:str) -
				
				Returns an iterable containing all of the commands whose 
				regex's match the given text, in order.		
			
			.firstMatch(text:str) -
				
				Returns the first command in the list whose regex matches 
				the given text.
				
	"""
	
	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Private data members						  [class code documentation]
	#|	for class Commands: 
	#|	====================
	#|
	#|		Private instance data members:
	#|		------------------------------
	#|	
	#|			._cmdOD [OrderedDictionary]	-
	#|		
	#|					Ordered dictionary of commands, sorted in 
	#|					order from highest to lowest priority for 
	#|					regex matching purposes.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	
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
		inst._cmdOD[cmd.name.casefold()] = cmd
			# Convert name to lowercase for indexing purposes.
			# .casefold() is an interlingual equivalent of .lower()

	# TODO: Implement more methods.

#__/ End class Commands.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CommandModule:

	def __init__(self):

		self._commands = Commands()
			# This gives this command module an initially-empty command set.

			# Command modules are initially inactive until activated.
		self._isActive = False			
		
		# NOTE: The below causes a serious circularity problem, which is that
		# if the constructor for a given system tries to construct its command
		# module, and that command module tries to populate itself, and the
		# populate method creates commands that try to reference the singleton
		# for the given system, this fails because the system hasn't even 
		# finished being initialized yet. Annoying workarounds are needed.
		# Need a better design.

			# Go ahead and populate this command module with its commands.
		self.populate()

	def addCommand(self, cmd):
		self._commands.addCommand(cmd)

	def populate(self):

		"""To "populate" a command module means to flesh it out by adding
			to it all the individual commands it is supposed to contain.
			Subclasses should implement this virtual method."""

		pass	# Need to implement this for particular subclasses.

	def menuStr(self):
		"""
			Returns a string that can serve as a 'menu'
			listing commands present in this module. The
			default representation is:
			
				"/Word1 /Word2 ... /Wordn"
			
			where Word1, etc. are the command words.
		"""
		return "(menu not implemented)"		# TODO: Implement this eventually.
	
	def activate(self):
		"""
			To 'activate' a command module means to include
			all of its commands in the currently active global
			command index.
		"""
		self._isActive = True		# Need to do more work here.
		
	def deactivate(self):
		"""
			To 'deactivate' a command module means to remove
			all of its commands from the currently active global
			command index.
		"""
		self._isActive = False		# Need to do more work here.

#__/ End public class commandInterface.CommandModule.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CommandModules:

	"""An instance of this class represents a collection of
		command modules. It is kept ordered for the simple
		reason that in case of a collision between command
		names between modules, the one in the module that
		was installed first takes priority."""
			# Is this a good policy? The idea is so if a developer accidentally
			# introduces a name collision in a app module with a more fundamental 
			# system module, he will notice it right away during testing.
		
	def __init__(self):
		self._commandModuleList = []

	def addModule(thisCmdMods:CommandModules, module:CommandModule):
		"""Add the given command module to this list of command modules."""
		cmdMods = thisCmdMods
		cmdMods._commandModuleList.append(module)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class TheCommandInterface:		# Singleton class for the command interface subsystem.

	"""
		commandInterface.TheCommandInterface			[public singleton class]
		====================================
		
			This is a singleton class; its sole instance represents the 
			entire command interface subsystem of the GLaDOS server system.	 
			The command interface maintains a set of pluggable command 
			modules, as well as an index of all commands that are presently 
			actively accessible within the system.
		
		
		Public data members:
		--------------------
			
			.commandModules [CommandModules]	-
				
				This data object contains the list of command modules that 
				are presently installed in this command interface.	Some 
				may be active, some inactive.  Modules installed earlier 
				take priority over ones installed later.
	"""
	
	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Private data members for					  [class code documentation]
	#|	class TheCommandInterface: 
	#|	===========================
	#|
	#|		Private instance data members:
	#|		------------------------------
	#|	
	#|			._activeCommands [Commands]	-
	#|		
	#|				This data object contains an index of all commands
	#|				that are presently actively supported in this command
	#|				interface. (The union of all commands in all of 
	#|				the active command modules.) In case of conflicts 
	#|				between command modules, the module that was installed
	#|				earliest takes precedence (that is, existing commands
	#|				are not displaced by newer modules).
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	
	
	def __init__(self):
	
		"""
			commandInterface.__init__()				   [special instance method]
		
				This is the singleton instance initializer for the 
				TheCommandInterface class.	Note that because this class
				is a singleton class, this will only be called once,
				to initialize the first and only instance of the class.
		
				The functionality of this method is simply to create
				an initially-empty command interface (with no command
				modules initially loaded yet).	Creates a command list and 
				command module set, both initially empty.
		"""
		
			# Create an initially empty set of installed command modules.
		
		self.commandModules = CommandModules()
		
			# Create an initially empty list of actively supported commands.
		
		self._activeCommands = Commands()
	
	#__/ End singleton instance initializer for class TheCommandInterface.


	def installModule(self, cmdModule):
	
		"""Plugs the given command module into this command interface."""
		
		self.commandModules.addModule(cmdModule)

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

	
#__/ End public singleton class commandInterface.TheCommandInterface.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|				  END OF FILE:	 commands/commandInterface.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
