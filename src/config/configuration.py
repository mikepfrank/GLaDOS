#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 config/configuration.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""

	FILE NAME:		config/configuration.py			 [Python module source file]
		
	IN PACKAGE:		config
	MODULE NAME:	config.configuration
	FULL PATH:		$GIT_ROOT/GLaDOS/src/config/configuration.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (Generic Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.server.config (server configuration component)


	MODULE DESCRIPTION:
	===================
		
		This module allows loading of the GLaDOS system configuration from a 
		config file or files.  The default name of the main config file is
				
			'glados-config.hjson'
		
		It is expected by default to reside in the directory from which the 
		server process was launched. The file format is HJSON, which is a more 
		human-readable extension of JSON format; see https://hjson.github.io/.
		
		The config file to use can be customized somewhat by setting environment 
		variables. If the environment variable GLADOS_CONFIG_FILENAME is set, 
		then it is used instead of the default config filename.	 If the 
		environment variable GLADOS_PATH is set, then it (rather than the 
		current directory) is used as the location in which to look for the 
		config file. If the environment variable GLADOS_CONFIG_PATH is set, then 
		it is used instead of any of the above.	 
		
		There is also a separate file for AI-specific settings.  It is normally
		installed in the AI's data directory, under say '/opt/AIs/'.  There are
		additional environment variables to customize its location as well.  See
		under 'ENVIRONMENT VARIABLES,' below.


	USAGE:
	======
		
		from config.configuration import TheConfiguration
		...
		config = TheConfiguration()				# Construct singleton instance.
		...
		

	ENVIRONMENT VARIABLES:
	======================
	

		The following environment variables are for main system configuration.
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	

		GLADOS_CONFIG_FILENAME
				
			If the environment variable GLADOS_CONFIG_FILENAME is set, then 
			it is used instead of the default config filename.	Otherwise,
			the default filename 'glados-config.hjson' is used.
		
		
		GLADOS_PATH
						
			If the environment variable GLADOS_PATH is set, then it (rather 
			than the current directory) is used as the location in which to 
			look for the config file.
				
				
		GLADOS_CONFIG_PATH
					   
			If the environment variable GLADOS_CONFIG_PATH is set, then it
			is used as the full path to the config file, instead of using 
			any of the above.  
				
				
		The following environment variables are for configuring the AI persona.
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		

		AI_DATADIR
				
			The environment variable AI_DATADIR should be set to point to the
			data directory in which all data specific to a given AI persona
			is stored; for example, '/opt/AIs/gladys'.	If this environment
			variable is not defined, we default to using the 'ai-data/'
			subdirectory of the directory from which the GLaDOS server is 
			executed.
						
			Ideally, each AI should be given its own user account on the 
			host, and GLaDOS should be run from within that account, so that 
			the files in the data directory can be made writable only by the
			AI itself.
		
		
		AI_CONFIG_FILENAME
		
			If this is envrionment variable is set, then it will be used as 
			the filename (relative to AI_DATADIR) from which we will load the 
			main high-level configuration data for the AI persona to be hosted
			in the GLaDOS system.  If not set, we use the a default filename 
			'ai-config.hjson'.
		
		
	MODULE PUBLIC CLASSES:
	----------------------


		configuration.TheConfiguration										 [class]
				
			This is a singleton class; its constructor always returns
			the same instance, which represents the GLaDOS server
			configuration.
			
			
		configuration.TheAIPersonaConfig									 [class]
		
			Another singleton class; its instance represents the 
			configuration of the specific AI persona to be hosted.
			
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	#|==========================================================================
	#|
	#|	1. Module imports.								   [module code section]
	#|
	#|		Load and import names of (and/or names from) various
	#|		other python modules and pacakges for use from within
	#|		the present module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from os			import	getenv, path		# Access environment variables, build paths.
from hjson		import	load, OrderedDict 	# For loading data from .hjson files.
from pprint		import	pformat			  	# For pretty-printing structures for diagnostics.

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from 	infrastructure.decorators 	import singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from 	infrastructure.logmaster 	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))				# Our package name.
_logger = getComponentLogger(_component)						# Create the component logger.


			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	field.placement				import Placement
	# This is an enumerated type used for placing new application windows.

	#|==========================================================================
	#|	2. Globals										   [module code section]
	#|
	#|		Declare and/or define various global variables and constants.  
	#|		Top-level 'global' declarations are not strictly required, but 
	#|		they serve to verify that these names were not previously used, 
	#|		and also serve as documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|
		#|	2.1. Special globals.						[module code subsection]
		#|
		#|		These globals have special meanings defined by the
		#|		Python language.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__	# List of public symbols exported by this module.
__all__ = [
		'TheConfiguration',   	# Singleton class for the GLaDOS system configuration.
		'TheAIPersonaConfig',	# Singleton class for the AI persona config.
	]


		#|======================================================================
		#|		
		#|	2.2. Private globals.						[module code subsection]
		#|
		#|		These globals are not supposed to be accessed from 
		#|		outside of the present module.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|---------------------------------------------------------------------
	#| These are constants providing default values for module parameters.

global	_DEFAULT_CONFIG_FILENAME,	_DEFAULT_BASEDIR
global	_DEFAULT_AI_DATADIR,		_DEFAULT_AI_CONFIG_FILENAME
	
	# Default name of config file.
_DEFAULT_CONFIG_FILENAME		= 'glados-config.hjson'

	# What is the config filename relative to?
_DEFAULT_BASEDIR 				= '.'		# Look in current directory by default.

	# Default working directory for AI-specific state data.
