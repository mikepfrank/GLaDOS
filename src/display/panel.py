# panel.py
#
# Module to support applications using a "panel" abstraction to manage the display.
# The idea behind panels is that they are non-overlapping windows with clear separators
# between them, and clearly-defined placement rules and geometry constraints that determine
# what happens to them when the screen is resized.
#
#	Classes defined in this module include:
#
#		PanelPlacement	- Enum of supported panel placement modes.
#		Panel 			- Main class for panels.
#		PanelClient		- Subclass of DisplayClient for panel-based clients.

from enum import Enum					# Enumerated type support.
from os import path

from infrastructure.logmaster import (
		sysName,			# Used just below.
		getComponentLogger 	# Used just below.
	)
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.
global _sw_component
_sw_component = sysName + '.' + _component

from .display import (
		BORDER,
		style_to_attr,		# Needed to use render styles.
		DisplayClient		# We extend this to form panelclient.
	)

class PanelPlacement(Enum):
	"""This enum lists the panel-placement specifiers presently supported."""
	FILL_BOTTOM = 'fill-bottom',	# Occupy full width of display, at the bottom. Place this before columnar panels.
	LOWER_RIGHT	= 'lower-right',	# Place this panel at the bottom of the right-hand column (but after previous LOWER_RIGHT panels).
	FILL_RIGHT	= 'fill-right',		# This panel expands to fill all remaining space in the right-hand column.
	FILL_LEFT	= 'fill-left',		# This panel expands to fill all remaining space in the left-hand column.

global FILL_BOTTOM, LOWER_RIGHT, FILL_RIGHT, FILL_LEFT
FILL_BOTTOM = PanelPlacement.FILL_BOTTOM
LOWER_RIGHT = PanelPlacement.LOWER_RIGHT
FILL_RIGHT = PanelPlacement.FILL_RIGHT
FILL_LEFT = PanelPlacement.FILL_LEFT	

class PanelClient: pass

