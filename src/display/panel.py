#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 display/panel.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""	FILE NAME:		display/panel.py				 [Python module source file]
	
	MODULE NAME:	display.panel
	IN PACKAGE:		display
	FULL PATH:		$GIT_ROOT/GLaDOS/src/display/panel.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.display (Display screen management)


	MODULE DESCRIPTION:
	===================

		This module defines a base class PanelClient for a category of 
		display clients called "panel clients"; more specific panel clients 
		should inherit from this class.
		
		A panel client is distinguished by organizing the display screen 
		into a set of "panels", or non-overlapping sub-windows for displaying
		different information.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| Original header comment:
#|
#|	This is a module to support applications using a "panel" abstraction 
#|	to manage the display.  The idea behind panels is that they are non-
#|	overlapping windows with clear separators between them, and clearly-
#|	defined placement rules and geometry constraints that determine what 
#|	happens to them when the screen is resized.
#|
#|	Classes defined in this module include:
#|
#|		PanelPlacement	- Enum of supported panel placement modes.
#|		Panel 			- Main class for panels.
#|		PanelClient		- Subclass of DisplayClient for panel-based clients.
#|
#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

global __all__
__all__ = [

			# Major classes we provide.
		'PanelPlacement', 'Panel', 'PanelClient',

			# Panel placement designators.
		'FILL_BOTTOM', 'LOWER_RIGHT', 'FILL_RIGHT', 'FILL_LEFT'

	]

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

#import curses
from curses import error, newwin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .colors import (
		BORDER,				# Render style for panel borders.
		style_to_attr,		# Needed to use render styles.
	)

from .keys import KeyEvent

from .client import (
		DisplayClient,		# We extend this to form panelclient.
	)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PanelPlacement(Enum):

	"""This enum lists the panel-placement specifiers presently supported."""

	FILL_BOTTOM = 'fill-bottom'		# Occupy full width of display, at the bottom. Place this before columnar panels.
	LOWER_RIGHT	= 'lower-right'		# Place this panel at the bottom of the right-hand column (but after previous LOWER_RIGHT panels).
	FILL_RIGHT	= 'fill-right'		# This panel expands to fill all remaining space in the right-hand column.
	FILL_LEFT	= 'fill-left'		# This panel expands to fill all remaining space in the left-hand column.

	def __str__(pp):
		return pp.value

global FILL_BOTTOM, LOWER_RIGHT, FILL_RIGHT, FILL_LEFT
FILL_BOTTOM = PanelPlacement.FILL_BOTTOM
LOWER_RIGHT = PanelPlacement.LOWER_RIGHT
FILL_RIGHT = PanelPlacement.FILL_RIGHT
FILL_LEFT = PanelPlacement.FILL_LEFT	

class Panel: pass
class PanelClient: pass

