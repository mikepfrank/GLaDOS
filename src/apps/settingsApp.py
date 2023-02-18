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
	
	# def __init__(newAppCmdModule: The_SettingsApp_CmdModule, appName: str, application: Application_):
	# 	"""Instance initializer for the The_SettingsApp_CmdModule class.""""
	#		
	# 	acm = newAppCmdModule	# For convenience.
	#
	# 		# Do generic initialization for AppCommandModule instances.
	# 	super().__init__(appName, The_Settings_App())
	
	# def buildIntroText(thisAppCmdModule: The_SettingsApp_CmdModule):
	#
	# 	"""Build the introductory text for the help screen for this app.
	# 		We start with the default text, then add to it."""
	#
	# 	acm = thisAppCmdModule	# For convenience.
	#
	# 	# First let our superclass build its default introductory text.
	# 	acm._introText = super().buildIntroText()
	#
	# 	# Now add our application-specific stuff to it.
	# 	acm._introText += " This application allows you to view and " \
	# 		"modify the various settings in the system."
	#
	# 	return acm._introText


@singleton
class The_Settings_App(Application_):

	"""The Settings app can be used by the A.I. to adjust various
		settings within GLaDOS.	 These can be associated with major
		systems or subsystems of GLaDOS, or individual apps or
		processes."""

	# This sentence (suggested by DaVinci v3) will be automatically included in
	# the introductory text for the help screen for this app.
	appSpecificIntroText = "This application allows you to view and modify " \
		"the various settings in the system."

	#------------------------------------------------------------
	# Help-related attributes.

	## Here's the intro text that DaVinci v3 composed for the Settings app:
	# helpIntro = \
	#	"Welcome to the Settings application! This application allows you to " \
	#	"view and modify the various settings in the system. The following " \
	#	"commands are available when the Settings application has the command "\
	#	"focus:"
	#
	# However, we are now going to semi-automate the process of building the
	# introductory text for the help screen, as follows.  We will start with 
	# the default introductory text for all apps, which is defined in the 
	# base class Application_.  This will be just:
	#
	#	"Welcome to the <app name> application!"
	#
	# Then we will add to it any application-specific text, which in this case
	# is:
	#
	#	" This application allows you to view and modify the various settings
	#	in the system."
	#
	# Then finally, we'll ask the command module to add its introductory text
	# to the end of the string.  This will generically be:
	#
	#	" The following commands are available when the <app name> application
	#	has the command focus:"

	# MPF wrote the following intro text earlier, but it may be too long.
	# # Default introductory text that appears at the top of the help screen,
	# # after the module topic and before the list of commands.  
	# helpIntro = \
	# 	"This is the main help screen for the Settings app.  This app " \
	# 	"can be used by the A.I. to adjust various settings within " 	\
	# 	"GladOS.  These can be associated with major systems or " 		\
	# 	"subsystems of GladOS, or individual apps or processes."
