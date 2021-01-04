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
		
		
			#|-----------
			#| Functions.
		
		'colors_attr', 'style_to_attr', 'isNonprinting', 'isMeta',
		'render_char', 'draw_rect', 'keystr',


			#|--------------------
			#| "Type" definitions.
		
		'Loc',			# A location struct in a screen/window.    [struct type]
		'Brightness',	# Type of brightness designators.	   [enumerated type]
		'ColorSpec',	# Constructor for color specifier structs.	  [function]
		'RenderStyle',	# Type of rendering style designators. [enumerated type]


			#|---------------------
			#| Global data members.		- NOTE: These aren't dynamically exported.
		
		'DIM', 'NORMAL', 'BRIGHT',		# Brightness designator values.
		
				# Color specifier values.
		'BLACK', 'GRAY', 'WHITE', 'BRIGHT_WHITE',
		'RED', 'GREEN', 'BLUE', 'CYAN', 'MAGENTA', 'YELLOW',
		'BRIGHT_RED', 'BRIGHT_GREEN', 'BRIGHT_BLUE',
		'BRIGHT_CYAN', 'BRIGHT_MAGENTA', 'BRIGHT_YELLOW',

				# Rendering style designators.
		'PLAIN', 'BORDER', 'CONTROL', 'WHITESP', 'METACTL', 'METAWSP'
		
	]


	#|==========================================================================
	#| 	2.	Imports.									   [module code section]
	#|
	#|		2.1.  Standard Python modules imported into this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from threading import RLock		# Reentrant locks for concurrency control.
from time import sleep
from os	import environ, path 	
	# Access environment variables, manipulate filesystem path strings.


		#-------------------------------------------------------------------
		# Locale setup. Here we obtain the system's default string encoding.

import locale
	# This sets the locale for all categories to the user's default setting, 
	# e.g., from the LANG environment variable, if that is specified.
locale.setlocale(locale.LC_ALL, '')
	# This gets the preferred encoding configured by the user preferences 
	# (the exact method for this is system-dependent).
global encoding	
encoding = locale.getpreferredencoding()
	# We'll use this wherever we need to encode/decode strings to bytes.


		#--------------------------------------------------------------
		# Import a bunch of stuff that we need from the curses package.

import curses
from curses import *
	# At some point we should change this to an explicit list of the
	# curses names that we actually use.
from curses.textpad import rectangle, Textbox
from curses.ascii import (controlnames, iscntrl, isspace, isgraph, DC4)


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	2.1.  Custom imports.						[module code subsection]
		#|
		#|		Here we import various local/application-specific 
		#|		modules that we need.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.decorators	import	singleton	# Class decorator.
from infrastructure.worklist	import	RPCWorker	# Display driver uses this.

			#|------------------------
			#| Logging-related stuff.

from infrastructure.logmaster import (
		sysName,			# Used just below.
		ThreadActor,		# TUI input thread uses this.
		getComponentLogger,	# Used just below.
		LoggedException,	# DisplayException inherits from this.
		FatalException		# We derive TerminateServer from this.
	)
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.
global _sw_component
_sw_component = sysName + '.' + _component


			#|----------------------------------------------------------------
			#| Import sibling modules we need from within the display package.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from .colors import *		# All color-related definitions.


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
		#|		Note that in the constructor call, the y coordinate is 
		#|		specified first, as is standard within curses.
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


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(display.)KeyEvent								[public simple type]
		#|
		#|		An instance of this class is a simple struct that
		#|		represents a "key event" received from curses.  The 
		#|		quotation marks here allude to the fact that some of 
		#|		these events may not correspond to actual keypresses; 
		#|		for example, window resize events.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class KeyEvent:
	"""Class of simple events received from the input terminal."""
	def __init__(thisKeyEvent, keycode=None):
		thisKeyEvent.keycode = keycode
		thisKeyEvent.keyname = keystr(keycode)

