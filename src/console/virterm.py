# virterm.py

#|	A "virterm" is a virtual terminal-like object that provides
#|	input/output/error streams that applications can utilize for
#|	communication as if they were interacting with an actual 
#|	terminal, whereas, the stream data is really going to/from 
#|	some other special data sources/sinks.
#|
#|	A virterm also adds some special extra features, including:
#|
#|		* A buffer that remembers past data sent to the 
#|			output/error streams.
#|
#|		* Automatic line-based interleaving of output/error
#|			streams; applications can scan the interleaved 
#|			history in temporal order, and examine whether 
#|			each line came from the regular or error stream.
#|
#|		* Ability to "tee" each output stream, so that all
#|			writes to it go both to the virterm and to some 
#|			other stream.  This can be utilized to capture
#|			a stream in the virterm while still letting it 
#|			also go to its usual destination.
#|
#|	In GLaDOS, virterm objects are utilized in a couple of places:
#|	
#|		* In the main server application, a virterm is created
#|			when the server first starts up, and stdout/stderr 
#|			are redirected to it, as well being duplicated to 
#|			the original streams; this allows early diagnostic
#|			output to be captured and then re-displayed in a 
#|			console panel after the server is started up.
#|
#|		

from 	typing						import Callable
from	io							import StringIO		# Type for I/O streams.
import	sys
from 	time						import time
from 	threading 					import RLock
from 	infrastructure.timestamp 	import CoarseTimeStamp
from	infrastructure.flag			import Flag

class _TS_Counter:

	"""Thread-safe counter class. Can be accessed concurrently
		from multiple threads."""
	
	lock = RLock()		# Re-entrant lock for thread safety.
	_count = 0
	
	@classmethod
	def getSeqNo(thisClass):
		"""Returns the 'next' counter value, in sequence.
			Consistent across multiple threads."""
		with thisClass.lock:					# Acquire the mutex lock.
			curCount = thisClass._count			# Starts at 0.
			thisClass._count = curCount + 1		# Increments counter for next guy.
			return curCount						# Return orig. counter value.
	
class BufItem: pass

class BufItem:

	"""An item of buffered raw data to include in a stream buffer.
		Items are timestamped (with about +/- ~10 ms precision) and 
		assigned unique sequence numbers in the order of creation."""

	def __init__(newBufItem, data:str=None):
			# Get the next sequence number. Thread-safe.
		newBufItem._seqno = _TS_Counter.getSeqNo()	
			# Also store a rough timestamp for the item.
		newBufItem._timestamp = CoarseTimeStamp(time())
			# And of course, the actual data.
		newBufItem._data = data
			# Also make a note of its size.
		newBufItem._size = len(data)

	@property
	def seqno(thisBufItem:BufItem):
		return thisBufItem._seqno

	@property
	def timestamp(thisBufItem:BufItem):
		return thisBufItem._timestamp
	
	@property
	def data(thisBufItem:BufItem):
		return thisBufItem._data

	@property
	def size(thisBufItem:BufItem):
		return thisBufItem._size

class StreamBuf: pass

class StreamBuf:

	"""This class implements a simple buffer for output streams, with
		timestamping of buffered data, and mirroring of output.  The
		timestamping is useful to allowed the buffered data to be 
		interleaved with that from other streams (e.g. in the case
		of simulteanous 'normal' and 'error' streams).
		
		"Handler" methods may be installed to receive copies of 
		newly-buffered data.
		
		This class is not thread-safe, so you should not have multiple
		threads writing simultaneously to a given StreamBuf.
		"""
		
		# Eventually need to make this a configurable system parameter.
	_DEFAULT_MAX_SIZE = 10000		# By default, we buffer the last 10k bytes worth of data.
		
	def __init__(newStreamBuf):
		newStreamBuf._items = []	# Initially empty list of buffered data entries.
		newStreamBuf._size = 0		# Initialize content size to 0 bytes.
		newStreamBuf._handlers = []	# No data handlers installed initially.

	def addHandler(thisStreamBuf, handler:Callable):
		"""Adds a handler function to the list."""
		thisStreamBuf._handlers.append(handler)

	def removeHandler(thisStreamBuf, handler:Callable):
		thisStreamBuf._handlers.remove(handler)

	def _addItem(thisStreamBuf, item:BufItem):
		"""Adds a new item to the buffer, while keeping the total buffer 
			size in check. (The oldest items disappear as needed.)"""

		strmbuf = thisStreamBuf

		strmbuf._items.append(item)	# Adds the item.
			# Calculate new size of buffered data.
		strmbuf._size = strmbuf._size + item._size
			# This loop trims old items off the front as needed.
		while strmbuf._size > strmbuf._DEFAULT_MAX_SIZE:
				# Remember size of item we're about to remove.
			firstItemSize = strmbuf._items[0]._size
				# Remove it from the list.
			strmbuf._items.pop(0)	
				# Update buffer size.
			strmbuf._size = strmbuf._size - firstItemSize

	def addData(thisStreamBuf, data:str):
		"""Appends the given data to the end of the stream buffer."""
			# First, wrap up the data in a sequence-numbered, timestamped object.
		dataItem = BufItem(data)
			# Add the item to our internal buffer.
		thisStreamBuf._addItem(dataItem)
			# Now that it's safely stored, call each of our handlers on it.
		for handler in thisStreamBuf._handlers:
			handler(dataItem)


