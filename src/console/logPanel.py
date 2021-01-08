#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 console/logPanel.py
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		console/logPanel.py				 [Python module source file]
		
	MODULE NAME:	console.logPanel
	IN PACKAGE:		console
	FULL PATH:		$GIT_ROOT/GLaDOS/src/console/logPanel.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.console (GLaDOS System Console)


	MODULE DESCRIPTION:
	===================

		This module implements a panel to be displayed on the main system 
		console display for the GLaDOS server application.
		
		This panel displays the last few lines of the system log file,
		color-coded so that different types of log lines will stand out:
		
			Logging
			Level	  Color Scheme
			-------	  ---------------------
			DEBUG	- Bright blue on black.
			INFO	- Magenta on black.
			NORMAL	- Green on black.
			WARNING	- Yellow on black.
			ERROR	- Red on black.
			FATAL	- Bright yellow on red.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| 	The following is literally a vertatim example of what the log panel looked 
	#|	like on system startup, in one test:
	#|	
	#|		+--- System Log ------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
	#|		| ========================+==========================+======================================+==================================================+=========================================================================================== |
	#|		| YYYY-MM-DD hh:mm:ss,msc | SysName.appName.pkgName  | ThreadName: Component      role      |     sourceModuleName.py:ln# : functionName()     | LOGLEVEL: Message text                                                                     |
	#|		| ------------------------+--------------------------+--------------------------------------+--------------------------------------------------+------------------------------------------------------------------------------------------- |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.display    |   Thread-2: GLaDOS.display DisplDrvr |              display.py:1588: paint()            |    DEBUG: display.paint(): Repainting display.                                             |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.display    |   Thread-2: GLaDOS.display DisplDrvr |                panel.py:408 : paint()            |    DEBUG: panelClient.paint(): Repainting panel client                                     |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.display    |   Thread-2: GLaDOS.display DisplDrvr |                panel.py:261 : paint()            |    DEBUG: panel.paint(): Repainting panel 'System Log'.                                    |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.console    |   Thread-2: GLaDOS.display DisplDrvr |              console.py:348 : drawHeader()       |    DEBUG: logPanel.drawHeader(): Drawing header sub-window of log panel...                 |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.console    |   Thread-2: GLaDOS.display DisplDrvr |              console.py:357 : drawHeader()       |    DEBUG: logPanel.drawHeader(): Reading log panel header data from file for first time.   |
	#|		| 2021-01-02 20:30:16,512 | GLaDOS.server.console    |   Thread-2: GLaDOS.display DisplDrvr |              console.py:445 : _init_data()       |    DEBUG: panel._init_data(): Initializing panel content data to empty list.               |
	#|		| 2021-01-02 20:30:16,512 | GLaDOS.server.console    |   Thread-2: GLaDOS.display DisplDrvr |              console.py:292 : launch()           |    DEBUG: logPanel.launch(): Starting the feeder thread.                                   |
	#|		| 2021-01-02 20:30:16,512 | logmaster                |   Thread-3: GLaDOS.console LogFeeder |            logmaster.py:2254: update_context()   |    DEBUG: ThreadActor.update_context(): Updating logging context to role [LogFeeder] & com |
	#|		| 2021-01-02 20:30:16,514 | GLaDOS.server.display    |   Thread-4: GLaDOS.display TUI_Input |              display.py:1722: _runMainloop()     |    DEBUG: display._runMainloop(): Starting main event loop.                                |
	#|		| 2021-01-02 20:30:16,514 | GLaDOS.server.console    |   Thread-3: GLaDOS.console LogFeeder |              console.py:203 : main()             |    DEBUG: logFeeder.main(): Creating 'tail -f' subprocess to feed log panel.               |
	#|		| 2021-01-02 20:30:16,514 | GLaDOS.server.console    |   Thread-3: GLaDOS.console LogFeeder |              console.py:208 : main()             |    DEBUG: logFeeder.main(): Command words are: [tail -n 12 -f log/GLaDOS.server.log]       |
	#|		| 2021-01-02 20:30:16,516 | GLaDOS.server.console    |   Thread-3: GLaDOS.console LogFeeder |              console.py:232 : main()             |    DEBUG: logFeeder.main(): Just added my very first line of log data to the panel.        |
	#|		\-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------/
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	#/==========================================================================
	#|	1. Module imports.								   [module code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from threading	import	RLock			# To maintain consistency of log data.
