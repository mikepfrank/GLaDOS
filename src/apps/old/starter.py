# This module exists for purposes of starting up the application system.

from os import path

from config.loader	import	Configuration, getSystemConfiguration

global appSystem
appSystem = None

global appList

class Application:

	# An Application has:
	#
	#	- A name.
	#	- A process.
	#	- A window.
	#	- A state (not-yet-started, running, not running).
	#	- A data directory (within the AI's data directory).
	#		This is used to preserve application state information
	#		between GLaDOS system runs.
	#	- A command module.
	#		Provides all of the commands associated with the 
	#		application.
	#
	# And some methods are:
	#
	#	- launch()
	
	
	def __init__(self, name:str, conf:dict):
	
			# Remember the name of this application.
	
		self.name = name
		
			# Create a new window for this application, with a suitable title.
			# We don't actually display this window until the application is launched.
		
		self.window = window = Window(name + ' Window', self)
		
			# Create a process for this application, to run in that window.
			# We don't actually start the process until the application is launched.
		
		self.process = process = Process(name, window)
		
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

class AppSystem:

	# The AppSystem has:
	#
	#	- Dict of registered applications: Maps app name to app object.

	def __init__(self):
		
		self._appDict = {}

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

		
class AppSystemStarter:


	def __init__(self, config:Configuration):
	
		self.sysConfig = config		# Save our system configuration for later use.
	
		appSystem = AppSystem()		# Create empty initial application system.
		self.appSystem = appSystem
		
			# At this point, we register the applications that are
			# listed as 'available' in our configuration information.
			
		self._registerAvailableApps()
	
	
	def _registerAvailableApps(self):
	
		for app in appList:		# These are simple dict structures.
		
			appName = app['name']
			appClass = app['class']
			
			appConfigs = self.sysConfig.appConfigs
			
			appAvailable = appConfigs[appName]['avail']		# Is the app available to be registered?
			appAutoStart = appConfigs[appName]['auto']
			appConfig	 = appConfigs[appName]['conf']
			
			if appAvailable:
				self.appSystem._registerApp(appName, appClass, appConfig, appAutoStart)
			
		self.appSystem.startup()


#	General classes:
#
#		Application
#		AppSystem
#		AppSystemStarter
#
#
#	Classes for specific applications (move each to its own module):
#
#		1.	Help_App
#		2.	Apps_App (The only app that doesn't appear on the apps list in the Apps app.)
#		3.	Info_App
#		4.	Settings_App
#		5.	Memory_App
#		6.	ToDo_App
#		7.	Diary_App
#		8.	Browse_App
#		9.	Comms_App
#		10.	Writing_App
#		11.	Unix_App


class Help_App(Application):

	"""
		The "Help" tool simply displays some basic information
		about how to use GLaDOS (for the A.I.'s benefit).
	"""

	# Note the string literal given here is just a default Help 
	# message, which may be overridden by the main-msg attribute
	# in the system config file.
	_helpMsg =
		"""
		
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

class Apps_App(Application):

	"""
		Apps - This tool simply displays the list of all the
		available apps, and allows the A.I. to select one to 
		launch.
	"""

	pass

class Info_App(Application):
	
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
	
		sysConf = getSystemConfiguration()
			# Note this retrieves the current value of the 
			# systemConfiguration module-level global from the 
			# conf.loader module object.

			#------------------------------------------------------
			# OK, now, get the location of the AI's data directory.
			
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
			
		with open(infoFilename) as file:
			infoText = "\n" + file.read() + "\n"
			
			#--------------------------------------------------
			# Next, we size our window to exactly fit the text.
			
		self.window.nRows = countLines(infoText)
		
			#----------------------------------------------
			# Finally, we have our window display the text.
			
		self.window.addText(helpMsg)

#__/ End class Info_App.


class Settings_App(Application):

	"""
		Settings - This app can be used by the A.I. to adjust various
		settings within GLaDOS.  These can be associated with major 
		systems or subsystems of GLaDOS, or individual apps or 
		processes. 
	"""

	pass

class Memory_App(Application):
	
	"""
		Memory - The memory tool allows the A.I. to browse and search
		a database of records of its past conversations, thoughts, and
		actions.
	"""

	pass

class ToDo_App(Application):
	
	"""
		ToDo - The idea of this app is that it is a simple to-do list 
		tool, which the A.I. can use to make notes to itself of important
		tasks that it wants to do later.  The tasks can be given priority 
		levels.  The A.I. can check them off or delete them when complete. 
	"""

	pass

class Diary_App(Application):
	
	"""
		Diary - This tool allows the A.I. to keep a "diary" of important
		notes to itself, organized by date/time.
	"""

	pass

class Browse_App(Application):
	
	"""
		Browse - This is a simple text-based tool to facilitate simple web
		browsing and searching.
	"""

	pass

class Comms_App(Application):
	
	"""
		The "comms" tool faciltates the A.I.'s two-way 
		communications with the outside world.  This may include direct 
		messages sent via Telegram, email messages, or other interfaces.  
		This may be broken out later into a whole 'Comms' subfolder of 
		separate apps.
	"""

	pass

class Writing_App(Application):
	
	"""
		The writing tool is an interface that helps the A.I.
		to compose and edit complex, hierarchically-structured works:  
		Stories, poems, and extended multi-chapter books.
	"""

	pass

class Unix_App(Application):
	
	"""
		This app gives the A.I. access to an actual Unix shell
		environment on the host system that GLaDOS is running on.  The A.I.
		runs within its own user account with limited permissions.
	"""

	pass

appList = 
	[
		{
			'name':		'Help',
			'class':	Help_App
		},
		{	
			'name':		'Apps',
			'class':	Apps_App
		},
		{
			'name':		'Info',
			'class':	Info_App
		},
		{
			'name':		'Settings',
			'class':	Settings_App
		},
		{
			'name':		'Memory',
			'class':	Memory_App
		},
		{
			'name':		'ToDo',
			'class':	ToDo_App
		},
		{
			'name':		'Diary',
			'class':	Diary_App
		},
		{
			'name':		'Browse',
			'class':	Browse_App
		}
		{
			'name':		'Comms',
			'class':	Comms_App
		},
		{
			'name':		'Writing',
			'class':	Writing_App
		},
		{
			'name':		'Unix',
			'class':	Unix_App
		},
	]