#__/ End simple type KeyEvent.


	#|==========================================================================
	#|	4.	Static data structures.					   	   [module code section]
	#|
	#|		In this section, we define various static data structures
	#|		(such as arrays, tables, and dictionaries) that we need.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	display._nonprint_7bit_glyphs	[private global data structures]
			#|	display._nonprint_8bit_glyphs
			#|
			#|		This is a lookup table that maps the code point for 
			#|		each non-printing 7-bit ASCII character (including 
			#|		whitespace characters and other control characters)
			#|		to an ordered pair of a (non-plain) render style and
			#|		a glyph, or printable (non-blank, non-control)
			#|		character.  This then gives us a way to render such
			#|		characters on the display in a uniquely identifiable
			#|		way, in case they happen to be generated by the AI
			#|		(or by one of our apps).
			#|
			#|		The 8-bit version of the table should be used when the
			#|		terminal's font supports the Western (LATIN-1) character
			#|		set (a subset of Unicode) for at least the range of 
			#|		code points 161-255.  If the terminal does not support 
			#|		these characters, then the 7-bit version should be used.
			#|
			#|		These tables could be dynamically modified, but 
			#|		support for doing that has not been implemented yet.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	#|------------------------------------------------------------------
	#| The idea of the below is that, on terminals with only 7-bit ASCII
	#| font support, we can render various (normally non-printable)
	#| ASCII control and whitespace characters as a single 7-bit
	#| character glyph using some alternate display attributes.

_nonprint_7bit_glyphs = {	# Returns pair of (render style, printable 7-bit character)

	  #CdPt:	(RNDSTYL, GLPH),
	  #-----	---------------
# NOTE: The first nine are control characters, which are rendered black-on-red.
		0:		(CONTROL, '_'),		# Null character.
		1:		(CONTROL, ':'),		# Start of heading.
		2:		(CONTROL, '['),		# Start of text.
		3:		(CONTROL, ']'),		# End of text.
		4:		(CONTROL, '.'),		# End of transmission.
		5:		(CONTROL, '?'),		# Enquiry.
		6:		(CONTROL, 'Y'),		# Acknowledgement.
		7:		(CONTROL, '*'),		# Bell.
		8:		(CONTROL, '<'),		# Backspace.
# Note the next few are whitespace characters (rendered gray-on-black).
		9:		(WHITESP, '>'),		# Horizontal tab.
		10:		(WHITESP, '/'),		# Line feed.
		11: 	(WHITESP, 'v'),		# Vertical tab.
		12:		(WHITESP, 'V'),		# Form feed.
		13:		(WHITESP, '<'),		# Carriage return.
# Now we go back to the rest of the non-whitespace control characters.
		14:		(CONTROL, '('),		# Shift-out.
		15:		(CONTROL, ')'),		# Shift-in.
		16:		(CONTROL, '/'),		# Data-link escape.
		17:		(CONTROL, 'o'),		# Device control 1.
		18:		(CONTROL, '@'),		# Device control 2.
		19:		(CONTROL, '='),		# Device control 3.
		20:		(CONTROL, '-'),		# Device control 4.
		21:		(CONTROL, 'N'), 	# Negative acknowledgement.
		22:		(CONTROL, '~'),		# Synchronous idle.
		23:		(CONTROL, ';'),		# Emd transmission block.
		24: 	(CONTROL, 'X'), 	# Cancel.
		25:		(CONTROL, '|'), 	# End of medium.
		26:		(CONTROL, '$'),		# Substitute.
		27: 	(CONTROL, '^'),		# Escape.
		28:		(CONTROL, 'F'),		# File separator.
		29: 	(CONTROL, 'G'),		# Group separator.
		30: 	(CONTROL, '&'),		# Record separator.
		31: 	(CONTROL, ','), 	# Unit separator.
# These last couple are outside the range 0-31 of the normal control characters.
		32: 	(WHITESP, '_'),		# Space.
		127:	(CONTROL, '#'), 	# Rubout/delete.
	}


	#|------------------------------------------------------------------
	#| The idea of the below is that, on terminals without full Unicode
	#| font support, but with support for extended 8-bit (LATIN-1) ASCII, 
	#| we can render various (normally non-printable) ASCII control and 
	#| whitespace characters as a single 8-bit character glyph using 
	#| some alternate display attributes.