from os 		import 	path, popen		# We use 'popen' to grab 'head' output.

import subprocess	
	# From this system module, we use 'Popen' and 'PIPE' for streaming log
	# output data from a'tail' command.


		#|----------------------------------------------------------------------
		#|	Imports and related globals to support logging facility.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.logmaster import (
		sysName,			# Used just below.
		ThreadActor,		# Log feeder thread is subclassed from this.
		getComponentLogger 	# Used just below.
	)

global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component

	# Maybe should move this to LogPanel initializer?
global logFilename
logFilename = path.join('log', 'GLaDOS.server.log')
	# It would be cleaner to just retrieve this from the logmaster package.


		#|----------------------------------------------------------------------
		#|	Import names we need from the display module.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import curses

from display.colors		import (

		HEADER,				# Render style we use for the log panel header area.
		PLAIN,				# Render style we use for log lines of unknown level.
		DEBUG_STYLE,		# Render style we use for debug-level log messages.
		INFO_STYLE, 		# Render style we use for input-level log messages.
		GOOD_STYLE,			# Render style we use for normal-level log messages.
		WARNING_STYLE,		# Render style we use for warning-level log messages.
		ERROR_STYLE,		# Render style we use for error-level log messages.
		CRITICAL_STYLE,		# Render style we use for critical-level (or fatal) log messages.
		style_to_attr,		# Converts render styles to display attributes.

	)
	
from display.drawing	import (

		addLineClipped, 	# Adds a line of text to a window, but with right-clipping.
		addTextClipped		# Adds a body of text to a window, but with right-clipping.

	)

from	display.panel	import (

		Panel,			# This is the base class from which we derive the LogPanel.
		FILL_BOTTOM		# This is the panel placement specifier we use for the log panel.
		
	)


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|
	#|	Panel subclasses for specific panels:
	#|	.....................................
	#|
	#|		LogPanel		- This is the panel to display the system log 
	#|							across the bottom of the screen.
	#|
	#|
	#|	Subordinate classes:
	#|	....................
	#|
	#|		LogFeeder	- This is a thread that feeds log data to the LogPanel.
	#|						(It and LogPanel could be moved out together to a
	#|						new module 'logPanel'.)
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class LogPanel: pass	# Forward declaration for type hints.

# A LogFeeder is a ThreadActor whose job it is to spool log file data
# into the content area of the log panel.

