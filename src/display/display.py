#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 display/display.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""	FILE NAME:		display/display.py				 [Python module source file]
	
	MODULE NAME:	display.display
	IN PACKAGE:		display
	FULL PATH:		$GIT_ROOT/GLaDOS/src/display/display.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.display (Display screen management)


	MODULE DESCRIPTION:
	===================
	
		This module manages the "display screen," or virtual text terminal
		that is used to interact with human users.  
		
		This module is used by both the GLaDOS system console package, used 
		by system operators when monitoring the system, and by the terminal 
		package, which manages the individual sessions of users who are 
		connecting to the GLaDOS server, whether from another login session
		on the local host, or from a remote site.
		
		Presently, this module assumes that the actual terminal emulator that
		the human user is using is (more or less) compatible with xterm.  The
		Putty terminal used on Windows systems falls into this category.  
		Specifically, we assume that 64 color pairs and a Western/LATIN-1 font
		are available.  A future version of this module may generalize it to 
		a broader range of terminals.
		
		This module is based on the Python curses library.
		
	
	USAGE:
	------
	
		The primary means of utilizing the 'display' module is to subclass
		DisplayClient, and override the .paint() method for drawing the 
		display, and the .handle() method for handling input events.  Of 
		course, more complex, multi-window applications are possible. 
	
	
	EXPORTED NAMES:
	===============
	
		This module defines and exports the following public names:
		
			Classes:
			--------

				TheDisplay
				
		
			Types:
			------
			
				Loc [struct]	- An x,y location in a screen or window.
				
			
	Dependencies:
	-------------
	
		This module references the following sister modules within the
		display package:  .exceptions, .colors, .controls, .keys, and 
		.threads.
		
		This module is referenced by...										 """
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
	#|						from display.display import *
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
global __all__ 
__all__ = [		# List of all public names exported from this module.

			#|---------
			#| Classes.
		
		'TheDisplay',		# Singleton class; anchor for module.
		
			#|--------------------
			#| "Type" definitions.
		
		'Loc',			# A location struct in a screen/window.    [struct type]
		
	]


	#|==========================================================================
	#| 	2.	Imports.									   [module code section]
	#|
	#|		2.1.  Standard Python modules imported into this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from threading 	import RLock		# Reentrant locks for concurrency control.  Used in theDisplay.__init__().
from time		import sleep		# Causes thread to give up control for a period.  Used in theDisplay.do1iteration().
from os			import path 		# Manipulate filesystem path strings.  Used in logger setup.


		#|======================================================================
		#| Import a bunch of stuff that we need from the curses package.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import curses
from curses import *
	# At some point we should change this '*' to an explicit list of the
	# curses names that we actually use in this module.

from curses.ascii import (

		TAB, LF, NL, VT, FF, CR,	# Whitespace code points.

		DC4	# Constant: Code point for Device Control 4 (control-T).  Used in theDisplay.do1iteration().
	)


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	2.2.  Custom imports.						[module code subsection]
		#|
		#|		Here we import various local/application-specific 
		#|		modules that we need.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


from infrastructure.decorators	import	singleton	# Class decorator.  Used by TheDisplay.


			#|------------------------
			#| Logging-related stuff.
			#|vvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.logmaster import (
		sysName,			# Used for forming _sw_component.
		ThreadActor,		# BlinkTimer inherits from this.
		getComponentLogger 	# Used just below.
	)
global _package, _logger
_package = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_package)  # Create/access the package logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _package

			#|------------------------------------------------------------------
			#| Import sibling modules we need from within the display package.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from .exceptions import (	# Display-related exception classes.

		RenderExcursion,		# display.renderText() can throw this.
		DisplayNotRunning,		# We handle this return from driver().
		DisplayDied,			# display._do1iteration() can throw this.
		RequestRestart,			# display._resize() might throw this.
		TerminateServer,		# display._do1iteration() can throw this.
	
	) 	

from .colors import *		# All color-related definitions.

	# Imports related to rendering of control/whitespace characters.

from .controls import (

		render_char			# Renders any 7/8-bit character in a curses window.

	)

	# Imports related to representation and processing of keys and 
	# key combinations provided from the text terminal input.

from .keys import (

		KeyEvent,			# Simple type for holding key information.
		TheKeyBuffer,		# Facility for sophisticated keyboard input processing.
	
	)

	# Imports relating to display-specific threads.

from .threads import (

		TUI_Input_Thread,	# Thread for running the text UI main loop.
		DisplayDriver,		# Thread for coordinating display output tasks.
		#in_driver_thread,	# Function for verifying we're in the driver thread.

	)


	#|==========================================================================
	#|	3.	Type definitions.							   [module code section]
	#|
	#|		In this section, we define various "types" that we provide.
	#|		Essentially, for us, a "type" just means a simple class, or
	#|		any way of using a structured object as a simple data type.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(display.)Loc									[public struct type]
		#|
		#|		This class essentially implements a simple 2-element 
		#|		struct type with named public data members 'x' and 'y' 
		#|		that represent a pair of character coordinates within 
		#|		a screen or window.
		#|
		#|		Note that in the constructor call, if argument names
		#|		aren't given, then the y coordinate is specified first, 
		#|		as is standard within curses.
		#|
		#|		This type is used for the 'loc' argument to (e.g.) the 
		#|		display.add_str() instance method.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Loc:
	"""(display.)Loc										[public struct type]
	
		This class effectively just defines a simple struct representing 
		a location within the screen or a window.  It includes .x and .y
		coordinate attributes representing the horizontal and vertical
		distance, in character cells, from the upper-left character cell
		of the screen or window.  Note y increases in the down direction.
		
	USAGE:
	
		loc = Loc(myY, myX)
			# Note the Y coordinate needs to be specified first if 
			# the argument keywords are not provided.
		
		loc = Loc(x = myX, y = myY)
			# Alternatively, you can do it explicitly, like this.
			
		print(loc.x, loc.y)													 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def __init__(thisloc, y=None, x=None):
		"""loc.__init__()							   [special instance method]
		
			This is the instance initializer for new Loc structures.  
			Note the y coordinate is specified first if argument 
			keywords are not provided.										 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		thisloc.x = x
		thisloc.y = y
		
	#__/ End struct instance initializer loc.__init__().

#__/ End struct type Loc.


	#|==========================================================================
	#|
	#|	5.	Class definitions.						   	   [module code section]
	#|
	#|		In this section we define the various classes provided by 
	#|		this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|---------------------------------------------------
		#| Forward class declarations, for use in type hints.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class TheDisplay:		pass	# Forward declaration for type hints.
class DisplayClient: 	pass	# Dummy declaration for type hints.
class BlinkTimer: 		pass

class BlinkTimer(ThreadActor):
	
	"""The purpose of this thread is to actively blink the display cursor.
		The blink cycle is 1 second (1/2 second "on", 1/2 second "off")."""
	
	defaultRole = 'BlinkTimr'
	defaultComponent = _sw_component
	
	def __init__(newBlinkTimer:BlinkTimer, display:TheDisplay):
	
		_logger.debug("blinkTimer.__init__(): Initializing blink timer.")
	
		timer = newBlinkTimer
		timer._display = display
		timer._exitRequested = False

		timer.defaultTarget = timer._main
		super(BlinkTimer, timer).__init__(daemon=True)	# ThreadActor initialization.
			# The daemon=True tells Python not to let this thread keep the process alive.
	
	@property
	def display(newBlinkTimer:BlinkTimer):
		timer = newBlinkTimer
		return timer._display
	
	def _main(thisBlinkTimer:BlinkTimer):
		
		_logger.debug("blinkTimer._main(): Blink timer starting.")
		
		timer = thisBlinkTimer

		while not timer._exitRequested:

			#_logger.debug("blinkTimer._main(): Starting a blink cycle.")

			# The full blink cycle is 1 second.  Blink on, wait half abs
			# second, blink off, wait half a second.
		
			timer.blinkOn()		# Turn cursor A_BLINK attribute on.
			sleep(0.5)			# Sleep half a second.
			timer.blinkOff()	# Turn cursor A_BLINK attribute off.
			sleep(0.5)			# Sleep half a second.
			
	def blinkOn(thisBlinkTimer:BlinkTimer):
		timer = thisBlinkTimer
		display = timer.display
		driver = display.driver
		driver(display.setBlinkOn, desc="Blink cursor on")
			# Wait for return so we don't get ahead of driver
		
	def blinkOff(thisBlinkTimer:BlinkTimer):
		timer = thisBlinkTimer
		display = timer.display
		driver = display.driver
		driver(display.setBlinkOff, desc="Blink cursor off")
			# Wait for return so we don't get ahead of driver


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.TheDisplay					   		[public singleton class]
		#|
		#|		This singleton class is the main class that anchors the 
		#|		'display' module, and manages the underlying curses display 
		#|		interface.
		#|
		#|		Applications usually do not need to construct or use this 
		#|		singleton directly, but can go through their application-
		#|		specific subclass of the DisplayClient class, which can be 
		#|		found in client.py.
		#|
		#|		This class definition is rather long.  Here is a concise 
		#|		list of contents.  See internal docstrings for more detail.
		#|
		#|	Class contents:
		#|	===============
		#|
		#|		Singleton instance initializer:
		#|		-------------------------------
		#|
		#|			.__init__()						   [special instance method]
		#|
		#|
		#|		Public data attributes:
		#|		-----------------------
		#|
		#|			.{running, isRunning}			[boolean read-only property]
		#|			.client					  [DisplayClient read-only property]
		#|			.screen			 		  [curses window read-only property]
		#|			.{width, height}			  [integer read-only properties]
		#|			.lock							  [RLock read-only property]
		#|			.driver					  [DisplayDriver read-only property]
		#|
		#|
		#|		Public initialization methods:
		#|		------------------------------
		#|
		#|			.setClient()						[public instance method]
		#|			.start()							[public instance method]
		#|
		#|
		#|		Input thread methods:
		#|		---------------------
		#|
		#|			._main()								[public instance method]
		#|			._manage()						   [private instance method]
		#|			
		#|
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

@singleton
class TheDisplay:
	"""
		TheDisplay										   [public anchor class]
		
			This is a singleton class which also serves as the public anchor
			point for the display module.
			
			Its sole instance represents the text display screen, which is 
			managed by the curses library.	 For now, it assumes that the 
			display is compatible with xterm/Putty (8 colors, Western script).
	
	
		Public data attributes (implemented as properties):
		----------------------
			
			display.{running, isRunning}			[boolean read-only property]
			
				True if the display is currently running (i.e., curses is
				in control of the text terminal).  Clients should not try
				to perform any display operations if the display is not in
				the running state (they will typically fail, or be ignored).
			
			display.client					  [DisplayClient read-only property]
			
				This is a handle to the currently active client (display-
				based application) that presently owns & controls the 
				display.  If it is None, no client is currently connected.
			
			display.screen			[curses top-level window read-only property]
			
				If the display is currently running, this is a handle to
				to the "screen" or top-level window of the curses display.
			
			display.{width, height}				  [integer read-only properties]
			
				These attributes return the current width (in assumed-
				fixed-with character columns) and height (in text rows) 
				of the text display.
			
			display.lock							  [RLock read-only property]
			
				This is a reentrant mutex lock, from the Python threading
				library, which controls access to sensitive data structures
				associated with the display (in particular, the state of 
				the curses library).  Before performing any operations that
				might affect the state of the display, one should grab this 
				lock using syntax like:
				
						with display.lock:
							...(do sensitive operations)...
				
				Note that this syntax will automatically take care of 
				releasing the lock when the code block is exited, even if
				this occurs via an exception.
				
			display.driver					  [DisplayDriver read-only property]
			
				An alternative method for performing thread-safe display 
				operations is to package the desired procedure into a 
				callable (e.g., a function, method, or anonymous delegate)
				and pass it to the display driver using any of the 
				following syntax patterns:
				
							
						dispDrvr(callable)
							# This form waits for completion, but discards 
							# any result.
				
						result = dispDrvr(callable)	
							# This form waits for completion and gets a result.
							
						dispDrvr.do(callable)
							# This runs the callable in the background by
							# adding it onto a queue of tasks to be executed
							# asynchonously by the display driver.
			
				Note that, behind the scenes, the display driver is imple-
				mented as an RPC- style Worker thread (from the infrastruc-
				ture.worklist module) whose assigned role is to interleave  
				and execute display-related operations coming from various
				source.  Before executing each task, the display driver 
				grabs the display.lock and makes sure that the display is
				actually running.  If not, the requested task is discarded.
				
				
		Public read-only methods:
		-------------------------
			
			display.get_size()						 [read-only instance method]
			
				Gets the current dimensions of the display in cells.
			
			display.get_max_yx()					 [read-only instance method]								
			
				Get the coordinates of the lower-right character cell.
		
		
		Public initialization methods:
		------------------------------
		
			display.setClient()					[instance initialization method]
			
				Tell the display what client will control it.
				
			display.start()							   [instance startup method]
			
				Starts the display running.  This launches a couple of
				threads (see the threads module) to handle display I/O.
		
		
		Sensitive public methods:
		-------------------------
		
			display.paint()								 [display driver method]
			
				Re-paints the entire display.
		
			[...CONTINUE...]
		
	"""

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def __init__(theDisplay:TheDisplay):
		"""
			theDisplay.__init__()					   [special instance method]
			
				This is the instance initializer for the sole instance of 
				the singleton class TheDisplay.  It is normally called for
				the first time by display.client.displayClient.__init__(), 
				when the first active client instance is created.
		
				The effect of this method is to initialize the display 
				system for later use.  However, not much can be done yet.
				We note that the display is not running yet, and initialize
				some private data members to null values to show that they
				are uninitialized.
				
				However, we do go ahead and create the display driver thread 
				(defined in the display.threads module) for later use.  But,
				when first created, it is just sitting idle and does nothing.
				It is a worker thread, so won't do anything until given work.
		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		display = theDisplay	# Get a shorter name for the display.

			#----------------------------------------------------------------
			# Mark this display as not running yet, to make sure we don't try 
			# to do anything with it until it's actually running.
			
		display._running = False		# Display is not up and running yet.

			#-----------------------------------------------------------------
			# Initialize various other private data members to None, to make
			# explicit that they have not been initialized yet.

		display._client = None		# Client is not yet attached.

		display._screen = None		
			# The actual display screen structure hasn't been created yet.
			
		display._width  = None	# No width/height yet, because no screen
		display._height = None

			#|------------------------------------------------------------------
			#|	As a most basic measure to ensure that the state of the curses 
			#|	library remains self-consistent across all threads within a 
			#|	multithreaded environment, we here create a reentrant lock
			#|	which threads can grab (using "with display.lock: ..." syntax)
			#|	in order to atomically obtain ownership of the display for a 
			#|	period of time.  Note: To prevent deadlocks, don't do a blocking
			#|	RPC-style call to another thread which may also need the lock 
			#|	while you have it.  Instead, you should send the other thread 
			#|	requests to be executed asynchronously in the background, using
			#|	syntax like "driver.do(...)".
			
		display._lock = RLock()		# Reentrant lock for concurrency control.

			#|------------------------------------------------------------------
			#|	As a secondary tool to facilitate multithreaded curses apps,
			#|	we create this "display driver" thread, which is an RPCWorker
			#|	(from the worklist module).  It can carry out display tasks 
			#|	either synchronously ("driver(...)" syntax) or asynchronously
			#|	("driver.do(...)" syntax).

		display._driver = DisplayDriver(display)		# Creates display driver thread.
			# (This newly created thread is initially just waiting for work to do.)
	
			#|---------------------------------------------------------------------
			#| Create the cursor blink timer thread. This will be started after the
			#| display is started up.
		display._blinker = BlinkTimer(display)
	
		# Nothing else to do here yet. Nothing really happens until .start() is called.
	
	#__/ End singleton instance initializer for class TheDisplay.


	#|==========================================================================
	#|	Public instance properties.							[class code section]
	#|
	#|		Below we define public properties which provide gated access 
	#|		to certain instance attributes.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@property
	def running(theDisplay:TheDisplay):
		"""Is the display currently running?"""
		return theDisplay.isRunning
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@property
	def isRunning(theDisplay:TheDisplay):
		"""Synonymous with the .running() method."""
		return theDisplay._running
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@property
	def client(theDisplay:TheDisplay):
		"""Returns a handle to the currently active client that owns the display."""
		return theDisplay._client
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@property
	def screen(theDisplay:TheDisplay):
		"""This handles getting theDisplay.screen attribute.
			Note this is an error if the display isn't running."""
		return theDisplay._screen
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@property
	def height(theDisplay:TheDisplay):
		"""Returns the current height of the display screen, in rows of text."""
		return theDisplay._height
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@property
	def width(theDisplay:TheDisplay):
		"""Returns the current width of the display screen, in (assumed 
			fixed-width) character cells."""
		return theDisplay._width
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@property
	def lock(theDisplay:TheDisplay):
	
		"""Reentrant lock for controlling concurrent access to the underlying 
			curses library.  A thread should use the following syntax to grab
			the lock within the dynamical scope of a lexical block of code:
			
					with display.lock: 
						...(statements)...
						
			This will ensure that the lock is released when the code block is
			exited, whether normally or via an exception.  This is important 
			for preventing deadlocks.										 """
			
		return theDisplay._lock
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	@property
	def driver(theDisplay:TheDisplay):
		"""Returns a handle to the display's centralized driver thread."""
		return theDisplay._driver
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	

	#|==========================================================================
	#|	Public read-only methods.							[class code section]
	#|
	#|		Below we define methods which are read-only; that is, they do
	#|		not modify the state of the display.
	#|
	#|		Note that because they are read-only (and atomic, in the 
	#|		abscence of pre-emptive interrupts), these methods can be 
	#|		called by any thread, and the caller is not required to lock 
	#|		the display before calling them.
	#|
	#|	.get_size() 									[public instance method]
	#|				
	#|		Gets the current dimensions of the display, in character cells.
	#|		[returns (height:int, width:int)]
	#|
	#|	.get_max_yx() 									[public instance method]
	#|				
	#|		Gets the coordinates of the cell at the lower-right 
	#|		corner of the display. [returns (max_y:int, max_x:int)]
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	def get_size(theDisplay:TheDisplay):
	
		"""Returns a pair (h,w) giving the height of the display in lines,
			and the width of the display in columns (character cells).
			
			These values are set up by the private _check_size() method.
			Note that they are only available/valid/current after calling 
			._resize()."""
			
		return (theDisplay._height, theDisplay._width)	


	def get_max_yx(theDisplay:TheDisplay):
	
		"""Returns a pair (y,x) giving the coordinates of the lower-right 
			cell of the display.
			
			These values are set up by the private _check_size() method.
			Note that they are only available/current after calling 
			._resize()."""
			
		return (theDisplay._max_y, theDisplay._max_x)


	#|==========================================================================
	#|	Public initialization methods.						[class code section]
	#|
	#|		Below we define public methods which clients may use to perform 
	#|		additional initialization of the display, beyond what is done 
	#|		automatically when the singleton instance of TheDisplay is first 
	#|		constructed.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def setClient(theDisplay:TheDisplay, displayClient:DisplayClient):
		"""display.setClient()				  			[public instance method]
			
				Calling this method configures the display to be managed by 
				the given client (which should be an instance of Display-
				Client or one of its subclasses).  Most clients will call 
				this automatically as they are initializing themselves.
			
				Note: This method needs to be called before the display is 
				started.  We do not currently support changing the currently 
				active client dynamically once the display is up and running; 
				however, this may be supported in the future.				 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		theDisplay._client = displayClient		# Store the client.

	#__/ End public instance method display.setClient().
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def start(theDisplay:TheDisplay, waitForExit:bool=False):
		"""display.start()					  			[public instance method]
			
				Calling this method is what actually causes the display to
				start running.  Normally, this method is called automati-
				cally by client.start().
				
				Please note that, before this method is called, a client 
				should have previously been attached to the display using
				the display.setClient() method, above.
				
				
			Arguments:
			----------
			
				waitForExit							[boolean keyword argument]
				
					If waitForExit is not provided, or is False, then the 
					display's TUI (text UI) input loop is allowed to run 
					in the background (in the TUI_Input_Thread), and this 
					.start() method returns immediately.  Otherwise, if 
					waitForExit=True is provided, then this method does 
					not return until the input loop is terminated (either 
					due to a user interrupt (^T), or because some other, 
					un-handled exception occurred in it).					 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		_logger.debug("display.start(): Starting display with "
			f"waitForExit={waitForExit}...")

		display = theDisplay
		
			#------------------------------------------------------------------
			# First, we create the thread to manage the main input loop for the
			# human user's TUI (text user interface).
			
		tuiInputThread = TUI_Input_Thread(target=display._main)
		display._tuiInputThread = tuiInputThread	# Remember it.
		
			#-------------------------------------------------------------------
			# This starts the new thread running in the background. This will 
			# bring up the curses interface by calling display._main().  Once 
			# it's up, however, all (or most) of the I/O to/from it should be 
			# managed through the separate DisplayDriver thread, so as to
			# interleave display requests from multiple sources (not just this
			# user input thread).
			
		tuiInputThread.start()		# Starts thread on display._main() method.
			
			#------------------------------------------------------------------
			# If the user requested us to wait for the the input loop to exit,
			# then do so, by calling a thread .join() operation on it.
			
		if waitForExit:
			_logger.debug("display.start(): Waiting for TUI input thread to exit...")
			try:
				tuiInputThread.join()
			except Exception as e:
				_logger.FATAL("display.start(): Uncaught exception [{str(e)}] in TUI input thread.")
				raise
				
				
		_logger.debug("display.start(): Returning.")

	#__/ End public instance method theDisplay.start().
	
	
	#|==========================================================================
	#|	Input thread methods.								[class code section]
	#|
	#|		The following private methods are intended to be executed by 
	#|		the user input thread (TUI_Input_Thread).  They handle display 
	#|		setup, teardown, and the main event loop.
	#|
	#|		Please note, however, that the actual handling of events, and 
	#|		most activity that actually writes to the display is supposed
	#|		to go through the display driver thread; see next section.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _main(theDisplay:TheDisplay):
		"""display._main()					 		   [private instance method]
		
				This method provides the main body of the TUI_Input_Thread
				execution, after that thread is started by display.start().
		
				This method is responsible for bringing up and managing the 
				entire display, and bringing it down again when done.  The
				purpose of running it in its own thread is so that it can 
				operate asynchonously with other independently-running parts
				of the system.
				
				Most of the real work here is done inside the private method 
				display._manage(), which we run inside the curses wrapper(). """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		display = theDisplay
			
		_logger.debug("display._main(): Starting the display running.")

		# The try/except clause here is needed to catch exceptions so we
		# can tell the client about them.

		try:

			#|------------------------------------------------------------------
			#| NOTE: wrapper() is a curses function, so we acquire the display 
			#| lock here to ensure thread-safety.  However, although we acquire 
			#| the display lock while entering and exiting the wrapper function, 
			#| internally to ._manage(), the lock is released whenever we're not 
			#| actively using it.  This is needed to avoid deadlocks.

			with display.lock:
		
				# Call the standard curses wrapper on our private display management 
				# method, below.
				wrapper(theDisplay._manage)
				# ._manage() sets up the display and runs our main input loop.
		
		except TerminateServer as e:
			# If we get this exception, it means that the user intentionally
			# terminated the server by pressing ^T.  Execute a clean exit.

			_logger.info("display._main(): Exiting because user requested server termination.")

		finally:

			_logger.debug("display._main(): Finished running the display.")

			_logger.debug("display._main(): Notifying client of display shutdown.")
			display.client.notifyShutdown()

	#__/ End private instance method theDisplay._main().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _manage(theDisplay:TheDisplay, screen):
		#| Note 'screen' is the top-level curses window for the entire 
		#| terminal screen; it is passed into this method by the curses 
		#| wrapper() function.
		#\-------------------------------------------------------------
		"""display._manage()				 [sensitive private instance method]
			
				This is a private method that does all the work of 'mana-
				ging' the curses display once it has been created.  It is 
				invoked from within the curses wrapper() by display._main(), 
				above, and is passed the top-level window (screen) by the
				wrapper function.  
				
				Note that when this ._manage() method returns, we exit from 
				wrapper() and the entire display will be torn down.  So, 
				this method should take care not to actually exit until we 
				are really completely done with using the curses display.
				
				Note also this method, unlike most other display methods, 
				does *not* run within the DisplayDriver thread.  Instead,
				this method actually runs within the TUI input loop thread, 
				although it hands off input events to event handlers running
				in the DisplayDriver thread.  The display.lock is managed 
				judiciously so as to avoid inter-thread conflicts between 
				the activities of this thread and DisplayDriver.
				
				The reason why display package operations are organized in 
				this manner is that it separates the relatively complex logic
				of the main UI input loop from the relatively simple logic of
				the display output driver.  All that the output driver needs
				to do is interleave output requests from various sources.
				Whereas, the main loop has a relatively complex pattern of
				activity.													 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		_logger.debug("display._manage(): Starting up.")

		display = theDisplay
		dispDrv = display.driver		# Display driver thread.

			#|------------------------------------------------------------------
			#| The first thing we do is to mark the display as now being in the 
			#| "running" state, where we can do stuff with it. We need to do 
			#| this now to make sure that subsequent display operations won't 
			#| suppress themselves because they think the display isn't running
			#| yet.  We wrap this in a try/finally construct, to make sure that, 
			#| when we exit, we will have marked the display as no longer 
			#| running, to maintain consistency.

		try:	# Cleanup properly in case of exception-driven exits.

				# Store our top-level window (screen) for future reference.
			display._screen = screen	# Do this *before* we start running.

			display._running = True		# Display is now declared 'running'.

				#|--------------------------------------------------------------
				#|	This releases the display lock that we acquired earlier in 
				#|	the 'with' statement in the ._main() method.  We have to do 
				#|	this now because the display driver is about to need it.  
				#|	However, at this point, no other threads in the system 
				#|	should be trying to use the display yet anyway.  So, this 
				#|	should be safe to do here, without us having to worry that 
				#|	someone else might try to use the display before it's really 
				#|	been fully initialized.

			display.lock.release()
	
				#|--------------------------------------------------------------
				#| 	Now that the display is declared to be "running", the very 
				#|	first thing that we ask it to do is to initialize itself.  
				#|	This sets up the state of the curses library appropriately 
				#|	for our application.  Note that we do this by delegating it 
				#|	to the display driver thread, which is how we try to do as 
				#|	many of our display-related operations as possible.
				
			dispDrv(display._init, desc="Initialize display")
				# Note this call waits for initialization to be completed.

				#---------------------------------------------------------------
				# Now that the display has been initialized, we can go ahead 
				# and start running the main UI event loop.
				
			display._runMainloop()		# Run the main loop.

		finally:	# Whether any exceptions happen or not, do this:

			# First, we have to re-acquire the lock, because we're about to
			# tear down the display when we exit the wrapper.
			display.lock.acquire()

			# Now mark the display as no longer running.
			display._running = False		# Display is no longer running.
			
			# If we get here, then the display driver has exited, and the display was torn down.
			theDisplay._screen = None		# It's no longer valid anyway.
		
		#__/ End try/finally clause for display startup/shutdown.

		_logger.debug("display._manage(): Exiting.")

		# Now, when we exit from this method, we also exit from curses' wrapper() function.

	#__/ End sensitive private singleton instance method theDisplay._manage().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _runMainloop(theDisplay:TheDisplay):
		"""display._runMainloop()			 		   [private instance method]
			
				This private method contains the main user-interface event
				loop for the entire display facility.  It runs within the 
				TUI input thread that is created for this purpose.  It is
				normally invoked by display._manage(), above, after the 
				curses display has been initialized.
		
				Please note that the TUI input thread has a Flag named 
				'.exitRequested'; if another thread wants to cause the
				main loop to terminate after its current iteration, it can 
				do so by raising this flag via:
				
							thread.exitRequested.raise().					 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		_logger.debug("display._runMainloop(): Starting main event loop.")

		display = theDisplay
		
		dispDrv = display.driver
		thread = display._tuiInputThread
		
			#|-----------------------------------------------------------------
			#| Here's the actual main loop. Keep going until requested to exit,
			#| or there is an exception.
				
		while not thread.exitRequested:
			
			display._do1iteration()		# Does one iteration of the main loop.

		#__/ End main user input loop.
		
		_logger.debug(f"display._runMainloop(): Exited main loop.")

	#__/ End private instance method theDisplay._runMainloop().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _do1iteration(theDisplay:TheDisplay):	
		"""display._do1iteration()					   [private instance method]
			
				This method simply executes just a single iteration of the 
				main UI event loop.  It runs in the TUI input thread.  
				
				Please note the careful interplay of 'with display.lock' 
				and sleep() within this method, so as to maintain consistency
				while allowing other threads ample opportunity to execute.   """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
			# Suppress this to prevent excessive logging since this method
			# runs, like, 20 times per second.
		#_logger.debug("Doing one main-loop iteration...")
		
		display = theDisplay
		
		dispDrv = display.driver
		screen = display.screen
		client = display._client
		thread = display._tuiInputThread
		
			#/------------------------------------------------------------------
			#|	OK, now the following code implements a pattern of display 
			#|	lock/unlock actions that deserves some explanation.  We lock 
			#|	the display before getting an event.  If the 'key' denotes a 
			#|	high-priority event, such as a window resize event, then we 
			#|	handle it right away, in one atomic process, that is, without 
			#|	releasing the lock in between.  This is important to allow the 
			#|	effects of e.g., a window resize to finish playing out before 
			#|	we try to do anything else with the display.  However, for 
			#|	less-critical events, like ordinary keypresses, we go ahead 
			#|	and release the lock before processing them, less urgently, 
			#|	in the display driver thread.  This gives other threads an 
			#|	opportunity to also make their own display requests.
			
		with display.lock:		# Lock the display temporarily in this TUI input thread.
		
				#---------------------------------------------------------------
				# First, we make sure the display is nice and up-to-date before 
				# we ask for anything from the user (since, how's he supposed to
				# be able to respond appropriately otherwise?)
				
			display.update()	# NOTE: Does nothing if no updates are needed.
		
				# Initialize both of these key-related variables to None until 
				# we actually have values for them.
				
			ch = None		# This will be a raw keycode (integer).
			event = None	# This will be a more complex KeyEvent data stucture.

			#/------------------------------------------------------------------
			#|	NOTE: The following try/except clause allows us to handle 
			#|	keyboard interrupts (i.e., interrupts caused by the user 
			#|	hitting ^C) and other exceptions cleanly; however, please 
			#|	also note that we previously turned on raw() mode in 
			#|	display._init(), so, we don't actually expect any keyboard 
			#|	interrupt exceptions to occur.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			try:
			
					#|---------------------------------------------------
					#| This obtains get the next key input event from our 
					#| fancy-dancy input processing system in keys.py.
					
				event = TheKeyBuffer().get_next_key(screen)
				ch = event.keycode

					#-----------------------------------------------------
					# Below was our old way of doing things, but it didn't
					# handle as many keys and key-combos cleanly.
					
				#ch = screen.getch()		# Gets a 'character' (keycode) ch.
					# Note earlier, we configured .getch() to be nonblocking.

					#-------------------------------------------------
					# This version is also commented out, because wide 
					# characters didn't seem to be very useful either.
					
				#wch = screen.get_wch()
				#_logger.debug(f"display._do1iteration(): Got a wide character: [{wch}]")

			except curses.error as e:	# If get_wch() was used, this means no input was received yet.
				# NOTE: This should never happen since we're not using get_wch().

				ch = ERR	# Just set the keycode to the normal ERR (-1) code.

			except KeyboardInterrupt as e:				# User hit CTRL-C?
				# Note that currently, we should not get these events anyway, since
				# earlier, we put the terminal in raw() mode.

				_logger.debug("display._do1iteration(): Caught a keyboard "
							  "interrupt during screen.getch().")

				ch = KEY_BREAK		# Translate ^C to the abstract BREAK key.

			except Exception as e:

				_logger.fatal("display._do1iteration(): Unknown exception "
							  f"during screen.getch(): {str(e)}.")
				raise e
				
			else:	# No exceptions occurred during 'try' body.
			
				# Note we suppress debug output if the keycode is ERR (= none yet) to
				# prevent excessive debug logging.

				if ch != ERR:
					_logger.debug(f"display._do1iteration(): Got character code {ch}.")

			#__/ End try/except clause for keyboard input (.getch()) call.
			
				#|--------------------------------------------------------------
				#| If we don't have an Event by now, make one.  Generally, this
				#| only happens in the curses.error and KeyboardInterrupt cases 
				#| above (which should never occur currently).

			if event is None:
				event = KeyEvent(keycode = ch)

			#/------------------------------------------------------------------
			#|	OK, if we get here, this means that there were no un-handleable 
			#|	exceptions during .getch(), and so now, we just need to figure 
			#|	out if there was any kind of high-priority event that we would 
			#|	need to handle right away, before we exit the 'with' clause and 
			#|	release our display lock.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
				#/--------------------------------------------------------------
				#| First case: If the user pressed control-T, then this is a 
				#| command to immediately terminate the entire GLaDOS server 
				#| application process.  Treat this at highest priority.
			
			if ch == DC4:		# ^T = Device control 4, primary stop, terminate.
				_logger.fatal("display._do1iteration(): Exiting due to ^T = terminate key.")

				# Notify client that it should prepare for imminent display termination.
				client.prepareForShutdown()

				raise TerminateServer("Terminating server because user pressed ^T.")
			
				#/--------------------------------------------------------------
				#| Second case: If we received a Resize event, then we need 
				#| to try to handle it as best we can before we try to do 
				#| anything else with the display. (Because, handling resize 
				#| properly is difficult enough without having to worry that 
				#| other threads might interfere with what we're doing.)
			
			if ch == KEY_RESIZE:
				_logger.info("display._do1iteration(): Got a resize event; handling at high priority.")
				display._resize()	# Resize & then repaint the display.
				return	# Complete this main loop iteration normally.
				
		#__/ End with display locked.

		#/----------------------------------------------------------------------
		#| If we get here, then we did not get a high-priority event, and the
		#| display is now unlocked.  So now, figure out what to do next.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		if ch == ERR:
			# If we're in nonblocking or half-delay mode, getting an error 
			# return just means that no new characters have been typed yet.

				# This is commented out to avoid excessive log messages.
			#_logger.debug(f"display._runMainloop(): Got an ERR from screen.getch().")

				#|--------------------------------------------------------------
				#| This sleep is important to allow other threads using the 
				#| display to have a sufficient opportunity to run in between 
				#| our checking for new inputs, and also reduce the amount of 
				#| CPU time that we waste with excessive polling.  The time 
				#| delay value given here until wakeup is 50 milliseconds or 
				#| 1/20th of a second.  If the time given here were too long, 
				#| the console would seem slow to respond to input.  If the 
				#| time were too short, the main loop will waste too much CPU 
				#| time with repeated input polling, and overall program 
				#| operation would be slower because of the wastage.

			sleep(1/20)		# Sleep for 0.05 second = 50 milliseconds.
			#sleep(1)		# A long sleep is sometimes useful during debugging.
			
				# We don't need to do anything else in a main-loop iteration
				# in this case.
			
			return		# I.e., complete this main-loop iteration normally.
		
		#/----------------------------------------------------------------------
		#| If we get here, then we have some 'real' key event to be handled.
		#| Normally, we handle all events by handing them off to the display 
		#| driver thread (which is a worker thread).  The advantage of doing 
		#| things this way is that other threads (also going through the
		#| centralized display driver thread) can asynchronously be doing other
		#| stuff with the display (writing updates, etc.) and the handling of 
		#| key events will be interleaved with that other work automatically in 
		#| a thread-safe way.  Also, there is some automated logging work done.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		result = dispDrv(lambda: client.handle_event(event), desc="Handle event")
			# Note this waits for the event handler to finish before we get another
			# key. This helps prevent the input loop from "getting ahead" of the
			# display, and building up a big backlog of input-processing work to 
			# do in the display queue.  However, if we preferred, we could also 
			# change this to kick off the handler work to be done in the 
			# background using dispDrv.do().  Although then there'd be no return.
		
		# Now, we process any result that was returned by the display driver.
		
			#--------------------------------------------------------------------
			# If the display driver returned a "display not running" warning
			# exception, this is an unexpected event which means that the display
			# was somehow unexpectedly terminated before we got here.  If this 
			# happens, we don't really know how to respond ourselves, except by 
			# raising an error-level exception, which will probably cause the
			# main loop to die (if not handled at some higher level).
			
		if isinstance(result, DisplayNotRunning):
			raise DisplayDied("display._do1iteration(): Display unexpectedly quit.")
			
	#__/ End private instance method display._do1iteration().
	
	
	#|==========================================================================
	#|	Output thread methods.								[class code section]
	#|
	#|		This section contains methods that are specifically intended 
	#|		to be executed within the display driver thread (DisplayDriver).  
	#|		They handle most display operations other than input and the 
	#|		very outermost setup/teardown operations.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _init(theDisplay:TheDisplay):
		"""display._init()					 [sensitive private instance method]
		
			This private instance method initializes the curses display. 
			The client should be attached first.  							 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		_logger.debug("display._init(): Initialziing the display.")

		display = theDisplay
		screen = display.screen

		#|----------------------------------------------------------------------
		#|	The first thing we do to initialize the display is to configure 
		#|	it to be in the input mode that we want.  We do this early on,
		#|	because we would like to suppress ordinary terminal control key 
		#|	processing, because we wish to handle these keys specially, in 
		#|	a way that is specific to our application.  (Especially ctrl-C, 
		#|	because we can't control which process/thread will see it, which 
		#|	introduces a lot of unnecessary extra complexity if we wanted to 
		#|	try to handle it cleanly.)  The ordinary controls that are being 
		#|	suppressed here are as follows:
		#|
		#|		^C (ETX)	-
		#|
		#|			This would normally cause a SIGINT (signal interrupt) 
		#|			signal to be sent to the process.  In Python curses 
		#|			programs, this would normally cause a KeyboardInterrupt 
		#|			exception to be raised, which would be fine, except that 
		#|			actually, the signal could end up getting caught by any 
		#|			of our subprocesses instead, and even if it's caught by 
		#|			the main process, the specific thread that it's raised 
		#|			within will be unpredictable.  Rather than having to 
		#|			figure out how to cope with all this unpredictability, 
		#|			we instead want to just handle interrupts manually, 
		#|			by e.g., binding a different key such as ^T (DC4) to a 
		#|			system-terminate behavior that we can handle cleanly.
		#|
		#|		^Q (DC1)	-
		#|
		#|			Also known as XON, this resumes a previously-suspended 
		#|			stream of data from the terminal.  However, XON/XOFF 
		#|			are extremely annoying controls, because it's very easy 
		#|			to hit ^S by accident, and then the terminal will seem 
		#|			to freeze up, and the user may not know to hit ^Q.
		#|
		#|		^S (DC3)	- 
		#|
		#|			Also known as XOFF; this is used in some protocols for 
		#|			flow control.  But in interactive user input, it's very
		#|			undesirable, because it causes the keyboard to appear 
		#|			to become unresponsive until a matching ^Q (XON) is
		#|			pressed.  We'd greatly prefer to just disable this 
		#|			antiquated, crappy-ass functionality altogether.
		#|
		#|		^Z (SUB)	-
		#|
		#|			In Unix systems, this tends to suspend the entire 
		#|			current process, and return the user to the shell 
		#|			prompt.  Again, although reversible ('fg' command) 
		#|			this behavior can be extremely disconcerting if the 
		#|			user hits the key by accident and isn't expecting it.  
		#|			So, we prefer to disable this functionality as well.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|--------------------------------------------------------------
			#| Set the input mode. Suppress processing of terminal controls,
			#| and configure win.getch() to be nonblocking by default.

			# Should this be done in the TUI_Input_Thread instead?
		raw()					# Suppresses processing of ^C/^S/^Q/^Z.
		screen.timeout(0)		# Non-blocking read on getch(), zero delay.
		
			# Not using the following settings currently. (Although we've tried 'em.)
		#screen.keypad(True)	# Interpret keypad escape sequences. (Doesn't work?)
		#cbreak()				# Not doing this because it doesn't suppress ^C/^S/^Q.
		#halfdelay(1)			# .getch() Returns ERR after 0.1 secs if no input seen.
			# Not doing that, because it just wastes time to have any input timeout at all.

			#|------------------------------------------------------------------
			#| Next, initialize all of the color pairs to be set up like we 
			#| want.  Note this method assumes an 8-color, 64-pair colormap 
			#| like in Putty/xterm.
			
		init_color_pairs()		# Configure color map (from colors module).
		
			#|-------------------------------------------------------------------
			#| Cursor setup. By default, we turn the system cursor off so we can
			#| control cursor display in a customized way.
		curs_set(0)		# 0=invisible, 1=normal, 2=very visible
		#screen.leaveok(True)	# Minimize cursor movement (do we need this?)

			#|------------------------------------------------------------------
			#| This effectively first measures the size of the display, & then 
			#| automatically paints its entire contents, for the first time.
			
		display._resize()		# Sizes/paints display.
	
			#|------------------------------------------------------------------
			#| This starts the blinker thread going in the background, which 
			#| makes the cursor blink.
		
		_logger.debug("display._init(): Starting blink timer thread.")
		display._blinker.start()	# Starts blinker thread running in background.
		
	#__/ End sensitive private instance method theDisplay._init().


	#|==========================================================================
	#|	Sensitive methods.									[class code section]
	#|
	#|		The following private methods may be called from any thread,
	#|		*but* the caller must ensure that he has grabbed display.lock
	#|		before calling them, since they affect the state of the 
	#|		curses display.
	#|
	#|		Note that currently, ._resize() is called from both of the
	#|		following display threads:
	#|
	#|			* The displayDriver thread calls it from display._init()
	#|				when the display is first being initialized.
	#|
	#|			* TUI_Input_Thread calls it from display.do1iteration() 
	#|				after a KEY_RESIZE event has been received.
	#|
	#|		Internally, resize calls ._check_size() and .paint().
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _resize(theDisplay:TheDisplay):
		"""display._resize()				 [sensitive private instance method]
		
				This private method is used internally by the display 
				facility to update its idea of the display's size.
				
				This is called on display startup, and again each
				time we get a display resize event (KEY_RESIZE).
				
				The calling thread should acquire display.lock before
				calling this method to prevent interference from other
				threads that may be asynchronously using the display.		 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		display = theDisplay
		client = display.client

			# Find out the new dimensions of the window.
		display._check_size()
		(height, width) = display.get_size()

			#----------------------------------------------------------
			# Now we potentially need to resize the window structures
			# within curses, if the terminal size has actually changed.

		_logger.debug(f"display._resize(): Resizing terminal to {(height,width)}.")
		resizeterm(height, width)
			# This has the effect of updating curses' idea of the terminal
			# size in curses.{LINES,COLS}; note that this *only* works right
			# if the environment variables LINES, COLUMNS are not set!  So
			# e.g., if you ever call update_lines_cols(), this will break.

		#/----------------------------------------------------------------------
		#| At this point, it would be nice if we could just handle the resize
		#| event gracefully, *but* we haven't yet figured out how to get that
		#| working.  So instead, at this point we just tear down and rebuild 
		#| the entire display.
		
		# Commented out because not quite resorting to this yet.
		# display.teardownAndRebuild()	# This raises a RequestRestart exception.

		# If we have a client attached, tell it to handle the resize internally.
		if client != None:
			client.handle_resize()		# Clients should implement this.

		_logger.debug("display._resize(): Repainting entire display after resize...")

			# Now that everything is consistent, repaint the entire display.
		display.paint()

	#__/ End sensitive private instance method display._resize().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def _check_size(theDisplay:TheDisplay):
		"""display._check_size()			 [sensitive private instance method]
		
				Checks the current size of the display screen after the
				user resizes his terminal window.  Sets the following 
				instance properties/functions accordingly:
				
					.width, .height, .get_size(), get_max_yx().				 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		screen = theDisplay._screen

			#|----------------------------------------------------------------
			#| It's important to note that .getmaxyx() will not work properly
			#| if either the LINES and/or COLUMNS environment variable is set;
			#| if so, those values will override the current window size.  So,
			#| please DO NOT SET THESE VARIABLES at all unless you really want 
			#| the app to treat the window size as fixed instead of self-
			#| adjusting on resize events.
			
		(height, width) = screen.getmaxyx()
		_logger.debug(f"._check_size(): .getmaxyx() returned {(height,width)}.")

			# Remember the new window size.  This affects the .width and .height
			# properties, and the return value of the display.get_size() method.
		theDisplay._width  = width
		theDisplay._height = height
		
			# Calculate and store bottom-right cell coordinates as well.  This 
			# affects the value that will be returned by display.get_max_yx().
		theDisplay._max_x  = width - 1
		theDisplay._max_y  = height - 1

	#__/ End private method theDisplay._check_size().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def paint(theDisplay:TheDisplay):
		"""display.paint()					  [sensitive public instance method]
		
			Paints the display; i.e., fills it with content.
			Does an automatic curses screen refresh when finished."""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		_logger.debug("display.paint(): Repainting display.")

		display = theDisplay
		client = display.client
		
			# Delegate all of the real work (except for refresh) to the client.
		client.paint()		
				# Note that this is all application-specific.
		
			#|-------------------------------------------------------------------
			#| By the time we get here, the virtual display (background buffer) 
			#| has been painted; now we update the real display (minimally) so
			#| the user can see the changes.
		
		display.refresh()		# Do it here so client doesn't have to.
	
	#__/ End sensitive instance method display.paint().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def refresh(theDisplay:TheDisplay):
		"""display.refresh()				  [sensitive public instance method]
		
			Refreshes the display, based on any accumulated changes to 
			the screen that are not yet visible.							 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		display = theDisplay
		screen = display.screen
		
		if screen is not None:
			screen.refresh()

	#__/ End sensitive public instance method display.refresh().
	

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def update(theDisplay:TheDisplay):
		"""display.update()					  [sensitive public instance method]
		
			Like other sensitive methods, this method should only be 
			called from within the display driver thread, when the 
			display is running; or in a similarly safe context, with 
			display.lock grabbed.

			It updates the physical state of the entire display screen
			(or at least, as much of it as actually needs updating); 
			this updates all sub-windows that have been previously 
			marked as needing updating using win.noutrefresh().				 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#_logger.debug("display.update(): A display update was requested.")
		if not theDisplay.isRunning:
			_logger.debug("display.update(): The display isn't running; ignoring.")
			return

			# Also check to make sure we're in the right thread here?

		doupdate()	# This actually causes the physical display to be updated.
		
	#__/ End sensitive public instance method display.update().


	#|==========================================================================
	#|	Methods for use by clients.							[class code section]
	#|
	#|		The following methods are intended for use by clients, but
	#|		are not referenced by TheDisplay class itself directly.
	#|
	#|		The following public methods may be called from any thread,
	#|		*but* the caller must ensure that he has grabbed display.lock
	#|		before calling them, since they affect the state of the 
	#|		curses display.  Ideally, this should be done by passing them
	#|		to the display.driver thread for execution.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def erase(theDisplay:TheDisplay):
		"""display.erase()					  [sensitive public instance method]
		
				Erases the entire display screen (delayed effect).  That 
				is, this and subsequent drawing operations will take place 
				in the curses display buffer, and the full physical display 
				will be updated on the next display.refresh() operation.	 """ 
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		theDisplay.screen.erase()
			# This does a "lazy erase"; i.e., no effect until next refresh.
		
	#__/ End sensitive public instance method display.erase().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def clear(theDisplay:TheDisplay):
		"""display.clear()					  [sensitive public instance method]
		
				Immediately clears the entire display.  Note that this 
				does not require a subsequent .update() or .refresh() 
				in order to take effect.									 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
			# Dispatch to the underlying curses display.
		theDisplay.screen.clear()	# Equals erase+refresh.
		
	#__/ End sensitive public instance method display.clear().
	

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	theDisplay.drawOuterBorder()	  [sensitive public instance method]
		#|
		#|		This method draws a border just inside the edge of the
		#|		display screen, using the predefined BORDER render style.
		#|
		#|		Presently, this renders by default in a bright cyan text
		#|		color on a black background.
		#|
		#|		The following display attributes are also set up for the
		#|		purpose of making it easier for clients to confine their 
		#|		drawing operations within the 'interior' region within the 
		#|		outer border if they wish (however, a sub-window for this
		#|		purpose is not automatically created by this method):
		#|
		#|			.int_width, .int_height, 
		#|			.int_top, .int_bot, .int_left, .int_right
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def drawOuterBorder(theDisplay:TheDisplay):
		"""theDisplay.drawOuterBorder()		  [sensitive public instance method]
		
				Draws a border just inside the edge of the display screen.	 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		display = theDisplay
		screen = display.screen
		
			# Use predefined render style for drawing borders.
		attr = style_to_attr(BORDER)	
		
		screen.attrset(attr)
		screen.border('|', '|', '-', '-', '/', '\\', '\\', '/')
		screen.attrset(0)
		
			# Set "interior" geometry attributes for just inside outer border.
		display.int_width	= int_width		= display.width  - 2
		display.int_height	= int_height	= display.height - 2
		display.int_top		= int_top 		= 1
		display.int_bot		= int_bot		= int_top + int_height - 1
		display.int_left	= int_left		= 1
		display.int_right	= int_right		= int_left + int_width - 1

	#__/ End sensitive public instance method theDisplay.drawOuterBorder().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def drawCenter(theDisplay:TheDisplay, text:str="", row:int=None,
				   lrpad:str=None, style:RenderStyle=None, extraAttr:int=0,
				   win=None):
				   
		"""display.drawCenter()				  [sensitive public instance method]
		
				Draws the given text string centered on the given line 
				with the given padding and attributes.						 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		display = theDisplay
		screen = display.screen

			# Default the window to the top-level screen if not given.
		if win is None:
			win = screen
			(height, width) = display.get_size()
		else:
			(height, width) = win.getmaxyx()

			# If the row is not specified, use current cursor row.
		if row is None:
			(cy, cx) = win.getyx()
			row = cy

			# Add the left/right padding, if any.
		if lrpad is not None:
			text = lrpad + text + lrpad
			
			# Calculate starting position for text.
		startPos = int((width - len(text))/2)
		
		_logger.debug(f"display.drawCenter(): width={width}, startPos={startPos}")

			# Calculate display attributes.
		attr = extraAttr	# Start with the extra-attrs, if any.
		if style is not None:
			attr = attr | style_to_attr(style)	# Add in the style attrs.
		
			# Go ahead and write the text to the screen or window.
		win.addstr(row, startPos, text, attr)
		
	#__/ End sensitive public instance method display.drawCenter().
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def add_str(theDisplay:TheDisplay, text:str, loc:Loc=None, attr=None):
	
		"""display.add_str() 				  [sensitive public instance method]
		
				Puts the given text string onto the display starting at 
				the given location, with the given attributes.				 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		screen = theDisplay._screen
		
		if loc is None:
			if attr is None:
				screen.addstr(text)
			else:
				screen.addstr(text, attr)
		else:
			if attr is None:
				screen.addstr(loc.y, loc.x, text)
			else:
				screen.addstr(loc.y, loc.x, text, attr)
				
	#__/ End sensitive public instance method display.add_str().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def renderChar(theDisplay:TheDisplay, charcode:int, win=None,
				   defStyle=None):	
		# If defStyle is supplied, it denotes a default style to use, if
		# not special.
		# TODO: Also add loc,attr support.
	
		"""display.renderChar()				  [sensitive public instance method]
		
				Puts the given character (specified by its ordinal 
				character code point integer) on the display screen 
				(or into a specified sub-window); if the given char-
				acter is not normally a visible character, use 
				special styles to render it visible.	 		 			 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		display = theDisplay
		screen = display.screen
		
		if defStyle is not None:
			baseAttrs = style_to_attr(defStyle)
		else:
			baseAttrs = 0

		if win is None:
			win = screen	# Use the display's top-level window by default.
		
		render_char(win, charcode, baseAttrs)		# Function defined in .controls module.

	#__/ End sensitive public instance method display.renderChar().


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def renderText(theDisplay:TheDisplay, text:str="", win=None, hang:int=0,
					promptChar = None, defStyle = None):
		"""display.renderText()				  [sensitive public instance method]
		
				This method renders the given text to the given curses
				window, using special styles as needed to render 
				control characters.  If the window is not specified,
				the top-level screen is used.  If the width of the 
				window is reached, we display a grayed-out backslash 
				('\') character at the end of the line, and wrap around 
				to the next line.  Various whitespace characters are also
				handled appropriately.
				
			Arguments:
			~~~~~~~~~~

				hang [int] - If this is provided, it denotes a number of
					spaces of hanging indent to output after each line
					break.

				promptChar [char] - If this is provided, it denotes a 
					character such that, every character up to and
					including the first occurrence of that character is
					rendered in 'prompt' style by default.

				defStyle [RenderStyle] - If this is provided, then the
					given render-style is used for every character that
					is not rendered in a special style.
		

			Return values:
			~~~~~~~~~~~~~~
			
				This method returns a pair (yx2pos, pos2yx) of dictionaries
				that map between positions in the text and (y,x) positions
				within the window.  This is to facilitate editing.
			
			
			Exceptions thrown:
			~~~~~~~~~~~~~~~~~~
			
				
				
				"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		display = theDisplay
		screen = display.screen
		
		if win is None:
			win = screen

		promptDone = False	# Prompt is not done yet.

		hangPad = ' '*hang	# Left pad string to use for hanging indent.

		yx2pos = dict()		# Map from (y,x) pairs to positions in string.
		pos2yx = dict()		# Map from positions in string to (y,x) pairs.

			# Get dimensions of selected window.
		(height, width) = win.getmaxyx()

			# We need to keep track of whether the last character output
			# was a carriage return, because we treat LF after CR as null.
		lastCharWasCR = False
		
		pos = 0		# Position in text.
		for char in text:
		
			ch = ord(char)
			
				#|----------------------------------------------------
				#| Next, if we are already at the right margin, then,
				#| before rendering the character, add a grayed-out '\'
				#| character to call attention to the line-wrapping.
				#| Exception: If the character is already a line break
				#| character (CR or LF), then it will take care of 
				#| wrapping itself.
			
			if ch != CR and ch != LF:
			
					# Get current cursor position within window.
				(cy, cx) = win.getyx()
				
					# Are we already at the right margin?
				if cx >= width - 2:
					# Note: width-1 is the actual rightmost column.
					# but, we want to avoid displaying there anyway
					# to avoid triggering a curses exception on the
					# last line of the window.  So instead, we see 
					# if we are already at width-2.  This results in
					# an effective 1-character pad on the right side.
				
					attr = style_to_attr(WHITESP)
					win.addstr('\\', attr)	
						# Note this is actually a single blackslash character.
						
					win.addstr('\n' + hangPad)
						# And this actually goes to the next line.

			#__/ End if possible automatic line-wrap.
		
				# Update pos <--> xy maps.
			(cy, cx) = win.getyx()
			yx2pos[(cy,cx)] = pos
			pos2yx[pos] = (cy, cx)
			
			# If we're supposed to be looking for a prompt char
			# and we're not done with displaying the prompt, then
			# use PROMPT render style.
			if promptChar is not None and not promptDone:
				style = PROMPT
			else:
				style = defStyle	# Just uses the default style.

			# Use try/except here to catch if we try to draw 
			# outside the window.
			try:
				# This actually displays the current character.			
				display.renderChar(ch, win=win, defStyle=style)
			except curses.error as e:
				msg = str(e)
				
				# Wrap up some state information that the caller
				# might want to know in a RenderExcursion exception.
				excursion = RenderExcursion(
					"display.renderText() got curses error: " + msg, 
					ch, pos, Loc(cy, cx), yx2pos, pos2yx)
				
				# Throw that back to the caller.
				raise excursion
			
				# If we just rendered the prompt character, we're done
				# with the prompt part of the string.
			if promptChar is not None and ch == ord(promptChar):
				promptDone = True

			#/------------------------------------------------------------------
			#|	Non-space whitespace characters need to be handled specially 
			#|	here. Specifically:
			#|
			#|		HT (TAB) - If we're not already at a tab stop,
			#|			then move forward to the next tab stop.
			#|
			#|		VT (vertical tab) - Move cursor straight downwards 
			#|			into next line.
			#|
			#|		LF (line feed) - We interpret a bare LF the same as
			#|			a CR/LF sequence; that is, we put the cursor at
			#|			the start of the next line.
			#|
			#|		CR (carriage return) - Put the cursor at the start 
			#|			of the next line.
			#|
			#|		FF (form feed) - Go down two lines and to start of
			#|			line; also display a form separator in between.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
			if ch == TAB:	# Move forward to next tab stop, if needed.
			
				tabsize = 8
				#tabsize = get_tabsize()		# Get current tab size.
				
					# Get current cursor position within window.
				(cy, cx) = win.getyx()
				
					# If we're already at a tab stop, this is 
					# because we were just left of it and then
					# displayed a gray '>'. So now we don't need
					# to move at all.  Otherwise, we output a
					# real tab char to go to the next tab stop.
				if cx % tabsize != 0:
					win.addstr('\t')
			
			elif ch == VT:	# Move down one line, without CR.
			
				# Note that here, we are actually one column to the right of 
				# where we were due to having displayed one gray 'v' to show
				# the vertical tab.  So, we move one position down and to the
				# left, to implement the straight-down motion.
			
					# Get current cursor position within window.
				(cy, cx) = win.getyx()
				
					# Move one cell down and to the left.
				win.move(cy + 1, cx - 1)
				
			elif ch == LF:	# Line feed: Suppress if we just output CR; otherwise just do a newline.
			
				if not lastCharWasCR:
					win.addstr('\n' + hangPad)	# Output newline.
			
			elif ch == CR:	# Carriage return:  Output newline, and remember last char was CR.

				win.addstr('\n' + hangPad)		# Output newline.
					# Now remember we already did this, in case next character is NL.
				lastCharWasCR = True	
				
			elif ch == FF:	# Newline, centered page separator, newline.

				win.addstr('\n')
				(ht, wd) = win.getmaxyx()
				pageSep = "* * *"
				nSpaces = int(((wd - 1)-len(pageSep))/2)
				spaces = ' '*nSpaces
				win.addstr(spaces + pageSep + '\n' + hangPad)

			
			#__/ End if/elif for handling whitespace characters.
			
			# Remember to reset lastCharWasCR after non-CR characters.
			if ch != CR:
				lastCharWasCR = False
	
			pos = pos + 1
	
		#__/ End for loop over characters in string.
	
		return (yx2pos, pos2yx)
	
	#__/ End sensitive public instance method display.renderText().
	

	def setBlinkOn(theDisplay:TheDisplay):
		
		display = theDisplay
		screen = display.screen
		
		#(sy, sx) = getsyx()					# Get cursor screen coordinates.
		#_logger.debug(f"Blink ON at ({sy},{sx})")

		attrs = style_to_attr(BRIGHT_CURSOR)
		screen.chgat(1, attrs)

		#cursdata = screen.inch(sy, sx)		# Fetch data from screen at cursor loc.
		#attrs = cursdata >> 8				# Get just the attrs part.
		#attrs = attrs | A_BLINK				# Make sure A_BLINK (bright background) attribute is on.
		#screen.chgat(1, attrs)				# Change attributes of 1 character at that loc.
		#screen.refresh()					# Refresh screen to push change.
		#curs_set(2)


	def setBlinkOff(theDisplay:TheDisplay):

		display = theDisplay
		screen = display.screen
		
		#(sy, sx) = getsyx()					# Get cursor screen coordinates.
		#_logger.debug(f"Blink OFF at ({sy},{sx})")

		attrs = style_to_attr(DIM_CURSOR)
		screen.chgat(1, attrs)

		#cursdata = screen.inch(sy, sx)		# Fetch data from screen at cursor loc.
		#attrs = cursdata >> 8				# Get just the attrs part.
		#attrs = attrs & ~A_BLINK			# Make sure A_BLINK (bright background) attribute is off.
		#screen.chgat(1, attrs)				# Change attributes of 1 character at that loc.
		#screen.refresh()					# Refresh screen to push change.
		#curs_set(1)


#__/ End singleton class TheDisplay.

	
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/display.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