class VirOut:	# Virtual output-stream class.

	# Note this class does double duty; instances of it can be used to handle
	# either "normal" or "error" output streams by setting the isErr flag
	# appropriately.
	
	# TODO: Still need to implement methods for line-based readout of buffered data.

	def __init__(newVirOut, isErr:bool=False):
		"""If isErr=True then this is marked as an 'error' stream."""

			# Remember if this is marked as an error stream.
		newVirOut._isErr = isErr

			# Create and store a stream buffer to hold the data.
		newVirOut._buffer = StreamBuf()

			# Also open a file to copy error text to.
		if isErr:
			newVirOut._errFile = errFile = open('err.out', 'a')
			print("\n================================================================================\n",
				  file=errFile)
			print("STARTING NEW ERROR TRANSCRIPT:\n", file=errFile)
	
	def addHandler(thisVirOut, handler:Callable):
		thisVirOut._buffer.addHandler(handler)	# Delegate to buffer.
	
	def removeHandler(thisVirOut, handler:Callable):
		thisVirOut._buffer.removeHandler(handler)

		# write() method, expected by users of File objects.
	def write(thisVirOut, data):

		if data == "": return		# Empty strings are ignored and don't generate data records.

		# Also send data to error log file.
		if thisVirOut._isErr:
			thisVirOut._errFile.write(data)
			thisVirOut._errFile.flush()

		thisVirOut._buffer.addData(data)
    
		# flush() method, expected by users of File objects.
	def flush(newVirOut):
		pass


def _preserve_orig_stdio():
		# Before we actually reassign stdout/stderr streams to print to our
        # virterm, we first make sure we have a record of our original
        # stdout/stderr streams (if any), so we can restore them later if/when
        # the virterm shuts down.
    if sys.__stdout__ == None:          # If the default stdout is not already set (e.g. we're running under IDLE)
        sys.__stdout__ = sys.stdout         # Set it to our actual current stdout.
        
    if sys.__stderr__ == None:          # Likewise with stderr.
        sys.__stderr__ = sys.stderr
        
    if sys.__stdin__  == None:
        sys.__stdin__  = sys.stdin


def streamHandler(stream:StringIO):
	"""Given a (duck-typed) File object, returns an item handler
		method that just writes the item data to that file."""
	return lambda item: stream.write(item._data)


class Line: pass

class Line:
	
	"""An object of this class represents a single line within a
		LineBuffer."""

	def __init__(newLine:Line, text:str, seqno:int, isErr:bool):
		line = newLine
		line._text = text
		line._seqno = seqno
		line._isErr = isErr

	@property
	def text(thisLine:Line):
		return thisLine._text

	def setText(thisLine:Line, text:str):
		thisLine._text = text

	@property
	def seqno(thisLine:Line):
		return thisLine._seqno

	@property
	def isErr(thisLine:Line):
		return thisLine._isErr

class LineBuffer: pass

