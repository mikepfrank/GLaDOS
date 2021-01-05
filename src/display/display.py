#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 display/display.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		display/display.py				 [Python module source file]
	
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
		
			Functions:
			----------
		
			Types:
			------
			
				Loc [struct]	- An x,y location in a screen or window.
				
			
			Globals:
			--------
			
	
	Dependencies:
	-------------
	
		This module references...
		
		This module is referenced by...
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

			#|---------
			#| Classes.
		
		'TheDisplay',		# Singleton class; anchor for module.
		
			#|-----------
			#| Functions.
		
			# Drawing functions.
		'draw_rect', 'addLineClipped', 'addTextClipped',
		

			#|--------------------
			#| "Type" definitions.
		
		'Loc',			# A location struct in a screen/window.    [struct type]
		'KeyEvent',		# An event caused by a keypress. 		   [simple type]
		
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
		controlnames, 	# Array: Names of characters 0-33, used in KeyEvent.
		iscntrl, 		# Function: Is this code a 7-bit ASCII control? Used in KeyEvent.
		DC4				# Constant: Code point for Device Control 4 (control-T).  Used in theDisplay.do1iteration().
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
		sysName,			# Used just below.
		getComponentLogger,	# Used just below.
		LoggedException,	# DisplayException inherits from this.
		FatalException		# We derive TerminateServer from this.
	)
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.
global _sw_component
_sw_component = sysName + '.' + _component


			#|------------------------------------------------------------------
			#| Import sibling modules we need from within the display package.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from .colors import *		# All color-related definitions.

	# Imports related to rendering of control/whitespace characters.
from .controls import (
		render_char			# Renders any 7/8-bit character in a curses window.
	)

from .keys import (
		KeyEvent,			# Simple type for holding key information.
		TheKeyBuffer,		# Facility for sophisticated key input processing.
	)

	# Imports relating to display-specific threads.
