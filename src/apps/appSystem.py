#|==============================================================================
#|				  TOP OF FILE:	  apps/appSystem.py
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		apps/appSystem.py				 [Python module source file]

	MODULE NAME:	apps.appSystem
	IN PACKAGE:		apps
	FULL PATH:		$GIT_ROOT/GLaDOS/src/apps/appSystem.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (Generic Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.apps (application system component)


	MODULE DESCRIPTION:
	===================

		This module provides definitions for creating and starting up the
		application system, which manages GLaDOS applications (intended for
		use by the embedded A.I.).

		Currently, the module includes definitions for general classes making
		up the application system, as well as classes defining specific
		applications.  Later on, some of these definitions might be moved out
		to their own modules.

		The general public classes defined by this module include:

			* TheAppSystem	- Singleton class for the overall application
								system, itself.

		The classes for specific applications include, or will eventually
		include the following (in order of actual/intended implementation):

		1.	The_Info_App		-

				The Info app is started automatically, and is intended to
				remain always visible.  It displays important contextual
				information for the A.I. to help make sure it remains
				cognizant of its identity & situation and high-level goals.
				It will also allow the A.I. to edit its list of high-level
				goals using a separate app, called the 'Goals' app (below).

		2.	The_Clock_App		-

				The Clock app provides a simple digital clock that displays
				itself in a small window at the top of the receptive field.

		3.	The_Goals_App		- 	[NOT YET IMPLEMENTED.]

				The Goals app gives the A.I. an interactive interface that 
				it can use to view and edit its list of high-level goals.

		4.	The_Help_App		- 	[NOT YET IMPLEMENTED.]

				The Help app implements the help system, which allows the AI
				to browse a set of help menus and obtain detailed help for
				specific commands.

		5.	The_Apps_App		- 	[NOT YET IMPLEMENTED.]

				This app is anticipated to become needed in the future as
				GLaDOS becomes more complex.  The intent is to show a menu of
				all of the installed applications that the A.I. can navitage.
				(Note, however, that the Apps app will be the only app that
				doesn't appear on the apps list displayed in the Apps app.)

		6.	The_Settings_App	-	[NOT YET IMPLEMENTED.]

				The Settings app allows the A.I. to browse and adjust various
				settings of GLaDOS, including general OS settings, application
				settings, and settings of the A.I. itself.

		7.	The_Memory_App		-	[NOT YET IMPLEMENTED.]

				The Memory app allows the A.I. to browse a database of
				"memories", which can include transcripts of its past
				conversations from AI Dungeon, as well as history records
				resulting from its own use of GLaDOS.

		8.	The_ToDo_App		-	[NOT YET IMPLEMENTED.]

				The ToDo app allows the A.I. to maintain a "to-do list" to
				help it remember a more detailed list of things it wants to
				do, beyond the more limited list of high-level goals
				supported by the Info app.  It can check off or delete
				individual to-do items.

		9.	The_Diary_App		-	[NOT YET IMPLEMENTED.]

				The Diary app allows the A.I. to keep a "diary" or personal
				record of important events that it wants to remember.

		10.	The_Comms_App		-	[NOT YET IMPLEMENTED.]

				The Comms app allows the A.I. to send and receive (real-world)
				email messages and text messages.

		11.	The_Browse_App		-	[NOT YET IMPLEMENTED.]

				The Browse app provides a simple environment to support
				(real-world) web browsing and searching on the part of
				the A.I.

		12.	The_Writing_App		-	[NOT YET IMPLEMENTED.]

				The Writing app allows the A.I. to write and edit longer
				written works, including books.

		13.	The_Unix_App		-	[NOT YET IMPLEMENTED.]

				The Unix app provides access to a real shell on the host
				machine on which GLaDOS is running.  This shell runs in the
				A.I.'s own user account.
																			 """
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#|==========================================================================
	#|
	#|	 0. Public names exported from this module.		   [module code section]
	#|
	#|			Special Python global structure defining the list of 
	#|			public names that dependent modules will import if 
	#|			they do 'from apps.application import *'.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	__all__		# List of public symbols exported by this module.
__all__ = [
			# Classes.
		'AppSystem',		# Singleton class for the application system.

			# These apps have already been implemented:
		'The_Info_App',		# Application that manages the information window.
		'The_Clock_App',	# Application that manages the clock window.

			# Add others to the list here as they are implemented.
		'The_Help_App',		# Application that manages the help system.
	]


	#|==========================================================================
	#|
	#|	 1. Module imports.								   [module code section]
	#|
	#|			Load and import names of (and/or names from) various
	#|			other python modules and pacakges for use from within
	#|			the present module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.2. Imports of optional python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	hjson	import	OrderedDict		
	# Ordered dictionary structure. Used in AppSystem_.
	

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

				#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				#| 1.3.1.2. Here are some other infrastructure modules we use.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	1.3.2. These modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from config.configuration		import	TheConfiguration, TheAIPersonaConfig
		# Singletons that provide the current GLaDOS system configuration
		# and the configuration of the current AI persona.

from entities.entity			import	The_AppSystem_Entity, AI_Entity_
		# These are referenced in the _AppSystemAction_ ABC when creating new
		# application actions on behalf of an AI, or the application system.

from commands.commandInterface	import	TheCommandInterface		# Anchor singleton.

from field.placement			import	Placement
		# This is needed to place application windows on the receptive field.

	#----------------------------------------------------
	# Imports from sibling modules to the current module.

from	.application			import	Application_
		# Base class from which we derive subclasses for specific applications.

from	.appActions				import	(

		The_AppSystem_Subscriber,	
			# Lets us be notified about and respond to actions we care about.
			
		AutoOpenWindowAction,
			# We create & initiate this action to auto-open a app window.
	)

from	.appCommands			import	The_AppSys_CmdModule, the_appSys_cmdModule	# Second one here is a special constructor to avoid singleton circularity
		# Anchor point for the command module for the application system.

	# Import all of the various specific applications that exist.

from	.infoApp	import	The_Info_App	# Implemented 1/16/'21.
from	.clockApp	import	The_Clock_App	# Implemented 1/17/'21.

	# The below are just stubs for not-yet-completed apps.

from	.goalsApp		import	The_Goals_App
from	.helpApp		import	The_Help_App
from	.appsApp		import	The_Apps_App
from	.settingsApp	import	The_Settings_App
from	.memoryApp		import	The_Memory_App
from	.todoApp		import	The_ToDo_App
from	.diaryApp		import	The_Diary_App
from	.browseApp		import	The_Browse_App
from	.commsApp		import	The_Comms_App
from	.writingApp		import	The_Writing_App
from	.unixApp		import	The_Unix_App

	#|==========================================================================
	#|
	#|	 3. Globals										   [module code section]
	#|
	#|		Declare and/or define various global variables and
	#|		constants.	Note that top-level 'global' statements are
	#|		not strictly required, but they serve to verify that
	#|		these names were not previously used, and also serve as
	#|		documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	3.1. Private globals.							   [code subsection]
		#|
		#|		These globals are not supposed to be accessed from
		#|		outside of the present module.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|	_APP_MAP					   [module private global structure]
			#|
			#|		This defines a global constant data structure (speci-
			#|		fically, a dictionary) that provides the map between 
			#|		the names and classes of the full list of (intended-to-
			#|		be-) supported applica- tions.  
			#|
			#|		Note that some of the apps on this list may not yet be 
			#|		implemented as of this writing.
			#|
			#|		The structure of the name/value pairs in the map is:
			#|
			#|			name	- Short text name of the application.
			#|						This must match the name used in the
			#|						app-configs attribute of the system
			#|						config file (glados-config.hjson).
			#|
			#|			class	- Class defining the application.  This
			#|						must be a subclass of Application_.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# NOTE: We could define this map within the AppSystem_ class instead of globally.
global _APP_MAP		# Map from application name to application class.

# NOTE: The order listed here is intended to match the order in app-config.
# But, the actual registration order depends on the ordor in app-config.
_APP_MAP = {	

	# We'll register the Clock app first, so that when it auto-opens, it will 
	# pin itself to the very top of the receptive field (just after the header bar.
	
		'Clock':	The_Clock_App,		# #2: First implemented 1/17/'21.

	# We'll register the Info app second, so that when it auto-opens, it will pin 
	# itself just under the Clock app.
	
		'Info':		The_Info_App,		# #1: First implemented 1/16/'21.

	#========== APPS BELOW THIS LINE ARE NOT YET IMPLEMENTED ==========
	
		'Goals':	The_Goals_App,
		'Help':		The_Help_App,
		'Apps':		The_Apps_App,
		'Settings':	The_Settings_App,
		'Memory':	The_Memory_App,
		'ToDo':		The_ToDo_App,
		'Diary':	The_Diary_App,
		'Browse':	The_Browse_App,
		'Comms':	The_Comms_App,
		'Writing':	The_Writing_App,
		'Unix':		The_Unix_App,
	}


	#|==========================================================================
	#|
	#|	3. Class forward declarations.					   [module code section]
	#|
	#|			Pre-declare classes to be defined later in this module.
	#|			(Such dummy definitions are really only useful in type 
	#|			hints, which don't really do anything.)
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class	AppSystem_:		pass	# Abstract base class for application systems.
class	TheAppSystem:	pass	# Concrete singleton class to anchor this module.


	#|==========================================================================
	#|
	#|	4. Class definitions.							   [module code section]
	#|
	#|			Define the classes provided by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	4.1. General classes.							   [code subsection]
		#|
		#|		These classes are not application-specific, but apply
		#|		generally to the entire application system.
		#|
		#|			AppSystem_		    			[public abstract base class]
		#|
		#|				Abstract base class for applications systems.
		#|				Has one one concrete derived leaf class, namely
		#|				TheAppSystem, which is the singleton class that
		#|				anchors this module.
		#|
		#|			TheAppSystem						[public singleton class]
		#|
		#|				Singleton class for the application system.
		#|				Sole subclass of AppSystem_.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class AppSystem_:

	"""Abstract base class for applications systems.  However, for now,
		there should only be one derived class, TheAppSystem, which is 
		a singleton class with a single instance, TheAppSystem()."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Instance data members							   [class documentation]
	#|	=====================
	#|
	#|		Private instance data members:
	#|		------------------------------
	#|
	#|		._appDict [dict] - This is a dictionary of registered applica-
	#|			tions, mapping the app name to the corresponding instance 
	#|			of an application-specific subclass of Application_.
	#|
	#|		._subscriber [The_AppSystem_Subscriber] - A convenient refer-
	#|			ence to appActions.The_AppSystem_Subscriber(), which is 
	#|			the singleton instance of the application system's action
	#|			subscriber.  It looks for interesting action reports, and
	#|			dispatches appropriately to the rest of the app system.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def __init__(theNewAppSys:AppSystem_):
	
		"""One-time initializer for the new unique singleton instance."""

		appSys = theNewAppSys

		_logger.info("        [Apps/Init] Initializing applications system...")

		appSys._appDict = OrderedDict()
			# Ordered dictionary of registered applications: Maps app name to 
			# app object. The order reflects order of appearance in app-list.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| At this point, we register the applications that are listed in 
			#| our configuration information as being 'available'.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		_logger.info("        [Apps/Init]     Registering available apps...")

		appSys._registerAvailableApps()
			# Note this is where the application objects for all of the 
			# available applications are created.


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Next, we create, install, and activate the app-system command 
			#| module. This creates, installs, and activates all of the commands
			#| for launching individual manually-launchable applications.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			# First, create the app-system's command module.
		appSys_cmdMod = the_appSys_cmdModule(appSys)	# Creates & returns the 'singleton' for our command module.
				# ^ It's very important that we're calling this function instead of a normal singleton class constructor.
		appSys._cmdMod = appSys_cmdMod					# Remember it for later reference.
		
			# Next, install that module into the GLaDOS command interface.
		cmdIface = TheCommandInterface()		# Gets this singleton.
		cmdIface.installModule(appSys_cmdMod)	# Plug this module into it.
		
			# Finally, activate the command module.
		appSys_cmdMod.activate()	# This enables all commands in the module.


			#-------------------------------------------------------------------
			# Next, we have to create our action news subscriber, which will 
			# ensure that we are notified of important system actions that we 
			# want to be made aware of.  In particular, once the AI's cognitive 
			# system has booted up to the extent that its receptive field is 
			# available, we want to know about it, because that's when we'll 
			# tell our auto-opening applications that they should go ahead and 
			# open up their windows on the field.

		appSys._subscriber = The_AppSystem_Subscriber(appSys)
				# We have to pass it a pointer to ourselves, so that later, 
				# when it actually starts receiving notifications, it can call 
				# our own methods as needed.

	#__/ End singleton instance initializer for class AppSystem_.


	def _registerAvailableApps(theAppSys:AppSystem_):
	
		"""This private method is called during application system 
			initialization.  It is responsible for registering each of
			the individual apps with the application system."""

		appSys = theAppSys

		# NOTE: The below implementation implies that auto-open apps 
		# will be placed on the field in the same order in which
		# they are listed in the 'app-list' list within the system 
		# configuration file.

		appConfigs = TheConfiguration().appConfigs

		# Go through all apps that have config records.
		for appName in appConfigs.keys():	# (Note this is an OrderedDict.)
			# NOTE: The order here is the order in which we should register the apps.
		
			_logger.info(f"        [Apps/Init]         Registering app '{appName}'...")

				# Get the app's class from the _APP_MAP global struct.
			appClass = _APP_MAP[appName]

				# Fetch the configuration record for this app.
			appConf = appConfigs[appName]

				#|-------------------------------------------------------------------
				#| Extract all of the generic application parameters from the record.

			appAvailable = appConf['avail']
				# Is the app marked as available to be registered?

			appAutoStart = appConf['auto-start']
				# Should the app be automatically started on system startup?

			appAutoOpen	 = appConf['auto-open']
				# Should the app window be automatically opened on field startup?

			appAutoFocus = appConf['auto-focus']
				# Should the app window grab the command focus when it opens?

			appLoudUpdate = appConf['loud-update']
				# Should the app window wake up the A.I. when it updates its display?

			appPlacement = appConf['placement']
				# Where should the app window (if any) initially be placed?

			appConfig	 = appConf['conf']
				# What's the app-specific data structure?

				#|-------------------------------------------------------------------
				#| Now actually register the application.

			# If the app is marked as available to register, then register it.
			if appAvailable:
				appSys._registerApp(appName, appClass, appAutoStart,
					appAutoOpen, appAutoFocus, appLoudUpdate,
					appPlacement, appConfig)

		#__/ End loop over keys of the appConfigs ordered dictionary.

			#-------------------------------------------------------------
			# We might as well go ahead and start up all the apps that are
			# supposed to be launched immediately on system startup.

		_logger.info("        [Apps/Init] Starting up auto-start apps...")

		appSys.startup()
		
	#__/ End private (singleton) instance method appSys._registerAvailableApps().
	

	def _registerApp(theAppSys:AppSystem_, appName:str, appClass:type, 
			appAutoStart:bool, appAutoOpen:bool, appAutoFocus:bool, 
			appLoudUpdate:bool, appPlacement:Placement, appConfig:dict):

		"""Registers an application with the application system.
			This is where the application object is actually created.
			Generic configuration parameters of the app are passed in 
			as individual arguments.  App-specific parameters are in 
			the appConfig record."""

			# First, call the class constructor to actually create the application object.
		app = appClass(appName, appAutoStart, appAutoOpen, appAutoFocus,
					   appLoudUpdate, appPlacement, appConfig)

			# Now add that app object to our dict of apps.
		theAppSys._appDict[appName] = app
		
	#__/ End private singleton instance method appSys._registerApp().


	def __call__(self:AppSystem_, name:str):
		"""Calling the application system with an application name as
			the argument just returns the application with that name."""
		return self._appDict(name)


	@property
	def apps(thisAppSys:AppSystem_):
		"""Gets an ordered list of all the currently-registered apps."""
		return thisAppSys._appDict.values()


		# This executes the startup sequence, which basically consists of starting up
		# all of the apps that we tagged for auto-start.
	def startup(self:AppSystem_):

		"""This method handles startup activities for the application system.
			It is called by the system supervisor during system startup."""

		# So far, the only thing we have to do is start up all of the
		# individual apps that are marked to be auto-started on startup.
		for app in self.apps:
			if app.autoStart:
				_logger.info("        [Apps/Init]     Auto-starting "
					f"'{app.name}' app...")
				app.start()


	def displayWindows(thisAppSys:AppSystem_):

		"""Tells the application system that it's OK now to actually display
			any open application windows on the receptive field."""

		appSys = thisAppSys

		_logger.info("[Apps/Open] Automatically opening 'auto-open' app windows...")

		for app in appSys.apps:

			# If this particular application hasn't even been started yet,
			# we can skip trying to auto-open its window.

			if not app._launched:
				continue

			# Check to see if this particular app is configured to auto-open
			# its window.  If so, then we do an auto-open action, and also we
			# check whether we need to auto-focus.

			if app.autoOpen:

				_logger.info(f"[Apps/Open] Auto-opening '{app.name}' app window(s)...")

				# At this point, we could just call app.openWins directly, but
				# instead, we conceive and then initiate an explicit action to
				# do the job, namely, an instance of AutoOpenWindowAction. We
				# do this so that the event of this action's execution will be
				# automatically incorporated into the AI's cognitive stream; i.e.,
				# the AI will explicitly be made aware of the fact that this
				# action occurred.  This is to help it to understand what's
				# going on in this new operating environment it's in.  Also, this
				# does some degree of automatic logging of the action.

				aowi = AutoOpenWindowAction(app)	# Construct (conceive) the action.
				aowi.initiate()						# Tell it to initiate its execution.
					# This will probably also go ahead and finish executing too.

				# Also, check for auto-focus.
				if app.autoFocus:
					app.grabFocus()		# Tell the app to grab command focus.

			#__/ End if app is marked for auto-open.

		#__/ End loop over registered apps.

	#__/ End public singleton instance method appSys.displayWindows().

#__/ End public abstract class AppSystem_.


@singleton
class TheAppSystem(AppSystem_):

	"""This singleton subclass of AppSystem_ anchors the entire appSystem
		module.  Dependent modules may retrieve its unique instance using 
		TheAppSystem()."""

	pass	# Code is all in our parent class AppSystem_, above.

#__/ End public singleton class TheAppSystem.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					 END OF FILE:	apps/appSystem.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