_DEFAULT_AI_DATADIR 			= "ai-data"	   # Just use this if nothing else is provided.

	# Default filename for AI-specific configuration data.
_DEFAULT_AI_CONFIG_FILENAME 	= 'ai-config.hjson'		# Generally use this filename.

	#|---------------------------------------------------------------------
	#| These are variables providing current values for module parameters.
	#| NOTE: We really could/should make these into class variables instead.

global	_BASEDIR,		_CONFIG_FILENAME
global	_AI_DATADIR,	_AI_CONFIG_FILENAME

	# Filename of the config file.
_CONFIG_FILENAME = _DEFAULT_CONFIG_FILENAME 
	# Default to the default value before we've checked the environment.

	# Base directory for finding stuff.
_BASEDIR = _DEFAULT_BASEDIR					# Default before checking environment.

	# Pathname to the config file.
_CONFIG_PATHNAME = path.join(_BASEDIR, _CONFIG_FILENAME)
	# Default before checking environment.

	# Pathname to the AI-specific data directory.
_AI_DATADIR = path.join(_BASEDIR, _DEFAULT_AI_DATADIR)
	# Default before checking environment.

	# Filename of the AI-specific config file.
_AI_CONFIG_FILENAME = _DEFAULT_AI_CONFIG_FILENAME	
	# Default to the default value before we've checked the environment.

	# Pathname to the AI's config file.
_AI_CONFIG_PATHNAME = path.join(_AI_DATADIR, _AI_CONFIG_FILENAME)
	# Default before checking environment.


	#|==========================================================================
	#|
	#|	3. Classes.										   [module code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class TheConfiguration:		pass	# Forward declaration to ourself.
