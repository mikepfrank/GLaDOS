#|==============================================================================
#|				  TOP OF FILE:	  apps/appSystem.py
#|------------------------------------------------------------------------------
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
		applications.  Later, some definitions might be moved out to their 
		own modules.

		The general classes include:

			* Application_	- Abstract base class from which to derive
								classes for specific applications.
			
			* TheAppSystem	- Singleton class for the overall application
								system, itself.

		The classes for specific applications include (this one goes to 11):

			1. Help_App		- The Help app implements the help system,
								which allows the AI to browse a set of
								help menus and obtain detailed help for 
								specific commands.
			
			2. Apps_App		- This app is not yet implemented, but it is
								anticipated to become needed in the future
								as GLaDOS becomes more complex.	 The intent
								is to show a menu of all of the installed
								applications that the A.I. can navitage.
								(Note, however, that the Apps app is the
								only app that doesn't appear on the apps 
								list displayed in the Apps app.)
										[NOT YET IMPLEMENTED.]
			
			3. Info_App		- The Info app is started automatically, and
								is intended to remain always visible.  It
								displays important contextual information
								for the A.I. to help make sure it remains
								cognizant of its identity & situation and 
								high-level goals.  It will also allow the
								A.I. to edit its list of high-level goals.
			
			4. Settings_App	- The Settings app allows the A.I. to browse
								and adjust various settings of GLaDOS, 
								including general OS settings, application
								settings, and settings of the A.I. itself.
										[NOT YET IMPLEMENTED.]
			
			5. Memory_App	- The Memory app allows the A.I. to browse a
								database of "memories", which can include
								transcripts of its past conversations from 
								AI Dungeon, and history records from its 
								own use of GLaDOS.
										[NOT YET IMPLEMENTED.]
			
			6. ToDo_App		- The ToDo app allows the A.I. to maintain a
								"to-do list" to help it remember a more
								detailed list of things it wants to do,
								beyond the more limited list of high-level
								goals supported by the Info app.  It can
								check off or delete individual to-do items.
										[NOT YET IMPLEMENTED.]
			
			7. Diary_App	- The Diary app allows the A.I. to keep a "diary"
								or personal record of important events that
								it wants to remember.
										[NOT YET IMPLEMENTED.]
			
			8. Comms_App	- The Comms app allows the A.I. to send and 
								receive (real-world) email messages and text 
								messages.
										[NOT YET IMPLEMENTED.]
			
			9. Browse_App	- The Browse app provides a simple environment 
								to support (real-world) web browsing and 
								searching on the part of the A.I.
										[NOT YET IMPLEMENTED.]
			
			10. Writing_App	- The Writing app allows the A.I. to write and 
								edit longer written works, including books.
										[NOT YET IMPLEMENTED.]
			
			11. Unix_App	- The Unix app provides access to a real shell
								on the host machine on which GLaDOS is running.
								This shell runs in the A.I.'s own user account.
										[NOT YET IMPLEMENTED.]
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


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

from os			import path				# Manipulate filesystem path strings.


		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster	import getComponentLogger

		# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.


		# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton
from infrastructure.utils		import	countLines

			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from entities.entity			import	The_AppSystem_Entity, AI_Entity_

from field.placement			import	Placement

from config.configuration		import	TheConfiguration, TheAIPersonaConfig
		# Singletons that provide the current GLaDOS system configuration
		# and the configuration of the current AI persona.

from supervisor.action			import	ActionSubscriber_, ActionBySystem_, TheEverythingChannel

from windows.windowSystem		import	Window
from processes.processSystem	import	SubProcess

