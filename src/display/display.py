# display.py
#
# This module supports display on a text terminal, which is managed using the curses library.
#
# This module is used by both the GLaDOS system console package, and by the terminal package,
# which manages individual users' sessions when they're connected to the GLaDOS server.
#

from enum import Enum

from os		import	environ, path	# Manipulate filesystem path strings.
from infrastructure.logmaster import getComponentLogger
global _component, _logger		# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.

#------------------------------------------------------------
# Here we obtain the default string encoding from the system.

import locale

	# This sets the locale for all categories to the user's default setting, e.g., from LANG environment variable.
locale.setlocale(locale.LC_ALL, '')

	# This gets the preferred encoding configured by the user preferences (system-dependent).
global encoding	# We'll use this wherever we need to encode/decode strings to bytes.
encoding = locale.getpreferredencoding()


#-----------------------------------------------
# Import stuff we need from the curses library.

import curses
from curses import *
from curses.textpad import rectangle, Textbox
from curses.ascii import controlnames, iscntrl, isspace, isgraph

#-------------------------------------
# Imports of optional/custom packages.

from infrastructure.decorators import singleton

#-------------------------------------------------------------
# Brightness values.

class Brightness(Enum):
	"""
	Enumerated type for color display brightness values.
	We're assuming the display (like xterm/Putty) supports
	'normal' and 'bright' brightness values.  (We only 
	assume that 'dim' is supported in the case of white; 
	internally, this is implemented as "bright black.")
	"""
	DIM='dim'			# Supported only for white (implemented as bright black).
	NORMAL='normal'
	BRIGHT='bright'

# Define shorter names for brightness values.
global DIM, NORMAL, BRIGHT
DIM=Brightness.DIM
NORMAL=Brightness.NORMAL
BRIGHT=Brightness.BRIGHT

#---------------------------------------------------------------------------------
# A "color specifier" is a pseudo-type that actually just consists of an ordered
# pair; the first element of the pair is a "base color" which means a curses color;
# the second element of the pair is a brightness value, as above.  The following
# function constitutes a special constructor for color specifiers, which automatically
# translates "dim white" to "bright black", to make our code more readable.

def ColorSpec(baseColor, brightness):
	"""Generates a pair representing a color specification consisting of
		a base color together with a brightness value."""
	
	# Replace "dim white" with "bright black."
	if (baseColor is COLOR_WHITE) and (brightness is DIM):
		baseColor = COLOR_BLACK
		brightness = BRIGHT
		
	# Return the color/brightness pair we just constructed.
	return (baseColor, brightness)


# Define shorter names for certain color specifiers we'll use.

	# Gray-scale colors.
BRIGHT_WHITE = ColorSpec(COLOR_WHITE, BRIGHT)
WHITE		 = ColorSpec(COLOR_WHITE, NORMAL)
GRAY		 = ColorSpec(COLOR_WHITE, DIM)		# Same thing as bright black.
BLACK		 = ColorSpec(COLOR_BLACK, NORMAL)

	# Primary colors.
RED	  = ColorSpec(COLOR_RED,   NORMAL)
GREEN = ColorSpec(COLOR_GREEN, NORMAL) 
BLUE  = ColorSpec(COLOR_BLUE,  NORMAL)

	# Secondary colors.
CYAN	= ColorSpec(COLOR_CYAN,	   NORMAL)
MAGENTA	= ColorSpec(COLOR_MAGENTA, NORMAL)
YELLOW	= ColorSpec(COLOR_YELLOW,  NORMAL)

	# Bright primary colors.
BRIGHT_RED	 = ColorSpec(COLOR_RED,	  BRIGHT)
BRIGHT_GREEN = ColorSpec(COLOR_GREEN, BRIGHT) 
BRIGHT_BLUE	 = ColorSpec(COLOR_BLUE,  BRIGHT)

	# Bright secondary colors.