class TheAIPersonaConfig:	pass	# Forward declaration.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class TheConfiguration:	# The GLaDOS server configuration.
	"""
		TheConfiguration								[public singleton class]
		================
				
			This is a singleton class, meaning that it creates and manages 
			a single instance.	The TheConfiguration instance represents the
			configuration of the GLaDOS system.
				
			On its initial invocation, the constructor method automatically 
			loads the configuration from a file.  Subsequent invocations 
			do not, but the user has the option of calling the .reinit()
			method to manually reinitialize the configuration, with the 
			option of reloading the origial config file (in case it has
			changed), or loading a different file.
			
			We also dispatch the loading (or reloading) of the AI persona's
			configuration to the TheAIPersonaConfig singleton class, below.
			
		
		Public instance attributes:
		---------------------------
		
			The following are basic config parameters needed for
			finding other data, and are customized using environment
			variables.
		
				.baseDir [str] 			- Base directory for the GLaDOS system.
				
				.configFilename [str] 	- The name of the system config file 
											that was loaded.
				
				.configPathname [str] 	- The full pathname of the system 
											config file that was loaded.
				
			The following are detailed configuration parameters 
			that are specified in the config file itself.
				
				.appList [list] - List of more detailed configuration data
									for specific GLaDOS applications.
	"""
	
		#|======================================================================
		#| Private class constant data members. 				 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		# Note: The following hard-coded defaults, and their associated
		# configuration processing should probably be moved into a new module
		# apps.appSettings.

		# By default, do apps grab the command focus when they first pop up
		# their window?  (Not sure yet which default value makes more sense.)
	_DEFAULT_APP_AUTO_FOCUS = False		# True could also make sense here.

		# By default, do apps poke or wake up the A.I. when they update
		# their field display.  (Not sure yet which value makes more sense.)
	_DEFAULT_APP_LOUD_UPDATE = False	# True might also make sense here.

		# What is the default initial placement for app windows?
	_DEFAULT_APP_INITIAL_PLACEMENT = Placement.SLIDE_TO_BOTTOM
			# Initially, new application windows will by default open
			# up at the bottom of the receptive field (but above
			# pinned & anchored slots). They will not be anchored,
			# but will be free to scroll up.
	
	
		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	TheConfiguration._lastLoadedConf	     [private class data member]
		#|
		#|		This class-level attribute references the most recent 
		#|		*raw* configuration data structure to have been loaded.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# The last *raw* configuration data structure loaded.
	_lastLoadedConf = None			# No such structure has yet been loaded.


		#|======================================================================
		#| Special instance methods.							 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(theConfig:TheConfiguration, *args, **kwargs):
		"""
			TheConfiguration.__init__()			[singleton instance initializer]
			
				This instance initializer (which normally only gets called 
				once, because of our singleton wrapper) calls the .reinit() 
				method, which can also be called again manually by the 
				using module if it wishes to reinitialize the configuration.
		"""

		_logger.normal("    [Config] Loading system configuration...")

			# This does the real work of initializing the configuration.
		theConfig.reinit(*args, **kwargs)

			# Also invoke the initializer for TheAIPersonaConfig.
			# (Always checks its environment & reloads its config file.)
			
		_logger.normal("")
		TheAIPersonaConfig()
			
	#__/ End singleton instance initializer method theConfiguration.__init__().
		

		#|======================================================================
		#| Private instance methods.							 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def _checkEnvironment(theConfig:TheConfiguration):
		"""
			theConfig._checkEnvironment()	 [private singleton instance method]
			
				Checks environment variables to determine location of
				GLaDOS's system config file.
		"""
			
			# Declare these names as globals that we'll reinitialize here.
			# (It would really be cleaner to change these to class variables.)
			
		global _CONFIG_FILENAME, _BASEDIR, _CONFIG_PATHNAME

			# Go ahead and get the environment variables associated with
			# locating the main system config file.
			
		envFilename = getenv('GLADOS_CONFIG_FILENAME')
		envBaseDir	= getenv('GLADOS_PATH')
		envPathname = getenv('GLADOS_CONFIG_PATH')
		
			# Update the globals for the file name and base directory
			# if they were specified in the environment variables.
		
		if envFilename != None:	 _CONFIG_FILENAME = envFilename
		if envBaseDir  != None:	 _BASEDIR = envBaseDir
		
			# If the full pathname was not provided in an environment
			# variable, then calculate it from those globals.
		
		if envPathname is None:
		
			_logger.debug(f"Constructuring config path from '{_BASEDIR}'"
						  f" + '{_CONFIG_FILENAME}'... ")

			_CONFIG_PATHNAME = path.join(_BASEDIR, _CONFIG_FILENAME)
		
		else:	# Full pathname was provided in environment.
		
			_CONFIG_PATHNAME = envPathname
			
		#__/ End if envPathname==None ... else ...
			
	#__/ End private singleton instance method theConfiguration._checkEnvironment().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _loadConfig(theConfig:TheConfiguration):
		"""
			theConfig._loadConfig()			 [private singleton instance method]
			
				Loads the configuration file and returns it as a raw, 
				unprocessed data structure (made of dicts & arrays, 
				similar to what we'd get from json.load).  Also stashes 
				it in the private theConfig._lastLoadedConf attribute.
		"""
	
		_logger.normal("")
		_logger.normal(f"    [Config]   Loading server configuration from {_CONFIG_PATHNAME}...")

		try:
			with open(_CONFIG_PATHNAME) as cf:
				conf = load(cf)			# Load structure from hjson file.
		except:
			_logger.error(f"Couldn't load config file {_CONFIG_PATHNAME}.")
			return {}

		pconf = pformat(conf, indent=4, width=224)

		_logger.debug(f"        Loaded the following raw configuration structure:\n{pconf}")

		theConfig._lastLoadedConf = conf
		return conf

	#__/ End private singleton instance method theConfiguration._loadConfig().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _parseConf(theConfig:TheConfiguration, conf:dict = None):	   
		""" theConfig._parseConf()			 [private singleton instance method]
			
				Reads the given raw configuration data structure into 
				the configuration object."""

		# Don't even try to read a mind config from the sys config file currently.
		theConfig.mindConf = None
	 

		    #|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Extract the 'timezone' parameter, which specifies the offset 
			#| from UTC preferred by the operator for display of time values.
			#| If this is not provided, UTC (+0) will be assumed by default.

		if 'timezone' in conf:
			theConfig.timezone = timezone = conf['timezone']	# Expect a number of hours.
			_logger.normal(f"    [Config]      System config: The time zone offset from UTC is {timezone} hours.")
		else:
			_logger.warn("configuration._parseConf(): The 'timezone' parameter "
							"was not supplied. Defaulting to +0 (UTC).")
			theConfig.timezone = 0


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Extract the 'tab-width' parameter, which expresses the default
			#| number of characters that tab stops are located at a multiple of.
			#| If this is not provided, we default to 4.			

		if 'tab-width' in conf:
			theConfig.tabWidth = tabWidth = conf['tab-width']	# Expect an integer.
			_logger.normal(f"    [Config]      System config: The tab width is {tabWidth}.")
		else:
			_logger.warn("configuration._parseConf(): The 'tab-width' parameter "
							"was not provided. Defaulting to 4.")
			theConfig.tabWidth = 4


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| The has-box-chars config parameter is supposed to indicate whether
			#| the font selected on the text terminal has box-drawing characters.
			#| If it is not provided, we default to False. However, this parameter
			#| is not currently used in GLaDOS.

		if 'has-box-chars' in conf:
			theConfig.hasBoxChars = hasBoxChars = conf['has-box-chars']
			_logger.normal("    [Config]      System config: has-box-chars is " +
						   str(hasBoxChars) + '.')
		else:
			_logger.warn("configuration._parseConf(): The 'has-box-chars' parameter "
							"was not provided. Defaulting to False.")
			theConfig.hasBoxChars = False


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Extract the 'window-conf' parameter, which contains configuration
			#| parameters for the AI's text-based windowing system.

		if 'window-conf' in conf:
			theConfig.winConf = winConf = conf['window-conf']
		else:
			_logger.info("_parseConf(): The optional 'window-conf' parameter was "
							"not provided. Using hard-coded defaults.")
			winConf = dict()	# Empty dict by default.
	 
	 			#|--------------------------------------------------------------
				#| The 'side-decorators' sub-parameter is a boolean indicating
				#| whether the windowing system should display side-decorators
				#| (e.g. the '|' characters) along the left & right edges of
				#| the window. If it is not provided, we default to True.

		if 'side-decorators' in winConf:
			theConfig.sideDecorators = sideDec = winConf['side-decorators']
			_logger.normal(f"    [Config]      Window config: Use side decorators? = {sideDec}.")
		else:
			theConfig.sideDecorators = True


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Extract the 'field-conf' parameter, which contains configuration
			#| parameters for the receptive field facility.
	 
		if 'field-conf' in conf:
			theConfig.fieldConf = conf['field-conf']
		else:
			_logger.warn("_parseConf(): The required 'field-conf' parameter was "
							"not provided.")
	
			# NOTE: We should parse its parameters here.


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Extract the 'app-list' parameter, which contains a list of
			#| supported applications and their configuration parameters.
				
		if 'app-list' in conf:
			theConfig.appList = conf['app-list']
		else:
			_logger.warn("_parseConf(): The required 'app-list' parameter was "
							"not provided.")
			theConfig.appList = None

		
		# NOTE: It would be good to do some additional error-checking 
		# here, such as warning the user if there are other parameters 
		# included in the provided config file that we don't understand.
		
	#__/ End private singleton instance method theConfiguration._parseConf().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _process(theConfig:TheConfiguration):	
		""" 
			theConfig._process()			 [private singleton instance method]
			
				Given that the configuration has just been reinitialized
				but without much detailed processing of it yet, go ahead
				and do some routine processing of the provided config
				data to work it more deeply down into the system innards.
				
				In particular, we infer detailed application configuration
				information from the still-raw appList data structure.
		"""
	
			#|---------------------------------------------------------
			#| Process our raw .appList to form the .appConfigs dict of 
			#| app configurations.

		appConfigs = OrderedDict()		# Initially empty ordered dict.

		if theConfig.appList is not None:

			_logger.debug(f"About to process {len(theConfig.appList)} apps...")

			for appStruct in theConfig.appList:
				# Note that appList is an actual list, so the enumeration order
				# here is deterministic, and is the same as the order in the file.
		
				_logger.debug(f"About to process app struct: \n" + pformat(appStruct))

					#-----------------------------------------------
					# The 'name' parameter is the application name.
					# (Implicitly required to be present, but really 
					# we should do some error-checking here.)
		
				appName = appStruct['name']
				
					#--------------------------------------------------
					# Convert the 'available' parameter (also required)
					# to a proper Boolean value. (Need error check.)
			
				appAvail = appStruct['available']
				
					#---------------------------------------------------
					# Convert the 'auto-start' parameter (also required)
					# to a proper Boolean value.
					
				appAutoStart = appStruct['auto-start']
				
					#--------------------------------------------------
					# Convert the 'auto-open' parameter (also required)
					# to a proper Boolean value.
					
				appAutoOpen = appStruct['auto-open']
				
					#--------------------------------------------------
					# Our first optional parameter is 'auto-focus'.
					# Default value comes from a class-level constant.

				if 'auto-focus' in appStruct:
					appAutoFocus = appStruct['auto-focus']
				else:
					appAutoFocus = theConfig._DEFAULT_APP_AUTO_FOCUS

					#--------------------------------------------------
					# Our next optional parameter is 'quiet-update'.
					# Alternatively, user can supply 'loud-update'.
					# Default value comes from a class-level constant.

				if 'quiet-update' in appStruct:
					appQuietUpdate = appStruct['quiet-update']
					appLoudUpdate = not appQuietUpdate

				elif 'loud-update' in appStruct:
					appLoudUpdate = appStruct['loud-update']
					appQuietUpdate = not appLoudUpdate

				else:
					appLoudUpdate = theConfig._DEFAULT_APP_LOUD_UPDATE
					appQuietUpdate = not appLoudUpdate

					#------------------------------------------------------
					# If the 'placement' parameter is available, record it.
					# Otherwise, we use MOVE_TO_BOTTOM as the default 
					# initial placement for newly-started apps.
					
				if 'placement' in appStruct:
					# Really should do error checking here to make sure the
					# provided symbol is a valid Placement value.
					appInitPlacement = Placement(appStruct['placement'])
				else:
					appInitPlacement = theConfig._DEFAULT_APP_INITIAL_PLACEMENT
				
					# If the 'app-config' parameter is available, record it.
					# (We can't process it yet since it's application-specific
					# and the actual app objects haven't been created yet.)
						
				if 'app-config' in appStruct:
					appConfig = appStruct['app-config']
				else:
					appConfig = None
				
					# Construct an 'application attributes' dictionary.
					# This is what we'll actually end up handing to the app.
					# This should already have regularization of type values.
				
				appAttribs = {	
					'name':			appName,	# This one is not strictly necessary to include, but.
					'avail':		appAvail, 			# Is the app available to be registered?
					'auto-start':	appAutoStart,		# Should the application auto-start?
					'auto-open':	appAutoOpen,		# Should the application window auto-open?
					'auto-focus':	appAutoFocus,		# Should the app window grab the command focus?
					'loud-update':	appLoudUpdate,		# Should app window wake up AI when it updates?
					'placement':	appInitPlacement,
						# Where should we initially place the window on the field?
						# (Allowed values for this are specified in the field.placement.Placement class.)

					'conf':			appConfig	  		# App-specific configuration record.
				}
				
				_logger.debug(f"Setting attribs of '{appName}' app to:\n    " + 
								pformat(appAttribs, indent=4))

					# Set this dict as the value that appName maps to in 
					# the appConfigs dict.
				
				appConfigs[appName] = appAttribs
						
			#__/ End loop over structures in appList.			
		#__/ End if appList isn't None.
		
			# Store the appConfigs ordered dict as an instance data member.
		
		theConfig.appConfigs = appConfigs
	
	#__/ End private singleton instance method _theConfiguration.process().


		#|======================================================================
		#| Public instance methods.								 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	TheConfiguration().reinit()	  [public singleton instance method]
			#|
			#|		This public method gets automatically called once,	
			#|		by this class's singleton instance initializer, to
			#|		initialize the single instance of the Configuration 
			#|		class.	
			#|
			#|		It may also be invoked again explicitly by using 
			#|		modules whenever they wish to cause the system 
			#|		configuration to be reinitialized.
			#|
			#|		The configuration is only loaded from the filesystem 
			#|		if it hasn't been loaded yet, or if reloadConf==True.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	def reinit(theConfig:TheConfiguration, confStruct=None, 
				recheckEnv:bool=False, reloadConf:bool=False):
		"""
		(Re)initialization method for configurations.
		
			If confStruct (a raw configuration data structure) is provided,
			then it is used, and the reloadConf argument is ignored.
						
			If recheckEnv is True or the environment variables haven't been
			checked yet, environment variables are checked to potentially 
			reset the location of the current configuration file.
						
			If no configuration has been loaded yet or reloadConf is True,
			the configuration is (re-)loaded from the current configuration 
			file.  Otherwise, the last loaded configuration is just reused.
		"""
				
			#-------------------------------------------------------
			# First, if checkEnv is true, then we check the environment
			# variables to see if they are overriding any of our default
			# directory locations.
	
		if recheckEnv or not hasattr(theConfig, 'envChecked'):
			theConfig._checkEnvironment()
			theConfig.envChecked = True			 # Remember it's been checked.

			#---------------------------------------------------------
			# Let's remember the directory locations we ended up with,
			# in case needed for later reference.
			
		theConfig.baseDir			 = _BASEDIR
		theConfig.configFilename	 = _CONFIG_FILENAME
		theConfig.configPathname	 = _CONFIG_PATHNAME
		
			#-----------------------------------------------------------
			# Now let's figure out our raw configuration data structure.
			# Either it was provided to us in an argument, or we need to 
			# load it from the config file, or we already loaded it 
			# earlier and we're just going to reuse that one.
				
		if confStruct == None:	# No config struct provided; we have to load one.
						
				# Load (or possibly reload) the config file, 
				# or else use the last loaded copy.
						
			if reloadConf or theConfig._lastLoadedConf == None:
				confStruct = theConfig._loadConfig()
			else:
				confStruct = theConfig._lastLoadedConf
			
			#-------------------------------------------------------
			# OK, let's remember the raw structure we're using in case
			# needed for later reference (mainly for debugging).
			
		theConfig._rawConfStruct = confStruct
				
			#-------------------------------------------------------
			# 'Parse' the configuration data structure to initialize
			# our associated instance attributes.
	
		theConfig._parseConf(confStruct)
				
			#-------------------------------------------------------
			# Now process the configuration object (i.e., ourself) 
			# to do any other needed work with that information.
		
		theConfig._process()
		
	#__/ End TheConfiguration().reinit().