_nonprint_8bit_glyphs = {	# Returns pair of (render style, printable character)

	  #CdPt:	(RNDSTYL, GLPH),
	  #-----	---------------
# NOTE: The first nine are control characters, which are rendered black-on-red.
		0:		(CONTROL, '_'),		# Null character.
		1:		(CONTROL, '$'),		# Start of heading.
		2:		(CONTROL, '«'),		# Start of text.
		3:		(CONTROL, '»'),		# End of text.
		4:		(CONTROL, '.'),		# End of transmission.
		5:		(CONTROL, '?'),		# Enquiry.
		6:		(CONTROL, '!'),		# Acknowledgement.
		7:		(CONTROL, '¢'),		# Bell.
		8:		(CONTROL, '<'),		# Backspace.
# Note the next few are whitespace characters (rendered gray-on-black).
		9:		(WHITESP, '>'),		# Horizontal tab.
		10:		(WHITESP, '/'),		# Line feed.
		11: 	(WHITESP, 'v'),		# Vertical tab.
		12:		(WHITESP, '§'),		# Form feed.
		13:		(WHITESP, '®'),		# Carriage return.
# Now we go back to the rest of the non-whitespace control characters.
		14:		(CONTROL, '('),		# Shift-out.
		15:		(CONTROL, ')'),		# Shift-in.
		16:		(CONTROL, '±'),		# Data-link escape.
		17:		(CONTROL, '°'),		# Device control 1.
		18:		(CONTROL, '©'),		# Device control 2.
		19:		(CONTROL, '='),		# Device control 3.
		20:		(CONTROL, '-'),		# Device control 4.
		21:		(CONTROL, '¬'), 	# Negative acknowledgement.
		22:		(CONTROL, '~'),		# Synchronous idle.
		23:		(CONTROL, ';'),		# Emd transmission block.
		24: 	(CONTROL, '×'), 	# Cancel.
		25:		(CONTROL, '|'), 	# End of medium.
		26:		(CONTROL, '¿'),		# Substitute.
		27: 	(CONTROL, '^'),		# Escape.
		28:		(CONTROL, '¦'),		# File separator.
		29: 	(CONTROL, '÷'),		# Group separator.
		30: 	(CONTROL, '¶'),		# Record separator.
		31: 	(CONTROL, '·'), 	# Unit separator.
# These last couple are outside the range 0-31 of the normal control characters.
		32: 	(WHITESP, '_'),		# Space. (Gray on black.)
		127:	(CONTROL, '#'), 	# Rubout/delete. (Black on red.)
}

# (For terminals with full Unicode capability, we could choose from an even
# broader range of glyphs, but we haven't bothered with that here yet.)


	#|==========================================================================
	#|	4.	Function definitions.						   [module code section]
	#|
	#|		In this section we define the various functions provided by 
	#|		this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.isNonprinting()							   [public function]
		#|
		#|		Given a character code point, returns True if this is a
		#|		(normally) non-printing character in the range 0-255.
		#|
		#|		Note that by "non-printing" characters, we include the
		#|		various whitespace characters, as well as control codes.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def isNonprinting(code):

	"""Returns true if the given code point is a 7- or 8-bit whitespace
		or control character, which normally would not be visible."""

	# 7-bit ASCII x00-1F controls and space.
	if code >=0 and code <= 32:
		return True

	if code == 127:		# Delete charater.
		return True

	# Controls/whitespace in 8-bit ASCII/Unicode
	if code >= 128 and code <= 160:
		return True

	# For everything else, assume it's printing.
	return False

#__/ End function display.isNonprinting().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.isMeta()								   [public function]
		#|
		#|		Given a character code point, returns True if this is an
		#|		8-bit code point that does not also fit in 7 bits.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def isMeta(code):
	"""Retruns True if <code> is an 8-bit code point
		with its high-order bit set (0x80-0xFF)."""
	if code >= 128 and code <= 255:
		return True