class LineBuffer:

	"""This class implements a sorted buffer for lines of text, in sequence
		order, with each line marked as to whether it is from a normal
		stream or an error stream.  It is used by VirTerm for assembling
		the interleaved, line-based combination of the virtual input and
		output streams.  It is thread-safe, so that we can add and remove
		lines from it safely from within multiple threads."""

	def __init__(newLineBuffer:LineBuffer):

		linebuf = newLineBuffer
		linebuf._lock = RLock()

		with linebuf.lock:
			linebuf._lines = []
			linebuf._outLine = None		# Non-error line being assembled.
			linebuf._errLine = None		# Error line being assembled.
			linebuf._hasData = Flag()	# This flag is raised when buffer has data.

	@property
	def hasData(thisLineBuffer:LineBuffer):
		return thisLineBuffer._hasData

	def addOut(thisLineBuffer:LineBuffer, outItem:BufItem):

		"""Adds a new output data item into the line buffer."""
		
		linebuf = thisLineBuffer

		seqno = outItem.seqno
		tstamp = outItem.timestamp
		data = outItem.data
		size = outItem.size

		# See if we've started assembling an output line; if not, do so.
		outLine = linebuf._outLine
		if outLine is None:
			linebuf._outLine = outLine = Line("", seqno, isErr=False)

		# Does the new data contain a newline? If so, then we can now
		# finish assembling an output line and adding it to the buffer.
		# If not, then the new data just gets appended to data present.

		nlpos = data.find('\n')

		if nlpos == -1:
			outLine.setText(outLine.text + data)	# Append new data.

		else:
			restLine = data[:nlpos+1]
			outLine.setText(outLine.text + restLine)
			linebuf.addLine(outLine)

			linebuf._outLine = Line(data[nlpos+1:], seqno, isErr=False)


	def addErr(thisLineBuffer:LineBuffer, errItem:BufItem):

		"""Adds a new error data item into the line buffer."""
		
		linebuf = thisLineBuffer

		seqno = errItem.seqno
		tstamp = errItem.timestamp
		data = errItem.data
		size = errItem.size

		# See if we've started assembling an output line; if not, do so.
		errLine = linebuf._errLine
		if errLine is None:
			linebuf._errLine = errLine = Line("", seqno, isErr=True)

		# Does the new data contain a newline? If so, then we can now
		# finish assembling an output line and adding it to the buffer.
		# If not, then the new data just gets appended to data present.

		nlpos = data.find('\n')

		if nlpos == -1:
			errLine.setText(errLine.text + data)	# Append new data.

		else:
			restLine = data[:nlpos+1]
			errLine.setText(errLine.text + restLine)
			linebuf.addLine(errLine)

			linebuf._errLine = Line(data[nlpos+1:], seqno, isErr=True)


	@property
	def lock(thisLineBuffer:LineBuffer):
		return thisLineBuffer._lock

	@property
	def lines(thisLineBuffer:LineBuffer):
		return thisLineBuffer._lines

	@property
	def nLines(thisLineBuffer:LineBuffer):
		return len(thisLineBuffer.lines)

	def setLines(thisLineBuffer:LineBuffer, newLines):
		thisLineBuffer._lines = newLines

	def addLine(thisLineBuffer:LineBuffer, newLine:Line):

		"""Inserts the given line into the line buffer, maintaining
			sequence number order."""

		linebuf = thisLineBuffer

		with linebuf.lock:

			linebuf = thisLineBuffer
			lines = linebuf.lines
			seqno = newLine.seqno

			pos = linebuf.nLines
			for i in range(0, len(lines)):
				if seqno < lines[i].seqno:
					pos = i
					break

			newLines = lines[:pos] + [newLine] + lines[pos:]
		
			linebuf.setLines(newLines)

				# Raises the "we have data" flag (if not already raised).
			linebuf.hasData.rise()	# Make the flag rise (go high).

	def popFirstLine(thisLineBuffer:LineBuffer):

		"""Removes and returns the first line from the line buffer,
			or returns None if the line buffer is currently empty."""

		linebuf = thisLineBuffer

		with linebuf.lock:
			
			if linebuf.nLines == 0:
				return None
		
			lines = linebuf.lines

			firstLine = lines[0]
			restLines = lines[1:]

			linebuf.setLines(restLines)

			# Lower our 'we have data' flag if we were just emptied out.
			if linebuf.nLines == 0:
				linebuf.hasData.fall()	# Make the flag fall (go low).

			return firstLine
	

class VirTerm: pass

