# infoApp.py

__all__ = [ 'The_Info_App' ]

from os import path

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from infrastructure.logmaster	import getLoggerInfo, ThreadActor

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	config.configuration		import	TheAIPersonaConfig
		# Singleton that provides the configuration of the current AI persona.

from	.application			import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Info_App(Application_):

	"""
		The_Info_App			    [public singleton class--GLaDOS application]
		============

			The is a singleton class implementing the 'Info App' or
			"information application" that is available within GLaDOS.

			The idea behind this app is that it maintains and displays
			certain critical contextual information that the A.I. needs
			to know, including its identity, life circumstances, and
			its present high-level goals.  Its window normally remains
			pinned near the top of the A.I.'s receptive field.

			Once the Information app is launched, it allows the A.I. to
			edit certain information such as its high-level goals.

			NOTE: This is one of the few apps that is generally launched
			automatically at system startup.
																			 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# NOTE: The feature to allow the AI to view/edit goals is not
		# yet implemented. For now the Info app just displays the
		# contents of a static text file. Also, we've decided that the
		# goal-editing function will be handled by a separate 'Goals' app.

	def appSpecificInit(self, conf:dict):

		"""This method performs application-specific initialization
				for the Info application, at app creation time.  By
				the time this is called, our window has already been
				created, but is not yet displayed.."""

		_logger.debug("infoApp.appSpecificInit(): Initializing Info app...")

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

			#-----------------------------------------------------
			# Next, we need to get the name of the info text file
			# (relative to that directory). This comes from our
			# app-specific configuration data.

		infoFilename = conf['info-filename']

			#------------------------------------------------------
			# Next, we need to construct the full pathname of the
			# info text file.

		infoPathname = path.join(aiDataDir, infoFilename)

			#------------------------------------------------------
			# Next, we need to actually load the info text from the
			# appropriate data file in that directory.

		with open(infoPathname) as file:
			infoText = '\n' + file.read() # + "\n"
				# Note: We are padding with blank lines both
				# before and after the file contents. This is
				# for visual appearance. But, alternatively
				# we could have automated padding within the
				# window.

		#_logger.debug("Loaded inital info text:\n" + infoText)

			#--------------------------------------------------
			# Next, we're going to turn on word-wrapping in our
			# window so that the text will automatically wrap
			# neatly to fit within our window width.  Also,
			# we'll turn on auto-size so that the vertical size
			# of the window will shrink or stretch to fit our
			# text.

		win = self.window

		win.wordWrap = True		# Turn on word-wrapping.
		win.autoSize = True		# Turn on auto-sizing

		_logger.info(f"Window {win.title} has wordWrap={win.wordWrap}.")

			#----------------------------------------------
			# Finally, we have our window display the text.

		win.addText(infoText)

	##def start(inst):
	##	"""Starts up the Info application."""
	##	# Right now, the start method for the Info app doesn't need
	##	# to do anything particular, because the app has no dynamic
	##	# behavior yet.  So, just dispatch to our parent class.
	##	# However, we may add some dynamic behavior to the app later.
	##	super(The_Info_App.__wrapped__, inst).start()

#__/ End class Info_App.


