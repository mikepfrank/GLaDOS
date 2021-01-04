# threads.py - Special threads associated with the display.

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


