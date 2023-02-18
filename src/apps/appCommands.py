# appCommands.py
# This module defines command types that apply to all apps 
# or to the app system as a whole.

from sys import stderr

		#|======================================================================
		#|	1.3. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|==================================================================
			#|	1.3.1. The following modules, although custom, are generic 
			#|		utilities, not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				#| 1.3.1.1. The logmaster module defines our logging framework.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.logmaster	import getLoggerInfo

	#----------------------------------------------------------
	# Go ahead and create or access the logger for this module,
	# and obtain the software component name for our package.

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.

#from infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	entities.entity		import The_AppSystem_Entity		# Reps us.

from	supervisor.action	import output	# For output to the GLaDOS screen.

from	commands.commandInterface	import	(

		Command,		# We subclass this.
		CommandModule	# We subclass this.
		
	)

# Dummy class declarations. (Definitions not available in this module. Used only as type designators.)
class Application_: pass	# Abstract class for applications.
class AppSystem_: pass		# Abstract class for the whole application system.

# Forward declarations.
class AppCommandModule: 	pass	# Class for command modules for apps.
class AppLaunchCommand: 	pass	# Class for app-launch commands.
class The_AppSys_CmdModule: pass	# Top-level command module for app system.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	# NOTE: Normally, we wouldn't need this global, but there's a problem which
	# is that the singleton constructor gets called recursively from within itself
	# before it's finished being created, which leads to it being created twice,
	# which causes unexpected results (._appSys member not being available).
	# This global is added as a hack to work around this problem.

global _the_appSys_cmdModule	# The top-level command module object for the app system.
_the_appSys_cmdModule = None	# Not yet created at Python module load time.

	# Here's a special "constructor" function for the above global variable to 
	# work around the above-mentioned issue with the singleton construction.
def the_appSys_cmdModule(appSys:AppSystem_ = None):
	
	global _the_appSys_cmdModule

	_logger.info("        [Apps/Init] Entered the_appSys_cmdModule() to create/retrieve the command module for the application system.")

		# If the global 'singleton' object isn't yet initialized, then we need to initialize it here.
	if _the_appSys_cmdModule is None:

		_logger.info("        [Apps/Init] the_appSys_cmdModule(): The application "
					 "system's command module hasn't been created yet, so I'll create it.")

		_the_appSys_cmdModule = The_AppSys_CmdModule(appSys)	# Call 'singleton' (not really) constructor.
			# This assignment is redundant because the constructor also does it. But this is harmless

		return _the_appSys_cmdModule	# Now return it.

	else:
		_logger.info("        [Apps/Init] the_appSys_cmdModule(): The application system's command module is already being initialized, so I'll just return it.")

		return _the_appSys_cmdModule	# It's already started being created; just return it. 