BRIGHT_CYAN	   = ColorSpec(COLOR_CYAN,	  BRIGHT)
BRIGHT_MAGENTA = ColorSpec(COLOR_MAGENTA, BRIGHT)
BRIGHT_YELLOW  = ColorSpec(COLOR_YELLOW,  BRIGHT)

#---------------------------------------------------------------------------------------------
# This function returns the curses display attributes for a given fg/bg pair of color specs.

def colors_attr(fgColorSpec, bgColorSpec):
	"""Turns a pair of color specs into appropriate display attributes."""

		#---------------------------------------------------
		# Extract the base foreground and background colors.
		
	(fgBase, fgIntensity) = fgColorSpec
	(bgBase, bgIntensity) = bgColorSpec

		#|---------------------------------------------------------------------
		#| Turn the foreground-background base colors into a color-pair index.
		#| (For this to work, note that we must have previously set up the 
		#| color pairs accordingly.
		
	colorPairIndex = bgBase*8 + (fgBase+1)%8

		#|---------------------------------
		#| Calculate the attribute setting.
		
	# Start with the attribute setting for the color pair.
	attrVal = color_pair(colorPairIndex)
	
	# To make the foreground color bright, apply the 'bold' attribute.
	if fgIntensity is BRIGHT:
		attrVal = attrVal | A_BOLD	
			# Note the 'bold' attribute on xterm/Putty really just makes foreground brighter.
	
	# To make the background color bright, apply the 'blink' attribute.
	if bgIntensity is BRIGHT:
		attrVal = attrVal | A_BLINK	
			# Note the 'blink' attribute on xterm/Putty really just makes background brighter.

	return attrVal

#------------------------------------------------------------------------------
# Predefined rendering styles. Each of these selects a particular combination
# of display attributes. So far we have available to choose from: Color, 
# brightness, and underline. Italics may be available in some environments.

# Enumerated type of predefined render styles.
class RenderStyle(Enum):

	# Use this style for normal printable text.
	PLAIN='plain'

	# Use this style for drawing borders.
	BORDER='border'

	# Use this style for rendering 7-bit control characters.
	CONTROL='control'

	# Use this style for rendering whitespace characters
	WHITESPACE='whitespace'

	# Use this style for rendering control characters with 8th bit set.
	META_CONTROL='meta-control'

	# Use this style for rendering whitespace characters with 8th bit set.
	META_WHITESPACE='meta-whitespace'

# Put the render styles in shorter globals.
global PLAIN, BORDER, CONTROL, WHITESP, METACTL, METAWSP
PLAIN	=	RenderStyle.PLAIN
BORDER	=	RenderStyle.BORDER
CONTROL	=	RenderStyle.CONTROL
WHITESP	=	RenderStyle.WHITESPACE
METACTL	=	RenderStyle.META_CONTROL
METAWSP	=	RenderStyle.META_WHITESPACE

_style_colors = {	# Maps render style to (fgcolor,bgcolor) pairs.
	#STYLE:		(FOREG,		  BACKG ),
	PLAIN:		(WHITE,		  BLACK ),	# Normal characters: White text on black background.
	BORDER:		(BRIGHT_CYAN, BLACK ),	# Border characters: Bright cyan text on a black background.
	CONTROL:	(BLACK,		  RED	),	# Control characters: Black text on red background.
	WHITESP:	(GRAY,		  BLACK ),	# Whitespace characters: Faded (gray) text on black background.
	METACTL:	(BLACK,		  BLUE	),	# Meta-control characters: Black text on blue background.
	METAWSP:	(BLUE,		  BLACK ),	# Meta-whitespace characters: Blue text on black background.
}

def style_to_attr(style):
	"""Given a render style, convert it to a display attribute setting."""
	(fgSpec, bgSpec) = _style_colors[style]
	return colors_attr(fgSpec, bgSpec)

#------------------------------------------------------------------
# The idea of the below is that, on terminals without full Unicode
# font support, we can render various (normally non-printable)
# ASCII control and whitespace characters as a single 7-bit
# character glyph using some alternate display attributes.