from mind.aiActions				import	AnnounceFieldExistsAction
	# We need this so that we can watch for actions of this class,
	# because that's what tells us that it's safe to go ahead and
	# start opening up the windows for apps marked as auto-open.

	#|==========================================================================
	#|
	#|	 2. Globals										   [module code section]
	#|
	#|		Declare and/or define various global variables and
	#|		constants.	Note that top-level 'global' statements are
	#|		not strictly required, but they serve to verify that
	#|		these names were not previously used, and also serve as 
	#|		documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|
		#|	Special globals.									[code subsection]
		#|
		#|		These globals have special meanings defined by the
		#|		Python language. 
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__	# List of public symbols exported by this module.
__all__ = [
		'Application_',		# Abstract base class for deriving applications.
		'AppSystem',		# Singleton class for the application system.
		'The_Help_App',		# Application that manages the help system.
		'The_Info_App',		# Application that manages the information window.
			# Add others as they are implemented.
	]


		#|======================================================================
		#|		
		#|	Private globals.								   [code subsection]
		#|
		#|		These globals are not supposed to be accessed from 
		#|		outside of the present module.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|	_APP_LIST						[module private global constant]
			#|
			#|		This is a structure (list of dicts) that defines the
			#|		full list of supported applications.  See the 
			#|		definition at the end of the file for further 
			#|		documentation.
			#|
			#|		Note that some of these may not yet be implemented.
			#|
			#|		The structure of each dict in the list is:
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

global _APP_LIST	# We could put this into the AppSystem class instead.


	#|==========================================================================
	#|
	#|	3. Class forward declarations.					   [module code section]
	#|
	#|			Pre-declare classes to be defined later in this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


class	AppSystem_:		pass	# Abstract base class for application system.
class	TheAppSystem:	pass	# Singleton class to anchor this module.

class	Application_:	pass	# Abstract base class for applications.

class	The_Help_App:		pass
class	The_Apps_App:		pass
class	The_Info_App:		pass
class	The_Goals_App:		pass
class	The_Settings_App:	pass
class	The_Memory_App:		pass
class	The_ToDo_App:		pass
class	The_Diary_App:		pass
class	The_Browse_App:		pass
class	The_Comms_App:		pass
class	The_Writing_App:	pass
class	The_Unix_App:		pass

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
		#|		These classes are not application-specific but apply 
		#|		generally to the entire application system.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
				
class Application_:
	#---------------------------------------------------------------------------
	"""
	app.Application_							  [module public abstract class]
	
		This is the abstract superclass from which the class for each 
		specific GLaDOS application should be derived.
		
		The class for a typical specific application should generally
		be declared as a singleton class to ensure that there is only
		one instance of each application in the system.
		
		Generically, an application has the following associated
		elements:

			- A name.
			
			- A process.
			
			- A window.
			
			- A state (not-yet-started, running, not running).
			
			- A data directory (within the AI's data directory).
				This is used to preserve application state 
				information in between GLaDOS system runs.
					
			- A command module.
				Provides all of the commands associated with the 
				application.

		And some methods are:
		
			- launch()		- Starts the application running.
	"""
	
	def __init__(self, name:str, autoStart:bool, autoOpen:bool, autoFocus:bool,
				 loudUpdate:bool, placement:Placement, conf:dict):
		#	name - The name of the application object.
		#	autoStart - Whether to start the app on system startup.
		#	placement - Where to place the app window in the receptive field.
		#	conf - Application-specific dictionary object.
	
			# Remember the name of this application, & other generic parameters.

		self.name 				= name

		self._launched			= False			# Easy way to tell we've never been started.

		self.autoStart			= autoStart
		self.autoOpen			= autoOpen
		self.autoFocus			= autoFocus
		self.loudUpdate			= loudUpdate
		self.initialPlacement	= placement
		
		_logger.debug(f"Initializing application '{name}' with the following parameters:")

		_logger.debug(f"\tautoStart = {autoStart}, autoOpen = {autoOpen}, "
					  f"autoFocus = {autoFocus}, loudUpdate = {loudUpdate}, "
					  f"placement = {placement}")

			# Create a new window for this application, with a suitable title & placement.
			# (We don't actually display this window until the application is launched
			# and the receptive field is ready.)
		
		self.window = Window(name + ' Window', app=self, placement=placement, loudUpdate=loudUpdate)
		
			# Create a subprocess (GLaDOS process) for this application, to run in that window.
			# We don't actually start the process until the application is launched.
	
		self.process = SubProcess(name, self.window)
		
			# Designate the state of this application as "not yet started."
		
		self.state = 'not-yet-started'
		
			# Do any initialization work that's specific to the individual app's Application subclass.
			# This includes doing any needed processing of the application configuration struct.
		
		self.appSpecificInit(conf)

			# Create the application's command module, and install it in the GLaDOS command interface.
		
		self.initCommandModule()
		
	#__/ End initializer for class Application.
			
			
	def appSpecificInit(self, conf:dict): 
	
		""" 
		This method performs application-specific initialization,
		using the 'conf' dictionary, which comes from the 'app-config'
		attribute in the system config file (glados-config.hjson).
		
		Please note that this is a virtual method (placeholder) which 
		needs to be overridden in each application-specific subclass.
		"""
				
		pass
	#__/ End appSpecificInit().

	
	def initCommandModule(self):
		"""
				
		"""
		
			# First, create the application's command module.
			# Subclasses should implement this method.
		
		cmdModule = self.createCommandModule()
		
			# Remember it for later.
		
		self.commandModule = cmdModule
		
			# Install it in the system's command interface.
		
				
	#__/ End initCommandModule().


	def createCommandModule(self):
		"""
		This virtual method should be overridden in application-specific
		subclasses.	 It should create a command module for the application
		(i.e., an instance of CommandModule or one of its subclasses) and
		return it.	Generally, the command module should have been pre-
		loaded with all of the application's commands.
		"""
		
		return None				
			# This makes sense since the abstract Application class isn't itself 
			# associated with any specific command module.
				
	#__/ End createCommandModule().

	def start(self):	# Generic start method for apps.

		"""This method is called whenever an application is started,
			whether this happens during system startup because it's
			an auto-start application, or in response to an explicit
			command. This default implementation just does some basic
			bookkeeping. Subclasses that override this method should
			do a super() call to this version, so as to extend it."""

		# This just means the app has been started (for the first time).
		self._launched = True

		# For generic apps, generally speaking, the only thing we need to do
		# when we first start them up is mark them as being in the running state.
		# In this state, the app's window might not yet be open.

		self.state = 'running'


	def openWins(thisApp):	# Subclasses should override this.

		"""Tells this app to go ahead and automatically open up its window(s)
			on the field, or at least, any windows that are currently designated
			as being eligible to be opened.  Details are app-dependent."""

		win = thisApp.window

		win.openWin()	# Tells the window to open itself up.

		thisApp.state = 'open'	# Running, with windows open.
		