#__/ End function display.isMeta().
	

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.render_char()							   [public function]
		#|
		#|		Given a window and a single character code point, render
		#|		this character at the current location in the window, even
		#|		if it is a normally-nonprintable 7- or 8-bit control or
		#|		whitespace character.  Note this uses the mechanisms above.
		#|
		#|		If the optional argument baseAttrs is supplied, then it is
		#|		combined with the attributes needed to render the character.
		#|		This is probably only useful for baseAttrs=A_UNDERLINE.
		#|
		#|		Note that code points greater than 383 may not be supported
		#|		by the terminal font, and thus may not be displayable even
		#|		using this function.  For reference, below is a table of 
		#|		characters from 160-383 that are commonly available in
		#|		Western scripts supported on most terminals. (Please note
		#|		that the characters after the break don't fit in 8 bits.)
		#|
		#|
		#|							Low-order Hexadecimal Digit
		#|
		#|					0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
		#|					==============================================
		#|			 A: 	   ¡  ¢  £  ¤  ¥  ¦  §  ¨  ©  ª  «  ¬  ­  ®  ¯ 
		#|			 B:		°  ±  ²  ³  ´  µ  ¶  ·  ¸  ¹  º  »  ¼  ½  ¾  ¿ 
		#|			 C:		À  Á  Â  Ã  Ä  Å  Æ  Ç  È  É  Ê  Ë  Ì  Í  Î  Ï 
		#|			 D:		Ð  Ñ  Ò  Ó  Ô  Õ  Ö  ×  Ø  Ù  Ú  Û  Ü  Ý  Þ  ß 
		#|			 E:		à  á  â  ã  ä  å  æ  ç  è  é  ê  ë  ì  í  î  ï 		^
		#|			 F:		ð  ñ  ò  ó  ô  õ  ö  ÷  ø  ù  ú  û  ü  ý  þ  ÿ		| 8-bit
		#|					----------------------------------------------		+------
		#|			10:		Ā  ā  Ă  ă  Ą  ą  Ć  ć  Ĉ  ĉ  Ċ  ċ  Č  č  Ď  ď 		| 9-bit
		#|			11:		Đ  đ  Ē  ē  Ĕ  ĕ  Ė  ė  Ę  ę  Ě  ě  Ĝ  ĝ  Ğ  ğ 		V
		#|			12:		Ġ  ġ  Ģ  ģ  Ĥ  ĥ  Ħ  ħ  Ĩ  ĩ  Ī  ī  Ĭ  ĭ  Į  į 
		#|			13:		İ  ı  Ĳ  ĳ  Ĵ  ĵ  Ķ  ķ  ĸ  Ĺ  ĺ  Ļ  ļ  Ľ  ľ  Ŀ 
		#|			14:		ŀ  Ł  ł  Ń  ń  Ņ  ņ  Ň  ň  ŉ  Ŋ  ŋ  Ō  ō  Ŏ  ŏ 
		#|			15:		Ő  ő  Œ  œ  Ŕ  ŕ  Ŗ  ŗ  Ř  ř  Ś  ś  Ŝ  ŝ  Ş  ş 
		#|			16:		Š  š  Ţ  ţ  Ť  ť  Ŧ  ŧ  Ũ  ũ  Ū  ū  Ŭ  ŭ  Ů  ů 
		#|			17:		Ű  ű  Ų  ų  Ŵ  ŵ  Ŷ  ŷ  Ÿ  Ź  ź  Ż  ż  Ž  ž  ſ 	
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|----------------------------------------------------------------------
	#| The following renders even nonprintable control/whiteplace characters
	#| using substitute glyphs with alternate attributes.

def render_char(win, code, baseAttrs=0):
		# win is screen or window.
		# code is the ordinal character code point.

	"""Renders the given code point at the current location in the given
		window, even if it's a normally-nonprintable control or whitespace
		character."""
		
		#|--------------------------------------------------------------
		#|	First, if the given character code isn't one of the 7/8-bit 
		#|	non-printing characters that we now how to handle specially,
		#|	then just render it in the normal way.
		
	if not isNonprinting(code):		# This means, we don't know anything special to do with it.
		if code >= 0 and code <= 0x10ffff:		# Make sure it's in the Unicode range.
			win.addstr(chr(code), baseAttrs)	# Alright now just add the bastard.
		else:
			_logger.warn("render_char(): Was given an invalid code point {code}. Ignoring.")
		return

		#|---------------------------------------------------------------------
		#|	OK, if we get here, then it's a non-printing character in the range 
		#|	that we know how to handle; so, figure out what rendering style and 
		#|	glyph to use to render it.
	
		# Special handling for rendering 8-bit non-printing characters.

	meta = isMeta(code)
	if meta:
			# Use the same glyph for meta specials as for normal ones.
		code = code - 128

		# Render this non-printing character code as a styled glyph.
	(style, glyph) = _nonprint_8bit_glyphs[code]	# Uses Western/LATIN-1.
	#(style, glyph) = _nonprint_7bit_glyphs[code]	# Less pretty code

		# If meta, map the render styles to their meta equivalents.
	if meta:
		if style is CONTROL:
			style = METACTL
		elif style is WHITESP:
			style = METAWSP
	
		# Convert the style to a display attribute setting.
	attr = style_to_attr(style) | baseAttrs
	
		# Now display the glyph, using those attributes.
	win.addstr(glyph, attr)
	
