# helpApp.py

__all__ = [ 'The_Help_App' ]

from	infrastructure.logmaster	import getLoggerInfo, ThreadActor

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	commands.commandInterface	import	Command,CommandModule	# We'll subclass these.

from	helpsys.helpSystem			import	(
			HelpModule,		# We'll subclass this.
			TheHelpSystem
		)

from	infrastructure.utils		import	countLines		# Used in 'Help' app

from	.application			import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class	HelpCommand_(Command):		# Dummy abstract superclass for help commands.
	# (Currently, we just use this in type hints.)
	pass

@singleton
class	The_Help_Command(HelpCommand_):

	# NOTE: This is the version of the /Help command that takes priority 
	# when the Help app is active, so that we can process requests for
	# help on individual commands. Note this is separate from the app-
	# launch command that launches the Help app if it's not alreadyy
	# running. However, if the /help command is provided bare with no
	# arguments, then the version of the Help command here will not
	# match, and instead the app-launch command will be invoked, which
	# will have the effect of refreshing the Help app's window (bringing
	# it to the front, if it's not already there, and moving it to the
	# bottom of the receptive field, if it's not already there).

	"""The '/help <command-or-topic>' command is used for bringing up 
		help screens for individual commands, and other topics that have 
		help modules currently installed. It searches the list of currently
		installed help modules for a module with a name that matches the
		<command-or-topic> argument. If it finds one, it displays the help
		screen for that module in the Help app's window. If it doesn't find
		one, it displays an error message on the console."""

	name = 'help'	# Initialize name of this command to 'help'.

	# The usageText, shortDesc and longDesc attributes are used when generating 
	# a HelpItem for this command. 

	usageText = '/help (<command-name> | <help-module-name> | <topic-name>)'

	shortDesc = 'Displays help screens for individual commands and topics.'

	longDesc = "The '/help <command-or-topic>' command is used for bringing "  \
		"up help screens for individual commands, and other topics that have " \
		"help modules or help items currently installed. It searches the list " \
		"of currently installed help modules and help items for a module or "  \
		"item with a name or topic that matches the <command-or-topic> "	   \
		"argument. If there are multiple matches, the first match found is "   \
		"displayed. Items/modules nested under the current help module are "   \
		"searched first, then items/modules nested under the root help "	   \
		"module. In each case, the search is depth-first. If it finds a "	   \
		"match, it displays the help screen for that module/item in the Help " \
		"app's window. If it doesn't find a match, it displays an error "	   \
		"message on the GLaDOS console."

	needsArgs = True	# This command requires arguments.
		# Note that we have to set this to True, so that this command doesn't
		# override the /Help app-launch command when the Help app is active. If 
		# we let this be False, then the app-launch command will never be 
		# invoked when the Help app is active, and the user won't be able to 
		# refresh the Help app's window.

	# The following regex is used to parse the argument list for this command.
	# Currently, the /help command only takes a single argument, which is the
	# name of the command or topic for which help is requested. This may be any
	# alphanumeric identifier, including underscores and hyphens. It must begin
	# with an alphabetic character or underscore. It may not contain any 
	# whitespace. (Note that the regex below is not case-sensitive.)

	argListRegex = r'(?P<argList>(?P<id>[a-zA-Z_][a-zA-Z0-9_-]*))'
		# Usage example for this regex:
		#	>>> import re
		#	>>> argListRegex = r'(?P<argList>(?P<id>[a-zA-Z_-][a-zA-Z0-9_-]*))'
		#	>>> re.match(argListRegex, 'foo')
		#	<_sre.SRE_Match object; span=(0, 3), match='foo'>
		#	>>> re.match(argListRegex, 'foo').groupdict()
		#	{'argList': 'foo', 'id': 'foo'}
		

	def handler(theHelpCommand:HelpCommand_, groups:list=None):

		"""This method is called by the Command class's stanard command	line 
			parser, when it has successfully parsed the command line for this 
			command. It takes the parsed group list and uses it to handle
			further processing of the command line."""

		cmd = theHelpCommand	# Just to make the code below more readable.

		if groups is None:	# Shouldn't happen, but just in case...
			# Really this should give some kind of error
			return

		# The first group is the entire argument list.	
		if len(groups) >= 1:
			argList = groups[0]
		else:
			argList = None

		# Parse the argument list using the Command class's default parser.
		cmd.parseArgs(argList)
			# This will automatically dispatch to our .handle() method, below.


	def handle(theHelpCommand:HelpCommand_, groups:list=None, groupDict:dict=None):

		"""This method is called by the Command class's default argument
			parser, when it has successfully parsed the argument list for
			this command. It takes the parsed group list and the parsed
			group dictionary, and uses them to process the command."""

		cmd = theHelpCommand	# Just to make the code below more readable.

		# if groups is None:	# Shouldn't happen, but just in case...
		# 	# Really this should give some kind of error
		# 	return

		if groupDict is None:	# Shouldn't happen, but just in case...
			# Really this should give some kind of error
			return

		# # The first group is the entire argument list.	
		# # (We don't actually use this for anything though.)
		# if len(groupDict) >= 1:
		# 	argList = groupDict['argList']
		# else:
		# 	argList = None

		# The second group is the identifier for the command, module or 
		# topic for which help was requested.
		if len(groupDict) >= 2:
			identifier = groupDict['id']
		else:
			identifier = None

		# If we get here, then the user typed '/help <command-or-topic>' with
		# one argument which was formatted like an identifier. In this case, 
		# we want to search for a help module or help item that matches the 
		# command or topic name, and display the help screen for that module/
		# item in the Help app's window.

		helpSys = TheHelpSystem()
		module = helpSys.lookupModule(identifier)
		if module is not None:
			# We found a help module that matches the identifier.
			# Display the help screen for that module in the Help app's window.
			helpSys.displayHelpModule(module)
			return


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class	The_Help_CmdModule(CommandModule):

	"""This singleton class implements the command module for the Help app.
		It provides the '/Help' command, which both launches the app and
		navigates to the help screens for various individual commands."""

	#def __init__(theNewHelpCmdModule:The_Help_CmdModule):
	#
	#	"""Singleton instance initializer for the The_Help_CmdModule class.
	#		Its job is to construct the command module by adding all of its
	#		individual commands and subcommands to it."""
	#	
	#	cmdmod = theNewHelpCmdModule
	#
	#		# Calls the default instance initializer for CommandModules.
	#	super(The_Help_CmdModule, cmdmod).__init__()

	def populate(theHelpCmdModule):

		helpCmd = The_Help_Command(module=theHelpCmdModule)
			# Creates the '/help' command.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Note to self: Does the 'Help' app really even need its own help module?  Or is