nonprint_7bit_glyphs = {	# Returns pair of (render style, printable character)
	0:	(CONTROL, '_'),	# Null character.
	1:	(CONTROL, ':'),	# Start of heading.
	2:	(CONTROL, '['),	# Start of text.
	3:	(CONTROL, ']'),	# End of text.
	4:	(CONTROL, '.'),	# End of transmission.
	5:	(CONTROL, '?'),	# Enquiry.
	6:	(CONTROL, 'Y'),	# Acknowledgement.
	7:	(CONTROL, '*'),	# Bell.
	8:	(CONTROL, '<'),	# Backspace.
	9:	(WHITESP, '>'),	# Horizontal tab.
	10:	(WHITESP, '/'),	# Line feed.
	11: (WHITESP, 'v'),	# Vertical tab.
	12:	(WHITESP, 'V'),	# Form feed.
	13:	(WHITESP, '<'),	# Carriage return.
	14:	(CONTROL, '('),	# Shift-out.
	15:	(CONTROL, ')'),	# Shift-in.
	16:	(CONTROL, '/'),	# Data-link escape.
	17:	(CONTROL, 'o'),	# Device control 1.
	18:	(CONTROL, '@'),	# Device control 2.
	19:	(CONTROL, '='),	# Device control 3.
	20:	(CONTROL, '-'),	# Device control 4.
	21:	(CONTROL, 'N'), # Negative acknowledgement.
	22:	(CONTROL, '~'),	# Synchronous idle.
	23:	(CONTROL, ';'),	# Emd transmission block.
	24: (CONTROL, 'X'), # Cancel.
	25:	(CONTROL, '|'), # End of medium.
	26:	(CONTROL, '$'),	# Substitute.
	27: (CONTROL, '^'),	# Escape.
	28:	(CONTROL, 'F'),	# File separator.
	29: (CONTROL, 'G'),	# Group separator.
	30: (CONTROL, '&'),	# Record separator.
	31: (CONTROL, ','), # Unit separator.
	32: (WHITESP, '_'),	# Space.
	127:(CONTROL, '#'), # Rubout/delete.
}

def isNonprinting(code):

	# 7-bit ASCII x00-1F controls and space.
	if code >=0 and code <= 32:
		return True

	if code == 127:		# Delete charater.
		return True

	# Controls in 8-bit ASCII/Unicode
	if code >= 128 and code <= 159:
		return True

	# For everything else, assume it's printing.
	return False

def isMeta(code):
	"""Retruns True if <code> is an 8-bit code point
		with its high-order bit set (0x80-0xFF)."""
	if code >= 128 and code <= 255:
		return True

# The following renders even nonprintable control/whiteplace characters
# using substitute glyphs with alternate attributes.
def render_char(win, code, baseAttrs=0):	
	# win is screen or window.
	# code is the ordinal character code point.

	# If it's not non-printing, just render it normally.
	if not isNonprinting(code):
		if code >= 0 and code <= 0x10ffff:
			win.addstr(chr(code))
		else:
			_logger.warn("render_char(): Was given an invalid code point {code}. Ignoring.")
		return

	# OK, figure out the style and glyph to use.
	if isMeta(code):
		(style, glyph) = nonprint_7bit_glyphs[code-128]
		if style is CONTROL:
			style = METACTL
		elif style is WHITESP:
			style = METAWSP
	else:
		(style, glyph) = nonprint_7bit_glyphs[code]

	# Convert the style to a display attribute setting.
	attr = style_to_attr(style) | baseAttrs
	
	# Now display, using those attributes.
	win.addstr(glyph, attr)
	
def draw_rect(win, top, left, bottom, right, att):

	_logger.info(f"Drawing rectangle from ({top},{left}) to ({bottom},{right})...")

		# Draw the corner characters.
	win.addstr(top,		left,  '/',	 att) 
	win.addstr(bottom,	right, '/',	 att)
	win.addstr(top,		right, '\\', att)
	win.addstr(bottom,	left,  '\\', att)
	
		# Draw the horizontal edges.
	for x in range(left+1, right):
		win.addstr(top,	   x, '-', att)
		win.addstr(bottom, x, '-', att)
		
		# Draw the vertical edges.
	for y in range(top+1, bottom):
		win.addstr(y, left,	 '|', att)
		win.addstr(y, right, '|', att)
		
	win.refresh()

