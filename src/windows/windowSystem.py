#|==============================================================================
#|                TOP OF FILE:    windows/windowSystem.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:      windows/windowSystem.py     [Python module source file]

    IN PACKAGE:		windows
	MODULE NAME:    windows.windowSystem
    FULL PATH:      $GIT_ROOT/GLaDOS/src/windows/windowSystem.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (General Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.commands (command interface component)


	MODULE DESCRIPTION:
	-------------------

		This module initializes the GLaDOS command interface. This is the
		interface that allows the AI to type commands to the GLaDOS system
		and have them be executed by the system.
		
		The command interface is organized into "command modules" associated
		with specific facilities or processes within the GLaDOS system.  New
		command modules can be added dynamically into the interface.  In the
		main loop of the system, when the A.I. generates a text event, it is
		parsed to see if it matches a command template, and if so, then 
		control is dispatched to an appropriate command handler.

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


    #|==========================================================================
    #|
    #|   1. Module imports.                                [module code section]
    #|
    #|          Load and import names of (and/or names from) various
    #|          other python modules and pacakges for use from within
    #|          the present module.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|  1.1. Imports of standard python modules.    [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|  1.2. Imports of custom application modules. [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|  The following modules, although custom, are generic utilities,
			#|  not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        # A simple decorator for singleton classes.
from infrastructure.decorators  import  singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.  (This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)    			# Create the component logger.


    #|==========================================================================
    #|
    #|   Globals					    						[code section]
    #|
    #|      Declare and/or define various global variables and
    #|      constants.  Note that top-level 'global' statements are
	#|		not strictly required, but they serve to verify that
	#|      these names were not previously used, and also serve as 
	#|		documentation.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|
        #|  Special globals.                              	[code subsection]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language. 
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__	# List of public symbols exported by this module.
__all__ = [
		'TextBuffer',		# Class for an adjustable-sized buffer of text spooled to the window.
		'Window',			# Class for a single window within the GLaDOS text window system.
		'Windows',			# Class for a collection of text windows.
		'WindowSnapshot',	# Class for a static, frozen record of what a given window contained at a specific point in time.
		'WindowSystem',		# A singleton class for the entire window subsystem of GLaDOS.
	]


	#|==========================================================================
	#|
	#|	Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


# Window system classes:
#
#       TextBuffer              - An adjustable-sized buffer of text spooled to the window.
#       Window                  - A text window within the GLaDOS window system.
#       Windows                 - A collection of text windows.
#       WindowSnapshot          - A static image of a text window at a given point in time.
#       WindowSystem            - The entire window subsystem in a given GLaDOS system instance.




class TextBuffer:       # A text buffer.

	"""
		TextBuffer										   [module public class]
		
			This is a class for text buffers used in the window system.
			Conceptually, a text buffer is a (usually bounded-length)
			linear sequence of individual lines or rows of text.  A given
			line is defined by containing no newline characters, except 
			that (in certain configurations) there is always one at the 
			very end of the line, except that the very last line in the 
			buffer will generally have no newline at the end.
			
			Characteristics of a text buffer include:
			
				- A maximum length in rows, which is an integer >= 0.
					Or, if this is None, then the length is unbounded.
					(WARNING: This is dangerous, as the host may run
					out of space.)
					
				- An iterable, indexible sequence of >= 0 actual lines of 
					text.  If the maximum length is not None, then the
					actual length of this sequence should be no greater 
					than the maximum length.  If this sequence is None, 
					this is deemed equivalent to a sequence of 0 rows.
					
				- A text buffer may optionally also have a maximum width,
					which is the maximum length of any line in the buffer.
					Lines that are longer are either wrapped to the next 
					line or truncated, depending on buffer configuration.
					If there is no maximum width, this can be dangerous.
					
			Operations on a text buffer include:
			
				- Text (any string) may be appended to the end of the
					buffer.  This creates new rows as needed.  If the
					maximum number of rows in the buffer would have been
					exceeded, rows are automatically removed from the 
					start of the buffer to make room.
	"""

	#/--------------------------------------------------------------------------
	#|	Private instance data members.					   [class documentation]
	#|
	#|		._maxLen [int or None]
	#|
	#|			This is an integer >= 0 indicating the maximum length of
	#|			the text buffer in rows, or None to indicate that there is
	#|			no maximum length (note that this can be dangerous).
	#|
	#|		._maxWid [int or None]
	#|
	#|			This is an integer >= 0 indicating the maximum length of
	#|			each line of text, in characters, or None if there is no
	#|			maximum length (note that this can be dangerous).  The
	#|			max width does not include any final newline character.
	#|
	#|		._includeNewlines [bool]
	#|
	#|			This is a boolean value which should be True if and only if
	#|			each line (except possibly the last) should be terminated
	#|			with an explicit newline character ('\n').  (If this is False
	#|			then the entire text buffer will contain no newlines.)  (Note
	#|			that the AI's view of the buffer will generally have newlines
	#|			added in any case, so this option doesn't make much difference.)
	#|
	#|		._wrapLines [bool]
	#|
	#|			If this is True, then overlong lines will be wrapped around
	#|			to the next line; otherwise, they will be truncated at 
	#|			._maxWid characters long.
	#|
	#|		._rows [Iterable]
	#|
	#|			This is an iterable, indexible sequence of lines of text,
	#|			each of which should be a string.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        
    def __init__(self, maxLen:int = 100, maxWid:int = 100, includeNewlines:bool=True,
					wrapLines:bool = True, rows:Iterable=None):
		
		"""textBuffer.__init__()					  [special instance method]
		
				Instance initializer for the TextBuffer class.  This 
				basically just sets private instance data members
				to the provided parameters.  Arguments are:
				
					maxLen [int or None]
					
						Maximum buffer length in rows of text, or None 
						if unlimited (DANGER!).  Default value is 100.
					
					maxWid [int or None]
					
						Maximum buffer width in characters, or None if
						unlimited (DANGER!).  Terminating newlines are 
						not counted.  Default value is 100.
					
					includeNewlines [bool]
					
						True if the newline character at the end of each
						line is explicit; otherwise, it is implicit.
						Default value is True.
					
					wrapLines [bool]
						
						False if overlong lines are truncated; if True 
						then they are wrapped around to the next line.
						Default value is True.
					
					rows [Iterable]
					
						Initial sequence of rows contained in the buffer.
						Each line should be a string.  The effect is the
						same as adding the text of each row (terminated by
						an explicit implicit newline) to the buffer.  (That 
						is, overlong lines will be truncated or wrapped, and 
						lines will spool off the end of the buffer if it gets 
						overfull.)
		"""
					
        self._maxLen 			= maxLen
		self._maxWid			= maxWid
		self._includeNewlines	= includeNewlines
		self._wrapLines			= wrapLines

        self._rows = None           # Buffer is empty initially. No row data.
		
			# If rows are provided, add them to the buffer.
		
		if rows is not None:
			for str in rows:
				self.addLine(str)	# Make sure each added line ends with a newline.
				
	#__/ End TextBuffer.__init__().
		
        
    def addText(self, text:str = None):
		"""
			textBuffer.addText()						[public instance method]
			
				Appends the given text string to the end of this buffer.
				Overlong lines are truncated or wrapped.  If the buffer
				becomes overfull, initial rows are scrolled up and off 
				the top of the buffer and discarded until the buffer is
				no longer overfull.
		"""
        return if text is None		# Do nothing if there's no text.

			# First, we'll split the given text on newlines,
			# and then add the lines individually.  Note that this 
			# always returns a list with at least one element.
			
		lines = text.split('\n')
		
			# For each line before the last one, we're going to add it 
			# to the buffer using the '.addLine()' method.  This makes 
			# sure that each line added actually ends with a newline 
			# (these lines don't, yet) and then adds it to the buffer
			# using the '._addRaw()' method, which doesn't add a newline
			# unless the current line gets overlong.
		
		for line in lines[0:-1]:	# Could be empty if text was ''.
			self.addLine(line)
			
			# The last line added is whatever was after the last newline
			# in the text, thus, it shouldn't have a newline added, so
			# instead we just use ._addRaw() for that one.
		
		self._addRaw(lines[-1])
		
	#__/ End method textBuf.addText().
	
	
	def addLine(self, line:str = None):
		"""
			textBuffer.addLine()						[public instance method]
			
				The provided text string should not have any newlines,
				except for possibly one at the end.  This method ensures
				the string ends in a newline (one is added if not present)
				and then appends that string to the buffer.  In the process,
				the final line of the buffer could end up being truncated or
				wrapped, and earlier lines may be scrolled up and off if the
				buffer becomes overfull.
		"""
	
		return if line is None		# If nothing, do nothing.
		
			# If line doesn't already end with a newline, add one.
		
		if line == '' or line[-1] != '\n':
			line = line + '\n'
			
			# Now do the raw add.
			
		self._addRaw(self, line)
		
	#__/ End method textBuf._addLine().
	
	
	def _addRaw(self, rawStr:str = None):
		"""
			textBuffer._addRaw()						[private instance method]
			
				This method does the real low-level work of adding text to 
				the buffer.  First, if there are no rows in the buffer yet,
				then a new row is opened to contain the required text.  Then
				the text is appended to that row.  Then, if the row is now
				overlong, it is truncated or wrapped.  If the buffer now 
				contains too many rows, then rows are scrolled off the top.
				
				NOTE: The text string provides MAY NOT CONTAIN ANY NEWLINES 
				prior to its final character, which can be a newline or not.
				(If so, then a new line is added after this one.)
		"""
		return if rawStr is None	# If nothing provided, do nothing.
		
		# An important assumption here is that rawStr contains no newlines
		# before the last character. We really should check this here.
		
			# At this point, we know that we at least have an empty string,
			# so we need at least one row in the buffer to contain the string.
			# If there are no rows yet, create one, initially with "".
			
		if self._rows is None or len(self._rows) == 0:
			self._rows = ['']	# A single initially-empty row.
			
			# Next we need a while loop, in case we're in line-wrap mode and
			# the text ends up spilling over multiple lines.  We'll break out 
			# of it when we're done.
			
		while True:
			
				# OK, now we simply append the given raw string onto the end of
				# the string in the last row of the buffer.
			
			self._rows[-1] = self._rows[-1] + rawStr
		
				# As a result of doing this, the last row of the buffer may have
				# become overlong!  If so, then we need to either truncate it or
				# wrap it.
			
			if self._maxWid is not None:	# First, make sure there *is* a max width.
			
				if self._effectiveStrLen(self._rows[-1]) > self._maxWid:	# Line (even ignoring any final newline) is too long.
				
						# If we're supposed to be doing line wrapping, then we 
						# need to remember the part of the line we're chopping 
						# off, so that we can wrap it around to the next line 
						# instead.
						
					if self._wrapLines:
						chopped = self._rows[-1][self._maxWid:-1]		# Save what we're chopping off.
					
						# Now, we just chop the line short to fit.
					self._rows[-1] = self._rows[-1][0:self._maxWid]
					
						# If we're line-wrapping, then at this point, we *have*
						# to open a new line, because there's stuff left that
						# has to go on the next line. This is the case where
						# we have to continue the while loop.
						
					if self._wrapLines:
						self._openNewLine()
							# And, at this point, the chopped text becomes our new raw text, and we continue.
						rawStr = chopped
						continue			# Goes back up to top of while loop.
					#__/ End if wrapping.
				#__/ End if line is too long.
			#__/ End if there's a max line length.
			
			# If we get here, then either:
			#
			#	(1) We just truncated an overlong line;
			#	(2) The effective line length is less than or equal to the maximum;
			#	(3) There is no maximum line length (max buffer width).
			#
			# In any of these cases, we are done with line wrapping, so at this
			# point, we simply break out of the loop.
			
			break	
			
		#__/ End line-wrapping while loop..
		
		# When we get here, it means that we're done with adding the text,
		# including whatever line wrapping or truncating we needed to do.
		
			# If we're not in the '_includeNewlines' mode, then we need to
			# make sure that what we just did didn't cause the last line of
			# of the buffer to end in a newline character (which could have
			# happened if the rawStr ended in newline).  If it did, then
			# we remove it.
		
		if not self._includeNewlines:
			if len(self.rows[-1]) > 0 and self.rows[-1][-1] == '\n':	# Is last character newline?
				self.rows[-1] = self.rows[-1][0:-1]		# Trim off last character.
		
			# At this point, we have one final task.  Namely: If the raw text
			# string we were given to add ended with a newline, then the last
			# thing we have to do is to actually open a new line at the end of
			# the buffer.  Otherwise, we just stay on the line we're on.
			
		if len(rawStr) > 0 and rawStr[-1] == '\n':
			self._openNewLine()
			
	#__/ End textBuf._addRaw().

			
	def _effectiveStrLen(self, text:str = None):
		"""
			textBuffer._realLength()				   [private instance method]
			
				Given a string which may or may not end in a newline, how
				long is that string if we don't include the final newline
				(if any) in the count?
		"""
		return 0 if text is None or text == ''
		
		realLen = len(text)
		
		if text[-1] == '\n':
			effectiveLen = realLen - 1
		else:
			effectiveLen = realLen
		
		return effectiveLen
		
	#__/ End method textBuf._effectiveStrLen().
	
	
	def _openNewLine(self):
		"""
			This method adds a new line to the end of the buffer.
			This means, make sure the last line ends in a newline
			character (if we're doing explicit newlines), and then
			add a new line after it that is initially empty.
		"""
		if self._rows is None or len(self._rows) == 0:
			self._rows = ['']	# A single initially-empty row.
		else:
			if self._includeNewlines:
				if len(self._rows[-1]) == 0 or self._rows[-1][-1] != '\n':
					self._rows[-1] = self._rows[-1] + '\n'
			self._rows.append('')	# Add a new row that's initially empty.
		
			# At this point, since we just added a new row to the buffer,
			# we have to make sure that the buffer isn't now overfull (too
			# many lines).  If it is, then we shorten it by removing rows 
			# from the top until it is back in spec.
			
		while True:		# Infinite loop (terminated with break).
		
			bufLen = len(self._rows)	# How big are we?
			
			if bufLen <= self._maxLen:	# Is buffer length OK?
				break	# Hey, we're all good, so bust loose.
				
				# Scroll the top row of the buffer off the top.
			self._rows = self._rows[1:bufLen]
		#__/ End while loop.
		
	#__/ End ._openNewLine().
	
#__/ End class TextBuffer.

class Window:   # A text window within the GLaDOS window system.

        # A window has:
        #       - A title (textual label).
        #       - A text history buffer.
        #       - A list of snapshots.
        #       - Whether it is the currently active window.
        #       - An associated process.
        #       - Its state (open, minimized, or closed)
        #       - Its current size (number of lines to view)
        #       - Whether it is trying to stay in the receptive field
        #       - Whether it anchors to the top or bottom of the receptive field or is floating.
		#		- A set of past snapshots taken of it that are known to exist in the system.
        
        def __init__(self, title="Untitled Window", textBuf:TextBuffer=None,
						isActive=True, process:Process=None, state:str='closed'
						viewSize=15, stayVisible:bool=False, anchor:str=None):
		
			if textBuf is None:
				textBuf = TextBuffer()

			if process is None:
				process = Process()
		
			self._title 		= title
			self._textBuf 		= textBuf
			self._isActive		= isActive
			self._process		= process
			self._state			= state
			self._viewSize		= viewSize
			self._stayVisible	= stayVisible
			self._anchor		= anchor
		
            self._snapshots 	= set()

        def addText(self, text:str):
		
				# First, add the text to the end of our internal buffer.
			self.textBuffer.addText(text)
            

class Windows:
    def Windows(self):
        self._windowList = []

class WindowSnapshot:   # A static image of a text window at a given point in time.

        # A snapshot has:
        #       - A text history buffer.
        #       - The window it's a snapshot of.
        #       - The time it was taken.
        #       - Its location in the text stream.
        #       - Its state (open or minimized).
        #       - Its current size (number of lines to inspect).
        
        pass

@singleton      
class WindowSystem:

        # The WindowSystem has:
        #       - Set of all windows in the system.
        #       - List of windows present in the receptive field.
        #       - List of windows anchored to the top of the receptive field.
        #       - List of windows anchored to the bottom of the receptive field (usually there is just one, the presently active window).

        def __init__(self):
                self._windows = Windows()
                


