# settingsApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

#from	helpsys.helpSystem			import	HelpModule

from	commands.commandInterface	import	TheCommandInterface, Command

from	.appCommands				import	AppCommandModule

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

class The_Settigns_App: pass
class The_SettingsApp_CmdModule: pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@singleton
class	The_Settings_List_Command(Command):
	
	"""This command displays a list of all of the settings in the system."""
		# NOTE: Eventually we need to replace this with commands to navigate
		# through a hierarchy of settings modules.

	name = "list"	# The name of the command.

	usageText = "/list [<settingsModule>]"
		# The usage text for the command.  This is displayed on help screens
		# that show documentation for this command.

	shortDesc = "Displays a list of settings."
		# A short description of the command.  This is displayed on help
		# screens that show documentation for this command.

	longDesc = \
		"This command displays a list of all of the settings in the system," \
		" or a list of the settings in a specific settings module (optional)."

	cmdFormat = ""

	def __init__(self, cmdMod: The_SettingsApp_CmdModule, cmdName: str, cmdDesc: str, cmdHelp: str, cmdSyntax: str, cmdExample: str, cmdAliases: List[str] = None):

		"""Instance initializer for the The_Settings_List_Command class."""


		# Do generic initialization for Command instances.
		super().__init__(cmdMod, cmdName, cmdDesc, cmdHelp, cmdSyntax, cmdExample, cmdAliases)


	def execute(self, cmdArgs: List[str]) -> bool:

		"""Execute the command.  This method is called by the command
			interface when the user enters a command that matches this
			command's name or one of its aliases.  The command interface
			passes a list of the command's arguments to this method.  The
			method returns True if the command was successfully executed,
			or False if it was not."""

		# Get the command module that this command is associated with.
		cmdMod = self.getCommandModule()

		# Get the application that this command module is associated with.
		app = cmdMod.getApplication()

		# Get the command interface.
		cmdIF = TheCommandInterface()

		# Get the list of settings in the system.
		settings = app.getSettings()

		# If there are no settings, tell the user.
		if len(settings) == 0:
			cmdIF.print("There are no settings in the system.")
			return True

		# Display the list of settings.
		cmdIF.print("The following settings are available:")
		for setting in settings:
			cmdIF.print(setting)

		return True

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@singleton
class The_SettingsApp_CmdModule(AppCommandModule):

	"""This singleton class defines the command module for the Settings
		app.  The Settings app can be used by the A.I. to adjust various
		settings within GLaDOS.	 These can be associated with major
		systems or subsystems of GLaDOS, or individual apps or
		processes."""


	def __init__(newAppCmdModule: The_SettingsApp_CmdModule, appName: str, application: Application_):
		
		"""Instance initializer for the The_SettingsApp_CmdModule class.""""
			
		thisCmdMod = newAppCmdModule	# For convenience.
	
		# Do generic initialization for AppCommandModule instances.
		super().__init__("Settings", The_Settings_App())
			# Note this should call the .populate() method below.

			# Go ahead & install this module in the global command interface.
		cmdIF = TheCommandInterface()
		cmdIF.installModule(thisCmdMod)


	def populate(self) -> None:

		"""Populate the command module with the commands that it
			supports.  This is called automatically when the command
			module is instantiated."""
		
		# Here we add all of the commands that are specific to this app
		# to the command module.  We do this by calling the addCommand()
		# method of the command module, passing it the command object
		# that we want to add.  The command object is created by calling
		# the constructor for the command class, passing it the command
		# module that it is associated with, and any other arguments
		# that the command's constructor requires.



		# Let our superclass finish the job.
		return super().populate()
			# This adds generic application commands '/close', etc. to 
			# the app's command module.

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


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
