#|==============================================================================
#|                TOP OF FILE:    apps/appSystem.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:      apps/appSystem.py     			 [Python module source file]

    MODULE NAME:    apps.appSystem
    IN PACKAGE:     apps
    FULL PATH:      $GIT_ROOT/GLaDOS/src/apps/appSystem.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
    SW COMPONENT:   GLaDOS.apps (application system component)


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

			* Application_  - Abstract base class from which to derive
								classes for specific applications.
			
			* TheAppSystem	- Singleton class for the overall application
								system, itself.

		The classes for specific applications include (this one goes to 11):

			1. Help_App		- The Help app implements the help system,
								which allows the AI to browse a set of
								help menus and obtain detailed help for 
								specific commands.
			
			2. Apps_App     - This app is not yet implemented, but it is
								anticipated to become needed in the future
								as GLaDOS becomes more complex.  The intent
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
    #|   1. Module imports.                                [module code section]
    #|
    #|          Load and import names of (and/or names from) various
    #|          other python modules and pacakges for use from within
    #|          the present module.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|  1.1. Imports of standard python modules.    [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from os         import path             # Manipulate filesystem path strings.


        #|======================================================================
        #|  1.2. Imports of custom application modules. [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|  The following modules, although custom, are generic utilities,
			#|  not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.  (This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster   import getComponentLogger

        # Go ahead and create or access the logger for this module.

global _component, _logger      # Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)            # Create the component logger.


        # A simple decorator for singleton classes.
from infrastructure.decorators  import  singleton
from infrastructure.utils       import  countLines

			#|----------------------------------------------------------------
			#|  The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from config.configuration       import  TheConfiguration   
        # Singleton class that provides the current GLaDOS system configuration.

from windows.windowSystem       import  Window
from processes.processSystem    import  SubProcess

    #|==========================================================================
    #|
    #|   2. Globals                                        [module code section]
    #|
    #|      Declare and/or define various global variables and
    #|      constants.  Note that top-level 'global' statements are
    #|      not strictly required, but they serve to verify that
    #|      these names were not previously used, and also serve as 
    #|      documentation.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|
        #|  Special globals.                                    [code subsection]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language. 
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__  # List of public symbols exported by this module.
__all__ = [
		'Application_',		# Abstract base class for deriving applications.
		'AppSystem',        # Singleton class for the application system.
		'Help_App',         # Application that manages the help system.
		'Info_App',         # Application that manages the information window.
            # Add others as they are implemented.
    ]


		#|======================================================================
		#|      
		#|	Private globals.                                   [code subsection]
		#|
		#|		These globals are not supposed to be accessed from 
		#|      outside of the present module.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|	_APP_LIST                       [module private global constant]
			#|
			#|		This is a structure (list of dicts) that defines the
			#|      full list of supported applications.  See the 
			#|      definition at the end of the file for further 
			#|      documentation.
			#|
			#|      Note that some of these may not yet be implemented.
			#|
			#|      The structure of each dict in the list is:
			#|
			#|      	name    - Short text name of the application.
			#|          			This must match the name used in the
			#|                      app-configs attribute of the system
			#|                      config file (glados-config.hjson).
			#|
			#|			class   - Class defining the application.  This 
			#|						must be a subclass of Application_.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global _APP_LIST    # We could put this into the AppSystem class instead.


    #|==========================================================================
    #|
    #|	3. Classes.                                        [module code section]
    #|
    #|      Declare and/or define the classes of this module.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	3.1. General classes.                              [code subsection]
		#|
		#|		These classes are not application-specific but apply 
		#|      generally to the entire application system.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
                
