# text/buffer.py

#		TextBuffer				- An adjustable-sized buffer of text spooled to the window.

from	collections.abc		import	Iterable

from os import path
from infrastructure.logmaster	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)				# Create the component logger.


# We should probably move this to its own package because it isn't really
# specific to the window system per se.  For example, it can also be used
# by the receptive field, the writing app, or other packages.

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
					wrapLines:bool = True, wordWrap:bool = False, rows:Iterable=None):
		
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
		self._wordWrap			= wordWrap

		self._rows = None			# Buffer is empty initially. No row data.
		
			# If rows are provided, add them to the buffer.
		
		if rows is not None:
			for str in rows:
				self.addLine(str)	# Make sure each added line ends with a newline.
				
	#__/ End TextBuffer.__init__().
	
	@property
	def wordWrap(buf):
		return buf._wordWrap

	@wordWrap.setter
	def wordWrap(buf, newVal:bool):
		_logger.debug(f"Setting word wrapping on text buffer to {newVal}.")
		buf._wordWrap = newVal

	def view(self):

		"""Returns a 'view' of this text buffer, which simply means, a single
			text string that renders the entire visual appearance of the buffer's
			contents. Generally, this is generated by just joining together the
			lines in the buffer (interspersed with newlines if needed)."""

		bufHasNLs = self._includeNewlines
		delimiter = '' if bufHasNLs else '\n'

		theView = delimiter.join(self._rows)

		return theView


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
			
		maxWid = self._maxWid
		while True:
			
				# OK, now we simply append the given raw string onto the end of
				# the string in the last row of the buffer.
			
			self._rows[-1] = self._rows[-1] + rawStr
		
				# As a result of doing this, the last row of the buffer may have
				# become overlong!	If so, then we need to either truncate it or
				# wrap it.
			
			if maxWid is not None:	# First, make sure there *is* a max width.
			
				line = self._rows[-1]

				if self._effectiveStrLen(line) > maxWid:
					# Line (even ignoring any final newline) is too long.

					_logger.debug(f"The following line is longer than maxWid={maxWid}:\n" + line)
				
					# Are we supposed to be doing wrapping? (Either character-based or word-based?)

					wordWrap = self.wordWrap

						# Normally if we're in word-wrap mode, that will override
						# regular-style line wrapping.
					lineWrap = self._wrapLines and not wordWrap

					doWrapping = lineWrap or wordWrap

						# If we're supposed to be doing wrapping, then we 
						# need to remember the part of the line we're chopping 
						# off, so that we can wrap it around to the next line 
						# instead.
						
						# In word wrap mode, we have to search for the line-break location.
					if wordWrap:
						_logger.debug("Trying word-wrapping...")
						# Determine where to insert line break.
						found = False
						for i in range(0, maxWid):
							pos = (maxWid - 1) - i
							char = line[pos]
							if char == ' ':  # Look for space.
								found = True
								pos = pos + 1			# Insert break just after the space.
									# Chop off everything after space.
								chopped = line[pos:]
								self._rows[-1] = line[:pos]
								break	# Stop looking.
						
						if not found:
							# Didn't find any spaces! Revert to regular line wrapping instead.
							lineWrap = True 
						
					if lineWrap:	# We're in line-wrap mode, we or reverted to it.
						chopped = line[maxWid:]		# Save what we're chopping off.
					
					# Unless we're doing word wrapping, the line that
					# we're currently working on is going to be truncated
					# to (just barely) fit on the current row.

					if not wordWrap:
						# Now, we just chop the line short to fit.
						self._rows[-1] = line[:maxWid]
					
					# If we're wrapping at all, then at this point, we *have*
					# to open a new line, because there's stuff left that
					# has to go on the next line. This is the case where
					# we have to continue the while loop.
						
					if doWrapping:
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

		# NOTE: We need to modify this code to handle embedded tabs; also,
		# we need the textBuffer to know what column it's starting at and
		# what the tab-width is in order to even interpret tabs correctly!

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
	
	
	def getLine(self, rowIndex, nlTerminated=True):
		"""Gets a line from the buffer. The returned line
			will be newline-terminated unless nlTerminated
			is False."""
	
		if self._rows is None:
			return None 
		
		bufLen = self.nRows()
		if bufLen is 0: return None 
		
		if rowIndex >= bufLen:
			return None

		lineWithNL = self.ensureLine(self._rows[rowIndex])

		# Does caller want lines to be newline-terminated
		if nlTerminated:
			line = lineWithNL
		else:
			line = lineWithNL[:-1]	# Truncate off final NL.

		return line
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

