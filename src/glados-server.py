#!/usr/bin/python3
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|                      TOP OF FILE:    glados-server.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:      glados-server.py               [Python 3 application script]

    FULL PATH:      $GIT_ROOT/GLaDOS/src/glados-server.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)


	FILE DESCRIPTION:
	-----------------

		This script constitutes the main server process executable for the
		GLaDOS system.  Within the OS process running this script, threads 
		are created to carry out the following functions:

			1. Primary "mind" thread for the A.I. itself.

			2. Various GLaDOS processes, which may include 'bridge' 
				processes for communicating to external systems (e.g.,
				Internet-based services), or to local resources (e.g., 
				Unix command prompt), or to internal subsystems of
				the GLaDOS system itself, such as the memory system,
				the settings interface, & the book authoring system.

			3. A thread for managing the text-based 'windowing' system
				inside of GLaDOS, which is the primary 'GUI' seen by 
				the A.I.  (The windowing system itself is not a GLaDOS
				process; it is used by the A.I. to interact with GLaDOS
				processes.)

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


    #|--------------------------------------------------------------------------
    #|
    #|      RAW_DEBUG:bool                             [module global parameter]
    #|
    #|          Raw debugging flag.  This is a very low-level
    #|          feature, preliminary to any more sophisticated
    #|          error-logging capability.  Just check this flag
    #|          before doing low-level diagnostic output.  This
    #|          allows all such diagnostic output to be
    #|          suppressed easily.
    #|
    #|          Please note that this is the only global that
    #|          appears before the "Globals" code section, so
    #|          that we can begin using it right away.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global RAW_DEBUG	# Raw debugging flag.
RAW_DEBUG = False   # Change this to True as needed during initial development.

	# Get the name of the current file, for use in raw debug messages.

from os 	import path		# Manipulate filesystem path strings.

global FILENAME						# Filename of this module's file.
FILENAME = path.basename(__file__)	# Strip off ancestor directories.

    # Conditionally display some initial diagnostics if RAW_DEBUG is on...

if RAW_DEBUG:
    print(f"In {FILENAME}:  Turned on raw debugging...")

if __name__ == "__main__":
    if RAW_DEBUG:
        print(f"__main__: Loading {FILENAME}...")


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

if __name__ == "__main__":
    if RAW_DEBUG:
        print("__main__: Importing standard Python library modules...")

from    sys     import  stderr      # Used for error output to console.


        #|======================================================================
        #|  1.2. Imports of custom application modules. [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

if __name__ == "__main__": 
    if RAW_DEBUG:
        print("__main__: Importing custom application modules...", file=stderr)

			#|----------------------------------------------------------------
			#|  The following modules, although custom, are generic utilities,
			#|  not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.  (This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster import (
        appLogger,          # Top-level logger for the application.
        configLogMaster,    # Function to configure logmaster module.
        setComponent,       # Dynamically sets the current software component.
        setThreadRole,      # Dynamically sets the current thread's role.
        doInfo,             # Boolean: Whether to display info-level output.
        doNorm,             # Boolean: Whether to display normal output.
    )


    #|----------------------------------------------------------------
    #|  The following modules are specific to the present application.
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from appdefs                        import  systemName, appName
    # Name of the present application.  Used for configuring logmaster.

from config.configuration			import	Configuration
	# This singleton class manages loading of the GLaDOS system 
	# configuration from config files on system startup.

from supervisor.supervisor			import	Supervisor
	# This class manages startup of the Supervisor subsystem, which in
	# turn starts up and manages all of the other major subsystems.


    #|==========================================================================
    #|
    #|  2.  Global constants, variables, and objects.      [module code section]
    #|
    #|          Declare and/or define various global variables and
    #|          constants.  Top-level global declarations are not
    #|          strictly required, but they serve to verify that
    #|          these names were not previously used, and also
    #|          serve as documentation.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|
        #|  2.1.  Special globals.                      [module code subsection]
        #|
        #|          These globals have special meanings defined by the
        #|          Python language.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

            #-------------------------------------------------------------
            # NOTE: Defining __all__ is actually not necessary here, since
            # this script is not intended to be imported as a module.
            # However, if it were, then this might conceivably be useful.
            #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__		# List of public symbols exported by this module.
__all__ = [
        'is_top'    # Boolean; is this module running at top level?
    ]


        #|======================================================================
        #|
        #|   2.2.  Public module globals.               [module code subsection]
        #|
        #|      These are the globals specific to this module that we
        #|      encourage other modules to access and utilize.
        #|
        #|      The documentation for these should be included in the
        #|      module documentation string at the top of this file.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global  is_top      # Boolean; was this module first loaded at top level?


        #|======================================================================
        #|
        #|  2.3.  Private globals.                      [module code subsection]
        #|
        #|          In this section, we define global variables that
        #|          are used within this module, but that are not
        #|          exported nor intended to be used by other modules.
        #|
        #|          Since these are private, they aren't documented
        #|          in the module's documentation string.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    # The logmaster-based logger object that we'll use for logging
    # within this module.  Initialized in _main().
    