from .threads import (
		TUI_Input_Thread,	# Thread for running the text UI main loop.
		DisplayDriver,		# Thread for coordinating display output tasks.
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

class Loc:
	"""This class effectively just defines a simple struct representing a 
		location within the screen or a window."""
	def __init__(thisloc, y=None, x=None):
		thisloc.x = x
		thisloc.y = y

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

		#|===========================================
		#| Exception classes provided by this module.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class DisplayException(LoggedException):
	
	"""This is an abstract base class for all exception types generated
		by the text display facility."""
	
	defLogger = _logger		# Use the display package's logger.


class TerminateServer(DisplayException, FatalException):

	"""This is an exception type that is thrown when the display facility
		is requesting the entire GLaDOS server process to shut down.  This
		generally happens because we caught a ^T (terminate) keystroke
		that was typed by the system operator."""

	pass


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.TheDisplay					   		[public singleton class]
		#|
		#|		This singleton class is the main class that anchors the 
		#|		'display' module and manages the underlying curses display 
		#|		interface.
		#|
		#|		Applications do not need to construct or use this directly,
		#|		but can go through their application-specific subclass of
		#|		the DisplayClient class, above.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

@singleton
class TheDisplay:

	"""This is a singleton class.  Its sole instance represents the text display
		screen, which is managed by the curses library.	 For now, it assumes that 
		the display is compatible with xterm/Putty (8 colors, Western script)."""

	def __init__(theDisplay):
		"""Initializes the display system."""

		display = theDisplay

			# Mark this display as not running yet, to make sure we don't try 
			# to do anything with it until it's actually running.
		display._running = False		# Display is not up and running yet.

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
			
		# Nothing else to do here yet. Nothing really happens until .start() is called.
	
	#__/ End singleton instance initializer for class TheDisplay.
	
	@property
	def lock(theDisplay):
		"""
			Reentrant lock for controlling concurrent access to the underlying 
			curses library.  A thread should use the following syntax to grab
			the lock within the dynamical scope of a lexical block of code:
			
					with display.lock: 
						...(statements)...
						
			This will ensure that the lock is released when the code block is
			exited, whether normally or via an exception.  This is important for
			preventing deadlocks.
		"""
		return theDisplay._lock
	
	@property
	def client(theDisplay):
		return theDisplay._client

	@property
	def isRunning(theDisplay):
		return theDisplay._running

	@property
	def running(theDisplay):
		"""Is the display currently running?"""
		return theDisplay.isRunning

	@property
	def width(theDisplay):
		return theDisplay._width

	@property
	def height(theDisplay):
		return theDisplay._height

	@property
	def driver(theDisplay):
		"""Returns a handle to the display's centralized driver thread."""
		return theDisplay._driver
	
	
	def setClient(theDisplay, displayClient:DisplayClient):
	
		"""Sets the display to be managed by the given client (which should be
			an instance of DisplayClient or one of its subclasses)."""
			
		theDisplay._client = displayClient
	
	
	def start(theDisplay, waitForExit:bool=False):
	
		"""This actually starts the display running.  If waitForExit is not
			provided or is False, then the display's TUI input loop is started 
			up in a background thread, and this .start() method returns 
			immediately.  Otherwise, if waitForExit=True is provided, this 
			method does not return until the input loop is terminated (either 
			through a user interrupt, or because some other, un-handled 
			exception occurred in it)."""
		
		_logger.debug(f"display.start(): Starting display with waitForExit={waitForExit}...")

		display = theDisplay
		
			# First, we create the thread to manage the main input loop for the
			# human user's TUI (text user interface).
		tuiInputThread = TUI_Input_Thread(target=display.run)
		display._tuiInputThread = tuiInputThread	# Remember it.
		
			# This starts the new thread in the background. This will bring up
			# the curses interface.  Once it's up, however, all I/O to/from it 
			# should be managed through the separate DisplayDriver thread.
		tuiInputThread.start()
			
			# If the user didn't want the input loop to run in the background,
			# this simply waits for the TUI input thread to terminate.
		if waitForExit:
			_logger.debug("display.start(): Waiting for TUI input thread to exit...")
			try:
				tuiInputThread.join()
			except Exception as e:
				_logger.FATAL("display.start(): Uncaught exception [{str(e)}] in TUI input thread.")
				raise
				

		_logger.debug("display.start(): Returning.")

	#__/ End singleton instance method theDisplay.start().
	
	
	def run(theDisplay):
	
		"""This method is responsible for bringing up and operating the entire
			display, and bringing it down again when done.	It ought to be run 
			in its own thread (specifically, TUI_Input_Thread), so that other 
			subsystems can asynchonously communicate with it if needed.  The
			display.start() method automatically arranges for this method to 
			be executed by the TUI_Input_Thread."""

		display = theDisplay
			
		_logger.debug("display.run(): Starting the display running.")

		#|---------------------------------------------------------------------
		#| NOTE: wrapper() is a curses function, so we acquire the display 
		#| lock here to ensure thread-safety.  However, although we acquire 
		#| the display lock while entering and exiting the wrapper function, 
		#| internally to ._manage(), the lock is released whenever we're not 
		#| actively using it.  This is needed to avoid deadlines.

		with display.lock:
			# Call the standard curses wrapper on our private display management method, below.
			wrapper(theDisplay._manage)
				# ._manage() sets up the display and runs our main input loop.
		
		# If we get here, then the display driver has exited, and the display was torn down.
		theDisplay._screen = None	# It's no longer valid anyway.
		
		_logger.debug("display.run(): Finished running the display.")

	#__/ End singleton instance method theDisplay.run().


	@property
	def screen(theDisplay):
		"""This handles getting theDisplay.screen attribute.
			Note this is an error if the display isn't running."""
		return theDisplay._screen


	@property
	def width(theDisplay):
		return theDisplay._width


	def update(theDisplay):

		"""This method should only be called from within the display
			driver thread, when the display is running.

			It updates the physical state of the entire display screen
			(or at least, as much of it as actually needs updating); this
			updates all sub-windows that have been marked as needing
			updating using win.noutrefresh()."""

		#_logger.debug("display.update(): A display update was requested.")
		if not theDisplay.isRunning:
			_logger.debug("display.update(): The display isn't running yet; ignoring.")
			return

		# Check to make sure we're in the right thread.

		doupdate()	# This actually causes the physical display to be updated.
		


	def refresh(theDisplay):
		screen = theDisplay._screen
		screen.refresh()


	def erase(theDisplay):
		"""Erases the display.""" # "Lazy erase"; no effect until next refresh.
		theDisplay.screen.erase()
	

	def clear(theDisplay):
		"""Clears the display."""
			# Dispatch to the underlying curses display.
		theDisplay.screen.clear()	# Equals erase+refresh.


	def renderChar(theDisplay, charcode):	# TODO: Add loc,attr support.
		"""Puts the given character on the display; if it is not normally
			a visible character, use special styles to render it visible."""
		screen = theDisplay._screen
		render_char(screen, charcode)	# Function defined earlier.


	def add_str(theDisplay, text:str, loc:Loc=None, attr=None):
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
				
	#__/ End singleton instance method theDisplay.add_str().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	theDisplay.drawOuterBorder()			  	[public instance method]
		#|
		#|		This method draws a border just inside the edge of the
		#|		display screen, using the predefined BORDER render style.
		#|
		#|		Presently, this renders by default in a bright cyan text
		#|		color on a black background.
		#|
		#|		The following display attributes are also set up for the
		#|		purpose of facilitating clients to draw within the 'interior'
		#|		region within the outer border if they wish (however, a 
		#|		sub-window is not created):
		#|
		#|			.int_width, .int_height, 
		#|			.int_top, .int_bot, .int_left, .int_right
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def drawOuterBorder(theDisplay):
		"""Draw a border just inside the edge of the display screen."""

			# Use predefined render style for drawing borders.
		attr = style_to_attr(BORDER)	
		
		display = theDisplay
		screen = display.screen
		
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

	#__/ End method theDisplay.drawOuterBorder().


	def drawCenter(theDisplay:TheDisplay=None, text:str="", row:int=None,
				   lrpad:str=None, style:RenderStyle=None, extraAttr:int=0):
		"""Draws the given text string centered on the given line with the
			given padding and attributes."""
		
		display = theDisplay
		screen = display.screen
		width = display.width

			# Add the left/right padding, if any.
		if lrpad is not None:
			text = lrpad + text + lrpad
			
			# Calculate starting position for text.
		startPos = int((width - len(text))/2)
		
			# Calculate display attributes.
		attr = extraAttr	# Start with the extra-attrs, if any.
		if style is not None:
			attr = attr | style_to_attr(style)	# Add in the style attrs.
		
			# Go ahead and write the text to the screen.
		screen.addstr(row, startPos, text, attr)
	
	
	def paint(theDisplay):
		"""Paints the display; i.e., fills it with content.
			Does an automatic curses screen refresh when finished."""

		_logger.debug("display.paint(): Repainting display.")

		display = theDisplay
		client = display._client
		screen = display.screen
		
			# Delegate the work (except for refresh) to the client.
		client.paint()		
				# Note this is all application-specific.
		
			#|-------------------------------------------------------------------
			#| By the time we get here, the virtual display (background buffer) 
			#| has been painted; now we update the real display (minimally) so
			#| the user can see the changes.
		
		if screen != None:
			screen.refresh()		# Do it here so client doesn't have to.
	
	#__/ End singleton instance method theDisplay.paint().


	def get_max_yx(theDisplay):
		"""Returns a pair (y,x) giving the coordinates of the lower-right 
			cell of the display."""
		return (theDisplay._max_y, theDisplay._max_x)


	def get_size(theDisplay):
		"""Returns a pair (h,w) giving the height of the display in lines,
			and the width of the display in columns (character cells).
			Note this is only valid/current after calling .resize()."""
		return (theDisplay._height, theDisplay._width)
	

	def resize(theDisplay):
		"""Call this method when you want to handle a resize event."""

		display = theDisplay
		client = display.client

			# Find out the new dimensions of the window.
		display._check_size()
		(height, width) = display.get_size()

		#----------------------------------------------------------
		# Now we potentially need to resize the window structures
		# within curses, if the terminal size has actually changed.

		_logger.debug(f"display.resize(): Resizing terminal to {(height,width)}.")
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
		
		# display.teardownAndRebuild()	# This raises a RequestRestart exception.

		# If we have a client attached, tell it to handle the resize internally.
		if client != None:
			client.handle_resize()

		_logger.debug("display.resize(): Repainting entire display after resize...")

			# Now that everything is consistent, repaint the entire display.
		display.paint()

	#__/ End singleton instance method theDisplay.resize().


	#|==========================================================================
	#|	Private methods.									[class code section]
	#|
	#|		The following methods should not normally need to be directly 
	#|		called (or overridden) by applications.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def _initColorPairs(theDisplay):
		"""This initializes the color pairs, assuming 8 standard colors and 64 pairs."""
		for pair_index in range(1,64):		# Iterate over 6-bit color pair codes.
		
				# Obtain the background color as the most-significant 3 bits.
			bgcolor = int(pair_index / 8)
			
				# Obtain the foreground color from the least-significant 3 bits.
			fgcolor = (pair_index - 1) % 8
				# The -1 (+7) here is needed because pair 0 has fg=white standardly.
			
				# Make sure that particular color pair is set up properly as we want it.
			_logger.info(f"Creating color pair #{pair_index} = (fg: {fgcolor}, bg: {bgcolor}).")

			init_pair(pair_index, fgcolor, bgcolor)
			
		#__/ End loop over all customizable color-pair indices.

	#__/ End private singleton instance method theDisplay._initColorPairs().
	

	def _check_size(theDisplay):
		"""Check the current size of the display screen."""

		screen = theDisplay._screen

			#----------------------------------------------------------------
			# It's important to note that .getmaxyx() will not work properly
			# if either the LINES and/or COLUMNS environment variable is set;
			# those values will override the current window size.  So please
			# DO NOT SET THESE VARIABLES unless you really want your app to
			# treat the window size as fixed instead of self-adjusting on 
			# resize events.
			
		(height, width) = screen.getmaxyx()
		_logger.debug(f"._check_size(): .getmaxyx() returned {(height,width)}.")

			# Remember the new window size.
		theDisplay._width  = width
		theDisplay._height = height
		
			# Calculate and store bottom-right cell coordinates as well.
		theDisplay._max_x  = width - 1
		theDisplay._max_y  = height - 1

	#__/ End private method theDisplay._check_size().


	def _init(theDisplay):
		"""Initializes the curses display. Client should be attached first."""

		_logger.debug("display._init(): Initialziing the display.")

			# Initialize the color pairs to be set up like we want.
		theDisplay._initColorPairs()
		
			# This effectively just measures & then paints the display.
		theDisplay.resize()
	
	#__/ End private singleton instance method theDisplay._init().
	
	
	def _has_buffered_keys(theDisplay):

		if not hasattr(display, '_bufferedKeys'):
			return False

		keybuf = display._bufferedKeys

		if keybuf is None:
			return False

		if keybuf == "":
			return False

		return True


	def _do1iteration(theDisplay):
	
		"""This method executes just a single iteration of the main event 
			loop.  It runs in the TUI input thread."""
			
		# Suppress this to prevent excessive logging since this loops
		# runs 20 times per second.
		#_logger.debug("Doing one main-loop iteration...")
		
		display = theDisplay
		
		dispDrv = display.driver
		screen = display.screen
		client = display._client
		thread = display._tuiInputThread
		
			#/------------------------------------------------------------------
			#|	OK, now the following code implements a pattern of display 
			#|	lock/unlock actions that deserves some explanation.  We lock 
			#|	the display before getting an event.  If the key is a 
			#|	high-priority event, such as a window resize event, then we 
			#|	handle it right away, in one atomic process, that is, without 
			#|	releasing the lock in between.  This is important to allow the 
			#|	effects of e.g., a window resize to finish playing out before 
			#|	we try to do anything else with the display.  However, for 
			#|	less-critical events, like ordinary keypresses, we go ahead 
			#|	and release the lock before processing them, less urgently, 
			#|	in the display driver thread.
			
		with display.lock:		# Lock the display temporarily in this TUI input thread.
		
				# First, we make sure the display is up-to-date before asking for
				# anything from the user (how's he supposed to respond otherwise?)
			display.update()
		
			#/----------------------------------------------------------------
			#| This try/except clause allows us to handle keyboard interrupts
			#| (i.e., interrupts caused by the user hitting ^C) and other
			#| exceptions cleanly; however, please note that we previously
			#| turned on raw() mode, so, we don't expect keyboard interrupts
			#| to actually occur.
			
				# Initialize these key-related variables to None until we have 'em.
			ch = None; event = None

			try:
			
					# Get the next key event from our input processing system in keys.py.
				event = TheKeyBuffer().get_next_key(screen)
				ch = event.keycode

				#ch = screen.getch()		# Gets a 'character' (keycode) ch.
					# Note earlier, we configured .getch() to be nonblocking.

				# Commented out because wide characters don't seem very useful.
				#wch = screen.get_wch()
				#_logger.debug(f"display._do1iteration(): Got a wide character: [{wch}]")

			except curses.error as e:	# If get_wch() was used, this means no input was received yet.

				ch = ERR

			except KeyboardInterrupt as e:				# User hit CTRL-C?
				# Note that currently, we should not get these events anyway, since
				# earlier, we put the terminal in raw() mode.

				_logger.debug("display._do1iteration(): Caught a keyboard "
							  "interrupt during screen.getch().")

				ch = KEY_BREAK		# Translate to BREAK key.

			except Exception as e:

				_logger.fatal("display._do1iteration(): Unknown exception "
							  f"during screen.getch(): {str(e)}.")
				raise e
				
			else:
					# Note we suppress debug output if the keycode is ERR (= none yet) to
					# prevent excessive logging.

				if ch != ERR:
					_logger.debug(f"display._do1iteration(): Got character code {ch}.")

			#__/ End try/except clause for keyboard input (.getch()) call.
			
				#|------------------------------------------------------------
				#| If we don't have an event by now, make one.  Generally this
				#| only happens in the KEY_BREAK case above.

			if event is None:
				event = KeyEvent(keycode = ch)


			#/------------------------------------------------------------------
			#|	OK, if we get here, there were no un-handleable exceptions 
			#|	during .getch(), and now we just need to figure out if there
			#|	was a high-priority event that we need to handle before we 
			#|	exit the 'with' clause and release the display lock.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
				#/--------------------------------------------------------------
				#| First case: If the user pressed control-T, then this is a 
				#| command to immediately terminate the entire GLaDOS server 
				#| application process.
			
			if ch == DC4:		# ^T = Device control 4, primary stop, terminate.
				_logger.fatal("display._do1iteration(): Exiting due to ^T = terminate key.")
				raise TerminateServer("Terminating server because user pressed ^T.")
			
				#/--------------------------------------------------------------
				#| Second case: If we received a Resize event, then we need 
				#| to try to handle it as best we can before we try to do 
				#| anything else with the display. (Because, handling resize 
				#| properly is difficult enough without having to worry that 
				#| other threads might try to interfere with what we're doing.)
			
			if ch == KEY_RESIZE:
				_logger.info("display._do1iteration(): Got a resize event; handling at high priority.")
				display.resize()
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
				#| our checking for new inputs, and reduce CPU time wasted in 
				#| polling.  The time here is 50 milliseconds or 1/20th of a 
				#| second.  If the time given here was too long, the console 
				#| would seem slow to respond to input.  If the time was too 
				#| short, the main loop will waste too much CPU time with 
				#| repeated input polling and display updates will be slower.

			sleep(0.05)		# Sleep for 0.05 second = 50 milliseconds.
			#sleep(1)
					
			return		# I.e., complete this main-loop iteration normally.
		
		#/----------------------------------------------------------------------
		#| Normally, we handle all events by handing them off to the display 
		#| driver thread (which is a worker thread).  The advantage of doing 
		#| things this way is that other threads (also going through the
		#| centralized display driver thread) can asynchronously be doing other
		#| stuff with the display (writing updates, etc.) and the handling of 
		#| key events will be interleaved with that other work automatically in 
		#| a thread-safe way.  Also there is some automated logging work done.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		dispDrv(lambda: client.handle_event(event), desc="Handle event")
			# Note this waits for the event handler to finish before we get another
			# key. This helps prevent the input loop from "getting ahead" of the
			# display, and building up a big backlog of input-processing work to 
			# do in the display queue.  However, if we preferred, we could also 
			# change this to kick off the handler work to be done in the 
			# background using dispDrv.do().
			
	#__/ End private singleton instance method display._do1iteration().
	
	
	def _runMainloop(theDisplay):
	
		"""This is the main event loop.  It runs in the TUI input thread."""
		
		_logger.debug("display._runMainloop(): Starting main event loop.")

		display = theDisplay
		
		dispDrv = display.driver
		screen = display.screen
		#client = display._client
		thread = display._tuiInputThread
		
			#--------------------
			# Set the input mode.

		# We could put this in a method and send it to the driver, but
		# just grabbing the lock instead here 'cuz it's easier.
		with display.lock:
			raw()					# Suppresses processing of ^C/^S/^Q/^Z
			screen.timeout(0)		# Non-blocking read on getch(), zero delay.
			screen.keypad(True)		# Interpret keypad escape sequences.
			#cbreak()				# Not doing this because it doesn't suppress ^C/^S/^Q.
			#halfdelay(2)			# .getch() Returns ERR after 0.1 secs if no input seen.
				# Not doing that because it wastes time to have a timeout.

			#-----------------------------------------------------------------
			# Here's the actual main loop. Keep going until requested to exit,
			# or there is an exception.
				
		while not thread.exitRequested:
			
			display._do1iteration()		# Does one iteration of the main loop.

		#__/ End main user input loop.
		
		_logger.debug(f"display._runMainloop(): Exited main loop.")

	#__/ End private singleton instance method theDisplay._runMainloop().
	
	
	def _manage(theDisplay,
			screen	# This is the top-level curses window for the whole terminal screen.
		):		
		
		"""Private method to 'manage' the curses display. It is called by 
			theDisplay.run(), above.  Note that when this manager method 
			returns, the entire display will be torn down. So, it should 
			not exit until we are completely done with using the display.
			
			Note also this method does not run within the DisplayDriver
			thread. This method actually runs in the TUI input loop
			thread, although it hands off input events to event handlers 
			running in the DisplayDriver thread."""
		
		_logger.debug("display._manage(): Starting up.")

		display = theDisplay
		dispDrv = display.driver		# Display driver thread.

			# Store our top-level window (screen) for future reference.
		display._screen = screen

			#|-----------------------------------------------------------
			#| Mark display as now being in the "running" state, where we
			#| can do stuff with it. We need to do this now to make sure
			#| that subsequent display operations won't suppress 
			#| themselves because they think the display isn't running
			#| yet.

		try:	# Cleanup properly in case of exception-driven exit.

			display._running = True			# Display is now running.

				#|------------------------------------------------------------------
				#| This releases the display lock that we acquired earlier in the 
				#| 'with' statement in the .run() method.  We have to do this now
				#| because the display driver is about to need it.

			display.lock.release()
	
				# The very first thing we do with the display is to
				# initialize it. We let the display driver thread do this.
			dispDrv(display._init, desc="Initialize display")
				# Note this call waits for initialization to be completed.

				# Now we can start the main loop.
			display._runMainloop()		# Run the main loop.

		finally:
			display._running = False		# Display is no longer running.
			# Now we have to re-acquire the lock because we're about to
			# tear down the display when we exit the wrapper.
			display.lock.acquire()


		_logger.debug("display._manage(): Exiting.")

	#__/ End private singleton instance method theDisplay._manage().

#__/ End singleton class TheDisplay.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/display.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%