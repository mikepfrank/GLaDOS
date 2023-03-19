# helpApp.py

__all__ = [ 'The_Help_App' ]

from	infrastructure.logmaster	import getLoggerInfo, ThreadActor

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	entities.entity			import	The_HelpApp_Entity

from	commands.commandInterface	import	Command,CommandModule	# We'll subclass these.

from	helpsys.helpSystem			import	HelpModule	# We'll subclass this.

from	infrastructure.utils		import	countLines		# Used in 'Help' app

from	.application			import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class	The_Help_Command(Command):

	"""The '/Help' command launches the Help app (if not already launched),
		moves its window to the bottom of the receptive field (if not
		already there) to call attention to it, and sets the input focus to it."""

	initName = 'Help'	# Initialize name of this command to 'Help'.

		# Rather than writing a regex like the below for each prefix-invokable
		# command, wouldn't it be a heckuva lot better to just code up a general
		# recipe for recognizing these kinds of commands? Just, like, specify
		# that it's a property of a given command that it's prefix-invocable,
		# and then either generate the regex automatically, or use some non-
		# regex-based algorithm to identify the command.
		#
		# ^ NOTE: Automatic regex generation is implemented now, supposedly.
		#		(See Command._autoInitCmdFormat().)

	#initCmdFmt = '^[^/]*/[Hh]([Ee]([Ll](Pp)?)?)?(?:\\s+(\\S.*))?$'
		# Beginning of line, any number of non-slash characters, followed
		# by a slash and then any initial prefix of 'Help' (case-independent),
		# optionally followed by whitespace and then anything else to end of line.

	def initHandler(restOfLine:str):
		"""Initial invocation handler for the Help command. This should
			launch the Help app (if not already launched), move its window
			to the bottom of the receptive field (if not already there) to
			call attention to it, and set the input focus to it."""

		pass	# Implement me.

	#def __init__(theHelpCommand:The_Help_Command):
	#	"""Instance initializer for the /Help command. Just passes appropriate
	#		arguments to"""

	#pass	# TO DO: Fill in implementation.


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

		The_Help_Command(module=Thehelpcmdmodule)
			# Creates the '/Help' command.


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
@singleton
class The_Help_App(Application_):

	"""
	The "Help" tool simply displays some basic information
	about how to use GLaDOS (for the A.I.'s benefit).
	"""

	# Note the string literal given here is just a default Help
	# message, which may be overridden by the main-msg attribute
	# in the system config file.

	_helpMsg = """

		 This is the main Help message for GLaDOS, the
		Generic Lifeform and Domicile Operating System,
		(c) 2020 Metaversal Contructions.

		 At the prompt, you may enter a command line starting
		with '/', or type free-form text to add to your history.

		 Available command words include:

						/Help /Info /Settings /Memory /ToDo
						/Diary /Browse /Comms /Writing /Unix

		 Note: Command words are not case-sensitive, and you may
		abbreviate them using any unique prefix.

		"""[1:-1]

	def appSpecificInit(self, conf:dict):

		self.entity = The_HelpApp_Entity()

			# Override the default help message with the message
			# from the 'main-msg' config attribute, if present.

		if 'main-msg' in conf:
				self._helpMsg = conf['main-msg']

		helpMsg = self._helpMsg

		win = self.window

		win.wordWrap = True		# Turn on word-wrapping.
		win.autoSize = True		# Turn on auto-sizing

		_logger.info(f"Window {win.title} has wordWrap={win.wordWrap}.")

			# Now we can go ahead and tell our window to display
			# the help message contents.

			# First, size the window the exactly fit the message.
		#win.nRows = countLines(helpMsg) # No longer needed due to autoSize

			# .nRows should be a property
			# countLines() should go in infrastructure/utils

			# Now, display the text.
		win.addText(helpMsg)

#__/ End class The_Help_App.
