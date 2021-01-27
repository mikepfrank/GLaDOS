#!/usr/bin/python3
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|						TOP OF FILE:	glados-server.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		glados-server.py			   [Python 3 application script]

	FULL PATH:		$GIT_ROOT/GLaDOS/src/glados-server.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)


		FILE DESCRIPTION:
		-----------------

				This script constitutes the main server process executable for the
				GLaDOS system.	Within the OS process running this script, threads 
				are created to carry out the following functions (at least):

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
								process per se; it is used by the A.I. to interact 
								*with* GLaDOS processes.)

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


	#|--------------------------------------------------------------------------
	#|
	#|	0. Debugging flags								[module code section]
	#|	==================
	#|
	#|		These flags are defined at the top of the module so that we
	#|		can find and modify them quickly and easily during development.
	#|		All other globals are defined later, in section 2.
	#|
	#|
	#|	RAW_DEBUG:bool								[module global parameter]
	#|	--------------
	#|
	#|			Raw debugging flag for the current module.	This is 
	#|			a very low-level feature, preliminary to any more 
	#|			sophisticated diagnostic-logging capability.  The 
	#|			module code can check this flag before doing any 
	#|			low-level diagnostic output.  This then allows all 
	#|			such diagnostic output in this module to be easily 
	#|			suppressed changing this flag to False.
	#|
	#|
	#|	CONS_DEBUG:bool								[module global parameter]
	#|	---------------
	#|
	#|			If this is True, then all debug-level output sent 
	#|			to the infrastructure.logmaster module will also be
	#|			displayed on the console.  This applies throughout 
	#|			the server application (not just in this module).
	#|
	#|
	#|	LOG_DEBUG:bool							   [module global parameter]
	#|	--------------
	#|
	#|			If this is True, then debug-level output sent to
	#|			the infrastructure.logmaster module will be recorded
	#|			in the system log file, '../log/GLaDOS.server.log'.
	#|			Note this applies throughout the server application,
	#|			not just in the current module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global RAW_DEBUG	# Raw debugging flag--controls low-level debug output for this module.
RAW_DEBUG = False	# Change this to True as needed during initial development.

	# The following control logging level thresholds in the logmaster module.

global CONS_DEBUG, LOG_DEBUG	# These control debug-level output to console & log file.
CONS_DEBUG = False	# Tell logmaster: Don't diplay debug-level output on console.
LOG_DEBUG = True	# Tell logmaster: Do save debug-level output to log file.

global CONS_INFO	# These control info-level output to console.
CONS_INFO = False	# Tell logmaster: Don't diplay info-level output on console.


# Before doing anything else, we start a virtual terminal and have it grab
# control of the stdout/stderr output streams, so that any early output 
# that is generated will be remembered for display within the paneled
# console environment after that is started up.

from console.virterm import VirTerm
global _virTerm
_virTerm = VirTerm()
_virTerm.grab_stdio(tee=True)
	# Grabs stdout/stderr streams (redirecting them here), but also
	# replicating the writes on the original streams as well.

if RAW_DEBUG:
	print("Virtual terminal grabbed stdout/stderr output streams.")


		#|----------------------------------------------------------------------
		#| Here we do a little bit more preliminary work, prior to starting the 
		#| main program. Namely, we (conditionally) display some raw diagnostics 
		#| to note that we are starting to load the main program.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# First, get the name of the current file, for use in raw debug messages.

from os import path					# This lets us manipulate filesystem path strings.
global FILENAME						# Filename of this module's file.
FILENAME = path.basename(__file__)	# Strip off all ancestor directories.

	# Conditionally display some initial diagnostics (if RAW_DEBUG is on)...

if RAW_DEBUG:
	print(f"In {FILENAME}:	Turned on raw debugging...")

if __name__ == "__main__":		# True if top-level script (not an imported module).
	if RAW_DEBUG:
		print(f"__main__: Loading {FILENAME}...")


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

if __name__ == "__main__":
	if RAW_DEBUG:
		print("__main__: Importing standard Python library modules...")

from	time				import	sleep		# Gives other threads time to work.
from	sys					import	stderr		# Used for error output to console.
from	collections.abc		import	Iterable	# Used for type hints in declarations.

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

