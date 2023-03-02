#|==============================================================================
#|                      TOP OF FILE:    appdefs.py
#|------------------------------------------------------------------------------
#|
#|	FILE NAME:      appdefs.py                     [Python 3 module source code]
#|	==========================
#|
#|		FULL PATH:      $GIT_ROOT/GLaDOS/src/appdefs.py
#|		MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
#|
#|	FILE DESCRIPTION:
#|	=================
#|
#|		This file defines the appdefs module.  See the module docstring
#|		below for more details.
#|
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	MODULE NAME:	appdefs									   [Python 3 module]
	=======================
	
		IN PACKAGE:		(top level)

		SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
		APP NAME:       GLaDOS.server (GLaDOS server application)
        APP NAME:       TelegramBot (Gladys' Telegram Bot)
		SW COMPONENT:   GLaDOS.logging (GLaDOS logging framework)

		CODE LAYER:		0 (bottommost layer; no imports of custom modules)
	
	
    MODULE DESCRIPTION:
    -------------------

        This module gives Application-specific definitions for use 
		within the logging system.
        
        This module is imported by the logging system.

        To configure this module for a specific application, you must
        call the selectApp() function.  Note, this function MUST be called
        BEFORE the logmaster module is imported, because the logmaster
        module imports this module and obtains its application-specific
        settings from this module.

        This file defines some parameters specific to the present
        application.  It may be utilized from within general-purpose 
		modules to customize those modules for this particular 
		application.

        At present, we are only using this to define <systemName>,
		<appName>, and <topfile> parameters. The first two are used
        to compose names of system-specific and application-specific
        loggers.  Also, <topFile> is utilized in logger output.

        E.g., the logger for a module or component that is specific
        to the system (but not to the particular application program)
        would be called "<systemName>.<othername>", whereas the logger
        for a module specific to the present application would be
        called "<appName>.<othername>".  Further, <appName> itself
        should normally begin with "<systemName>."


    MODULE PUBLIC GLOBALS:
    ----------------------


        appdefs.systemName:str                  [global constant string]
        
                This string gives the name of the overall
                system that the present application is a
                part of.  Lexically it should be a standard
                identifier (alphanumeric string).
			
			
        appdefs.appName:str                     [global constant string]

                This string gives the name of the present
                application (as a component of the overall
                system).  It consists of the <systemName>
                followed by a "." and an identifier
                specifying this application (as distinct
                from other components of the system).
			
			
        appdefs.topFile:str                     [global constant string]
        
                This string gives the name of the top-level
                file of the present application, sans the .py
                extension.
    

    MODULE PUBLIC FUNCTIONS:
    ------------------------

        appdefs.selectApp(appName:str) -> None      [module public function]

                This function configures the application-specific
                settings appropriately for the named application.
                The top-level file of the application should call
                this function immediately after importing this
                module, and before importing the logmaster module.
				
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


    #|==========================================================================
    #|
    #|	1.	Globals					    				   [module code section]
    #|
    #|  	Declare and/or define various global variables and
    #|      constants.  Top-level global declarations are not
    #|      strictly required, but they serve to verify that
    #|      these names were not previously used, and also
    #|      serve as documentation.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


        #|======================================================================
        #|
        #|  Special globals.                                    [code section]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global  __all__         # List of public symbols exported by this module.

__all__ = [
            # Global constants.
		'systemName',    # Name of the system this application is part of.
		'appName',       # Name of the current application program.
		'topFile',       # The filename of the top-level file of this app.

            # Functions.
        'selectApp'      # Function to select the application.
    ]


        #|======================================================================
        #|
        #|  Module private globals.                             [code section]
        #|
        #|      These globals are not meant to be used by other modules.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    # This dictionary exists so that we can configure this module for the
    # correct application at run-time using the selectApp() function.
    # It is not meant to be used outside of this module.

_appDict = {

    'glados-server': {  # Main GLaDOS server application.

        'systemName':   'GLaDOS',               # The server application is part of the GLaDOS system.
        'appName':      'GLaDOS.server',        # We use the <system>.<component> naming scheme for the server app.
        'topFile':      'glados-server'         # Top-level file of this application is glados-server.py.

    },
    
    'telegram-bot': {   # Gladys' Telegram bot application.

        'systemName':   'GLaDOS',               # The Telegram bot application uses some GLaDOS-specific features.
        'appName':      'TelegramBot',          # However, it's conceptually a separate application from the GLaDOS system.
        'topFile':      'telegram-bot'   # Top-level file of this application is gladys-telegram-bot.py.

    }
}


        #|======================================================================
        #|
        #|  Module public globals.                              [code section]
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

global systemName, appName, topFile
    # Note this declaration doesn't really do anything at top level.

        #|----------------------------------------------------------------------
        #|
        #|      appdefs.systemName:str              [global constant string]
        #|
        #|          This string gives the name of the overall
        #|          system that the present application is a
        #|          part of.  Lexically it should be a standard
        #|          identifier (alphanumeric string).
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Commenting this out because we now configure the application after the initial import.
#systemName  =   "GLaDOS"       # This code is part of the "GLaDOS" system.

systemName   =   None           # Not yet initialized. (Initialized by selectApp()).


        #|----------------------------------------------------------------------
        #|
        #|      appdefs.appName:str                 [global constant string]
        #|
        #|          This string gives the name of the present
        #|          application (as a component of the overall
        #|          sytem).  It normally consists of the
        #|          <systemName> followed by a "." and an 
        #|          identifier specifying this application (as 
        #|          distinct from other components of the system).
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Commenting this out because we now configure the application after the initial import.
#appName     =   systemName + ".server"
    #-This application program is the (main, central) component
    # of the system. NOTE: This should be overridden by other apps.

appName      =   None           # Not yet initialized. (Initialized by selectApp()).


        #|----------------------------------------------------------------------
        #|
        #|      appdefs.topFile:str                 [global constant string]
        #|
        #|          This string gives the name of the top-level
        #|          file of the present application, sans the .py
        #|          extension.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Commenting this out because we now configure the application after the initial import.
#topFile 	= 	'glados-server'    # Note that the .py is implicit here.
    # Note that this should be overridden by other apps.

topFile     =   None           # Not yet initialized. (Initialized by selectApp()).


    #|==========================================================================
    #|
    #|  2.  Function definitions.                            [code section]
    #|
    #|      These functions are defined in this module.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def selectApp(appID:str) -> None:
    """
        Select the application to be used.

            This function is used to select the application to be used.
            It is called by the main program after importing appdefs
            to select the application to be used.  It is not meant to 
            be used by other modules.  Note it should be called prior
            to importing any other module that imports appdefs.

        Parameters:

            appID:str

                Identifier for the application to be selected.  It
                should be a standard identifier (alphanumeric string).
                Currently supported applications are:

                    glados-server   - Main GLaDOS server application.

                    telegram-bot    - Gladys' Telegram bot application.

        Returns:
            None
    """

    global systemName, appName, topFile

    # Check that the application name is valid.
    if appID not in _appDict:
        raise ValueError("Invalid application name: " + appID)

    # Set the system name.
    systemName = _appDict[appID]['systemName']

    # Set the application name.
    appName = _appDict[appID]['appName']

    # Set the top-level file name.
    topFile = _appDict[appID]['topFile']

    # Return. (Technically, this statement is not needed, but it
    # makes the code more readable.)

    return      # This function has no return value.

#__/ End of function selectApp().


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                      END OF FILE:   appdefs.py
#|=============================================================================
