#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 display/threads.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		display/threads.py				 [Python module source file]
	
	MODULE NAME:	display.threads
	IN PACKAGE:		display
	FULL PATH:		$GIT_ROOT/GLaDOS/src/display/threads.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.display (Display screen management)


	MODULE DESCRIPTION:
	===================
	
		This module defines two different, special threads that are 
		associated with operating the text terminal display:
		
			TUI_Input_Thread - A thread that is responsible for obtaining
								and dispatching on input from the user.

			DisplayDriver	- A worker thread that handles display output.
								Specifically, it executes all key handlers.
								Other threads may also asynchronously send 
								it output requests.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|
	#|	1.  Exported name list. 		   				   [module code section]
	#|
	#|			Here we list all of the public names that are standardly
	#|			exported from this module, if the using module does:
	#|
	#|						from display import *
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
global __all__ 
__all__ = [		# List of all public names exported from this module.

			#|----------------
			#| Thread classes.
		
		'TUI_Input_Thread', 	# Thread for running main TUI input loop.
		
		'DisplayDriver',		# Thread for performing display operations.
		
			#|-----------
			#| Functions.
			
		'in_driver_thread',		# Returns True if called in the display driver.
		
	]


	#|==========================================================================
	#| 	2.	Imports.									   [module code section]
	#|
	#|		2.1.  Standard Python modules imported into this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from os	import path 			# Manipulate filesystem path strings.


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	2.2.  Custom imports.						[module code subsection]
		#|
		#|		Here we import various local/application-specific 
		#|		modules that we need.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.worklist	import	RPCWorker	# Display driver uses this.

			#|------------------------
			#| Logging-related stuff.

from infrastructure.logmaster import (
		sysName,			# Used just below.
		ThreadActor,		# TUI input thread uses this.
		getComponentLogger,	# Used just below.
	)
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.
global _sw_component
_sw_component = sysName + '.' + _component


from .exceptions import (
		DisplayNotRunning,	# Returned by display driver if display is not running.
	)

	#|==========================================================================
	#|	3. Thread definitions.							   [module code section]
	#|
	#|		In this section, we define the threads that are provided by 
	#|		this module.  These include the following two threads:
	#|
	#|
	#|			TUI_Input	- Input thread for the Text User Interface.
	#|
	#|			DisplDrvr	- Display driver thread for the TUI.
	#|
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|----------------------------------------------------------------------
		#|	TUI_Input									  [module public thread]
		#|
		#|		This thread is created and started up automatically by 
		#|		the display.start() method.  It immediately executes 
		#|		the display.run() method, which brings up curses and
		#|		calls the display._manage() method, which sets up the
		#|		display and enters the main input loop, which repeatedly
		#|		obtains input events (keypresses or resize events) and
		#|		dispatches to the appropriate event handlers.  
		#|
		#|		Keypress handlers, however, are handed off to the display
		#|		driver thread (see below) for execution; this allows them
		#|		to be interleaved with other display-related tasks that 
		#|		may be asynchronously requested by other threads.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class TUI_Input_Thread(ThreadActor):
	"""This thread exists for the sole purpose of executing the main
		user input loop for the curses-based 'TUI' (Text User Interface).
		It communicates with the display driver thread to carry out I/O.
		"""
		
	defaultRole			= 'TUI_Input'
	defaultComponent	= _sw_component 
	
	def __init__(newTuiInputThread, *args, **kwargs):
		thread = newTuiInputThread
		thread.exitRequested = False		# Set this to True if you want this thread to quit.
		super(TUI_Input_Thread, thread).__init__(*args, **kwargs)	# ThreadActor initialization.

#__/ End module public thread class TUI_Input_Thread.


		#|----------------------------------------------------------------------
		#|	DisplDrvr								  	  [module public thread]
		#|
		#|		This thread is created and started up automatically by 
		#|		the instance initializer for the singleton instance of
		#|		the 'TheDisplay' class.  It is a subclass of RPCWorker
		#|		(see infrastructure/worklist.py), which means that, if
		#|		passed a callable, it evaluates it and returns a result.  
		#|		Alternatively, one can call its '.do()' method to hand 
		#|		it a task to run asynchronously in the background.  Tasks
		#|		are normally executed first-come, first serve.
		#|
		#|		The display driver thread is invoked by the main loop to
		#|		handle all keypress events.  It may also be called by 
		#|		other asynchronously running threads, GLaDOS processes, 
		#|		and GLaDOS subsystems to update the display as needed.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global _theDisplayDriver	# Global object for the unique display driver thread.