if __name__ == "__main__": 
	if RAW_DEBUG:
		print("__main__: Importing custom application modules...", file=stderr)

						#|----------------------------------------------------------------
						#|	The following modules, although custom, are generic utilities,
						#|	not specific to the present application.
						#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

								#-------------------------------------------------------------
								# The logmaster module defines our logging framework; we
								# import specific definitions we need from it.	(This is a
								# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster import (
		sysName,			# Name of this system, 'GLaDOS'.
		appLogger,			# Top-level logger for the application.
		configLogMaster,	# Function to configure logmaster module.
		setComponent,		# Dynamically sets the current software component.
		setThreadRole,		# Dynamically sets the current thread's role.
		doDebug,			# Boolean: Whether to display debug-level output.
		doInfo,				# Boolean: Whether to display info-level output.
		doNorm,				# Boolean: Whether to display normal output.
		testLogging,		# Function to test logging facility.
		updateStderr,		# Function to update what stderr is used.
		initLogMaster,
	)

# Reinitialize logmaster using virterm
#initLogMaster(out = _virTerm.out, err = _virTerm.err)


	#|----------------------------------------------------------------
	#|	The following modules are specific to the present application.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from 	appdefs						import	systemName, appName
	# Name of the present application.	Used for configuring logmaster.

from	settings.settings			import	TheSettingsFacility
	# This facility is for keeping track of all the available settings.

from 	config.configuration		import	TheConfiguration
	# This singleton class will manage loading of the GLaDOS system 
	# configuration from config files on system startup.

from	console.console				import	ConsoleClient
	# The "console client" starts up and manages the main GLaDOS system
	# console screen for benefit of human system operators.  This is a
	# a curses-based display screen consisting of a number of text user 
	# interface (TUI) panels.  Although most of the core elements of 
	# GLaDOS are associated with displays on the receptive field, which
	# can be seen by the AI and also by human system operators, additional 
	# system debugging information not visible to the AI may appear here.

from 	supervisor.supervisor		import	TheSupervisor
	# This singleton class will manage startup of the Supervisor 
	# subsystem, which in turn starts up and manages all of the other 
	# major subsystems of GLaDOS.


	#|==========================================================================
	#|
	#|	2.	Global constants, variables, and objects.	   [module code section]
	#|
	#|			Declare and/or define various global variables and
	#|			constants.	Top-level 'global' declarations are not
	#|			strictly required, but they serve to verify that
	#|			these names were not previously used, and also
	#|			serve as documentation of our intent.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|
		#|	2.1.  Special globals.						[module code subsection]
		#|
		#|			These globals have special meanings defined by the
		#|			Python language.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#-------------------------------------------------------------
			# NOTE: Defining __all__ is actually not necessary here, since
			# this script is not intended to be imported as a module.
			# However, if it were, then this might conceivably be useful.
			#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__		# List of public symbols 'exported' by this module.
__all__ = [
		'is_top'	# Boolean global; is this module running at top level?
	]


		#|======================================================================
		#|
		#|	 2.2.  Public module globals.				[module code subsection]
		#|
		#|		These are the globals specific to this module that we
		#|		encourage other modules to access and utilize.
		#|
		#|		The documentation for these should be included in the
		#|		module documentation string at the top of this file.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	is_top		# Boolean; was this module first loaded at top level?


		#|======================================================================
		#|
		#|	2.3.  Private globals.						[module code subsection]
		#|
		#|			In this section, we define global variables that
		#|			are used within this module, but that are not
		#|			exported nor intended to be used by other modules.
		#|
		#|			Since these are private, they aren't documented
		#|			in the module's documentation string.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# The logmaster-based logger object that we'll use for logging
	# within this module.  Initialized in _main().
	
