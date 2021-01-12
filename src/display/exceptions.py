# exceptions.py - Display-related exception classes.

	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|
	#|	1.  Exported name list. 		   				   [module code section]
	#|
	#|			Here we list all of the public names that are standardly
	#|			exported from this module, if the using module does:
	#|
	#|						from display.exceptions import *
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
global __all__ 
__all__ = [		# List of all public names exported from this module.

			#|------------
			#| Exceptions.
		
		'DisplayException', 	# Base class for display-related exceptions.
		'RenderExcursion',		# InfoException: Rendered text went off the screen.
		'DisplayNotRunning',	# WarningException: Display is not running.
		'DisplayDied',			# ErrorException: Display unexpectedly quit.
		'RequestRestart',		# CriticalException: Request display restart.
		'TerminateServer',		# FatalException: Terminate entire GLaDOS server.
		
	]


from os			import path 		# Manipulate filesystem path strings.  Used in logger setup.

			#|------------------------
			#| Logging-related stuff.
			#|vvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.logmaster import (
		sysName,			# Used just below.
		getComponentLogger,	# Used just below.
		LoggedException,	# DisplayException inherits from this.
		InfoException,		# RenderExcursion inherits from this.
		WarningException,	# DisplayNotRunning inherits from this.
		ErrorException,		# DisplayDied inherits from this.
		CriticalException,	# RequestRestart inherits from this.
		FatalException		# We derive TerminateServer from this.
	)
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.
global _sw_component
_sw_component = sysName + '.' + _component



		#|===========================================
		#| Exception classes provided by this module.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class DisplayException(LoggedException):
	
	"""This is an abstract base class for all exception types generated
		by the text display facility."""
	
	defLogger = _logger		# Use the display package's logger.


class Loc: pass

class RenderExcursion(DisplayException, InfoException):

	"""This is an exception type that is thrown by the 
		display.renderText() method when the rendering
		moves outside the available window."""

	def __init__(exception, msg:str="Render excursion",
		ch:int=None, pos:int=None, loc:Loc=None, yx2pos:dict={},
		pos2yx:dict={}):
		
		exception._msg = msg
		exception._ch = ch
		exception._pos = pos
		exception._loc = loc
		exception._yx2pos = yx2pos
		exception._pos2yx = pos2yx
	
	def __str__(exception):
		return exception._msg
	

class DisplayNotRunning(DisplayException, WarningException):

	"""This is an exception type that is returned (not thrown)
		by the display driver when a requested task is aborted
		and ignored because the display is not actually running."""
		
	pass

class DisplayDied(DisplayException, ErrorException):

	"""This is a more serious (error-level) exception that notes
		that the display is apparently no longer running, even though 
		we expected it to still be running."""
		
	pass

class RequestRestart(DisplayException, CriticalException):

	"""This is an exception type that requests for the entire curses
		display to be torn down and restarted.  Not yet supported."""
	
	pass

class TerminateServer(DisplayException, FatalException):

	"""This is an exception type that is thrown when the display facility
		is requesting the entire GLaDOS server process to shut down.  This
		generally happens because we caught a ^T (terminate) keystroke
		that was typed by the system operator."""

	pass

