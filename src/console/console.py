#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 console/console.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		console/console.py				 [Python module source file]
		
	MODULE NAME:	console.console
	IN PACKAGE:		console
	FULL PATH:		$GIT_ROOT/GLaDOS/src/console/console.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.server.console (GLaDOS System Console)


	MODULE DESCRIPTION:
	===================

		This module implements the main system console of the GLaDOS server.
		This runs on the tty where the server process is started.  A human 
		operator can use this console to monitor the system status, and enter
		maintenance commands.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# console.py
# Implements the main GLaDOS system console display

# Here is a rough sketch of the console display layout (not actual size or to scale):
#
#		/---------------------------------------- GLaDOS System Console ----------------------------------------\
#		| [This area is used to display a human-readable	| [The receptive field display flows around to		|
#		|  rendition of the AI's entire receptive field.	|  this column, if it doesn't fit in the first		|
#		|  Any normally-nonprintable ASCII characters are	|  column.]											|
#		|  rendered using special display codes & styles.	|													|
#		|  The view of the receptive field is also word-	|													|
#		|  wrapped to fit within the column.  The screen	|													|
#		|  is divided into two roughly equal-size columns,	|													|
#		|  unless the screen width is less than 120 char-	|													|
#		|  acter cells, in which case we use only a single	|													|
#		|  column.  If the receptive field doesn't fit in	|													|
#		|  the allotted area, a scrollable curses "pad"		|													|
#		|  larger than the visible area is utilized to		|													|
#		|  allow the user to browse the entire field.]		+--- Diagnostic Output -----------------------------+
#		|													| [This area is used to display what would norm-  	|
#		|  													|  ally be the STDOUT/STDERR streams from the 	  	|
#		|   												|  server process.  STDERR output is rendered	  	|
#		|   												|  in red.  STDOUT text comes out in green.		  	|
#		|  													|  Operator can scroll back in this window.			|
#		|  													+--- Operator Input --------------------------------+
#		|													| [This area is a text box that the human operator  |
#		|													|  can use to input commands/text to the system.]	|
#		+--- System Log ------------------------------------+---------------------------------------------------+
#		| [This area is for real-time display of detailed log lines being spooled to the system log file.		|
#		|																										|
#		|																										|
#		\-------------------------------------------------------------------------------------------------------+
#
#	Control character rendering:
#
#							Rendering as a single (usually black-on-red) 8-bit character.
#							|
#							|	Rendering as a single (usually black-on-red) 7-bit character.
#							|	|
# 	 	Dec	Hex	Abb CC		8	7	Full name / description.
# 	 	---	--- ---	--		-	-	------------------------
#		 0	x00	NUL	^@		_	_	Null character.
#		 1	x01	SOH	^A		$	:	Start of heading (console interrupt?).
#		 2	x02	STX	^B		«	[	Start of text.
#		 3	x03	ETX	^C		»	]	End of text.
#		 4	x04	EOT	^D		.	.	End of transmission.
#		 5	x05	ENQ	^E		?	?	Enquiry (used with ACK).
#		 6	x06	ACK	^F		!	Y	Acknowledgement (used with ENQ). ("Y" is for "Yes!")
#		 7	x07	BEL	^G		¢	*	Bell.
#		 8	x08	BS	^H		<	<	Backspace.
#		 9	x09	HT	^I		>	>	Horizontal tabulation [Tab]. (Whitespace; render as gray on black.)
#		10	x0A	LF	^J		/	/	Line feed [Enter]. (Whitespace; render as gray on black.)
#		11	x0B	VT	^K		v	v	Vertical tabulation. (Whitespace; render as gray on black.)
#		12	x0C FF	^L		§	V	Form feed. (Whitespace; render as gray on black.)
#		13	x0D CR	^M		®	<	Carriage return [Return]. (Whitespace; render as gray on black)
#		14	x0E SO	^N		(	(	Shift-out; begin alt. char. set.
#		15	x0F SI	^O		)	)	Shift-in; resume default char. set.
#		16	x10 DLE	^P		±	/	Data-link escape. (Like my command-line escape character.)
#		17	x11 DC1	^Q		°	o	Device control 1 (XON), used with XOFF.  Turn on/resume.  ('o' is for "on.")
#		18	x12 DC2	^R		©	@	Device control 2.  Special mode.
#		19	x13 DC3	^S		=	=	Device control 3 (XOFF), used with XON.  Secondary stop (wait, pause, standby, halt).
#		20	x14 DC4	^T		-	-	Device control 4.  Primary stop (interrupt, turn off).
#		21	x15 NAK	^U		¬	N	Negative acknowledgement. (N is for "No!")
#		22	x16	SYN	^V			~	~	Synchronous idle.	
#		23	x17	ETB	^W		;	;	End transmission block.
#		24	x18	CAN	^X		×	X	Cancel.
#		25	x19	EM	^Y		|	|	End of medium.
#		26	x1A	SUB	^Z		¿	$	Substitute.
#		27	x1B	ESC	^[		^	^	Escape.
#		28	x1C	FS	^\		¦	F	File separator.	(F is for "file.")
#		29	x1D	GS	^]		÷	G	Group separator. (G is for "group.")
#		30	x1E	RS	^^		¶	&	Record separator. (And, here's another record!  Or, 'P' looks like an end-paragraph marker.)
#		31	x1F	US	^_		·	,	Unit separator. (In CSV, separates fields of a database row.)
#		32	x20	SP	^`		_	_	Space. (Whitespace; render as gray on black.)
#	   127	x7F	DEL	^?		#	#	Delete. (Looks like RUBOUT hash.)
#
#	For character codes from 128-255, we render them as above (but in a different color) if they are controls,
#	and as themselves if they are printable Western font (Latin-1) characters.  For codes above 255, how we 
#	handle them is not really defined yet.  Maybe we just send them to the terminal, and just hope that they
#	are supported.

