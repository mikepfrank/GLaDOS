# settingsApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	helpsys.helpSystem			import	HelpModule

from	.appCommands				import	AppCommandModule

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

class The_Settigns_App: pass
class The_SettingsApp_CmdModule: pass

@singleton
class The_SettingsApp_CmdModule(AppCommandModule):

	"""This singleton class defines the command module for the Settings
		app.  The Settings app can be used by the A.I. to adjust various
		settings within GLaDOS.	 These can be associated with major
		systems or subsystems of GLaDOS, or individual apps or
		processes."""
	
	def __init__(newAppCmdModule: The_SettingsApp_CmdModule, appName: str, application: Application_):

		acm = newAppCmdModule	# For convenience.

			# Do generic initialization for AppCommandModule instances.
		super().__init__(appName, The_Settings_App())
	
	def buildIntroText(thisAppCmdModule: The_SettingsApp_CmdModule):

		"""Build the introductory text for the help screen for this app.
			We start with the default text, then add to it."""

		acm = thisAppCmdModule	# For convenience.

		# First let our superclass build the default introductory text.
		acm._introText = super().buildIntroText()

		# Now add our application-specific stuff to it.
		acm._introText += " This application allows you to view and " \
			"modify the various settings in the system."

		return acm._introText

@singleton
class The_Settings_App(Application_):

	"""The Settings app can be used by the A.I. to adjust various
		settings within GLaDOS.	 These can be associated with major
		systems or subsystems of GLaDOS, or individual apps or
		processes."""

	# Default introductory text that appears at the top of the help screen,
	# after the module topic and before the list of commands.  
	helpIntro = \
		"This is the main help screen for the Settings app.  This app " \
		"can be used by the A.I. to adjust various settings within " 	\
		"GLaDOS.  These can be associated with major systems or " 		\
		"subsystems of GLaDOS, or individual apps or processes."

	def getHelpIntro(self):
		"""
		"""
		return self.__doc__

