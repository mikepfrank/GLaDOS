#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|				  TOP OF FILE:	  commands/commandInterface.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""FILE NAME:		commands/commandInterface.py	 [Python module source file]

	MODULE NAME:	commands.commandInterface
	IN PACKAGE:		commands
	FULL PATH:		$GIT_ROOT/GLaDOS/src/commands/commandInterface.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.commands (Command interface component)


	MODULE DESCRIPTION:
	-------------------

		This module initializes the GLaDOS command interface. This is
		the interface that allows the AI to type commands to the
		GLaDOS system and have them be executed by the system.
		
		The command interface is organized into "command modules"
		associated with specific facilities, processes, or apps within
		the GLaDOS system.  New command modules can be added
		dynamically into the interface.  In the main loop of the
		system, when the A.I. generates a text event, it is parsed to
		see if it matches a command template, and if so, then control
		is dispatched to an appropriate command handler.

		Individual command modules can also be activated and
		deactivated.  This makes sense to help facilitate command name
		reuse between different apps.  For example, many different
		apps may provide a '/Next' command to page forward in their
		data.  But, we assume that only one app at a time has the
		command focus.  All apps that want to use commonplace command
		names (likely to have collisions) should isolate those
		commands into a "focus commands" module, which is only
		activated when that app has the command focus.  (Other app
		commands should only be activated when that app is running,
		except for the command to invoke an app, which could be
		provided by the 'Apps' app's command module, which may be
		considered to be always running.)

		Here are some additional details:

		1. The list of command modules in the system is ordered. The
			order corresponds to priority, where earlier-occurring
			modules (unless deactivated) take priority over
			later-occurring modules.

		2. Newly-added modules are added at the end of the list of
			modules, so are lower-priority than earlier modules. (So,
			for example, system commands take priority over apps that
			are loaded later.)  Once added, normally the order of
			modules is not changed.

		3. When a line of input is sent to the command interface,
			first we try to parse it with the generic default command
			regex, which attempts to extract a command identifier
			(alphanumeric + '_').  If one is found, we attempt to do
			command lookup (step 4); otherwise, we go to the generic
			command-matching procedure (see step 6 below).

		4. During command lookup, first we check to see if the given
			identifier is an exact match for an existing command name
			or names.  If so, we generate a list of all commands from
			all modules having that exact name, and then filter them
			down to the ones from active modules whose regexes match
			the input line.  If the first matching command has the
			unique=True attribute, and there are other matching
			commands, this tells us that we really should confirm with
			the user which command was intended.  Otherwise, just
			execute the command.

		5. If there's no exact match to the provided command
			identifier, we next generate a list of all command names
			having the provided identifier as a prefix, and we collect
			a list of all commands from all active modules having any
			of those names, sorted in module order, and then do the
			same filtering process from step 4 for that list.

		6. If and only if no command identifier was found, or neither
			direct lookup nor prefix lookup found any active/matching
			commands, then and only then do we go to generic command
			matching. This goes through the list of nonstandard format
			commands in the system, meaning ones that don't trigger on
			a '/<cmdname>' format pattern, attempting to match them
			against the input line.  Again, we pick the first matching
			one from an active module, and check its unique attribute,
			and prompt the user if unique=True but there were other
			commands that also matched.
			
		Some relevant methods to the above are:

			* commandInterface.obtainCommandList().


		NOTE: This module includes support for potentially matching
		command patterns even if they don't begin at the start of the
		line. This is only needed because the AI may occasionally make
		a mistake and write something like "I type '/Help' at the
		prompt." instead of just writing "/Help". We'd like to be able
		to detect such cases, and either go ahead and execute the
		command anyway, or at least, give the AI a helpful hint such
		as "To execute a command, please type it on a line by itself."

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
			# A CommandModule is a set of commands associated with a specific
			# facility or application within GLaDOS.
		
		'Commands',			
			# Special container class for a set of commands to allow fast lookup,
			# as well as ordering of commands. We use this both to store the
			# list of commands within an individual module, as well as the union
			# of all commands presently defined within the GLaDOS system. In the
			# event of a conflict between mutliple commands demanding uniqueness,
			# the most recently-added command takes priority.
		
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

from typing				import	List

from os					import	path
	# Manipulate filesystem path strings.

from collections		import	OrderedDict
	# Dictionary that maintains item order. We use this in the Commands class.

from collections.abc	import	Iterable
	# Used in type hints.

import re	# Standard regular expression facility.


		#|======================================================================
		#|	1.2. Imports of optional python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|======================================================================
		#|	1.3. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|==================================================================
			#|	1.3.1. The following modules, although custom, are generic 
			#|		utilities, not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.decorators	import	singleton
	# A simple decorator for singleton classes.

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

from	entities.entity		import	(
				Entity_,				# Abstract base class for reified entities.
				AI_Entity_,
				Operator_Entity,
				Human_Entity_,
				The_CommandInterface_Entity
			)

from	helpsys.helpSystem	import	(
				HelpItem				# Base class for help items.
					# (We use this to generate the help items for commands.)
			)

from	supervisor.action	import	(
				Action_,			# Abstract base class for general actions.
				warn,				# Generates a warning message.
				error,				# Generates an error message. 
				CommandAction_, 	# An action type for command actions.
					# (so that we can turn commands into actions).
				OperatorCommand,	# Lets us construct operator command actions.
				CommandByHuman_		# Lets us contruct actions for commands by human users.
			)

from	mind.aiActions		import	CommandByAI_
	# This lets us turn commands issued by the AI into appropriate actions.


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
	#|	_GENERIC_STD_CMD_REGEX			  [private module-level global constant]
	#|	_genericStdCmdPat
	#|
	#|		These constants contain the standard default regular expression
	#|		(and corresponding compiled pattern) that are used for parsing
	#|		command lines.	 The normal format for these in GLaDOS is, to
	#|		describe it simplistically:
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
		#| Note that whether the following pattern can occur anywhere in the
		#| line or must occur at the start of the line only depends on whether
		#| the search() or match() functions/methods are used with it.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global _GENERIC_STD_CMD_REGEX	# For detecting standard commands.
# Please note that the following pattern must be compiled with re.VERBOSE.
_GENERIC_STD_CMD_REGEX = r"""/		# Command pattern starts with a slash ('/').
                             (  	     # Begin command identifier group.
                               [A-Za-z_]   # Identifer starts with alpha or '_'.
                               \w*         # Word characters (alphanumberic or '_').
                             )           # End command identifier group.
                             (?:	# Begin non-capturing group for rest of line.
                               \s+    # At least one whitespace character.
                               (      # Begin group for argument list.
                                 \S     # At least one non-whitespace character.
                                 .*     # This gulps up the rest of the line.
                               )?     # End group for argument list. It's optional.
                             )?     # End rest-of-line group. It's also optional.
                             $      # At this point, the line must end.
                             """