def keystr(k):
	
	if k==KEY_RESIZE:
		return "Resize"
	elif k==ERR:
		return "<ERROR>"
	else:
		try:
			return keyname(k).decode(encoding)
		except ValueError as e:
			_logger.error(f"keystr(): {str(e)}: Received unknown key code {k}.")

class Loc:
	def __init__(thisloc, y=None, x=None):
		thisloc.x = x
		thisloc.y = y

class DisplayClient:
	"""A display client is an entity that uses the display as a server
		to interact with the user.	Only one client may use the display
		at a time."""

	def __init__(thisClient):
			# Connect us up with the display.
		thisClient._display = display = TheDisplay()
		display.setClient(thisClient)

	def run(thisClient):
		display = thisClient._display
		display.run()

	def addChar(thisClient, char:int, *args, **argv):
		display = thisClient._display
		display.renderChar(char)

	def addText(thisClient, text:str, *args, **argv):
		display = thisClient._display
		display.add_str(text, *args, **argv)

	def drawOuterBorder(thisClient):
		attr = style_to_attr(BORDER)
		
		client = thisClient
		display = client._display
		#(max_y, max_x) = display.get_max_yx()
		
			# Draw a border-style rectangle around the edges of the display screen.
		#draw_rect(thisClient._display.screen, 0, 0, max_y, max_x, attr)
		display.screen.attrset(attr)
		display.screen.border('>', '<', 'v', '^', '/', '\\', '\\', '/')
		display.screen.attrset(0)
		(client._lry, client._lrx) = getsyx()

	def paint(thisClient):
		"""Subclasses should override/extend this method to paint the display."""

		thisClient._display.erase()
		thisClient.drawOuterBorder()
		
		if hasattr(thisClient, '_lastEvent'):
			thisClient.displayEvent()

		thisClient._display.refresh()
		
	def displayEvent(thisClient):

		keyevent = thisClient._lastEvent

		client = thisClient
		keycode = keyevent.keycode
		keyname = keyevent.keyname

		(height, width) = client._display.get_size()

			# Default behavior: Display information about key code received.
		client.addText(f"Screen size is {height} rows high x {width} columns wide.", Loc(1,2))
		client.addText(f"LINES,COLS={curses.LINES},{curses.COLS}. [{client._lry},{client._lrx}]", Loc(2,2))
		client.addText(f".getmaxyx() returns: {client._display.screen.getmaxyx()}", Loc(3,2))
		client.addText(f"Received key code: #{keycode}.", Loc(4,2))
		#client.addText(f"Wide char code: {widechar}.", Loc(3,2))
		client.addText(f"Direct rendering is: ", Loc(5,2))
		client.addChar(keycode)		# What if we interpret keycode directly as a character?
		client.addText(f"Key name string is: ({keyname})", Loc(6,2))

	def handle_event(thisClient, keyevent):
		"""Subclasses should override this method with their own event handler."""

		client = thisClient
		keycode = keyevent.keycode
		keyname = keyevent.keyname
		
		client._lastEvent = keyevent

		_logger.debug(f"Got a key with code={keycode}, name={keyname}.")

		if keycode == KEY_RESIZE:
			client._display.resize()
		else:
			client.paint()

class KeyEvent:
	def __init__(thisKeyEvent, keycode=None):
		thisKeyEvent.keycode = keycode
		thisKeyEvent.keyname = keystr(keycode)

class RestartCurses(Exception):
	pass