class LogFeeder(ThreadActor):
	
	defaultRole			= 'LogFeeder'
	defaultComponent	= _sw_component		# GLaDOS.console component.
	
	def __init__(newLogFeeder, panel:LogPanel=None):
		feeder = newLogFeeder
		
		feeder._panel = panel
		
		feeder.defaultTarget = feeder.main				# Point at our .main() method.
		super(LogFeeder, feeder).__init__(daemon=True)	# ThreadActor initialization.
			# The daemon=True tells Python not to let this thread keep the process alive.
		
	def main(thisLogFeeder):

		"""This is the main routine of the newly-created LogFeeder thread.
			It basically just reads lines from the log file tail and adds
			them to the panel."""
		
		feeder = thisLogFeeder
		panel = feeder._panel
		client = panel.client
		display = client.display
		dispDrv = display.driver
		
		_logger.debug("logFeeder.main(): Creating 'tail -f' subprocess to feed log panel.")
		
		command_words = ['tail', '-n', str(panel._content_height), '-f', logFilename]
		command_string = ' '.join(command_words)
		
		_logger.debug(f"logFeeder.main(): Command words are: [{command_string}]")

		process = subprocess.Popen(
			command_words, 
			stdout=subprocess.PIPE,
			universal_newlines=True)

		# This just keeps track of whether we have already sent subprocess data to the panel.
		started = False

		# Infinite loop, reading output of tail. The only way this will exit
		# is if the tail process terminates, or we get an exception.
		
		exitRequested = False

		while not exitRequested:

			logLine = process.stdout.readline().strip()
			panel.addLogLine(logLine)

			# Request screen to update shortly after new line is added.
			dispDrv.do(display.update, desc="Update display after adding log line")

			if not started:
				_logger.debug("logFeeder.main(): Just added my very first line of log data to the panel.")
				started=True

				# If subprocess terminated, check for & process any return code.
			return_code = process.poll()
			if return_code is not None:

				_logger.warn(f"logFeeder.main(): 'tail -f' subprocess unexpectedly terminated with return code {return_code}.")

					# In case there was output we didn't read yet, go ahead and display it. 
				for logLine in process.stdout.readlines():

					logLine = logLine.strip()

					panel.addLogLine(logLine)

				dispDrv.do(display.update, desc="Update display after flushing log lines")
				exitRequested = True
		
		# Feeder thread can only terminate at this point.
		_logger.info("logFeeder.main(): Log panel feeder thread is exiting.")