class Application_:
	#---------------------------------------------------------------------------
	"""
	app.Application_                              [module public abstract class]
	
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
		
			- launch()      - Starts the application running.
	"""
	
	def __init__(self, name:str, conf:dict):
	
			# Remember the name of this application.

		self.name = name
		
			# Create a new window for this application, with a suitable title.
			# We don't actually display this window until the application is launched.
		
		self.window = Window(name + ' Window', app=self)
		
			# Create a process for this application, to run in that window.
			# We don't actually start the process until the application is launched.
	
		self.process = Process(name, self.window)
		
			# Designate the state of this application as not yet started.
		
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
		subclasses.  It should create a command module for the application
		(i.e., an instance of CommandModule or one of its subclasses) and
		return it.  Generally, the command module should have been pre-
		loaded with all of the application's commands.
		"""
		
		return None             
			# This makes sense since the abstract Application class isn't itself 
			# associated with any specific command module.
				
	#__/ End createCommandModule().
	
#__/ End class Application.

@singleton
class AppSystem:

	# The AppSystem has:
	#
	#   - Dict of registered applications: Maps app name to app object.


	def __init__(self):     # One-time initializer for singleton instance.
			
		self._appDict = {}
		
			# At this point, we register the applications that are
			# listed as 'available' in our configuration information.
				
		self._registerAvailableApps()


	def _registerApp(self, appName:str, appClass:type, appConfig:dict, appAutoStart:bool):
			
			# First, call the class constructor to actually create the application object.
				
		app = appClass(appName, appConfig)
		
			# Now add that app object to our dict of apps.
		
		self._appDict[appName] = app
		
			# Annotate the app with its autostart indicator.
		app.autoStart = appAutoStart
					
	def __call__(self, name:str):
		return self._appDict(name)
			
		# This executes the startup sequence, which basically consists of starting up
		# all of the apps that we tagged for auto-start.
			
	def startup(self):
		for app in self._appDict.values():
			if app.autoStart:
				app.start()

	def _registerAvailableApps(self):
	
		for app in _APP_LIST:    # These are simple dict structures.
		
			appName = app['name']
			appClass = app['class']
			
			appConfigs = Configuration().appConfigs
			
			appAvailable = appConfigs[appName]['avail']  # Is the app available to be registered?
			appAutoStart = appConfigs[appName]['auto']
			appConfig        = appConfigs[appName]['conf']
			
			if appAvailable:
				self._registerApp(appName, appClass, appConfig, appAutoStart)
				
		self.startup()
			
#__/ End class AppSystem.
        

		#|======================================================================
		#|	3.2. Application-specific classes.                 [code subsection]
		#|
		#|		These classes define specific applications within GLaDOS.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

@singleton
class Help_App(Application_):

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
class Apps_App(Application_):

	"""
	Apps - This tool simply displays the list of all the
	available apps, and allows the A.I. to select one to 
	launch.
	"""

	pass

@singleton
class Info_App(Application_):
        
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
	
			#----------------------------------------------------------
			# First, get the system configuration, because it contains
			# key information we need, such as the location of the AI's 
			# data directory.

		sysConf = Configuration()
			# Note this retrieves the singleton instance 
			# of the Configuration class.

			#------------------------------------------------------
			# First, get the location of the AI's data directory,
			# which is in the system configuration.
				
		aiDataDir = sysConf.aiDataDir
		
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
				infoText = "\n" + file.read() + "\n"
				
		_logger.debug("Loaded inital info text:\n" + infoText)

			#--------------------------------------------------
			# Next, we size our window to exactly fit the text.
				
		self.window.nRows = countLines(infoText)
		
			#----------------------------------------------
			# Finally, we have our window display the text.
				
		self.window.addText(infoText)

	def start(inst):
			pass

#__/ End class Info_App.


@singleton
class Settings_App(Application_):

	"""
	Settings - This app can be used by the A.I. to adjust various
	settings within GLaDOS.  These can be associated with major 
	systems or subsystems of GLaDOS, or individual apps or 
	processes. 
	"""

	pass

@singleton
class Memory_App(Application_):
        
	"""
	Memory - The memory tool allows the A.I. to browse and search
	a database of records of its past conversations, thoughts, and
	actions.
	"""

	pass

@singleton
class ToDo_App(Application_):
        
	"""
	ToDo - The idea of this app is that it is a simple to-do list 
	tool, which the A.I. can use to make notes to itself of important
	tasks that it wants to do later.  The tasks can be given priority 
	levels.  The A.I. can check them off or delete them when complete. 
	"""

	pass

@singleton
class Diary_App(Application_):
        
	"""
	Diary - This tool allows the A.I. to keep a "diary" of important
	notes to itself, organized by date/time.
	"""

	pass

@singleton
class Browse_App(Application_):
        
	"""
	Browse - This is a simple text-based tool to facilitate simple web
	browsing and searching.
	"""

	pass

@singleton
class Comms_App(Application_):
        
	"""
	The "comms" tool faciltates the A.I.'s two-way 
	communications with the outside world.  This may include direct 
	messages sent via Telegram, email messages, or other interfaces.  
	This may be broken out later into a whole 'Comms' subfolder of 
	separate apps.
	"""

	pass

@singleton
class Writing_App(Application_):
        
	"""
	The writing tool is an interface that helps the A.I.
	to compose and edit complex, hierarchically-structured works:  
	Stories, poems, and extended multi-chapter books.
	"""

	pass

@singleton
class Unix_App(Application_):
        
	"""
	This app gives the A.I. access to an actual Unix shell
	environment on the host system that GLaDOS is running on.  The A.I.
	runs within its own user account with limited permissions.
	"""

	pass

    #|==========================================================================
    #|
    #|	4. Main body.                                	   [module code section]
    #|
    #|		This code constitutes the main body of the module
	#|      which is executed on the initial import of the module.
	#|                      
	#|      All it does currently is initialize the appList global 
	#|      using the application classes as defined above.
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
		#|		name    - Short text name of the application.  This must 
		#|					match the name used in the app-configs 
		#|                  attribute of the system config file 
		#|                  (glados-config.hjson).
		#|
		#|      class   - Class defining the application.  This must be 
		#|                  one of the subclasses of Application_ 
		#|                  defined above.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

_APP_LIST = [
		{
			'name':         'Help',
			'class':        Help_App
		},
		{       
			'name':         'Apps',
			'class':        Apps_App
		},
		{
			'name':         'Info',
			'class':        Info_App
		},
		{
			'name':         'Settings',
			'class':        Settings_App
		},
		{
			'name':         'Memory',
			'class':        Memory_App
		},
		{
			'name':         'ToDo',
			'class':        ToDo_App
		},
		{
			'name':         'Diary',
			'class':        Diary_App
		},
		{
			'name':         'Browse',
			'class':        Browse_App
		},
		{
			'name':         'Comms',
			'class':        Comms_App
		},
		{
			'name':         'Writing',
			'class':        Writing_App
		},
		{
			'name':         'Unix',
			'class':        Unix_App
		},
	]


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                   END OF FILE:   apps/appSystem.py
#|=============================================================================