from threading	import	RLock
from os 		import 	path, popen

			#------------------------
			# Logging-related stuff.

from infrastructure.decorators import singleton

from infrastructure.logmaster import (
		sysName,			# Used just below.
		ThreadActor,		# TUI input thread uses this.
		getComponentLogger 	# Used just below.
	)

global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component


from display.display	import (
		PLAIN, BORDER, HEADER,
		DEBUG_STYLE, INFO_STYLE, GOOD_STYLE,
		WARNING_STYLE, ERROR_STYLE, CRITICAL_STYLE,
		style_to_attr
	)

# To implement the console, we draw an arrangement of borders and separators, within which are different "panels",
# or curses sub-windows with specific functionality.  Each panel has a position and size.  In the event of a screen
# resize, we redo the panel arrangement and refresh the display.

# Classes include:
# ----------------
#
#		ConsoleClient	- Subclass of PanelClient for setting up the console display specifically.
#
#
#	Panel subclasses:
#	.................
#
#		LogPanel		- This is the panel to display the system log at the bottom of the screen.
#
#		InputPanel		- This is the panel for gathering operator input.
#
#		DiagnosticPanel	- This is the panel for displaying STDOUT/STDERR streams.
#
#		FieldPanel		- This is the panel for displaying all or part of the AI's receptive field.
#

import subprocess	# Used for streaming output from 'tail'

from display.panel import Panel, PanelClient, FILL_BOTTOM


	# Maybe should move this to LogPanel initializer?
global logFilename
logFilename = path.join('log', 'GLaDOS.server.log')


