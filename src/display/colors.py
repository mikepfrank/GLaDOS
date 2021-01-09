#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 display/colors.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""	FILE NAME:		display/colors.py				 [Python module source file]
	
	MODULE NAME:	display.colors
	IN PACKAGE:		display
	FULL PATH:		$GIT_ROOT/GLaDOS/src/display/colors.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.display (Display screen management)


	MODULE DESCRIPTION:
	===================
	
		This module provides definitions to support working with colors on a 
		text terminal.  (Presently, it only supports 8-color, 64-color-pair 
		xterm-like terminals such as Windows Putty.)
		
	
	DEPENDENCIES:
	-------------
	
		* The colors module references the (standard) 'enum' module, the
			curses package, and our infrastructure.logmaster module.
		
		* The colors module is referenced by the '.controls' module and the 
			'.display' module and...										 """
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
		
		'init_color_pairs', 'colors_attr', 'style_to_attr', 


			#|--------------------
			#| "Type" definitions.
		
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
		'PLAIN', 'BORDER', 'HEADER', 'BRIGHT_CURSOR', 'DIM_CURSOR',
				# Rendering style designators for character types.
		'CONTROL', 'WHITESP', 'METACTL', 'METAWSP',
				# Logging-related rendering styles (move to console package?)
		'DEBUG_STYLE', 'INFO_STYLE', 'GOOD_STYLE', 'WARNING_STYLE', 
		'ERROR_STYLE', 'CRITICAL_STYLE', 'FATAL_STYLE'
	]
	
#__/ End definition of module-level special global constant array, __all__.


	#|==========================================================================
	#| 	2.	Imports.									   [module code section]
	#|
	#|		2.1.  Standard Python modules imported into this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from enum	import Enum			# Support for enumerated types.
from os		import path 		# Manipulate filesystem path strings.

from curses import (	# A bunch of names, below.

			#-----------------
			# Color constants.
			
		COLOR_BLACK, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA,
		COLOR_RED, COLOR_WHITE, COLOR_YELLOW,

			#---------------------
			# Attribute constants.
			
		A_BOLD,		# Actually just brightens the foreground color.
		A_BLINK,	# Actually just brightens the background color.

			#-----------
			# Functions.
			
		init_pair, color_pair
	
	)

			#|------------------------
			#| Logging-related stuff.

from infrastructure.logmaster import (
		sysName,			# Used just below.
		ThreadActor,		# TUI input thread uses this.
		getComponentLogger,	# Used just below.
	)
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.
global _sw_component
_sw_component = sysName + '.' + _component


	#|==========================================================================
	#|	3.	Type definitions.							   [module code section]
	#|
	#|		In this section, we define various "types" that we provide.
	#|		Essentially, for us, a "type" just means a simple class, or
	#|		any way of using a structured object as a simple data type.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(colors.)Brightness						[public enumerated type]
		#|
		#| 		Below we define an enum type and some associated global 
		#|		constants for designating brightness values.  In addition 
		#|		to 'bright' and 'normal' brightness levels we also have 
		#|		'dim' which is used when referring to gray or 'dim white', 
		#|		which is really implemented as 'bright black' behind the 
		#|		scenes.  These values are used in forming "color specifiers," 
		#|		defined further below.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Brightness(Enum):
	"""Brightness										[public enumerated type]
	
		This class provides an enumerated type for color display bright-
		ness designators.  We're assuming that the display (like xterm/
		Putty) natively supports 'normal' and 'bright' brightness values.  
		We only assume that the 'dim' value is supported in the case of 
		white; internally, this is implemented as "bright black."			 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	DIM		=	'dim'		# Supported only for white (implemented as bright black).
	NORMAL	=	'normal'
	BRIGHT	=	'bright'	# Bright colors are generated by the A_BOLD attribute.

#__/ End enum Brightness.

	#|--------------------------------------------
	#| Define shorter names for brightness values.
	
global DIM, NORMAL, BRIGHT

