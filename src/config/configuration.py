#|==============================================================================
#|                   TOP OF FILE:    config/configuration.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""

	FILE NAME:		config/configuration.py			[Python module source file]
	
    IN PACKAGE:		config
	MODULE NAME:    config.configuration
    FULL PATH:      $GIT_ROOT/GLaDOS/src/config/configuration.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
    SW COMPONENT:   GLaDOS.server.config (server configuration component)


	MODULE DESCRIPTION:
	-------------------
	
		This module allows loading of the GLaDOS system configuration from a 
		config file.  The default name of the config file is
		
			'glados-config.hjson'
			
		It is expected by default to reside in the directory from which the 
		server process was launched. The file format is HJSON, which is a more 
		human-readable extension of JSON format; see https://hjson.github.io/.
		
		The config file to use can be customized somewhat by setting environment 
		variables. If the environment variable GLADOS_CONFIG_FILENAME is set, 
		then it is used instead of the default config filename.  If the 
		environment variable GLADOS_PATH is set, then it (rather than the 
		current directory) is used as the location in which to look for the 
		config file. If the environment variable GLADOS_CONFIG_PATH is set, then 
		it is used instead of any of the above.  


	USAGE:
	------
		
		from config.configuration import Configuration
		...
		config = Configuration()		# Construct singleton instance.
		...
	

	ENVIRONMENT VARIABLES:
	----------------------
	
		GLADOS_CONFIG_FILENAME
		
			If the environment variable GLADOS_CONFIG_FILENAME is set, then 
			it is used instead of the default config filename.  Otherwise,
			the default filename 'glados-config.hjson' is used.
	
	
		GLADOS_PATH
			
			If the environment variable GLADOS_PATH is set, then it (rather 
			than the current directory) is used as the location in which to 
			look for the config file.
		
		
		GLADOS_CONFIG_PATH
			
			If the environment variable GLADOS_CONFIG_PATH is set, then it
			is used as the full path to the config file, instead of using 
			any of the above.  
		
		
		AI_DATA
		
			The environment variable AI_DATA should be set to point to the
			data directory in which all data specific to a given AI persona
			is stored; for example, '/opt/AIs/gladys'.  
			
			Ideally, each AI should be given its own user account on the 
			host, and GLaDOS should be run from within that account, so that 
			the files in the data directory can be made writable only by the
			AI itself.
		
	
	
    MODULE PUBLIC CLASSES:
    ----------------------


		configuration.Configuration									[class]
		
			This is a singleton class; its constructor always returns
			the same instance, which represents the GLaDOS server
			configuration.

																			"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------

	#|==========================================================================
	#|	Imports.												[code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from os		import	getenv, path  # Access environment variables, build paths.
from hjson	import	load		  # For loading data from .hjson files.
from pprint	import	pformat		  # For pretty-printing structures for diagnostics.

	#----------------------------------------
	# Create/access a logger for this module.

from logmaster import getComponentLogger

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)    			# Create the component logger.


    #|==========================================================================
    #|
    #|   Globals					    						[code section]
    #|
    #|      Declare and/or define various global variables and
    #|      constants.  Top-level global declarations are not
    #|      strictly required, but they serve to verify that
    #|      these names were not previously used, and also
    #|      serve as documentation.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|
        #|  Special globals.                              	[code subsection]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__		# List of public symbols exported by this module.
__all__ = [
	'Configuration',	# Singleton class for the GLaDOS system configuration.
    ]


		#|======================================================================
		#|	
		#|	Private globals.									[code section]
		#|
		#|		These globals are not supposed to be accessed from 
		#|		outside of the present module.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|---------------------------------------------------------------------
	#| These are constants providing default values for module parameters.

global 	_DEFAULT_CONFIG_FILENAME, _DEFAULT_BASEDIR, _DEFAULT_AI_DATADIR
		
	# Default name of config file.
_DEFAULT_CONFIG_FILENAME = 'glados-config.hjson'

	# What is the config filename relative to?
_DEFAULT_BASEDIR = '.'		# Look in current directory by default.

	# Default working directory for AI-specific state data.
_DEFAULT_AI_DATADIR = "ai-data"		# Just use this if nothing else is provided.


	#|---------------------------------------------------------------------
	#| These are variables providing current values for module parameters.
	#| NOTE: We could make these class variables in Configuration instead.

global	_CONFIG_FILENAME, _BASEDIR, _CONFIG_FILENAME, _AI_DATADIR

	# Filename of the config file.
_CONFIG_FILENAME = _DEFAULT_CONFIG_FILENAME		# Default before checking environment.

	# Base directory for finding stuff.
_BASEDIR = _DEFAULT_BASEDIR		# Default before checking environment.

	# Pathname to the config file.
_CONFIG_PATHNAME = path.join(BASEDIR, CONFIG_FILENAME)
	# Default before checking environment.

	# Pathname to the AI-specific data directory.