# The following is just a non-verbose version of the above, for reference.
#_GENERIC_STD_CMD_REGEX = r'/([a-zA-Z_]\w*)(?:\s+(\S.*)?)?$'
	#|
	#| This means: 
	#|
	#|	(1) '/' = A single slash character ('/').
	#|
	#|	(2) '([a-zA-Z_]\\w*)' = (Group 1) A command identifier consisting of:
	#|
	#|			(a) '[a-zA-Z_]' = A single *alphabetic* character (upper- or
	#|					lowercase A-Z) or underscore.
	#|
	#|			(b) '\\w*' = Zero or more word characters (alphabetic, numeric, 
	#|					or underscore).
	#|
	#|	(3) '(?:\\s+(\\S.*)?)?' = An optional 'rest of command line', consisting of:
	#|
	#|			(a) '\\s+' = One or more whitespace characters, to separate the 
	#|					command identifier from the argument list (if present).
	#|
	#|			(b) '(\\S.*)?' = An optional 'argument list', consisting of:
	#|
	#|					(i) '\\S' = One non-whitespace character.
	#|					(ii) '.*' = Zero or more non-newline characters.
	#|
	#|	(4) '$' = The end of the line, or the end of the string.
	#|
	#\__________________________________________________________________________

global _genericStdCmdPat	# Compiled version of above
_genericStdCmdPat = re.compile(_GENERIC_STD_CMD_REGEX, re.VERBOSE)
	#\__ Note the re.VERBOSE here is critical to parse the verbose RE format.


	#|==========================================================================
	#|
	#|	3. Class forward declarations.					   [module code section]
	#|
	#|		These are really only useful as documentation in type hints.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class	CommandHelpItem:		pass	# A help item summarizing a command.