DIM    	=	Brightness.DIM	   # Used only for 'dim white' (a.k.a. 'bright black').
NORMAL	=	Brightness.NORMAL
BRIGHT	=	Brightness.BRIGHT


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| A "color specifier" is a pseudo-type that actually just consists of 
		#| an ordered pair; the first element of the pair is a "base color," 
		#| which means a curses-defined color, while the second element of the 
		#| pair is a brightness designator, defined above.  The following
		#| function constitutes a specialized constructor for color specifiers,
		#| which automatically translates "dim white" to "bright black", so as 
		#| to make our code for constructing that specific color more readable.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ColorSpec(baseColor, intensity):
	"""ColorSpec									 [public pseudo-constructor]
	
		This function generates an ordered pair representing a color 
		specification, consisting of a base color together with a 
		brightness value.  This 'constructor' does some special work
		that is needed to support the "dim white" color spec.				 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# Simply replace "dim white" with "bright black."
	if (baseColor == COLOR_WHITE) and (intensity == DIM):
	
		baseColor	= COLOR_BLACK
		intensity	= BRIGHT
		
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class RenderStyle(Enum):
	"""RenderStyle										[public enumerated type]
	
		This enum provides designators for some pre-defined rendering
		styles, each of which translates into a foreground/background 
		pair of color specifiers, using the private '_style_colors[]'
		lookup table defined in this module.								 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# Use this style for displaying normal printable text.
	PLAIN='plain'

		# Use this style for drawing window borders and separators.
	BORDER='border'

		# Use this style for displaying text headers that stand out.
	HEADER='header'

		# Styles used for alternating bright and dim (blinking) cursor.
	BRIGHT_CURSOR='bright-cursor'
	DIM_CURSOR='dim-cursor'

		#|------------------------------------------------------------
		#| The following styles are for rendering of control and
		#| whitespace characters.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# Use this style for rendering 7-bit ASCII control characters.
	CONTROL='control'

		# Use this style for rendering ordinary whitespace characters
	WHITESPACE='whitespace'

		# Use this style for rendering control characters with 8th bit set.
	META_CONTROL='meta-control'

		# Use this style for rendering whitespace characters with 8th bit set.
	META_WHITESPACE='meta-whitespace'
	
		#|------------------------------------------------------------
		#| The following styles were added for use by the log panel.
		#| Error style and good style also used within the diagnostic 
		#| panel.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		# Use this style for rendering debug-level log output.
	DEBUG_STYLE='debug-style'
	
		# Use this style for rendering info-level log output.
	INFO_STYLE='info-style'
	
		# Use this style for rendering normal-level log output.
	GOOD_STYLE='good-style'
	
		# Use this style for rendering warning-level log output.
	WARNING_STYLE='warning-style'
	
		# Use this style for rendering error-level log output.
	ERROR_STYLE='error-style'
	
		# Use this style for rendering critical-level log output.
	CRITICAL_STYLE='critical-style'

#__/ End enum RenderStyle.

	# Put the render styles in shorter globals.

global PLAIN, BORDER, HEADER, BRIGHT_CURSOR, DIM_CURSOR

PLAIN			=	RenderStyle.PLAIN
BORDER			=	RenderStyle.BORDER
HEADER			=	RenderStyle.HEADER
BRIGHT_CURSOR	=	RenderStyle.BRIGHT_CURSOR
DIM_CURSOR		=	RenderStyle.DIM_CURSOR

global CONTROL, WHITESP, METACTL, METAWSP

CONTROL		=	RenderStyle.CONTROL
WHITESP		=	RenderStyle.WHITESPACE
METACTL		=	RenderStyle.META_CONTROL
METAWSP		=	RenderStyle.META_WHITESPACE

global DEBUG_STYLE, INFO_STYLE, GOOD_STYLE
global WARNING_STYLE, ERROR_STYLE, CRITICAL_STYLE

