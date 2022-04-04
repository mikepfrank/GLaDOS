#|==============================================================================
#|					 TOP OF FILE:	 infrastructure/logmaster.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		infrastructure/logmaster.py	   [Python 3 module source file]
  
	MODULE NAME:	logmaster
	FULL PATH:		$GIT_ROOT/GLaDOS/src/logmaster.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (Generic Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.logging
  
  
	SOFTWARE SYSTEM:		GLaDOS (Generic Lifeform and Domicile Operating System)
	----------------
  
		Note:  Although the present file exists as part of the
		GLaDOS system, the logmaster module is actually designed
		to be usable in any software system; it does not depend
		on any other parts of the GLaDOS system.
  
  
	SOFTWARE COMPONENT:		GLaDOS.logging
	-------------------
  
		For our purposes, a "software component" means a set of
		modules that are logically related to each other and
		that together implement some important capability.
		Component names generally appear in log record output,
		with the exception of the present component.
 
  
	MODULE DESCRIPTION:
	-------------------
  
		This module provides a customized logger based on Python's
		general logging facility.  The intent of putting this code
		into its own module is to enable its definitions to be
		accessed from within any number of other modules in the
		application, so they all can do logging in a consistent way
		This is particularly important when debugging.
  
		The specific new logging functionality we provide includes:
  
			 1.	 A new logging level called "NORMAL" is added
				 (in between INFO and WARNING).	 Its purpose
				 is to enable messages that are ordinarily
				 printed on stdout to be simultaneously logged
				 to the log file as NORMAL-level messages.
  
			 2.	 Ultra-convenient logging functions are exported
				 (debug(), info(), etc.) that do not require
				 even specifying a logger.
  
			 3.	 The logger can be configured (via global bools)
				 to display or not display various "optional"
				 levels of log messages (warning, info, debug)
				 to the console (stderr), and, separately, to
				 save them or not save them in the log file.
  
			 4.	 The logging formats for the file loghandlers
				 include the time, down to the millisecond.
  
			 5.	 All formats include the log level (except for
				 NORMAL messages displayed on stdout).
  
			 6.	 All log messages (again except normal messages
				 to the console) always include the
				 thread name, to facilitate debugging of
				 multithreaded programs.


	MODULE USAGE:
	-------------

		These are basic usage instructions, but for more features,
		see the rest of the module docs.  To use the logmaster
		module in an application,

			(1) In a file appdefs.py, define and export the
					globals systemName, appName, and topFile.
					systemName should be a string (a concise
					name for the software system); appName
					should be another string, in the format
					"<systemName>.<appSuffix>" (w/o brackets),
					and topFile should be the name of the
					top-level application script (w/o .py).

			(2) In the main application script and each
					module, import the logmaster module.

						import logmaster

			(3) In the main application script, do something
					like the following:

						logmaster.configLogMaster(role='startup',
							component=logmaster.appName)
						logger = logmaster.appLogger

					and thence, for normal program output, do:

						logger.normal("Blah blah blah...")

					and for logging at other levels, use logger.info(),
					logger.warn(), etc.	 After the startup phase of the
					program is over, you can change the thread role
					designation with something like

						logmaster.setThreadRole('running')	  ;

					this role designator appears in log file output.

			(4) At the top of other modules (after importing logmaster),
					do something like:

						logger = logmaster.getComponentLogger('<compName>')

					where <compName> is the formal name of the software
					component that that module is conceptually a part of.
					The component name will appear in log file output.

			(5) Look for output in the file <appName>.log.

		There are additional features for multithreaded applications
		and for generating automatically-logged exceptions.
		

	PUBLIC GLOBALS:
	---------------

	  The following are the global attributes of this module, which
	  may be accessed by other modules.


		Public constants:
		-----------------

			logmaster.{NORMAL_LEVEL,NORMAL}:int [public global constant integer]

				These constants identify a new logging level for
				normal program output.	(Above INFO, below WARNING.)
				NORMAL is just provided as a shorter name for
				NORMAL_LEVEL.


			logmaster.{systemName,sysName}:str	[public global constant string]

				Name of the overall system we are a part of.  This can
				be modified if needed for another application by
				assigning to logmaster.systemName any time before
				logmaster.configLogMaster() is called, or as an
				optional argument to it.  This name is important for
				setting up the logger (logging channel) hierarchy.


			logmaster.appName:str				[public global constant string]

				Name of the current application within the overall
				system.	 This can be modified if needed for another
				application by assigning to logmaster.appName any time
				before logmaster.configLogMaster() is called, or as an
				optional argument to it.  This name is important for
				setting up the logger (logging channel) hierarchy.


			logmaster.{NAME,THREADNAME,COMPONENT,	[public global constant integers]
				THREADROLE,MODULE,FUNCNAME,
				LEVELNAME}_FIELDWIDTH : int

				These integer parameters determine the widths of the
				corresponding fields of our default log line format
				string.	 Their values are also used by the
				CleanFormatter class to abbreviate content to the
				desired width before it is formatted, so that it
				doesn't overflow its field.


			logmaster.LOG_FORMATSTR:str			[public global constant string]
				
				Default line format for the main log file.	Actually,
				this "constant" can be modified if needed before
				initLogMaster() is called, or as an optional argument
				to initLogMaster().


			logmaster.{CONS_{WARN,INFO,DEBUG},	[public global constant booleans]
				LOG_{INFO,DEBUG}:bool
				
				Change these Booleans to modify how the logging levels
				for the console and the main log file are set up.
				Normally (using the default values recommended below)
				the console will show warnings and higher, and the log
				file will show info-level messages and higher.	For
				more flexible control, you can always just set the log
				level explicitly.


			logmaster.{log,console}_level:int
												[public global constant integers]
				
				These keep track of what logging level we are using for
				both the main log file and the console.	 Change these
				indirectly using configLogMaster().


			logmaster.minLevel:int				[public global constant integer]

				This is the minimum logging level we will display
				considering both the log file and console levels.


			logmaster.{doDebug,doInfo,doNorm,doWarn,doErr}:bool
												[public global constant booleans]

				Each of these booleans is set to True if the present
				minimum logging level is less than or equal to the
				specified level.


			logmaster.consHandler:logging.StreamHandler	  [public global object]
			
				A logging.StreamHandler that sends log lines to the
				system console (i.e., standard output).


		Public objects:
		---------------
				
			logmaster.logFormatter:LogFormatter			[public global object]
				
				This is the default LogFormatter instance used by
				logmaster for the main application log file.  It is
				based on the format string LOG_FORMATSTR above.	 It
				is created in initLogMaster().


			logmaster.theLoggingContext:LoggingContext
											[public global thread-local object]
				
				This is a single (but thread-local) LoggingContext
				object, to be shared by all modules (but it is
				different for each thread), for passing to their
				module-specific loggerAdapter objects that they
				will use for logging.  This object is created in
				this module, (in init_logging()), it gets
				initialized separately within each thread, and
				then it is updated dynamically, if needed, as
				the thread progresses.	It maintains thread-
				specific information, such as the thread's role
				and the software component that it is part of.


			logmaster.mainLogger:Logger					[public global object]
				
				This is the main logger for the application.  It can
				be used in modules that don't bother to define their
				own logger (but most modules should define a logger,
				either based on the systemName, the appName, or at
				least the module's own name).
				
				We don't initialize this when the module is first
				loaded, but wait until initLogMaster() is called,
				which should be done only once in the program, before
				using any of the logging capabilities.
				
				
			logmaster.{sysLogger,appLogger}:Logger		[public global objects]
				
				These are additional loggers that are included in the
				default logger hierarchy; they are both subordinate
				to the main logger, while being specific to the
				present system, and to the present application within
				the system, respectively.  


	EXCEPTION CLASSES:
	------------------

		Applications may subclass or mixin these classes to create
		their own exception classes that automatically generate log
		entries at designated logging levels.  See these classes'
		docstrings for additional details.	The indentation below
		indicates the subclass relationships between these classes.

			logmaster.LoggedException			[module public exception class]

			  logmaster.InfoException			[module public exception class]

				logmaster.ExitException			[module public exception class]

			  logmaster.WarningException		[module public exception class]

				logmaster.WrongThreadWarning	[module public exception class]

			  logmaster.ErrorException			[module public exception class]

				logmaster.CriticalException		[module public exception class]

				  logmaster.FatalException		[module public exception class]


	PUBLIC CLASSES:
	---------------

		Public classes exported by this module, other than exception
		classes.  See the classes' docstrings for additional details.

			logmaster.CleanFormatter					 [module public class]
			
			logmaster.LoggingContext					 [module public class]

			logmaster.ThreadActor						 [module public class]

			logmaster.AbnormalFilter					 [module public class]

			logmaster.NormalLogger						 [module public class]

			logmaster.NormalLoggerAdapter				 [module public class]

				
	Module revision history:
	------------------------
		
		v0.1 (2009-2012) - Initial version developed as part of the COSMICi
			system at FAMU Physics Dept., APCR-DRDL laboratory.	 (M. Frank)
			
		v0.2 (2016) - New revision for the Dynamic simulator, Sandia Labs,
			Dept. 1425.	 (M. Frank)
			
		v0.3 (2020-21) - Importing into GLaDOS for use in that system.
		
  
	Work to do/in progress:
	-----------------------
  
		 [ ] Create a structure (class object?) that lets us
			 avoid making each using module refresh its copies
			 of our globals whenever they change.
																			 """
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------

global _RAW_DEBUG		# Boolean: Whether to turn on low-level debug output.
_RAW_DEBUG = False		# Don't use it by default; it's pretty disruptive.

	#|===================================================================
	#| The following allows user code to tell logmaster to use different
	#| output streams in place of the usual STDOUT and STDERR streams,
	#| without necessarily having to actually change sys.stdout/stderr.
	#| So, for example, a curses application can reserve STDOUT for its
	#| own use, while telling logmaster to send normal-level log messages
	#| somewhere other than STDOUT for console display purposes.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global _alt_stdout, _alt_stderr
_alt_stdout = None
_alt_stderr = None

def set_alt_stdout(alt_stdout):
	global _alt_stdout
	_alt_stdout = alt_stdout

def set_alt_stderr(alt_stderr):

	global _alt_stderr

	_alt_stderr = alt_stderr
	updateStderr(alt_stderr)

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Note that the following two functions are marked private (leading '_') 
	# because they are only intended to be used from within logmaster itself.

def _outstr():

	"""Returns the current normal-output stream that 
		logmaster should be using for output of normal-level
		log messages to the 'console'."""

	if _alt_stdout != None:
		outstrm = _alt_stdout
	else:
		outstrm = sys.stdout

	return outstrm

def _errstr():

	"""Returns the current error-output stream that logmaster
		should be using for output of abnormal-level log 
		messages to the 'console'."""

	if _alt_stderr != None:
		errstrm = _alt_stderr
	else:
		errstrm = sys.stderr

	return errstrm

		#-----------------------------------------------------------------------
		#
		#  Some previously-completed coding tasks:
		#
		#		[/] Give each thread a logging context.
		#
		#		[/] Have each module use a LoggerAdapter, which uses
		#				the logging context.
		#
		#		[/] Let each module use its own logger, a descendant
		#				of the root logger "" in the logging hierarchy.
		#
		#		[/] Create a child logger for each node.
		#
		#-----------------------------------------------------------------------

#|==============================================================================
#|
#|	TABLE OF CONTENTS									
#|	-----------------
#|
#|		1.	Module imports.								   [module code section]
#|
#|			1.1.  Imports of standard python modules.	[module code subsection]
#|			1.2.  Imports of custom application modules.[module code subsection]
#|
#|		2.	Global constants, variables, and objects.	   [module code section]
#|
#|			2.1.  Special globals.						[module code subsection]
#|			2.2.  Public globals.						[module code subsection]
#|				2.2.1.	Public global constants.	 [module code subsubsection]
#|				2.2.2.	Public global objects.		 [module code subsubsection]
#|			2.3.  Private globals.						[module code subsection]
#|
#|		3.	Class definitions.							   [module code section]
#|
#|			3.1.  Exception classes.					[module code subsection]
#|			3.2.  Normal public classes.				[module code subsection]
#|			3.3.  Private classes.						[module code subsection]
#|
#|		4.	Function definitions.						   [module code section]
#|
#|			4.1.  Public function definitions.			[module code subsection]
#|			4.2.  Private function definitions.			[module code subsection]
#|
#|		5.	Module initialization.						   [module code section]
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		

	#|==========================================================================
	#|	 1. Module imports.								   [module code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	os		import	path
	# Used in calculating _srcfile, and also in getLoggerInfo().

import	sys			 # For stdout/stderr, for console loghandler & internal debugging of logmaster.
import	io			 # For TextIOBase, which we subclass in _NullOut.
import	logging		 # General python logging facility.
	# - Don't import names from within it, b/c we redefine some of them.
import	threading	 # Used for our threading.local LoggingContext.
import	traceback	 # Used for printing stack traces.


		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	systemName, sysName, appName, topFile
	# - The initial values of these that are defined later in this file are
	#	placeholders that should never be used.
	
import	appdefs					# Import definitions for the current application.
from	appdefs		import *	# Use systemName, appName, topFile for this application.

if _RAW_DEBUG:
	# Print the values of systemName, appName, and topFile that we imported
	# from appdefs.
	print(f"logmaster diagnostics:\n\tsystemName: {systemName}\n\tappName: {appName}\n\ttopFile: {topFile}")

	#|==========================================================================
	#|	2.	Global constants, variables, and objects.	   [module code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	2.1.  Special globals.						[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|
			#|	 logmaster.__all__:List[str]					[special global]
			#|
			#|		List of explicitly exported public names.
			#|
			#|		These are the names we provide that will get
			#|		automatically imported into another module if/when
			#|		it does:
			#|
			#|			from logmaster import *
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	__all__

__all__ = [
	'NORMAL_LEVEL',							 # Public global variables.
	'LOG_FILENAME', 'LOG_FORMATSTR',
	'CONS_WARN', 'CONS_INFO', 'CONS_DEBUG',
	'LOG_INFO', 'LOG_DEBUG',
	'systemName', 'sysName', 'appName',
	'log_level', 'console_level', 'minLevel',
	'doDebug', 'doInfo', 'doNorm', 'doWarn', 'doErr',
	'theLoggingContext', 'mainLogger',		 # Public global objects.
	'sysLogger', 'appLogger',
	'logFormatter', 'consHandler',
	'LoggedException', 'InfoException',		 # Public exception classes.
	'DebugException',
	'ExitException', 'WarningException', 
	'WrongThreadWarning', 'ErrorException',
	'CriticalException', 'FatalException',
	'LoggingContext', 'ThreadActor',		 # Public regular classes.
	'AbnormalFilter', 'NormalLogger',
	'NormalLoggerAdapter', 'CleanFormatter',
	'initLogMaster', 'configLogMaster',		 # Public functions.
	'normal', 'debug', 'info', 'error',
	'warning', 'warn', 'error', 'exception',
	'critical', 'lvlname_to_loglevel',
	'byname', 'getLogger', 'getComponentLogger',
	'testLogging', 'updateStderr',
	'setThreadRole', 'setComponent',
	'set_alt_stdout', 'set_alt_stderr',
	'getLoggerInfo',
]


		#|======================================================================
		#|
		#|	 2.2.  Public globals.						[module code subsection]
		#|
		#|		These are our globals that we encourage other modules
		#|		to access and utilize.
		#|
		#|		The documentation for these is included in the module
		#|		documentation string at the top of this file.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|==================================================================
			#|
			#|	 2.2.1.	 Public global constants.	 [module code subsubsection]
			#|
			#|		The following globals are not supposed to be ever
			#|		changed after their initial definition.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#|--------------------------------------------------------------
				#|
				#|	NORMAL_LEVEL,NORMAL:int			   [public global constants]
				#|
				#|		These constants identify a new logging level for
				#|		normal program output.	(Above INFO, below WARNING.)
				#|
				#|		NOTE: It might be imagined that NORMAL should be
				#|		between WARNING and ERROR instead, so that the
				#|		console log level can be set to NORMAL to cause
				#|		warnings to be suppressed from the console without
				#|		suppressing normal output.	However, this is
				#|		ensured anyway since the NormalLogger.normal()
				#|		method prints the given message to stdout
				#|		unconditionally, in addition to maybe logging it
				#|		using appropriate handlers.	 So, if we want to
				#|		suppress warnings from the console, we can just
				#|		set the console log level to ERROR, and we will
				#|		still see normal output (but not warnings).
				#|
				#|		Having NORMAL be between INFO and WARNING instead
				#|		is useful because it means that if the file log
				#|		level is set to WARNING, warnings (which may be
				#|		useful for detecting possible problems) will be
				#|		logged, while normal output (which may be
				#|		excessive) will not be.	 If we wish to log normal
				#|		output as well as warnings, we can set the file
				#|		log level to NORMAL.  And if we also want verbose
				#|		output, we can set the file log level to INFO.
				#|		And for maximum diagnostics for debugging, we set
				#|		the file log level to DEBUG.
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	NORMAL_LEVEL, NORMAL, NOTSET


NORMAL_LEVEL  =	 int((logging.INFO + logging.WARN)/2)
	# \_ New level for normal output.  Between INFO and WARNING.
	
NORMAL		  =	 NORMAL_LEVEL	# A more concise synonym.
	# \_ initLogMaster() adds this new level to our logging facility.

NOTSET		  =	 logging.NOTSET	# The default value for log_level
	# \_ Used in lvlname_to_loglevel() function.

				#|--------------------------------------------------------------
				#|
				#|	systemName,sysName,appName:str	[public global constants]
				#|
				#|		Name of the overall system we are a part of, and the
				#|		specific application within that system.  They can be
				#|		modified if needed for another application by assigning
				#|		to logmaster.systemName, etc., any time before
				#|		logmaster.configLogMaster() is called, or as optioal
				#|		arguments to it.  These are important for setting up
				#|		the logger (logging channel) hierarchy.
				#|
				#|	LOG_FILENAME:str				[public global constant]
				#|
				#|		Actually this is not really constant; it can be
				#|		modified for other applications if needed before
				#|		configLogMaster() is called, or as an optional
				#|		 argument to configLogMaster().
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#global	systemName,sysName
#global	appName
global	LOG_FILENAME

	# Ensure that systemName, appName, sysName and LOG_FILENAME are initialized.

if not "systemName" in dir():	# If appdefs did not already define systemName,
	sysName = systemName = "(Unknown System)"	# Define it (placeholder value).
else:
	sysName = systemName	# Shorter synonym for systemName

if not "appName" in dir():		# If appdefs did not already define systemName,
	appName = systemName + ".(Unknown App)"
		# The name of this application program (child of system).	 
else:									# Application name was defined.
	LOG_FILENAME = 'log/' + appName + ".log"	 # Construct the default log file name.

if not "LOG_FILENAME" in dir():		# If not already defined above,
	LOG_FILENAME = "script.log"		# Set it to a generic default log file name.


				#|--------------------------------------------------------------
				#|
				#|		NAME_FIELDWIDTH,			[public global constants]
				#|		THREADNAME_FIELDWIDTH,
				#|		COMPONENT_FIELDWIDTH,
				#|		THREADROLE_FIELDWIDTH,
				#|		MODULE_FIELDWIDTH,
				#|		FUNCNAME_FIELDWIDTH,
				#|		LEVELNAME_FIELDWIDTH : int
				#|
				#|			These integer parameters determine the widths
				#|			of the corresponding fields of our default log
				#|			line format string.	 Their values are also used
				#|			by the CleanFormatter class to abbreviate content
				#|			to the desired width before it is formatted, so
				#|			that it doesn't overflow its field.
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	NAME_FIELDWIDTH, THREADNAME_FIELDWIDTH, COMPONENT_FIELDWIDTH
global	THREADROLE_FIELDWIDTH, MODULE_FIELDWIDTH, FUNCNAME_FIELDWIDTH
global	LEVELNAME_FIELDWIDTH

NAME_FIELDWIDTH			= 24	# Width of logger name field.
THREADNAME_FIELDWIDTH	= 10	# Width of thread name field.
COMPONENT_FIELDWIDTH	= 14	# Width of component name field.
THREADROLE_FIELDWIDTH	= 9		# Width of thread role field.
MODULE_FIELDWIDTH		= 13	# Width of module filename field.
FUNCNAME_FIELDWIDTH		= 18	# Width of function name field.
LEVELNAME_FIELDWIDTH	= 8		# Width of logging level name field.


				#|--------------------------------------------------------------
				#|
				#|		LOG_FORMATSTR:str			  [public global constant]
				#|
				#|			Default format for the main log file.  Actually,
				#|			this "constant" can be modified if needed before
				#|			initLogMaster() is called, or as an optional
				#|			argument to initLogMaster().
				#|
				#|			IMPORTANT NOTE:	 The fields named 'threadrole' and
				#|			'component' below are only meaningful because these
				#|			keys are defined in the dictionary of the thread-
				#|			local (but lexically global) LoggingContext object
				#|			that gets passed into the constructor for the
				#|			LoggerAdapter that is used for doing the actual
				#|			logging.
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	LOG_FORMATSTR

LOG_FORMATSTR = (	# Current time.
				 "%(asctime)s | "										+
					# Logger name.
				 "%%(name)-%ds | "			% NAME_FIELDWIDTH			+	
					# Thread & its logging context (role & component):
				 "%%(threadName)%ds: "		% THREADNAME_FIELDWIDTH		+
				 "%%(component)%ds "		% COMPONENT_FIELDWIDTH		+
				 "%%(threadrole)-%ds | "	% THREADROLE_FIELDWIDTH		+
					# Source code file, line #, and function/method name.
				 "%%(module)%ds.py:"		% MODULE_FIELDWIDTH			+	
				 "%(lineno)-4d: "										+
				 "%%(funcName)-%ds | "		% FUNCNAME_FIELDWIDTH		+
					# Log level and log message.
				 "%%(levelname)%ds: "		% LEVELNAME_FIELDWIDTH		+	
				 "%(message)s"
				)								  


# ALT_FORMATSTR = (	# Current time.
#				 "%(asctime)s | "										+
#					# Logger name.
#				 "%%(name)-%ds | "			% NAME_FIELDWIDTH			+	
#					# Thread & its logging context (role & component):
#				 "%%(threadName)%ds: "		% THREADNAME_FIELDWIDTH		+
#				 "				 "		+
#				 "			| "			+
#					# Source code file, line #, and function/method name.
#				 "%%(module)%ds.py:"		% MODULE_FIELDWIDTH			+	
#				 "%(lineno)-4d: "										+
#				 "%%(funcName)-%ds | "		% FUNCNAME_FIELDWIDTH		+
#					# Log level and log message.
#				 "%%(levelname)%ds: "		% LEVELNAME_FIELDWIDTH		+	
#				 "%(message)s"
#				)								  


				#|--------------------------------------------------------------
				#|
				#|	CONS_WARN, CONS_INFO,		[public global constant booleans]
				#|	CONS_DEBUG, LOG_INFO,
				#|	LOG_DEBUG : bool
				#|
				#|		Change these Booleans to modify how the
				#|		logging levels for the console and the
				#|		main log file are set up.  Normally (using
				#|		the default values recommended below) the
				#|		console will show warnings and higher, and
				#|		the log file will show info-level messages
				#|		and higher.	 For more flexible control,
				#|		you can always just set the log level
				#|		explicitly.
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global CONS_WARN, CONS_INFO, CONS_DEBUG, LOG_INFO, LOG_DEBUG

		#|---------------------------------------------------
		#| Initialize the booleans that control the logging
		#| level for messages to the system console.

CONS_WARN = True	# Default value: True.
	# - Change this to False before initialization to suppress warnings from console.
	
CONS_INFO = False	# Default value: False.
	# - Change this to True before initialization if you want verbose information on console.
	
CONS_DEBUG = False	# Default value: False.
	# - Change this to True before initialization if you want detailed debug info on console.
	#	Overrides CONS_WARN.


		#|---------------------------------------------------
		#| Initialize the booleans that control the logging
		#| level for messages to the log file.

LOG_INFO = True		# Default value: True.
	# - Change this to False before initialization to suppress verbose info from log file.
	
LOG_DEBUG = False	# Default value: False.
	# - Change this to True before initialization to log detailed debugging information in log file.
	#	Overrides CONS_INFO.


				#|--------------------------------------------------------------
				#|
				#|	{log,console}_level:int	   [public global constant integers]
				#|
				#|		These keep track of what logging level we are
				#|		using for both the main log file and the console.
				#|		Change these indirectly using configLogMaster().
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global log_level, console_level

log_level		= logging.INFO		# By default, log file records messages at INFO level and higher.
console_level	= logging.WARNING	# By default, console displays messages at WARNING level & higher.


				#|--------------------------------------------------------------
				#|
				#|	minLevel,				   [public global constant integers]
				#|
				#|	do{Debug,Info,			   [public global constant Booleans]
				#|		Norm,Warn,Err}
				#|
				#|		The minLevel global is the minimum of the
				#|		current console logging level and the current
				#|		log-file logging level.	 Any messages below
				#|		this level (except normal out) do not need to
				#|		be generated at all.
				#|
				#|		The various do* globals are Booleans indicating
				#|		whether we need to generate log messages at the
				#|		corresponding level.
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global minLevel, doDebug, doInfo, doNorm, doWarn, doErr

	# The below function needs to be moved to the functions section.

def _noticeLevels():

	global minLevel, doDebug, doInfo, doNorm, doWarn, doErr
	
	minLevel = min(log_level, console_level)	# Calculate min logging level
	
	doDebug = (minLevel <= logging.DEBUG)
	doInfo = (minLevel <= logging.INFO)
	doNorm = True # Not (minLevel <= NORMAL) b/c we always display normal output
	doWarn = (minLevel <= logging.WARNING)
	doErr = (minLevel <= logging.ERROR)
	# Critical and fatal-level messages are always logged or displayed,
	# so there is no need for 'doCrit' or 'doFatal'.

	# If desired, one can turn on debug logging but comment out the following
	# to ferret out code that doesn't have an "if do___:" wrapped around it.
	
##	  doDebug = doInfo = doNorm = doWarn = doErr = False
	
#__/ End _noticeLevels().

	# Move this to the main body section
_noticeLevels()

			#|==================================================================
			#|
			#|	 2.2.2.	 Public global objects.		 [module code subsubsection]
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#|--------------------------------------------------------------
				#|
				#|	logFormatter:LogFormatter			[public global object]
				#|
				#|		This is the default LogFormatter instance used
				#|		by logmaster for the main application log file.
				#|		It is based on the format string LOG_FORMATSTR
				#|		above.	It is created in initLogMaster().
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	logFormatter

logFormatter = None		# Initially, no logFormatter has been created yet.

				#|--------------------------------------------------------------
				#|
				#|	theLoggingContext:LoggingContext	   [public global
				#|											thread-local object]
				#|
				#|		This is a single (but thread-local) LoggingContext
				#|		object, to be shared by all modules (but it is
				#|		different for each thread), for passing to their
				#|		module-specific loggerAdapter objects that they
				#|		will use for logging.  This object is created in
				#|		this module, (in init_logging()), it gets
				#|		initialized separately within each thread, and
				#|		then it is updated dynamically, if needed, as
				#|		the thread progresses.	It maintains thread-
				#|		specific information, such as the thread's role
				#|		and the software component that it is part of.
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	theLoggingContext	# A single global (but thread-local) LoggingContext object.

theLoggingContext = None	# To be properly initialized later (in init_logging()).


				#|--------------------------------------------------------------
				#|
				#|	mainLogger:Logger					[public global object]
				#|
				#|		This is the main logger for the application.
				#|		It can be used in modules that don't bother
				#|		to define their own logger (but most modules
				#|		should define a logger, either based on the
				#|		systemName, the appName, or at least the
				#|		module's own name).
				#|
				#|		We don't initialize this when the module is
				#|		first loaded, but wait until initLogMaster()
				#|		is called, which should be done only once in
				#|		the program, before using any of the logging
				#|		capabilities.
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	mainLogger	# The main logger for the current application.

mainLogger = None	# To be initialized later (in initLogMaster()).


				#|--------------------------------------------------------------
				#|
				#|	sysLogger,appLogger:Logger			[public global objects]
				#|
				#|		These are additional loggers that are included
				#|		in the default logger hierarchy; they are both
				#|		subordinate to the main logger, while being
				#|		specific to the present system, and to the
				#|		present application within the system,
				#|		respectively.	
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# Some more loggers.  Subordinate to the main logger, but
	# specific to the system and the application within the
	# system.  These may not be needed...
	
global	sysLogger, appLogger

sysLogger = None	# Logger for the overall system named by logmaster.systemName.
appLogger = None	# Logger for the specific application named by logmaster.appName.


				#|--------------------------------------------------------------
				#|
				#|	consHandler:logging.StreamHandler	[public global object]
				#|
				#|		A logging.StreamHandler that sends log lines
				#|		to the system console (i.e., standard output).
				#|
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global consHandler

consHandler = None	# Will be properly initialized later, in initLogMaster().


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


			#|------------------------------------------------------------------
			#|
			#|	_initialized:bool				[module private global variable]
			#|
			#|		This bool is set to True once the logmaster module
			#|		has been initialized.  It is used to prevent the
			#|		module from being initialized more than once.  Use
			#|		the initLogMaster() function to initialize the
			#|		module.	 (We didn't use a concurrency-control flag
			#|		here because nobody else will get the opportunity
			#|		to wait for it anyway.)
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	_initialized

_initialized = False	# Initially false; this module has not yet been initialized.
		
	   
			#|------------------------------------------------------------------
			#|
			#|	_moduleLogger:Logger		  [module private global object]
			#|
			#|		This logger (which is not publicly exported) is
			#|		to be used, from within this module only, for log
			#|		messages generated by this module.	This is also a
			#|		model for what other non-application-specific
			#|		modules that use logmaster should do to get their
			#|		own module-local loggers.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	_moduleLogger

_moduleLogger = None	 # Really initialize this later, in init_logging().


			#|------------------------------------------------------------------
			#|
			#|	_srcfile:str				[module private global variable]
			#|
			#|		Copied from logging/__init__.py.  This code had to
			#|		be copied into this module in order for it to get
			#|		the value of __file__ that we want to use here.
			#|
			#|		Comment from logging/__init__.py:  "_srcfile is
			#|		used when walking the stack to check when we've
			#|		got the first caller stack frame, by skipping
			#|		frames whose filename is that of this module's
			#|		source. It therefore should contain the filename
			#|		of this module's source file."
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global _srcfile		# Name of this file (logmaster.py).	 Initialized below.

def dummyFunc(): pass
	# This function is being defined solely as a hack that allows us
	# to find out our filename even when this module is frozen.

if hasattr(sys, 'frozen'):
	_srcfile = dummyFunc.__code__.co_filename
elif __file__[-4:].lower() in ['.pyc', '.pyo']:
	_srcfile = __file__[:-4] + '.py'
else:
	_srcfile = __file__
_srcfile = path.normcase(_srcfile)


	#|==========================================================================
	#|
	#|	3.	Class definitions.							   [module code section]
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|
		#|	3.1.  Exception classes.					[module code subsection]
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|
			#|		LoggedException						[public exception class]
			#|
			#|			A LoggedException is an exception such that,
			#|			when it is first constructed, a log message of
			#|			an appropriate level is automatically
			#|			generated and sent to a specified logger.
			#|
			#|			The constructor for a LoggedException takes a
			#|			logger and a message.  The logging level for
			#|			the message is determined by the subclass of
			#|			LoggedException that is used (see subclasses
			#|			defined below).
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# IMPLEMENTATION NODE: The following class is intended to be used as an
	# abstract base class, so really, we should set its meta-class to abc.

class LoggedException(Exception):
	
	"""A LoggedException is an exception such that, when it is first
		constructed, a log message of an appropriate level is automatically
		generated and sent to a specified logger.
		
		The constructor for a LoggedException takes a logger and a message.
		The logging level for the message is determined by the subclass of
		LoggedException that is used (see subclasses defined below).


			CLASS VARIABLES:
			----------------

				LoggedException.defLogger:logging.Logger		[class variable]
		
						The default logger to use for exceptions of a
						given (subclass) type.	NOTE: This value is
						just a placeholder for this attribute in this
						abstract base class.  All concrete derived
						classes (ones for which a constructor will
						actually be called) MUST override this class
						variable, or it will cause an exception to be
						thrown (before the one you want gets thrown)!
			
				LoggedException.loglevel:int					[class variable]
		
						The logging level of the exception.	 We set
						its default value to logging.NOTSET as a
						placeholder in this abstract class.	 Subclasses
						should override this value with the value that
						is appropriate for their purposes.	This is
						done in the subclasses defined below.

		"""

		#|======================================================================
		#|						(in class LoggedException)
		#|	Class variables.								[class code section]
		#|

			#|----------------------------------------------------------------------
			#|
			#|		LoggedException.defLogger:logging.Logger	[class variable]
			#|
			#|				The default logger to use for exceptions of a
			#|				given (subclass) type.	NOTE: This value is
			#|				just a placeholder for this attribute in this
			#|				abstract base class.  All concrete derived
			#|				classes (ones for which a constructor will
			#|				actually be called) MUST override this class
			#|				variable, or it will cause an exception to be
			#|				thrown (before the one you want gets thrown)!
			#|

	defLogger = None	# Default logger.  None defined for this base class.


			#|----------------------------------------------------------------------
			#|
			#|		LoggedException.loglevel:int				[class variable]
			#|
			#|			The logging level of the exception.	 We set
			#|			its default value to logging.NOTSET as a
			#|			placeholder in this abstract class.	 Subclasses
			#|			should override this value with the value that is
			#|			appropriate for their purposes.	 This is done in
			#|			the subclasses defined below.
			#|

	loglevel = logging.NOTSET


		#|======================================================================
		#|						(in class LoggedException)
		#|	Special instance methods.						[class code section]
			
			#|------------------------------------------------------------------
			#|
			#|		LoggedException.__init__()		[special instance method]
			#|
			#|			The instance initializer for a LoggedException
			#|			creates a default log message for the exception
			#|			(if none is provided), and then goes ahead and
			#|			logs the occurrence of the exception to the
			#|			provided logger.  Note that this initial logging
			#|			of the exception will generally occur *before*
			#|			the exception is actually raised, in the raising
			#|			routine wherever the exception's constructor is
			#|			called.	 The entity that catches the exception
			#|			may of course do additional logging, such as a
			#|			logger.exception() call which will also display
			#|			a traceback.  We avoid printing tracebacks here,
			#|			since that may not be needed for exceptions that
			#|			are caught and handled appropriately somewhere
			#|			in the surrounding (i.e., catching) code.
			#|
	
	def __init__(inst, msg:str=None, level:int=None, logger:logging.Logger=None):
		
		"""The instance initializer for a LoggedException creates a
		   default log message for the exception (if none is
		   provided), and then goes ahead and logs the occurrence of
		   the exception to the provided logger.  Note that this
		   initial logging of the exception will generally occur
		   *before* the exception is actually raised, in the raising
		   routine wherever the exception's constructor is called.
		   The entity that catches the exception may of course do
		   additional logging, such as a logger.exception() call which
		   will also display a traceback.  We avoid printing
		   tracebacks here, since that may not be needed for
		   exceptions that are caught and handled appropriately
		   somewhere in the surrounding (i.e., catching) code."""

			#--------------------------------------------------------
			# If no logger was specified in the constructor call, use
			# the instance's class's default logger.
		
		if logger==None:
			logger = inst.defLogger	 # This should get the value of this
				# class variable for the object's actual class (not from
				# this abstract base class LoggedException).

			#----------------------------------------------------------------
			# Do some error handling in case no default logger was specified.
			# (Or, should we just use our own private _moduleLogger in
			# such a case?)
				
		if logger==None:
			errmsg = ("LoggedException.__init__(): No default logger " +
					  "was provided for this class of LoggedException.")
			if doErr: _moduleLogger.error(errmsg)
			traceback.print_stack()	 # goes to sys.stderr
			raise TypeError(errmsg)

			#-----------------------------------------------------------
			# If no logging level was specified in the constructor call,
			# use the instance's class's default logging level.
			
		if level==None:
			level = inst.loglevel	# Get derived class's log level.

			#----------------------------------------------------------------
			# Do some error handling in case no logging level was specified.
				
		if level==None:
			errmsg = ("LoggedException.__init__(): No default log level " +
					  "was provided for this class of LoggedException.")
			if doErr: _moduleLogger.error(errmsg)
			traceback.print_stack()	 # goes to sys.stderr
			raise TypeError(errmsg)

			#-----------------------------------------------------------
			# If no log message was provided in the constructor call,
			# create a default message appropriate to our logging level.
			
		if msg==None:
			msg = ('Creating a LoggedException at level %s.' %
				   logging._levelNames[level])

			#---------------------------------------
			# Finally, actually log the log message.
			
		#[The following low-level diagnostic for debugging is commented out.]
		#print("About to log message [%s] at level %s." % (msg, str(level)),
		#	   file=sys.stdout)

		logger.log(level, msg)
		
	#__/ End LoggedException.__init__().
 
# End class LoggedException


			#|------------------------------------------------------------------
			#|
			#|		InfoException						[public exception class]
			#|
			#|			An InfoException, when it is raised at all, is
			#|			simply a way to indicate in which of several
			#|			normal ways a routine is returning, in cases
			#|			where this information is worth reporting in
			#|			the log file at INFO level.	 An InfoException
			#|			should be immediately caught by the caller &
			#|			not re-raised.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class InfoException(LoggedException):

	"""An InfoException, when it is raised at all, is simply a way to
	   indicate in which of several normal ways a routine is
	   returning, in cases where this information is worth reporting
	   in the log file at INFO level.  An InfoException should be
	   immediately caught by the caller & not re-raised.

			CLASS VARIABLES:
			----------------

				InfoException.loglevel:int			[class variable]

					The default logging level of an InfoException
					is of course logging.INFO.	This overrides the
					default value of logging.NOTSET that otherwise
					would have been inherited from LoggedException."""
	
		#|======================================================================
		#|	Class variables.	(in class InfoException)	[class code section]

			#|------------------------------------------------------------------
			#|
			#|		InfoException.loglevel:int					[class variable]
			#|
			#|			The default logging level of an InfoException
			#|			is of course logging.INFO.	This overrides the
			#|			default value of logging.NOTSET that otherwise
			#|			would have been inherited from LoggedException.
	
	loglevel = logging.INFO
	
#__/ End class InfoException


class DebugException(LoggedException):

	"""Like InfoException, but is only logged at DEBUG level."""

	loglevel = logging.DEBUG

			#|------------------------------------------------------------------
			#|
			#|		ExitException						[public exception class]
			#|
			#|			An ExitException is like an InfoException in
			#|			that it is reported at INFO level; however, it
			#|			is intended to cause the entire thread in which
			#|			it takes place to terminate.  (Use FatalException
			#|			to cause the entire application PROCESS to
			#|			terminate.)
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
class ExitException(InfoException):

	"""An ExitException is like an InfoException in that it is
	   reported at INFO level; however, it is intended to cause
	   the entire thread in which it takes place to terminate.
	   (Use FatalException to cause the entire application
	   PROCESS to terminate.)"""
	
	pass	# No differences from InfoException class except connotation.

#__/ End class ExitException


			#|------------------------------------------------------------------
			#|
			#|		WarningException					[public exception class]
			#|
			#|			These exceptions, when they are raised at all,
			#|			are simply used as a way to exit early from a
			#|			routine with some indication as why we are
			#|			exiting early, due to some harmless but unex-
			#|			pected circumstance that is worth reporting at
			#|			WARNING level, as a sort of alternate return
			#|			code; they should be caught (and not re-raised)
			#|			at a high level, before they have a chance to
			#|			interfere significantly with overall program
			#|			flow.  Basically, for any routine that might
			#|			throw a WarningException, all callers of that
			#|			routine should handle it.
			#|
			#|			Creating a WarningException automatically
			#|			generates a log message at WARNING level.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class WarningException(LoggedException):
	
	"""A WarningException, when it is raised at all, is simply used as
	   a way to exit early from a routine with some indication as why
	   we are exiting early, due to some harmless but unexpected
	   circumstance that is worth reporting at WARNING level, as a
	   sort of alternate return code; they should be caught (and not
	   re-raised) at a high level, before they have a chance to
	   interfere significantly with overall program flow.  Basically,
	   for any routine that might throw a WarningException, all
	   callers of that routine should handle it.
			Creating a WarningException automatically generates a log
	   message at WARNING level.

			CLASS VARIABLES:
			----------------

				WarningException.loglevel:int					[class variable]

					The default logging level of a WarningException is
					of course logging.WARNING.	This overrides the
					default value of logging.NOTSET that otherwise
					would have been inherited from LoggedException."""
	
		#|======================================================================
		#|	Class variables.   (in class WarningException)	[class code section]

			#|------------------------------------------------------------------
			#|
			#|		WarningException.loglevel:int				[class variable]
			#|
			#|			The default logging level of a WarningException
			#|			is of course logging.WARNING.  This overrides the
			#|			default value of logging.NOTSET that otherwise
			#|			would have been inherited from LoggedException.
			#|
	
	loglevel = logging.WARNING
	
#__/ End class WarningException.


			#|------------------------------------------------------------------
			#|
			#|		WrongThreadWarning					[public exception class]
			#|
			#|			This subclass of WarningException connotes
			#|			that a method that was intended to be called
			#|			only from within a specific thread is being
			#|			called from some other thread, instead.	 In
			#|			such a case, the method will generally just
			#|			throw a WrongThreadWarning exception instead
			#|			of returning normally, and will have no side
			#|			effects.  This exception is designated to be
			#|			at warning level, b/c it may be safely caught
			#|			and ignored given that the method throwing it
			#|			will have had no side effects.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class WrongThreadWarning(WarningException):

	"""This subclass of WarningException connotes that a method that
	   was intended to be called only from within a specific thread is
	   being called from some other thread, instead.  In such a case,
	   the method may just throw a WrongThreadWarning exception
	   instead of returning normally, and in such a case the method
	   should have had no side effects.	 This exception is designated
	   to be logged at warning level, b/c it may be safely caught and
	   ignored, given that the method throwing it will have had no
	   side effects."""
	
	pass
#__/ End class WrongThreadWarning.


			#|------------------------------------------------------------------
			#|
			#|		ErrorException						[public exception class]
			#|
			#|			An ErrorException indicates a fairly serious
			#|			problem, one that might prevent us from doing
			#|			(or doing properly) a fairly signifcant task.
			#|			A caller may or may not be able to handle it.
			#|			Creating an ErrorException automatically
			#|			generates a log message at ERROR level.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class ErrorException(LoggedException):

	"""An ErrorException indicates a fairly serious problem, one that
	   might prevent us from doing (or doing properly) a fairly
	   signifcant task.	 A caller may or may not be able to handle it.
	   Creating an ErrorException automatically generates a log
	   message at ERROR level.

			CLASS VARIABLES:
			----------------

				ErrorException.loglevel:int						[class variable]

					The default logging level of an ErrorException
					is of course logging.ERROR.	 This overrides the
					default value of logging.NOTSET that otherwise
					would have been inherited from LoggedException."""
	
		#|======================================================================
		#|	Class variables.   (in class ErrorException)	[class code section]
		#|,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

			#|------------------------------------------------------------------
			#|
			#|		ErrorException.loglevel:int					[class variable]
			#|
			#|			The default logging level of an ErrorException
			#|			is of course logging.ERROR.	 This overrides the
			#|			default value of logging.NOTSET that otherwise
			#|			would have been inherited from LoggedException.
			#|
			#|,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

	loglevel = logging.ERROR
	
#__/ End class ErrorException.


			#|------------------------------------------------------------------
			#|
			#|		CriticalException					[public exception class]
			#|
			#|			A CriticalException indicates a very serious
			#|			problem, one that will probably cause us to
			#|			fail to accomplish some very important task.
			#|			It may be difficult for callers to recover
			#|			gracefully, if at all.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class CriticalException(ErrorException):

	"""A CriticalException indicates a very serious problem, one that
	   will probably cause us to fail to accomplish some very
	   important task.	It may be difficult for callers to recover
	   gracefully, if at all.

			CLASS VARIABLES:
			----------------

				CriticalException.loglevel:int					[class variable]

					The default logging level of a CriticalException
					is of course logging.CRITICAL.	This overrides the
					default value of logging.ERROR that otherwise
					would have been inherited from ErrorException."""
	
		#|======================================================================
		#|	Class variables.  (in class CriticalException)	[class code section]

			#|------------------------------------------------------------------
			#|
			#|		CriticalException.loglevel:int				[class variable]
			#|
			#|			The default logging level of a CriticalException
			#|			is of course logging.CRITICAL.	This overrides the
			#|			default value of logging.NOTSET that otherwise
			#|			would have been inherited from LoggedException.

	loglevel = logging.CRITICAL
	
#__/ End class CriticalException


			#|------------------------------------------------------------------
			#|
			#|		FatalException						[public exception class]
			#|
			#|			Like a CriticalException, but even worse.
			#|			When this exception is raised, it generally
			#|			causes the application to exit, with or
			#|			without a stack backtrace (depending on how
			#|			and whether it is handled).
			#|
			#|				Fatal exceptions are actually logged at
			#|			the same level as critical exceptions; this
			#|			class designation is really just documentation
			#|			to the programmer to tell them to expect to be
			#|			unable to recover from this kind of error other
			#|			than by exiting.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class FatalException(CriticalException):

	"""A FatalException is a kind of CriticalException, but even worse.
	   When this type of exception is raised, it generally causes the
	   application to exit, with or without a stack backtrace
	   (depending on how and whether it is handled).

		   Fatal exceptions are actually logged at the same level as
		critical exceptions; this class designation is really just
		documentation to the programmer to tell them to expect to be
		unable to recover from this kind of critical error other than
		by exiting.

			CLASS VARIABLES:
			----------------

				FatalException.loglevel:int					 [class variable]

					The default logging level of a CriticalException
					is of course logging.FATAL.	 This overrides the
					default value of logging.NOTSET that otherwise
					would have been inherited from LoggedException."""
	
		#|======================================================================
		#|	 Class variables.  (in class FatalException)  [class code section]

			#|------------------------------------------------------------------
			#|
			#|		FatalException.loglevel:int					[class variable]
			#|
			#|			The default logging level of a FatalException
			#|			is of course logging.FATAL.	 This overrides the
			#|			default value of logging.NOTSET that otherwise
			#|			would have been inherited from LoggedException.
			#|

	loglevel = logging.FATAL	# This is actually the same as CRITICAL.
	
#__/ End class FatalException
			

		#|======================================================================
		#|
		#|	 3.2.  Normal public classes.				[module code subsection]
		#|
		#|		In this code section, we define public classes other
		#|		than exception classes.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|
			#|	CleanFormatter(logging.Formatter)				[public class]
			#|													
			#|		This customized subclass of logging.Formatter
			#|		ensures that values to be formatted will fit in
			#|		the designated field widths (defined by the
			#|		logmaster.*_FIELDWIDTH globals).  It also includes
			#|		support for new fields <component> and
			#|		<threadrole> which are helpful when debugging
			#|		complex, multithreaded applications.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class CleanFormatter(logging.Formatter):
	
	"""This customized subclass of logging.Formatter ensures that
		values to be formatted will fit in the designated field
		widths (defined by the logmaster.*_FIELDWIDTH globals).
		It also includes support for new fields <component> and
		<threadrole> which are helpful when debugging complex,
		multithreaded applications."""

	#[This is unnecessary since it's inherited anyway.]
	#def __init__(self, fmt=None, datefmt=None, style='%'):
	#	 logging.Formatter.__init__(self, fmt, datefmt, style)
		
	def format(self, record):
		"""This overrides the default .format() method inherited
		   by the logging.Formatter class, to first truncate string
		   fields of the log record to the desigated field width."""

			# Shorten all the string fields of the record as necessary to fit within the designated field widths.
		
		if hasattr(record,'name'):
			record.name			= _limitLength(record.name,			NAME_FIELDWIDTH)

		if hasattr(record,'threadName'):
			record.threadName	= _limitLength(record.threadName,	THREADNAME_FIELDWIDTH)

		if hasattr(record,'component'):
			record.component	= _limitLength(record.component,	COMPONENT_FIELDWIDTH)
		else:
			record.component	= _limitLength("(unknown)",	COMPONENT_FIELDWIDTH)

		if hasattr(record,'threadrole'):
			record.threadrole	= _limitLength(record.threadrole,	THREADROLE_FIELDWIDTH)
		else:
			record.threadrole	= _limitLength("(unknown)",	THREADROLE_FIELDWIDTH)

		if hasattr(record,'module'):
			record.module		= _limitLength(record.module,		MODULE_FIELDWIDTH)

		if hasattr(record,'funcName'):
			record.funcName		= _limitLength(record.funcName+'()',FUNCNAME_FIELDWIDTH)

		if hasattr(record,'levelname'):
			record.levelname	= _limitLength(record.levelname,	LEVELNAME_FIELDWIDTH)
		
		return	logging.Formatter.format(self, record)
	
	#__/ End method CleanFormatter.format().
	
#__/ End class CleanFormatter.


			#|----------------------------------------------------------------------
			#|
			#|	LoggingContext(threading.local)						[public class]
			#|
			#|		An object of this thread-local class serves as a
			#|		dictionary on which each thread can store & track
			#|		context information which will be passed to the
			#|		LoggerAdapter for any given module, enabling the log
			#|		records to be augmented with extra information printed
			#|		in the top-level log line format string.
			#|
			#|		A single global LoggingContext object tracks context
			#|		information throughout the application - although its
			#|		attributes have different values in different threads.
			#|
			#|		Each time a new thread is created or a thread changes
			#|		its role, the attributes of the global loggingContext
			#|		should be updated to reflect the context information
			#|		specific to that thread.  Some of this is handled
			#|		automatically by LoggingContext's .__init__() method.
			#|
			#|		In the scope of typical user applications, important
			#|		pieces of context information may include:
			#|
			#|			.threadname
			#|
			#|				The name of the current thread, helpful for
			#|				debugging threading problems.
			#|
			#|			.threadrole
			#|			
			#|				The role that the current thread is engaged
			#|				in. E.g. "startup", "Node1Main.consDriver",
			#|				"guibot", and so forth.
			#|
			#|			.component
			#|
			#|				The system component that the thread is
			#|				associated with, e.g., "server", "node #0",
			#|				"node #1", etc.
			#|
			#|			.nodenum
			#|			
			#|				The numeric ID of the network node (if any)
			#|				associated with this action.  None if no
			#|				network node is related.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class LoggingContext(threading.local):

	"""An object of this thread-local class serves as a dictionary on
	   which each thread can store & track context information which
	   will be passed to the LoggerAdapter for any given module,
	   enabling the log records to be augmented with extra thread-
	   specific information printed in the top-level log line format
	   string.

	   A single global LoggingContext object tracks context
	   information throughout the application - although its
	   attributes have different values in different threads.
	
	   Each time a new thread is created or a thread changes its role,
	   the attributes of the global loggingContext should be updated
	   to reflect the context information specific to that thread.
	   Some of this is handled automatically by LoggingContext's
	   .__init__() method.
	
	   In the scope of typical user applications, important
	   pieces of context information attached to the LoggingContext
	   may include:
	
		   .threadname
		   
				The name of the current thread, helpful for debugging
				threading problems.
		
		   .threadrole
				  
				The role that the current thread is engaged in. E.g.
				"startup", "Node1Main.consDriver", "guibot", and so
				forth.
		
		   .component

				The system component that the thread is associated
				with, e.g., "server", "node #0", "node #1", etc.
		
		   .nodenum
		
				The numeric ID of the network node (if any) associated
				with this action.  None if no network node is related.


		CLASS VARIABLES:
		----------------

			LoggingContext.defComp:str							[class variable]

				This class variable specifies the default value of the
				LoggingContext's .component attribute, if it is not
				otherwise specified.  This is just a placeholder value,
				"(unsetComp)".

			LoggingContext.defRole:str							[class variable]

				This class variable specifies the default value of the
				LoggingContext's .threadrole attribute, if it is not
				otherwise specified.  This is just a placeholder value,
				"(unsetRole)".


		PUBLIC PROPERTIES:
		------------------

			loggingContext.threadrole:str					[public property]

				The name of the role that the current thread is
				currently playing.
				

			loggingContext.component:str					[public property]

				The name of the software or hardware component of the
				overall system that the current thread is currently
				implementing, modeling, or serving."""

		#|======================================================================
		#|						 (in class LoggingContext)
		#|		Class attributes.							[class code section]
		#|,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

	defComp = "(unsetComp)"	   # By default, we don't know which system component this thread is being created to manage.
	defRole = "(unsetRole)"	   # By default, we don't know what role this thread is supposed to be playing.


		#|----------------------------------------------------------------------
		#|						 (in class LoggingContext)
		#|		Private instance attributes.		[class code documentation]
		#|
		#|			The following attributes of instances of this class
		#|			are not intended to be directly accessed by external
		#|			users of this class.
		#|
		#|				._dict						[private instance attribute]
		#|
		#|					A dictionary containing the attribute-value
		#|					mapping for this LoggingContext object.
		#|
		#|----------------------------------------------------------------------

	
		#|======================================================================
		#|						 (in class LoggingContext)
		#|		Special instance methods.					[class code section]
			
			#|------------------------------------------------------------------
			#|
			#|	LoggingContext.__init__()			[special instance method]
			#|
			#|		The initializer of the global loggingContext will
			#|		get called once for each thread, when the global
			#|		is first accessed from within that thread.	We
			#|		simply initialize its members based on thread
			#|		attributes.	 Every thread that wants to use the
			#|		logmaster module for logging should be an instance
			#|		of the logmaster.ThreadActor class, or of a
			#|		subclass of it, or at least have a .role attribute.
			#|		The value to which the "component" dictionary key
			#|		is assigned can be changed to "node0", "node1", etc.,
			#|		for errors being reported on behalf of specific
			#|		network nodes.

	def __init__(inst, myrole=None, forWhom=None, **kwargs):

		"""The initializer of the global loggingContext will get
		   called once for each thread, when the global is first
		   accessed from within that thread.  We simply initialize its
		   members based on thread attributes.	Every thread that
		   wants to use the logmaster module for logging should be an
		   instance of the logmaster.ThreadActor class, or of a
		   subclass of it, or at least have a .role attribute.	The
		   value to which the "component" dictionary key is assigned
		   can be changed to "node0", "node1", etc., for errors being
		   reported on behalf of specific network nodes.

			   Initializer arguments:
			   ----------------------

				   myrole	- Initial value of .threadrole attribute.

				   forWhom	- Initial value of .component attribute.

				   **kwargs - Any additional keyword arguments to be
							   passed to threading.local.__init__()."""

			#-------------------------------------------------------
			# First, do the default initialization for thread.local
			# objects, so that subsequent operations on this object
			# in this initializer will treat it as thread-local.

		threading.local.__init__(inst, **kwargs)
			#\_ Do the default thread.local initialization.

			#------------------------------------------
			# Initialize local copies of the component
			# and role from arguments or defaults.

		if (forWhom == None):	forWhom = inst.defComp
		if (myrole	== None):	myrole	= inst.defRole

			#-----------------------------------
			# Figure out which thread we're in.
			
		thread = threading.current_thread()

		#[Commented-out diagnostic for low-level debugging.]
		#print("Initializing logging context in thread %s." % thread,
		#	   file=sys.stderr)

			#----------------------------------------------------------
			# Set up the loggingContext's dictionary of context items.
			
		inst._dict = {}	 # Start with empty dictionary.

			#---------------------------------------------------------
			# If the thread we're in has no role/component attributes
			# defined, go ahead set them based on our local values.

		if not hasattr(thread, 'role'):			thread.role		 = myrole
		if not hasattr(thread, 'component'):	thread.component = forWhom

			#--------------------------------------------------------
			# Set this logging context's threadrole and component
			# attributes.  These next two lines use the property
			# setters defined after the current method.
			
		inst.threadrole = thread.role	   # Set the role of this thread.
		inst.component = thread.component  # What system component does it involve?

#[Commented-out diagnostic for low-level debugging.]
#		 print("The dictionary is: [%s]." % inst._dict, file=sys.stderr)

	#__/ End method LoggingContext.__init__().


		#|======================================================================
		#|						 (in class LoggingContext)
		#|		Instance public properties.					[class code section]

			#|------------------------------------------------------------------
			#|
			#|	inst.threadrole						[instance public property]
			#|
			#|		This property is used to keep track of the current
			#|		thread's current role string within the dictionary
			#|		structure provided by the LoggingContext object.

	@property
	def threadrole(inst):
		
		"""The name of the role that the current thread is currently
		   playing."""
		
		return inst._dict['threadrole']

	@threadrole.setter
	def threadrole(inst, role:str):
		inst._dict['threadrole'] = role


			#|------------------------------------------------------------------
			#|
			#|	inst.component						[instance public property]
			#|
			#|		This property is used to keep track of the current
			#|		thread's component string within the dictionary
			#|		structure provided by the LoggingContext object.

	@property
	def component(inst):
		
		"""The name of the software or hardware component of the
		   overall system that the current thread is currently
		   implementing, modeling, or serving."""
		
		return inst._dict['component']

	@component.setter
	def component(inst, forWhom:str):
		inst._dict['component'] = forWhom


		#|======================================================================
		#|						 (in class LoggingContext)
		#|		Duck-typing support.						[class code section]
		#|
		#|			The following definitions allow instances of the
		#|			present class to behave like instances of other
		#|			types that we are not formally a subclass of.
		
			#|------------------------------------------------------------------
			#|					  (in class LoggingContext)
			#|	Dictionary behavior.						[class duck type]
			#|
			#|		The following code allows LoggingContext objects
			#|		to be used as if they were dictionary objects.	We
			#|		define these methods to support "dictionary-like"
			#|		behavior on the part of instances of the
			#|		LoggingContext class by dispatching them directly
			#|		to the underlying dictionary.

	#[I think the following is not necessary since we define .__iter__() below.]
	#def iter(inst):		 # If someone asks for an interator on us,
	#	 inst._dict.iter()	 #	 give them an iterator on our dictionary.

	def __getitem__(inst, name):			# .__getitem__() on us goes to
		return inst._dict.__getitem__(name) #	our dictionary instead.

	def __iter__(inst):						# .__iter__() on us goes to
		return inst._dict.__iter__()		#	our dictionary instead.

#__/ End class LoggingContext


			#|----------------------------------------------------------------------
			#|
			#|	ThreadActor											[public class]
			#|
			#|		This subclass of Thread (which can be used as a
			#|		mixin class) adds an extra initialization keyword
			#|		argument role=<str>, which sets the .role attribute of
			#|		the thread, as separate from the .name argument (this
			#|		lets us keep the .name argument as an automatic
			#|		sequence counter, Thread-1, Thread-2, etc.).
			#|
			#|		The 'role' attribute is used by the loggingContext
			#|		when it gets initialized later on, when the thread
			#|		uses it.  The purpose of that is so that the thread
			#|		role is available as a field that can be displayed
			#|		as specified in the logging format string.
			#|
			#|		In addition to 'role', there's another optional
			#|		initialization keyword argument called
			#|		'component', the idea of which is to identify which
			#|		system component a given thread is currently working
			#|		on behalf of.  This is used similarly to 'role.'
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
class ThreadActor(threading.Thread):

	"""This subclass of threading.Thread (which can be used as a mixin
	   class) adds an extra initialization keyword argument role=<str>,
	   which sets the .role attribute of the thread, as separate from
	   the .name argument (this lets us keep the .name argument as an
	   automatic sequence counter, Thread-1, Thread-2, etc.).
	
	   The 'role' attribute is used by the loggingContext when it gets
	   initialized later on, when the thread uses it.  The purpose of
	   that is so that the thread role is available as a field that
	   can be displayed in log lines as specified in the logging format
	   string.

	   In addition to 'role', there's another optional initialization
	   keyword argument called 'component', the idea of which is to
	   identify which system component a given thread is currently
	   working on behalf of.  This is used similarly to 'role.'


			Public class attributes:
			------------------------

				ThreadActor.defaultRole:str			[public class attribute]

					This class attribute specifies the default role
					for new ThreadActor objects when the role is not
					otherwise specified.  The default value is just
					a placeholder role, "actor".  Subclasses should
					override this value.
				
				ThreadActor.defaultComponent:str	[public class attribute]

					This class attribute specifies the default compo-
					nent name for new ThreadActor objects when the
					component is not otherwise specified.  The default
					value is just a placeholder component name,
					"logdapp" denoting a general logged application.
					Subclasses should override this value.

				ThreadActor.defaultTarget:Callable	[public class attribute]

					This class attribute specifies the default method
					to be called when the thread is run, if not the
					normal .run() method.  The default value is None
					which specifies that .run() will be used.  Sub-
					classes may wish to override this value.


			Public instance attributes:
			---------------------------

				threadActor.role:str				[public instance attribute]

					The name of the role that this thread plays within
					the application.

				threadActor.component:str			[public instance attribute]

					The name of the system hardware or software compo-
					nent that this thread is running on behalf of."""

		#|======================================================================
		#|							(in class ThreadActor)
		#|		Class attributes.							[class code section]

			#----------------------------------------------------------
			# The following class attributes specify the default role
			# and component for newly-created ThreadActor objects when
			# they are not otherwise specified, and a default target
			# method for the thread (if not .run()).  Subclasses may
			# want to override these class attributes.

	defaultRole		 = 'actor'		 # The role of a ThreadActor is that it is an actor that has a role.
	defaultComponent = 'logdapp'	 # By default, new ThreadActors will be operating on behalf of a "logged application".
	defaultTarget	 = None			 # By default, just use the class's run() method, no other target.
	
		#|======================================================================
		#|							(in class ThreadActor)
		#|		Special instance methods.					[class code section]

			#|------------------------------------------------------------------
			#|
			#|	ThreadActor.__init__()				[special instance method]
			#|
			#|		Initialzer method for new ThreadActor instances.
			#|		Here, we override the default threading.Thread
			#|		initializer to process the new keyword arguments
			#|		<role> and <component> by storing their values in
			#|		attributes of this ThreadActor object.	Later
			#|		these values will get picked up by the thread's
			#|		LoggingContext for use in generating log lines.
		
	def __init__(inst, *args, role:str=None, component:str=None, target=None, **kwargs):

		"""Initialzer method for new ThreadActor instances.	 Here, we
		   override the default threading.Thread initializer to first
		   process the new keyword arguments <role> and <component> by
		   storing their values in attributes of this ThreadActor
		   object.	Later these values will get picked up by the
		   thread's LoggingContext for use in generating log lines.

				New keyword arguments:
				----------------------

					role:str								[keyword argument]

						The name of the role that this new thread will
						be playing in the application.	The default
						value of None results in the class's default
						role (stored in the .defaultRole class
						attribute) being used instead.

					component:str							[keyword argument]

						The name of the software or hardware component
						that this new thread is acting on behalf of.
						the default value of None results in the
						class's default component (stored in the
						.defaultComponent class attribute) being used
						instead."""

			#---------------------------------------------------------
			# If the parent thread has role and component attributes
			# set, use them (instead of class defaults) as the default
			# values for this new thread.  (Unless, of course, we're
			# running in a subclass of ThreadActor that is overriding
			# the parent class's role/component.)

		# First, find the parent thread...
		parent = threading.current_thread()
			#\_ The current thread, which this initializer for the
			#	newly-created thread object is being run in, will be
			#	the parent thread of the newly-created thread.
			
		if inst.defaultRole == 'actor' and hasattr(parent, 'role'):		# If our subclass's default role isn't customized, and our parent thread has a role,
			inst.defaultRole = parent.role								#	change our instance's default role to match our parent's role.
			
		if inst.defaultComponent == 'logdapp' and hasattr(parent, 'component'):		# If our subclass's default role isn't customized, and our parent thread has a role,
			inst.defaultComponent = parent.component								#	change our instance's default component to match our parent's component.

			#---------------------------------------------------------
			# If non-None values of the keyword arguments were not
			# provided, then instead, take their values from the class
			# defaults.	 This means that subclasses can define their
			# thread's role by simply overriding the .defaultRole
			# class variable.  Same for component.	And target.

		if		 role==None:		 role = inst.defaultRole
		if	component==None:	component = inst.defaultComponent
		if	   target==None:	   target = inst.defaultTarget

			#-------------------------------------------------------
			# Remember the role & component in instance attributes.
			
		inst.role		= role			# Initialize our .role instance attribute.
		inst.component	= component		# Initialize our .component instance attribute.

			#---------------------------------------------------------
			# Generate a debug-level diagnostic reflecting actor info.

		if doDebug:
			_moduleLogger.debug("ThreadActor.__init__(): Initialized a new "
								"ThreadActor instance with role [%s] for "
								"component [%s]..."
									 % (inst.role, inst.component))
		
		# NOTE: We can't actually update the thread-local logging
		# context yet at this point, because we're not actually
		# running within the newly-created thread yet!
		
			#---------------------------------------------------------
			# Finish with default initialization for Thread instances.
			
		threading.Thread.__init__(inst, *args, target=target, **kwargs)
		
	#__/ End ThreadActor.__init__().


			#|------------------------------------------------------------------
			#|
			#|	threadActor.__str__					[special instance method]
			#|
			#|		This special instance method returns a simple
			#|		string representation of the given object.	We
			#|		override the default implementation defined in
			#|		the threading.Thread class, and instead return
			#|		a string that gives both the thread's name and
			#|		its role.
		
	def __str__(inst):

		"""This special instance method returns a simple string
		   representation of the given object.	We override the
		   default implementation defined in the threading.Thread
		   class, and instead return a string that gives both the
		   thread's name and its role."""
		
		if hasattr(inst, 'role'):	# So this method will work for non-ThreadActor classes also.
			return "%s (%s)" % (inst.name, inst.role)
		else:
			return inst.name	# If role is unset, just return the name.
		
	#__/ End ThreadActor.__str__().


		#|======================================================================
		#|							(in class ThreadActor)
		#|		Public instance methods.					[class code section]

			#|------------------------------------------------------------------
			#|
			#|	threadActor.run()						[public instance method]
			#|
			#|		A thread calls its .run() method by default when
			#|		the thread starts.	Here, we override the default
			#|		.run() method inherited from threading.Thread so
			#|		as to initialize the thread's logging context
			#|		before doing anything else.	 It should only ever
			#|		be called from within the ThreadActor thread
			#|		itself! (If not, it raises a WrongThreadWarning.)
		
	def run(self, *args, **kwargs):		# May throw WrongThreadWarning.
			# \_ Run this method only from within the newly-created thread itself.

		"""A thread calls its .run() method by default when the thread starts.
		   Here in ThreadActor, we override the default .run() method inherited
		   from threading.Thread in order to initialize the thread's logging
		   context before doing anything else.	It should only ever be called
		   from within the ThreadActor thread itself!  (If not, it raises a
		   WrongThreadWarning.)"""
		
		self.starting();
			# Does ThreadActor-specific initialization here at the start of run().
			
		return threading.Thread.run(self, *args, **kwargs)
			# Dispatches to the default run() method for superclass threading.Thread().
	
	#__/ End ThreadActor.run().

			#|------------------------------------------------------------------
			#|
			#|	threadActor.starting()					[public instance method]
			#|
			#|		This method is for ThreadActor-specific initial-
			#|		ization to be done within the thread after the
			#|		thread starts.	It is called at the start of the
			#|		ThreadActor class's .run() method.	It may also
			#|		be called again later if needed.  It updates the
			#|		thread-local logging context to reflect initial or
			#|		newly-changed values of thread attributes.	It
			#|		should only ever be called from within the
			#|		ThreadActor thread itself! (If not, it raises a
			#|		WrongThreadWarning.)

	def starting(self):		# May throw WrongThreadWarning.
			# self="Run this method only from this thread, itself.

		"""This method is for ThreadActor-specific initialization to
		   be done within the thread after the thread starts.  It is
		   called at the start of the ThreadActor class's .run()
		   method.	It may also be called again later if needed.  It
		   updates the thread-local logging context to reflect initial
		   or newly-changed values of thread attributes.  It should
		   only ever be called from within the ThreadActor thread
		   itself!	(If not, it raises a WrongThreadWarning.)"""

			#-------------------------------------------------------
			# Make sure this method is being called from within the
			# thread represented by this ThreadActor object, itself.
			# If not, raise a warning.
		
		if self != threading.current_thread():

			errstr = ("ThreadActor.starting():	Can't execute "
					  ".starting() method of thread %s from within a "
					  "different thread %s!	 Ignoring request."
					  % (self, threading.current_thread()))

			raise WrongThreadWarning(errstr, logger=_moduleLogger)

			#[Previously, we just logged a warning and returned.
			# Is it better style to actually throw an exception?]
			#
			#_moduleLogger.warn(errstr)
			#
			#return	 # We don't even bother throwing a WarningException
			#	 # here, b/c our caller is just being a numbskull for
			#	 # calling us from the wrong thread, and so he probably
			#	 # wouldn't be prepared to catch the exception anyway.
				
		#__/ End if (in the wrong thread).

			#-------------------------------------------------------
			# If we get here, then we're in the right thread, so do
			# the actual work of updating the logging context.
		
		self.update_context()	# Update the logging context for this new thread

	#__/ End ThreadActor.starting().


			#|------------------------------------------------------------------
			#|
			#|	threadActor.update_context()			[public instance method]
			#|
			#|		This method updates the thread-local logging
			#|		context to reflect initial or newly-changed
			#|		values of thread attributes.  It should only
			#|		ever be called from within the ThreadActor
			#|		thread itself! (If not, it raises a
			#|		WrongThreadWarning.)
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def update_context(self):	# May throw WrongThreadWarning.
			# self="Run this method only from this thread, itself.

		"""This method updates the thread-local logging context to
		   reflect initial or newly-changed values of thread
		   attributes.	It should only ever be called from within
		   the ThreadActor thread itself! (If not, it raises a
		   WrongThreadWarning.)"""

			#-------------------------------------------------------
			# Make sure this method is being called from within the
			# thread represented by this ThreadActor object, itself.
			# If not, raise a warning.
			
		if self != threading.current_thread():

			errmsg = ("ThreadActor.update_context(): Can't update "
					  "logging context for thread %s from within a "
					  "different thread %s!	 Ignoring request."
					  % (self, threading.current_thread()))
			
			raise WrongThreadWarning(errmsg, logger=_moduleLogger)
		
			#[Previously, we just logged a warning and returned.
			# Is it better style to actually throw an exception?]
			#_moduleLogger.warn(errmsg)
			#return
			
		#__/ End if (in the wrong thread).

			#---------------------------------------------------
			# Generate a diagnostic log message at debug level.

		if doDebug:
			_moduleLogger.debug("ThreadActor.update_context(): Updating "
								"logging context to role [%s] & component"
								" [%s]..." % (self.role, self.component))

			#------------------------------------------
			# Now actually update the logging context.
		
		theLoggingContext.threadrole = self.role			 
		theLoggingContext.component	 = self.component	
			# \_ NOTE: theLoggingContext is a thread.local global, so
			#	 it differs for each thread.  Why did we not just
			#	 leave this information in thread attributes?  Because
			#	 LoggerAdapter wants an object that supports a dict-
			#	 like interface.  I suppose we could have stored such
			#	 an object as a single thread attribute, instead of a
			#	 thread-local global.  'Cuz you can always get hold of
			#	 it through threading.current_thread().	 Oh well.  Que
			#	 sera sera.
			
	#__/ End ThreadActor.update_context().

		#|===========================================================
		#| We should probably make the following two methods private 
		#| and build .role and .component properties on top of them. 
		#| That would be a little bit more elegant.	 Oh well.		 

			#|------------------------------------------------------------------
			#|
			#|	threadActor.set_role()					[public instance method]
			#|
			#|		Set the role of this ThreadActor to the given string.
			#|		May be called only from within the ThreadActor thread,
			#|		itself.	 If not, a WrongThreadWarning is raised.

	def set_role(self, role:str):	# May throw WrongThreadWarning.

		"""Set the role of this ThreadActor to the given string.  May
		   be called only from within the ThreadActor thread, itself.
		   If not, a WrongThreadWarning is raised."""
		
		if self != threading.current_thread():

			errmsg = ("ThreadActor.set_role(): Can't update logging "
					  "context for thread %s from within a different "
					  "thread %s!  Ignoring request." %
					  (self, threading.current_thread()))

			raise WrongThreadWarning(errmsg, logger=_moduleLogger)

			#_moduleLogger.warn(errmsg)
			#return
		
		#__/ End if (in the wrong thread).
		
		if doDebug:
			_moduleLogger.debug("ThreadActor.set_role(): Setting role to "
								"[%s] for this thread & its logging "
								"context." % role)
		
		self.role					 = role		# Provides for easy access.
		theLoggingContext.threadrole = role		# Also store it in the thread-local global LoggingContext.

	#__/ End ThreadActor.set_role().


			#|------------------------------------------------------------------
			#|
			#|	threadActor.set_component()				[public instance method]
			#|
			#|		Set the component of this ThreadActor to the given
			#|		string.	 May be called only from within the
			#|		ThreadActor thread, itself.	 If not, a
			#|		WrongThreadWarning is raised.

	def set_component(self, comp:str):	# May throw WrongThreadWarning.

		"""Set the component of this ThreadActor to the given string.
		   May be called only from within the ThreadActor thread,
		   itself.	If not, a WrongThreadWarning is raised."""
		
		if self != threading.current_thread():

			errmsg = ("ThreadActor.set_component(): Can't update "
					  "logging context for thread %s from within a "
					  "different thread %s!	 Ignoring request."
					  % (self, threading.current_thread()))
			
			raise WrongThreadWarning(errmsg, logger=_moduleLogger)
		
			#_moduleLogger.warn(errmsg)
			#return
		
		#__/ End if (in the wrong thread).

		if doDebug:
			_moduleLogger.debug("ThreadActor.set_component(): Setting "
								"component to [%s] for this thread & its "
								"logging context." % comp)
		
		self.component				= comp	# Provides for easy access.
		theLoggingContext.component = comp	# Also store it in the thread-local global LoggingContext.

	#__/ End ThreadActor.set_component().

#__/ End class ThreadActor.


			#|------------------------------------------------------------------
			#|
			#|	AbnormalFilter							   [module public class]
			#|
			#|		Subclass of Filter that only allows through log
			#|		messages that are not at NORMAL level.
			#|
			#|		This is used by our ConsoleHandler because NORMAL-
			#|		level messages appear anyway in the normal output
			#|		stream (on stdout) so it would be redundant to
			#|		display them again to stdout in the form of log
			#|		messages.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class AbnormalFilter(logging.Filter):

	"""Subclass of logging.Filter that only allows through log
	   messages that are not at NORMAL level.
			This is used by our ConsoleHandler, because NORMAL-level
	   messages appear anyway in the normal output stream (on stdout),
	   so it would be redundant to display them again to stdout in the
	   form of log messages"""
	
		# Override the filter() method.
	
	def filter(inst, record:logging.LogRecord):	  # Decide whether log record gets through this filter.

		"""This augments the default filter() method inherited from
		   logging.Filter to also filter out log messages that are at
		   NORMAL level."""
		
		return (record.levelno != NORMAL_LEVEL			# Evaluates as nonzero iff level is not NORMAL,
			and logging.Filter.filter(inst, record))	#	and also let our superclass's filter have a say.

	#__/ End AbnormalFilter.filter().
	
#__/ End class AbnormalFilter


			#|------------------------------------------------------------------
			#|
			#|	NormalLogger							   [module public class]
			#|
			#|		NormalLogger extends the logging.Logger class with
			#|		a new logging method normal(), which prints the
			#|		given message to sys.stdout as well as logging it.
			#|
			#|		Note that since loggers are instantiated by cal-
			#|		ling the logging.getLogger() function, rather than
			#|		by specifying the class explicitly, we have to
			#|		designate this as the new default logger class
			#|		using the logging.setLoggerClass() function, which
			#|		is done by logmaster.initLogMaster() when this
			#|		module is first loaded.
			#|
			#|		We also override the Logger._log() method with a
			#|		new version that allows the caller to optionally
			#|		pass the findCaller() result in directly.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class NormalLogger(logging.Logger):

	"""NormalLogger extends the logging.Logger class with a new log-
	   ging method normal(), which prints the given message to
	   sys.stdout as well as logging it.
			Note that since new loggers are instantiated by calling
	   the logging.getLogger() function, rather than by specifying the
	   class explicitly at instantiation time, we have to designate
	   the NormalLogger class as the new default logger class using
	   the logging.setLoggerClass() function, which is done by
	   logmaster.initLogMaster() when the logmaster module is first
	   loaded.
			We also override the Logger._log() method with a new ver-
	   sion that allows the caller to pass the findCaller() result in
	   directly."""

		#-------------------------------------------------------------
		# Override the logging.Logger class's .__init__() method.
		# The docstring for logging.setLoggerClass() tells us that we
		# need to define the .__init__() method of a new logger class
		# in this way.

	def __init__(inst, name:str):
		
		"""This version of the .__init__() method takes a name
		   argument but no level argument; this is what is expected by
		   the logging.setLoggerClass() function."""
		
		logging.Logger.__init__(inst, name)

	#__/ End NormalLogger.__init__().

		#-------------------------------------------------------------
		# Extend logging.Logger with new normal() method for printing
		# normal-level messages.
	
	def normal(inst, message:str, *args, caller=None, **kwargs):

		"""This special new logging method added by the NormalLogger
		   class prints the given message string to stdout before
		   then passing it on to the logging system for processing at
		   the new NORMAL logging level."""
		
		print(message, file=_outstr())
			# Print the message to our "normal" console output stream 
			# (this may or may not be the same as sys.stdout currently).
		
		if inst.isEnabledFor(NORMAL):
			if caller==None:								
				caller = mainLogger.logger.findCaller()
			inst.log(NORMAL, message, *args, caller=caller, **kwargs)  # Also log it via the active LogHandlers.
			
	#__/ End NormalLogger.normal().

		#-----------------------------------------------------------------------
		# Override Logger's standard logging methods to also find caller information.
	
	def debug(self, msg, *args, caller=None, **kwargs):
		if self.isEnabledFor(logging.DEBUG):
			if caller==None:								
				caller = mainLogger.logger.findCaller()
			self._log(logging.DEBUG, msg, args, caller=caller, **kwargs)

	def info(self, msg, *args, caller=None, **kwargs):
		if self.isEnabledFor(logging.INFO):
			if caller==None:								
				caller = mainLogger.logger.findCaller()
			self._log(logging.INFO, msg, args, caller=caller, **kwargs)

	def warning(self, msg, *args, caller=None, **kwargs):
		if self.isEnabledFor(logging.WARNING):
			if caller==None:								
				caller = mainLogger.logger.findCaller()
			self._log(logging.WARNING, msg, args, caller=caller, **kwargs)

	def error(self, msg, *args, caller=None, **kwargs):
		if self.isEnabledFor(logging.ERROR):
			if caller==None:								
				caller = mainLogger.logger.findCaller()
			self._log(logging.ERROR, msg, args, caller=caller, **kwargs)

	def critical(self, msg, *args, caller=None, **kwargs):
		if self.isEnabledFor(logging.CRITICAL):
			if caller==None:								
				caller = mainLogger.logger.findCaller()
			self._log(logging.CRITICAL, msg, args, caller=caller, **kwargs)

	fatal = critical	# Alternate name w. a different connotation.

		#-----------------------------------------------------------------------
		# Modify Logger's _log() method to take an additional kwarg "caller".
		
	def _log(self, level, msg, args, exc_info=None, extra=None, caller=None):
		
		global _srcfile
		
		"""This is a low-level logging routine which creates a
		   LogRecord and then calls all the handlers of this logger
		   to handle the record.  This version of the routine, defined
		   in the logging.NormalLogger class, adds a new keyword
		   argument <caller> to optionally specify the calling
		   function or method, instead of us looking it up here."""
		
		if caller != None:							# Was caller specified?
			fn, lno, func, *rest_ignored = caller	# Parse that tuple.
		else:
			if _srcfile:
				#IronPython doesn't track Python frames, so findCaller throws an
				#exception. We trap it here so that IronPython can use logging.
				try:
					fn, lno, func = self.findCaller()
				except ValueError:
					fn, lno, func = "(unknown file)", 0, "(unknown function)"
					if hasattr(appdefs,'topFile'): fn = appdefs.topFile
			else:
				fn, lno, func = "(unknown file)", 0, "(unknown function)"
				if hasattr(appdefs,'topFile'): fn = appdefs.topFile
				
			#__/ End if _srcfile... else...
				
		#_/ End if caller != None... else...

		#[Low-level diagnostic, currently commented out.]		
		#print("logging/__init__.py/Logger._log(): Got function: " + func.__str__() + "()",file=sys.stderr)
				
		if exc_info and not isinstance(exc_info, tuple):
			exc_info = sys.exc_info()
		#__/ End if exc_info is a non-tuple object.
			
		record = self.makeRecord(self.name, level, fn, lno, msg, args,
								 exc_info, func, extra)
		
		self.handle(record)
		
	#__/ End method NormalLogger._log().
		
#__/ End class NormalLogger.


			#|------------------------------------------------------------------
			#|
			#|	NormalLoggerAdapter						   [module public class]
			#|
			#|		Does for LoggerAdapter what NormalLogger does for
			#|		Logger.	 (Adds .normal() method and caller kwarg.)
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class NormalLoggerAdapter(logging.LoggerAdapter):

	"""The NormalLoggerAdapter class does for LoggerAdapter what
	   NormalLogger does for Logger. (Adds the .normal() method and
	   the <caller> kwarg.)"""
	
	@property
	def underlying(inst):
		return inst._underlying

	def normal(inst, msg:str, *args, caller=None, **kwargs):
		msg, kwargs = inst.process(msg, kwargs)
		if caller==None:								
			caller = mainLogger.logger.findCaller()
		inst.logger.normal(msg, *args, caller=caller, **kwargs)

	# Override LoggerAdapter's standard logging methods to also find caller information.
	
	def debug(self, msg, *args, caller=None, **kwargs):
		msg, kwargs = self.process(msg, kwargs)
		if caller==None:								
			caller = mainLogger.logger.findCaller()
		self.logger.debug(msg, *args, caller=caller, **kwargs)

	def info(self, msg, *args, caller=None, **kwargs):
		msg, kwargs = self.process(msg, kwargs)
		if caller==None:								
			caller = mainLogger.logger.findCaller()
		self.logger.info(msg, *args, caller=caller, **kwargs)

	def warning(self, msg, *args, caller=None, **kwargs):
		msg, kwargs = self.process(msg, kwargs)
		if caller==None:								
			caller = mainLogger.logger.findCaller()
		self.logger.warning(msg, *args, caller=caller, **kwargs)

	warn = warning		# Just a shorter name for convenience.

	def error(self, msg, *args, caller=None, **kwargs):
		msg, kwargs = self.process(msg, kwargs)
		if caller==None:								
			caller = mainLogger.logger.findCaller()
		self.logger.error(msg, *args, caller=caller, **kwargs)

	def critical(self, msg, *args, caller=None, **kwargs):
		msg, kwargs = self.process(msg, kwargs)
		if caller==None:								
			caller = mainLogger.logger.findCaller()
		self.logger.critical(msg, *args, caller=caller, **kwargs)

	def exception(self, msg, *args, caller=None, **kwargs):
		msg, kwargs = self.process(msg, kwargs)
		if caller==None:								
			caller = mainLogger.logger.findCaller()
		self.logger.exception(msg, *args, caller=caller, **kwargs)

	def FATAL(self, msg, *args, caller=None, **kwargs):
		msg, kwargs = self.process(msg, kwargs)
		if caller==None:								
			caller = mainLogger.logger.findCaller()
		self.logger.fatal(msg, *args, caller=caller, **kwargs)

#__/ End class NormalLoggerAdapter.


NormalLoggerAdapter.fatal = NormalLoggerAdapter.FATAL


		#|======================================================================
		#|
		#|	 3.3.  Private classes.						[module code subsection]
		#|
		#|		In this code section, we define private classes.
		#|		These are not exported from this module, and are
		#|		not intended to be referenced by other modules.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
			#|------------------------------------------------------------------
			#|
			#|	_NullOut								  [module private class]
			#|
			#|		This class implements an output stream similar to
			#|		Unix's "/dev/null" stream; it just silently does
			#|		nothing with text that is written to it.
			#|
			#|		We use this as a temporary implementation of
			#|		sys.stdout and sys.stderr in contexts where these
			#|		streams have not been defined, such as when
			#|		starting the script by double-clicking the ".pyw"
			#|		version of the program icon.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class _NullOut(io.TextIOBase):	# A simple class implementing a "null" output stream (i.e., bit-bucket).

	"""This class implements an output stream similar to Unix's
	   "/dev/null" stream; it absorbs and just silently does nothing
	   with text that is written to it.
			We use this as a temporary implementation of sys.stdout
	   and sys.stderr in contexts where these streams have not been
	   defined, such as when starting the script by double-clicking
	   the ".pyw" version of the program icon."""

	# Are these two methods enough, or do we need to implement a full set
	# of the empty abstract methods defined in io.TextIOBase or some such?

	def write(inst, s:str = "", *args, **kwargs):
		# Just return the length of the string, as if all characters were written.
		return len(s)
	
	def flush(inst, *args, **kwargs): pass	 # Flushing the stream?	 Do nothing.

#__/ End class _NullOut.
	

	#|==========================================================================
	#|	4.	Function definitions.						   [module code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	4.1.  Public function definitions.			[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|
			#|	setThreadRole(),					   [module public functions]
			#|	setThreadComponent()
			#|
			#|		Functions for setting the global, thread-local
			#|		"threadrole" and "component" attributes.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def setThreadRole(role:str):
	"Set the global (but thread-local) thread role attribute to the given name."
	thread = threading.current_thread()
	theLoggingContext.threadrole = thread.role = role

def setComponent(component:str):
	"Set the global (but thread-local) component attribute to the given name."
	thread = threading.current_thread()
	theLoggingContext.component = thread.component = component


			#|------------------------------------------------------------------
			#|
			#|	getLogger()								[module public function]
			#|
			#|		Gets a Logger (or LoggerAdapter) object for use by
			#|		the using module.  Makes sure that the logger that
			#|		is obtained supports our new normal() method.
			#|		Wraps a NormalLoggerAdapter around the provided
			#|		logger, which has the effect of including in the
			#|		log record the extra thread-local information from
			#|		our global (but thread-local) LoggingContext.
			#|
			#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def getLogger(name:str = appName):

	"""Gets a Logger (or LoggerAdapter) object for use by the using
	   module.	Makes sure that the logger that is obtained supports
	   our new normal() method.	 Wraps a NormalLoggerAdapter around
	   the provided logger, which has the effect of including in the
	   log record the extra thread-local information from our global
	   (but thread-local) LoggingContext object."""

		#-----------------------------------------------------------------------
		# Use the ordinary logging facility to get the underlying logger.  This
		# will be a NormalLogger instead of a logging.Logger, b/c of the call
		# to logging.setLoggerClass() in initLogMaster().
		
	logger = logging.getLogger(name)
		
		#-----------------------------------------------------------------------
		# Wraps a NormalLoggerAdapter with the extra LoggingContext information
		# around the logger that was returned by logging.getLogger().  Remember,
		# the global LoggingContext object has thread-local content.
		
	wrapped_logger = NormalLoggerAdapter(logger, theLoggingContext)
	wrapped_logger._underlying = logger
	
	return	wrapped_logger		# Return that wrapped-up logger.

#__/ End function getLogger().


			#|------------------------------------------------------------------
			#|
			#|	getComponentLogger()					[module public function]
			#|
			#|		Gets a Logger (or LoggerAdapter) for use by the named
			#|		software or system component.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def getComponentLogger(component:str):

	"""Gets a Logger (or LoggerAdapter) object specific to a given
	   software component or system component, designated by a short
	   string identifier.  For software components that correspond to
	   Python packages, normally the component name is the same as the
	   package name.  The package's __init__.py file may obtain this
	   string using the code:
	   
					from os	import path
					...
					_component = path.basename(__path__[0])
					  
	   Note that the name of the logger created by this call is
	   <sysName>.<appName>.<component>, which is a hierarchical logger 
	   name.  Thus messages sent to this logger will also be passed up 
	   to the application logger, named '<sysName>.<appName>' and to 
	   the top-level system logger, named <sysName>."""

	# Could do some error checking here to make sure <component>
	# is really a string (or convert it to a string).

	return getLogger(appName + '.' + component)

#__/ End function getComponentLogger().

	
			#|------------------------------------------------------------------
			#|
			#|	normal(), debug(), info(),			   [module public functions]
			#|	warning(), warn(), error(),
			#|	exception(), critical(),
			#|	fatal(), FATAL()
			#|
			#|		Concise logging functions.	For modules that use
			#|		the mainLogger for logging, these functions
			#|		provide for logging more concisely than by
			#|		explicitly invoking the logger.
			#|			Note that warn() is just a shorter name for
			#|		warning(), and that fatal() is just an alternate
			#|		name for critical() that connotes that program
			#|		termination is expected.  FATAL() is just a name
			#|		for fatal() that stands out more in the code.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
def normal(msg:str, *args, **kwargs):
	"""Logs the given message at NORMAL level using the global
	   logmaster.mainLogger (and also sends it to standard output)."""
	caller = mainLogger.logger.findCaller()
	mainLogger.normal(msg, *args, caller=caller, **kwargs)

	
def debug(msg:str, *args, **kwargs):
	"Logs the given message at DEBUG level using logmaster.mainLogger."
	caller = mainLogger.logger.findCaller()
	#print("Got caller: (%s, %d, %s)" % caller, file=sys.stdout)
	mainLogger.debug(msg, *args, caller=caller, **kwargs)


def info(msg:str, *args, **kwargs):
	"Logs the given message at INFO level using logmaster.mainLogger."
	caller = mainLogger.logger.findCaller()
	#print("Got caller: (%s, %d, %s)" % caller, file=sys.stdout)
	mainLogger.info(msg, *args, caller=caller, **kwargs)


def warning(msg:str, *args, **kwargs):
	"Logs the given message at WARNING level using logmaster.mainLogger."
	caller = mainLogger.logger.findCaller()
	mainLogger.warning(msg, *args, caller=caller, **kwargs)

warn = warning		# Serves as a shorter synonym.


def error(msg:str, *args, **kwargs):
	"Logs the given message at ERROR level using logmaster.mainLogger."
	caller = mainLogger.logger.findCaller()
	mainLogger.error(msg, *args, caller=caller, **kwargs)


def exception(msg:str, *args, **kwargs):
	
	"""Logs the given message at ERROR level using logmaster.mainLogger,
	   and also output exception information to standard error."""
	
	caller = mainLogger.logger.findCaller()

		# We surround the traceback above and below with "vvvv", "^^^^"
		# delimiter lines, to set it off from other output.
	
	errstrm = _errstr()

	print("v"*70,file=errstrm)		
	mainLogger.exception(msg, *args, caller=caller, **kwargs)
	print("^"*70,file=errstrm)
			#- WARNING:	 The above code may do weird things (specifically,
			#	print the delimiters in one place and the traceback in
			#	another) if the console is shutting down and logging is being
			#	temporarily redirected to somewhere other than sys.stderr.
			
#__/ End function exception().


def critical(msg:str, *args, **kwargs):
	"Logs the given message at ERROR level using logmaster.mainLogger."
	caller = mainLogger.logger.findCaller()
	mainLogger.critical(msg, *args, caller=caller, **kwargs)

fatal = critical	# Same effect, different connotation.
FATAL = fatal		# Alternate name with more emphasis.


			#|------------------------------------------------------------------
			#|
			#|	lvlname_to_loglevel()					[module public function]
			#|
			#|		This function simply converts the string name of a
			#|		given logging level to its numeric equivalent.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def lvlname_to_loglevel(lvlname):
	
	"""This function simply converts the string name of a given
	   logging level to its numeric equivalent."""
	
	# We use the logging._levelNames dictionary b/c it already
	# has the reverse mappings as well as the forward ones.
	if lvlname in logging._levelNames.keys():	
		return logging._levelNames[lvlname]
	else:
		if doErr:
			_moduleLogger.error("There is no logging level named '%s'." % lvlname)
		return NOTSET	# This is the default value, if not otherwise set.
			#	 \__ This is assigned to logging.NOTSET earlier in the file.


			#|------------------------------------------------------------------
			#|
			#|	byname()								[module public function]
			#|
			#|		This simply generates a log message using the main
			#|		logger and the string name of the desired logging
			#|		level.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def byname(lvlname, msg):
	"""This simply generates a log message using the main logger and
	   the string name of the desired logging level."""
	caller = mainLogger.logger.findCaller()
	loglevel = lvlname_to_loglevel(lvlname)
	mainLogger.log(loglevel, msg, caller=caller)


			#|------------------------------------------------------------------
			#|
			#|	testLogging()							[module public function]
			#|
			#|		Tests the logging facility for various message
			#|		types.	The initLogMaster() function, defined
			#|		below, should already have been called.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def testLogging():
	
	"""Tests the logging facility for various message types using the
	   logmaster module's logger.  The initLogMaster() function should
	   already have been called."""
	
	_moduleLogger.debug	  ('This message just verifies that debug-level log output is enabled for this stream.')
	_moduleLogger.info	  ('This message just verifies that info-level log output is enabled for this stream.')
	_moduleLogger.normal  ('This message just verifies that normal-level log output is enabled for this stream.')
	_moduleLogger.warning ('This message just verifies that warning-level log output is enabled for this stream.')	  
	# Maybe shouldn't test these two b/c they look unnecessarily panicky & are always enabled anyway?
	_moduleLogger.error	  ('This message just verifies that error-level log output is enabled for this stream.')
	_moduleLogger.critical('This message just verifies that critical-level log output is enabled for this stream.')

#__/ End function testLogging().


			#|------------------------------------------------------------------
			#|
			#|	updateStderr()							[module public function]
			#|
			#|		In case the definition of sys.stderr changes, this
			#|		function retrieves its new definition for use by
			#|		the console output log handler (if that has been
			#|		defined).
			#|
			#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def updateStderr(new_errstrm=None):

	"""In case the definition of sys.stderr changes, this function
	   retrieves its new definition for use by the console output log
	   handler (if that has been defined)."""

	global consHandler

	if new_errstrm is None:
		new_errstrm = sys.stderr

	# The locking here prevents another thread from putting some
	# more output to the console handler after we flush it, and
	# before we redirect its stream.  Or from nulling out the
	# consHandler global after we check it and before we use it.
	logging._acquireLock()	
	if consHandler:

		consHandler.flush()
		consHandler.stream = new_errstrm

		# mainLogger.underlying.removeHandler(consHandler)
		
		# consHandler = logging.StreamHandler(stream=new_errstrm)
		# consHandler.addFilter(AbnormalFilter())	   # Add a filter to ignore NORMAL-level messages.
		# consHandler.setLevel(console_level)		   # Set console to log level we determined earlier.

		# # Console log messages will just have the simple format showing the log
		# # level name and the actual log message.	Look at the log file to see
		# # more details such as thread info, module, and function.

		# consHandler.setFormatter(logging.Formatter("%(levelname)8s: %(message)s"))

		# # Add the console log handler to the main logger adapter's underlying logger.

		# mainLogger.logger.addHandler(consHandler)

		
		#consHandler.setStream(new_errstrm)

	logging._releaseLock()
	

			#|------------------------------------------------------------------
			#|
			#|	setLogLevels()							[module public function]
			#|
			#|		Set up the file and console logging levels based
			#|		on various configuration Booleans.	Prints some
			#|		diagnostic information to stdout if argument
			#|		<verbose> is True.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def setLogLevels(verbose=False):
	
	"""Sets up the file and console logging levels based on various
	   configuration Booleans.	Prints some diagnostic information
	   to stdout if argument <verbose> is True."""
	
	global console_level, log_level
	
		# Set the log level for the console based on whether we want to see warnings or not,
		# and whether the console is in debug mode.
		
	console_level = logging.WARNING		# Default setting.
	if CONS_DEBUG:
		if verbose:
			print("logmaster.setLogLevels(): Turning on detailed debug messages on console...",
				  file=sys.stderr)
		console_level = logging.DEBUG
	elif CONS_INFO:
		if verbose:
			print("logmaster.setLogLevels(): Turning on informational messages on console...",
				  file=sys.stderr)
		console_level = logging.INFO
	else:
		if not CONS_WARN:
			if verbose:
				print("logmaster.setLogLevels(): Suppressing warnings from console...",
					  file=sys.stderr)
			console_level = logging.ERROR
	if verbose:
		print("logmaster.setLogLevels(): Console log level is set to %d (%s)." %
			  (console_level, logging.getLevelName(console_level)),
			  file=sys.stderr)

		# Set the log level for the log file based on whether we want to log verbose info or not,
		# and whether the main logger is in debug mode.

	log_level = logging.INFO	# Default setting.
	if LOG_DEBUG:
		if verbose:
			print("logmaster.setLogLevels(): Turning on detailed debug messages in log file...",
				  file=sys.stderr)
		log_level = logging.DEBUG
		if not LOG_INFO:
			if verbose:
				print("logmaster.setLogLevels(): Suppressing verbose info from log file...",
					  file=sys.stderr)
			log_level = logging.NORMAL
	if verbose:
		print("logmaster.setLogLevels(): File log level is set to %d (%s)." %
			  (log_level, logging.getLevelName(log_level)),
			  file=sys.stderr)

	_noticeLevels()

#__/ End setLogLevels().


			#|------------------------------------------------------------------
			#|
			#|	initLogMaster()								[public function]
			#|
			#|		Basic initialization of the logmaster facility,
			#|		called whenever this module is first loaded.
			#|		Can also be re-called when desired to
			#|		re-initialize the module.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def initLogMaster(out=None, err=None):
	# If out and err are provided, they are used instead of stdout/stderr.

	"""Do basic initialization of the logmaster facility.  This
	   routine is called whenever the logmaster module is first
	   loaded.	It can also be re-called when desired to re-
	   initialize the module."""
	
	global logFormatter, theLoggingContext, mainLogger	   # In python, we have to declare
	global consHandler, _moduleLogger, _initialized		  # the globals that we'll reassign.
	global sysLogger, appLogger

	if out is not None:
		set_alt_stdout(out)

	if err is not None:
		set_alt_stderr(out)

			#|==================================================================
			#|
			#|	 Install hacks to some standard modules. [unorthodox code block]
			#|
			#|		The following code modifies some standard Python
			#|		modules in an "unauthorized" way to get the
			#|		functionality that we want.	 This is rather
			#|		inelegant, but it works....
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# Modify the real Thread class's .__str__() method to take advantage
		# of the role attribute even for non-ThreadActor classes, as long
		# as the attribute exists.

	threading.Thread.__str__ = ThreadActor.__str__

		# Pretend that the main thread is a ThreadActor by giving it a "role"
		# attribute.  This is descriptive, for debugging purposes.	  

	_setDefaultRole()

		# Modify Python's logging module to change how it determines the
		# stack frame of user code.	 This is necessary because we are
		# adding an additional level of indirection to logging calls.

	logging.currentframe = _currentframe	 # Replace logging's currentframe() method.

			#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			#|	End of hacks to standard modules.
			#|==================================================================

		# If we have no stdout/stderr streams yet (which will be the case
		# if the program was started by, for example, just double-clicking
		# on a script.pyw icon), temporarily assign them to null output
		# streams, just to make sure we won't crash if someone tries
		# to send log messages to the console before more effective values
		# of stdout/stderr have been set up.

	if sys.stdout == None:	 sys.stdout = _NullOut()
	if sys.stderr == None:	 sys.stderr = _NullOut()
		
		# Define a new logging level for "normal" messages that should be
		# echoed (without decoration) to standard output.  The level of this
		# is in between ERROR and WARNING, so that warnings can be suppressed
		# without suppressing normal output.

	logging.addLevelName(NORMAL_LEVEL,'NORMAL')
	logging.NORMAL = NORMAL_LEVEL

		# Create our main log file formatter.  This may be useful for
		# creating file log handlers in subordinate loggers that use
		# the same file format as the main file log handler.  This can
		# be changed if needed in a later call to configLogMaster().
		# (Note: Changing the logFormatter is not yet implemented.)
	cleanFormatter = CleanFormatter(LOG_FORMATSTR)
	logFormatter = cleanFormatter
			# - LOG_FORMATSTR will be our normal log message format.

		# Create our log handler which uses our custom formatter.
		# Note that this sets the absolute path to the log file based
		# on the current directory AT THE TIME THAT THE LOGMASTER MODULE
		# IS FIRST LOADED.
		
	cleanHandler = logging.FileHandler(LOG_FILENAME, 'a')
	cleanHandler.setFormatter(cleanFormatter)

		# Set the default console and file logging levels based on the
		# module defaults.	(Don't print debug info since this is just
		# the default setting anyway.)

	setLogLevels(verbose=False)		   

		# Set the default log file name, and its log level & format.
		# With the initial defaults, the log file will just contain
		# messages at INFO level or higher (no DEBUG).	To change
		# this, use configLogMaster().
		
	logging.basicConfig(level=log_level,
						format=LOG_FORMATSTR,
						handlers=[cleanHandler])

		# Create the global loggingContext object.	This is thread-local, and
		# does not get initialized for a given thread until it is actually
		# first accessed within that thread.

	theLoggingContext = LoggingContext()   

		# Tell the logging module to please use our custom NormalLogger
		# class (instead of the default logging.Logger class) when
		# generating new loggers.

	logging.setLoggerClass(NormalLogger)

		# Get the main (root) logger object for this environment.  Note this
		# uses our special getLogger() method defined above, which actually
		# creates a NormalLoggerAdapter wrapped around a NormalLogger.	We
		# don't use appName as the logger name here, because we want modules
		# that are not even application-specific to still go through this
		# logger.
	
	mainLogger = getLogger('')

		# Add a console log handler for messages (other than NORMAL messages)
		# that are (typically) at warning level or higher.	This will ensure
		# that these messages also appear on the stdout/stderr console.
	
	errstrm = _errstr()

	consHandler = logging.StreamHandler(stream=errstrm)	   # The default stream handler uses stderr.
	consHandler.addFilter(AbnormalFilter())	   # Add a filter to ignore NORMAL-level messages.
	consHandler.setLevel(console_level)		   # Set console to log level we determined earlier.

		# Console log messages will just have the simple format showing the log
		# level name and the actual log message.  Look at the log file to see
		# more details such as thread info, module, and function.

	consHandler.setFormatter(logging.Formatter("%(levelname)8s: %(message)s"))

		# Add the console log handler to the main logger adapter's underlying logger.

	mainLogger.logger.addHandler(consHandler)

		# Create a subordinate logger that is the top-level logger for system components.
	
	sysLogger = getLogger(sysName)

		# Create a subordinate logger that is the top-level logger for application components.

	appLogger = getLogger(appName)		  

		# Get a subordinate logger for use by routines in this module.
		# Note that hierarchically, this logger is parallel to, not
		# under the system logger.	(However, it's still under the main
		# logger.)

	_moduleLogger = getLogger('logmaster')	  # For messages produced by this module only.

		# Remember that this module has already been initialized, to
		# make sure we don't try to initialize it again.

	_initialized = True

#__/ End initLogMaster().
		

			#|------------------------------------------------------------------
			#|
			#|	configLogMaster()						[module public function]
			#|
			#|		Configures the logmaster facility.	Optional
			#|		arguments can be used to modify various logmaster
			#|		parameters from their preprogrammed defaults.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def configLogMaster(sysname:str = None, appname:str = None,
					filename:str = None, formatstr:str = None,
					conswarn:bool = None, consdebug:bool = None,
					consinfo:bool = None, loginfo:bool = None,
					logdebug:bool = None, component:str = None,
					role:str = None):

	"""Configures the logmaster facility.  Optional keyword arguments
	   can be used, if desired, to modify various logmaster parameters
	   from their preprogrammed defaults."""

		# Do I really need to re-declare all these globals despite the
		# global statements at top level above?
	
	global NORMAL_LEVEL
	global LOG_FILENAME, LOG_FORMATSTR
	global CONS_WARN, LOG_INFO, LOG_DEBUG, CONS_DEBUG, CONS_INFO
	global systemName, sysName, appName
	global logFormatter, theLoggingContext, mainLogger, _moduleLogger
	global _initialized, consHandler
	global sysLogger, appLogger

		# Reinitialize some globals, if requested, in optional args.
		
	if sysname:
		sysName = systemName = sysname
		appdefs.systemName = sysname  # In case someone imports appdefs later.
			#-Warning: Other modules that have already imported
			# names from appdefs will still have the old value of
			# systemName in their module's copy of this global.

	if appname:
		appName = appname
		appdefs.appName = appname	# In case someone imports appdefs later.
			#-Warning: Other modules that have already imported
			# names from appdefs will still have the old value of
			# appName in their module's copy of this global.
		LOG_FILENAME = 'log/' + appName + ".log"
		
	if filename:			LOG_FILENAME					= filename
	if formatstr:			LOG_FORMATSTR					= formatstr
	if conswarn	 != None:	CONS_WARN						= conswarn		  # Note:  False != None.
	if consinfo	 != None:	CONS_INFO						= consinfo
	if consdebug != None:	CONS_DEBUG						= consdebug
	if loginfo	 != None:	LOG_INFO						= loginfo
	if logdebug	 != None:	LOG_DEBUG						= logdebug
	if component != None:	theLoggingContext.component		= component
	if role		 != None:	theLoggingContext.threadrole	= role

	if _RAW_DEBUG: 
		print("logmaster.configLogMaster(): The top-level log file is %s." % LOG_FILENAME,
			  file=sys.stderr)

		# Start by appending a header to the log file for better
		# human-readability.  NOTE: Currently this has to be manually
		# adjusted in accordance with the log-format string defined
		# above.  There must be a better way???

	with open(LOG_FILENAME,'a') as tmp_file:
	 tmp_file.write(
	  "========================+==========================+======================================+===========================================+===========================================================================================\n"
	  "YYYY-MM-DD hh:mm:ss,msc | SysName.appName.pkgName  | ThreadName:		 Component role		 | srcModuleName.py:ln# : functionName()	 | LOGLEVEL: Message text\n"
	  "------------------------+--------------------------+--------------------------------------+-------------------------------------------+-------------------------------------------------------------------------------------------\n")

		# Figure out the file and console log levels based on user
		# selections.  (Verbose in this call is turned on for now,
		# to confirm the final post-config level settings to stderr.)

	setLogLevels(verbose=_RAW_DEBUG)

		# Update the root log file name, logging level, and format.
		# NOTE: So far this only changes the logging level.	 More
		# research into guts of logging module needed to figure out
		# how to surgically alter the log file name and log format
		# after the main root log file handler has already been
		# created.
		
	mainLogger.logger.setLevel(log_level)

		# Update the console log handler's logging level.

	consHandler.setLevel(console_level)		   # Set console to log level we determined earlier.

	#testLogging()		# Don't do this normally.

#__/ End configLogMaster().


		#|======================================================================
		#|
		#|	4.2.  Private function definitions.			[module code subsection]
		#|
		#|			This code section defines module-level functions that
		#|			are used internally by this module but that are not
		#|			supposed to be used by other modules.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|
			#|		_currentframe()					   [module private function]
			#|
			#|			This version of _currentframe() actually
			#|			returns the stack frame two levels above the
			#|			real current one, because this will be the
			#|			point in the user code where some logging
			#|			method is being called.
			#|
			#|			This is a very hacky implementation borrowed
			#|			from the inspect.py module in Python 1.5.2.
			#|			It might be good to figure out a better way...
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _currentframe():
	"""Return the frame object for the caller's stack frame."""
	try:
		raise Exception
	except:
		return sys.exc_info()[2].tb_frame

if hasattr(sys, '_getframe'):
	_currentframe = lambda: sys._getframe(2)
	

			#|------------------------------------------------------------------
			#|
			#|	_limitLength(s:str, limit:int)->str			  [private function]
			#|
			#|			Given a string <s> and an integer <limit>,
			#|			return a version of <s> that is limited to
			#|			be at most <limit> characters in length,
			#|			interposing ".." if needed to represent
			#|			any elided characters near the end of the
			#|			string.
			#|
			#|			This function is used by CleanFormatter
			#|			to generate log output that fits neatly
			#|			in the available field widths.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _limitLength(s:str, limit:int) -> str:
	if len(s) > limit:
		newstr = s[0:limit-4] + '..' +s[-2:]
		#print("Limiting length of string [%s] to [%s] (%d chars)" % (s, newstr, limit))
		return newstr
	else:
		return s


			#|------------------------------------------------------------------
			#|
			#|	_setDefaultRole()							  [private function]
			#|
			#|		If we're in the MainThread, and it has no "role"
			#|		attribute assigned yet, or if its role is None,
			#|		give it a default role called "general".  Also,
			#|		make its .__str__() method like ThreadActor's.
			#|		If we're in another thread, this does nothing.
			#|
			#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _setDefaultRole():
	
	"""If we're in the MainThread, and it has no "role" attribute
	   assigned yet, or if its role is None, give it a default role
	   called "general".  Also, make its .__str__() method like
	   ThreadActor's.  If we're in another thread, does nothing."""
	
	thread = threading.current_thread()								# Get the current thread.
	if thread.name == "MainThread":									# If we're in the main thread,
		if not hasattr(thread, "role") or thread.role == None:			 # and it has no role assigned yet,
			thread.role = "general"											# assign it a generic role.
		# The main thread's __str__() method also does something
		# ugly.	 Fix it up by replacing it with ThreadActor's method.
		thread.__str__ = lambda: ThreadActor.__str__(thread)
	
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getLoggerInfo(moduleFilename):
	"""
	getLoggerInfo()													  [function]
	
		Modules can call getLoggerInfo(__file__) to get back a tuple
	
								(logger, component)
						
		where <logger> is a logger with the path <sysName>.<appName>.<pkgName>
		where <sysName> is the system name (from the appdefs module), <appName>
		is the application name (also from appdefs), and <pkgName> is the (last 
		part of) the name of the package containing the current file; that is, 
		it's a dedicated logger for the package <pkgName>.	Meanwhile, <component>
		is a dotted name for the current "software component;" this is just 
		<sysName>.<pkgName>.  This can be used as the .defaultComponent attribute
		of ThreadActor subclasses defined within the module.
	
	EXAMPLE USAGE:
	
			global _logger		# Logger for this module.
			global _component	# Software component name, as <sysName>.<pkgName>.
			
			(_logger, _component) = getLoggerInfo(__file__)		# Fill in globals.
	
			...
			
			class MyThread(ThreadActor):
			
				defaultRole = 'play god'	# To appear in thread's log records.

					#------------------------------------------------------------
					# Set this class variable to fill in the component parameter
					# automatically in all log records generated by this thread.				
					
				defaultComponent = _component		
						# Use value obtained earlier from getLoggerInfo().
				
				def myMethod(thread):
					_logger.debug("Here I am!")		# Log record automatically includes package name.
					...
	"""
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| First, get the name of the package that the specified file is in.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	packageName = path.basename(path.dirname(moduleFilename))
			# The last component of the name of the directory that the
			# given file is in, in the name of this file's package.

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Next, get a component logger (treed under the application logger)
		#| for the caller's package.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	logger = getComponentLogger(packageName)
			# This is a logger whose path is <sysName>.<appName>.<pkgName>

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Finally, construct the component name for the caller's package.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	swComponent = sysName + '.' + packageName	# Just <sysName>.<pkgName.

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Return the results to the caller.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	return (logger, swComponent)
	
#__/ End module function logmaster.getLoggerInfo().

	#|--------------------------------------------------------------------------
	#|
	#|	5.	Module initialization.						   [module code section]
	#|
	#|		In this section, we have initialization code for the
	#|		logmaster module, which is supposed to be executed
	#|		whenever this module is first loaded.  Normally, a given
	#|		module will only be loaded once anyway per python
	#|		interprer session.	But, we check and set our
	#|		"_initialized" flag anyway,to make extra sure we don't
	#|		accidentally re-initialize the module.	(To intentionally
	#|		reinitialize it, users can explicitly call
	#|		logmaster.initLogMaster() for themselves.)
	#
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

if not _initialized:	 # If the module is not already initialized,
	#if hasattr(sys, "stderr") and sys.stderr != None:	 # Needed b/c in some environments, it's not defined!
	#	 print("logmaster.py: Initializing logmaster module...", file=sys.stderr)
	initLogMaster()			# then initialize it.

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#	End of infrastructure/logmaster.py module.
#===============================================================================