class VirTerm:	# Virtual-terminal class.

	# Note: Still need to implement methods for line-based interleaving of streams.

	def __init__(newVirTerm:VirTerm):

		virterm = newVirTerm
		
		virterm._outVstrm = vout = VirOut()
		virterm._errVstrm = verr = VirOut(isErr = True)
		virterm._lineBuffer = LineBuffer()
		virterm._has_stdout = False
		virterm._has_stderr = False

		vout.addHandler(virterm.outHandler)
		verr.addHandler(virterm.errHandler)

	def popFirstLine(thisVirTerm:VirTerm):

		virterm = thisVirTerm
		linebuf = virterm._lineBuffer

		return linebuf.popFirstLine()

	@property
	def hasData(thisVirTerm:VirTerm):
		return thisVirTerm._lineBuffer.hasData

	def outHandler(thisVirTerm:VirTerm, outBufItem:BufItem):
		"""This is a handler method that we install in our output
			virtual stream to process normal output data items.
			It adds the item to our line buffer."""

		virterm = thisVirTerm
		linebuf = virterm._lineBuffer

		linebuf.addOut(outBufItem)

	def errHandler(thisVirTerm:VirTerm, errBufItem:BufItem):
		"""This is a handler method that we install in our output
			virtual stream to process error output data items.
			It adds the item to our line buffer."""

		virterm = thisVirTerm
		linebuf = virterm._lineBuffer

		linebuf.addErr(errBufItem)

	@property
	def out(thisVirTerm:VirTerm):
		return thisVirTerm._outVstrm

	@property
	def err(thisVirTerm:VirTerm):
		return thisVirTerm._errVstrm
	
	def grab_stdout(thisVirTerm, tee:bool=True):
		"""Redirects stdout to this virtual terminal."""
	
			# Remember orig. stdout.
		origStream 					= sys.stdout	
		thisVirTerm._orig_stdout	= origStream
		
			# If we're teeing to it, add a handler to do this.
		if tee:
			thisVirTerm._out_teehandler = tee_handler = streamHandler(origStream)
			thisVirTerm._outVstrm.addHandler(tee_handler)
		
			# OK, now redirect sys.stdout to our virtual stream guy.
		sys.stdout = thisVirTerm._outVstrm
		
			# Remember that we grabbed stdout.
		thisVirTerm._has_stdout = True
	
	def untee_out(thisVirTerm):
		if thisVirTerm._out_teehandler is not None:
			thisVirTerm._outVstrm.removeHandler(thisVirTerm._out_teehandler)
			thisVirTerm._out_teehandler = None

	def release_stdout(thisVirTerm):
		if thisVirTerm._has_stdout:
			sys.stdout = thisVirTerm._orig_stdout
			thisVirTerm._has_stdout = False
				
	def grab_stderr(thisVirTerm, tee:bool=True):
		"""Redirects stderr to this virtual terminal."""
	
			# Remember orig. stderr.
		origStream 					= sys.stderr
		thisVirTerm._orig_stderr	= origStream
		
			# If we're teeing to it, add a handler to do this.
		if tee:
			thisVirTerm._err_teehandler = tee_handler = streamHandler(origStream)
			thisVirTerm._errVstrm.addHandler(tee_handler)
		
			# OK, now redirect sys.stderr to our virtual stream guy.
		sys.stderr = thisVirTerm._errVstrm
		
			# Remember that we grabbed stderr.
		thisVirTerm._has_stderr = True

	def untee_err(thisVirTerm):
		if thisVirTerm._err_teehandler is not None:
			thisVirTerm._errVstrm.removeHandler(thisVirTerm._err_teehandler)
			thisVirTerm._err_teehandler = None

	def untee(thisVirTerm):
		thisVirTerm.untee_out()
		thisVirTerm.untee_err()

	def release_stderr(thisVirTerm):
		if thisVirTerm._has_stderr:
			sys.stderr = thisVirTerm._orig_stderr
			thisVirTerm._has_stderr = False
			
	def grab_stdin(thisVirTerm):
		pass	# Not yet implemented.
	
	def release_stdin(thisVirTerm):
		pass	# Not yet implemented.
	
	def grab_stdio(thisVirTerm, tee:bool=True):
		"""This tells the virTerm to grab control of STDIO, except
			that if 'tee=False' is not specified, stdout/stderr data
			is also still echoed to the original stdout/stderr, in 
			addition to being sent to the virTerm instance."""
		
			# Make sure there's a record of the default STDIO streams.
		_preserve_orig_stdio()
		
			# Now grab the three streams.
		thisVirTerm.grab_stdout(tee)
		thisVirTerm.grab_stderr(tee)
		thisVirTerm.grab_stdin()	# This does nothing yet.
	
	def release_stdio(thisVirTerm):
		"""Release control of stdio streams; i.e., they revert back to normal."""
		thisVirTerm.release_stdout()
		thisVirTerm.release_stderr()
		thisVirTerm.release_stdin()		# This does nothing yet.

	def dump_all(thisVirTerm):		# Dump everything to real stdout/stderr.
		virterm = thisVirTerm

		virterm.release_stdio()		# Make sure we're not still holding these.

		print("\n\n"
			  "============================================================\n"
			  "DUMPING VIRTERM LINES:\n"
			  "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
			  
		while virterm.hasData():
			line = virterm.popFirstLine()
			if line.isErr:
				print(line.text, end='', file=sys.stderr)
			else:
				print(line.text, end='')

		print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
			  "END VIRTERM DUMP\n"
			  "============================================================")
