# diagPanel.py - Panel for server diagnostic output (what would normally be STDOUT/STDERR).


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

from .virterm import Line

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConsolePanel(Panel):

	"""Panel for displaying the GLaDOS server application program's
		diagnostic output; i.e., what would normally go to the
		STDOUT/STDERR output streams in the absence of the paneled
		console display."""

	_DEFAULT_MAXLINES = 100

	def __init__(newConsolePanel:ConsolePanel, virterm:VirTerm):

		panel = newConsolePanel

			# Remember the virtual terminal whose output we're displaying.
		panel._virterm = virterm

			# Initialize our panel contents.
		panel._lines = []

			# Initialize our max number of lines to remember.
		panel._max_nlines = panel._DEFAULT_MAXLINES

		# General panel initialization.
		super(ConsolePanel, panel).__init__("Console Output", LOWER_RIGHT, 8)
			# By default, the input panel appears at the bottom of the right column.
			# A default height of 8 for this panel is fine.  It can grow if needed.
		
		# Create and store the console feeder thread.
		# Its job will be to relay STDOUT/STDERR lines to us to display.
		feederThread = ConsoleFeeder(panel)
		panel._consoleFeeder = feederThread

	def addLine(thisConsolePanel:ConsolePanel, line:Line):
		"""Adds a line's worth of virtual terminal data to the console
			panel's contents."""

		panel = thisConsolePanel
		client = panel.client
		display = client.display
		driver = display.driver()

		panel._lines.append(line)
		nlines = len(panel.lines)

		# If there are too many lines saved, trim the buffer.
		if len(panel.lines) > panel._max_nlines:
			panel._lines = panel.lines[-panel._max_nlines]

		driver(panel.redisplayContent)	# Tell panel to redisplay its content.

	@property
	def lines(thisConsolePanel:ConsolePanel):
		return thisConsolePanel._line

	def drawContent(thisConsolePanel:ConsolePanel):
		"""This is a standard Panel method that is called to fill in
			the content of a blank log panel."""

		panel = thisConsolePanel
		win = panel.win
		(height, width) = win.getmaxyx()

		lastLines = panel.lines[-height:]	# Last <height> lines

		for line in lastLines:

			text = line.text
			isErr = line.isErr

				# Set the rendering style for this line.
			style = ERROR_STYLE if isErr else GOOD_STYLE
			attr = style_to_attr(style)

			win.addstr(text, attr)

	@property
	def virterm(thisConsolePanel:ConsolePanel):
		return thisConsolePanel._virterm