@singleton
class TheDisplay:
	"""
	This is a singleton class.	Its sole instance represents a text display
	screen, which is managed by the curses library.	 For now, it assumes
	that the display is compatible with xterm/Putty.
	"""
	def __init__(theDisplay):
		"""Initializes the display system."""
		# Nothing to do here yet. Nothing happens until .run()
		pass
	
	@property
	def screen(theDisplay):
		"""This handles getting theDisplay.screen attribute.
			Note this is an error if the display isn't running."""
		return theDisplay._screen

	def _measure_terminal_size(theDisplay):
		"""This measures the actual current size of the display
			terminal. So far, the only way we've found to do this
			is to try drawing characters at progressively greater
			coordinates until we get an exception.	This seems
			like an extremely hacky way to do it, but it works."""

			# Say it's not OK for the cursor to leave the window.
		theDisplay._screen.leaveok(False)

		# Try progressively greater x coordinates.
		sx = 0
		while True:
			try:
				theDisplay.screen.addch(0,sx,'*')
			except:
				#	_logger.debug(f"In _measure_terminal_size(), sx loop: Got exception: {str(e)}")
				break
			sx = sx + 1
		width = sx

		# Try progressively greater y coordinates.
		sy = 0
		while True:
			try:
				theDisplay.screen.addch(sy,0,'*')
			except:
				#_logger.debug(f"In _measure_terminal_size(), sy loop: Got exception: {str(e)}")
				break
			sy = sy + 1
		height = sy

		_logger.debug(f"_measure_terminal_size(): Got height={height} lines and width={width} columns.")

			# Now that we've measured the terminal size, make sure that the
			# (possibly new) size gets recorded properly in several places.
		theDisplay._record_terminal_size(height, width)
		
	def _record_terminal_size(theDisplay, term_height, term_width):
		"""Records the specified terminal size in various data structures."""

			# First, store it in our singleton instance data members.
		theDisplay._width  = term_width
		theDisplay._height = term_height

			# Also set these derived members.
		theDisplay._max_x = term_width - 1
		theDisplay._max_y = term_height - 1

			# Next, store width/height in some standard environment variables.
		#environ['LINES'] = str(term_height)
		#environ['COLUMNS'] = str(term_width)

			# Next, tell curses to update its internal LINES,COLS attributes.
		#update_lines_cols()

	# def	_reinitScreen(theDisplay):
	#	"""Re-initializes the top-level curses window or 'screen.'
	#		This is necessary to pick up terminal size changes."""
	#	theDisplay._screen = screen = initscr()
	#	return screen

	def setClient(theDisplay, displayClient):
		theDisplay._client = displayClient
	
	def refresh(theDisplay):
		screen = theDisplay._screen

	def erase(theDisplay):
		"""Erases the display.""" # Minimal
		theDisplay._screen.erase()
	
	def clear(theDisplay):
		"""Clears the display."""
			# Dispatch to the underlying curses display.
		theDisplay._screen.clear()

	def renderChar(theDisplay, charcode):
		screen = theDisplay._screen
		render_char(screen, charcode)

	def add_str(theDisplay, text:str, loc=None, attr=None):
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
	
	def paint(theDisplay):
		"""Paints the display; i.e., fills it with content."""
		# Delegate this to the client.
		theDisplay._client.paint()
		theDisplay.screen.refresh()
	
	def get_max_yx(theDisplay):
		return (theDisplay._max_y, theDisplay._max_x)

	def get_size(theDisplay):
		return (theDisplay._height, theDisplay._width)
	
	def _check_size(theDisplay):

		"""Check the current size of the display screen."""

		screen = theDisplay._screen

		(height, width) = screen.getmaxyx()
		_logger.debug(f"._check_size(): .getmaxyx() returned {(height,width)}.")

		theDisplay._width  = width
		theDisplay._height = height
			# Calculate and store bottom,right coordinates as well.
		theDisplay._max_x  = width - 1
		theDisplay._max_y  = height - 1
	#		# Next, store width/height in some standard environment variables.
	#	environ['LINES'] = str(height)
	#	environ['COLUMNS'] = str(width)
	#		# Next, tell curses to update its internal LINES,COLS attributes.
	#	update_lines_cols()		# Uses environment variables we just set.


	def resize(theDisplay):
		"""Call this method when you want to handle a resize event."""

			# Now we potentially need to resize the window structures
			# within curses, if the terminal size has actually changed.
		theDisplay._check_size()
		(height, width) = theDisplay.get_size()

		#_logger.debug(f".resize(): Before resizing, .getmaxyx() returned {theDisplay._screen.getmaxyx()}.")

		#theDisplay._measure_terminal_size()
		#(height, width) = theDisplay.get_size()

		#if is_term_resized(height, width):
		_logger.debug(f".resize(): Resizing terminal to {(height,width)}.")
		resizeterm(height, width)

		#_logger.debug(f".resize(): curses.LINES={curses.LINES}, curses.COLS={curses.COLS}.")

		#theDisplay._measure_terminal_size()
		#(height, width) = theDisplay.get_size()

		#_logger.debug("Handling a resize event by restarting curses.")
			# Only way to find out new size?
		#raise RestartCurses

		theDisplay.paint()

	def _initColorPairs(theDisplay):
		"""This initializes the color pairs, assuming 8 standard colors and 64 pairs."""
		for pair_index in range(1,64):		# Iterate over 6-bit color pair codes.
		
				# Obtain the background color as the most-significant 3 bits.
			bgcolor = int(pair_index / 8)
			
				# Obtain the foreground color from the least-significant 3 bits.
			fgcolor = (pair_index - 1) % 8	# The -1 (+7) here is needed because pair 0 has fg=white standardly.
			
				# Make sure that particular color pair is set up properly as we want it.
			_logger.info(f"Creating color pair #{pair_index} = (fg: {fgcolor}, bg: {bgcolor}).")

			init_pair(pair_index, fgcolor, bgcolor)

	def _initDisplay(theDisplay):
		"""Initializes the curses display."""

			# Initialize the color pairs to be what we expect.
		theDisplay._initColorPairs()
		
			# Say it's OK for the cursor to leave the window.
		#theDisplay._screen.leaveok(False)

		theDisplay.resize()

			# At this point, hopefully screen.getmaxyx() will pick up
			# the correct values of screen height and width.
