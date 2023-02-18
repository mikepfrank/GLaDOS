#|==============================================================================
#|				  TOP OF FILE:	  apps/application.py
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		apps/application.py				 [Python module source file]

	MODULE NAME:	apps.application
	IN PACKAGE:		apps
	FULL PATH:		$GIT_ROOT/GLaDOS/src/apps/application.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (Generic Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.apps (application system component)


	MODULE DESCRIPTION:
	===================

		This module defines the abstract base class Application_ from which
		the subclasses for specific GLaDOS applications should be derived.
		
	Public Classes:
	---------------
	
		Application_	- 
		
			Abstract base class from which to derive subclasses for specific 
			GLaDOS applications.
	
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

global __all__	# List of public names exported by this module.
__all__ = [

		'Application_'		# Abstract base class for GLaDOS applications.

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

from infrastructure.logmaster	import getLoggerInfo, ThreadActor

	#----------------------------------------------------------
	# Go ahead and create or access the logger for this module,
	# and obtain the software component name for our package.

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	1.3.2. These modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from apps.appHelp				import	AppHelpModule	
	# Generic help module for GLaDOS applications.

from apps.appCommands			import	AppCommandModule
	# Generic command module for GLaDOS applications.

from field.placement			import	Placement, SLIDE_TO_BOTTOM
		# This is needed to place application windows on the receptive field.

from windows.windowSystem		import	Window		# Apps need to create their window(s).

from processes.processSystem	import	SubProcess	# Apps need to create their subprocess(es).

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


	#|==========================================================================
	#|
	#|	3. Class forward declarations.					   [module code section]
	#|
	#|			Pre-declare classes to be defined later in this module.
	#|			(Such dummy definitions are really only useful in type 
	#|			hints, which don't really do anything, but are useful
	#|			as documentation in argument lists.)
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class	Application_:	pass	# Abstract base class for applications.


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
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	application.Application_		  [module public abstract class]
			#|
			#|		This is the abstract superclass from which the class 
			#|		for each specific GLaDOS application should be derived.
			#|
			#|		The class for a typical specific application should 
			#|		generally be declared as a singleton class, to ensure 
			#|		that there is only one instance of each application 
			#|		extant within the system. (Although, that might be 
			#|		changed later, if/when we want to support hosting of 
			#|		multiple AI personas simultaneously within one Python 
			#|		runtime.)
			#|
			#|
			#|	Virtual instance methods:
			#|	-------------------------
			#|
			#|	These methods can or should be extender or overridden in
			#|	subclasses.  The default implementations provided below are 
			#|	not intended to be called directly by external code.
			#|
			#|		.appSpecificInit(conf) - Do app-specific initialization.
			#|
			#|		.createCommandModule() - Create the application's command module.
			#|
			#|		.getHelpIntro() [OVERRIDE] - Return the intro text for the
			#|			application's help module. This is called by the default
			#|			AppHelpModule class to initialize the app's help module.
			#|
			#|		.grabFocus() [EXTEND] - Tell the application to grab the
			#|			command focus.
			#|
			#|		.start() [EXTEND] - Start the application running.
			#|
			#|		.openWins() [EXTENSIBLE] - Open the application's windows.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
class Application_:

	"""Abstract base class for GLaDOS applications. This class is not actually 
		instantiated directly, but is the superclass from which the subclass for 
		each specific application should be derived."""
	
	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Public data members:					   [class documentation section]
	#|	====================
	#|
	#|		These data members are public, and can be accessed directly
	#|		by any code that has access to an instance of this class.
	#|		They may be implemented either as instance variables, or as
	#|		properties (using the @property decorator).
	#|
	#|		Those implemented as instance variables may be initialized
	#|		(to default values) as class variables, which may be overrid-
	#|		den by subclass variables; then these default values may be 
	#|		later overridden by instance variables.
	#|
	#|
	#|	Basic application information:
	#|	------------------------------
	#|
	#|		.name [string]	- Short name for the application; used in
	#|			app-launch commands, help items, and other places where a 
	#|			short name is needed.  This name should be unique among all
	#|			applications installed in the system.  By convention, it
	#|			should be capitalized, and should not contain any spaces.
	#|			Some examples: 'Clock', 'Info', 'Goals', 'Help', 'Settings',
	#|			and so forth.
	#|
	#|
	#|	App sonfiguration information:
	#|	------------------------------
	#|
	#|		.confFileDir [string] - Path to the directory containing the application's
	#|			app-specific configuration file, if any.
	#|
	#|		.confFile [string]	- Path to the application's configuration file.
	#|
	#|		.conf [dict]		- Application-specific configuration parameters.
	#|			[NOTE: This one has not yet been exposed as a public prop-
	#|			erty, but see the private data member _conf below.]]
	#|
	#|
	#|	General application parameters:
	#|	-------------------------------
	#|
	#|		.autoStart [bool]	- Whether to start up the app automatically on 
	#|			system startup.
	#|
	#|		.autoOpen [bool]	- Whether to open the app automatically once the 
	#|			receptive field is created.
	#|
	#|		.autoFocus [bool]	- Whether the app should grab the command focus 
	#|			when it is first opened and whenever it is refreshed.
	#|
	#|		.loudUpdate [bool]	- Whether the app's window updates should wake 
	#|			up the AI if it is sleeping.
	#|
	#|		.placement [Placement] - Where to place the app window in the AI's
	#|			receptive field. (See the field.placement module for details.)
	#|
	#|		.sticky [bool] - Whether the app window should be *sticky*, meaning 
	#|			that it will anchor itself to the top of the receptive field
	#|			rather than scrolling off the top of the screen.  (This setting
	#|			is only relevant when the app window is floating.)
	#|			[This feature is not yet implemented.]
	#|
	#|
	#|	App settings module information:
	#|	--------------------------------
	#|
	#|		.settingsModule [SettingsModule] - The top-level settings module that is
	#|			installed for this application in the interactive settings management 
	#|			facility. [NOT YET IMPLEMENTED.]
	#|
	#|
	#|	App persistent data information:
	#|	--------------------------------
	#|
	#|		.dataDir [string]		- The path to the application's data directory,
	#|			within the AI's data directory.  This directory is used to store
	#|			application-specific data files.
	#|
	#|
	#|	Help-related information:
	#|	-------------------------
	#|
	#|		.helpIntro [string] - Introductory text for the application's 
	#| 			main help screen. If provided, this string will be displayed on
	#|			the screen of the help module for this application, followed by
	#|			any help text for the application's command module.
	#|
	#|		.helpText [string] - If provided, this string will be displayed on 
	#|			the main screen of the help module for this application. (This
	#|			overrides any help text that might have been automatically
	#|			generated for the application by appHelp.AppHelpModule.)
	#|			This is used by appHelp.AppHelpModule, but it may be overridden 
	#|			by the application's help-text config parameter, or by the 
	#|			application's custom help module, if it exists.
	#|
	#|
	#|	App command module information:
	#|	-------------------------------
	#|
	#|		.cmdModuleCls [AppCommandModule] - The class to be used for creating
	#|			the application's main command module.  This should generally be
	#|			overridden by the application's subclass and reassigned to the
	#|			application's actual command module class, which should be a
	#|			subclass of AppCommandModule.
	#|
	#|		.commandModule [cmdModuleCls] - The top-level command module that
	#|			is installed on behalf of this application in GLaDOS' command 
	#|			interface.  Provides all of the commands and subcommands assoc-
	#|			iated with the application.
	#|
	#|
	#|	Basic run-time state information:
	#|	---------------------------------
	#|
	#|		.state [string]	- A symbolic indicating the overall state of the 
	#|			application.  It should be one of the following values:
	#|
	#|				'initializing'		- Hasn't finished being initialized yet.
	#|
	#|				'not-yet-started'	- Initialized, but not yet running.
	#|
	#|				'running'			- Has been initialized and started.
	#|
	#|				'open'				- Running and its window(s) is/are open 
	#|										on the AI's receptivefield.
	#|
	#|				'suspended'			- The app is paused indefinitely.
	#|
	#|				'terminated'		- The has ended all activity (until 
	#|										app or system restart).
	#|
	#|	Most of the following were suggested by Copilot but are not yet implemented:
	#|
	#|		.launched [bool]	- True if/when the app has been started.
	#|
	#|		.hasFocus [bool]	- Does this app currently have the command focus?
	#|
	#|		.isRunning [bool]	- True if the app is running (i.e., not suspended).
	#|
	#|		.isSuspended [bool]		- True if the app is suspended.
	#|
	#|		.isTerminated [bool]	- True if the app has been terminated.
	#|
	#|		.isInitialized [bool]	- True if the app has been initialized.
	#|
	#|		.isNotYetStarted [bool]	- True if the app has been initialized, but not yet started.
	#|
	#|		.isInitializing [bool]	- True if the app is in the process of being initialized.
	#|
	#|		.isOpen [bool]		- True if the app is open (i.e., its window(s) are open).
	#|
	#|		.isClosed [bool]	- True if the app is closed (i.e., its window(s) are closed).
	#|
	#|
	#|	Major application runtime components:
	#|	-------------------------------------
	#|
	#|		.window [Window]		- The main GLaDOS window for this app.
	#|
	#|		.process [SubProcess]	- The primary GLaDOS process that is running in
	#|			the background on behalf of this application (if any).
	#|
	#|
	#|--------------------------------------------------------------------------
	#|	End list of public data members for abstract class Application_.
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#/==========================================================================
	#|	Here, we go ahead and initialize some of the public data members with 
	#|	class variable defaults; these are easily overridden in subclasses.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#------------------------------------------------
	# Default values for some application parameters:

	autoStart = False	# Don't start the app automatically when it's created.
	autoOpen = False	# Don't open the app's window automatically when it's created.
	autoFocus = False	# Don't give the app the command focus automatically when it's created/refreshed.
	loudUpdate = False	# Don't wake up the AI when the app's window is updated.
	placement = SLIDE_TO_BOTTOM		# Default placement for new app windows.

	# NOTE: The below is commented out because the default help intro message
	# is now constructed in the getHelpIntro() method, which may be overridden by
	# the Application_ subclass for each application.  However, subclasses may
	# also choose to provide their default help message by just defining a class
	# variable named "helpIntro" (as shown below).

	# # This default help intro message is just a placeholder.  It should be
	# # overridden by the Application_ subclass for each application.
	# helpIntro = \
	# 	"This application's introductory help text has not yet been defined. " \
	# 	"Please contact the application's developer for more information."

	# The class to be used for creating the application's main command module.
	# This should generally be overridden by the application's subclass.
	cmdModuleClass = AppCommandModule		# Default command module class.
		# This is a generic command module class for applications.
		# It includes commands for starting, stopping, and suspending 
		# the application.


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Private data members for Application_:	   [class documentation section]
	#|	======================================
	#|
	#|	As private data members, these are not intended to be accessed directly
	#|	by external code, although they might be accessible indirectly through 
	#|	properties or methods.  They are documented here for the benefit of
	#|	developers who are modifying the GladOS codebase.
	#|
	#|		._conf [dict]		- Application-specific configuration parameters.
	#|
	#|		._helpModule [HelpModule] - The top-level help module that is installed
	#|			on behalf of this application in GLaDOS' help system. (This will be
	#|			set to a generic appHelp.AppHelpModule instance if the application
	#|			does not provide its own help module.)
	#|
	#|		._launched [bool]	- True if/when the app has been started.
	#|
	#|		._hasFocus [bool]	- Is this the app that currently has the command focus?
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#/==========================================================================
	#|	Here, we go ahead and initialize some of the private data members with 
	#|	class variable defaults; these are easily overridden in subclasses.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# The class to be used for creating the application's main help module.
	# This may be overridden by the application's subclass.
	_helpModuleClass = AppHelpModule		# appHelp.AppHelpModule
		# This is a generic help module class for applications.
		# It includes help items for the application's commands.

	# The application's main help module, if it has been created. (It hasn't yet.)
	_helpModule = None


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	newApplication.__init__()				   [special instance method]
		#|
		#|		This is the default initializer called by the class con-
		#|		structor to initialize new instances of (concrete sub-
		#|		classes of!) the Application_ abstract class.  Rather 
		#|		than overriding this method, subclasses should preferably
		#|		extend it by defining .appSpecificInit().
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(
			newApp		:Application_,	
				# This new Application_ instance, to be initialized.
			
			name:str,				# The name of the application object (e.g., 'Goals').
			
				# The following parameters may be (optionally) provided to 
				# configure the application's behavior and appearance on the 
				# receptive field. If not provided, default values from class
				# or subclass variables are used.

			autoStart:bool=None, 		# Whether to start up the app automatically on system startup.
			autoOpen:bool=None,			# Whether to open the app automatically once the receptive field is created.
			autoFocus:bool=None,		# Whether the app should grab the command focus when first opened.
			loudUpdate:bool=None,		# Whether the app's window updates should wake up the AI.
			placement:Placement=None,	# Where to place the app window in the receptive field.
			#sticky:bool=None,			# Whether the app window should be sticky (i.e., stay on top).
			
			conf:dict = {}		# Application-specific dictionary structure.
		):
		
		"""Default initializer for new instances of concrete subclasses of the 
			Application_ abstract class.  Instance initializers for subclasses 
			should extend this method by defining .appSpecificInit()."""

			#|----------------------------------------------------------------
			#| Designate the state of this application as "initializing."
			#| (So that, if anyone looks at us while we're still initializing, 
			#| they'll be able to see that we're not ready to use yet.)

		newApp.state = 'initializing'

			#|----------------------------------------------------------------
			#| Initialize any arguments not provided by the caller to their
			#| default values, obtained from class or subclass variables.

		if autoStart is None:		autoStart = newApp.autoStart
		if autoOpen is None:		autoOpen = newApp.autoOpen
		if autoFocus is None:		autoFocus = newApp.autoFocus
		if loudUpdate is None:		loudUpdate = newApp.loudUpdate
		if placement is None:		placement = newApp.placement
		#if sticky is None:			sticky = newApp.sticky

			#|----------------------------------------------------------------
			#| Output some debug-level diagnostics.

		_logger.debug(f"Initializing application '{name}' with the following parameters:")

		_logger.debug(f"\tautoStart = {autoStart}, autoOpen = {autoOpen}, "
					  f"autoFocus = {autoFocus}, loudUpdate = {loudUpdate}, "
					  f"placement = {placement}")

			#|-----------------------------------------------------------------------------
			#|	Store our parameters as instance variables, so that they can be accessed
			#|	by the application's methods.  Most of these are stored in public instance
			#|	variables so that external code may access them.  (Note that, however, we 
			#|	store the 'conf' parameter as a private instance variable, since it's 
			#|	intended to be accessed mainly by the application's internal methods.)

		newApp.name 				= name			# The name of the application object.
		
		newApp.autoStart			= autoStart		# Whether to start up the app automatically on system startup.
		newApp.autoOpen				= autoOpen		# Whether to open app automatically when receptive field exists.
		newApp.autoFocus			= autoFocus		# Whether the app should grab the command focus when first opened.
		newApp.loudUpdate			= loudUpdate	# Whether the app's window updates should wake up the AI.
		newApp.initialPlacement		= placement		# Where to place the app's window in the receptive field.
		
		newApp._conf				= conf			# Application-specific dictionary structure.
			# Note this is private. Subclasses should use .conf() to access it. [Not implemented.]

			#|--------------------------------------
			#| Initialize some private data members.

		newApp._launched	= False		# Easy way to tell we've never been started yet.
		newApp._hasFocus	= False		# No app has the focus yet when first created.
			# (It can't be, because doesn't have a command module yet & isn't open yet.)

			#|------------------------------------------------------------------
			#| Create a new window for this application, with a suitable title 
			#| & placement. (Note that we won't actually display this window 
			#| until the application is launched and the cognitive system 
			#| has announced that its receptive field is ready for use.)

		newApp.window = Window(name + ' Window', app=newApp, 
			placement=placement, loudUpdate=loudUpdate)

			#|------------------------------------------------------------------
			#| Create a subprocess (GLaDOS process) for this application, to run 
			#| in that window. Note that we don't actually start up the process 
			#| until the application is launched.

		newApp.process = SubProcess(name, newApp.window)	# Doesn't do anything yet.

			#|-------------------------------------------------------------------
			#| Create the application's command module, and auto-install it in 
			#| the GladOS command interface.

		newApp.initCommandModule()

			#|------------------------------------------------------------------
			#| Do any initialization work that's specific to the individual 
			#| app's Application subclass.  This includes doing any needed 
			#| processing of the application-specific configuration dict.

		newApp.appSpecificInit(conf)

			#|------------------------------------------------------------------
			#| We're done initializing, so now, designate the state of this 
			#| application as "not yet started."

		newApp.state = 'not-yet-started'

	#__/ End default subclass instance initializer for abstract base class Application_.


	#|---------------------------------------------------------------
	#| Expose some of our private instance variables as read-only
	#| properties, so that external code can access them, but not
	#| change them directly.

	@property
	def conf(thisApp) -> dict:
		"""Dictionary property: Application-specific configuration dictionary."""
		return thisApp._conf

	@property
	def hasFocus(thisApp) -> bool:
		"""Boolean property: Does this app currently have the command focus?"""
		return thisApp._hasFocus

	@property
	def launched(thisApp) -> bool:
		"""Boolean property: Has this app been launched?"""
		return thisApp._launched


	#/==========================================================================
	#|	Public instance methods.
	#|	========================
	#|
	#|	Note that some of these methods may or should be extended or 
	#|	overridden in subclasses.
	#|
	#|		.activateCommandModule() [EXTENSIBLE] - Activate the 
	#|			application's command module.
	#|
	#|		.appSpecificInit(conf) [EXTEND] - Do app-specific initialization.
	#|
	#|		.createCommandModule() - Create the application's command module.
	#|
	#|		.createHelpModule() - Create the application's help module.
	#|
	#|		.foreground() [EXTENSIBLE] - Bring the application to the foreground.
	#|
	#|		.getHelpIntro() [OVERRIDE] - Return the intro text for the
	#|			application's help module. This is called by the default
	#|			AppHelpModule class to initialize the app's help module.
	#|
	#|		.grabFocus() [EXTEND] - Tell the application to grab the
	#|			command focus.
	#|
	#|		.initCommandModule() [EXTEND] - Create & install the
	#|			application's command module.
	#|
	#|		.launch() [EXTEND] - Launch the application.
	#|
	#|		.start() [EXTEND] - Start the application running.
	#|
	#|		.openWins() [EXTENSIBLE] - Open the application's windows.
	#|
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	def activateCommandModule(thisApp:Application_):

		"""Activate this application's primary command module, if any."""

		app = thisApp	# For convenience.

		if app.commandModule is not None:
		
			app.commandModule.activate()


	def appSpecificInit(thisApp, conf:dict):

		"""This method performs application-specific initialization,
			using the 'conf' dictionary, which comes from the 'app-config'
			attribute in the system config file (glados-config.hjson).

			Please note that this is a virtual method (placeholder) which
			should be extended or overridden by each application-specific 
			subclass."""

		app = thisApp	# For convenience.

		# Create the application's help module, if it doesn't already
		# exist, and install it in the GLaDOS interactive help system.
		app.helpModule = app.createHelpModule()
		
	#__/ End appSpecificInit().


	def createCommandModule(thisApp:Application_):
	
		"""This virtual method should be overridden in application-specific
			subclasses.	 It should create a command module for the application
			(i.e., an instance of AppCommandModule or one of its subclasses) and
			return it.	Generally, the command module should have been pre-
			loaded with all of the application's commands."""

		app = thisApp	# For convenience.

		cmdModClass = app.commandModuleClass
			# Subclasses should define this as a class attribute.

		if cmdModClass is not None:
			cmdModule = cmdModClass(app)
			return cmdModule

		return None
			# This makes sense since the abstract Application class isn't itself
			# associated with any specific command module. Although, we may add
			# one in the future to handle generic application commands, such as
			# /suspend-app and /exit-app.

	#__/ End createCommandModule().


	# Method to create the help module for this application.

	def createHelpModule(thisApp):		# Create app's main help module.

		"""This virtual method should be overridden in application-specific
			subclasses.	 It should create a help module for the application
			(i.e., an instance of AppHelpModule or one of its subclasses) and
			return it.	Generally, the help module should populate itself with 
			]all of the application's help topics."""

		app = thisApp	# For convenience.

		helpModule = app.helpModule		# Get initial value (probably None).

		# If this app's help module was already created, return it. 
		if helpModule is not None:
			return helpModule

			#|------------------------------------------------------------
			#| Create the help module for this application. This is done
			#| using the application's .helpModuleClass attribute and/or
			#| the application's configuration dictionary, which may
			#| contain a 'help' attribute.

		helpModuleClass = app.helpModuleClass
		if helpModuleClass is not None:

			# Get the app's help module's configuration dictionary.
			conf = app.conf	# Get the app's configuration dictionary.
			helpConf = conf.get('help', None)

			# Instantiate the help module.
			helpModule = helpModuleClass(app, config=helpConf)

		else:
			helpModule = None	# Can't create a help module.

		return helpModule

	#__/ End createHelpModule().


	def foreground(thisApp):

		"""
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
		"""

		app = thisApp

		app.window.resetPlacement()
			# Reset the app's window location back to its initial placement.

		app.activateCommandModule()
			# Activate the app's command module, if it has one.
			# This effectively gives the app the command focus.

		# TODO: Update window decorations? (e.g., change border style to '===',
		# and add command hints to lower border).


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Default method to retrieve the "intro" text for this application's 
	#|	help screen. This is called by the default AppHelpModule class when
	#|	initializing itself.  It can be overridden by subclasses to provide
	#|	a different method for specifying the app's intro text, if desired.

	def getHelpIntro(thisApp):

		"""Returns the introductory text for this application's help screen
			This is used to initialize the application's help module."""

		app = thisApp	# For convenience.

		# Default placeholder intro text if none is provided by the app.
		helpIntro = f"""This is the main help screen for {app.name}, " \
			"which is a GLaDOS application.  Its introductory help text has " \
			"not yet been defined."""

		# Next, check for a '.helpIntro' (instance or class) attribute, 
		# and use that as the intro text instead, if it exists.
		if hasattr(app, 'helpIntro'):
			helpIntro = app.helpIntro

		# Next, look for an 'intro-text' attribute in the app's configuration 
		# dictionary, and use that as the intro text instead, if it exists.
		if 'intro-text' in app._conf:
			helpIntro = app._conf['intro-text']

		# Cache the intro text in a private instance attribute, for reference.
		app._helpIntro = helpIntro

		# Return the intro text.
		return thisApp._helpIntro
	
	#__/ End default getIntroText() method for abstract base class Application_.


	def grabFocus(app):

		"""Tells the app to grab the command focus, if it doesn't already have it.
			This also updates the window appearance to the focus-having style."""
			# (The latter feature is not yet implemented.)

		app._hasFocus = True

		# Here, we really should notify the app's command module 
		# that it now has the focus, so that it can activate any
		# focus-dependent commands.  But we don't have a way to
		# do that yet, so we'll just leave it for now.

			# Tell the app's window that it now has the command focus.
		app.window.notifyOfFocus()	# To implement.
				# The window should respond by changing its decorator style.
				

	def initCommandModule(thisApp:Application_):
	
		"""Initializes and installs the application's command module,
			so that these commands will be available to GLaDOS users
			(including the AI)."""

		app = thisApp	# For convenience.

			# First, create the application's command module.
			# Subclasses should implement this method.

		cmdModule = app.createCommandModule()

			# Remember it for later.

		app.commandModule = cmdModule

			# Auto-install it in the system's command interface.
		# [TO IMPLEMENT]

	#__/ End initCommandModule().


	def launch(self):	# Generic launch method for apps.
		
		"""Launch this app, which generally means, to start the app running (if
		    it's not already running), and open its windows, if they aren't already
		    open. Windows should also be foregrounded (moved to a prominent location,
			resized to their default size) and the app should get the command focus."""

		self.start()		# First, start up the app, if not already started.
		self.openWins()		# Next, tell it to open its windows, if not already open.

		self.foreground()	# Bring the app to the foreground.
	
	#__/ End instance method app.launch().


	def openWins(thisApp):	# Subclasses should override this.

		"""Tells this app to go ahead and automatically open up its window(s)
			on the field, or at least, any windows that are currently designated
			as being eligible to be opened.  Details are app-dependent."""

			# If this app already has its windows open, there's nothing to do. Return.

		if thisApp.state == 'open':
			return

			#-----------------------------------------------------------
			# If we get here, we need to actually open the app's window.

		win = thisApp.window

		win.openWin()	# Tells the window to open itself up.

		thisApp.state = 'open'	# Running, with windows open.

	#__/ End instance method app.openWins().


	def start(self):	# Generic start method for apps.

		"""This method is called whenever an application is started,
			whether this happens during system startup because it's
			an auto-start application, or in response to an explicit
			command. This default implementation just does some basic
			bookkeeping. Subclasses that override this method should
			do a super() call to this version, so as to extend it."""

		# If this app has already been launched, we don't need to do anything.
		if self.launched:
			return

		# This just means the app has been started (for the first time).
		self._launched = True

		# For generic apps, generally speaking, the only thing we need to do
		# when we first start them up is mark them as being in the running state.
		# Note that, in this state, the app's window might not yet be open.
		self.state = 'running'

	#__/ End instance method app.start().


#__/ End module public abstract base class application.Application_.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					 END OF FILE:	apps/application.py
#|=============================================================================
