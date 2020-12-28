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
	SW COMPONENT:	GLaDOS.server.display (Display screen management)


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
		the human user is using is more or less compatible with xterm.  The
		Putty terminal used on Windows systems falls into this category.  A
		future version of this module may generalize it to a broader range of
		terminals.
		
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
		
		'', 
		'',
		

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

from enum import Enum			# Support for enumerated types.
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
from curses.textpad import rectangle, Textbox
from curses.ascii import controlnames, iscntrl, isspace, isgraph


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	2.1.  Custom imports.						[module code subsection]
		#|
		#|		Here we import various local/application-specific 
		#|		modules that we need.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.decorators import singleton		# Class decorator.

			#------------------------
			# Logging-related stuff.

from infrastructure.logmaster import getComponentLogger # Used just below.
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.


	#|==========================================================================
	#|	3.	Type definitions.							   [module code section]
	#|
	#|		In this section, we define various "types" that we provide.
	#|		Essentially, for us, a "type" just means a simple class, or
	#|		any way of using a structured object as a simple data type.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.Loc										[public struct type]
		#|
		#|		This class essentially implements a simple 2-element 
		#|		struct type with named public data members 'x' and 'y' 
		#|		that represent a pair of character coordinates within 
		#|		a screen or window.
		#|
		#|		Note that in the constructor call, the y coordinate is 
		#|		specified first, as is standard within curses.
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
		#|	display.KeyEvent								[public simple type]
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


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| 	Below we define a type and some global constants for designating 
		#|	brightness values.  In addition to 'bright' and 'normal' brightness 
		#|	levels we also have 'dim' which is used when referring to gray or 
		#|	'dim white', which is really implemented as 'bright black' behind 
		#|	the scenes.  These values are used in forming "color specifiers," 
		#|	defined further below.

class Brightness(Enum):
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	"""
		Brightness										[public enumerated type]
	
			This class provides an enumerated type for color display 
			brightness designators.  We're assuming that the display 
			(like xterm/Putty) supports 'normal' and 'bright' 
			brightness values.  We only assume that the 'dim' value
			is supported in the case of white; internally, this is 
			implemented as "bright black."
	"""
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	DIM='dim'		 # Supported only for white (implemented as bright black).
	NORMAL='normal'
	BRIGHT='bright'	 # Bright colors are generated by the A_BOLD attribute.

#__/ End enum Brightness.

	#--------------------------------------------
	# Define shorter names for brightness values.
global DIM, NORMAL, BRIGHT
DIM    = Brightness.DIM	   # Used only for 'dim white' (a.k.a. 'bright black').
NORMAL = Brightness.NORMAL
BRIGHT = Brightness.BRIGHT


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| A "color specifier" is a pseudo-type that actually just consists of 
		#| an ordered pair; the first element of the pair is a "base color," 
		#| which means a curses-defined color, while the second element of the 
		#| pair is a brightness designator, defined above.  The following
		#| function constitutes a specialized constructor for color specifiers,
		#| which automatically translates "dim white" to "bright black", so as 
		#| to make our code for constructing that specific color more readable.

def ColorSpec(baseColor, intensity):
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	"""
		ColorSpec									 [public pseudo-constructor]
	
			This function generates an ordered pair representing a color 
			specification, consisting of a base color together with a 
			brightness value.  This constructor does some special work
			that is needed to support the "dim white" color spec.
	"""
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# Simply replace "dim white" with "bright black."
	if (baseColor is COLOR_WHITE) and (intensity is DIM):
		baseColor = COLOR_BLACK
		brightness = BRIGHT
	#__/
		
		# Return the resulting color/brightness pair we just constructed.
	return (baseColor, intensity)

#__/ ColorSpec


#-------------------------------------------------------------
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


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	Predefined rendering styles. Each of these designators selects a 
		#|	particular combination of display attributes. So far we have the 
		#|	following underlying attributes available to choose from: 
		#|	Foreground/background colors, brightness values, and underlining. 
		#|	Italics may also be available in some terminal environments, but 
		#|	are not yet used here.

# Enumerated type of predefined render styles.
class RenderStyle(Enum):
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	"""
		RenderStyle										[public enumerated type]
	
			This enum provides designators for some pre-defined rendering
			styles, each of which translates into a foreground/background 
			pair of color specifiers, using the private '_style_colors[]'
			lookup table defined in this module.
	"""
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# Use this style for displaying normal printable text.
	PLAIN='plain'

		# Use this style for drawing window borders and separators.
	BORDER='border'

		# Use this style for rendering 7-bit ASCII control characters.
	CONTROL='control'

		# Use this style for rendering ordinary whitespace characters
	WHITESPACE='whitespace'

		# Use this style for rendering control characters with 8th bit set.
	META_CONTROL='meta-control'

		# Use this style for rendering whitespace characters with 8th bit set.
	META_WHITESPACE='meta-whitespace'