# the top-level screen of the help system already sufficient?

@singleton
class The_Help_HelpModule(HelpModule):

	"""This singleton class implements the help module for the Help
		app. It provides an overview of the app, and documents its
		associated commands and subcommands."""

	pass	# TO DO: Fill in implementation.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The_Init_HelpModule singleton class is a special help module that is the first
# one displayed when the Help app is launched. It provides a brief introduction 
# to GlaDOS and its applications.

@singleton
class The_Init_HelpModule(HelpModule):

	"""This singleton class implements the initial help module for the Help
		app. It provides a brief introduction to GlaDOS and its applications."""

	name = 'intro'		# The name of this help module.
		# User can get to this help module by typing '/help intro'.

	topicName = 'Introduction'		# The name of the topic for this help module.
		# User can get to this help module by typing '/help introduction'.

	topicDesc = 'Welcome to GLaDOS'	# The description of the topic for this help module.

	# Default introductory text for this help module. Note that this can be
	# overridden using the 'intro-text' configuration parameter in the section
	# for the Help app in the GLaDOS configuration file.

	introText = \
		"This is the introductory Help screen for GladOS, Gladys' Lovely and " \
		"Dynamic Operating System, Copyright (c) 2020-23 Metaversal " \
		"Constructions." \
		"\n\n" \
        "At the prompt, you may enter a command line starting with '/', or " \
		"type a free-form paragraph of text to add to your cognitive " \
		"history.  Available command words include:"\
		"\n\n" \
        "\t/Goals /Settings /Memory /ToDo /Help" \
        "\t/Diary /Browse /Comms /Writing /Unix" \
		"\n\n" \
		"Note: Command words are not case-sensitive, and you may abbreviate " \
		"them using any unique prefix.  For detailed help on any command, " \
		'type "/Help <command>".' \
		"\n\n"

	# # LOL! Version written by Copilot:
	# introText = """\
	# 	Welcome to GLaDOS, the Generalized Language and Data Operating System.
	# 	GLaDOS is a general-purpose, open-source, cross-platform, multi-user
	# 	operating system for the A.I. (Artificial Intelligence) community.
	# 	"""



	# TO DO: Fill in the rest of the implementation.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Help_App(Application_):

	"""
		The_Help_App			    [public singleton class--GLaDOS application]
		============

			The "Help" app initially displays some basic information about how 
			to use GLaDOS (for the A.I.'s benefit).  It also allows the user to 
			navigate the interactive help system to bring up help screens for
			individual commands or subcommands, and other topics that have help 
			modules currently installed.

			The app's window normally is slid, upon first being opened, down to 
			a floating location initially near the bottom of the AI's receptive 
			field, just above any anchored windows and the pinned field elements 
			such as the input area and the prompt separator. Currently it moves 
			with the history data, and may scroll off the top of the receptive 
			field if not refreshed. When refreshed, it will slide back down to 
			its initial floating location.

		USAGE:
		======
		
			Currently available /help command formats include:

				- /Help - Open or refresh the Help app.

				- /help <command-or-topic> - Display help for 
					the given command or topic.
				
				- /help <command>-<subcommand> - Display help
					for the given subcommand.
	"""

	# NOTE: This may be displayed at the bottom of the Help app's window to
	# give the user a hint about how to use the variants of the /help command.
	usageHint = "USAGE: '/help ( <command> | <command>-<subcommand> | <topic>)'."


	# Note the string literal given here is just a default Help
	# message, which may be overridden by the main-msg attribute
	# in the system config file.

	_helpMsg = """

		 This is the main Help message for GLaDOS, Gladys'
		Lovely and Dynamic Operating System, (c) 2020-23 
		Metaversal Contructions.

		 At the prompt, you may enter a command line starting
		with '/', or type free-form text to add to your history.

		 Available command words include:

			/Help /Info /Settings /Memory /ToDo
			/Diary /Browse /Comms /Writing /Unix

		 Note: Command words are not case-sensitive, and you may
		abbreviate them using any unique prefix.

		"""[1:-1]

	def appSpecificInit(self, conf:dict):

		"""This method is called by the Application base class's __init__()
			method to perform any application-specific initialization."""

		# First, call the base class's appSpecificInit() method to
		# perform any initialization that it needs to do.

		super().appSpecificInit(conf)

		# NOTE: The following code is no longer needed, since the
		# Help app now uses the new HelpModule classes to manage the
		# contents of its window, and The_Init_HelpModule subclass
		# is now used to display the initial help message. However,
		# I'm leaving it here for now, in case I need to refer to
		# it later, and possibly for backward compatibility.

			# Override the default help message with the message
			# from the 'main-msg' config attribute, if present.

		if 'main-msg' in conf:
				self._helpMsg = conf['main-msg']

		helpMsg = self._helpMsg

			# Set up the window for the Help app.

		win = self.window

		win.wordWrap = True		# Turn on word-wrapping.
		win.autoSize = True		# Turn on auto-sizing

		_logger.info(f"Window {win.title} has wordWrap={win.wordWrap}.")

			# Update the current help screen to show the initial help module.
			# (Note that this does not actually cause the Help app to launch!)

		self.updateHelpScreen(The_Init_HelpModule())

		# Deprecated code follows:
		#
		# 	# Now we can go ahead and tell our window to display
		# 	# the help message contents.
		#
		# win.addText(helpMsg)

	def updateHelpScreen(self, helpModule:HelpModule=None):

		"""This method should be called whenever we want to update the Help 
			app's window with the contents of the given help module.  The
			help system's current help module is also set to the given help 
			module.  If the helpModule argument is None, then the current 
			help module is not changed, but the help screen is redisplayed
			to show the current help module (in case it has changed)."""

		helpSys = TheHelpSystem()	# Get the Help system singleton.

		# If no help module was given, then use the current help
		# module; otherwise, change the current help module to
		# the given one.

		if helpModule is None:
			helpModule = helpSys.currentModule	# Uses getter method.
		else:
			# See if the given help module is already the current
			# help module.  If so, then we don't need to do anything
			# else, so just return.

			if helpModule is helpSys.currentModule:
				return

			helpSys.currentModule = helpModule	# Uses setter method.

		# If we get here, then assume we may need to actually update
		# the contents of the Help app's window.

		# Do what we need to do to update the Help app's window.

		win = self.window

			# First, clear the window contents.

		win.clearText()		# Clear old window text (but postpone update).

			# Now add the new help module's text to the window.

		win.addText(helpModule.helpScreenText)

		win.redisplay(loudly=False)
			# Redisplay the help window on the receptive field, but without
			# waking up the AI if it's asleep.
		
#__/ End class The_Help_App.
