#|==============================================================================
#|                   TOP OF FILE:    config/configuration.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""

    FILE NAME:      config/configuration.py          [Python module source file]
        
    IN PACKAGE:     config
    MODULE NAME:    config.configuration
    FULL PATH:      $GIT_ROOT/GLaDOS/src/config/configuration.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
    SW COMPONENT:   GLaDOS.server.config (server configuration component)


    MODULE DESCRIPTION:
    ===================
        
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
        config = Configuration()                # Construct singleton instance.
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


        configuration.Configuration                                      [class]
                
            This is a singleton class; its constructor always returns
            the same instance, which represents the GLaDOS server
            configuration.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------

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

from os         import  getenv, path  	# Access environment variables, build paths.
from hjson      import  load              # For loading data from .hjson files.
from pprint		import  pformat           # For pretty-printing structures for diagnostics.

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from infrastructure.decorators import singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger      # Software component name, logger for component.

_component = path.basename(path.dirname(__file__))              # Our package name.
_logger = getComponentLogger(_component)                        # Create the component logger.


    #|==========================================================================
	#| 	2. Globals                                         [module code section]
    #|
    #|      Declare and/or define various global variables and constants.  
	#|		Top-level 'global' declarations are not strictly required, but 
	#|		they serve to verify that these names were not previously used, 
	#|		and also serve as documentation.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|
        #|	2.1. Special globals.                       [module code subsection]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__	# List of public symbols exported by this module.
__all__ = [
        'Configuration',   # Singleton class for the GLaDOS system configuration.
    ]


        #|======================================================================
        #|      
        #|	2.2. Private globals.                       [module code subsection]
        #|
        #|		These globals are not supposed to be accessed from 
        #|      outside of the present module.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|---------------------------------------------------------------------
    #| These are constants providing default values for module parameters.

global  _DEFAULT_CONFIG_FILENAME, _DEFAULT_BASEDIR, _DEFAULT_AI_DATADIR
    
    # Default name of config file.
_DEFAULT_CONFIG_FILENAME = 'glados-config.hjson'

    # What is the config filename relative to?
_DEFAULT_BASEDIR = '.'		# Look in current directory by default.

    # Default working directory for AI-specific state data.
_DEFAULT_AI_DATADIR = "ai-data"    # Just use this if nothing else is provided.


    #|---------------------------------------------------------------------
    #| These are variables providing current values for module parameters.
    #| NOTE: We could make these class variables in Configuration instead.

global  _CONFIG_FILENAME, _BASEDIR, _CONFIG_FILENAME, _AI_DATADIR

    # Filename of the config file.
_CONFIG_FILENAME = _DEFAULT_CONFIG_FILENAME # Default before checking environment.

    # Base directory for finding stuff.
_BASEDIR = _DEFAULT_BASEDIR             	# Default before checking environment.

    # Pathname to the config file.
_CONFIG_PATHNAME = path.join(_BASEDIR, _CONFIG_FILENAME)
    # Default before checking environment.

    # Pathname to the AI-specific data directory.
_AI_DATADIR = path.join(_BASEDIR, _DEFAULT_AI_DATADIR)
    # Default before checking environment.


    #|==========================================================================
    #|
    #|	3. Classes.                                        [module code section]
    #|
    #|		Classes defined by this module.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