#		theDisplay._check_size()
#		height = theDisplay._height
#		width = theDisplay._width

			# Repaint the display.
#		theDisplay.paint()
	
	
	def _runMainloop(theDisplay):
		
		screen = theDisplay._screen
		client = theDisplay._client
		
		# Here's the actual main loop.
		while True:	# Infinite loop; we just have to break out when done.
			try:
				#wide_ch = screen.get_wch()		# Wide instead of regular character.
				#unget_wch(wide_ch)
				ch = screen.getch()
				if ch == ERR:
					#_logger.error("_runMainLoop(): Received keycode ERR (-1).")
					continue
				keyevent = KeyEvent(keycode=ch) #, wide=wide_ch)
				client.handle_event(keyevent)
			except KeyboardInterrupt as e:
				break
			except RestartCurses as e:
				theDisplay._restart = True
				break
	
	def _displayDriver(theDisplay,
			screen	# This is the top-level curses window for the whole terminal screen.
		):		
		"""Private method to drive the curses display. It is called by 
			theDisplay.runDisplay(), below.	 Note that when this driver 
			method returns, the entire display will be torn down. So, it 
			should not exit until we are completely done with using the 
			display."""
		theDisplay._screen = screen
		theDisplay._initDisplay()		# Initialize the display.
		theDisplay._runMainloop()		# Run the main loop.

	def run(theDisplay):
		"""This method is responsible for bringing up and operating the entire
			display, and bringing it down again when done.	It needs to be run 
			in its own thread, so that other systems can asynchonously communicate
			with it."""
			
		while True:
			theDisplay._restart = False
			# Call the standard curses wrapper on our private display driver method, above.
			wrapper(theDisplay._displayDriver)
			if not theDisplay._restart:
				break
		# If we get here, then the display driver has exited, and the display was torn down.
	#__/ End method theDisplay.runDisplay().
	
#__/ End singleton class TheDisplay.