#__/ End class Application.

@singleton
class The_AppSystem_Subscriber(ActionSubscriber_):

	"""This subscribes to action news channels that the application system
		is potentially interested in watching."""

	def __init__(newSubscriber, appSys, name="AppSys"):

		_logger.debug("appSysSubscriber.__init__(): Initializing the AppSystem's subscriber...")

		sub = newSubscriber

		sub._appSys = appSys

		super(The_AppSystem_Subscriber.__wrapped__, sub).__init__(name=name)

		_logger.debug("appSysSubscriber.__init__(): Subscribing to The Everything Channel...")

			# For now, we'll just subscribe to the everything channel.
		TEC = TheEverythingChannel()	# Defined in the action module.
		sub.subscribe(TEC)

	def notify(thisSub, status, action):
		
		appSys = thisSub._appSys	# The application system.

		# If the action report was that an announcement of the receptive
		# field's existence was just completed, then we'll take that as 
		# our due that it's a good time to display all of our app windows
		# that are supposed to be open.

		if status=='completed' and isinstance(action, AnnounceFieldExistsAction):
			
			_logger.info("[Apps/Open] Received field-existence notification.")

			appSys.displayWindows()
				# This tells the application system, "OK, you can go ahead and
				# display all of your existing open windows on the receptive field."

class _AppSystemAction_: pass
class _AppSystemAction_(ActionBySystem_):

	"""This is a private (leading '_') abstract (trailing '_') base class
		for actions taken by the application system.  Its functions include
		setting the conceiver (the AppSystem)."""

	defaultConceiver = The_AppSystem_Entity()

	def __init__(new_AppSys_Action:_AppSystemAction_,
				 
			description:str="A generic action was taken by the application system.",
				# REQUIRED. A description string. SUBCLASSES SHOULD OVERRIDE THIS VALUE.

			conceiver:AI_Entity_=None,
				 # The AI entity that conceived of taking this action.
				 # If not provided, we'll default it to The_AppSystem_Entity().

			importance:int=None
			
		):

		asAction = new_AppSys_Action

		super(_AppSystemAction_, asAction).__init__(description, conceiver=conceiver)