#__/ End class TheConfiguration.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class	TheAIPersonaConfig:
	"""
		TheAIPersonaConfig								[public singleton class]
		=================
				
			This is similar to the main Configuration class above, but it
			handles configuration information that is specific to the 
			individual artificially intelligent persona that is being 
			hosted within the GLaDOS system.
			
			NOTE: These two classes are so similar that it might make 
			sense to abstract out their commonalities into a common 
			abstract superclass, but we have not done this yet.
			
		
		Public instance attributes:
		~~~~~~~~~~~~~~~~~~~~~~~~~~~

			The following are basic config parameters needed for
			finding other data, and are customized using environment
			variables.
							
				.aiDataDir [str] 		- The base directory for finding any 
											AI-specific data.
				
				.aiConfigFilename [str]	- Filename of the AI-specific config 
											file.
											
				.aiConfigPathname [str]	- The full pathname of the AI-specific
											config file.

			The following are AI-specific config substructures that are
			read in from the config file and used to initialize the
			AI-specific configuration object.

				.fieldConf [dict]		- The configuration data for the
											AI's receptive field.

				.mindConf [dict]		- The configuration data for the
											AI persona's "mind."

				.apiConf [dict]			- The configuration data for the
											API to the underlying AI.

				.telegramConf [dict]	- The configuration data for the
											AI persona's Telegram bot.

			The following are the detailed configuration parameters 
			that are specified in the config file itself.


			Receptive field configuration parameters (under 'field-conf'):
			--------------------------------------------------------------

				.maxVisibleTokens [int] - Assumed size of the AI's receptive
											field in tokens.


			Mind configuration parameters (under 'mind-conf'):
			--------------------------------------------------

				.personaName [str]		- The name of the AI persona
											(E.g., "Gladys Eden").

				.personaID [str]		- A short identifier for the AI 
											persona. (E.g., "Gladys").

				.personaUsername [str]	- The username of the Unix account
											belonging to the AI persona.
											(E.g., "gladys").

				.modelFamily [string] 	- AI model type (e.g., 'gpt-2' or 
											'gpt-3').
				
				.modelVersion [string]	- AI model version (e.g., 'davinci').
				
				.minQueryTokens [int]	- Minimum number of tokens worth of
											space to reserve for the AI's 
											response to a single query.
											(Default value is 42.)

				.sysNotifyThresh [int]	- Threshold for system notifications
											that will be noticed by the AI.
											(Default is 0.)

				.exampleResponse [str]	- A sample response that will be
											shown to the AI persona when the
											system is first started up.


			GPT-3 API configuration parameters (under 'api-conf'):
			------------------------------------------------------

				.maxReturnedTokens [int] - Maximum number of tokens to return
											in one completion from the GPT-3 API.
				
				.temperature [float]	- Randomness temperature parameter for the 
											GPT-3 API. (Recommended value: 0.75.)
				
				.topP [float]			- Top-p parameter for the GPT-3 API.
											(Note: Not compatible with temperature.)
				
				.nCompletions [int]		- Number of completions to return from the
											GPT-3 API. (Default value is 1.)
				
				.doStream [bool]		- Whether or not to stream the GPT-3 API
											responses. (Default value is False.)
				
				.logProbs [int]			- If non-null, the GPT-3 API will return
											the log-probabilities of the top this
											many returned completions. (Default 
											value is null.)
				
				.doEcho [bool]			- If True, the GPT-3 API will echo back
											the prompt in the response. (Default
											value is False.)

				.stopSequences [list]	- A list of substrings that will be taken
											to indicate the end of GPT-3's response.
			
				.presencePenalty [float] - A penalty to apply to the log-probability
											of tokens previously occurring in the
											response. (Default value is 0.0.)
				
				.frequencyPenalty [float] - A penalty to apply to the log-probability
											of tokens based on their frequency of
											occurrence in the response. (Default
											value is 0.0.)

				.bestOf [int]			- The number of top-scoring completions to
											sample, server-side. (Default value is 1.)


			Telegram interface configuration parameters (under 'telegram-conf'):
			--------------------------------------------------------------------

				.botName [str]			- The name of the Telegram bot.
											(E.g., Gladys.)
				
				.startMsg [str]			- The message that will be sent to the
											user when the Telegram bot is first
											started up.

				.context [str]			- The persistent context data that the
											persona will see at the start of
											each conversation.

	"""
		
		#|======================================================================
		#| Special instance methods.							 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(theAIConfig:TheAIPersonaConfig, *args, **kwargs):
		#-----------------------------------------------------------------------	
		"""
			TheAIPersonaConfig.__init__()		[singleton instance initializer]
			
				This instance initializer (which normally only gets called 
				once, because of our singleton wrapper) calls the .reinit() 
				method, which can also be called again manually by the 
				using module if it wishes to reinitialize the configuration.
		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		_logger.normal("    [Config/AI] Loading AI persona configuration...")

		theAIConfig.reinit(*args, **kwargs)

	#__/ End singleton instance initializer method TheAIPersonaConfig.__init__().
		

		#|======================================================================
		#| Private instance methods.							 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	def _loadConfig(theAIConfig:TheAIPersonaConfig):
		#-----------------------------------------------------------------------
		"""
		theAIConfig._loadConfig()			 [private singleton instance method]
		
			Loads the AI's configuration file and returns it as a 
			raw, unprocessed data structure (made of dicts & arrays, 
			similar to what we'd get from json.load).  Also stashes 
			it in the private theAIConfig._lastLoadedConf attribute.
		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		aiConfigPath = theAIConfig.aiConfigPathname

		_logger.normal(f"    [Config/AI]   Loading AI configuration from {aiConfigPath}...")

		with open(_AI_CONFIG_PATHNAME) as cf:
			conf = load(cf)			# Load structure from hjson file.

		pconf = pformat(conf, indent=4, width=224)

		_logger.debug(f"        Loaded the following raw configuration structure:\n{pconf}")

		theAIConfig._lastLoadedConf = conf

		return conf

	#__/ End theAIConfig.loadConfig().


	def _parseConf(theAIConfig:TheAIPersonaConfig, conf:dict = None):			   
		#-----------------------------------------------------------------------
		"""
			theAIConfig._parseConf()		 [private singleton instance method]
			
				Reads the given raw configuration data structure into 
				the AI persona configuration object.
		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	 
				#|====================================
				#| Parse the field-conf substructure.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
			#------------------------------------
			# Extract the field-conf parameter.
		
		if 'field-conf' in conf:
			theAIConfig.fieldConf = fieldConf = conf['field-conf']
				# TODO: Make sure value given is valid.
			_logger.info(f"    [Config/AI]     AI config: The AI's field configuration is {fieldConf}.")
		else:
			_logger.warn("parseConf(): The required field-conf parameter "
							"was not provided.")
			theAIConfig.fieldConf = fieldConf = dict()	# Empty dict by default.

			#------------------------------------
			# Extract the max-visible-tokens parameter.
		
		if 'max-visible-tokens' in fieldConf:
			theAIConfig.maxVisibleTokens = maxTok = fieldConf['max-visible-tokens']
				# TODO: Make sure value given is valid.
			_logger.normal(f"    [Config/AI]     AI config: The AI's receptive field size is {maxTok}.")
		else:
			_logger.warn("parseConf(): The required max-visible-tokens parameter "
							"was not provided.")
			theAIConfig.maxVisibleTokens = None
		

				#|====================================
				#| Parse the mind-conf substructure.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
			#------------------------------------
			# Extract the mind-conf record.
		
		if 'mind-conf' in conf:
			theAIConfig.mindConf = mindConf = conf['mind-conf']
				# TODO: Make sure value given is valid.
			_logger.debug(f"    [Config/AI]     AI config: The AI's mind configuration is {mindConf}.")
		else:
			_logger.warn("parseConf(): The required mind-conf parameter "
							"was not provided.")
			theAIConfig.mindConf = mindConf = dict()	# Empty dict by default.


			#------------------------------------
			# Extract the persona-name parameter.
		
		if 'persona-name' in mindConf:
			theAIConfig.personaName = personaName = mindConf['persona-name']
				# TODO: Make sure value given is valid.
			_logger.normal(f"    [Config/AI]     AI config: The AI persona's name is {personaName}.")
		else:
			_logger.warn("parseConf(): The required persona-name parameter "
							"was not provided.")
			theAIConfig.personaName = None

	
			#------------------------------------
			# Extract the persona-id parameter.
		
		if 'persona-id' in mindConf:
			theAIConfig.personaID = personaID = mindConf['persona-id']
				# TODO: Make sure value given is valid.
			_logger.normal(f"    [Config/AI]     AI config: The AI persona's short ID is {personaID}.")
		else:
			_logger.warn("parseConf(): The required persona-id parameter "
							"was not provided.")
			theAIConfig.personaID = None

	
			#------------------------------------
			# Extract the persona-user-account parameter.
		
		if 'persona-user-account' in mindConf:
			theAIConfig.personaUsername = personaUsername = mindConf['persona-user-account']
				# TODO: Make sure value given is valid.
			_logger.normal(f"    [Config/AI]     AI config: The AI persona's user account is {personaUsername}.")
		else:
			_logger.warn("parseConf(): The required persona-user-account parameter "
							"was not provided.")
			theAIConfig.personaUsername = None

	
			#------------------------------------
			# Extract the model-family parameter.
		
		if 'model-family' in mindConf:
			theAIConfig.modelFamily = modelFamily = mindConf['model-family']
				# TODO: Make sure value given is valid.
			_logger.normal(f"    [Config/AI]     AI config: The AI's model family is {modelFamily}.")
		else:
			_logger.warn("parseConf(): The required model-family parameter "
							"was not provided.")
			theAIConfig.modelFamily = None

	
			#------------------------------------
			# Extract the model-version parameter.
	
		if 'model-version' in mindConf:
			theAIConfig.modelVersion = modelVersion = mindConf['model-version']
				# TODO: Make sure value given is valid.
			_logger.normal(f"    [Config/AI]     AI config: The AI's model version is {modelVersion}.")
		else:
			_logger.warn("parseConf(): The required model-version parameter "
							"was not provided.")
			theAIConfig.modelVersion = None


			#--------------------------------------------------
			# Extract the sys-notification-threshold parameter.

		if 'sys-notification-threshold' in mindConf:
			theAIConfig.sysNotifyThresh = sysNotifyThresh = mindConf['sys-notification-threshold']
				# TODO: Make sure value given is valid.
			_logger.normal("    [Config/AI]     AI config: The importance threshold for "
						   f"system notifications is {sysNotifyThresh}.")
		else:
			_logger.warn("parseConf(): The sys-notification-threshold parameter "
							"was not provided. Defaulting to 0.")
			theAIConfig.sysNotifyThresh = 0

			#--------------------------------------------------
			# Extract the min-query-tokens parameter.

		if 'min-query-tokens' in mindConf:
			theAIConfig.minQueryTokens = minQueryTokens = mindConf['min-query-tokens']
			_logger.normal("    [Config/AI]     AI config: The minimum size of "
						   f"the response region is {minQueryTokens}.")
		else:
			theAIConfig.minQueryTokens = 42		# Default

			#--------------------------------------------------
			# Extract the example-response parameter.

		if 'example-response' in mindConf:
			theAIConfig.exampleResponse = exampleResponse = mindConf['example-response']
			_logger.normal("    [Config/AI]     AI config: The example response "
						   f" is: [{exampleResponse}].")
		else:
			theAIConfig.exampleResponse = None	# Default

				#|====================================
				#| Parse the api-conf substructure.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
			#------------------------------------
			# Extract the mind-conf record.
		
		if 'api-conf' in conf:
			theAIConfig.apiConf = apiConf = conf['api-conf']
				# TODO: Make sure value given is valid.
			_logger.debug(f"    [Config/AI]     AI config: The AI's API configuration is {apiConf}.")
		else:
			_logger.warn("parseConf(): The required api-conf parameter "
							"was not provided.")
			theAIConfig.apiConf = apiConf = dict()	# Empty dict by default.

		# Go ahead and pull out the parameter values from the API conf record.

		if 'max-returned-tokens' in apiConf:
			theAIConfig.maxReturnedTokens = apiConf['max-returned-tokens']
		else:
			theAIConfig.maxReturnedTokens = None # No default value provided in config file.

		if 'temperature' in apiConf:
			theAIConfig.temperature = apiConf['temperature']
		else:
			theAIConfig.temperature = None	# No default value provided in config file.

		if 'top-p' in apiConf:
			theAIConfig.topP = apiConf['top-p']
		else:
			theAIConfig.topP = None	# No default value provided in config file.

		if 'n-completions' in apiConf:
			theAIConfig.nCompletions = apiConf['n-completions']
		else:
			theAIConfig.nCompletions = None	# No default value provided in config file.

		if 'do-stream' in apiConf:
			theAIConfig.doStream = apiConf['do-stream']
		else:
			theAIConfig.doStream = None	# No default value provided in config file.

		if 'log-probs' in apiConf:
			theAIConfig.logProbs = apiConf['log-probs']
		else:
			theAIConfig.logProbs = None	# No default value provided in config file.

		if 'do-echo' in apiConf:
			theAIConfig.doEcho = apiConf['do-echo']
		else:
			theAIConfig.doEcho = None	# No default value provided in config file.

		if 'stop-sequences' in apiConf:
			theAIConfig.stopSequences = apiConf['stop-sequences']
		else:
			theAIConfig.stopSequences = None	# No default value provided in config file.

		if 'presence-penalty' in apiConf:
			theAIConfig.presencePenalty = apiConf['presence-penalty']
		else:
			theAIConfig.presencePenalty = None	# No default value provided in config file.

		if 'frequency-penalty' in apiConf:
			theAIConfig.frequencyPenalty = apiConf['frequency-penalty']
		else:
			theAIConfig.frequencyPenalty = None	# No default value provided in config file.

		if 'best-of' in apiConf:
			theAIConfig.bestOf = apiConf['best-of']
		else:
			theAIConfig.bestOf = None	# No default value provided in config file.


				#|======================================
				#| Parse the telegram-conf substructure.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
			#------------------------------------
			# Extract the telegram-conf record.
		
		if 'telegram-conf' in conf:
			theAIConfig.telegramConf = telegramConf = conf['telegram-conf']
			_logger.debug(f"    [Config/AI]     AI config: The AI's Telegram configuration is {telegramConf}.")
		else:
			_logger.warn("parseConf(): The required telegram-conf parameter "
							"was not provided.")
			theAIConfig.telegramConf = telegramConf = dict()	# Empty dict by default.

		# Go ahead and pull out the parameter values from the API conf record.

		if 'bot-name' in telegramConf:
			theAIConfig.botName = botName = telegramConf['bot-name']
			_logger.normal(f"    [Config/AI]     AI config: The AI persona's Telegram bot name is {botName}.")
		else:
			theAIConfig.botName = None	# No default value provided in config file.

		if 'start-message' in telegramConf:
			theAIConfig.startMsg = startMessage = telegramConf['start-message']
			_logger.normal(f"    [Config/AI]     AI config: The AI persona's Telegram start message is {startMessage}.")
		else:
			theAIConfig.startMsg = None	# No default value provided in config file.

		if 'context' in telegramConf:
			context = telegramConf['context']
			# Make sure context string ends in a newline.
			if not context.endswith('\n'):
				context += '\n'
			theAIConfig.context = context
			_logger.normal(f"    [Config/AI]     AI config: The AI persona's Telegram context data is [{context.strip()}].")
		else:
			theAIConfig.context = None	# No default value provided in config file.


		#|**********************************************************************
		#| NOTE: It would be nice to do some additional error-checking 
		#| here, such as warning the user if there are other parameters 
		#| in the provided config file that we don't understand.
		#|**********************************************************************
		
		_logger.normal("    [Config/AI]     AI config: The AI configuration has been parsed.")
		return
	#__/ End private singleton instance method theAIConfig._parseConf().


	def _process(theAIConfig:TheAIPersonaConfig):
	
		""" 
			--------------------------------------------------------------------
			theAIConfig._process()			 [private singleton instance method]
			
				Given that the AI TheAIPersonaConfig has just been reinitialized
				but without much detailed processing of it yet, go ahead
				and do some routine processing of the provided config
				data to work it more deeply down into the system innards.
			--------------------------------------------------------------------
		"""
	
		# (No work needs to be done here yet.)
	
	#__/ End private singleton instance method theAIConfig._process().


	def _checkEnvironment(theAIConfig:TheAIPersonaConfig):

		"""
			--------------------------------------------------------------------
			theAIConfig._checkEnvironment()	 [private singleton instance method]
			
				Checks environment variables to determine locations of
				the AI persona's state data and its config file.
			--------------------------------------------------------------------	
		"""
			
			# Declare these names as globals that we'll reinitialize here.
			# (It would really be cleaner to change these to class variables.)
			
		global _AI_DATADIR, _AI_CONFIG_FILENAME, _AI_CONFIG_PATHNAME

			# Update the location of the AI's data directory, 
			# and the name of its config file, if they were 
			# provided in environment variables.
		
		envAIDataDir	= getenv("AI_DATADIR")
		envAIConfFile	= getenv("AI_CONFIG_FILENAME")
		
		if envAIDataDir 	!= None:	_AI_DATADIR 			= envAIDataDir
		if envAIConfFile	!= None:	_AI_CONFIG_FILENAME		= envAIConfFile
		
			# Compute the full pathname of the AI's config file.
		
		_AI_CONFIG_PATHNAME = path.join(_AI_DATADIR, _AI_CONFIG_FILENAME)

			# Print this key info at NORMAL level.
		
		_logger.normal(f"    [Config/AI]   The AI-specific data directory is set to {_AI_DATADIR}.")
		_logger.normal(f"    [Config/AI]   The AI-specific config file is set to {_AI_CONFIG_PATHNAME}.")
			
	#__/ End private singleton instance method theAIConfig._checkEnvironment().


		#|======================================================================
		#| Public instance methods.								 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def reinit(theAIConfig:TheAIPersonaConfig, confStruct=None, recheckEnv:bool=False, 
					reloadConf:bool=False):
		#-----------------------------------------------------------------------
		"""
		theAIConfig.reinit()						 [singleton instance method]
		
			(Re)initialization method for AI persona configurations.
			Environment variables are always checked & the config file 
			is always reloaded.		
		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#---------------------------------------------------------
			# First, we check the environment variables to see if they
			# are overriding any of our default directory locations.
	
		theAIConfig._checkEnvironment()
				
			#---------------------------------------------------------
			# Let's remember the directory locations we ended up with,
			# in case needed for later reference.
			
		theAIConfig.aiDataDir			= _AI_DATADIR
		theAIConfig.aiConfigFilename	= _AI_CONFIG_FILENAME
		theAIConfig.aiConfigPathname	= _AI_CONFIG_PATHNAME
		
			#-----------------------------------------------------
			# Now let's load our raw configuration data structure.
				
		try:
			confStruct = theAIConfig._loadConfig()
		except:
			_logger.error(f"Couldn't load AI config file {_AI_CONFIG_PATHNAME}.")
			return
			
			#---------------------------------------------------------
			# OK, let's remember the raw structure we're using in case
			# it's needed for later reference (mainly for debugging).
			
		theAIConfig._rawConfStruct = confStruct
				
			#-------------------------------------------------------
			# 'Parse' the configuration data structure to initialize
			# our associated instance attributes.

		theAIConfig._parseConf(confStruct)
				
			#-------------------------------------------------------
			# Now process the configuration object (i.e., ourself) 
			# to do any other needed work with that information.
		
		theAIConfig._process()
		
	#__/ End TheAIPersonaConfig().reinit().

#__/ End class TheAIPersonaConfig.
	

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					END OF FILE:	  config/configuration.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