#__/ End enum RenderStyle.

# Put the render styles in shorter globals.
global PLAIN, BORDER, CONTROL, WHITESP, METACTL, METAWSP

PLAIN		=	RenderStyle.PLAIN
BORDER		=	RenderStyle.BORDER
CONTROL		=	RenderStyle.CONTROL
WHITESP		=	RenderStyle.WHITESPACE
METACTL		=	RenderStyle.META_CONTROL
METAWSP		=	RenderStyle.META_WHITESPACE


	#|==========================================================================
	#|	4.	Static data structures.					   	   [module code section]
	#|
	#|		In this section, we define various static data structures
	#|		(such as arrays, tables, and dictionaries) that we need.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	display._style_colors			 [private global data structure]
			#|
			#|		This private lookup table maps each display style 
			#|		designator to the corresponding foreground/background
			#|		pair of color specifiers that is used for rendering
			#|		characters in that display style in the render_char()
			#|		function, below.
			#|
			#|		This could be dynamically modified, but support for 
			#|		doing that has not been implemented yet.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global _style_colors
_style_colors = {		# Maps render style to (fgcolorspec, bgcolorspec) pairs.

	#STYLE:		(FOREG,		  	BACKG ),
	#-------	-------------	--------
	PLAIN:		(WHITE,		  	BLACK ),	# Normal characters: White text on black background.
	BORDER:		(BRIGHT_CYAN, 	BLACK ),	# Border characters: Bright cyan text on a black background.
	CONTROL:	(BLACK,		  	RED	  ),	# Control characters: Black text on red background.
	WHITESP:	(GRAY,		  	BLACK ),	# Whitespace characters: Faded (gray) text on black background.
	METACTL:	(BLACK,		  	BLUE  ),	# Meta-control characters: Black text on blue background.
	METAWSP:	(BLUE,		  	BLACK ),	# Meta-whitespace characters: Blue text on black background.

}


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
		#|	display.colors_attr()							   [public function]
		#|
		#|		Turns a pair of color specs into a correspending setting
		#|		of display attributes (which is a non-negative integer 
		#|		encoding a bit string).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def colors_attr(fgColorSpec, bgColorSpec):

	"""This function returns the curses display attribute setting that 
		corresponds to a given fg/bg pair of color specs."""

		#----------------------------------------------------------------------
		# First, break down the two color specs and extract the base foreground 
		# and background colors, and the intensity (brightness) values.
		
	(fgBase, fgIntensity) = fgColorSpec
	(bgBase, bgIntensity) = bgColorSpec

		#|---------------------------------------------------------------------
		#| Turn the foreground-background base colors into a color-pair index.
		#| In order for this to work, note that we must have previously set up 
		#| the color pairs accordingly; this in done automatically in the meth-
		#| od theDisplay._initColorPairs() when the display driver starts up.
		
	colorPairIndex = bgBase*8 + (fgBase+1)%8	
		# The +1 here is needed in order to map a foreground color of white (7) 
		# to 0, for compatibility with the built-in color pair index 0, which 
		# is predefined to always mean white-on-black.  Note that there's a 
		# corresponding -1 in the reverse mapping in _initColorPairs().

		#|-------------------------------------------------------------------
		#| Calculate the attribute setting to apply the color and brightness.
		
	# We start with the base attribute setting for the specific color pair.
	attrVal = color_pair(colorPairIndex)
	
	# To make the foreground color bright, we also apply the 'bold' attribute.
	if fgIntensity is BRIGHT:
		attrVal = attrVal | A_BOLD	
			# Note the 'bold' attribute on xterm/Putty really just makes 
			# foreground brighter, which is what we want to do here.
	
	# To make the background color bright, we also apply the 'blink' attribute.
	if bgIntensity is BRIGHT:
		attrVal = attrVal | A_BLINK	
			# Note the 'blink' attribute on xterm/Putty really just makes the 
			# background brighter, which is what we want to do here.

	return attrVal	# Returns the attribute setting we just computed.

#__/ End function display.colors_attr().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.style_to_attr()							   [public function]
		#|
		#|		This function maps a render style designator to the 
		#|		correspending display attribute setting (bit-vector).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def style_to_attr(style):
	"""This function maps a render style designator to the 
		correspending display attribute setting (bit-vector)."""

	(fgSpec, bgSpec) = _style_colors[style]
	return colors_attr(fgSpec, bgSpec)