global  _logger     # Module logger.  (Here, same as application logger.)


    #|==========================================================================
    #|
    #|  3.  Module-level function definitions.             [module code section]
    #|
    #|          These functions are defined at top level within the
    #|          module; they are not part of any particular class.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|------------------------------------------------------------
        #|
        #|  _initLogging()                  [module private function]
        #|
        #|      This little private utility function just
        #|      initializes the logging system. It is called only
        #|      once per application run, near the start of _main().
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _initLogging():

    """Initializes the logging system.  Intended to be called only
       once per application run, near the start of _main()."""
    
    global _logger      # Allows us to set this module-global variable.
    
        #---------------------------------
        # Configure the logging facility.
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    if RAW_DEBUG:
        print("__main__._initLogging(): Configuring the 'logmaster' "
              "logging module...", file=stderr)

        # NOTE: To turn on log-file debug messages, uncomment the
        # first line below and comment out the second.
    
    #configLogMaster(logdebug = True, role = 'startup', component = appName)
    configLogMaster(role = 'startup', component = appName)
        #   \
        #   Configure the logger with default settings (NORMAL level
        #   messages and higher output to console, INFO and higher to
        #   log file), set this main thread's role to "startup", and
        #   set the thread component to "GLaDOS.server".

    _logger = appLogger  # Set module logger to our application logger.
    
#__/ End _initLogging().


        #|----------------------------------------------------------------------
        #|
        #|   _main()                                [module private function]
        #|
        #|      Main routine of this module.  It is private; we do not
        #|      export it, and other modules shouldn't attempt to call it.
        #|
        #|      The _main() routine is traditionally called within a
        #|      module's main body code, within the context of a
        #|      conditional like
        #|
        #|           if __name__ == "__main__":
        #|
        #|      so that it won't be automatically executed in cases when
        #|      this module is only being imported as a sub-module of a
        #|      larger software system.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _main():    

    f"""Main routine of the {FILENAME} script.  Called from within
        the script's main body code, if the script is run at top level
        as opposed to being imported as a module of a larger system."""
    
    if RAW_DEBUG:
        print("__main__._main(): Entered application's _main() routine...",
              file=stderr)

    _initLogging()      # Initializes/configures the logmaster module.

        #--------------------------------------------------------------
        # Application startup:  Display splash text.
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    if doInfo: _logger.info(f"{systemName} server application is starting up...")

    if doNorm:
        print() # Just visual whitespace; no need to log it.
        _logger.normal("Welcome to the {systemName} server, v0.1 (alpha).")
        _logger.normal("Copyright (C) 2020 Metaversal Constructions.")
        #_logger.normal("See the LICENSE.txt file for terms of use.")
        print()


            #=========================================================
            # Below follows the main code of the server application.
            #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	setThreadRole('startup')	# Denotes we are starting up the server.

	config = Configuration()	# Loads the system configuration.
	supervisor = Supervisor()	# Starts the supervisory subsystem.
		# NOTE: This also starts up all of the other major subsystems.
		
		#---------------------------------------------------------------------
		# By the time we get here, the Supervisor is up and running in a 
		# background thread, and all we need to do is wait for it to exit, at 
		# which point we can exit the whole server process.
		
	_logger.normal("Waiting for the Supervisor to exit...")
	setThreadRole('waiting')
	supervisor.waitForExit()	 # Waits for the Supervisor to exit.

		#------------------------------------------------------------
		# If we get here, then we are exiting the server application.

    setThreadRole('shutdown')   # Denotes we are shutting down.

    if doNorm:
        _logger.normal(f"{systemName} server application is shutting down...")

            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # End of main code of server application.
            #=========================================================
    
    if RAW_DEBUG:
        print("__main__._main(): Exiting from _main()...", file=stderr)

#__/ End function _main().


    #|==========================================================================
    #|
    #|   4.  Main script body.                             [script code section]
    #|
    #|          Above this section should only be definitions and
    #|          assignments.  Below is the main executable body of
    #|          the script.  It just calls the _main() function (if
    #|          this script is not just being loaded as a submodule).
    #|  
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

is_top = (__name__ == "__main__")
    # Remember this for benefit of stuff called from within _main().
    # In case this script gets loaded as a module, we also export this
    # global publicly in case other modules need to check whether
    # this module was initially loaded at top level or not.

        #-----------------------------------------------------
        # The below just calls the _main() routine (if we're
        # running as a top-level script), with some optional
        # diagnostics wrapped around it.
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
           
if is_top:
    
    if RAW_DEBUG:
        print("__main__:  Top-level script is invoking _main() "
              "routine of application...", file=stderr)
        
    _main()     # Call the private _main() function, defined above.
    
    if RAW_DEBUG:
        print("__main__:  Application's _main() routine has exited.",
              file=stderr)
        print("__main__:  Exiting top-level script...",
              file=stderr)
        
else:
    
    if RAW_DEBUG:
        print(f"Finished import of {FILENAME} as a module...")

#__/ End if is_top ... else ...


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                      END OF FILE:    glados-server.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%