#__/ End function display.render_char().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.draw_rect()								   [public function]
		#|
		#|		Draws a rectangular box on the given window using the
		#|		specified attribute settings.
		#|
		#|		NOTE: Needs a bug-fix to work on the right or bottom
		#|		edge of the display (turn on leaveok temporarily).
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

#__/ End function display.draw_rect().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.keystr()								   [public function]
		#|
		#|		Given a numeric keycode, returns a string representation
		#|		of the key.  This may be an escape sequence or a key name.
		#|
		#|		The special KEY_RESIZE 'key code' (which is really a signal 
		#|		that the terminal window has been resized by the user) is 
		#|		mapped to the string "Resize".  The error code ERR (= -1)
		#|		is mapped to the string "<ERROR>".
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def keystr(k):

	"""Returns a string representation of the given numeric keycode."""
	
	if k == KEY_RESIZE:
		return "Resize"
	elif k == ERR:
		return "<ERROR>"
	elif k == None:
		return "(None)"
	else:
		try:
			return keyname(k).decode(encoding)
		except ValueError as e:
			_logger.error(f"keystr(): {str(e)}: Received unknown key code {k}.")

#__/ End function display.keystr().


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

#__/ End function display.addLineClipped().


def addTextClipped(win, text:str, attrs:int, padRight:int=None):
	"""Adds the given text to the window, clipping each line
		to fit within the window width."""
		
	lines = text.split('\n')

	#_logger.debug("addTextClipped(): About to add line:\n" + lines[0])

	addLineClipped(win, lines[0], attrs, padRight=padRight)

	for line in lines[1:]:

		win.addstr("\n", attrs)

		#_logger.debug("addTextClipped(): About to add line:\n" + line)

		addLineClipped(win, line, attrs, padRight=padRight)
		

	#|==========================================================================
	#|
	#|	5.	Class definitions.						   	   [module code section]
	#|
	#|		In this section we define the various classes provided by 
	#|		this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


# Forward declarations for type hints.
class TheDisplay: pass


global _theDisplayDriver	# The display driver thread.
_theDisplayDriver = None	# Thread not yet created.


		# Class to implement a thread that exists for the purpose
		# of serializing curses operations. Whenever you want to 
		# do something with the display, you can do it as follows:
		#
		#	displayDriver = DisplayDriver()
		#	displayDriver(callable)

class DisplayDriver(RPCWorker):
	#______________/         \_____________________________________________
	#| NOTE: By subclassing this class from RPCWorker instead of Worker, 
	#| the overall effect is simply to serialize all of the normal display 
	#| operations by having them wait for this single thread to do them.  
	#| However, users can also delegate operations to the driver to do as
	#| background activities without waiting for completion by calling the 
	#| driver's .do() method.
	#|---------------------------------------------------------------------
	
	@staticmethod
	def withLock(callable):
		"""This is a wrapper function that is to be applied around all bare
			callables that are handed to the display driver as tasks to be
			executed. It simply grabs the display lock, so that we avoid 
			conflicting with any other threads that may be using the 
			display.  (We assume curses operations are not thread-safe.)"""
		#_logger.debug("About to grab display lock...")
		with TheDisplay().lock:
			#_logger.debug("About to call wrapped callable...")
			return callable()				# Call the callable, return any result.
			#_logger.debug("Returned from wrapped callable...")
		#_logger.debug("Released display lock.")
	
	defaultWrapper = withLock
	
	def __init__(newDisplayDriver):
		
		"""Initialize the display driver by setting up its role & component 
			attributes appropriately for thread-specific logging purposes."""
			
		super(DisplayDriver, newDisplayDriver).__init__(
			role = 'DisplDrvr', component = _sw_component, daemon=True)
			# daemon=True tells Python not to let this thread keep the process alive
		
		# Stash this new display driver instance in a module-level global.
		global _theDisplayDriver
		_theDisplayDriver = newDisplayDriver

