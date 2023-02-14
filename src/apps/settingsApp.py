# settingsApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	helpsys.helpSystem			import	HelpModule

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Never mind this; I think we'll just let the Settings app inherit its help
# module construction procedure from the base class, Application_.

#@singleton
#class The_SettingsApp_HelpModule(HelpModule):
#
#	pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@singleton
class The_Settings_App(Application_):

	"""
	The Settings app can be used by the A.I. to adjust various
	settings within GLaDOS.	 These can be associated with major
	systems or subsystems of GLaDOS, or individual apps or
	processes.
	"""

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

