#|==============================================================================
#|				  TOP OF FILE:	  windows/windowSystem.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		windows/windowSystem.py		[Python module source file]

	IN PACKAGE:		windows
	MODULE NAME:	windows.windowSystem
	FULL PATH:		$GIT_ROOT/GLaDOS/src/windows/windowSystem.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.commands (command interface component)


	MODULE DESCRIPTION:
	-------------------

		This module initializes the GLaDOS command interface. This is the
		interface that allows the AI to type commands to the GLaDOS system
		and have them be executed by the system.
		
		The command interface is organized into "command modules" associated
		with specific facilities or processes within the GLaDOS system.	 New
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
	#|	 1. Module imports.								   [module code section]
	#|
	#|			Load and import names of (and/or names from) various
	#|			other python modules and pacakges for use from within
	#|			the present module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from collections.abc import Iterable
from os import path

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)				# Create the component logger.


			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from commands.commandInterface	import	CommandModule
	# We're going to extend CommandModule with various subclasses 
	# specific to the windowing system.

from processes.processSystem	import	Process

	# We don't need to create applications from this module, so no need
	# to actually import the real Application_ class.
#from apps.appSystem				import	Application_
class Application_: pass	# Do this instead to avoid circular imports.

	#|==========================================================================
	#|
	#|	 Globals												[code section]
	#|
	#|		Declare and/or define various global variables and
	#|		constants.	Note that top-level 'global' statements are
	#|		not strictly required, but they serve to verify that
	#|		these names were not previously used, and also serve as 
	#|		documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|
		#|	Special globals.								[code subsection]
		#|
		#|		These globals have special meanings defined by the
		#|		Python language. 
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__	# List of public symbols exported by this module.
__all__ = [
		'TextBuffer',			# Class for an adjustable-sized buffer of text spooled to the window.
		'WindowImage',			# A sort of text buffer that contains a static rendered window image.
		'WindowCommandModule',	# A command module that contains commands for controlling a specific window.
		'ViewPort',				# Represents the current view a window has on its underlying text buffer.
		'Window',				# Class for a single window within the GLaDOS text window system.
		'Windows',				# Class for a collection of text windows.
		'WindowSnapshot',		# Class for a static, frozen record of what a given window contained at a specific point in time.
		'WindowSystem',			# A singleton class for the entire window subsystem of GLaDOS.
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
#		TextBuffer				- An adjustable-sized buffer of text spooled to the window.
#		Window					- A text window within the GLaDOS window system.
#		Windows					- A collection of text windows.
#		WindowSnapshot			- A static image of a text window at a given point in time.
#		WindowSystem			- The entire window subsystem in a given GLaDOS system instance.




class TextBuffer:		# A text buffer.

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
			
				- The buffer may be cleared (emptied of all content).
				
				- Text (any string) may be appended to the end of the
					buffer.	 This creates new rows as needed.  If the
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
	#|			with an explicit newline character ('\n').	(If this is False
	#|			then the entire text buffer will contain no newlines.)	(Note
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
		
				Instance initializer for the TextBuffer class.	This 
				basically just sets private instance data members
				to the provided parameters.	 Arguments are:
				
					maxLen [int or None]
					
						Maximum buffer length in rows of text, or None 
						if unlimited (DANGER!).	 Default value is 100.
					
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
					
		self._maxLen			= maxLen
		self._maxWid			= maxWid
		self._includeNewlines	= includeNewlines
		self._wrapLines			= wrapLines

		self._rows = None			# Buffer is empty initially. No row data.
		
			# If rows are provided, add them to the buffer.
		
		if rows is not None:
			for str in rows:
				self.addLine(str)	# Make sure each added line ends with a newline.
				
	#__/ End TextBuffer.__init__().
	
	def nRows(self):
		"""Returns the length of the buffer's current contents, in rows of text."""
		if self._rows is None:
			return 0 
		return len(self._rows)
	
	def clear(self):
		"""Empties the text buffer of all content."""
		self._rows = None
		
	def addText(self, text:str = None):
		"""
			textBuffer.addText()						[public instance method]
			
				Appends the given text string to the end of this buffer.
				Overlong lines are truncated or wrapped.  If the buffer
				becomes overfull, initial rows are scrolled up and off 
				the top of the buffer and discarded until the buffer is
				no longer overfull.
		"""
		if text is None:		# Do nothing if there's no text.
			return

			# First, we'll split the given text on newlines,
			# and then add the lines individually.	Note that this 
			# always returns a list with at least one element.
			
		lines = text.split('\n')
		
			# For each line before the last one, we're going to add it 
			# to the buffer using the '.addLine()' method.	This makes 
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
	
	
		# This method can be used to ensure that a given line of
		# text ends with a newline (if it doesn't, then one is added).
		# (We could just make this a module function.)
	
	def ensureLine(self, line:str = None):
	
		if line is None:
			return None 	# No actual line, leave it alone.
		
			# If line doesn't already end with a newline, add one.
		
		if line == '' or line[-1] != '\n':
			line = line + '\n'

			# Now return the tweaked line.
			
		return line
	
	
	def addLine(self, line:str = None):
		"""
			textBuffer.addLine()						[public instance method]
			
				The provided text string should not have any newlines,
				except for possibly one at the end.	 This method ensures
				the string ends in a newline (one is added if not present)
				and then appends that string to the buffer.	 In the process,
				the final line of the buffer could end up being truncated or
				wrapped, and earlier lines may be scrolled up and off if the
				buffer becomes overfull.
		"""
	
		if line is None:		# If nothing, do nothing.
			return 
		
			# If line doesn't already end with a newline, add one.
		line = self.ensureLine(line)
			
			# Now do the raw add.			
		self._addRaw(line)
		
	#__/ End method textBuf._addLine().
	
	
	def _addRaw(self, rawStr:str = None):
		"""
			textBuffer._addRaw()						[private instance method]
			
				This method does the real low-level work of adding text to 
				the buffer.	 First, if there are no rows in the buffer yet,
				then a new row is opened to contain the required text.	Then
				the text is appended to that row.  Then, if the row is now
				overlong, it is truncated or wrapped.  If the buffer now 
				contains too many rows, then rows are scrolled off the top.
				
				NOTE: The text string provides MAY NOT CONTAIN ANY NEWLINES 
				prior to its final character, which can be a newline or not.
				(If so, then a new line is added after this one.)
		"""
		if rawStr is None:	# If nothing provided, do nothing.
			return
		
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
				# become overlong!	If so, then we need to either truncate it or
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
			# happened if the rawStr ended in newline).	 If it did, then
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
		if text is None or text == '':
			return 0 
		
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
			# many lines).	If it is, then we shorten it by removing rows 
			# from the top until it is back in spec.
			
		while True:		# Infinite loop (terminated with break).
		
			bufLen = len(self._rows)	# How big are we?
			
			if bufLen <= self._maxLen:	# Is buffer length OK?
				break	# Hey, we're all good, so bust loose.
				
				# Scroll the top row of the buffer off the top.
			self._rows = self._rows[1:bufLen]
		#__/ End while loop.
		
	#__/ End ._openNewLine().
	
	
	def getLine(self, rowIndex):
		"""Gets a line from the buffer. The returned line
			will be newline-terminated."""
	
		if self._rows is None:
			return None 
		
		bufLen = self.nRows()
		if bufLen is 0: return None 
		
		return self.ensureLine(self._rows[rowIndex])
			# Note this ensures that it will appear that the
			# buffer contains explicit newlines, even if it doesn't.
	
	
	def getTextSpan(self, startPos, endPos):
		"""Returns, as a single string, all lines contained
			in the buffer from row #<startPos> to row #<endPos-1>,
			inclusive.	Each line (including the last) will be
			terminated by a newline in the output."""
		
		outputStr = ""
		
		bufLen = self.nRows()
		
		if startPos < 0:
			startPos = 0
			
		if endPos > bufLen:
			endPos = bufLen
		
		for rowIndex in range(startPos, endPos):
			outputStr = outputStr + self.getLine(rowIndex)
		
		return outputStr
	
#__/ End class TextBuffer.

class Window: pass	# Forward declaration

class WindowImage:
	
	"""A rendered image of a text window. This is also a text buffer,
		with decorations at the top and bottom (and maybe also the side)."""
		
	def __init__(self, win:Window, imgHt:int):
		
		self._window		= win
		self._imageHeight	= imgHt
		
			# Create the text buffer to hold the window image.	Initially, 
			# we set the buffer height to the image size, and don't set any
			# maximum width.
		self._textBuffer	= TextBuffer(maxLen = imgHt, maxWid = None)
		
			# Paint the window image in our text buffer.
		self.repaint()
		
	#__/ End windowImage.__init__().
	
	def repaint(self):
		"""Tell the window image to repaint itself in its text buffer."""
		
		self._textBuffer.clear()	# First, clear our text buffer.
		
			# Make sure our window knows how to find us.
			# NOTE: This breaks encapsulation a bit--improve API.
		self._window._image = self

			# Ask our window, "please render your contents in us."
		self._window.render()
		
			# Now that we're done repainting ourselves, tell our
			# window, "hey, now would be a good time to update 
			# your display on the receptive field."
			
		self._window.redisplay()
		
	def addText(self, text:str):
		self._textBuffer.addText(text)
		
	def addLine(self, line:str):
		self._textBuffer.addLine(line)
	
#__/ End class WindowImage.

class WindowCommandModule(CommandModule):

	"""Provides commands for manipulating a specific window when it is active."""
	
	# Note: When a given window becomes active, we should activate its command module,
	# and deactivate that of the previously-active window.
	
	def __init__(self, win:Window):
	
			# First, do generic initialization for instances of class CommandModule.
		super(WindowCommandModule, self).__init__()
		
		self._targetWindow = win
		


class ViewPort:
	"""
		This object tracks the view that a given window has on its
		underlying text buffer.	 A viewPort instance has the following
		properties:
		
			- The underlying window it's associated with.
		
			- size: Size of this viewport, in rows.
		
			- mode: What mode is the viewport in? Supported modes:
			
				static	- In static mode, the top of the viewport 
							stays anchored to its current location
							within the text buffer (relative to the
							top of the buffer.
							
				follow-bot	- In follow-bot mode, the bottom of the
								viewport tries to stay anchored to
								the bottom of the text in the buffer.
								This is the default mode.
								
			- topPos: The position of the top row of the viewport,
				relative to the top of the buffer.
				
			- botPos: The position of (just past) the bottom row of the
				viewport, relative to the top of the buffer.
							
	"""
	def __init__(self, win:Window, size:int, mode='follow-bot', topPos=None, botPos = None):
		self._window = win
		self._size = size
		self._mode = mode
		self._topPos = 0 if topPos is None else topPos
		self._botPos = self._topPos + self._size
		
	def update(self):
		if self._mode == 'follow-bot':
			
				# Find out how many total rows there are in the text buffer currently.
			bufLen = self._window._textBuffer.nRows()
			
				# Get the row number just past the bottom row of the buffer.
			self._botPos = bufLen
			
				# Set our top edge position relative to that.
			self._topPos = self._botPos - self._size
			
				# If it's off the top, don't allow that.
			if self._topPos < 0:  self._topPos = 0
			
				# Now set the bottom row position relative to the top.
			self._botPos = self._topPos + self._size
			

class Window:	# A text window within the GLaDOS window system.

		_DEFAULT_WINDOW_DECORATOR_ROWS	= 2		# One line top, and one line bottom.
		_DEFAULT_WINDOW_DECORATOR_WIDTH = 60	# Sixty columns of fixed-width text characters.
		
		_windowDecoratorRows	= _DEFAULT_WINDOW_DECORATOR_ROWS
		_windowDecoratorWidth	= _DEFAULT_WINDOW_DECORATOR_WIDTH

		# A window has:
		#		- A title (textual label).
		#		- An aplication it's serving.
		#		- A text history buffer.
		#		- A window image (another text buffer).
		#		- A list of snapshots.
		#		- Whether it is the currently active window.
		#		- An associated process.
		#		- Its state (open, minimized, or closed)
		#		- Its current size (number of lines to view)
		#		- Whether it is trying to stay in the receptive field
		#		- Whether it anchors to the top or bottom of the receptive field or is floating.
		#		- A set of past snapshots taken of it that are known to exist in the system.
		#		- A command module for controlling this window when it is active.
		
		def __init__(self, title="Untitled Window", app:Application_=None, textBuf:TextBuffer=None,
						isActive=True, process:Process=None, state:str='closed',
						viewSize=15, stayVisible:bool=False, anchor:str=None):
		
			if textBuf is None:
				textBuf = TextBuffer()

			if process is None:
				process = Process()
		
			self._title			= title
			self._app			= app
			self._textBuffer	= textBuf
			self._isActive		= isActive
			self._process		= process
			self._state			= state
			self._viewSize		= viewSize
			self._stayVisible	= stayVisible
			self._anchor		= anchor
		
			self._commandModule	= WindowCommandModule(self)

			self._viewPort		= ViewPort(self, self._viewSize)
			self._viewPos		= 0		# Window is initially viewing the top of its text buffer.

			self._image			= None	# No image initially--but now we'll make one!
			self._image			= WindowImage(self, viewSize + self._windowDecoratorRows)

			self._snapshots		= set()

		def addText(self, text:str):
			"""Add the given text to the window contents (at the end)."""
		
				# First, add the text to the end of our internal buffer.
			self._textBuffer.addText(text)
			
				# Update our viewport (in case we're following the bottom of the text).
			self._viewPort.update()
			
				# Now, ask our window image to repaint itself.
			self._image.repaint()
		
		def addLine(self, line:str):
			"""Add the given single line of text to the window contents (at the end)."""
			
				# First, add the line to the end of our internal buffer.
			self._textBuffer.addLine(line)
			
				# Update our viewport (in case we're following the bottom of the text).
			self._viewPort.update()
			
				# Now, ask our window image to repaint itself.
			self._image.repaint()
		
		def render(self):
			"""Render this window in its image. Assumes image is initially clear."""
			self.renderTopDecorator()
			self.renderContents()
			self.renderBotDecorator()	# Render the decorator at the bottom of the window.
		
		def renderLine(self, line:str):
			self._image.addLine(line)
		
		def renderTopDecorator(self):
			"""
				The default window top decorator for non-active windows looks as follows:
			
					/----- Window Title ---------------------------------------\
				
				where the total width of this string (in fixed-width characters) is 60 by default.
				Alternatively, if the window is active, then the decorator looks like:
				
					/===== Window Title =======================================\
				
			"""
			
				# First, figure out which character we're going to use for the horizontal window edge.
			horizEdgeChar = '=' if self._isActive else '-'
			
				# Next, generate what the top decorator string would look like
				# if there were no title included at all.
			topDecStr = '/' + horizEdgeChar*(self._windowDecoratorWidth - 2) + '\\'
			
				# Now construct the title string, including padding.
			titleStr = ' ' + self._title + ' '
			
				# How long is it?
			titleStrLen = len(titleStr)
			
				# Where are we going to put it?
			titleStrLoc = 6
			
				# OK, now paint it there (overwriting what was there initially).
			topDecStr = topDecStr[0:titleStrLoc] + titleStr + topDecStr[titleStrLoc+titleStrLen:]
			
				# OK, render that line.
			self.renderLine(topDecStr)
			
		#__/ End method window.renderTopDecorator().
		
		def renderContents(self):
			"""
				This tells us (this window) to render the current view of our 
				window contents in our window image.
			"""
			self._image.addText(self.getViewText())
			
		def getViewText(self):
			"""
				This retrieves (as a single string) the portion of the window
				contents that is presently visible within the window's current 
				viewport on its contents.
			"""
			vp = self._viewPort
			text = self._textBuffer.getTextSpan(vp._topPos, vp._botPos)
			return text
		
		def renderBotDecorator(self):
			"""
				The default window bottom decorator for non-active windows looks as follows:
				
					\----------------------------------------------------------/
				
				If the window is active, however, we change it to:
				
					\=========== Window Commands: /Minimize /Close ============/
				
				where the commands shown are those provided in the window's command module.
			"""
			
				# First, figure out which character we're going to use for the horizontal window edge.
			horizEdgeChar = '=' if self._isActive else '-'
			
				# Next, generate what the bottom decorator string would look like
				# if there were no command text included at all.
			botDecStr = '\\' + horizEdgeChar*(self._windowDecoratorWidth - 2) + '/'
			
				# If the window is active, we'll superimpose a command menu on it:
			if self._isActive:
			
					# Generate a string for the command menu.
				menuStr = ' ' + 'Window Commands: ' + self._commandModule.menuStr() + ' '
				
					# How long is it?
				menuStrLen = len(menuStr)
			
					# Where are we going to put it?	 Center it... (Rounding down.)
				menuStrLoc = int((self._windowDecoratorWidth - menuStrLen)/2)
			
					# OK, now paint it there (overwriting what was there initially).
				botDecStr = botDecStr[0:menuStrLoc] + menuStr + botDecStr[menuStrLoc+menuStrLen:]
			#__/ End if window active.
				
		#__/ End method window.renderBotDecorator().
		
		def redisplay(self):
			"""Advises the window to re-display itself on the receptive field 
				(if it's supposed to be visible)."""
			pass
		
class Windows:
	def Windows(self):
		self._windowList = []

class WindowSnapshot:	# A static image of a text window at a given point in time.

		# A snapshot has:
		#		- A text history buffer.
		#		- The window it's a snapshot of.
		#		- The time it was taken.
		#		- Its location in the text stream.
		#		- Its state (open or minimized).
		#		- Its current size (number of lines to inspect).
		
		pass

@singleton		
class WindowSystem:

		# The WindowSystem has:
		#		- Set of all windows in the system.
		#		- List of windows present in the receptive field.
		#		- List of windows anchored to the top of the receptive field.
		#		- List of windows anchored to the bottom of the receptive field (usually there is just one, the presently active window).

		def __init__(self):
				self._windows = Windows()
				