#__/ End function display.style_to_attr().


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
		#|			 E:		à  á  â  ã  ä  å  æ  ç  è  é  ê  ë  ì  í  î  ï 
		#|			 F:		ð  ñ  ò  ó  ô  õ  ö  ÷  ø  ù  ú  û  ü  ý  þ  ÿ
		#|			
		#|			10:		Ā  ā  Ă  ă  Ą  ą  Ć  ć  Ĉ  ĉ  Ċ  ċ  Č  č  Ď  ď 
		#|			11:		Đ  đ  Ē  ē  Ĕ  ĕ  Ė  ė  Ę  ę  Ě  ě  Ĝ  ĝ  Ğ  ğ 
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
	if isMeta(code):	
			# Use the same glyph for meta specials as for normal ones.
		code = code - 128
			# However, map the render styles to their meta equivalents.
		if style is CONTROL:
			style = METACTL
		elif style is WHITESP:
			style = METAWSP
	
		# Render this non-printing character code as a styled glyph.
	(style, glyph) = _nonprint_8bit_glyphs[code]	# Uses Western/LATIN-1.
	#(style, glyph) = _nonprint_7bit_glyphs[code]	# Less pretty code

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
	else:
		try:
			return keyname(k).decode(encoding)
		except ValueError as e:
			_logger.error(f"keystr(): {str(e)}: Received unknown key code {k}.")

#__/ End function display.keystr().


	#|==========================================================================
	#|
	#|	5.	Class definitions.						   	   [module code section]
	#|
	#|		In this section we define the various functions provided by 
	#|		this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.DisplayClient					   [public extensible class]
		#|
		#|		This class, which can and should be further subclassed 
		#|		by using modules, defines the detailed behavior of the 
		#|		primary client process that is using the display.
		#|
		#|		Key methods that subclasses should override include
		#|		the following:
		#|
		#|
		#|			.paint() -
		#|
		#|				This should repaint the entire display with 
		#|				client-specific content.
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

		"""Draw a border just inside the edge of the display screen."""

		attr = style_to_attr(BORDER)
		
		client = thisClient
		display = client._display
		screen = display.screen
		
		screen.attrset(attr)
		screen.border('|', '|', '-', '-', '/', '\\', '\\', '/')
		screen.attrset(0)


	def paint(thisClient):
		"""Subclasses should override/extend this method to paint the display."""

		client = thisClient
		display = client._display
		screen = display.screen
		
		display.erase()
		thisClient.drawOuterBorder()
		
		if hasattr(thisClient, '_lastEvent'):
			thisClient.displayEvent()

			# Iterate through all character codes in our displayable range.
		for ch in range(0, 384):
		
				# Calculate coordinates for this character.
			y = 7 + int(ch/32)
			x = 2 + 2*int(ch%32)
		
				# Render the character at the given location.
			screen.move(y, x)
			client.addChar(ch)

		display.refresh()
		

	def displayEvent(thisClient):

		keyevent = thisClient._lastEvent

		client = thisClient
		keycode = keyevent.keycode
		keyname = keyevent.keyname

		(height, width) = client._display.get_size()

			# Default behavior: Display information about key code received.
		client.addText(f"Screen size is {height} rows high x {width} columns wide.", Loc(1,2))
		client.addText(f"Received key code: #{keycode}.", Loc(3,2))
		client.addText(f"Direct rendering is: ", Loc(4,2))
		client.addChar(keycode)		# What if we interpret keycode directly as a character?
		client.addText(f"Key name string is: ({keyname})", Loc(5,2))


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


	def resize(theDisplay):
		"""Call this method when you want to handle a resize event."""

			# Now we potentially need to resize the window structures
			# within curses, if the terminal size has actually changed.
		theDisplay._check_size()
		(height, width) = theDisplay.get_size()

			# This has the effect of updating curses' idea of the terminal
			# size in curses.{LINES,COLS}; note that this *only* works right
			# if the environment variables LINES, COLUMNS are not set!  If 
			# you ever call update_lines_cols(), this will break.
		_logger.debug(f".resize(): Resizing terminal to {(height,width)}.")
		resizeterm(height, width)

			# Now that everything is consistent, repaint the display.
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
		
			# This effectively just measures & paints the display.
		theDisplay.resize()
	
	
	def _runMainloop(theDisplay):
		
		screen = theDisplay._screen
		client = theDisplay._client
		
		# Here's the actual main loop.
		while True:	# Infinite loop; we just have to break out when done.
			try:
				ch = screen.getch()
				if ch == ERR:
					continue
				keyevent = KeyEvent(keycode=ch) #, wide=wide_ch)
				client.handle_event(keyevent)
			except KeyboardInterrupt as e:
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
			
			# Call the standard curses wrapper on our private display driver method, above.
		wrapper(theDisplay._displayDriver)
		# If we get here, then the display driver has exited, and the display was torn down.

	#__/ End method theDisplay.runDisplay().
	
#__/ End singleton class TheDisplay.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/display.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%