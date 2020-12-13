#|==============================================================================
#|                      TOP OF FILE:    config/loader.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""

	FILE NAME:		config/loader.py				[Python module source file]
	
    IN PACKAGE:		config
	MODULE NAME:    config.loader
    FULL PATH:      $GIT_ROOT/GLaDOS/src/config/loader.py
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
		
		from config.loader import ConfigurationLoader
		...
		ConfigurationLoader()
	

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
	
	
	MODULE PUBLIC GLOBALS:
	----------------------
	
		loader.serverConfiguration							[constant object]
		
			The serverConfiguration object is an instance of the
			Configuration class that holds the current configuration
			of the GLaDOS server.  It is loaded by ConfigurationLoader.
	
	
    MODULE PUBLIC CLASSES:
    ----------------------


		loader.Configuration										[class]
		
			An instance of this class represents a particular GLaDOS 
			server configuration.


		loader.ConfigurationLoader									[class]
		
			The constructor for this class automatically loads the
			configuration file from the filesystem into the 
			serverConfiguration global (module attribute).

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

global  __all__         # List of public symbols exported by this module.
__all__ = [
	'Configuration',		  # Class for configuration objects.
    'serverConfiguration',    # Current configuration object for the server.
    'ConfigurationLoader',    # Loads the server configuration from a file.
    ]


		#|======================================================================
		#|	
		#|	Private globals.									[code section]
		#|
		#|		These globals are not supposed to be accessed from 
		#|		outside of the present module.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
global _DEFAULT_CONFIG_FILENAME		# Default name of config file.
_DEFAULT_CONFIG_FILENAME = 'glados-config.hjson'

global _DEFAULT_BASEDIR		# What is the config filename relative to?
_DEFAULT_BASEDIR = '.'		# Look in current directory by default.

global _lastLoadedConf		# The last raw configuration data structure loaded.
_lastLoadedConf = None		# No such structure has yet been loaded.


        #|======================================================================
        #|
        #|  Public globals.                              		[code section]
        #|
        #|      These globals are specific to the present module
        #|      and exported publicly to other modules that use it.
        #|
		#|      User modules should do "from appdefs import *"
		#|      to get immediate copies of these globals.
		#|
		#|      If users wish to modify these globals, they must also
		#|      do "import appdefs" and then "appdefs.<global> = ..."
		#|      (Warning: This will not affect the values of these
		#|      globals seen by other modules that have already
		#|      imported this module!)
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global serverConfiguration		# Current Configuration of GLaDOS server.
serverConfiguration = None		# Not loaded yet at import time.

global CONFIG_FILENAME			# Filename of the config file.
CONFIG_FILENAME = _DEFAULT_CONFIG_FILENAME		# Default before checking environment.

global BASEDIR					# Base directory for finding stuff.
BASEDIR = _DEFAULT_BASEDIR

global CONFIG_PATHNAME			# Pathname to the config file.
CONFIG_PATHNAME = path.join(BASEDIR, CONFIG_FILENAME)
	# Default before checking environment.


	#|==========================================================================
	#|
	#|	Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


class ConfigurationLoader: pass		# Forward declaration.