DEBUG_STYLE 	=	RenderStyle.DEBUG_STYLE
INFO_STYLE		=	RenderStyle.INFO_STYLE
GOOD_STYLE		=	RenderStyle.GOOD_STYLE
WARNING_STYLE	=	RenderStyle.WARNING_STYLE
ERROR_STYLE		=	RenderStyle.ERROR_STYLE
CRITICAL_STYLE	=	RenderStyle.CRITICAL_STYLE
FATAL_STYLE		=	CRITICAL_STYLE


	#|==========================================================================
	#|	4.	Static data structures.					   	   [module code section]
	#|
	#|		In this section, we define various static data structures
	#|		(such as arrays, tables, and dictionaries) that we need.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	colors._style_colors			 [private global data structure]
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

	#STYLE:			(FOREGROUND,  	BACKGR),
	#-------		-------------	--------
	PLAIN:			(WHITE,		  	BLACK ),		# Normal characters: Medium-white text on black background.
	BORDER:			(BRIGHT_CYAN, 	BLACK ),		# Border characters: Bright cyan text on a black background.
	HEADER:			(BRIGHT_WHITE,	BLACK ),		# Text headers: Bright white on a black background.
	BRIGHT_CURSOR:	(BLACK,			BRIGHT_GREEN),	# Bright cursor: Black text on a bright green background.
	DIM_CURSOR:		(BLACK,			GREEN),			# Dim cursor: Black text on a medium green background.

	#STYLE:		(FOREGROUND,  	BACKGR),
	#-------	-------------	--------
	CONTROL:	(BLACK,		  	RED	  ),	# Control characters: 			Black text on a red background.
	WHITESP:	(GRAY,		  	BLACK ),	# Whitespace characters: 		Faded (gray) text on black background.
	METACTL:	(BLACK,		  	BLUE  ),	# Meta-control characters: 		Black text on blue background.
	METAWSP:	(BLUE,		  	BLACK ),	# Meta-whitespace characters: 	Blue text on black background.

	#STYLE:			(FOREGROUND,  		BACKGR),
	#-------------	-------------		--------
	DEBUG_STYLE:	(BRIGHT_BLUE,		BLACK),		# Debug log messages: 		Bright blue on black.
	INFO_STYLE:		(BRIGHT_MAGENTA,	BLACK),		# Info log messages: 		Bright magenta on black.
	GOOD_STYLE:		(GREEN,				BLACK),		# Normal log messages: 		Green means all is good!
	WARNING_STYLE:	(YELLOW,			BLACK),		# Warning log messages: 	Yellow is a warning color.
	ERROR_STYLE:	(RED,				BLACK),		# Error log messages: 		Red denotes bad/wrong/error.
	CRITICAL_STYLE:	(BRIGHT_YELLOW,		RED),		# Critical log messages:	Bright yellow on a red background.  Stands out the most.
	
}


	#|==========================================================================
	#|	4.	Function definitions.						   [module code section]
	#|
	#|		In this section we define the various functions provided by 
	#|		this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(colors.)init_color_pairs()						   [public function]
		#|
		#|		This public function initializes the color pairs, assuming 
		#|		that we have 8 standard colors available (curses standard) 
		#|		and 64 color pairs (1 fixed plus 63 configurable).
		#|
		#|		Note the calculation of the color components here from the
		#|		color pair index is the inverse of the calculation of the 
		#|		color pair index from the color components in colors_attr().
		#|		I.e., these two functions are designed to work together.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def init_color_pairs():
	"""(colors.)init_color_pairs()							  [public function]
	
		This function initializes all color pairs having indices in the 
		range 1-63 in such a way that every possible combination of a 
		foreground color and background color can be easily mapped to a 
		corresponding color pair index in the range 0-63.
			
		The function colors_attr() (below) can then be used to map any 
		desired foreground/background color combination to a correspond-
		ing setting of display attributes.									 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# Iterate over all possible 6-bit color pair codes, except for 000000.
	for pair_index in range(1,64):		
	
			# Obtain the background color as the most-significant 3 bits.
		bgcolor = int(pair_index / 8)
		
			# Obtain the foreground color from the least-significant 3 bits.
		fgcolor = (pair_index - 1) % 8
				# Note that the -1 (equiv. +7) here is needed for consistency
				# because color pair #0 has fg=white (7) standardly.
		
			# Make sure that particular color pair is set up properly as we want it.
		_logger.debug(f"Creating color pair #{pair_index} = (fg: {fgcolor}, bg: {bgcolor}).")

			# This actually initializes the color pair.
		init_pair(pair_index, fgcolor, bgcolor)
	
	#__/ End for loop over pair indices 1-63.
	
#__/ End function init_color_pairs().
		

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(colors.)colors_attr()							   [public function]
		#|
		#|		Turns a pair of color specs into a correspending setting
		#|		of display attributes (which is a non-negative integer 
		#|		encoding a bit string).  Assumes that the color pairs 
		#|		have been previously set up as in init_color_pairs().
		#|
		#|		Note the calculation of the color pair index here from the
		#|		foreground/background color components is the inverse of 
		#|		the calculation of color components from the color pair 
		#|		index in init_color_pairs().  That is, these two functions 
		#|		are designed to be used together.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def colors_attr(fgColorSpec:ColorSpec, bgColorSpec:ColorSpec):
	"""(colors.)colors_attr()								   [public function]
	
		This function returns the curses display attribute setting that 
		corresponds to a given fg/bg pair of color specs.					 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

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
		#|	(colors.)style_to_attr()						   [public function]
		#|
		#|		This function maps a render style designator to the 
		#|		corresponding display attribute setting (bit-vector).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def style_to_attr(style:RenderStyle):
	"""(colors.)style_to_attr()								   [public function]
	
		This function maps a render style designator to the corres-
		ponding display attribute setting (bit-vector).						 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# First, find the fg/bg pair of color specifiers 
		# that corresponds to the given rendering style.
	(fgSpec, bgSpec) = _style_colors[style]
	
		# Next, convert that to an attrs setting and return.
	return colors_attr(fgSpec, bgSpec)

#__/ End function display.style_to_attr().


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/colors.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