class Panel:

	"""A region of a panel client's display area that doesn't
		overlap with other panels on the display, except possibly
		that different panels can share edges."""
	
	def __init__(newPanel, 
			title:str = "Untitled Panel",
				 # REQUIRED ARGUMENT. Panel title. CALLER MUST PROVIDE THIS & OVERRIDE.
			initPlacement:PanelPlacement = None,	# REQUIRED ARGUMENT, panel placement specifier.
			initHeight:int = None,					# Initial internal panel height, in rows of text.
			leftPad:int = 1,				# Internal padding at left side of panel (inside border).
			hideTitle:bool = False,		# If true, then we don't display panel's title on its top edge.
		):
		newPanel._title		= title
		newPanel._placement = initPlacement
		newPanel._height	= initHeight		# This is our aspirational/initially-requested height.
		newPanel._leftPad	= leftPad
		newPanel._hideTitle = hideTitle

		newPanel._client	= None				# It hasn't been placed in a client yet.
		newPanel._placed 	= False				# Panel has not actually been placed yet.
		newPanel._win 		= None				# It has no internal sub-window yet.
		newPanel._launched 	= None				# Any subsidiary processes have not been started yet.

	def expand(thisPanel:Panel, byHowMuch:int=1):

		"""This method requests the panel to increase its vertical height by <byHowMuch> rows,
			which defaults to 1.  The method assumes that the display is already running.  As
			a side effect, it causes all panels to be re-placed and the entire display to be
			re-painted."""

		panel = thisPanel
		client = panel.client
		display = client.display
		driver = display.driver

			# This actually updates our internal specifier of the panel's size.
		panel.height = panel.height + byHowMuch

			# Expanding this panel could cause other panels have to be moved or resized, so at this
			# point, the easiest way to figure this out is to just redo all the panel placements.
		client.redoPlacements()

			# This causes the client to regenerate its entire display.
		#client.redisplay()
			# This tells the console client to regenerate the entire console display on the screen.
			# (We do this as a background task to avoid getting into an infinite loop here.)
		#driver.do(client.redisplay)
				# Pushes the redisplay task onto the tail end of the display driver's worklist.

	@property
	def hideTitle(thisPanel):
		return thisPanel._hideTitle

	@property
	def title(thisPanel):
		return thisPanel._title

	@property
	def name(thisPanel):
		return thisPanel.title	# Maybe someday have a separate 'name' ID.

	@property
	def height(thisPanel):
		return thisPanel._height

	@height.setter
	def height(thisPanel, newHeight):
		
		"""This .height property setter sets the panel's height and
			does any other needed adjustments."""
		
		thisPanel._height = newHeight

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
			may extend this as needed to also (re)configure any sub-windows."""
		
		panel	= thisPanel
		client	= panel.client
		display	= client.display
		screen	= display.screen
		win		= panel._win
		
		leftPad = panel._leftPad	# Number of spaces to pad with inside left edge.

		height = panel.height				# Panel AND interior window height.
		int_width = panel.width - leftPad	# Width of interior window.

		if win == None:	# No sub-window yet; create one.

			win_top = panel.top + 1
			win_left = (panel.left +1) + leftPad

			_logger.info(f"Creating window for panel '{panel.name}' with size "
						 f"({panel.height}, {int_width}) at ({win_top}, {win_left}).")

			panel._win = win = screen.subwin(panel.height, int_width, win_top, win_left)
			#panel._win = win = newwin(panel.height, int_width, win_top, win_left)
				# NOTE: <leftPad> gives a number of blank spaces to leave in between the panel's
				# left border and its interior sub-window.
		else:

				# First, we erase any content that may have been
				# left over under the window's old geometry.
			#win.erase()
			
				# Also, we make sure that the text cursor is
				# positioned at the upper-left order of the window.
			win.move(0,0)	

				# Get the window's current size and position relative to its parent.
			(cur_height, cur_width) = win.getmaxyx()
			(cur_winy, cur_winx) = win.getparyx()

				# Now, calculate its new position.
			new_winy = panel.top + 1
			new_winx = (panel.left + 1) + leftPad
				
				# At this point, we haven't actually moved or resized the panel's window yet.
			win_moved = False
			win_resized = False

				#---------------------------------------------------------------
				# Move the existing window if the panel's position changed.

			# Before we try to move it, make sure its position actually changed.
			if (new_winy != cur_winy) or (new_winx != cur_winx):

				_logger.debug(f"panel.configWin(): Moving panel '{panel.name}' "
							  f"internal window to ({new_winy},{new_winx}).")

				try:
					win.mvwin(new_winy, new_winx)
				except error as e:
					_logger.error(f"panel.configWin(): Move attempt generated curses error: {str(e)}")
					raise
				else:
					win_moved = True

				#----------------------------------------------------------
				# Also, resize the window in case the panel's size changed.

			if (height != cur_height) or (int_width != cur_width):

				_logger.debug(f"panel.configWin(): Resizing panel '{panel.name}' "
							  f"internal window to ({height}, {int_width}).")

				try:
					win.resize(height, int_width)
				except error as e:
					_logger.error(f"panel.configWin(): Resize attempt generated curses error: {str(e)}")
					raise
				else:
					win_resized = True


			# If we actually did either move or resize the window, then
			# mark the entire window as needing to be redrawn on refresh.
			if win_moved or win_resized:
				win.redrawwin()

			# Refresh the panel window; will take effect on next display update.
		win.noutrefresh()
	
	def replace(thisPanel):

		"""Same as .place() but for previously placed panels."""

		panel = thisPanel

		panel._placed = False
			# This is needed in order for .place() to do anything.

		panel.place()
		
	def place(thisPanel, panelClient:PanelClient = None):
	
		"""This does the actual work of placing the panel within the client display.
			This figures out the panel's size and location on the display, and 
			creates the sub-window object for its contents (within its frame)."""

		panel = thisPanel

		# If panel's client is being provided in an argument, then store it.
		if panelClient is not None:
			panel._client = panelClient
			
		client = panel._client

		# There's only anything we can do right now if the client's display is actually up and running.
		if not client.dispRunning:
			return
	
		# Also, if the panel is already placed, we don't need to do anything here.
		if panel._placed:
			return
	
		display = client.display	# Get the display.

			# Get the coordinates of the bottom/right edges of the screen.
		(scr_bot, scr_right) = display.get_max_yx()
	
		placement = panel._placement	# Get the panel's placement specifier.
	
		_logger.debug(f"panel.place(): About to place panel '{panel.name}' with placement {placement}.")

		# Here we process the placement and figure out panel coordinates.
		if placement == FILL_BOTTOM:
			# This places the panel across the bottom of the screen (both columns).
		
			panel.left = 0				# Left side of panel = left side of screen.
			panel.right = scr_right		# Right side of panel = right side of screen.
			
				# This places the panel above any previously placed FILL_BOTTOM panels.
			panel.bottom = scr_bot - client._botReserved

				# This reserves enough space at the bottom of the screen for
				# this panel and its top border/separator.
			client.reserveBot(panel.height + 1) 	# One extra for top edge.

				# This just calculates the panel's top edge.
			panel.top = scr_bot - client._botReserved
			
		elif placement == LOWER_RIGHT:
			
			# Here we do one of two different things depending on whether the client is in
			# one-column or two-column mode.
			
			if client.nColumns == 2:		# Two-column mode.
			
				_logger.debug("panel.place(): Doing LOWER_RIGHT placement for 2 columns.")

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

		#__/ End placement cases.


			# Compute internal width of panel (including pad but not border).
			#
			#	* Width *including* both left/right borders is right - left + 1
			#	* width *excluding* borders is right - left - 1

		panel.width = panel.right - panel.left - 1

		panel.configWin()	# Creates/resizes panel's internal window(s) as needed.
		
		panel._placed = True	# Remember we've been placed.

		# Now that the panel is placed, go ahead and paint it on the display.
		panel.paint()

	
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
		if top > 0:
			screen.addch(top, left, tlchar)
			screen.addch(top, right, trchar)
		screen.addch(bottom, left, blchar)
		if bottom != scr_bot or right != scr_right:		# Avoids an exception
			screen.addch(bottom, right, brchar)

			# Draw the edges.
		if top > 0: screen.hline(top, 	 left+1, '-', width)
		#screen.hline(bottom, left+1, '-', width)
			# Skip the bottom edge so we don't cover up title of panel below us.
		screen.vline(top+1,  left,   '|', height)
		screen.vline(top+1,  right,  '|', height)
		
			# Special case: For two-column-wide panels at top or bottom of screen, draw a '+' where column separator joins top or bottom edge.
		if client.nColumns == 2:
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
			panel.place(client)		# Assume client was set earlier at least.

			# OK, next, draw the panel's frame.
		panel.drawFrame()
		
			# Now draw the panel's title in its top frame, in border style.
		if panel.title != None and not panel.hideTitle:
			paddedTitle = ' ' + panel.title + ' '
			screen.addstr(panel.top, panel.left + 4, paddedTitle, style_to_attr(BORDER))
		
			# Now paint the panel's contents.  This method is implemented by the subclass.
		panel.drawContent()
	
	
	def clear(thisPanel):
		"""Clear's the panel's interior window."""
		panel = thisPanel
		win = panel.win
		win.clear()


	def drawContent(thisPanel):
	
		"""Extend this method to draw actual content in the given panel.
			This method should assume that the panel is initially erased,
			and that it will be refreshed some time after it's finished.
			Please note that subclass implmentations overriding this method
			should extend it by using super() to call this method before
			they return."""
	
		panel = thisPanel
		win = panel.win
	
		#/----------------------------------------------------
		#| EXTEND METHOD WITH ANY ADDITIONAL CODE BEFORE HERE.
		#\----------------------------------------------------
	
			# Updates screen locations that were changed in panel's interior window.
		#win.syncup()

			# Tell the display the panel's window needs refreshing now.
		win.noutrefresh()
	
		# Now is a good time to launch any subsidiary threads/processes
		# associated with the panel, if not already done.
		
		if not panel._launched:
			panel.launch()
			panel._launched = True
			
	#__/ End method panel.drawContent().


	def regenerateContent(thisPanel):
	
		"""[Display driver thread] This regenerates all of the content
			of the panel, but postpones the actual screen refresh, which
			can be done later using display.update().  This method is
			useful if you want to regenerate multiple panels before
			refreshing."""
	
		panel 	= thisPanel
		client	= panel.client
		display	= client.display
		win		= panel.win			# The panel's internal sub-window.
		
		with display.lock:	# Make sure display is locked.

			# Erase whatever is presently in the panel's subwin.
			win.erase()
		
			# Fill in panel contents.
			panel.drawContent()
			

	def redisplayContent(thisPanel):
	
		"""This repaints and refreshes the display of just this panel's 
			content, leaving the rest of the screen untouched."""
		
		panel 	= thisPanel
		client  = panel.client
		display	= client.display

			# Regenerate (draw from scratch) the content of this panel.
		panel.regenerateContent()
		
			# Tell curses to update the physical display.
		display.update()
		
	
	def launch(thisPanel):
	
		"""This starts up any subsidiary processes/threads that may be required
			in order to generate content that will be displayed in this panel.
			Subclasses should override this as needed."""
			
		panel = thisPanel	# Shorter name for argument.

		# DO SOMETHING HERE
		
	#__/ End method panel.launch().

	def grabFocus(thisPanel:Panel):
		"""Tells the panel to grab the keyboard focus."""
		
		panel	= thisPanel
		client	= panel.client
		
		client.setFocusPanel(panel)

#__/ End class Panel.


class PanelClient(DisplayClient):

	"""A type of DisplayClient that organizes the display into non-overlapping panels."""
	
	
	def __init__(newPanelClient, 
			title:str="Untitled Panel Client"	# REQUIRED ARGUMENT, client title; replace this!
		):
		"""Initializer for newly-created PanelClient instances."""
		
		client = newPanelClient

			# We first call the default initialization method from DisplayClient.
		super(PanelClient, client).__init__()
		
			# Stash our subclass-specific arguments.
		client._title = title	# Client title string.

			# Initialize some subclass-specific data structures.
		client._panels = []		# Initially empty list of panels.
		
			# Initialize the layout constraints.
		client._resetLayout()

			# Initialize the input focus panel.
		client._focusPanel = None

	def setFocusPanel(thisPanelClient:PanelClient, panel:Panel=None):
		"""This method sets which panel has the keyboard focus."""

		client	= thisPanelClient
		display	= client.display
		driver	= display.driver
		
		client._focusPanel = panel
		if panel is not None:
			if client.dispRunning:	# If the display is running,
				win = panel.win
				driver(win.cursyncup)		# Put the visible cursor in the selected panel.
					# Run in foreground to ensure new setting is visible before we go on.

	@property
	def focusPanel(thisPanelClient:PanelClient):
		return thisPanelClient._focusPanel

	def _resetLayout(thisPanelClient):

		"""This private method resets all of our internal panel-layout constraints,
			in preparation for panel placement."""

		client = thisPanelClient
		
			# These instance variables keep track of how much of the screen is reserved currently.
		client._botReserved = 0		# Rows reserved across entire screen bottom.
		client._brReserved = 0		# Rows reserved across bottom of right column.
		client._blReserved = 0		# Rows reserved across bottom of left column.


	def redoPlacements(thisPanelClient):
		"""Redo the placement of all panels on the display."""

		client = thisPanelClient

			# Re-initialize all of the panel layout constraints.
		client._resetLayout()

		# Now, re-place each of the individual panels.
		for panel in client._panels:	# For each panel in our list,
			panel.replace()		# Redo the placement of this single panel.
		
			# Tell the client to tell its screen that, after all that, it needs refreshing.
			# This is needed to make sure panel borders are updated.
		client.requestRefresh()

			# Now is a good time to update the panel client's physical display?
		client.updateDisplay()
	
	#__/ End method redoPlacements().


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

			# Now, tell the display to repaint the screen.
		#client.redisplay()
			# This is now done in TheDisplay._resize() after this returns.

	#__/ End method panelClient.handle_resize().


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
	#__/ End method setupColumns().

	
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
	#__/ End method drawSeparator().
	

	def redrawFrames(thisPanelClient):
		"""This is like .paint(), except that it only redraws the panel frames,
			but not the panel contents."""
		
		# NOTE: Not yet implemented or used.


	def paint(thisPanelClient):

		"""This paint method overrides the demo in DisplayClient.
			
			Context reminders: When this is called, all we know is that
			a complete re-painting of the display screen has been requested.
			The display buffer has not yet been erased.  The job of this 
			method is to do all of the display operations required to fill
			out the client's display.  After this returns, the display will 
			automatically be refreshed from its buffer in display.paint().
		"""

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
		
		# Erases what's on the main screen -- EVERYTHING IN BETWEEN THE PANEL INTERIOR WINDOWS.
		# This is effectively a "lazy clear"--it waits until refresh to take effect.
		display.erase()		# Marks all character cells as empty (and no attributes).
				# (We do this so we don't have to worry about old junk hanging around.)

		try:

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

		except error as e:
			_logger.error("panelClient.paint(): Got a curses error: " + str(e))
	
		# Not that it matters, since we have turned off the automatic cursor
		# display in display._init(), but we "Home" the cursor to (0,0).
		screen.move(0,0)
	#__/ End method panelClient.paint().

	
	def addPanel(thisPanelClient, panel:Panel):
		"""Adds a panel to the set that is (or will be) displayed by this panel client."""

		client = thisPanelClient

		if panel != None:
		
			client._panels.append(panel)	# First, just add it to our list.
			
				# Tell the panel to go ahead and try to do the work needed to place 
				# itself on our display. (This is needed if the display's already running.)
			panel.place(client)
			
				# Now tell the client to inform the display that the screen needs
				# repainting.
			#client.requestRepaint()
	#__/ End method addPanel().


	def handle_event(thisPanelClient:PanelClient, keyEvent:KeyEvent):
	
		"""This standard DisplayClient method is called by the display
			mainloop (in the display driver thread) to request the client
			to handle a keypress."""

		client = thisPanelClient
		
		# First call the superclass method in DisplayClient.
		super(PanelClient, client).handle_event(keyEvent)
			# So far this doesn't do much. This is optional.
			
		# If a panel has the focus, dispatch the keypress to it.
		focusPanel = client.focusPanel
		if focusPanel is not None:
			focusPanel.handle(keyEvent)
	#__/ End method handle_event().

#__/ End class PanelClient.

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/panel.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
