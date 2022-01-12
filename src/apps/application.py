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

from field.placement			import	Placement
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
			#|		multiple AI personas simultaneously.)
			#|
			#|	Public data members: 	(See documentation in class body.)
			#|	--------------------
			#|
			#|	Virtual instance methods:	(Can/should be overridden in subclasses.)
			#|	-------------------------
			#|
			#|		.appSpecificInit(conf) - Do app-specific initialization.
			#|
			#|		.createCommandModule() - Create the application's command module.
			#|
			#|		.start() [EXTEND] - Start the application running.
			#|
			#|		.openWins [EXTENSIBLE] - Open the application's windows.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
class Application_:

	"""Abstract base class for GLaDOS applications."""
	
	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Public data members:							   [class documentation]
	#|	--------------------
	#|
	#|		.name [string]	- Short name for the application.
	#|
	#|		.state [string]	- State of the application.  One of:
	#|
	#|			'initializing'		- Hasn't finished being initialized yet.
	#|
	#|			'not-yet-started'	- Initialized, but not yet running.
	#|
	#|			'running'			- Has been initialized and started.
	#|
	#|			'open'				- Running and its window(s) is/are open on the field.
	#|
	#|			'suspended'			- Paused indefinitely
	#|
	#|			'terminated'		- Has ended all activity (until system restart).
	#|
	#|		.window [Window]		- The main GLaDOS window for this app.
	#|
	#|		.process [SubProcess] - The primary GLaDOS process that is running in
	#|			the background on behalf of this application.
	#|
	#|		.settingsModule [SettingsModule] - The top-level settings module that is
	#|			installed for this application in the settings management facility.
	#|			[NOT YET IMPLEMENTED.]
	#|
	#|		.commandModule [CommandModule] - The top-level command module that
	#|			is installed on behalf of this application in GLaDOS' command interface.
	#|			Provides all of the commands associated with the application.
	#|
	#|
	#|	Private data members:
	#|	---------------------
	#|
	#|		._conf [dict]		- Application-specific configuration parameters.
	#|
	#|		._launched [bool]	- True if/when the app has been started.
	#|
	#|		._hasFocus [bool]	- Is this the app that currently has the command focus?
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	"""
		Generically, an application also has the following associated
		elements:

			- A data directory (within the AI's data directory).
				This is used to preserve application state
				information in between GLaDOS system runs.
				[NOT YET IMPLEMENTED]
	"""

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	newApplication.__init__()				   [special instance method]
		#|
		#|		This is the default initializer for instances of concrete
		#|		subclasses of the Application_ abstract class.  Rather 
		#|		than overriding this method, subclasses should extend it
		#|		by defining .appSpecificInit().
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(
			newApp:Application_,	# This new Application_ instance, to be initialized.
			
			name:str,				# The name of the application object.
			
			autoStart:bool, 		# Whether to start up the app automatically on system startup.
			autoOpen:bool,			# Whether to open the app automatically once the receptive field is created.
			autoFocus:bool,			# Whether the app should grab the command focus when first opened.
			loudUpdate:bool,		# Whether the app's window updates should wake up the AI.
			placement:Placement,	# Where to place the app window in the receptive field.
			
			conf:dict				# Application-specific dictionary structure.
		):
		
		"""Default initializer for new instances of concrete subclasses of the Application_ abstract class.
			Instance initializers for subclasses should extend this method by defining .appSpecificInit()."""

			#|-------------------------
			#| Debug-level diagnostics.

		_logger.debug(f"Initializing application '{name}' with the following parameters:")

		_logger.debug(f"\tautoStart = {autoStart}, autoOpen = {autoOpen}, "
					  f"autoFocus = {autoFocus}, loudUpdate = {loudUpdate}, "
					  f"placement = {placement}")

			#|----------------------------------------------------------------
			#| Designate the state of this application as "initializing."
			#| (So that, if anyone looks at us while we're still initializing, 
			#| they'll be able to see that we're not ready to use yet.)

		newApp.state = 'initializing'

			#|-----------------------------------------------------------------------------
			#| Remember the name of this application, & other arguments to our constructor.

		newApp.name 				= name			# The name of the application object.
		
		newApp.autoStart			= autoStart		# Whether to start up the app automatically on system startup.
		newApp.autoOpen				= autoOpen		# Whether to open app automatically when receptive field exists.
		newApp.autoFocus			= autoFocus		# Whether the app should grab the command focus when first opened.
		newApp.loudUpdate			= loudUpdate	# Whether the app's window updates should wake up the AI.
		newApp.initialPlacement		= placement		# Where to place the app's window in the receptive field.
		
		newApp._conf				= conf			# Application-specific dictionary structure.

			#|--------------------------------------
			#| Initialize some private data members.

		newApp._launched			= False		# Easy way to tell we've never been started yet.
		newApp._hasFocus			= False		# No app has the focus yet when first created.

			#|------------------------------------------------------------------
			#| Create a new window for this application, with a suitable title 
			#| & placement. (Note that we don't actually display this window 
			#| until the application is launched and the cognitive system 
			#| announces that its receptive field is ready for use.)

		newApp.window = Window(name + ' Window', app=newApp, 
			placement=placement, loudUpdate=loudUpdate)

			#------------------------------------------------------------------------------------
			# Create a subprocess (GLaDOS process) for this application, to run in that window.
			# Note that we don't actually start up the process until the application is launched.

		newApp.process = SubProcess(name, newApp.window)

			#-----------------------------------------------------------------------------------------
			# Create the application's command module, and install it in the GLaDOS command interface.

		newApp.initCommandModule()

			#-----------------------------------------------------------------------------------------
			# Do any initialization work that's specific to the individual app's Application subclass.
			# This includes doing any needed processing of the application-specific configuration dict.

		newApp.appSpecificInit(conf)

			#-----------------------------------------------------------------------------------------------
			# We're done initializing, so now, designate the state of this application as "not yet started."

		newApp.state = 'not-yet-started'

	#__/ End default subclass instance initializer for abstract base class Application_.


	def grabFocus(app):

		"""Tells the app to grab the command focus, if it doesn't already have it.
			This also updates the window appearance to the focus-having style."""

		app._hasFocus = True

			# Tell the app's window that it now has the command focus.
		app.window.notifyOfFocus()	# To implement.
				# The window should respond by changing its decorator style.
				

	def appSpecificInit(self, conf:dict):

		"""This method performs application-specific initialization,
			using the 'conf' dictionary, which comes from the 'app-config'
			attribute in the system config file (glados-config.hjson).

			Please note that this is a virtual method (placeholder) which
			needs to be overridden by each application-specific subclass."""

		pass	# Does nothing.
		
	#__/ End appSpecificInit().


	def initCommandModule(self):
	
		"""Initializes and installs the application's command module,
			so that these commands will be available to GLaDOS users
			(including the AI)."""

			# First, create the application's command module.
			# Subclasses should implement this method.

		cmdModule = self.createCommandModule()

			# Remember it for later.

		self.commandModule = cmdModule

			# Install it in the system's command interface.
		# [TO IMPLEMENT]

	#__/ End initCommandModule().


	def createCommandModule(self):
	
		"""This virtual method should be overridden in application-specific
			subclasses.	 It should create a command module for the application
			(i.e., an instance of CommandModule or one of its subclasses) and
			return it.	Generally, the command module should have been pre-
			loaded with all of the application's commands."""

		return None
			# This makes sense since the abstract Application class isn't itself
			# associated with any specific command module. Although, we may add
			# one in the future to handle generic application commands, such as
			# /suspend-app and /exit-app.

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


	def launch(self):	# Generic launch method for apps.
		
		self.start()		# First, start up the app, if not already started.
		self.openWins()		# Next, tell it to open its windows.


	def openWins(thisApp):	# Subclasses should override this.

		"""Tells this app to go ahead and automatically open up its window(s)
			on the field, or at least, any windows that are currently designated
			as being eligible to be opened.  Details are app-dependent."""

		win = thisApp.window

		win.openWin()	# Tells the window to open itself up.

		thisApp.state = 'open'	# Running, with windows open.

	#__/ End instance method app.openWins().


#__/ End module public abstract base class application.Application_.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					 END OF FILE:	apps/application.py
#|=============================================================================