class _AutoOpenWindowAction: pass
class _AutoOpenWindowAction(_AppSystemAction_):

	"""Class for the action of automatically opening an application's
		window on application-system startup.  We make this an explicit
		action to aid the AI's understanding of the fact that opening
		this particular window was done as an automatic system action."""

	def __init__(newAOWA:_AutoOpenWindowAction, app:Application_):

		"""This instance initializer for new auto-open-window actions
			simply sets the textual description of the action, and
			remembers which app we are intending to auto-open the
			window of."""

		newAOWA._app = app		# Remember which app we're opening.

		appName = app.name		# Get the name of the app.

		description=f"Auto-opening the '{appName}' app's window..."

		super(_AutoOpenWindowAction, newAOWA).__init__(description)

	#__/ End instance initializer for class _AutoOpenWindowAction.

	def executionDetails(thisAOWA:_AutoOpenWindowAction):

		"""Since this is a system action, the action processor will
			automatically execute it by calling this method.  In this
			case, all we need to do is call the app's .openWins()
			method, to tell it to actually open its windows."""

		app = thisAOWA._app		# Get the app that this action is for.
		app.openWins()			# Tell that app to open its windows.

	#__/ End instance method aowa.executionDetails().

#__/ End action class _AutoOpenWindowAction.


class AppSystem_:
	pass

class TheAppSystem: pass