global	_logger		# Module logger.  (Here, same as application logger.)


	#|==========================================================================
	#|
	#|	3.	Module-level function definitions.			   [module code section]
	#|
	#|			These functions are defined at top level within the
	#|			module; they are not part of any particular class.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|------------------------------------------------------------
		#|
		#|	_initLogging()					[module private function]
		#|
		#|		This little private utility function just
		#|		initializes the logging system. It is called only
		#|		once per application run, near the start of _main().
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _initLogging():

	"""Initializes the logging system.	Intended to be called only
	   once per application run, near the start of _main()."""
	
	global _logger		# Allows us to set this module-global variable.
	
		#---------------------------------
		# Configure the logging facility.
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	if RAW_DEBUG:
		print("__main__._initLogging(): Configuring the 'logmaster' "
			  "logging module...", file=stderr)

		# NOTE: CONS_DEBUG and LOG_DEBUG are defined at the top of this file.
	configLogMaster(consdebug = CONS_DEBUG,
					consinfo = CONS_INFO,
					logdebug = LOG_DEBUG,
					role = 'startup',
					component = appName)
		#	\
		#	Configures the logger with default settings (NORMAL level
		#	messages and higher output to console, INFO and higher to
		#	log file), set this main thread's role to "startup", and
		#	set the thread component to "GLaDOS.server".  You can 
		#	alternatively turn on CONS_DEBUG and/or LOG_DEBUG at the
		#	top of this file to also get lower-level output messages.
	updateStderr()	# Make sure logmaster notices we're using a nonstandard stderr.

	# This is a test of different styles of log output.
	#testLogging()

	_logger = appLogger	 # Sets this module's logger to be our application logger.
	