class Panel:
	"""A non-overlapping region of a panel client's display area."""
	def __init__(newPanel, 
			title:str = "Untitled Panel",			# REQUIRED ARGUMENT. Panel title. CALLER MUST PROVIDE THIS.
			initPlacement:PanelPlacement = None,	# REQUIRED ARGUMENT, panel placement specifier.
			initHeight:int = 8,						# Initial internal panel height, in rows of text.
		):
		newPanel._title		= title
		newPanel._placement = initPlacement
		newPanel._height	= initHeight		# This is our aspirational/initially-requested height.
		newPanel._client	= None				# It hasn't been placed in a client yet.
		newPanel._placed 	= False				# Panel has not actually been placed yet.
		newPanel._win 		= None				# It has no internal sub-window yet.
		newPanel._launched 	= None				# Any subsidiary processes have not been started yet.

	@property
	def title(thisPanel):
		return thisPanel._title

	@property
	def height(thisPanel):
		return thisPanel._height

	@property
	def client(thisPanel):
		return thisPanel._client

	@property
	def win(thisPanel):
		"""Gets the top-level internal window of this panel, or None
			if the window has not been created yet.  (Please note this
			refers to a curses display window, not a GLaDOS window.)"""
		return thisPanel._win

	def configWin(thisPanel):
		"""Assuming the panel already has a placement, make sure it has
			an internal window, and that it's the correct size.  Subclasses
			may extend this as needed to (re)configure any sub-windows."""
		
		panel = thisPanel
		client = panel.client
		display = client.display
		screen = display.screen
		
		if panel._win == None:	# No sub-window yet; create one.
			panel._win = screen.subwin(panel.height, panel.width, panel.top+1, panel.left+1)
		else:
				# Move the window in case the panel's position changed.
			panel._win.mvwin(panel.top+1, panel.left+1)
				# Resize the window in case the panel's size changed.
			panel._win.resize(panel.height, panel.width)
	
	def replace(thisPanel):
		"""Same as .place() but for previously placed panels."""
		panel = thisPanel
		panel._placed = False	# Needed for .place() to do anything.
		panel.place()
		
	def place(thisPanel, panelClient:PanelClient = None):
		"""This does the actual work of placing the panel within the client display.
			This figures out the panel's size and location on the display, and 
			creates the sub-window object for its contents (within its frame)."""

		panel = thisPanel

		# If panel's client is being provided, then store it.
		if panelClient is not None:
			panel._client = panelClient
			
		client = panel._client

		# There's only anything we can do right now if the client's display is actually up and running.
		if not client.dispRunning:
			return
	
		# Also, if the panel is already placed, we don't need to do anything.
		if panel._placed:
			return
	
		display = client.display

			# Get the coordinates of the bottom/right edges of the screen.
		(scr_bot, scr_right) = display.get_max_yx()
	
		placement = panel._placement	# Get the panel's placement specifier.
	
		# Here we process the placement and figure out panel coordinates.
		if placement == FILL_BOTTOM:
		
			panel.left = 0
			panel.right = scr_right
			panel.bottom = scr_bot - client._botReserved
			client.reserveBot(panel.height + 1) 	# One extra for bottom edge.
			panel.top = scr_bot - client._botReserved
			
		elif placement == LOWER_RIGHT:
			
			# Here we do one of two different things depending on whether the client is in
			# one-column or two-column mode.
			
			if client.nColumns == 2:		# Two-column mode.
			
				panel.left = client.colSepPos
				panel.right = scr_right
				panel.bottom = scr_bot - client._botReserved - client._brReserved
				client.reserveBotRight(panel.height + 1)
				panel.top = scr_bot - client._botReserved - client._brReserved
				
			elif client.nColumns == 1:		# One-column mode.

				panel.left = 0
				panel.right = scr_right
				panel.bottom = scr_bot - client._botReserved - client._brReserved
				client.reserveBotRight(panel.height + 1)
				panel.top = scr_bot - client._botReserved - client._brReserved
				
		elif placement == FILL_RIGHT and client.nColumns == 2:
		
			# NOTE: Still need to figure out how to handle FILL_RIGHT if there's only 1 column.
		
			panel.left = client.colSepPos
			panel.right = scr_right
			panel.bottom = scr_bot - client._botReserved - client._brReserved
			panel.top = 0
			panel.height = panel.bottom - panel.top - 1
			
		elif placement == FILL_LEFT:
		
			if client.nColumns == 2:
			
				panel.left = 0
				panel.right = client.colSepPos
				panel.bottom = scr_bot - client._botReserved
				panel.top = 0
			
			elif client.nColumns == 1:
			
				panel.left = 0
				panel.right = scr_right
				panel.bottom = scr_bot - client._botReserved - client._brReserved
				panel.top = 0
			
			panel.height = panel.bottom - panel.top - 1

			# Compute internal width of panel.
		panel.width = panel.right - panel.left - 1

		panel.configWin()	# Creates/resizes panel's internal window(s) as needed.
		
		panel._placed = True	# Remember we've been placed.

	
	def drawFrame(thisPanel):
		"""This draws a frame or outer border around the edge of the panel."""
		
		panel = thisPanel
		client = panel.client
		display = client.display
		screen = display.screen
		
		(scr_bot, scr_right) = display.get_max_yx()
		
			# Get coordinates of sides.
		top		= panel.top
		bottom	= panel.bottom
		left 	= panel.left
		right 	= panel.right
		width	= panel.width	# These width/height values
		height	= panel.height	# don't include the frame.
	
			# Figure out corner characters.
		tlchar = '/' if top == 0 and left == 0 else '+'
		trchar = '\\' if top == 0 and right == scr_right else '+'
		blchar = '\\' if bottom == scr_bot and left == 0 else '+'
		brchar = '/' if bottom == scr_bot and right == scr_right else '+'

			# Go into BORDER style.
		att = style_to_attr(BORDER)
		screen.attrset(att)
		
			# Place the corner characters.
		screen.addch(top, left, tlchar)
		screen.addch(top, right, trchar)
		screen.addch(bottom, left, blchar)
		if bottom != scr_bot or right != scr_right:		# Avoids an exception
			screen.addch(bottom, right, brchar)

			# Draw the edges.
		screen.hline(top, 	 left+1, '-', width)
		screen.hline(bottom, left+1, '-', width)
		screen.vline(top+1,  left,   '|', height)
		screen.vline(top+1,  right,  '|', height)
		
			# Special case: For two-column-wide panels at top or bottom of screen, draw a '+' where column separator joins top or bottom edge.
		colSepPos = client.colSepPos
		if left < colSepPos and right > colSepPos:	# Spans column separator.
			if top > 0: 
				screen.addch(top, colSepPos, '+')
			if bottom < scr_bot:
				screen.addch(bottom, colSepPos, '+')

			# Resume normal style.
		screen.attrset(0)
	
	
	def paint(thisPanel):
		"""This tells this panel to go ahead and paint itself on the display."""
		
		panel = thisPanel
		client = panel.client
		display = client.display
		screen = display.screen
		
		_logger.debug(f"panel.paint(): Repainting panel '{panel.title}'.")

			# First, place it, if it's not placed already.
		if not panel._placed:
			panel.place(panel._client)	# Assume this was set earlier at least.

			# OK, next, draw the panel's frame.
		panel.drawFrame()
		
			# Now draw the panel's title in its top frame, in border style.
		if panel._title != None:
			paddedTitle = ' ' + panel._title + ' '
			screen.addstr(panel.top, panel.left + 4, paddedTitle, style_to_attr(BORDER))
		
			# Now paint the panel's contents.  This is implemented by its subclass.
		panel.drawContent()
	
	
	def drawContent(thisPanel):
		"""Extend this method to draw actual content in the given panel.
			This method should assume that the panel is initially erased,
			and that it will be refreshed some time after it's finished.
			Please note that extensions should use super() to call this 
			method before they return."""
	
		panel = thisPanel
	
		#/-----------------------------------------
		#| EXTEND METHOD WITH ADDITIONAL CODE HERE.
		#\-----------------------------------------
	
		# Now is a good time to launch any subsidiary threads/processes
		# associated with the panel, if not already done.
		
		if not panel._launched:
			panel.launch()
			panel._launched = True
			
	#__/ End method panel.drawContent().
	
	
	def launch(thisPanel):
	
		"""This starts up any subsidiary processes/threads that may be required
			in order to generate content that will be displayed in this panel.
			Subclasses should override this as needed."""
			
		panel = thisPanel	# Shorter name for argument.

		# DO SOMETHING HERE
		
	#__/ End method panel.launch().