@singleton
class TheAppSystem(AppSystem_):

	# TheAppSystem has:
	#
	#	- Dict of registered applications: Maps app name to app object.


	def __init__(self):		# One-time initializer for singleton instance.
			
		_logger.info("        [Apps/Init] Initializing applications system...")

		self._appDict = {}
		
			# At this point, we register the applications that are
			# listed as 'available' in our configuration information.
				
		_logger.info("        [Apps/Init]     Registering available apps...")

		self._registerAvailableApps()

			# Next, we have to create our action news subscriber, which will ensure
			# that we are notified of important system actions that we want to be
			# made aware of.  In particular, when the AI's cognitive system boots up
			# to the extent that its receptive field is available, we want to know
			# about it, because that's when we'll tell our auto-opening applications
			# that they should go ahead and open up their windows on the field.

		self._subscriber = The_AppSystem_Subscriber(self)
			# We have to pass it a pointer to ourselves, so that later, when it
			# actually starts receiving notifications, it can call our methods
			# as needed.

	#__/ End singleton instance initializer for class TheAppSystem.


	def _registerApp(self, appName:str, appClass:type, appAutoStart:bool,
					 appAutoOpen:bool, appAutoFocus:bool, appLoudUpdate:bool,
					 appPlacement:Placement, appConfig:dict):
			
			# First, call the class constructor to actually create the application object.
		app = appClass(appName, appAutoStart, appAutoOpen, appAutoFocus,
					   appPlacement, appConfig)
		
			# Now add that app object to our dict of apps.
		self._appDict[appName] = app
	#__/
		
	def __call__(self, name:str):
		return self._appDict(name)
			
		# This executes the startup sequence, which basically consists of starting up
		# all of the apps that we tagged for auto-start.
			
	@property
	def apps(thisAppSys):
		return thisAppSys._appDict.values()

	def startup(self):

		"""This method handles startup activities for the application system.
			It is called by the system supervisor during system startup."""

		# So far, the only thing we have to do is start up all of the
		# individual apps that are marked to be auto-started on startup.
		for app in self.apps:
			if app.autoStart:
				_logger.info(f"        [Apps/Init]     Auto-starting '{app.name}' app...")
				app.start()

	def _registerAvailableApps(self):
	
		# NOTE: The below implementation implies that the placement
		# order for auto-open apps is the same as the order in which
		# they are listed in the _APP_LIST array defined in this file.

		appConfigs = TheConfiguration().appConfigs
			
		for app in _APP_LIST:	 # These are simple dict structures.
		
			appName = app['name']
			appClass = app['class']
			
			# Really we should do some error-checking here in case
			# appName isn't in appConfigs, but... not done yet.

			_logger.info(f"        [Apps/Init]         Registering app '{appName}'...")

			appAvailable = appConfigs[appName]['avail']
				# Is the app marked as available to be registered?

			appAutoStart = appConfigs[appName]['auto-start']
				# Should the app be automatically started on system startup?

			appAutoOpen	 = appConfigs[appName]['auto-open']
				# Should the app window be automatically opened on field startup?

			appAutoFocus = appConfigs[appName]['auto-focus']
				# Should the app window grab the command focus when it opens?

			appLoudUpdate = appConfig[appName]['loud-update']
				# Should the app window wake up the A.I. when it updates its display?

			appPlacement = appConfigs[appName]['placement']
				# Where should the app window (if any) initially be placed?

			appConfig	 = appConfigs[appName]['conf']
				# What's the app-specific data structure?
			
			if appAvailable:
				self._registerApp(appName, appClass, appAutoStart,
								  appAutoOpen, appAutoFocus, appLoudUpdate,
								  appPlacement, appConfig)
		
		#__/ End loop over global _APP_LIST array.
		
			#-------------------------------------------------------------
			# We might as well go ahead and start up all the apps that are 
			# supposed to be launched immediately on system startup.
			
		_logger.info("        [Apps/Init] Starting up auto-start apps...")

		self.startup()
			
	def displayWindows(thisAppSys):

		"""Tells the application system that it's OK to actually display
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
				# do the job, namely, an instance of _AutoOpenWindowAction. We
				# do this so that the event of this action's execution will be
				# automatically incorporated into the AI's cognitive stream; i.e.,
				# the AI will explicitly be made aware of the fact that this
				# action occurred.  This is to help it to understand what's
				# going on in this new operating environment it's in.  Also, this
				# does some degree of automatic logging of the action.

				aowi = _AutoOpenWindowAction(app)	# Construct (conceive) the action.
				aowi.initiate()						# Tell it to initiate its execution.

				# Check for auto-focus.
				if app.autoFocus:
					app.grabFocus()		# Tell the app to grab command focus.

				#app.openWins()
					# This tells the app to go ahead and automatically open
					# its window(s) on the receptive field.
			

#__/ End class AppSystem.
		

		#|======================================================================
		#|	4.2. Application-specific classes.				   [code subsection]
		#|
		#|		These classes define specific applications within GLaDOS.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

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

		#----------------------------------------------------------
		# NOTE: At the moment, the 'Apps' app is not needed because
		# the help window already lists all the apps.

@singleton
class The_Apps_App(Application_):

	"""
	Apps - This tool simply displays the list of all the
	available apps, and allows the A.I. to select one to 
	launch.
	"""

	pass

@singleton
class The_Info_App(Application_):
		
	"""
	Info - The idea behind this app is that it maintains and 
	displays certain critical contextual information that the A.I. 
	needs to know, including its identity, life circumstances, and
	its present high-level goals.  Its window normally remains pinned 
	at the top of the A.I.'s receptive field.  When the Information app
	is launched, it allows the A.I. to edit certain information such
	as its high-level goals. NOTE: This is one of the few apps that
	is generally launched automatically at system startup. 
	"""

		# NOTE: The feature to allow the AI to edit goals is not yet
		# implemented. For now the Info app just displays the contents
		# of a static text file.

	def appSpecificInit(self, conf:dict):
	
		"""This method performs application-specific initialization 
				for the Info application, at app creation time."""
	
		_logger.debug("infoApp.appSpecificInit(): Initializing Info app...")

			#----------------------------------------------------------
			# First, get the AI persona configuration, because it 
			# contains # key information we need, such as the location
			# of the AI's data directory.

		aiConf = TheAIPersonaConfig()
			# Note this retrieves the singleton instance 
			# of the Configuration class.

			#------------------------------------------------------
			# First, get the location of the AI's data directory,
			# which is in the system configuration.
				
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
				
		_logger.debug("Loaded inital info text:\n" + infoText)

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

	def start(inst):
		"""Starts up the Info application."""
		# Right now, the start method for the Info app doesn't need
		# to do anything particular, because the app has no dynamic 
		# behavior yet.  So, just dispatch to our parent class.
		# However, we may add some dynamic behavior to the app later.
		super(The_Info_App.__wrapped__, inst).start()

#__/ End class Info_App.


@singleton
class The_Clock_app(Application_):

	"""
	The 'Clock' app displays the current date and time.
	"""

	pass

@singleton
class The_Goals_App(Application_):

	"""
	The 'Goals' app can be used by the A.I. to modify its list
	of high-level goals.
	"""

	pass

@singleton
class The_Settings_App(Application_):

	"""
	Settings - This app can be used by the A.I. to adjust various
	settings within GLaDOS.	 These can be associated with major 
	systems or subsystems of GLaDOS, or individual apps or 
	processes. 
	"""

	pass

@singleton
class The_Memory_App(Application_):
		
	"""
	Memory - The memory tool allows the A.I. to browse and search
	a database of records of its past conversations, thoughts, and
	actions.
	"""

	pass

@singleton
class The_ToDo_App(Application_):
		
	"""
	ToDo - The idea of this app is that it is a simple to-do list 
	tool, which the A.I. can use to make notes to itself of important
	tasks that it wants to do later.  The tasks can be given priority 
	levels.	 The A.I. can check them off or delete them when complete. 
	"""

	pass

@singleton
class The_Diary_App(Application_):
		
	"""
	Diary - This tool allows the A.I. to keep a "diary" of important
	notes to itself, organized by date/time.
	"""

	pass

@singleton
class The_Browse_App(Application_):
		
	"""
	Browse - This is a simple text-based tool to facilitate simple web
	browsing and searching.
	"""

	pass

@singleton
class The_Comms_App(Application_):
		
	"""
	The "comms" tool faciltates the A.I.'s two-way 
	communications with the outside world.	This may include direct 
	messages sent via Telegram, email messages, or other interfaces.  
	This may be broken out later into a whole 'Comms' subfolder of 
	separate apps.
	"""

	pass

@singleton
class The_Writing_App(Application_):
		
	"""
	The writing tool is an interface that helps the A.I.
	to compose and edit complex, hierarchically-structured works:  
	Stories, poems, and extended multi-chapter books.
	"""

	pass

@singleton
class The_Unix_App(Application_):
		
	"""
	This app gives the A.I. access to an actual Unix shell
	environment on the host system that GLaDOS is running on.  The A.I.
	runs within its own user account with limited permissions.
	"""

	pass

	#|==========================================================================
	#|
	#|	4. Main body.									   [module code section]
	#|
	#|		This code constitutes the main body of the module
	#|		which is executed on the initial import of the module.
	#|						
	#|		All it does currently is initialize the appList global 
	#|		using the application classes as defined above.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|------------------------------------------------------------------
		#|	Here, we initialize the _APP_LIST global (declared earlier).
		#|
		#|	Recall, this is a structure (list of dicts) that defines the
		#|	full list of supported applications.  Note that some of these 
		#|	may not yet be implemented.
		#|
		#|	The structure of each dict in the list is:
		#|
		#|		name	- Short text name of the application.  This must 
		#|					match the name used in the app-configs 
		#|					attribute of the system config file 
		#|					(glados-config.hjson).
		#|
		#|		class	- Class defining the application.  This must be 
		#|					one of the subclasses of Application_ 
		#|					defined above.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

_APP_LIST = [

	# We list the Clock app first, so that when it auto-opens, it will pin itself
	# to the very top of the receptive field (just after the header bar.
		{
			'name':		'Clock',
			'class':		The_Clock_app
		},

	# We list the Info app second, so that when it auto-opens, it will pin itself
	# just under the Clock app.
		{
			'name':		'Info',					# First implemented 1/16/'21.
			'class':		The_Info_App
		},

	#========== APPS BELOW THIS LINE ARE NOT YET IMPLEMENTED ==========
		{
			'name':		'Help',
			'class':		The_Help_App
		},
		{		
			'name':		'Apps',
			'class':		The_Apps_App
		},
		{
			'name':		'Goals',
			'class':		The_Goals_App
		},
		{
			'name':		'Settings',
			'class':		The_Settings_App
		},
		{
			'name':		'Memory',
			'class':		The_Memory_App
		},
		{
			'name':		'ToDo',
			'class':		The_ToDo_App
		},
		{
			'name':		'Diary',
			'class':		The_Diary_App
		},
		{
			'name':		'Browse',
			'class':		The_Browse_App
		},
		{
			'name':		'Comms',
			'class':		The_Comms_App
		},
		{
			'name':		'Writing',
			'class':		The_Writing_App
		},
		{
			'name':		'Unix',
			'class':		The_Unix_App
		},
	]


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					 END OF FILE:	apps/appSystem.py
#|=============================================================================
