# diagPanel.py - Panel for server diagnostic output (what would normally be STDOUT/STDERR).


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from os import path
from infrastructure.logmaster import (
		sysName,			# Used just below.
		ThreadActor,		# Blink timer thread is subclassed from this.
		getComponentLogger 	# Used just below.
	)

global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from 	.virterm 			import (

		Line,				# A line of text output saved in the virtual terminal.
		VirTerm				# The virtual terminal.

	)

from	display.colors		import (

		DEBUG_STYLE,		# Render style we use for debug-level log messages.
		INFO_STYLE, 		# Render style we use for input-level log messages.
		GOOD_STYLE,			# Render style we use for normal-level log messages.
		WARNING_STYLE,		# Render style we use for warning-level log messages.
		ERROR_STYLE,		# Render style we use for error-level log messages.
		CRITICAL_STYLE,		# Render style we use for critical-level (or fatal) log messages.
		style_to_attr,		# Converts render styles to display attributes.
	
	)

from 	display.drawing		import (

		addLineClipped, 	# Adds a line of text to a window, but with right-clipping.
	)

from	display.panel		import (

		Panel,				# Console panel inherits from this.
		LOWER_RIGHT,		# Placement for the console panel.

	)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConsoleFeeder: pass
class ConsolePanel: pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConsoleFeeder(ThreadActor):
	defaultRole = 'ConsFeedr'
	defaultComponent = _sw_component

	def __init__(newConsoleFeeder, panel:ConsolePanel=None):
		feeder = newConsoleFeeder
		feeder._panel = panel
		feeder.exitRequested = False

		feeder.defaultTarget = feeder._main
		super(ConsoleFeeder, feeder).__init__(daemon=True)

	@property
	def panel(thisConsoleFeeder:ConsoleFeeder):
		return thisConsoleFeeder._panel

	def _main(thisConsoleFeeder:ConsoleFeeder):

		"""This is the main routine of the newly-created ConsoleFeeder
			thread.  It basically just reads lines from the virterm and
			adds them to the panel."""

		feeder	= thisConsoleFeeder

		panel	= feeder.panel
		virterm = panel.virterm
		client	= panel.client
		display	= client.display
		driver	= display.driver

		_logger.debug("consoleFeeder._main(): Console panel feeder thread has started.")

		while not feeder.exitRequested:

			# If the virterm doesn't have data currently, we wait
			# until it does.

			with virterm.hasData.lock:
				if not virterm.hasData():
					virterm.hasData.waitRise()
		
			# OK, now we pop a line from the virterm and add it to
			# our console panel display.

			line = virterm.popFirstLine()
			panel.addLine(line)

		# Feeder thread can only terminate at this point.
		_logger.info("logFeeder._main(): Console panel feeder thread is exiting.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConsolePanel(Panel):

	"""Panel for displaying the GLaDOS server application program's
		diagnostic output; i.e., what would normally go to the
		STDOUT/STDERR output streams in the absence of the paneled
		console display."""

	_DEFAULT_INITROWS = 38		# Default initial height of panel.
	_DEFAULT_MAXLINES = 100

	def __init__(newConsolePanel:ConsolePanel, virterm:VirTerm, initRows=None):

		panel = newConsolePanel

		if initRows is None:
			initRows = panel._DEFAULT_INITROWS

			# Remember the virtual terminal whose output we're displaying.
		panel._virterm = virterm

			# Initialize our panel contents.
		panel._lines = []

			# Initialize our max number of lines to remember.
		panel._max_nlines = panel._DEFAULT_MAXLINES

		# General panel initialization.
		super(ConsolePanel, panel).__init__("Console Output", LOWER_RIGHT, initRows)
			# By default, the input panel appears at the bottom of the right column.
			# A default height of 8 for this panel is fine.  It can grow if needed.
		
		# Create and store the console feeder thread.
		# Its job will be to relay STDOUT/STDERR lines to us to display.
		feederThread = ConsoleFeeder(panel)
		panel._consoleFeeder = feederThread

	def launch(thisConsolePanel:ConsolePanel):
		"""This starts up the feeder thread needed to stream content to the panel.
			Note this gets called automatically in Panel's .drawContent method."""
		
		panel = thisConsolePanel
		win = panel.win

		win.scrollok(True)

		_logger.debug("consolePanel.launch(): Starting the feeder thread.")
		panel._consoleFeeder.start()

	def addLine(thisConsolePanel:ConsolePanel, line:Line):
		"""Adds a line's worth of virtual terminal data to the console
			panel's contents."""

		panel = thisConsolePanel
		client = panel.client
		display = client.display
		driver = display.driver

		panel._lines.append(line)
		nlines = len(panel.lines)

		# If there are too many lines saved, trim the buffer.
		if len(panel.lines) > panel._max_nlines:
			panel._lines = panel.lines[-panel._max_nlines]

		if display.isRunning:
			driver(panel.redisplayContent, desc="Redisplay console panel to show new line")
			# Tell panel to redisplay its content.

	@property
	def lines(thisConsolePanel:ConsolePanel):
		return thisConsolePanel._lines

	def drawContent(thisConsolePanel:ConsolePanel):
		"""This is a standard Panel method that is called to fill in
			the content of a blank log panel."""

		panel = thisConsolePanel
		win = panel.win

		(height, width) = win.getmaxyx()

		lastLines = panel.lines[-height:]	# Last <height> lines

		lineNo = 0

		for line in lastLines:

			text = line.text
			isErr = line.isErr

				# Set the rendering style for this line.
			style = ERROR_STYLE if isErr else GOOD_STYLE

				# See if we can figure out a logging level from the line data.
			if len(text) >= 10:

				logLevel = text[0:10]
				
				if		logLevel == "   DEBUG: ":

					style = DEBUG_STYLE

				elif 	logLevel == "    INFO: ":

					style = INFO_STYLE

				elif 	logLevel == "  NORMAL: ":

					style = GOOD_STYLE

				elif	logLevel == " WARNING: ":

					style = WARNING_STYLE

				elif	logLevel == "   ERROR: ":

					style = ERROR_STYLE

				elif	logLevel == "CRITICAL: ":

					style = CRITICAL_STYLE

			attr = style_to_attr(style)

			addLineClipped(win, text.strip(), attr)

			if lineNo < height - 1:
				win.addstr('\n')
				lineNo = lineNo + 1

			# Call the original method in Panel, which does some general
			# bookkeeping work needed for all panels.
		super(ConsolePanel, panel).drawContent()

	@property
	def virterm(thisConsolePanel:ConsolePanel):
		return thisConsolePanel._virterm
