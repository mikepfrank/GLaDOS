
global windowSystem		# The last one initialized.
windowSystem = None

class TextBuffer:	# A text buffer.

	# A text buffer has:
	#	- A maximum length in rows.
	#	- A list of lines of text.
	
	def __init__(self, maxLen:int = 100):
		self._maxLen = maxLen
		self._rows = None		# Buffer is empty initially. No row data.
	
	def addText(self, text:str = None):
		pass


class Window:	# A text window within the GLaDOS window system.

	# A window has:
	#	- A title (textual label).
	#	- A text history buffer.
	#	- A list of snapshots.
	#	- Whether it is the currently active window.
	#	- An associated process.
	#	- Its state (open, minimized, or closed)
	#	- Its current size (number of lines to view)
	#	- Whether it is trying to stay in the receptive field
	#	- Whether it anchors to the top or bottom of the receptive field or is gloating.
	
	def __init__(self):
		self._snapshots = []

class Windows:
	def Windows(self):
		self._windowList = []

class WindowSnapshot:	# A static image of a text window at a given point in time.

	# A snapshot has:
	#	- A text history buffer.
	#	- The window it's a snapshot of.
	#	- The time it was taken.
	#	- Its location in the text stream.
	#	- Its state (open or minimized).
	#	- Its current size (number of lines to inspect).
	
	pass
	
class WindowSystem:

	# The WindowSystem has:
	#	- Set of all windows in the system.
	#	- List of windows present in the receptive field.
	#	- List of windows anchored to the top of the receptive field.
	#	- List of windows anchored to the bottom of the receptive field (usually there is just one, the presently active window).

	def __init__(self):
		self._windows = Windows()

class WindowSystemInitializer:
	def __init__(self):
		windowSystem = WindowSystem()
		self.windowSystem = windowSystem


# Window system classes:
#
#	TextBuffer			- An adjustable-sized buffer of text spooled to the window.
#	Window				- A text window within the GLaDOS window system.
#	Windows				- A collection of text windows.
#	WindowSnapshot		- A static image of a text window at a given point in time.
#	WindowSystem				- The entire window subsystem in a given GLaDOS system instance.
#	WindowSystemInitializer		- Initializer class for the window system.