#__/ End class DisplayDriver.

def in_driver_thread():
	return current_thread() == _theDisplayDriver


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.DisplayClient					   [public extensible class]
		#|
		#|		This class, which can and should be further subclassed 
		#|		by other modules that are using this module, defines the 
		#|		detailed behavior of the primary client process that is 
		#|		using the display.
		#|
		#|		Key methods that subclasses should override include
		#|		the following:
		#|
		#|
		#|			.paint() -
		#|
		#|				This method should repaint the entire display 
		#|				with (client-specific) content.
		#|
		#|
		#|			.handle_event()	-
		#|
		#|				This method is called by the display for each
		#|				input event that occurs.
		#|
		#|		
		#|		If this class is instantiated directly, the resulting
		#|		client just provides some simple demo functionality, 
		#|		displaying information about the window size, input
		#|		events, and a simple character table.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class DisplayClient:

	"""A display client is an entity that uses the display as a server
		to interact with the user.	Only one client may use the display
		at a time."""

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	newClient.__init__()						  [instance initializer]
		#|
		#|		Currently, this initializer for new client instances 
		#|		simply links up the client with the display (i.e., the 
		#|		singleton instance of TheDisplay class).
		#|
		#|		Subclasses that need override this method to do application-
		#|		specific initialization should extend this method, by first 
		#|		calling their superclass initializer using the standard idiom,
		#|
		#|			super(SubClassName, this).__init__(this, *args, **kwargs),
		#|
		#|		before doing their application-specific initialization work.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def __init__(thisClient):
		"""Initializes the client by linking it with the display."""
			# Connect us up with the display.
		thisClient._display = display = TheDisplay()
		display.setClient(thisClient)
	#__/ End instance initializer for class DisplayClient.


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.display					  	  	   [public property]
		#|
		#|		This retrieves the display that the client is connected
		#|		to (which should be the singleton instance of TheDisplay).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	@property
	def display(thisClient):
		return thisClient._display


	@property
	def screen(thisClient):
		return thisClient.display.screen

	def requestRefresh(thisClient):

		"""This method tells the client to request the display to 
			refresh the client's screen on the next display update."""

			# Do a delayed (i.e., no-output) internal refresh of the entire screen.
		thisClient.screen.noutrefresh()
			# The actual (physical) external refresh of the display terminal will
			# occur on the next call to display.update().


	def start(thisClient, waitForExit:bool=False):
		
		"""This starts up this display client, which implicitly also starts
			up the underlying curses-based display infrastructure."""
			
		_logger.debug(f"displayClient.start(): Starting with waitForExit={waitForExit}...")

		client  = thisClient
		display = client.display
		
		display.start(waitForExit = waitForExit)

		_logger.debug("displayClient.start(): Returning.")
		
	#__/ End instance method displayClient.start().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.run()						  	[public instance method]
		#|
		#|		This is the method that should be called to start the 
		#|		display client running.  It automatically starts up the
		#|		entire display facility as well, paints the screen, and 
		#|		starts up the main event loop.  It does not return until 
		#|		there is an application abort or quit, so, users should
		#|		probably create a new thread to run it in.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def run(thisClient):
		display = thisClient.display
		display.run()


	@property
	def dispRunning(thisPanelClient):
		"""Returns Boolean 'True' if this client's display is currently running."""
		return thisPanelClient.display.isRunning
	

	def redisplay(thisClient):
		"""Tells the client's display it needs to update itself. This works 
			through calling the display's .paint() method, which then dispatches
			the detailed work back to the client."""
		display = thisClient.display
		display.paint()

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.addChar()					  	[public instance method]
		#|
		#|		This method can be used to send a character to the 
		#|		client's display, with special rendering features 
		#|		available for (normally) non-printing characters.
		#|
		#|		TO DO: Implement processing of optional loc and 
		#|		attr arguments (not yet supported).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def addChar(thisClient, char:int, *args, **argv):
		display = thisClient.display
		display.renderChar(char, *args, **argv)


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.addText()					  	[public instance method]
		#|
		#|		This method can be used to send plain text to the 
		#|		client's display.  By "plain text," we mean that 
		#|		non-printing characters are not handled specially.
		#|
		#|		TO DO: Add an option to enable special handling of
		#|		non-printing characters.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def addText(thisClient, text:str, *args, **argv):
		display = thisClient._display
		display.add_str(text, *args, **argv)


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.drawOuterBorder()			  	[public instance method]
		#|
		#|		This method draws a border just inside the edge of the
		#|		display screen, using the predefined BORDER render style.
		#|
		#|		Presently, this renders by default in a bright cyan text
		#|		color on a black background.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def drawOuterBorder(thisClient):
		"""Draw a border just inside the edge of the display screen."""

		client = thisClient
		display = client.display
		display.drawOuterBorder()	# Let the display do the work.

	#__/ End method displayClient.drawOuterBorder().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.paint()			[placeholder public instance method]
		#|
		#|		This is the main method that subclasses should override
		#|		to draw their display contents.
		#|
		#|		The version defined here essentially implements a simple
		#|		demo, which displays a border and some diagnostics of the
		#|		window size, the last event received, and a character table.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def paint(thisClient):
		"""Subclasses should override/extend this method to paint the display."""

			# Get some important guys.
		client = thisClient
		display = client.display
		screen = display.screen
		
			# First, if the display isn't even running, then there's nothing
			# to do, so just exit early.
		if not display.running:
			_logger.debug("client.paint(): Display is not yet running; returning early.")
			return

		_logger.debug("client.paint(): Painting client display...")
		
			# This is effectively a "lazy clear"--it waits until refresh to take effect.
		display.erase()		# Marks all character cells as empty (and no attributes).
				# (We do this so we don't have to worry about old text hanging around.)

			# Draw a border just inside the edges of the screen.
		display.drawOuterBorder()
		
			# Display information about the screen size.
		(height, width) = display.get_size()
		client.addText(f"Screen size is {height} rows high x {width} columns wide.", Loc(1,2))

			# If we've received any events yet, display the last one received.
		if hasattr(thisClient, '_lastEvent'):
			thisClient.displayEvent()

		#|----------------------------------------------------------------
		#| Next, draw a character table.  (Code points 0x0 through 0x17F.)

			# Iterate through all character codes in our displayable range.
		for ch in range(0, 384):	# This will fill 12 rows.
		
				# Calculate coordinates for this character.
			y = 7 + int(ch/32)
			x = 2 + 2*int(ch%32)
		
				# Render the character at the given location.
			screen.move(y, x)
			client.addChar(ch)	# TODO: Add an optional loc argument.
			
		#__/ End loop over code points.

		#/----------------------------------------------------------------------
		#| 	TheDisplay handles refresh for us automatically, so we don't need 
		#|	to do it here. So, we're done!
		#\----------------------------------------------------------------------
	
	#__/ End method displayClient.paint().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.displayEvent()				[public instance method]
		#|
		#|		This is just here to support the demo application; it 
		#|		displays some information about the last event received.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def displayEvent(thisClient):

		client 		= thisClient
		display		= client.display
		keyevent	= client._lastEvent
		keycode		= keyevent.keycode
		keyname		= keyevent.keyname

			# Default behavior: Display information about key code received.
		client.addText(f"Received key code: #{keycode}.", Loc(3,2))
		client.addText(f"Direct rendering is: ", Loc(4,2))
		client.addChar(keycode)		# What if we interpret keycode directly as a character?
		client.addText(f"Key name string is: ({keyname})", Loc(5,2))

	#__/ End method displayClient.displayEvent().


	def handle_resize(thisClient):
		"""When we have already figured out the new screen size, this method
			is called by the display to let us do client-specific adjustments."""
		# There is nothing to do here by default, but subclasses should override this.
		pass

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.handle_event()	[placeholder public instance method]
		#|
		#|		This is the main event handler method.
		#|
		#|		Subclasses may want to override this method as appropriate
		#|		for their application.  The display (singleton instance of 
		#|		TheDisplay) will call this method whenever a new event is 
		#|		received.  The implementation of this method should then
		#|		dispatch the event to sub-handlers as appropriate.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
	def handle_event(thisClient, keyevent):
		"""Subclasses should override this method with their own event handler."""

			# Get some important guys.
		client = thisClient
		keycode = keyevent.keycode		# Numeric code for key or other event.
		keyname = keyevent.keyname		# String name for key or event.
		_logger.debug(f"Got a key with code={keycode}, name={keyname}.")
		
			# This next line is here to support our demo application, and may 
			# not be needed in all subclasses' replacements for this method.
		client._lastEvent = keyevent

			# The following code block or similar will be in most applications.
		if keycode == KEY_RESIZE:
			client._display.resize()

		# The following is commented out because generally there's no need to
		# repaint the entire display just because a key was pressed.

		#else:
		#	client.paint()

	#__/ End method displayClient.handle_event().