class AppCommandModule(CommandModule):
	"""
		appCommands.AppCommandModule					 		  [public class]
		
			This is the base class for all command modules for apps.  It 
			provides the basic functionality for all apps, including the 
			ability to launch the app, to foreground the app, and to 
			activate the app's command module. Maybe also commands to
			hide, suspend, resume, and quit the app. It can also include
			subordinate command modules for the app, including modules
			containing commands and/or subcommands that are specific to 
			the app which are activated when the app has the command focus.
	"""
	
	def __init__(newAppCmdModule:AppCommandModule,
				appName:str,				# A capitalized app name to use, like 'Goals'.
				application:Application_	# The application this command module is associated with.
			):
					
		"""Instance initializer for app command modules."""

		acm = newAppCmdModule	# For convenience.

		#|----------------------------------------------------------------------
		#|	Set up some fields appropriately for a generic application command 
		#|	module.

		# Store the value of the appName argument name giving the name of the 
		# app this command module is for.
		acm._appName = appName	# The capitalized name of the app, like 'Goals'.

		# Set the name of this command module (for debugging).
		acm._name = f"{appName}AppCmdModule"

		# Set the default help topic name for this command module.
		acm._topicName = appName  
			# The capitalized name of the app, like 'Goals'.

		# Set the help topic description for this command module.
		acm._topicDesc = f"Commands for the {appName} application."

		# Generate default intro text for this application's help screen.
		acm._introText = f"Welcome to the {appName} application."
			# This should be overridden or added to with more
			# specific content by the app's command module's 
			# subclass constructor.

		# First do generic initialization for all command modules.
		super().__init__(desc = f"{appName} app's command module")
		
		acm._application = application


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	
	
	@property
	def appName(newAppCmdModule:AppCommandModule) -> str:
		"""Return the app name for this command module."""
		return newAppCmdModule._appName

	def genHelpText(thisAppCmdModule:AppCommandModule) -> str:
		"""
			Generates a string containing help text an app's command module.
		"""

		self = thisAppCmdModule		# For convenience.

		helpText = f"The following commands are available when the {self.appName} application has the command focus:\n"
		helpText += self._commands.genHelpText()

		return helpText

	def initIntroText(thisAppCmdModule:AppCommandModule, introText:str) -> None:

		"""Initializes the intro text for this app's command module."""

		self = thisAppCmdModule		# For convenience.

		self._introText = introText

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AppLaunchCommand(Command):
	"""
		appCommands.AppLaunchCommand					 		  [public class]
		
			An app-launch command, such as '/Goals', is a special type of 
			command that launches an app (if not already launched), or 
			foregrounds it (if it was already launched).  To launch an 
			app typically involves the following steps:
		
				(1) Starting up the app (if it was not already started 
					earlier). This starts any background processes 
					associated with the app.
			
				(2) Creating the app's window (or windows, if it has >1 
					window).
			
				(3) Opening the app's window on the receptive field (using 
					its default initial placement).
					
				(4) Installing the app's command module (if it was not 
					already installed).  Possibly also activating the app's
					command module (if we want the app's commands to be
					available whether or not the app is foregrounded).
				
				(4) Foregrounding the app (see below).
			
			To foreground an app typically involves the following steps:
		
				(1) If the app is not already located at its preferred 
					initial placement (e.g., SLIDE_TO_BOTTOM), then we put 
					it there.
					
				(2) Activating the app's command module, if it was not already
					activated--this means its internal commands become available
					for invocation through the GLaDOS command interface.
				
				(3) Give the app the command focus. This means that generic
					app commands and window commands will be directed to that
					specific app (and to its main window). The app that has 
					the command focus is visually indicated with different 
					window decorations (e.g., '===' instead of '~~~' for 
					horizontal borders, command hints in lower border).
					[NOTE: This is not yet implemented.]
	"""

	# NOTE: The app-launch commands are all created after all of the apps
	# have been created and registered. Thus, it's our responsibility to
	# make sure that the app-launch commands insert themselves into the
	# applications' respective command modules, so that the CommandHelp-
	# Items for these commands will be shown in the application's help 
	# module, as well as in the app system's help module.  This is done 
	# in the AppLaunchCommand constructor below.

	def __init__(newAppLaunchCmd:AppLaunchCommand,
				appName:str,	# A capitalized app name to use, like 'Goals'.
				application:Application_	# The application to launch.
			):
					
		"""Instance initializer for app-launch commands. Constructs a custom
			unique format string."""

		cmd = newAppLaunchCmd	# Shorter name for this command.
		app = application		# Shorter name for the app to launch.

		cmd._app = app		# Remember our app.
		
			#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	Here, we put together a regex for purposes of parsing this
			#|	specific app-launch command.  It has the generic format:
			#|
			#|						/<appName> [<args>]
			#|
			#|	where <appName> is the app's name (one word), and <args> is an
			#|	optional argument list. The angle brackets '<>' denote 
			#|	variables, and are not a literal part of the command line, The
			#|	square brackets indicate that the argument list is optional, 
			#|	and are not a literal part of the command line. The space 
			#|	after '<appName>' represents any number of whitespace (space or 
			#|	TAB) characters.  If the argument list is not present, then the 
			#|	whitespace is not required to be present either.
		
		# No longer needed, because this is a standard command format, and its regex is auto-generated.
		#fmtStr = f"^/{appName}(?:\\s+(\\S.*)?)?$"
		
			# We already know what command module we're in...
		appSysCmdMod = the_appSys_cmdModule()	# Fetch this 'singleton'.
				# Note this isn't actually a @singleton due to a circularity problem.

			# Initialize some instance variables appropriately.

		cmd.name 		= appName		# Use the app's name as the command name.
		cmd.usageText 	= f"/{appName}"	# The usage text for this command. Simple!
		cmd.shortDesc 	= f"Launch/refresh the {appName} app."	# A short description of this command.
		cmd.longDesc 	= f"Launches the {appName} app, or refreshes it if it's already running."	
			# A long description of this command.
		cmd.takesArgs 	= False	# The app-launch command doesn't allow any argument list yet.
		cmd.cmdModule 	= appSysCmdMod	# The app-sys command module singleton.

		# Now dispatch to default initialization for Command instances.
		super(AppLaunchCommand, cmd).__init__()

		# Instead of passing all these things as arguments to the 
		# superclass initializer, we now set them as instance variables 
		# above, and then call the superclass initializer, which will
		# notice they're already set. Because, this just seems more 
		# straightforward?
		#
		# super(AppLaunchCommand, cmd).__init__(
		# 	name = appName,		# Use the app's name as the command name.
		# 	usageText = f"/{appName}",	# The usage text for this command. Simple!
		# 	shortDesc = f"Launch/refresh the {appName} app.",	
		# 		# A short description of this command.
		# 	longDesc = f"Launches the {appName} app, or refreshes it if it's already running.",	
		# 		# A long description of this command.
		# 	takesArgs = False,	# The app-launch command doesn't allow any argument list yet.
		# 	cmdModule = appSysCmdMod)	# The app-sys command module singleton.
			

	def handler(thisAppLaunchCmd:AppLaunchCommand, groups:list=None):
	
		"""This is the handler method that is called when a generic app-launch
			command is invoked. The <groups> argument, if present, is a list
			of match groups; it should include the argument list (if any)."""
			
		cmd = thisAppLaunchCmd
		
		app = cmd._app	# This gets the application that we're supposed to start.
		
		if groups is None:
			# Really should give some kind of error
			return

		# NOTE: The auto-generated command regex (which we use for app-launch
		# commands) doesn't even include a match group for the command word, so
		# we don't need to worry about extracting it here. (Commented out.)
		#
		#if len(groups) >= 1:
		#	cmdWord = groups[0]
		#else:
		#	cmdWord = None

			# Currently the app-launch commands don't even use argument lists,
			# but this code will be needed in the future if that changes.
		if len(groups) >= 1:
			argList = groups[0]
		else:
			argList = None

		_logger.info(f"Handling app-launch command for app {app} with "
					 f"argList='{argList}'.")

		app.launch()	# Launch the app (if not already launched).
			# (This automatically also foregrounds the app, whether or
			# not it was launched.)

		output(The_AppSystem_Entity(),
			   f"Launched/refreshed the {app.name} app.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Normally we would make the following be a singleton class, but this breaks 
# badly due to a circularity problem.  Instead, use the function 
# 
# 						the_appSys_cmdModule() 
# 
# above to construct the unique instance .
#@singleton

class	The_AppSys_CmdModule(CommandModule):

	"""The app-sys command module is responsible for managing all of the
		high-level commands associated with the application system.  This
		includes the app-launch commands for all of the individual apps 
		in the system."""
	
	def __init__(theNewAppSysCmdMod:The_AppSys_CmdModule, appSys:AppSystem_=None):
		"""Extends CommandModule's instance initalizer to also remember a 
			pointer to the overarching application system."""

		global _the_appSys_cmdModule	# Reference special global as a hack to handle recursive construction.

		_logger.info("        [Apps/Init] The_AppSys_CmdModule(): Trying to create the app-system command module.")

		module = theNewAppSysCmdMod

			# Go ahead and 'install' this object (if new) before we even finish initializing it.
		if _the_appSys_cmdModule is None:
			_logger.info("        [Apps/Init] The_AppSys_CmdModule(): I'm stashing this nascent object for later use.")
			_the_appSys_cmdModule = module	# Remember a reference to this new object we're constructing so we don't try to re-construct it.
		else:								# We shouldn't really get here, but just in case.
			return _the_appSys_cmdModule	# Just return the existing one.

			# If ._appSys is not already initialized, initialize it from our optional argument.
		if not hasattr(module, '_appSys'):
			if appSys is None:
				_logger.error("        [Apps/Init] The_AppSys_CmdModule(): Trying to initialize "
							  "the app-system command module with a null app-system!")
			else:
				_logger.info("        [Apps/Init] The_AppSys_CmdModule(): The app-system command "
							 "module is being initialized for a (non-null) app-system.")
				module._appSys = appSys

			# Default initialization for command modules.
		super(The_AppSys_CmdModule, module).__init__(desc="'command module for application system'")
		# .__wrapped__ isn't needed because this isn't really a singleton.
	
	
	def populate(thisAppSysCmdMod:The_AppSys_CmdModule):
	
		"""Populates this command module with all of its commands."""
		
		module = thisAppSysCmdMod
		appSys = module._appSys
		apps = appSys.apps

		# So far, the only thing that's in the AppSys's command module
		# is the launch commands for each of the registered apps.

		for app in apps:
		
			appName = app.name	# Get the app's name.
			
				# Create the app's launch command.
			appLaunchCmd = AppLaunchCommand(appName, app)

				# Insert the launch command's helpItem at the front
				# the app's AppCommandModule's helpItem list.

			appCmdMod = app.commandModule
			appCmdMod.helpItems.insert(0, appLaunchCmd.helpItem)
			
				# Add it to this module.
			#module.addCommand(appLaunchCmd)
			# This is now done automatically by the Command constructor.
	