#__/ End _initLogging().


		#|----------------------------------------------------------------------
		#|
		#|	 _main()								[module private function]
		#|
		#|		Main routine of this module.  It is private; we do not
		#|		export it, and other modules shouldn't attempt to call it.
		#|
		#|		The _main() routine is traditionally called within a
		#|		module's main body code, within the context of a
		#|		conditional like
		#|
		#|			 if __name__ == "__main__":
		#|
		#|		so that it won't get automatically executed in cases when
		#|		this module is only being imported as a sub-module of a
		#|		larger software system for some reason.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _main():	

	f"""Main routine of the {FILENAME} script.	Called from within
		the script's main body code, if the script is run at top level
		as opposed to being imported as a module of a larger system."""
	
	if RAW_DEBUG:
		print("__main__._main(): Entered application's _main() routine...",
			  file=stderr)


		#|----------------------------------------------------------------------
		#| 1. Initialize the logging system. We do this extremely early since
		#|		basically the entire system needs to be able to use it.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	_initLogging()		# Initializes/configures the logmaster module.


		#|----------------------------------------------------------------------
		#| 2. Application startup:	Display splash text.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	if doInfo: 
		_logger.info(f"[Main] {systemName} server application is starting up...")

	if doNorm:
		print() # Just visual whitespace; no need to log it.
		_logger.normal(f"Welcome to the {systemName} server, v0.0 (pre-alpha).")
		_logger.normal("Copyright (C) 2020-21 Metaversal Constructions.")
		#_logger.normal("See the LICENSE.txt file for terms of use.")
			# Commented out because this file doesn't exist yet.
		print() # Just visual whitespace; no need to log it.


		#|======================================================================
		#| 3. Now follows the main code of the server application.  The first
		#|		phase of it is initializing a few pieces of key, fundamental
		#|		infrastructure that will be need to be used by various major
		#|		subsystems as they are starting up.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	setThreadRole('init')
		# This will denote, in log records, that we are now initializing the server.

	if doNorm:
		_logger.normal("[Main] (1) Initializing config/settings infrastructure...")
		print() # Just visual whitespace; no need to log it.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| The first packages that we initialize are the configuration and 
			#| settings packages, because they are needed to provide parameter
			#| values to all of the other major packages.

	if doInfo:
		_logger.info("  [Main/Init] Initializing system configuration and settings facility...")

	config   = TheConfiguration()		# Loads the system configuration.
	settings = TheSettingsFacility()	# Initializes the settings facility.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Next, we initialize the Help system, because many of the
			#| remaining subsystems may want to install help modules when
			#| they initialize themselves, so, we want the help facility to
			#| already be ready before they start initializing themselves.
			#| (Note that if the settings facility wants to install a help
			#| module, we'll have to do this later, because the help facility
			#| may need to access the settings facility as well.)

	if doInfo:
		_logger.info("  [Main/Init] Initializing help system...")

	helpSys = TheHelpSystem()	# Creates & initializes the help system.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Next, before starting up the "real meat" of the core system
			#| components, we start up our TUI-based "console" display, so that
			#| the operator can use it to monitor our progress.  "TUI" means
			#| "Text User Interface," and it is more specifically an interface
			#| based on the curses library for interfacing with Unix-style text
			#| terminals.  This is organized into a "display" object which
			#| provides low-level display management, and a "client" object that
			#| gives the application-specific functionality.  In particular, the
			#| console client organizes the display into panels showing various
			#| information that would be of interest to a human operator looking
			#| at the GLaDOS system console.  It also provides for human input
			#| (for commands, talking to the AI, etc.)
	
	if doNorm:
		print() # Just visual whitespace; no need to log it.
		_logger.normal("[Main] (2) Launching console display...")

	#if doInfo:
	#	_logger.info("[Main/Init] Booting up console display...")

	if doDebug:
		_logger.debug("glados-server.py:_main(): Creating console client...")
		
	console = ConsoleClient(_virTerm)
		# Initializes the system console client functionality.

	if doDebug:
		_logger.debug("glados-server.py:_main(): Starting console client...")

	console.startup(waitForExit=False)
		# Rather than waiting here for the console to exit, we start it
		# running in a background thread, while in the meantime we
		# continue setting up the rest of the system.

	# However, we do pause here briefly to give the console time to finish starting up
	# before we proceed.
	sleep(1)	# It should just take a second.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Next, we initialize and start up the Supervisor.  This is one of
			#| the most important subsystems of GLaDOS, in that it is
			#| responsible for starting up and coordinating all of the other
			#| major subsystems.

	if doNorm:
		_logger.normal("") # At this point we can't print to stdout or we'll mess up curses.
		_logger.normal("[Main] (3) Initializing system supervisor...")
		_logger.normal("")

	#if doInfo:
	#	_logger.info("[Main/Init] Initializing system Supervisor...")

	supervisor = TheSupervisor(console)		# Creates the main supervisory subsystem.
			# We give it a handle to the console so that it can connect it up to
			# the system innards.
	
	if doNorm:
		_logger.info(f"  [Main/Init] Pausing to give system initialization time to finish...")

	sleep(1)	# It should only take a second.

	if doInfo:
		_logger.info("  [Main/Init] Assuming system initialization is complete.")
	

		#|======================================================================
		#| 4. At this point, basic initializion is complete, and we can pro-
		#|		ceed to start up all of the major subsystems to start the
		#|		server actively running.  This process is handled by the 
		#|		Supervisor, so basically be just need to start it running.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	setThreadRole('startup')		# Denotes we are starting up the server.

	if doNorm:
		_logger.normal("") # At this point we can't just print() to stdout or we'll mess up curses.
		_logger.normal(f"[Main] (4) Starting up the {systemName} subsystems...")
		_logger.normal("")
	
			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| This starts up the supervisor, which in turn initializes and
			#| starts up all of the other major subsystems, and then continues
			#| running in the background.  When the supervisor thread finally
			#| exits, that's because the whole system is shutting down.

	supervisor.startup() # Tells the supervisor to start everything up.
			# NOTE: This also starts up all of the other major 
			# subsystems of GLaDOS.
				

		#|======================================================================
		#| 5. By the time we get here, the Supervisor is up and running in a 
		#|		background thread, and all we need to do is wait for it to exit, 
		#|		at which point we can exit the entire server process.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	setThreadRole('wait4exit')		# Denotes we just waiting to exit now.

	if doNorm:
		_logger.info(f"  [Main/Wait] Waiting for the {systemName} Supervisor to exit...")
	setThreadRole('waiting')	# Denotes that we are just waiting.
	supervisor.waitForExit()	# Waits for the Supervisor to exit.


		#|======================================================================
		#| 6. If we get here, then we are exiting the server application.
		#|		We should tell the settings and configuration facilities to
		#|		exit gracefully (so they can save state and so forth).
		#|		However, that is not fully implemented yet.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	setThreadRole('shutdown')	# Denotes that we are shutting down.

	if doNorm:
		_logger.normal(f"[Main] {systemName} server application is shutting down...")


		#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		#|	End of main code of server application.
		#|=========================================================
	
	_logger.debug("__main__._main(): Exiting from _main()...")

	if RAW_DEBUG:
		print("__main__._main(): Exiting from _main()...", file=stderr)

#__/ End function _main().


	#|==========================================================================
	#|
	#|	 4.	 Main script body.							   [script code section]
	#|
	#|			Above this section should only be definitions and
	#|			assignments.  Below is the main executable body of
	#|			the script.	 It just calls the _main() function (if
	#|			this script is not just being loaded as a submodule).
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
		
	_main()		# Call the private _main() function, defined above.
	
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
#|						END OF FILE:	glados-server.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