class	Command:				pass	# A single command type.
class	Subcommand:				pass	# A special case of another command.
class	Commands:				pass	# A list of commands.
class	CommandModule:			pass	# A pluggable command module.
class	CommandModules:			pass	# A whole list of command modules.
class	TheCommandInterface:	pass	# Singleton anchor for this module.


	#|==========================================================================
	#|
	#|	5. Private functions.							   [module code section]
	#|
	#|		Private functions defined for use internally in this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def downcase(name:str):
	"""Produce a lowercased-version of a given name string, to facilitate
		lookup/matching for case-insensitive command names."""
	return name.casefold()
		# Converts the name to lowercase for indexing/matching purposes.
		# Note: .casefold() is an interlingual equivalent of .lower().
	

	#|==========================================================================
	#|
	#|	4. Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class CommandHelpItem(HelpItem):

	"""A CommandHelpItem is a specialized type of HelpItem, which separately 
      tracks the usageText and shortDesc attributes for a command."""

	def __init__(
				newHelpItem:CommandHelpItem,
				name		:str="unset-command-name",
				usageText	:str="(unset command usage string)", 
				shortDesc	:str="(unset command short description)",
				longDesc	:str="(unset command long description)"
			):
        # NOTE: Callers should really always supply all the parameters!

		item = newHelpItem

		item._name 		= name		 # Store the name for later use.
		item._usageText = usageText  # Store the usage text for later use.
		item._shortDesc = shortDesc  # Store the short description for later use.
		item._longDesc 	= longDesc	 # Store the long description for later use.	

        # Generate the text from usageText and shortDesc and pass it to the superclass initializer.
		# Also pass longDesc as the verboseDesc parameter to the superclass initializer.
		text = f"{usageText} - {shortDesc}"
		item._text = text

		super().__init__(
			name		= name, 
			text		= text, 
			shortDesc	= shortDesc, 
			verboseDesc	= longDesc)

	@property
	def usageText(thisHelpItem:CommandHelpItem):
		return thisHelpItem._usageText

	@property
	def shortDesc(thisHelpItem:CommandHelpItem):
		return thisHelpItem._shortDesc

	# Special override for the superclass's topicDesc property.
	# For command help items, the topicDesc is the same as the usageText.
	# (For most help items, the topicDesc is the same as the shortDesc.)
	# We do this because we want the usage to appear at the upper-right
	# corner of the help screen for the item's temporary ItemHelpModule,
	# whereas for non-command items, we want the shortDesc to appear there.
	@property
	def topicDesc(thisHelpItem:CommandHelpItem):
		return thisHelpItem.usageText

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
		=============================
			
			.name:str - Symbolic name for this command pattern. Usually
				(but not necessarily always) this is also an alphanumeric
				word that invokes the command if following a slash ('/').
				For example, the 'help' command has the name 'help', and
				is invoked by typing '/help' at the command line.

			.usageText:str - A short string summarizing the usage format of
				this command in a human-readable way, e.g. "/<cmdName> <arg1> 
				<arg2> ...".  This is used by the help system in the course of 
				generating a HelpItem and a help screen to describe the command 
				to the user.
			
			.shortDesc:str - A short text string describing the function of
				the command. This is used in the help system in the course 
				of generating a HelpItem for the command to describe the
				command to the user. A good short description is usually just 
				one line, or at most a single sentence. A typical format for 
				the HelpItem that gets auto-generated for a command is:
					<usageText> - <shortDesc>

			.longDesc:str - Longer text string describing the function of
				the command in more detail. This is used in the help system
				in the course of generating a full help screen for the 
				command in response to a "/help <cmdName>" command. A good
				long description is usually a paragraph or two, or at most
				about a half-page of text.

			.standard:bool=True - If this is True (the default), then the
				command may be invoked by including '/<cmdName>' at the
				start of the input line (or anywhere in the input line,
				if .anywhere=True; see below). If this is False, then a
				custom format string should be supplied.

			.anywhere:bool=False - If this is True, then the command will
				be invoked if its pattern is matched starting anywhere in
				the input line. If this is False, then the command will
				only be invoked if its pattern appears at the start of the
				input line. This setting is only needed for commands with
				auto-generated format strings; custom format strings can
				simply include '^' (or not) at the start of that regex.
	
			.caseSensitive:bool=False - If this is True, then any automatic
				matching of the command name from its name is case-sensitive.

			.prefixInvocable:bool=True - If this is True, then any unique
				prefix of the command name will also automatically invoke
				the command. (But this is ignored if standard=False.)

			.hasSubcmds:bool=False - If this is True, then this command
				has subcommands which we'll try to automatically detect
				and dispatch on.  See also class Subcommand.

			.cmdFormat:str	- Regex-format string for parsing this command
				pattern. This may be supplied manually (for custom parsing)
				or automatically generated.
				
			.unique:bool=True - Boolean that is True if the format regex is
				supposed to uniquely identify this particular command type.
				That is, matching command lines should not match any other
				command types. If this is True and there are multiple matches,
				then we have to disambiguate between those (via an error
				message leading to a further interaction with the user). If
				this is False, then the system invokes the highest-priority
				matching command type that is in a currently-active module.
				NOTE: Setting this to False can be dangerous!!! Beware.
			
			.cmdModule:CommandModule - Command module to which this
				command is associated.

			.helpItem:HelpItem - HelpItem object that is generated for this
				command. This is used in the help system to generate help
				screens for command modules that this command is contained
				in. This is automatically generated when the command is
				initialized, and (aspirationally) is updated whenever the 
				command's usage text or short description is changed.


		Subclasses may define the following class-level variables:
		==========================================================

		  Provideable: (not provided by default)
		  ------------

			.name:str - If defined, this is used to initialize cmd.name.

			.usageText:str - If defined, this is used to initialize
				cmd.usageText.

			.shortDesc:str - If defined, this is used to initialize
				cmd.shortDesc.

			.longDesc:str - If defined, this is used to initialize
				cmd.longDesc.

			.cmdFormat:str - If defined, this is used to initialize cmd.cmdFormat.

			.argListRegex:str - If defined, this is a regex that is used to 
				parse the command's argument list.

			.argListDoc:str	- If defined, this is a doc string for the command's 
				argument list.

			.cmdModule:CommandModule - If defined, this is used to
				initialize cmd.module.


		  Overrideable:
		  -------------

			.standard	: bool=True  - Default value of cmd.standard.
			.takesArgs	: bool=True  - Default value of cmd.takesArgs.
			.needsArgs	: bool=False - Default value of cmd.needsArgs.
			.anywhere	: bool=False - Default value of cmd.anywhere.
			.caseSens	: bool=False - Default value of cmd.caseSens.
			.prefInvoc	: bool=True	 - Default value of cmd.prefInvoc.
			.hasSubcmds : bool=False - Default value of cmd.hasSubcmds.
			.unique		: bool=True	 - Default value of cmd.unique.

			.actionClass:class=CommandAction_ - Subclasses should override this 
				with a subclass of CommandAction_ that is suitable for the 
				creation of actions for executing this command.


		Instance public methods:
		========================
			
			.matches(text:str, anywhere:bool=False) - Returns True if this
				command matches the given text string (usually a single line).
				if anywhere=False, then it must match at the start of the line.
				If anywhere=True and the command's anywhere attribute is True,
				then it can match anywhere in the line.

			.handler(groups:list) - This method is called to actually perform
				the command's functionality in more detail, beyond its basic
				pattern matching. It will be passed the groups (substrings)
				parsed out by the command's regex. For standard commands, this
				just consists of the command's argument list as a single string.
				The default method should be overridden by subclasses.

			.genCmdAction(text:str, by:Entity_) - Generates a command
				action (instance of CommandAction_ or one of its
				subclasses) that is appropriate for invocation of this
				command by the given entity based on the given text
				string.

	"""

	def __str__(thisCmd):
		return f"[cmd '{thisCmd.name}' in module '{thisCmd.cmdModule}']"

		# Our default action class (a class-level variable).
	actionClass = CommandAction_	# Generic base class for command actions.

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| The following class-level variables provide default values that
		#| are used to initialize the corresponding instance variables;
		#| subclasses may override these. (The idea of this way of overriding
		#| default initialization parameters is that it's simpler than passing
		#| overrides up a chain of super().__init__() calls.

	standard	= True		# By default, commands may be invoked by '/<name>'.
	takesArgs	= True		# By default, commands may take an optional argument list.
	needsArgs	= False		# By default, commands don't require an argument list.
	anywhere	= False		# By default, commands can't start anywhere on the command line (only at the start of the line).
	caseSens	= False		# By default, command format matching is case-insensitive.
	prefInvoc	= True		# By default, any unique prefix can be used to invoke a command.
	hasSubcmds	= False		# By default, commands don't have subcommands.
	unique		= True		# By default, we expect commands to match uniquely with command lines.

	def __init__(
			newCmd:		Command,	# Newly-created command object to be initialized.
			name:		str  =None,	# Symbolic name of this command pattern.
			usageText:	str  =None,	# Short text string describing the usage of this command.
			shortDesc:	str  =None,	# Short text string describing the function of this command.
			longDesc:	str  =None,	# Long text string describing the function of this command.
			standard:	bool =None,	# True (default) -> command may be invoked by '/<name>'.
			takesArgs:	bool =None,	# True (default) -> command may take an optional argument list.
			needsArgs:	bool =None,	# True -> command requires an argument list.
			anywhere:	bool =None,	# True -> command may start anywhere on the input line.
			caseSens:	bool =None,	# True -> command name should be treated as case-sensitive.
			prefInvoc:	bool =None, # True (default) -> any unique prefix can be used to invoke the command.
			hasSubcmds:	bool =None,	# True -> Dispatches to subcommand named in 1st argument.
			cmdFmt:		str  =None,	# Custom format string for parsing this command.
			unique:		bool =None,	# True (default) -> format is supposed to be unique.
			cmdModule:	CommandModule=None	# Command module this command is in.
		):
		
		"""
			Instance initializer for the Command class.
		
				Arguments:
				----------
				
					name:string - A symbolic name (required). Converted to
						all-lowercase for indexing purposes, unless caseSens
						(below) is True.
					
					standard:bool=True - If this is True, then we'll try to
						automatically match the command if '/<name>' is present
						in the input line (and also see the <anywhere> and
						<prefInvoc> parameters below).

					takesArgs:bool=True - If this is true, then the automatically-
						generated pattern for this command will allow an optional
						argument list.

					needsArgs:bool=False - If this is True, then the automatically-
						generated pattern for this command will require an argument
						list.

					anywhere:bool=False - If this is True, then we can match
						the command anywhere on the input line (assuming its
						format string doesn't start with '^'). If this is False,
						then the command will only match at the start of the line.

					caseSens:bool=False - If this is True, then matching of the
						command name is case-sensitive.

					prefInvoc:bool=True - If this is True, then any unique
						prefix of the command name can also be used to invoke
						the command. (But, it's ignored if standard=False.)

					hasSubcmds:bool=False - If this is True, then the first word
						after the command name will be interpreted as a subcommand
						identifier that we'll try to dispatch on. (Forces takesArgs
						to True.)

					cmdFmt:string - A custom 're' style regular expression format
						string for parsing the command.	If not supplied, a simple
						default command-line format is used.
										
					unique:boolean=True - This is True if the given format string is
						supposed to uniquely identify this command. If False, then
						this command can be easily overridden. Defaults to True. The
						value provided (if any) is ignored if no format string was
						supplied.
					
					cmdModule:CommandModule - The CommandModule instance that this
						command is associated with.	This is optional. If not
						provided, then this command is "free-standing" (not
						associated with a specific command module).
											
																			"""
		
		cmd = newCmd	# Shorter name for the new command.
		
			# Initialize initializer arguments from class-level attributes,
			# if not provided by caller, but provided by class definition.
		
		if name is None 		and hasattr(cmd,'name'):
			name = cmd.name

		_logger.info(f"Initializing command '{name}'...")

		if usageText is None 	and hasattr(cmd,'usageText'):
			usageText = cmd.usageText

		if shortDesc is None 	and hasattr(cmd,'shortDesc'):
			shortDesc = cmd.shortDesc

		if longDesc is None 	and hasattr(cmd,'longDesc'):
			longDesc = cmd.longDesc

		if standard is None:

			if hasattr(cmd, 'standard'):
				standard = cmd.standard
			else:
				standard = True		# Commands are slash-invocable by default.

		if takesArgs is None:

			if hasattr(cmd, 'takesArgs'):
				takesArgs = cmd.takesArgs
			else:
				takesArgs = True	# Commands allow argument lists by default.

		if needsArgs is None:

			if hasattr(cmd, 'needsArgs'):
				needsArgs = cmd.needsArgs
			else:
				needsArgs = False	# Commands don't require argument lists by default.

		if anywhere is None:

			if hasattr(cmd, 'anywhere'):
				anywhere = cmd.anywhere
			else:
				anywhere = False	# Commands aren't match-anywhere by default.

		if caseSens is None:

			if hasattr(cmd, 'caseSens'):
				caseSens = cmd.caseSens
			else:
				caseSens = False	# Commands are non-case sensitive by default.

		if prefInvoc is None:

			if hasattr(cmd, 'prefInvoc'):
				prefInvoc = cmd.prefInvoc
			else:
				prefInvoc = True	# Commands are prefix-invocable by default.

			# NOTE: prefInvoc should be ignored if standard=False.

		if hasSubcmds is None:

			if hasattr(cmd, 'hasSubcmds'):
				hasSubcmds = cmd.hasSubcmds
			else:
				hasSubcmds = False	# Don't assume command has subcommands.

		# If we have subcommands, force takesArgs to True.
		if hasSubcmds:
			takesArgs = True

		if cmdFmt is None 		and hasattr(cmd,'cmdFormat'):

			cmdFmt = cmd.cmdFormat

			# NOTE: A custom format MUST be provided (either in a class
			# attribute or in an initializer argument) if standard=False!

		if unique is None:

			if hasattr(cmd,'unique'):
				unique = cmd.unique
			else:
				unique = True	# Assume command types are unique by default.

		if cmdModule is None:
			if hasattr(cmd,'cmdModule'):
				cmdModule = cmd.cmdModule


			# Standardize the command name to lowercase, unless it's
			# supposed to be case-sensitive.

		if not caseSens:
			name = downcase(name)


			# Store initializer arguments in instance attributes.
		
		cmd.name			= name
		cmd.usageText		= usageText
		cmd.shortDesc		= shortDesc
		cmd.longDesc		= longDesc
		cmd.standard		= standard
		cmd.takesArgs		= takesArgs
		cmd.needsArgs		= needsArgs
		cmd.anywhere		= anywhere
		cmd.caseSensitive 	= caseSens
		cmd.prefixInvocable = prefInvoc
		cmd.hasSubcommands	= hasSubcmds
		cmd.cmdFormat		= cmdFmt
		cmd.unique			= unique
		cmd.cmdModule		= cmdModule
		
			# Automatically generate and store a help item for this command.
			# This will be used in assembling the help screen text for the
			# command module that the command is a part of.
		
		cmd.helpItem = CommandHelpItem(
			name		= cmd.name, 
			usageText	= cmd.usageText, 
			shortDesc	= cmd.shortDesc, 
			longDesc	= cmd.longDesc
		)

			# If command format was not provided, try to generate it automatically.

		if cmdFmt is None:
			if standard is True:
				cmd._autoInitCmdFormat()	# Call private method defined below.
				cmdFmt = cmd.cmdFormat
			else:
				_logger.error("Command initializer: No format provided "
							  "for nonstandard command!")
				# Really we should raise an exception here, too.
		
			# Go ahead and compile the command format appropriately.

		reFlags = re.IGNORECASE if not caseSens else 0
		cmd.pattern = re.compile(cmd.cmdFormat, reFlags)

			# If this command has subcommands, initialize them.
		if hasSubcmds and hasattr(cmd,'subcommand_classMap'):
			for subcmdWord,subcmdCls in cmd.subcommand_classMap.items():
				subcmdCls(subcmdWord, cmd)
			
			# Automatically add this newly-created command to its command 
			# module (if known).

		if cmdModule is not None:
			cmdModule.addCommand(cmd)
			
	#__/ End initializer for class Command.


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| command._autoInitCmdFormat()				   [private instance method]
		#|
		#|		This private instance method is used by the initializer
		#|		to automatically generate the command format string
		#|		(command parsing regex) if the caller/subclass didn't
		#|		provide one. The regex matches '/<cmdName>' (or prefixes
		#|		of that) anywhere in the line; an argument list is then
		#|		captured (following whitespace).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def _autoInitCmdFormat(cmd):

		"""This private method may be called by the instance initializer
			to automatically initialize the command format in cases where
			no custom format specifier was provided."""

		if cmd.cmdFormat is not None:
			# Should probably generate a warning here.
			return	# A format specifier already exists; we have nothing to do.

		if cmd.standard is False:
			# Should probably generate a warning here.
			return	# We don't know how to auto-generate formats for nonstandard commands.

		name = cmd.name		# Shorter variable name for the command name.

		# If a command name isn't even provided, we can't do very much, really.
		if name is None:
			cmd.cmdFormat = _GENERIC_STD_CMD_REGEX
			unique = False	# The default regex is most definitely NOT a unique pattern.
				# Not used currently?

			# NOTE: The above can be appropriate if we wish to add an unnamed "generic
			# command" # to the system, such that if the user puts
			#
			#		/<randomIdentifier> <blah>
			#
			# the system will treat it as an undefined command, and "execute" it, but
			# where this "execution" only generates an error message of some sort.

			return
			
		# Make sure the command name contains at least one character.
		if len(name) == 0:
			# This is an error condition, and we should do something sensible.
			# Like log-reporting it.
			return	# For now, just return.

		# Start with an empty regex.
		regex = ''

		# NOTE: We can uncomment one of the following to override the .anywhere
		# setting in all auto-generated patterns.

		# If the following line is uncommented, then the auto-generated pattern
		# will *only* match at the start of the line (regardless of the .anywhere
		# setting).
		
		#regex += '^'

		# Alternatively, if the following line is uncommented, then the auto-
		# generated pattern will match starting *anywhere* in the line
		# (regardless of the .anywhere) setting.

		#regex += '^.*'
			# The format always starts with beginning-of-line followed by any
			# number of random characters.

		# The auto-generated format always is kicked off by a slash.
		regex += '/'

		# Next we define a recursive internal function that we'll use to build
		# up the rest of our RE. This is needed to capture match arbitrary
		# prefixes of the command name.
		def optRestRE(rest:str):
			# <rest> is a suffix of a command word; this function returns
			# a regular expression that matches it if it's present.
			
			"""A recursive inner helper function to generate a regular
				expression for matching as much of the rest of the
				command word as is present."""

			if len(rest) == 0:	# Nothing left?
				return ""		# Then we don't need any more RE, either.

			if len(rest) == 1:	# Only 1 character left?
				return rest + '?'	# Match just that 1 character, optionally.

			firstChar = rest[0]	 # First character of rest (should be in [A-Za-z_]).
			restChars = rest[1:] # Remainder of string after first char.

				# The following line builds up the desired R.E. recursively.
			return '(?:' + firstChar + optRestRE(restChars) + ')?'
				#|
				#| Explanation:
				#|
				#|		1. The '(?:' begins a non-capturing group.
				#|			(There's no reason to save the rest of the
				#|			command word, if it's present.)
				#|
				#|		2. The first character of the rest of the command
				#|			word must be present, in order for this group
				#|			to match. (If the command isn't case-sensitive,
				#|			The command word should have been previously
				#|			downcased, and the entire regex-matching
				#|			process should be taking place in a case-
				#|			insensitive mode.)
				#|
				#|		3. Here, include a regular expression that
				#|			optionally matches any initial prefix of
				#|			the rest of the rest of the command word,
				#|			after its first character, if it is present.
				#|			This is generated by a recursive call to this
				#|			very same helper function.
				#|
				#|		4. The ')?' closes the non-capturing group, and
				#|			says, match it optionally, meaning 0 or 1 times.
				#|
				#\______________________________________________________________

		#__/ End internal recursive function optRestRE().

		firstChar = name[0]		# Extract first character of command name.
		restChars = name[1:]	# Remaining characters of command name, if any.

		# Note: First char should be alphanumeric or '_'.
		# NOTE: The following does not capture what actual command word prefix was used. Should we?

		regex = regex + firstChar + optRestRE(restChars)
			# This matches any nonzero-length prefix of the command name,
			# up to & including the entire command name.
		
		# If the command takes arguments, then optionally match an argument list.
		if cmd.takesArgs:

			# If the command has subcommands, then the arglist format is
			# " <subcmd> [<moreArgs>]".

			if cmd.hasSubcmds:
				regex = regex + r'\s+([A-Za-z_-][\w-]*)'
					# A few things to note. The subcommand word itself
					# is *not optional*. (Maybe in the future, we'll
					# allow it to be optional, but for now it isn't.)
					# The subcommand word may not start with a digit,
					# but it may begin with '_' or '-'. We capture the
					# subcommand word as a group (since we'll need to
					# use it to look up the subcommand).

			regex = regex + r'(\s+(\S.*)?)'
				# ^ This capture-matches an argument list (with leading 
				# whitespace). The argument list itself is captured as a group, 
				# so that we can pass it to the command's handler function. Note 
				# that any further parsing of the argument list is the 
				# responsibility of the command's handler function.

			if not cmd.needsArgs:
				regex = regex + '?'		# The argument list is optional.


		regex = regex + '$'		# At this point we must be at the end of the string.

			#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|
			#| Explanation of the construction above:
			#|
			#|		1. The previous regex scanned everything through the '/'.
			#|
			#|		2. Next, we must have *at least* the first character of
			#|			the command name.
			#|
			#|		3. Next, we may have any number of successive characters
			#|			from the rest of the command name.
			#|
			#|		4. Next, '(?:\\s+ starts a non-capturing group beginning
			#|			with one or more whitespace characters.
			#|
			#|		5. Next '(\\S.*)?' is a capturing group consisting of
			#|			a non-whitespace character and zero or more additional
			#|			characters -- this is the command's argument list, if
			#|			it is present.
			#|
			#|		6. Next ')?$' end the entire non-capturing group
			#|			that started with the whitespace, says that whole
			#|			thing is optional, and that now we must be at the end
			#|			of the line.
			#|
			#\__________________________________________________________________
			
		cmd.cmdFormat = regex	# Store that regex as our automatic command format.
		#cmd.unique = True		# Ideally this command should be unique...
		# Uncomment the above to override user setting of unique for all
		# autogenerated commands.

	#__/ End instance method command._autoInitCmdFormat().


	def matches(cmd:Command, text:str, anywhere:bool=False):

		"""Returns True if this command matches the given text string
			(usually a single line). If anywhere=False, then it must
			match at the start of the line.  If anywhere=True and the
			command's anywhere attribute is also True, then it can
			match anywhere in the line.

			Things also taken care of here include:
		
				* If the command is marked as case-sensitive, then
					case-sensitive matching is used. (This is actually
					taken care of at command pattern compile time.)

			"""

			# Only allow 'anywhere' search if both the argument
			# AND the command attribute allow it.
		anywhere = anywhere and cmd.anywhere

		if anywhere:
			match = cmd.pattern.search(text)
		else:
			match = cmd.pattern.match(text)

		return match
			# Note this is not really a boolean value, but can
			# still be used as an if condition appropriately.
			
	#__/ End instance method command.matches().


	# This method by used by subclasses to parse the command's argument list
	# using its argListPattern attribute.  The argListPattern attribute is
	# expected to be a compiled regular expression object.  The argument list
	# is expected to be a single string in the first group of the list.

	def parseArgs(thisCommand:Command,  # This command object.
				  restGroups:list  		# Groups after command word.
			):

		"""Parses the argument list from the given list of groups
			after the command word.  The argument list is expected
			to be a single string in the first group of the list."""

		cmd = thisCommand			# Shorter name for this command.

		argList = restGroups[0]		# There should be only one group: Rest of line.

		_logger.info(f"About to parse {cmd.name} arguments from argList [{argList}]...")

		if argList is None:
			error(The_CommandInterface_Entity(),
				  f"The '/{cmd.name}' command needs an argument list.")
			_logger.error(f"Command {cmd.name} wasn't given an argument list!")
			return

		match = cmd.argListPattern.match(argList)

		if match:	# We got a match; go ahead and dispatch to subcommand.
			groups = match.groups()
			groupDict = match.groupdict()
			cmd.handle(groups, groupDict)	# Dispatch to subcommand handler.
				# The .handle() method may use either/both of the groups
				# and groupDict arguments, depending on whether its regex
				# uses named groups or not.
		else:
			# The Command's regex didn't match the rest of the command line.
			# A sensible thing to do here would be to report an error message
			# to the AI containing the argListDoc, to explain the required format.

			error(The_CommandInterface_Entity(),
				  f"The required command format is: /{cmd.name} {cmd.argListDoc[1:]}")

			# For now, also report the error to the system log.
			_logger.error(f"Command {cmd.name} arglist [{argList}] didn't "
						  f"match pattern [{cmd.argListDoc}].")

	#__/ End instance method command.parseArgs().
	

	def genCmdAction(cmd, cmdLine:str, invoker:Entity_):

		"""Generates a command action object (instance of CommandAction_)
			that is suitable for passing this command to the action system
			for execution, when invoked by the given entity."""
		
		# Was the conceiver the AI, the operator, a generic human, or other?
		# Use this information to set the command action class appropriately.

		if isinstance(invoker, AI_Entity_):

			cmdActionClass = CommandByAI_		# Command issued by the AI.

		elif isinstance(invoker, Operator_Entity):

			cmdActionClass = OperatorCommand	# Command issued by the operator.

		elif isinstance(invoker, Human_Entity_):
			
			cmdActionClass = CommandByHuman_	# Command issued by a human user.

		else:	# We don't know any other special entities for command purposes.

			cmdActionClass = CommandAction_		# A generic command action.

			# Now go ahead and construct the command action object.

		cmdAction = cmdActionClass(
			cmdLine, # Pass the given command line as the cmdLine argument.
			cmdType = cmd,	# Pass the given command as the cmdType.
			conceiver = invoker)
		#	 \
		#	  \__ Note we DON'T pass a description; we'll let CommandAction_ construct it.

		return cmdAction
		

	def execute(thisCmd, cmdLine:str):
		
		"""Executes the given command type, for the given command line.
			This requires parsing the command line and then running
			the command handler."""

		_logger.info(f"Executing command {thisCmd} on command line [{cmdLine}]...")

		pattern = thisCmd.pattern

			# First try matching at start of line; if that doesn't work,
			# and the command's anywhere flag is set, search anywhere.

		match = pattern.match(cmdLine)
		if not match and thisCmd.anywhere:
			match = pattern.search(cmdLine)

			# Given the match, extract the groups and run the handler.
		groups = match.groups()
		thisCmd.handler(groups)


	def handler(cmd, groups):

		"""This is a default command handler that can be used in cases when
			no other command handler has been defined.  Subclasses should
			override this method."""

		_logger.debug(f"Executing default command handler for command: {cmd} on groups: {groups}")

		if cmd.hasSubcmds and hasattr(cmd, 'subcommand_classMap'):

			subcmdWord = groups[0]		# 1st group = subcommand name.
			rest = groups[1:]			# Remaining groups after 1st
			
			_logger.info(f"Executing subcommand '{subcmdWord}' on groups {rest}...")

			subcmd_classMap = cmd.subcommand_classMap

			if subcmdWord in subcmd_classMap:

				subcmdClass = subcmd_classMap[subcmdWord]

					# Dispatch to the particular subcommand's .parseArgs method
					# to process the rest of the command line.
				subcmdClass().parseArgs(rest)

			else:
				_logger.error(f"Subcommand [{subcmdWord}] is not defined for command: {cmd}.")

		else:
			_logger.error(f"Command [{cmd.name}] is not yet implemented.")

		# A sensible thing to do here would be to report a system error
		# like 'the <name> command has not yet been implemented.'

		pass	# For now, do nothing.


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| Public instance methods for class Commands.    [class definition section]

	def prefixes(cmd):		# NOTE: I don't think we're using this currently.

		"""Return a list of all prefixes of the name of this command (without
			regard to their possible uniqueness, or lack thereof). The shortest
			prefixes are returned first."""

		name = cmd.name

		# The following recursive algorithm is cute, but a simple for loop
		# would've been easier.

		def _prefHelper(pref:str):
			"""Recursive internal helper function for command.prefixes().
				Given a prefix, return a list of all its prefixes (including
				itself), shortest first."""

			if len(pref) == 1:	# Is this prefix already only 1 character long?
				return [pref]	# Return a singleton list of itself.

			return _prefHelper(pref[:-1]) + [pref]
				# Recursively generate the list of all prefixes shorter than
				# the current one, then add this one to it.

		#__/ End internal function _prefHelper().

		prefList = []
		if len(name) > 1:	# Is command name longer than 1 character?
			prefList = _prefHelper(name[:-1])
				# Recursively generate list of prefixes.

		return prefList

	#__/ End method command.prefixes().

#__/ End class Command.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Subcommand(Command):

	"""A subcommand is a type of command that is really just a special
		case of a more general command. For example, in the Goals app,
		the command module includes a '/goal' command whose overall
		format descriptor looks something like this:

			/goal (add|change|delete|insert|move) [<N> [to <M>]] ["<desc>"]

		Each of the command words that may appear after '/goal' denotes
		a subcommand; for example, one of the subcommands is:

			/goal add "<description>"

		which is considered a special case of the '/goal' command.

		Detailed documentation for how to use commands and subcommands
		is provided by means of the Help system; although individual apps
		may also provide hints about their commands in their on-screen text.

	"""

	# Subclasses should define these class variables:
	#
	#	name:str			- Symbolic name for subcommand, e.g., 'goals-add'.
	#	argListRegex:str	- Regex for the subcommand's argument list.
	#	argListDoc:str		- Doc string for the subcommand's arglist.

	def __init__(newSubcommand:Subcommand,	# Newly-created subcommand object to be initialized.
				 subcmdWord:str,			# The command word selecting this subcommand (e.g., 'add').
				 #name:str=None,			# Symbolic name of this subcommand (e.g., 'goals-add').
				 #cmdFmt:str=None,			# Custom format string for parsing this subcommand.
				 parent:Command=None		# The "parent" command that this is a subcommand of.
			):
		
		sc = newSubcommand	# Just a convenient shorter name for this guy.

		sc.word = subcmdWord

		sc.parent = parent	# Remember our parent command.

		#subcmdName		= sc.name

		if hasattr(sc, 'argListRegex'):
			argListRegex		= sc.argListRegex
			sc.argListPattern 	= re.compile(argListRegex, re.IGNORECASE)
				# For now, we always do case-insensitive matching of argument lists.
		else:
			_logger.error(f"Subcommand {sc.name} has no argListRegex attribute!")

		#argListDoc		= sc.argListDoc

	def parseArgs(thisSubcommand:Subcommand,  # This subcommand object.
				  restGroups:list  # Groups after subcommand word.
			):

		sc = thisSubcommand			# Shorter name for this subcommand.

		argList = restGroups[0]		# There should be only one group: Rest of line.

		_logger.info(f"About to parse {sc.name} arguments from argList [{argList}]...")

		if argList is None:
			error(The_CommandInterface_Entity(),
				  f"The '/{sc.parent.name} {sc.word}' subcommand needs an argument list.")
			_logger.error(f"Subcommand {sc.name} wasn't given an argument list!")
			return

		match = sc.argListPattern.match(argList)

		if match:	# We got a match; go ahead and dispatch to subcommand.
			groups = match.groups()
			groupDict = match.groupdict()
			sc.handle(groups, groupDict)
		else:
			# The subcommand's regex didn't match the rest of the command line.
			# A sensible thing to do here would be to report an error message
			# to the AI containing the argListDoc, to explain the required format.

			error(The_CommandInterface_Entity(),
				  f"The required command format is: /{sc.parent.name} {sc.word} {sc.argListDoc[1:]}")

			# For now, also report the error to the system log.
			_logger.error(f"Subcommand {sc.name} arglist [{argList}] didn't "
						  f"match pattern [{sc.argListDoc}].")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Commands:

	"""commandInterface.Commands								  [public class]
	
			This is a container class for an ordered list of commands
			(i.e., instances of the Command class).	 It facilitates fast 
			lookup of commands using their symbolic names, or prefixes of
			such. (Is this optimization really necessary?)  It also provides
			features for more general command lookup using trial regular
			expression matching.

			If multiple commands match a given line of input (which can
			happen if a non-unique command word prefix is provided, or if
			custom command regexes don't guarantee uniqueness, more
			generally), then we can return all matching commands.

			A constraint is enforced that only one command having any given
			exact symbolic name can be stored, to avoid confusion. Warnings
			are issued if the user of this class tries to add another command
			under a name that already exists.
		
		
		Public instance methods:
		========================
			
			.addCommand(cmd:Command) -
				
				Adds the given command to the Commands list, at the end of 
				the list (i.e., lowest priority for matching purposes). If
				there is already a command in the list with the same name,
	
			
			.lookupByName(name:str) -
				
				Return the command in the list having the given name, or 
				None if there is none with that name.
				

			.lookupByPrefix(prefix:str) -

				Returns a list of all standard, prefix-invocable commands
				in the command list having the given prefix.


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
	#|			._desc:str
	#|
	#|				A descriptive name for this particular command list.
	#|
	#|
	#|			._cmdOD:OrderedDictionary
	#|		
	#|				Ordered dictionary of commands, sorted in order from
	#|				highest to lowest priority for regex matching purposes.
	#|
	#|				The key is the (typically downcased) name of the
	#|				command; the value is the associated Command
	#|				object. A given Commands list can only store one
	#|				command of a given name.
	#|
	#|
	#|			._prefCmds:dict
	#|
	#|				This is a map from possible command prefixes (for
	#|				prefix-invocable commands) to the list of matching
	#|				full names, for this particular command set. The
	#|				order of command names in the list should match
	#|				their order in the master _cmdOD list.
	#|
	#|
	#|			._nonstds:list
	#|
	#|				A list, in priority order, of all non-standard format
	#|				commands in the comment list.
	#|
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	
	def __init__(self, desc:str = "(unnamed command list)",
				 initialList:Iterable = None):
	
		"""Instance initializer for the Commands class.  If <initialList>
			is provided, then the commands in it are added to the list."""
		
		# Remember this command list's descriptive name.
		self._desc = desc

			# Initialize the internal command list to an empty ordered
			# dictionary object.
		self._cmdOD = OrderedDict()
		
			# Initialize the prefix commands list to an empty dictionary.
		self._prefCmds = {}

			# Initialize the nonstandard commands list to empty list.
		self._nonstds = []

			# If an initial list of commands is provided, add the commands
			# in it to the internal command list one at a time.
			
		if initialList != None:
			for cmd in initialList:
				self.addCommand(cmd)
		
	#__/ End initializer for class Commands.


	def nCmds(cmds:Commands):
		return len(cmds._cmdOD)


	def __str__(cmds:Commands):
		return cmds._desc


	def addCommand(cmds:Commands, cmd:Command):

		"""Adds the given command to the end of the command list.
			If a command with the given name is already present in
			the list, generate a warning and don't add it."""

		cmdOD = cmds._cmdOD		# OrderedDict of commands.

		name = cmd.name		# Should already be in standard form.
		
		if name in cmdOD:	# Command is already in this command list!
			
			_logger.warn(f"commands.addCommand(): A command named {name} "
						 	f"is already in {cmds}; ignoring.")
			return

		cmds._cmdOD[name] = cmd

			# Now also add all of the command's prefixes to that index.

		prefixes = cmd.prefixes()	# Generates all prefixes of command name.

		for prefix in prefixes:

			_logger.debug(f"Installing command {name} under prefix {prefix}...")

			prefCmds = cmds._prefCmds

			if prefix in prefCmds:
				prefCmds[prefix] += [cmd]
			else:
				prefCmds[prefix] = [cmd]

			cmds._prefCmds = prefCmds

		#__/ End for prefixes.

			# If it's a nonstandard command, add it to that list.

		if not cmd.standard:
			cmds._nonst += [cmd]

	#__/ End method commands.addCommand().

	def lookupByName(cmds:Commands, name:str):

		"""Return the command in the list having the given name, or 
			None if there is none with that name."""

		if name in cmds._cmdOD:
			_logger.debug(f"Found command name {name} in command list {cmds}.")
			return cmds._cmdOD[name]
		else:
			return None

	def lookupByPrefix(cmds:Commands, prefix:str):

		"""Returns a list of all standard, prefix-invocable commands
			in the command list having the given prefix."""

		if prefix in cmds._prefCmds:
			_logger.debug(f"Found command prefix {prefix} in command list {cmds}.")
			return cmds._prefCmds[prefix]
		else:
			return []

def getHelpList(cmds:Commands) -> List[CommandHelpItem]:

    """Returns a list of CommandHelpItem objects, for all commands in
      the command list."""

    helpList = []

    for cmd in cmds._cmdOD.values():
      helpList += [cmd.helpItem]

    return helpList

def genHelpText(cmds:Commands) -> str:

	"""Generates a help text string for the given command list.
		The help text is a display of the help text for all 
		commands in the list, on separate lines with a blank
		line in between them, in the order in which they appear 
		in the command list.  The help text is returned as a
		string."""

	helpList = getHelpList(cmds)

	helpText = ""

	for item in helpList:
		helpText += f" - {item.text}\n\n"

	return helpText

#__/ End class Commands.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CommandModule:

	def nCmds(self):
		return self.commands.nCmds()

	def __str__(self):
		return self._desc

	def __init__(self, desc:str="(unnamed command module)"):

		self._desc = desc

		self._commands = Commands(desc=f"command list for module {self._desc}")
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
	
	@property
	def active(self):
		return self._isActive

	@property
	def commands(self):
		return self._commands

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

	def lookupCommands(
			cmdMod:CommandModule,		# This command module.
			cmdID:str,					# Command identifier to lookup.
			inputLine:str,				# The input line that it must match against.
			anywhere:bool = False,		# If True, allow command to start anywhere.
			prefix:bool = False):		# If True, then search command prefixes.
		
		"""Look up the given command identifier in the present module.
			Return a list of matching commands, in priority order.
			Each element of the list must satisfy both of the criteria:

				1. If prefix=False, then the command's symbolic name
					must match the supplied command identifier cmdID
					exactly; otherwise, the supplied identifier must
					be a prefix of the command's symbolic name.

				2. If anywhere=False, or if the command's anywhere
					attribute if False, then the command's pattern
					must match from the *start* of the given input line;
					otherwise, it may match anywhere in the input line.
		"""

			# Retrieve our own Commands object.
		cmds = cmdMod.commands

		_logger.debug(f"Note: Command module {cmdMod} contains {cmdMod.nCmds()} commands.")

			# Initialize our result to be an empty command list.
		cmdList = []
		
			# First, we need to do different things depending on if
			# this is supposed to be an exact match, or prefix match.
		if prefix:	# Match commands that have cmdID as a prefix, only.
			
			_logger.debug(f"CommandModule.lookupCommands(): About to lookup prefix {cmdID} in {cmds}.")

				# Retrieve all commands in this module having the given prefix.
			prefCmds = cmds.lookupByPrefix(cmdID)
		
				# If there are none, it could just be a case-sensitivity issue.
				# try downcasing the ID and prefix-searching again.
			if len(prefCmds) == 0:
				prefCmds = cmds.lookupByPrefix(downcase(cmdID))

				# Now, we need to go through the results, figuring out which ones
				# actually do match the given inputLine.
			for prefCmd in prefCmds:
				if prefCmd.matches(inputLine, anywhere):
					cmdList += [prefCmd]

		else:		# Match commands whose exact name is cmdID, only.

			_logger.debug(f"CommandModule.lookupCommands(): About to lookup command {cmdID} in {cmds}.")

				# Retrieve the command in this module, if any, with the given name.
			cmd = cmds.lookupByName(cmdID)

				# If there is none, it could just be a case-sensitivity thing.
				# Try downcasing the ID and look it up again.
			if cmd is None:
				cmd = cmds.lookupByName(downcase(cmdID))
			
				# Now, we need to make sure this command really matches.
			if cmd is not None and cmd.matches(inputLine, anywhere):
				cmdList += [cmd]

		return cmdList
			
	#__/ End lookupCommands().

	def findNonstdCmds(
			cmdMod:CommandModule,		# This command module.
			inputLine:str,				# The input line that it must match against.
			anywhere:bool = False):		# If True, allow command to start anywhere.

		"""Find nonstandard-format commands in this module matching the given
			input line."""

		### NOT YET IMPLEMENTED; THIS IS A STUB ###

		return []

	#__/

	def getHelpList(self) -> List[CommandHelpItem]:
		"""
			Returns a list of help items for all commands
			in this module.
		"""
		return self._commands.getHelpList()
	
	# Note: The following can be overridden by subclasses
	# for specific types of command modules, if desired.
	def genHelpText(self) -> str:
		"""
			Generates a string containing help text for all
			commands in this module.
		"""
		helpText = f"Help for commands in module {self.name}:\n"
		helpText += self._commands.genHelpText()

		return helpText

#__/ End public class commandInterface.CommandModule.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CommandModules:

	"""An instance of this class represents a collection of command modules. It 
		is kept ordered for the simple reason that in case of a collision 
		between command names in different modules, the one in the module that
		was installed first takes priority."""
			# Is this a good policy? The idea is so if a developer accidentally
			# introduces a name collision in an app module with a more fundamental 
			# system module, he will notice it right away during app testing, instead
			# of silently overriding the system command.

	def __init__(self):
		self._commandModuleList = []

	@property
	def modList(self):
		return self._commandModuleList

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
	#|			._allCommands
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
		
		_logger.info(f"Command interface is installing the {cmdModule} command module...")

		self.commandModules.addModule(cmdModule)


	def lookupCommands(
			cmdIF:TheCommandInterface,	# The entire command interface anchor.
			cmdID:str,					# Command identifier to lookup.
			inputLine:str,				# The input line that it must match against.
			anywhere:bool = False,		# If True, allow command to start anywhere.
			prefix:bool = False):		# If True, then search command prefixes.

		"""Look up the given command identifier in the installed modules
			of the command interface. Return a list of matching commands,
			in priority order. Each element of the list must satisfy all
			of the following criteria:

				1. If prefix=False, then the command's symbolic name
					must match the supplied command identifier cmdID
					exactly; otherwise, the supplied identifier must
					be a prefix of the command's symbolic name.

				2. The command's module must be currently active.

				3. If anywhere=False, or if the command's anywhere
					attribute if False, then the command's pattern
					must match from the *start* of the given input line;
					otherwise, it may match anywhere in the input line.
		"""

			# Initialize our result to be an empty command list.
		cmdList = []
		
			# This part is easy, we simply go through all of the
			# active modules, asking each of them to look up their
			# matching commands, and then we add their results to
			# the overall list.

		for cmdModule in cmdIF.commandModules.modList:
			
			_logger.debug(f"Looking for command {cmdID} in module: {cmdModule}.")

			if cmdModule.active:
				subList = cmdModule.lookupCommands(cmdID, inputLine,
												   anywhere, prefix)
				cmdList += subList

			# Return the accumulated list.
		return cmdList


	def findNonstdCmds(cmdIF, 
			inputLine:str,				# The input line that it must match against.
			anywhere:bool = False):		# If True, allow command to start anywhere.

		"""Find nonstandard-format commands in all modules matching the given
			input line."""

		cmdList = []

		for cmdModule in cmdIF.commandModules.modList:
			if cmdModule.active:
				subList = cmdModule.findNonstdCmds(inputLine, anywhere)
				cmdList += subList

		return cmdList


	def obtainCommandList(cmdIF, inputLine:str):

		"""Given a line of input, obtain and return a list of matching
			commands in active modules, sorted in priority order, that is,
			highest-priority commands first. This works as follows:

				1. First, we check to see if the line potentially *starts*
					with a standard-format command by matching it with
					the generic standard command pattern, _genericStdCmdPat.
					If it does, we'll go into a mode to look for standard
			   		commands at the start of the line *only*.

				2. If that doesn't yield anything, then we'll try searching
					to see if the standard pattern occurs *anywhere* in the
					line; if it does, we'll go into a mode to look for
					standard commands that can occur *anywhere* in the line.

				3. If that doesn't yield anything, then we'll try searching
					against nonstandard command patterns.
					
			In each of these cases, we verify each match against the
			command's pattern, and filter out commands from non-active
			modules.
		"""

			#|--------------------------------------------------------------
			#| First, check to see if the line matches the standard pattern.
			#| (Starting at the start of the line.

		match = _genericStdCmdPat.match(inputLine)
		if match:
			
			cmdId = match.group(1)		# Command identifier part of the match.
			#argList = match.group(2)	# Argument list, if any (or None).
				# (Currently unused.)

			# Now that we have extracted a potential command identifier,
			# we must try to look up commands matching that identifier.
			# First we look for exact matches; if that doesn't work, we
			# try prefix matches.

			cmdList = cmdIF.lookupCommands(cmdId, inputLine,
										   anywhere=False, prefix=False)

			if len(cmdList) >= 1:
				return cmdList

			cmdList = cmdIF.lookupCommands(cmdId, inputLine,
										   anywhere=False, prefix=True)

			if len(cmdList) >= 1:
				return cmdList

		#__/ End if match the standard command pattern (at start of line).

		
			#|--------------------------------------------------------------
			#| Alright, since that didn't work, next let's check to see if
			#| we can find the standard pattern anywhere in the line.

		match = _genericStdCmdPat.search(inputLine)
		if match:
			
			cmdId = match.group(1)		# Command identifier part of the match.
			argList = match.group(2)	# Argument list, if any (or None).

			# Now that we have extracted a potential command identifier,
			# we must try to look up commands matching that identifier.
			# First we look for exact matches; if that doesn't work, we
			# try prefix matches.

			cmdList = cmdIF.lookupCommands(cmdId, inputLine,
										   anywhere=True, prefix=False)

			if len(cmdList) >= 1:
				return cmdList

			cmdList = cmdIF.lookupCommands(cmdId, inputLine,
										   anywhere=True, prefix=True)

			if len(cmdList) >= 1:
				return cmdList

		#__/ End if match the standard command pattern (at start of line).

		
			#|------------------------------------------------------------
			#| All there is left to do at this point is to check to see if
			#| the line matches any commands with nonstandard formats.
			#| First check for them, constraining match to start of line.

		cmdList = cmdIF.findNonstdCmds(inputLine, anywhere=False)
			
		if len(cmdList) >= 1:
			return cmdList

			# If we get here, try again, but letting the pattern be anywhere.

		cmdList = cmdIF.findNonstdCmds(inputLine, anywhere=True)

		return cmdList	# Nothing else left to try.

	#__/ End singleton instance method commandInterface.obtainCommandList().


	def checkForCommand(cmdIF, action:Action_):		# WARNING: Circularity here?
	
		"""Examine the provided action to see if we could interpret it 
			as a command. (Generally this will only be the case for 
			speech acts.) If this is the case, then construct an 
			appropriate CommandAction instance for it and return that;
			otherwise, return None."""

		_logger.debug("cmdIF.checkForCommand(): About to check action "
					  f"{action} for commands.")

			# Does this type of action contain some piece of text that
			# could possibly be interpreted as a command line?  If so,
			# then retrieve it.

		if hasattr(action, 'possibleCommandLine'):

				# Retrieve that text.
			text = action.possibleCommandLine()
		
			_logger.debug("cmdIF.checkForCommand(): Retrieved a potential "
						  f"command line: [{text}].")

				# Alright, now obtain a list of potential matching commands.
			candidateCommands = cmdIF.obtainCommandList(text)

			_logger.debug("cmdIF.checkForCommand(): We found the following list"
						  f" of matching command types: {candidateCommands}.")

				# Our policy is to extract the first command from the list
				# and utilize it, unless it is marked unique but there are
				# other command types in the list. In which case, we need
				# to construct a RequestDisambiguationAction, and return
				# that instead.
			
			nCmdTypes = len(candidateCommands)
			if nCmdTypes == 0:
				_logger.debug("cmdIF.checkForCommand(): No matching command types"
							  " were found. Returning None.")
				return None

				# Retrieve the first command type.
			firstCommand = candidateCommands[0]

				# Does this command type expect to be uniquely indicated?
			expectsUniqueness = firstCommand.unique

				# If so, but there are other commands, then handle this.
			if expectsUniqueness and nCmdTypes >= 2:

				_logger.warn(f"cmdIF.checkForCommand(): Command {firstCommand}"
							 " expected to be uniquely selected, but the command line"
							 f" [{text}] can be interpreted in {nCmdTypes-1} other ways."
							 " Returning a disambiguation request action.")

					# RequestDisambiguationAction and returns it.
				return cmdIF.genDisambiguationRequest(text, candidateCommands)

			# If we get here, then it's safe to go ahead and construct
			# a CommandAction that interprets the given text as per the
			# selected command type.

				#----------------------------------------------------------------------
				# Examine the action's conceiver to determine the appropriate conceiver
				# for the command, and construct an appropriate command action.

			cmdInvoker = action.conceiver	# Who conceived the original action?
				# They're the ones invoking this command.

			cmdAction = firstCommand.genCmdAction(text, cmdInvoker)
			
			return cmdAction

		else:
			_logger.debug("cmdIF.checkForCommand(): Action has no "
						  "possibleCommandLine() method; returning None.")
			return None

	
	#def isCommand(self, text:str):
	#
	#	"""Is the given text invocable as a command?"""
	#
	#	return False	# Stub. (Not yet implemented.)

	
#__/ End public singleton class commandInterface.TheCommandInterface.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|				  END OF FILE:	 commands/commandInterface.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