_AI_DATADIR = path.join(BASEDIR, _DEFAULT_AI_DATADIR)
	# Default before checking environment.


	#|==========================================================================
	#|
	#|	Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Configuration:	# The GLaDOS server configuration.

	"""
		Configuration									[public singleton class]
		=============
		
			This is a singleton class, meaning that it creates and manages 
			a single instance.  The Configuration instance represents the
			configuration of the GLaDOS system.
		
			On its initial invocation, the constructor method automatically 
			loads the configuration from a file.  Subsequent invocations 
			have the option of reloading the configuration (in case it has
			changed).
			
			
		Public instance attributes:
		---------------------------
			
			.baseDir [string] - Base directory for GLaDOS system.
			.configFilename [string] - The name of the system config file that was loaded.
			.configPathname [string] - The full pathname of the system config file that was loaded.
			
			.aiDataDir [string] - The base directory for finding AI-specifi data.
			
			.modelFamily [string] - AI model type (e.g., 'gpt-2' or 'gpt-3').
			.modelVersion [string] - AI model version (e.g., 'davinci').

	"""
	
		#|----------------------------------------------------------------------
		#|	Configuration._configuration			[private class data member]
		#|
		#|		This class-level attribute references the unique instance of
		#|		this class that exists in the system.  It is initialized the
		#|		first time the class's constructor is called.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	_configuration = None		# Instance not yet created at module load time.


		#|----------------------------------------------------------------------
		#|	Configuration._lastLoadedConf			[private class data member]
		#|
		#|		This class-level attribute references the most recent 
		#|		*raw* configuration data structure to have been loaded.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# The last *raw* configuration data structure loaded.
	_lastLoadedConf = None		# No such structure has yet been loaded.


		#|----------------------------------------------------------------------
		#|	Configuration.__new__()						[special class method]
		#|
		#|		This special method is called to create new instances of
		#|		the class.  The design pattern used here is what makes
		#|		Configuration a singleton class; that is, it only creates
		#|		one instance.  Subsequent calls return the same instance.
		#|
		#|		At some point, we should abstract out this singleton 
		#|		functionality as a metaclass, but that is lower priority.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __new__(thisClass, *args, **kwargs):
		if thisClass._configuration is None:
			inst = super(Configuration, thisClass).__new__(thisClass)
			thisClass._configuration = inst
		else:
			inst = thisClass._configuration
		return inst

	
		#|----------------------------------------------------------------------
		#|	.__init__()						[singleton instance (re)initializer]
		#|
		#|		This private method is called to initialize (or re-
		#|		initialize) the single instance of the Configuration
		#|		class.  The configuration is only loaded from the 
		#|		filesystem if it hasn't been loaded yet, or if the
		#|		reloadConf flag is True.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def __init__(inst, confStruct=None, recheckEnv:bool=False, reloadConf:bool=False):
	
		"""Constructor method for configurations.  
			
			If confStruct (a raw configuration data structure) is provided,
			then it is used, and the reloadConf argument is ignored.
			
			If recheckEnv is True or the environment variables haven't been
			checked yet, environment variables are checked to potentially 
			reset the location of the current configuration file.
			
			If no configuration has been loaded yet or reloadConf is True,
			the configuration is (re-)loaded from the current configuration 
			file.  Otherwise, the last loaded configuration is reused.
		"""
		
			#-------------------------------------------------------
			# First, if checkEnv is true, then we check the environment
			# variables to see if they are overriding any of our default
			# directory locations.
		
		if checkEnv or not inst.hasattr('envChecked'):
			inst.checkEnvironment()
			inst.envChecked = True		# Remember it's been checked.

			#---------------------------------------------------------
			# Let's remember the directory locations we ended up with,
			# in case needed for later reference.
			
		inst.baseDir 			= _BASEDIR
		inst.configFilename 	= _CONFIG_FILENAME
		inst.configPathname 	= _CONFIG_PATHNAME
		inst.aiDataDir			= _AI_DATADIR
		
			#-----------------------------------------------------------
			# Now let's figure out our raw configuration data structure.
			# Either it was provided to us in a constructor argument,
			# or we need to load it from the config file, or we already
			# loaded it earlier and we're just going to reuse that one.
		
		if confStruct == None:		# No config struct provided; we have to load one.
			
				# Load (or possibly reload) the config file, 
				# or else use the last loaded copy.
			
			if reloadConf or _lastLoadedConf == None:
				confStruct = inst.loadConfig()
			else:
				confStruct = Configuration._lastLoadedConf
		
			#-------------------------------------------------------
			# OK, let's remember the raw structure we're using in case
			# needed for later reference (mainly for debugging).
			
		inst._rawConfStruct = confStruct
		
			#-------------------------------------------------------
			# 'Parse' the configuration data structure to initialize
			# our associated instance attributes.
		
		inst.parseConf(confStruct)
		
			#-------------------------------------------------------
			# Now process the configuration (ourself) to do any other
			# needed work with that information.
			
		inst.process()
	
	#__/ End Configuration().


	def parseConf(inst, conf:dict = None):
	
		"""Reads the given configuration data structure into this configuration object."""
	
			# Extract the model-family attribute.
	
		if conf.hasattr('model-family'):
			inst.modelFamily = conf['model-family']
			# TODO: Make sure value given is valid.
		else:
			_logger.warn("parseConf(): The required model-family attribute was not provided.")
			inst.modelFamily = None
		
			# Extract the model-version attribute.
		
		if conf.hasattr('model-version'):
			inst.modelVersion = conf['model-version']
			# TODO: Make sure value given is valid.
		else:
			_logger.warn("parseConf(): The required model-version attribute was not provided.")
			inst.modelVersion = None

			# Extract the app-list attribute.
			
		if conf.hasattr('app-list'):
			inst.appList = conf['app-list']
			# TODO: Process app-list structure
		else:
			_logger.warn("parseConf(): The required app-list attribute was not provided.")
			inst.appList = None
	
		# NOTE: It would be nice to do some additional error-checking here, such as
		# warning the user if there are other attributes in the provided config file
		# that we don't understand.
	
	#__/ End parseConf().


	def process(inst):
	
			# Process the app-list to form the .appConfigs dict of app configurations.
	
		appConfigs = {}	# Empty dict.
	
		for appStruct in inst.appList:
		
				# The 'name' attribute is the application name.
				# (Implicitly required to be present, but really 
				# we should do some error-checking here.)
		
			appName = appStruct['name']
			
				# Convert the 'available' attribute (also required)
				# to a proper Boolean value.
			
			appAvail = True if appStruct['available'] == 'true' else False
			
				# Convert the 'auto-start' attribute (also required)
				# to a proper Boolean value.
				
			appAutoStart = True if appStruct['auto-start'] == 'true' else False
			
				# If the 'app-config' attribute is available, record it.
				# (We can't process it yet since it's application-specific
				# and the actual app objects haven't been created yet.)
				
			if 'app-config' in appStruct:
				appConfig = appStruct['app-config']
			else:
				appConfig = None
			
				# Construct an 'application attributes' dictionary.
			
			appAttribs =
				{ 	'name':		appName,		# This is not strictly necessary to include, but.
					'avail':	appAvail,		# Is the app available to be registered?
					'auto':		appAutoStart,	# Should the application auto-start?
					'conf':		appConfig		# Application-specific configuration info.
				}
			
				# Set this dict as the value that appName maps to in 
				# the appConfigs dict.
			
			appConfigs[appName] = appAttribs
				
		#__/ End loop over appList. 
		
			# Store the availApps set as an instance data member.
		
		inst.appConfigs = appConfigs
	
	#__/ End instance method Configuration.process().


	def checkEnvironment(inst):
	
		"""
			Checks environment variables to determine locations of
			GLaDOS system config file and AI-specific state data.
		"""
		
			# Declare these names as globals that we'll reinitialize.
		global _CONFIG_FILENAME, _BASEDIR, _CONFIG_PATHNAME, _AI_DATADIR
	
		envFilename = os.getenv('GLADOS_CONFIG_FILENAME')
		envBaseDir  = os.getenv('GLADOS_PATH')
		envPathname = os.getenv('GLADOS_CONFIG_PATH')
		
		if envFilename != None:	 _CONFIG_FILENAME = envFilename
		if envBaseDir  != None:  _BASEDIR = envBaseDir
		
		CONFIG_PATHNAME = path.join(envFilename, envBaseDir)
		
		if envPathname != None:  _CONFIG_PATHNAME = envPathname
		
		envAIDataDir = os.getenv("AI_DATADIR")
		if envAIDataDir != None:	_AI_DATADIR = envAIDataDir
		
		_logger.normal(f"The AI-specific data directory is set to {_AI_DATADIR}.")
		
	#__/ End ConfigurationLoader.checkEnvironment().


	def loadConfig(inst):

		"""Loads the configuration file and returns it as a raw, unprocessed
			data structure (made of dicts & arrays, like from json.load).
			Also stashes it in the private inst._lastLoadedConf attribute."""
	
		_logger.normal(f"Loading server configuration from {CONFIG_PATHNAME}...")
	
		with open(CONFIG_PATHNAME) as cf:
			conf = load(cf)		# Load structure from hjson file.

		pconf = pformat(conf, indent=4)

		_logger.info(f"Loaded the following raw configuration structure:\n{pconf}")

		Configuration._lastLoadedConf = pconf

		return pconf

	#__/ End loadConfig().


#__/ End class ConfigurationLoader.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                     END OF FILE:   config/loader.py
#|=============================================================================