class Configuration:	# A GLaDOS server configuration.

	"""
		Configuration													[class]
		=============
		
			An instance of this class contains a particular configuration
			of a GLaDOS server.  The constructor method automatically loads
			the configuration from a file.
			
		Public instance attributes:
		---------------------------
			
			.modelFamily [string] - Model type (e.g., 'gpt-2' or 'gpt-3').
			.modelVersion [string] - Model version (e.g., 'davinci').

	"""
	
	def __init__(self, confStruct=None, checkEnv:bool=True, reloadConf:bool=True):
	
		"""Constructor method for configurations.  
			
			If confStruct (a raw configuration data structure) is provided,
			then it is used, and the reloadConf argument is ignored.
			
			If checkEnv is True, environment variables are checked
			to reset the location of the current configuration file.
			
			If reloadConf is True, the configuration is re-loaded from
			the current configuration file.  Otherwise, the last loaded 
			configuration is reused.
		"""
		
		if checkEnv:
			ConfigurationLoader.checkEnvironment()
		
		if confStruct == None:		# No config struct provided; we have to load one.
			
				# Reload the config file, or else use the last loaded copy.
			
			if reloadConf:
				confStruct = ConfigurationLoader.loadConfig()
			else:
				confStruct = _lastLoadedConf
		
			#-------------------------------------------------------
			# 'Parse' the configuration data structure to initialize
			# our instance attributes.
		
		self.parseConf(conf)
		
			# Process the configuration (ourself) to do any other
			# needed work with that information.
			
		self.process()
	
	#__/ End Configuration().

	def parseConf(self, conf:dict = None):
	
		"""Reads the given configuration data structure into this configuration object."""
	
			# Extract the model-family attribute.
	
		if conf.hasattr('model-family'):
			self.modelFamily = conf['model-family']
			# TODO: Make sure value given is valid.
		else:
			_logger.warn("parseConf(): The required model-family attribute was not provided.")
			self.modelFamily = None
		
			# Extract the model-version attribute.
		
		if conf.hasattr('model-version'):
			self.modelVersion = conf['model-version']
			# TODO: Make sure value given is valid.
		else:
			_logger.warn("parseConf(): The required model-version attribute was not provided.")
			self.modelVersion = None

			# Extract the app-list attribute.
			
		if conf.hasattr('app-list'):
			self.appList = conf['app-list']
			# TODO: Process app-list structure
		else:
			_logger.warn("parseConf(): The required app-list attribute was not provided.")
			self.appList = None
	
		# NOTE: It would be nice to do some additional error-checking here, such as
		# warning the user if there are other attributes in the provided config file
		# that we don't understand.
	
	#__/ End parseConf().

	def process(self):
	
			# Process the app-list to form the .appConfigs dict of app configurations.
	
		appConfigs = {}	# Empty dict.
	
		for appStruct in self.appList:
		
				# The 'name' attribute is the application name.
		
			appName = appStruct.name
			
				# Convert the 'available' attribute to a proper Boolean value.
			
			appAvail = True if appStruct.available == 'true' else False
			
				# Construct an 'application attributes' dictionary.
			
			appAttribs =
				{ 	'name':		appName,		# This is not strictly necessary to include, but
					'avail':	appAvail	}
			
				# Set this dict as the value that appName maps to.
			
			appConfigs[appName] = appAttribs
				
		#__/ End loop over appList. 
		
			# Store the availApps set as an instance data member.
		
		self.appConfigs = appConfigs
	
	#__/ End instance method Configuration.process().

#__/ End class Configuration.


class ConfigurationLoader:		# Class for help with loading configurations.

	"""This class collects functions used for loading configurations from
		the filesystem."""

	def __init__(self):
	
		"""This 'constructor' is not really a constructor because instances
			of this class are empty.  Really, it just initializes the module."""
		
			# Set the module global serverConfiguration to the result of
			# calling the Configuration constructor, which automatically
			# loads the configuration (using other methods of this class).
			
		serverConfiguration = Configuration()

	#__/ End ConfigurationLoader().

	def checkEnvironment():
	
		"""Checks environment variables to determine config file location."""
	
		envFilename = os.getenv('GLADOS_CONFIG_FILENAME')
		envBaseDir  = os.getenv('GLADOS_PATH')
		envPathname = os.getenv('GLADOS_CONFIG_PATH')
		
		if envFilename != None:	 CONFIG_FILENAME = envFilename
		if envBaseDir  != None:  BASEDIR = envBaseDir
		
		CONFIG_PATHNAME = path.join(envFilename, envBaseDir)
		
		if envPathname != None:  CONFIG_PATHNAME = envPathname
		
	#__/ End ConfigurationLoader.checkEnvironment().


	def loadConfig():

		"""Loads the configuration file and returns it as a raw, unprocessed
			data structure (made of dicts & arrays, like from json.load).
			Also stashes it in the private loader._lastLoadedConf attribute."""
	
		_logger.normal(f"Loading server configuration from {CONFIG_PATHNAME}...")
	
		with open(CONFIG_PATHNAME) as cf:
			conf = load(cf)		# Load structure from hjson file.

		pconf = pformat(conf, indent=4)

		_logger.info(f"Loaded the following raw configuration structure:\n{pconf}")

		_lastLoadedConf = pconf

		return pconf

	#__/ End loadConfig().


#__/ End class ConfigurationLoader.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                     END OF FILE:   config/loader.py
#|=============================================================================