class LogPanel: pass

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
		
	def main(thisLogFeeder):
		"""This is the main routine of the newly-created LogFeeder thread.
			It basically just reads lines from the log file tail and adds
			them to the panel."""
		
		feeder = thisLogFeeder
		
		process = subprocess.Popen(
			['tail', '-f', logFilename], 
			stdout=subprocess.PIPE,
			universal_newlines=True)
		
		# Infinite loop, reading output of tail. The only way this will exit
		# is if the tail process terminates, or we get an exception.
		
		while True:
			logLine = process.stdout.readline().strip()
			panel.addLogLine(logLine)

				# If subprocess terminated, check for & process any return code.
			return_code = process.poll()
			if return_code is not None:

				_logger.warn(f"LogFeeder.main(): 'tail' process unexpectedly terminated with return code {return_code}.")

					# In case there was output we didn't read yet, go ahead and display it. 
				for logLine in process.stdout.readlines():
					panel.addLogLine(logLine)

				break	# Feeder thread can only terminate at this point.

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
		super(LogPanel, panel).__init__("System Log", FILL_BOTTOM)
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


	def launch(thisLogPanel):
		"""This starts up the feeder process needed to stream content to the panel."""
		thisLogPanel._feeder.start()

				
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
				
			panel._data_subwin = win.derwin(3, 0)
				# This means: The data subwindow begins on row 3 (i.e.,
				# the 4th row of the window, under the header), column 0,	
				# and extends all the way to the lower-right corner of the
				# top-level window.
				
		else:	# Panel windows already exist; at most, we may need to resize them.
		
			# Header sub-window width may need adjusting.
			panel._header_subwin.resize(3, width)	# Width might be new.
	
		# Make sure we know the size of our content window, and remember it.
		(content_height, content_width) = panel._data_subwin.getmaxyx()
		panel._content_height = content_height
	
	
	def drawHeader(thisLogPanel):
		"""Fills in the content of the 'log header' sub-window."""
		
		panel = thisLogPanel		# Get the panel.
		win = panel._header_subwin	# Get the subwin.
		
		if panel._header_data is None:
				# Now we actually retrieve the first three lines from
				# the log file.  (Note this implementation assumes we're
				# on a Unix compatible system that provides the head (1) 
				# command in the default command path.)
				# Really here we should retrieve the filename from the logmaster module.
			head_stream = popen(f"head -3 {logFilename}")
			head_data = head_stream.read().strip()
				# Do we need to close the stream here, or will GC do it?
		#__/ End if no header data yet.
		
			# OK, now we are finally ready to actually draw the header text.
		attr = style_to_attr(HEADER)	# Get the attributes for the 'HEADER' rendering style. (Bright white.)
		win.addstr(head_data, attr)		# Puts the header data string in the header window.
	
	
	def drawLogLine(thisLogPanel, logLine:str):

		panel = thisLogPanel		# Get the panel.
		win = panel._data_subwin	# Get the subwin.
			
			# Default to plain style if we don't recognize the log level.
			
		style = PLAIN
	
			# Attempt to parse the log level.  Really we should do something smarter
			# here, like run a regex on the log line.
			
		if len(logLine) >= 149:
		
			logLevel = logLine[141:149]		# Extracts field where we expect to see the log level printed.
			
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
		
		(posy, posx) = win.getyx()		# Cursor position in window.
		if posx > 0:
			win.addstr('\n')	# Newline.
		win.addstr(logLine, attr)
		
	
	def drawData(thisLogPanel):
	
		panel 	= thisLogPanel
		win 	= panel._data_subwin
		height	= panel._content_height

			#|-----------------------------------------------------
			#| Select/adjust size of internal data array if needed.
		
		with panel.lock:	# Grab ownership of ._content_data.
		
			data	= panel._content_data
			
			# First, if there's no data yet, initialize with right size.
			if data is None:
				data = [""] * height	# All rows are empty initially.
				
			# Or, if we have too much data, throw away the early bits.
			elif len(data) > height:
				data = data[len(data)-height:]	# Only preserves last <height> rows.
				
			# Finally, if we have too little data, then pad it out with blank lines.
			while len(data) < height:
				data.add("")

				# Remember new data array.
			panel._content_data = data
		
				#|-------------------------------------
				#| Add the log lines to the sub-window.
			
			for logLine in data:
				panel.drawLogLine(logLine)

		
	def addLogLine(thisLogPanel, logLine:str):
		"""Adds the given (new) line of log file data to 
			our content dataset, and display it in our 
			content subwindow."""
		panel = thisLogPanel
		with panel.lock:
			height = panel._content_height
			data = panel._content_data
			data.add(logLine)
			while len(data) > height:
				data = data[1:]
			display.driver.do(lambda: panel.drawLogLine(logLine))
				# This will run in the background to avoid deadlocks.

		
	def drawContent(thisLogPanel):
		"""Fills in the content of a blank log panel."""
		panel = thisLogPanel
		panel.drawHeader()
		panel.drawData()
	
class InputPanel:
	pass
	
class DiagnosticPanel:
	"""Panel to display text that would normally go to sydtem stdout/stderr:
		Normal, info, warning, error messages etc."""
	pass
	
class FieldPanel:
	"""Panel to display all or part of the receptive field."""
	pass


class ConsoleClient(PanelClient):

	"""The console display client controls the display 
		when the system console is active."""

	def __init__(newClient, title:str="GLaDOS System Console"):
	
		client = newClient
		
			# First, do general initialization for panel clients.
		super(ConsoleClient, client).__init__(title)
		
			# Next, we need to create all our panels.
		
		client._logPanel	= logPanel 			= LogPanel()
		client._inputPanel	= inputPanel 		= InputPanel()
		client._diagPanel	= diagnosticPanel	= DiagnosticPanel()
		#client._rFieldPanel	= rightFieldPanel 	= FieldPanel(column='right')
		#client._lFieldPanel = leftFieldPanel	= FieldPanel(column='left')
		
			# This installs all the panels in this PanelClient.
			
		client.addPanel(logPanel)			# Place this first, to occupy bottom of screen.
		#client.addPanel(inputPanel)		# This goes next, at the bottom of the right column.
		#client.addPanel(diagnosticPanel)	# This goes next, just above the input panel.
		#client.addPanel(rightFieldPanel)	# This fills the rest of the right-hand column.
		#client.addPanel(leftFieldPanel)	# This fills the rest of the left-hand column.

	def start(thisClient, waitForExit:bool=True):
		# NOTE: Here we override the default value of waitForExit 
		# while we're debugging basic console capabilities.
		# We can remove this override once that's done.
		
		client = thisClient
		
		# IS THERE ANYTHING WE NEED TO DO HERE TO PREP FOR STARTUP?
		
			# Note: We do this last, because it will never return if
			# waitForExit is not False.
		super(ConsoleClient, client).start(waitForExit=waitForExit)
			# Calls DisplayClient's .start() method.
