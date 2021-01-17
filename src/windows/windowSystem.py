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

from collections.abc 	import Iterable
from os 				import path

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

from infrastructure.utils import overwrite

			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	config.configuration		import	TheConfiguration
	# We need this to get configuration parameters for the window system.

from 	text.buffer					import	TextBuffer
	# We use text buffers for both window contents and window images.

from	field.placement				import	Placement
	# This is an enum type that we use for specifying window placement.

from	field.fieldElement			import	WindowElement
	# This is a field element that lets us put windows onto the field.

from	field.receptiveField		import	TheReceptiveField
	# We access this singleton from window.openWin() so that we can
	# actually place newly-opening windows onto the receptive field.

from 	commands.commandInterface	import	CommandModule
	# We're going to extend CommandModule with various subclasses 
	# specific to the windowing system.

from 	processes.processSystem		import	SubProcess

	# We don't need to create applications from this module, so no need
	# to actually import the real Application_ class.
#from apps.appSystem				import	Application_
class Application_: pass	# Do this instead to avoid circular imports.

	#|==========================================================================
	#|
	#|	 2. Globals												  [code section]
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
		'TheWindowSystem',			# A singleton class for the entire window subsystem of GLaDOS.
	]


	#|==========================================================================
	#|
	#|	3. Classes.												  [code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


# Window system classes:
#
#		TextBuffer				- An adjustable-sized buffer of text spooled to the window.
#		Window					- A text window within the GLaDOS window system.
#		Windows					- A collection of text windows.
#		WindowSnapshot			- A static image of a text window at a given point in time.
#		TheWindowSystem			- The entire window subsystem in a given GLaDOS system instance.

class Window: pass	# Forward declaration

