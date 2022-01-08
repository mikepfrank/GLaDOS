# helpApp.py

__all__ = [ 'The_Help_App' ]

from	infrastructure.logmaster	import getLoggerInfo, ThreadActor

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	commands.commandInterface	import	Command,CommandModule	# We'll subclass these.

from	infrastructure.utils		import	countLines		# Used in 'Help' app

from	.application			import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class	The_Help_Command(Command):

	"""The '/Help' command launches the Help app (if not already launched),
		moves its window to the bottom of the receptive field (if not
		already there) to call attention to it, and sets the input focus to it."""

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