@singleton
class Configuration:    # The GLaDOS server configuration.

    """
        Configuration                                   [public singleton class]
        =============
                
            This is a singleton class, meaning that it creates and manages 
            a single instance.  The Configuration instance represents the
            configuration of the GLaDOS system.
                
            On its initial invocation, the constructor method automatically 
            loads the configuration from a file.  Subsequent invocations 
			do not, but the user has the option of calling the .reinit()
			method to manually reinitialize the configuration, with the 
			option of reloading the origial config file (in case it has
			changed), or loading a different file.
            
        
        Public instance attributes:
        ---------------------------
        
			The following are basic config parameters needed for
			finding other data, and are customized using environment
			variables.
		
				.baseDir [string] - Base directory for the GLaDOS system.
				
				.configFilename [string] - The name of the system config file 
											that was loaded.
				
				.configPathname [string] - The full pathname of the system 
											config file that was loaded.
							
				.aiDataDir [string] - The base directory for finding any 
										AI-specific data.
				
			The following are detailed configuration parameters 
			that are specified in the config file itself.
				
				.modelFamily [string] - AI model type (e.g., 'gpt-2' or 
											'gpt-3').
				
				.modelVersion [string] - AI model version (e.g., 'davinci').
				
				.maxVisibleTokens [int] - Assumed size of the AI's receptive
											field in tokens.
				
				.appList [list] - List of more detailed configuration data
									for specific GLaDOS applications.
    """
        
		#|----------------------------------------------------------------------
		#|	Configuration._lastLoadedConf       	 [private class data member]
		#|
        #|  	This class-level attribute references the most recent 
        #|      *raw* configuration data structure to have been loaded.
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        # The last *raw* configuration data structure loaded.
    _lastLoadedConf = None          # No such structure has yet been loaded.


		#|======================================================================
		#| Special instance methods. 							 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __init__(theConfig, *args, **kwargs):
	
		"""
			Configuration.__init__()			[singleton instance initializer]
			
				This instance initializer (which normally only gets called 
				once, because of our singleton wrapper) calls the .reinit() 
				method, which can also be called again manually by the 
				using module if it wishes to reinitialize the configuration.
		"""

        _logger.info("Loading system configuration...")

        theConfig.reinit(*args, **kwargs)
			
	#__/ End singleton instance initializer method Configuration.__init__().
        

		#|======================================================================
		#| Private instance methods. 							 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


    def _parseConf(theConfig, conf:dict = None):
       
        """
			theConfig._parseConf()			 [private singleton instance method]
			
				Reads the given raw configuration data structure into 
				the configuration object.
		"""
     
		
			#------------------------------------
			# Extract the model-family parameter.
        
        if 'model-family' in conf:
            theConfig.modelFamily = conf['model-family']
                # TODO: Make sure value given is valid.
		else:
			_logger.warn("parseConf(): The required model-family parameter "
							"was not provided.")
			theConfig.modelFamily = None
	
	
			#------------------------------------
			# Extract the model-version parameter.
	
		if 'model-version' in conf:
			theConfig.modelVersion = conf['model-version']
				# TODO: Make sure value given is valid.
		else:
			_logger.warn("parseConf(): The required model-version parameter "
							"was not provided.")
			theConfig.modelVersion = None


			#------------------------------------
			# Extract the max-visible-tokens parameter.
		
		if 'max-visible-tokens' in conf:
			theConfig.maxVisibleTokens = conf['max-visible-tokens']
				# TODO: Make sure value given is valid.
		else:
			_logger.warn("parseConf(): The required max-visible-tokens parameter "
							"was not provided.")
			theConfig.maxVisibleTokens = None


			#------------------------------------
			# Extract the app-list parameter.
				
		if 'app-list' in conf:
			theConfig.appList = conf['app-list']
				# TODO: Process app-list structure
		else:
			_logger.warn("parseConf(): The required app-list parameter was "
							"not provided.")
			theConfig.appList = None

        
		# NOTE: It would be nice to do some additional error-checking 
		# here, such as warning the user if there are other parameters 
		# in the provided config file that we don't understand.
        
	#__/ End parseConf().


	def _process(theConfig:Configuration):
	
		""" 
			--------------------------------------------------------------------
			theConfig._process()			 [private singleton instance method]
			
				Given that the configuration has just been reinitialized
				but without much detailed processing of it yet, go ahead
				and do some routine processing of the provided config
				data to work it more deeply down into the system innards.
				
				In particular, we infer detailed application configuration
				information from the still-raw appList data structure.
			--------------------------------------------------------------------
		"""
	
			#---------------------------------------------------------
			# Process our raw .appList to form the .appConfigs dict of 
			# app configurations.

		appConfigs = {} 	# Initially empty dict.

		if theConfig.appList is not None:

			_logger.debug(f"About to process {len(theConfig.appList)} apps...")

			for appStruct in theConfig.appList:
		
				_logger.debug(f"About to process app struct: \n" + pformat(appStruct))

					# The 'name' parameter is the application name.
					# (Implicitly required to be present, but really 
					# we should do some error-checking here.)
		
				appName = appStruct['name']
				
					# Convert the 'available' parameter (also required)
					# to a proper Boolean value.
			
				appAvail = appStruct['available']
				
					# Convert the 'auto-start' parameter (also required)
					# to a proper Boolean value.
					
				appAutoStart = appStruct['auto-start']
				
					# If the 'app-config' parameter is available, record it.
					# (We can't process it yet since it's application-specific
					# and the actual app objects haven't been created yet.)
						
				if 'app-config' in appStruct:
					appConfig = appStruct['app-config']
				else:
					appConfig = None
				
					# Construct an 'application attributes' dictionary.
					# This is what we'll actually end up handing to the app.
				
				appAttribs = {  
					'name':		appName,  # Not strictly necessary to include, but.
					'avail':    appAvail, # Is the app available to be registered?
					'auto':     appAutoStart, # Should the application auto-start?
					'conf':     appConfig     # App-specific configuration info.
				}
				
				_logger.debug(f"Setting attribs of '{appName}' app to:\n" + 
								pformat(appAttribs, indent=4))

					# Set this dict as the value that appName maps to in 
					# the appConfigs dict.
				
				appConfigs[appName] = appAttribs
						
			#__/ End loop over structures in appList. 			
		#__/ End if appList isn't None.
		
			# Store the appConfigs dict as an instance data member.
		
		theConfig.appConfigs = appConfigs
	
	#__/ End instance method Configuration.process().


	def _checkEnvironment(theConfig):

		"""
			--------------------------------------------------------------------
			theConfig._checkEnvironment()	 [private singleton instance method]
			
				Checks environment variables to determine locations of
				GLaDOS's system config file and AI-specific state data.
			--------------------------------------------------------------------	
		"""
			
			# Declare these names as globals that we'll reinitialize here.
			# (It would really be cleaner to change these to class variables.)
			
		global _CONFIG_FILENAME, _BASEDIR, _CONFIG_PATHNAME, _AI_DATADIR

			# Go ahead and get the environment variables associated with
			# locating the main system config file.
			
		envFilename = getenv('GLADOS_CONFIG_FILENAME')
		envBaseDir  = getenv('GLADOS_PATH')
		envPathname = getenv('GLADOS_CONFIG_PATH')
		
			# Update the globals for the file name and base directory
			# if they were specified in the environment variables.
		
		if envFilename != None:  _CONFIG_FILENAME = envFilename
		if envBaseDir  != None:  _BASEDIR = envBaseDir
		
			# If the full pathname was not provided in an environment
			# variable, then calculate it from those globals.
		
		if envPathname is None:
		
			_logger.debug(f"Constructuring config path from '{_BASEDIR}'"
						  f" + '{_CONFIG_FILENAME}'... ")

			_CONFIG_PATHNAME = path.join(_BASEDIR, _CONFIG_FILENAME)
		
		else:	# Pathname was provided in environment.
		
			_CONFIG_PATHNAME = envPathname
		#__/ 
		
			# Update the location of the AI's data directory, 
			# if that was provided in an environment variable.
		
		envAIDataDir = getenv("AI_DATADIR")
		if envAIDataDir != None:	_AI_DATADIR = envAIDataDir
		
		_logger.normal(f"The AI-specific data directory is set to {_AI_DATADIR}.")
			
	#__/ End ConfigurationLoader.checkEnvironment().


	def _loadConfig(theConfig):

		"""
			--------------------------------------------------------------------
			theConfig._loadConfig()			 [private singleton instance method]
			
				Loads the configuration file and returns it as a raw, 
				unprocessed data structure (made of dicts & arrays, 
				similar to what we'd get from json.load).  Also stashes 
				it in the private theConfig._lastLoadedConf attribute.
			--------------------------------------------------------------------
		"""
	
		_logger.normal(f"Loading server configuration from {_CONFIG_PATHNAME}...")

		with open(_CONFIG_PATHNAME) as cf:
			conf = load(cf)         # Load structure from hjson file.

		pconf = pformat(conf, indent=4, width=224)

		_logger.info(f"Loaded the following raw configuration structure:\n{pconf}")

		theConfig._lastLoadedConf = conf

		return conf

	#__/ End loadConfig().


		#|======================================================================
		#| Public instance methods. 							 [class section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|  Configuration().reinit()  	  [public singleton instance method]
			#|
			#|  	This public method gets automatically called once,  
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
        
    def reinit(theConfig, confStruct=None, recheckEnv:bool=False, 
				reloadConf:bool=False):
        
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
			theConfig.envChecked = True          # Remember it's been checked.

			#---------------------------------------------------------
			# Let's remember the directory locations we ended up with,
			# in case needed for later reference.
			
		theConfig.baseDir            = _BASEDIR
		theConfig.configFilename     = _CONFIG_FILENAME
		theConfig.configPathname     = _CONFIG_PATHNAME
		theConfig.aiDataDir          = _AI_DATADIR
		
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
        
    #__/ End Configuration().reinit().

#__/ End class Configuration.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                     END OF FILE:   config/loader.py
#|=============================================================================