class WindowImage:
	
	"""A rendered image of a text window. This is also a text buffer,
		with decorations at the top and bottom (and maybe also the side)."""
		
	def __init__(self, win:Window, imgHt:int, imgWd:int = None):
		
		self._window		= win
		self._imageHeight	= imgHt
		
			# Create the text buffer to hold the window image.	Initially, 
			# we set the buffer height to the image size, and don't set any
			# maximum width.
		self._textBuffer	= TextBuffer(maxLen = imgHt, maxWid = imgWd)
		
			# Paint the window image in our text buffer.
		self.repaint()
		
	#__/ End windowImage.__init__().
	
	def view(self):
		
		"""Returns a 'view' of this window image, which simply means,
			a single text string that renders the entire visual
			appearance of the window image."""

		winView = self._textBuffer.view()
		return winView + '\n'
			# Add final newline because textbuffer doesn't by default.

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
		"""Adds a line to the window image. Differs from .addText()
			in that we ensure that there's a newline at the end."""
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
		
	def resize(self, size:int):
		"""Resize the viewport to the given size."""
		self._size = size
		self.update()

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

		#|------------------------------------------------------------------
		#| Class constant data members 						 [class section]
		#|
		#|		These constants provide default values of various
		#|		parameters for the class. Eventually these should
		#|		maybe be settable by config parameters / settings.

	_DEFAULT_WINDOW_DECORATOR_ROWS	= 2		# By default, just one line top, and one line bottom.
	_DEFAULT_WINDOW_DECORATOR_WIDTH = 60	# Sixty columns of fixed-width text characters.
	_DEFAULT_WINDOW_VIEW_ROWS 		= 15	# By default, display 15 rows worth of content initially.
	_DEFAULT_LEFT_DECORATOR_STRING	= '| '	# Vertical bar and one space of interior padding.
	_DEFAULT_RIGHT_DECORATOR_STRING = ' |'  # One space of interior padding, and a vertical bar.

		#|------------------------------------------------------------------
		#| Class variable data members 						 [class section]
		#|
		#|		These class variables provide the current values of
		#|		various parameters for the class.  These affect newly
		#|		created instances, or properties that are the same 
		#|		for all instances.
	
	_decoratorRows	= _DEFAULT_WINDOW_DECORATOR_ROWS
	_decoratorWidth	= _DEFAULT_WINDOW_DECORATOR_WIDTH
	_viewRows		= _DEFAULT_WINDOW_VIEW_ROWS
		# By default, view the default number of rows (15).
	_leftDecoratorStr  = _DEFAULT_LEFT_DECORATOR_STRING
	_rightDecoratorStr = _DEFAULT_RIGHT_DECORATOR_STRING

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
	
	def __init__(self, 					# The window that's being initialized.

			title="Untitled Window",
				 # REQUIRED. Callers should *always* override this default.

			app:Application_=None,
				 # OPTIONAL. The application controlling this window (if any).

			placement:Placement=None,
				 # REQUIRED. Where this window should be placed in the
				 # receptive field when first opened.
				 
			textBuf:TextBuffer=None,
				 # OPTIONAL. Existing text buffer to use for window contents
				 # (if None, a new one is created).
				 
			isActive=False,
				 # OPTIONAL. Is this the currently active window? By default, not yet.
				 
			process:SubProcess=None,
				 # OPTIONAL. Existing subprocess whose I/O will go in this window.
				 # By default, none yet.
				 
			state:str='closed',
				 # OPTIONAL. Initial state of window. Normally all windows start closed,
				 # and are opened later. (Other states may include: 'minimized', 'maximized'.)

			viewSize=None,
				 # OPTIONAL. Initial view size within window, in rows. Default is 15.
				 
			stayVisible:bool=False,
				 # OPTIONAL. Whether the window should try to stay visible
				 # in the receptive field. (This means, if it floats to the

				 # top of the receptive field, it sticks and gets anchored there.)
		):
	
		win = self
		
		win._isOpen	  = False	# New windows aren't initially open.

		win._wordWrap = False	# No word-wrapping by default.
		win._autoSize = False	# No auto-sizing by default.

			#---------------------------------------------------------------------
			# Before doing anything else, we get some preferences from the window system
			# that apply to all newly-created windows in the system.

		winSys = TheWindowSystem()		# Get the sole instance of this singleton.

		self._hasSideBorders = sideBorders = winSys.useSideDecorators
			# This tells us whether to display the window with left-right borders.

		# If the window has side borders, then this means that its entire image
		# should have a fixed width that is the same as the width of its top &
		# bottom decorators.  Otherwise, it should have no fixed width.
		if sideBorders:
			imageWidth = self._decoratorWidth
		else:
			imageWidth = None
		self._imageWidth = imageWidth

		# If the window has side borders and a fixed image width, then it should
		# have a fixed content width that is equal to its image width minus enough
		# space for the interior padding and borders.
		if sideBorders and imageWidth is not None:
			contentWidth = imageWidth - len(self._leftDecoratorStr) - len(self._rightDecoratorStr)
		else:
			contentWidth = None		# No limit on window content width by default.
		self._contentWidth = contentWidth

		_logger.info(f"Creating window '{title}' with image width = {imageWidth}, content width = {contentWidth}.")

			#-----------------------------------------------------------
			# A window automatically creates a text buffer to hold its 
			# contents when it is first created, if one wasn't supplied.
	
		if textBuf is None:
			textBuf = TextBuffer(maxWid = contentWidth)

		if viewSize is None:
			viewSize = self._viewRows	# This is actually a class-level data member.

		self._title			= title
			# This gets displayed in the top decorator of the window image when it is rendered.
			
		self._app			= app
			# We reference this when general window commands need to
			# talk to the window's underlying app (e.g. to terminate it).
			
		self._placement		= placement
			# This gets used when the window is opened & placed on the field.
			
		self._textBuffer	= textBuf
			# All window content will get stored here, & it will be consulted
			# for displaying the view.
			
		self._isActive		= isActive		
		self._process		= process
		self._state			= state
		self._viewSize		= viewSize
		self._stayVisible	= stayVisible
	
		self._commandModule	= WindowCommandModule(self)

		self._viewPort		= ViewPort(self, self._viewSize)
		self._viewPos		= 0		# Window is initially viewing the top of its text buffer.

			# Create the window's image.

		self._image			= None	# No image initially--but we'll make one right now!
		self.createImage()

		self._snapshots		= set()

		self._fieldElem		= None
			# This is a "field element" object to contain this window.

	def createImage(win):
		"""Creates this winow's image. Any previous image is discarded."""

		viewSize = win._viewSize
		decRows = win._decoratorRows
		imgWidth = win._imageWidth

			# Create a window image of the appropriate dimensions.
		image = WindowImage(win, viewSize + decRows, imgWidth)
			# Note that we make room for the top/bottom decorators.

		win._image = image

	def checkSize(win):

		"""If we're in auto-resize mode, then, if needed, resize
			the window to fit the current size of its content."""

		if win.autoSize:
			win.resizeToFitContent()

	def resizeToFitContent(win):
		
		"""This method causes the window to resize itself to fit the
			current size of its content buffer."""

		curViewSize = win._viewSize		# Get current size of window's view in rows.

		nContentRows = win._textBuffer.nRows()	# Get number of rows of content.
		
		if nContentRows != curViewSize:

			# Change our view size to match the number of rows of content.
			win._viewSize = viewSize = nContentRows

			# Resize our viewport to match the new view size.
			win._viewPort.resize(viewSize)
		
			# Re-create the window's image from scratch.
			win.createImage()

			# Re-display the window on the receptive field.
			win.redisplay()

	@property
	def wordWrap(thisWin):
		return thisWin._wordWrap

	@wordWrap.setter
	def wordWrap(thisWin, newValue:bool):
		_logger.debug(f"Setting word-wrapping on window 'thisWin.title' to {newValue}")
		thisWin._wordWrap = newValue
			# Also relay this setting to our text buffer.
		thisWin._textBuffer.wordWrap = newValue

	@property
	def autoSize(thisWin):
		return thisWin._autoSize

	@autoSize.setter
	def autoSize(thisWin, newValue:bool):
		_logger.debug(f"Setting auto-sizing on window 'thisWin.title' to {newValue}")

		oldValue = thisWin.autoSize

		thisWin._autoSize = newValue

		# If auto-sizing is newly turned on, then go ahead and resize the window.
		if newValue and not oldValue:
			thisWin.resizeToFitContent()

	@property
	def title(thisWin):
		return thisWin._title

	@property
	def placement(thisWin):
		return thisWin._placement

	@property
	def image(thisWin):
		return thisWin._image

	def view(thisWin):
		"""Gets a 'view' of this window as a single text string."""
		image = thisWin.image	# Get this window's image structure.
		viewTxt = image.view()	# Convert it to a single text string.
		return viewTxt			# And return that.

	def openWin(thisWin):

		"""Tells the window to actually open itself up on the receptive field,
			if not already open."""
		
		win		= thisWin
		field	= TheReceptiveField()	# Gets the singleton instance.

			# Create a field element to contain this window.
		wElem = WindowElement(field, win)
				# This will automatically place itself on the field.
				# Add that will automatically update the field view.
		
			# Remember that we have opened this windo.
		win._isOpen = True

			# Tell the field that this is a good time for it to
			# notify its viewers that its contents have changed.
			# This will then update the console's field display,
			# and the field displays of any other connected user
			# terminals, and will also notify the AI's mind (if
			# running) that the field has changed, which should
			# wake up the AI (if sleeping) and give it a chance
			# to respond to the new field contents.

		win.redisplay()
		
	
	def addText(self, text:str):
		"""Add the given text to the window contents (at the end)."""
	
			# First, add the text to the end of our internal buffer.
		self._textBuffer.addText(text)
		
			# Update our viewport (in case we're following the bottom of the text).
		self._viewPort.update()
		
			# Now, ask our window image to repaint itself.
		self._image.repaint()

			# Also, check whether an auto-resize is needed.
		self.checkSize()
	
	def addLine(self, line:str):
		"""Add the given single line of text to the window contents (at the end)."""
		
			# First, add the line to the end of our internal buffer.
		self._textBuffer.addLine(line)
		
			# Update our viewport (in case we're following the bottom of the text).
		self._viewPort.update()
		
			# Now, ask our window image to repaint itself.
		self._image.repaint()
	
			# Also, check whether an auto-resize is needed.
		self.checkSize()
	
	def render(self):
		"""Render this window in its image. Assumes image is initially clear."""
		self.renderTopDecorator()
		self.renderContents()
		self.renderBotDecorator()	# Render the decorator at the bottom of the window.
	
	def renderText(self, text:str):
		self._image.addText(text)

	def renderLine(self, line:str):
		"""Renders a line to this window's image. Differs from .renderText()
			in that we ensure that there's a newline at the end of what's added."""
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
		topDecStr = '/' + horizEdgeChar*(Window._decoratorWidth - 2) + '\\'
		
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

		# If this window does not have side borders, then this is extremely
		# easy: We simply add the content view as raw text to the image.
		# However, if this window does have side borders, we have to do
		# more work, putting together each line using appropriate side
		# border decorators.

		if self._hasSideBorders:

			vp = self._viewPort

			topRow = vp._topPos
			botRow = vp._botPos

			# The following is a blank "template" consisting of a blank line filled
			# with spaces in between the side decorators.  We're overwrite part with the
			# actual contents of each line.
			blankLine = self._leftDecoratorStr + ' '*self._contentWidth + self._rightDecoratorStr
			startPos = len(self._leftDecoratorStr)

			for rowIndex in range(topRow, botRow):

				line = self._textBuffer.getLine(rowIndex, nlTerminated=False)
					# Gets the raw line from the buffer, without a newline.
			
				if line is None:	# Could happen if content buffer is empty, say.
					line = ''

					# Now fill those contents into our blank template.
				filledLine = overwrite(blankLine, startPos, line)

					# Adds this 'filled-in' line with borders to the window image.
				self.renderLine(filledLine)

		else:
			# No side borders, we can just display the raw text in the window view.
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
		botDecStr = '\\' + horizEdgeChar*(Window._decoratorWidth - 2) + '/'
		
			# If the window is active, we'll superimpose a command menu on it:
		if self._isActive:
		
				# Generate a string for the command menu.
			menuStr = ' ' + 'Window Commands: ' + self._commandModule.menuStr() + ' '
			
				# How long is it?
			menuStrLen = len(menuStr)
		
				# Where are we going to put it?	 Center it... (Rounding down.)
			menuStrLoc = int((Window._decoratorWidth - menuStrLen)/2)
		
				# OK, now paint it there (overwriting what was there initially).
			botDecStr = overwrite(botDecStr, menuStrLoc, menuStr)
			#botDecStr = botDecStr[0:menuStrLoc] + menuStr + botDecStr[menuStrLoc+menuStrLen:]
		#__/ End if window active.
			
		self.renderText(botDecStr)

	#__/ End method window.renderBotDecorator().

	def redisplay(win:Window):
		"""Advises the window to re-display itself on the receptive field 
			(if it's supposed to be visible)."""
		# If the window is currently open, then tell the field to update its view.
		if win._isOpen:
			TheReceptiveField().updateView()
		
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
class TheWindowSystem:

	# The TheWindowSystem has:
	#		- Various window-system-wide preferences.
	#		- Set of all windows in the system.
	#		- Reference to the currently-active window, if any.
	#		- List of windows present in the receptive field.
	#		- List of windows anchored to the top of the receptive field.
	#		- List of windows anchored to the bottom of the receptive field
	#			(usually there is just one, the presently active window).

	def __init__(self):

		sysConf = TheConfiguration()	# Get the system configuration.

		self._useSideDecorators = sysConf.sideDecorators
			# Boolean: Whether window images should include side decorators or not.

		self._windows = Windows()
			# This creates the window set (initially empty).

	@property
	def useSideDecorators(winSys):
		return winSys._useSideDecorators
	