_theDisplayDriver = None	# The display driver thread has not yet been created.

class TheDisplay: pass	# Forward declaration for type hints.

			#|------------------------------------------------------------------
			#|	DisplayDriver							   [module public class]
			#|
			#|		Class to implement a thread that exists for the 
			#|		purpose of serializing curses operations.  While
			#|		the display is running, whenever you want to do 
			#|		something with the display, you can do it as 
			#|		follows:
			#|
			#|				dispDrvr = display.driver
			#|
			#|				...
			#|
			#|				dispDrvr(callable, desc="Do bla bla bla")
			#|
			#|		 				- or -
			#|
			#|				dispDrvr.do(callable)	# Runs in background.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class DisplayDriver(RPCWorker):
	#______________/         \_____________________________________________
	#| NOTE: By subclassing this class from RPCWorker instead of Worker, 
	#| the overall effect is simply to serialize all of the normal display 
	#| operations by having them wait for this single thread to do them.  
	#| However, users can also delegate operations to the driver to do as
	#| background activities without waiting for completion by calling the 
	#| driver's .do() method.
	#|---------------------------------------------------------------------
	
	def withLock(thisDriver, callable):
	
		"""This is a wrapper function that is to be automatically applied 
			around all bare callables that are handed to the display driver 
			as tasks to be executed. It simply grabs the display lock, so 
			that we avoid conflicting with any other threads that may be 
			using the display.  (We do this because we assume that in general
			curses operations are not thread-safe.)"""
		
		driver = thisDriver
		display = driver._display
		
		# NOTE: Debug messages are suppressed currently to avoid excessive logging.
		#_logger.debug("About to grab display lock...")
		with display.lock:

			# Note we grab the lock before checking the running state, since 
			# asynchronous operations might affect the running state of the display.
			if not display.running:
				#_logger.warn("displayDriver.withLock(): Display not running; ignoring task.")
				return DisplayNotRunning("displayDriver.withLock(): Display not running; task ignored.")
				# Note: Callers who obtain a result should be prepared to handle results of this type.

			#_logger.debug("About to call wrapped callable...")
			return callable()				# Call the callable, return any result.
			#_logger.debug("Returned from wrapped callable...")
		#_logger.debug("Released display lock.")
		
	#__/ End instance method dispDrvr.withLock().
	
		#|--------------------------------------------------------------------
		#| The following class-level variable will be initialized at the time 
		#| that the (first, and presumably only) display driver instance is 
		#| initialized.  It affects the behavior of our superclass methods.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	defaultWrapper = None		# Not initialized yet.
	
	# This definition should really be moved into infrastructure.worklist.Worker.
	@classmethod
	def setDefaultWrapper(thisClass, wrapper):
		"""Sets the default wrapper for this class to the given function,
			which should take a single argument, a callable to wrap."""
		thisClass.defaultWrapper = wrapper
	
	def __init__(newDisplayDriver, theDisplay:TheDisplay=None):
		
		"""Initializes the display driver by setting up its role & component 
			attributes appropriately for thread-specific logging purposes, and
			installing an appropriate wrapper function."""
		
		driver = newDisplayDriver
		
			# Remember where the display is so we can find it later.
		driver._display = theDisplay	
		
			# Set the default wrapper appropriately. (Will this work?)
		driver.setDefaultWrapper(driver.withLock)
				# (If this doesn't work, use "lambda callable: driver.withLock(callable)".)
		
		super(DisplayDriver, driver).__init__(
			role = 'DisplDrvr', component = _sw_component, daemon=True)
			# daemon=True tells Python not to let this thread keep the process alive
		
		# Stash this new display driver instance in a module-level global
		# so that the in_driver_thread() function (below) can find it.
		global _theDisplayDriver
		_theDisplayDriver = driver

#__/ End module public thread class DisplayDriver.


	#----------------------
	# Function definitions.

def in_driver_thread():
	"""Returns true if run within the display driver thread."""
	return current_thread() == _theDisplayDriver


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/threads.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
