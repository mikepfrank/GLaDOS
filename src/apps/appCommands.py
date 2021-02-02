# appCommands.py
# This module defines command types that apply to all apps 
# or to the app system as a whole.

from	commands.commandInterface	import	(

		Command,		# We subclass this.
		CommandModule	# We subclass this.
		
	)

# Dummy class declarations. (Definitions not available in this module.)
class Application_: pass

# Forward declarations.
class AppLaunchCommand: pass		# Class for app-launch commands.
class The_AppSys_CmdModule: pass	# Top-level command module for app system.

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
					initial placement (e.g., MOVE_TO_BOTTOM), then we put 
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
	"""
	
	def __init__(newAppLaunchCmd:AppLaunchCommand,
				appName:str,	# A capitalized app name to use, like 'Goals'.
				application:Application_	# The application to launch.
			):
					
		"""Instance initializer for app-launch commands. Constructs a custom
			unique format string."""

		cmd = newAppLaunchCmd	# Shorter name for this command.
		
		cmd._app = application	# Remember our app.
		
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
		
		fmtStr = f"^/{appName}(?:\\s+(\\S.*)?)?$"
		
			# We already know what command module we're in...
		appSysCmdMod = The_AppSys_CmdModule()	# Fetch this singleton.

		# Now dispatch to default initialization for Command instances.
		super(AppLaunchCommand, cmd).__init__(
			name = appName,		# Use the app's name as the command name.
			format = fmtStr,	# This was assembled above.
			unique = True,		# App-launch commands are intended to be unique.
			handler = cmd.handler,	# Command handler method (defined below).
			module = appSysCmdMod)	# The app-sys command module singleton.
			

	def handler(thisAppLaunchCmd:AppLaunchCommand, argsGroup:str=None):
	
		"""This is the handler method that is called when a generic app-launch
			command is invoked. The <argsGroup> argument, if present, is a string
			that contains the portion of the app-launch command line that was 
			parsed as the "argument list" by the command format regex."""
			
		cmd = thisAppLaunchCmd
		
		app = cmd._app	# This gets the application that we're supposed to start.
		
		app.launch()	# Launch the app (if not already launched).
			# (This automatically also foregrounds the app, whether or
			# not it was launched.)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class	The_AppSys_CmdModule(CommandModule):

	"""The app-sys command module is responsible for managing all of the
		high-level commands associated with the application system.  This
		includes the app-launch commands for all of the individual apps 
		in the system."""
	
	def __init__(theNewAppSysCmdMod:The_AppSys_CmdModule, appSys:AppSystem_):
		"""Extends CommandModule's instance initalizer to also remember a 
			pointer to the overarching application system."""
		module = theNewAppSysCmdMod
		module._appSys = appSys
			# Default initialization for command modules.
		super(The_AppSys_CmdModule, module).__init__()
	
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
			
				# Add it to this module.
			module.addCommand(appLaunchCmd)
	