class PanelClient(DisplayClient):

	"""A type of DisplayClient that organizes the display into non-overlapping panels."""
	
	
	def __init__(newPanelClient, 
			title:str="Untitled Panel Client"	# REQUIRED ARGUMENT, client title; replace this!
		):
		"""Initializer for newly-created PanelClient instances."""
		
			# We first call the default initialization method from DisplayClient.
		super(PanelClient, newPanelClient).__init__()
		
			# Stash our subclass-specific arguments.
		newPanelClient._title = title	# Client title string.

			# Initialize some subclass-specific data structures.
		newPanelClient._panels = []		# Initially empty list of panels.
		
			# These instance variables keep track of how much of the screen is reserved currently.
		newPanelClient._botReserved = 0		# Rows reserved across entire screen bottom.
		newPanelClient._brReserved = 0		# Rows reserved across bottom of right column.
		newPanelClient._blReserved = 0		# Rows reserved across bottom of left column.


	def redoPlacements(thisPanelClient):
		"""Redo the placement of all panels on the display."""
		client = thisPanelClient
		for panel in client._panels:
			panel.replace()		# Redo the placement of this single panel.


	def handle_resize(thisPanelClient):
		"""When we have already figured out the new screen size, this method
			is called by the display to let us do client-specific adjustments."""
		
		client = thisPanelClient

		_logger.debug("panelClient.handle_resize(): Arranging paneled client display.")

			# First, figure out how many columns we have and (if two columns)
			# where the column separator should be positioned.
		client.setupColumns()

			# Next, redo all panel placements. This recalculates all of their 
			# sizes and locations.
		client.redoPlacements()


	def setupColumns(newPanelClient):
		"""Call this on display startup, and after each resize, to configure
			the display columns.  We currently support either 1 or 2
			columns depending on the screen width."""
		
		client = newPanelClient
		display = client.display
		width = display.width
		
		if width >= 123:			# Enough room for two 60-wide columns, plus framing.
			client.nColumns = 2				# Two columns of panels.
			client.colSepPos = int(width/2)	# Horizontal position of the column separator.
		else:
			client.nColumns = 1				# One column of panels.

	
	def reserveBot(thisPanelClient, nRows):
		client = thisPanelClient
		client._botReserved = client._botReserved + nRows

	def reserveBotRight(thisPanelClient, nRows):
		client = thisPanelClient
		client._brReserved = client._brReserved + nRows
			
	def drawSeparator(thisPanelClient):
		client = thisPanelClient
		display = client.display
		screen = display.screen
		
			# Calculate position & height of separator.
		sep_pos		= client.colSepPos
		sep_top		= display.int_top
		sep_height  = display.int_height - client._botReserved
		
			# Use predefined render style for drawing borders.
		attr = style_to_attr(BORDER)	
		
		screen.attrset(attr)
		screen.vline(sep_top, sep_pos, '|', sep_height)
		screen.attrset(0)
	
	def paint(thisPanelClient):
		"""This paint method overrides the demo in DisplayClient."""

		_logger.debug("panelClient.paint(): Repainting panel client")

			# Get some important guys.
		client = thisPanelClient
		display = client.display
		screen = display.screen
		
			# First, if the display isn't even running, then there's nothing
			# to do, so just exit early.
		if not display.isRunning:
			_logger.debug("panelClient.paint(): Display not yet running; exiting early.")
			return
		
			# This is effectively a "lazy clear"--it waits until refresh to take effect.
		display.erase()		# Marks all character cells as empty (and no attributes).
				# (We do this so we don't have to worry about old text hanging around.)

			# Draw a border just inside the edges of the screen.
		display.drawOuterBorder()	# Uses BORDER style.
		
		if client._title is not None:
				# Draw the title in the middle of the top border.
			display.drawCenter(client._title, row=0, lrpad=' ', style=BORDER)
				# (Pads it on the left and the right with a space.)
	
		if client.nColumns == 2:	# Two columns; need to draw separator.
			client.drawSeparator()
	
			# At this point, we need to paint all of our installed panels.
		for panel in client._panels:
			panel.paint()
	
	
	def addPanel(thisPanelClient, panel:Panel):
		"""Adds a panel to the set that is (or will be) displayed by this panel client."""

		client = thisPanelClient

		if panel != None:
		
			thisPanelClient._panels.append(panel)	# First, just add it to our list.
			
				# Tell the panel to go ahead and try to do the work needed to place 
				# itself on our display. (This is needed if the display's already running.)
			panel.place(client)
			
				# Now tell the client to re-display itself (if the display is running).
				# This is what actually causes the new panel to show up on the screen.
			thisPanelClient.redisplay()
