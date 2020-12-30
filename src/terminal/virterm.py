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
#|			the original streams; this allows early diagnostics
#|			to be captured and then re-displayed in a console
#|			sub-window after the server is started up.
#|
#|		

from 	typing						import Callable
import	sys
from 	time						import time
from 	threading 					import RLock
from 	infrastructure.timestamp 	import CoarseTimeStamp

class _TS_Counter:
	"""Thread-safe counter class. Can be accessed concurrently
		from multiple threads."""
	
	RLock lock		# Re-entrant lock for thread safety.
	_count = 0
	
	@classmethod
	def getSeqNo(thisClass):
		"""Returns the 'next' counter value, in sequence.
			Consistent across multiple threads."""
		with thisClass.lock:					# Acquire the mutex lock.
			curCount = thisClass._count			# Starts at 0.
			thisClass._count = curCount + 1		# Increments counter for next guy.
			return curCount						# Return orig. counter value.
	
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
		newStreamBuf._handlers.add(handler)

	def _addItem(thisStreamBuf, item:BufItem):
		"""Adds a new item to the buffer, while keeping the total buffer 
			size in check. (The oldest items disappear as needed.)"""
		newStreamBuf._items.add(item)	# Adds the item.
			# Calculate new size of buffered data.
		newStreamBuf._size = newStreamBuf._size + item._size
			# This loop trims old items off the front as needed.
		while newStreamBuf._size > _DEFAULT_MAX_SIZE:
				# Remember size of item we're about to remove.
			firstItemSize = newStreamBuf._items[0]._size
				# Remove it from the list.
			newStreamBuf._items.pop(0)	
				# Update buffer size.
			newStreamBuf._size = newStreamBuf._size - firstItemSize

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
	
	def addHandler(newVirOut, handler:Callable):
		newVirOut._buffer.addHandler(handler)	# Delegate to buffer.
	
		# write() method, expected by users of File objects.
	def write(newVirOut, data):
		if data == "": return		# Empty strings are ignored and don't generate data records.
		newVirOut._buffer.addData(data)
    
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

def streamHandler(stream:File):
	"""Given a (duck-typed) File object, returns an item handler method that writes to that file."""
	return lambda item: stream.write(item._data)

class VirTerm:	# Virtual-terminal class.

	# Note: Still need to implement methods for line-based interleaving of streams.

	def __init__(newVirTerm):
		newVirTerm._outVstrm = VirOut()
		newVirTerm._errVstrm = VirOut(isErr = True)
	
	def grab_stdout(thisVirTerm, tee:bool=True):
		"""Redirects stdout to this virtual terminal."""
	
			# Remember orig. stdout.
		origStream 					= sys.stdout	
		thisVirTerm._orig_stdout	= origStream
		
			# If we're teeing to it, add a handler to do this.
		if tee:
			thisVirTerm._outVstrm.addHandler(streamHandler(origStream))
		
			# OK, now redirect sys.stdout to our virtual stream guy.
		sys.stdout = thisVirTerm._outVstrm
		
			# Remember that we grabbed stdout.
		thisVirTerm._has_stdout = True
	
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
			thisVirTerm._errVstrm.addHandler(streamHandler(origStream))
		
			# OK, now redirect sys.stderr to our virtual stream guy.
		sys.stderr = thisVirTerm._errVstrm
		
			# Remember that we grabbed stderr.
		thisVirTerm._has_stderr = True

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
			that if 'tee=False' is not provided, stdout/stderr data
			is also still echoed to the original stdout/stderr, in 
			addition to being sent to the virTerm instance."""
		
			# Make sure there's a record of the default STDIO streams.
		_preserve_orig_stdio()
		
			# Now grab the three streams.
		thisVirTerm.grab_stdout()
		thisVirTerm.grab_stderr()
		thisVirTerm.grab_stdin()	# This does nothing yet.
	
	def release_stdio(thisVirTerm):
		"""Release control of stdio streams; i.e., they revert back to normal."""
		thisVirTerm.release_stdout()
		thisVirTerm.release_stderr()
		thisVirTerm.release_stdin()		# This does nothing yet.
