# helpApp.py

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

			# Now we can go ahead and tell our window to display
			# the help message contents.

			# First, size the window the exactly fit the message.

		self.window.nRows = countLines(helpMsg)
			# .nRows should be a property
			# countLines() should go in infrastructure/utils

			# Now, display the text.
		self.window.addText(helpMsg)