class LogPanel(Panel):
	# This is a panel that displays lines from the log stream

	lock = RLock()	# Reentrant lock for concurrency control.
		# The scope of this lock is the panel._content_data structure.
		
		# Here, we extend the default Panel initialization to also do 
		# LogPanel-specific initialization.
	def __init__(newLogPanel):
		"""Initializer for new instances of class LogPanel."""
		
			# Use a shorter name for this new log panel.
		panel = newLogPanel
		
			# First we do general panel initialization.
		super(LogPanel, panel).__init__("System Log", FILL_BOTTOM, 15)
			# Default height of 8 is fine.
			
			# Make a note that at this point, we have not yet configured our 
			# sub-windows, so that this will be done later in .configWin().
		panel._subWinsCreated = False

			# We also haven't loaded the header or content data yet.
		panel._header_data  = None
		with panel.lock:
			panel._content_data = None
		
			# Create the log feeder thread.
		panel._feeder = LogFeeder(panel=panel)
			# Note this isn't started yet, but later in .launch().
			
	#__/ End instance initializer for class Panel.

	def launch(thisLogPanel):
	
		"""This starts up the feeder process needed to stream content to the panel.
			Note this gets called automatically in Panel's .drawContent method."""
		
		_logger.debug("logPanel.launch(): Starting the feeder thread.")
		thisLogPanel._feeder.start()


	@property
	def data_win(thisLogPanel):
		return thisLogPanel._data_subwin
				
		# Here, we extend the configWin() method to also configure 
		# our LogPanel-specific sub-windows.
	def configWin(thisLogPanel):
	
			# Shorter name for this log panel.
		panel = thisLogPanel
	
			# First, we do general panel window configuration.
		super(LogPanel, panel).configWin()

			# This gets the panel's top-level interior window.
		win = panel.win

			# Get the current size of the top-level panel window.
		(height, width) = win.getmaxyx()			

		_logger.debug(f"logPanel.configWin(): About to configure subwindows for interior size ({height}, {width}).")

			# Create or resize our sub-windows, as appropriate.
			
		if not panel._subWinsCreated:	# Need to create them.
				
				# Now create our sub-windows.
				
			panel._header_subwin = win.derwin(3, width, 0, 0)			# NOTE: WHy do I need -1 here?
				# This means: The header sub-window is 3 rows tall,
				# same width as the top-level panel window, and begins
				# at the upper-left corner of the top-level window.
				
			panel._data_subwin = data_win = win.derwin(3, 0)
				# This means: The data subwindow begins on row 3 (i.e.,
				# the 4th row of the window, under the header), column 0,	
				# and extends all the way to the lower-right corner of the
				# top-level interior window for the panel.
			data_win.scrollok(True)		# Allow window to scroll (for adding new lines at bottom)
			
				# Remember that we already created our sub-windows.
			panel._subWinsCreated = True
				
		else:	# Panel windows already exist; at most, we may need to resize them.
		
				# Clear everything that used to be in these guys before move/resize.
			panel._header_subwin.clear()
			panel._data_subwin.clear()

			# Header sub-window width may need adjusting.
			try:
				# Reset both the position and size, just to make sure.
				
				panel._header_subwin.mvderwin(0, 0)
				panel._header_subwin.resize(3, width)	# Width might be new.

				panel._data_subwin.mvderwin(3, 0)
				panel._data_subwin.resize(height-3, width)

			except curses.error as e:
				_logger.error(f"logPanel.configWin(): During sub-window resizing, got curses error: {str(e)}")
	
		# Make sure we know the size of our content window, and remember it.
		(content_height, content_width) = panel._data_subwin.getmaxyx()
		panel._content_height = content_height
	
	
	def drawHeader(thisLogPanel):
		"""Fills in the content of the 'log header' sub-window."""
		
		_logger.debug("logPanel.drawHeader(): Drawing header sub-window of log panel...")

		panel = thisLogPanel		# Get the panel.
		win = panel._header_subwin	# Get the subwin.
		
		attr = style_to_attr(HEADER)	# Get the attributes for the 'HEADER' rendering style. (Currently, bright white.)

		head_data = panel._header_data
		if head_data is None:
			_logger.debug("logPanel.drawHeader(): Reading log panel header data from file for first time.")
				# Now we actually retrieve the first three lines from
				# the log file.  (Note this implementation assumes we're
				# on a Unix compatible system that provides the head (1) 
				# command in the default command path.)
				# Really here we should retrieve the filename from the logmaster module.
			head_stream = popen(f"head -3 {logFilename}")	
			panel._header_data = head_data = head_stream.read().strip()

			#_logger.debug("logPanel.drawHeader(): Got the following header data: " + '\n' + head_data)

				# Do we need to close the stream here, or will GC do it?
		#__/ End if no header data yet.
		
			# OK, now we are finally ready to actually draw the header text.

		win.move(0,0)	# Always start over at top-left corner.
		addTextClipped(win, head_data, attr)
			# This clips each line to the width of the window.
	
	
	def drawLogLine(thisLogPanel, logLine:str):

		panel = thisLogPanel		# Get the panel.
		win = panel._data_subwin	# Get the subwin.
			
			# Default to plain style if we don't recognize the log level.
			
		style = PLAIN
	
			# The following needs to be adjusted whenever you change the
			# format of log lines.

		levelFieldPos = 136
		levelFieldWidth = 8

			# Attempt to parse the log level.  Really we should do something smarter
			# here, like run a regex on the log line.
			
		if len(logLine) >= levelFieldPos + levelFieldWidth:
		
			logLevel = logLine[levelFieldPos:levelFieldPos+levelFieldWidth]
				# Extracts field where we expect to see the log level printed.
			
			# This is annoying due to the varying numbers of spaces.
			if logLevel == "   DEBUG":
				logLevel = 'debug'
			elif logLevel == "    INFO":
				logLevel = 'info'
			elif logLevel == "  NORMAL":
				logLevel = 'normal'
			elif logLevel == " WARNING":
				logLevel = 'warning'
			elif logLevel == "   ERROR":
				logLevel = 'error'
			elif logLevel == "CRITICAL":
				logLevel = 'critical'
			
				# Move this to a class variable?
			stylemap = {
					'debug':	DEBUG_STYLE,
					'info':		INFO_STYLE,
					'normal':	GOOD_STYLE,
					'warning':	WARNING_STYLE,
					'error':	ERROR_STYLE,
					'critical':	CRITICAL_STYLE,
				}
				
			if logLevel in stylemap:
				style = stylemap[logLevel]
					
		attr = style_to_attr(style)
		
			# If we didn't do a newline yet, do it now.
		(posy, posx) = win.getyx()		# Cursor position in window.
		if posx > 0:
			win.addstr('\n')	# Newline.
		
		addLineClipped(win, logLine, attr)

		win.noutrefresh()	# Mark this window for updating.
		
	
	def _init_data(thisLogPanel):

		"""This makes sure that the panel data has been initialized.
			Normally, we just initialize it to an initially-empty list."""

		panel = thisLogPanel

		with panel.lock:

			data = panel._content_data

			if data is None:
				_logger.debug("panel._init_data(): Initializing panel content data to empty list.")
				data = []

			panel._content_data = data

	
	def drawData(thisLogPanel):

		"""This fills in the actual log data within the data area
			of the log panel.  Assumes area is already clear, and
			that the display will be refreshed afterwards."""
	
		panel 	= thisLogPanel
		win 	= panel._data_subwin
		height	= panel._content_height

			#|-----------------------------------------------------
			#| Select/adjust size of internal data array if needed.
		
		with panel.lock:	# Grab ownership of ._content_data.
		
				# First, make sure panel data has been initialized.
			panel._init_data()

				# Extract just the last (at most) <height> rows of data.
			data = panel._content_data
			if len(data) > height:
				data = data[-height:]

				#|-------------------------------------
				#| Add the log lines to the sub-window.
			
			for logLine in data:
				panel.drawLogLine(logLine)

		
	def repaintDataArea(thisLogPanel):
		panel = thisLogPanel
		area = panel.data_win	# The data area (sub-window) within the log panel.
		
			# First, make sure panel data has been initialized.
		panel._init_data()

		#_logger.debug(f"Refreshing the {len(panel._content_data)}/{panel._content_height}-line data area within the log panel.")

			# Erase the current data area contents.
		area.erase()

			# Redraw all the data within the data area.
		panel.drawData()



	def _trim_data(thisLogPanel):

		"""Call this routine to keep the content data buffer from
			growing indefinitely."""

		panel = thisLogPanel

		max_size = 200	# Really should make this a configurable parameter.
		
		with panel.lock:
			
			data = panel._content_data

			if len(data) > max_size:
				data = data[-max_size:]		# Keeps last <max_size> entries.

			panel._content_data = data		# Remember the newly-trimmed dataset.


	def addLogLine(thisLogPanel, logLine:str):
		"""Adds the given (new) line of log file data to 
			our content dataset, and display it in our 
			content subwindow. NOTE: This runs within
			some thread other than the display driver."""

		panel = thisLogPanel
		client = panel.client
		display = client.display
		dispDrv = display.driver
		win = panel.data_win

		with panel.lock:

				# First, make sure panel data has been initialized.
			panel._init_data()

				# Add the new line to the dataset.
			data = panel._content_data
			data.append(logLine)
			panel._content_data = data

				# Limit size of data buffer.
			panel._trim_data()

				# Ask the display driver to (asynchronously)
				# draw the new log line in the data area.
			dispDrv.do(lambda: panel.drawLogLine(logLine), desc="Draw new log line")
				# This will run in the background to help avoid deadlocks.

				# Repaint the sub-window.
			#dispDrv.do(panel.repaintDataArea)
				# The only thing that changed as far as we're concerned is the data sub-window,
				# so just refresh that one.

	def drawContent(thisLogPanel):
		"""Fills in the content of a blank log panel."""
		
		panel = thisLogPanel
		panel.drawHeader()
		panel.drawData()
		
			# Call the original method in Panel, which does some general
			# bookkeeping work needed for all panels.
		super(LogPanel, panel).drawContent()

#__/ End class LogPanel.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					END OF FILE:	console/logPanel.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%