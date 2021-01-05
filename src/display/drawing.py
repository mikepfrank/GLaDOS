#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 display/drawing.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		display/drawing.py				 [Python module source file]
	
	MODULE NAME:	display.drawing
	IN PACKAGE:		display
	FULL PATH:		$GIT_ROOT/GLaDOS/src/display/drawing.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.display (Display screen management)


	MODULE DESCRIPTION:
	===================
	
		This module simply gathers together several functions that are 
		useful for drawing content onto a curses screen or window.
	
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

			#|-----------
			#| Functions.
		
			# Drawing functions.
		'draw_rect', 'addLineClipped', 'addTextClipped',
				
	]


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(drawing.)draw_rect()							   [public function]
		#|
		#|		Draws a rectangular box on the given window using the
		#|		specified attribute settings.
		#|
		#|		NOTE: Needs a bug-fix to work on the right or bottom
		#|		edge of the display (turn on leaveok temporarily?).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def draw_rect(win, top, left, bottom, right, att):

	"""Draws a rectangle with the given coordinates."""
	# NOTE: Should be rewritten using .vline(), .hline().

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

#__/ End module public function drawing.draw_rect().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(drawing.)addLineClipped()						   [public function]
		#|
		#|		Adds the given line of text to the given curses window,
		#|		with clipping to fit within the window width.  If the
		#|		optional keyword argument <padRight> is provided, it is
		#|		taken as a number of blanks to pad with on the right.
		#|		If it is not specified, the default pad is 1 character.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def addLineClipped(win, line:str, attrs:int, padRight:int=None):

	"""Adds a line of text to a window, with clipping to fit in the window width.
		Assumes <line> does not contain any newline characters."""
	
	if padRight is None:
		padRight = 1		# Default padding to 1 character.
	
		# Get the current cursor position.
	(curRow, curCol) = win.getyx()		
	
		# Get the width and height of the current window.
	(winHeight, winWidth) = win.getmaxyx()
	effWidth = winWidth - padRight
	
		# Get the length of the line.
	lineLen = len(line)
	
		# Clip the line down to what we have room for.
	if curCol + lineLen >= effWidth:
		line = line[:effWidth - curCol]
	
	win.addstr(line, attrs)

#__/ End module public function drawing.addLineClipped().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(drawing.)addTextClipped()						   [public function]
		#|
		#|		Adds the given (possibly multi-line) block of text to 
		#|		the given curses window, with clipping of each line to 
		#|		fit within the window width.  If the optional keyword 
		#|		argument <padRight> is provided, it is taken as a number 
		#|		of blanks to pad with on the right.  If it is not 
		#|		specified, the default pad is 1 character.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def addTextClipped(win, text:str, attrs:int, padRight:int=None):
	"""Adds the given text to the window, clipping each line
		to fit within the window width."""
		
	lines = text.split('\n')	# Break the text into lines.

	#_logger.debug("addTextClipped(): About to add line:\n" + lines[0])

		# Add the first line (without terminating it with newline).
	addLineClipped(win, lines[0], attrs, padRight=padRight)

		# If there are more lines, add them, with newlines in between.
	for line in lines[1:]:
		win.addstr("\n", attrs)		# Add a newline.

		#_logger.debug("addTextClipped(): About to add line:\n" + line)

		addLineClipped(win, line, attrs, padRight=padRight)
	
	#__/ End loop over lines.
	
#__/ End module public function drawing.addLineClipped().


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/drawing.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%