#__/ End class displayClient.


class TUI_Input_Thread(ThreadActor):
	"""This thread exists for the sole purpose of executing the main
		user input loop for the curses-based 'TUI' (Text User Interface).
		It communicates with the display driver thread to carry out I/O.
		"""
		
	defaultRole			= 'TUI_Input'
	defaultComponent	= _sw_component 
	
	def __init__(newTuiInputThread, *args, **kwargs):
		thread = newTuiInputThread
		thread.exitRequested = False		# Set this to True if you want this thread to quit.
		super(TUI_Input_Thread, thread).__init__(*args, **kwargs)	# ThreadActor initialization.

#__/ End class TUI_Input_Thread.


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

			# Mark this display as not running yet, to make sure we don't try 
			# to do anything with it until it's actually running.
		theDisplay._running = False		# Display is not up and running yet.

		theDisplay._client = None		# Client is not yet attached.

		theDisplay._screen = None		
			# The actual display screen structure hasn't been created yet.
		theDisplay._width  = None	# No width/height yet, because no screen
		theDisplay._height = None

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
			
		theDisplay._lock = RLock()		# Reentrant lock for concurrency control.

			#|------------------------------------------------------------------
			#|	As a secondary tool to facilitate multithreaded curses apps,
			#|	we create this "display driver" thread, which is an RPCWorker
			#|	(from the worklist module).  It can carry out display tasks 
			#|	either synchronously ("driver(...)" syntax) or asynchronously
			#|	("driver.do(...)" syntax).

		theDisplay._driver = DisplayDriver()		# Creates display driver thread.
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
			display, and bringing it down again when done.	It needs to be run 
			in its own thread, so that other systems can asynchonously communicate
			with it if needed.  Clients call it automatically from their .run() 
			method."""

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


	def drawCenter(theDisplay:TheDisplay=None, text:str="", row:int=None, lrpad:str=None, style:RenderStyle=None, extraAttr:int=0):
		"""Draws the given text string centered on the given line with the given padding and attributes."""
		
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
			fgcolor = (pair_index - 1) % 8	# The -1 (+7) here is needed because pair 0 has fg=white standardly.
			
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
			
			try:
			
				ch = screen.getch()		# Gets a 'character' (keycode) ch.
					# Note earlier, we configured .getch() to be nonblocking.

			except KeyboardInterrupt as e:				# User hit CTRL-C?
				# Note that currently, we should not get these events anyway, since
				# earlier, we put the terminal in raw() mode.

				_logger.debug("display._do1iteration(): Caught a keyboard interrupt during screen.getch().")

				event = KeyEvent(keycode = KEY_BREAK)	# Translate to BREAK key.
				
			except Exception as e:

				_logger.fatal(f"display._do1iteration(): Unknown exception during screen.getch(): {str(e)}.")
				raise e
				
			else:

					# Note we suppress debug output if the keycode is ERR (= none yet) to
					# prevent excessive logging.

				if ch != ERR:
					_logger.debug(f"display._do1iteration(): Got character code {ch}.")

					# Here, we package up the keycode into a KeyEvent object.

				event = KeyEvent(keycode = ch)		# Just pass the raw keycode.

			#__/ End try/except clause for keyboard input (.getch()) call.
			
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