# inputPanel.py

from time		import	sleep		# Causes thread to give up control for a period.  Used in BlinkTimer.
from os 		import 	path

from curses.ascii import (
		alt,	# Returns the meta (8th bit set) version of a key code.
	)

from infrastructure.logmaster import (
		sysName,			# Used just below.
		ThreadActor,		# Blink timer thread is subclassed from this.
		getComponentLogger 	# Used just below.
	)

global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component

from	display.keys	import (

		#-------------------------------
		# Special keys used for editing.

			# These ones are also normal ASCII A0 controls (& ASCII RUBOUT/DEL).
		KEY_BACKSPACE, KEY_TAB, KEY_LINEFEED, KEY_FORMFEED, KEY_RETURN, KEY_ESCAPE, KEY_DELETE,
		
			# These ones are found on the little keypad for special controls.
		KEY_HOME, KEY_END, KEY_DC, KEY_IC,	# KEY_DC = Del, KEY_IC = Ins.
		
			# Arrow keys.
		KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
		
			# Numeric keypad keys.
		KEY_ENTER,	# This is actually the same as KEY_LINEFEED, unfortunately.
			
			# Other "special" (synthesized) keys.
			
		KEY_IL, 	# Insert line.  Keycode synthesized from ^O = open new line at cursor.
		KEY_EOL,	# Delete to end of line.  Keycode synthesized from ^K = kill to end of line.

	)

from	display.panel	import (

		Panel,			# This is the base class from which we derive the InputPanel.
		LOWER_RIGHT		# This is the panel placement specifier we use for the input panel.
		
	)
	
from	entities.entity	import (

		Operator_Entity,	# An entity representing the console operator (human).

	)
	
from	events.event 	import (

		TextEvent,			# For an event representing the operator's text input.
		FullEventFormat,	
			# The format we use by default for displaying this text event in 
			# the inputPanel.  Includes the date/time and author (Operator).
		
	)

class PromptTimer: pass
class InputPanel: pass

class PromptTimer(ThreadActor):
	
	"""The purpose of this thread is to update the operator's prompt once
		per second with an updated time and date."""
	
	defaultRole = 'PromptTmr'
	defaultComponent = _sw_component
	
	def __init__(newPromptTimer:PromptTimer, inputPanel:InputPanel):
	
		timer = newPromptTimer
		timer._inputPanel = inputPanel
		timer._exitRequested = False

		timer.defaultTarget = timer._main
		super(PromptTimer, timer).__init__(daemon=True)	# ThreadActor initialization.
			# The daemon=True tells Python not to let this thread keep the process alive.
	
	@property
	def panel(thisPromptTimer:PromptTimer):
		return thisPromptTimer._inputPanel
	
	def _main(thisPromptTimer:PromptTimer):
		
		timer = thisPromptTimer		# Shorter name

		while not timer._exitRequested:

			# The prompt update cycle is 1 second.  Update time in prompt,
			# wait 1 second, update time in prompt again, etc.
		
			timer.updatePrompt()		# Update prompt with current time.
			
			sleep(1.0)			# Sleep for one second.
			
	def updatePrompt(thisPromptTimer:PromptTimer):
		timer = thisPromptTimer
		timer.panel.updatePrompt()	# Let the main Panel class do the work.
		

class InputPanel(Panel):

	"""Panel for prompting for and accepting input from the operator."""

	
	def __init__(newInputPanel:InputPanel):
			
		_logger.debug("inputPanel.__init__(): Initializing input panel.")

			# Use a shorter name for this new log panel.
		panel = newInputPanel
		
			# First we do general panel initialization.
		super(InputPanel, panel).__init__("Operator Input", LOWER_RIGHT, 4)
			# By default, the input panel appears at the bottom of the right column.
			# A default height of 4 for this panel is fine.  It can grow if needed.
		
			# Create and store the operator entity.
		operator = Operator_Entity()
		panel._operatorEntity = operator
		
			# Create and store the draft text input event.
		opTextEvent = TextEvent(chr(EOT), author=operator, defaultFormat=FullEventFormat)
			# Note the text of the event is just a single End-Of-Text (^C) character initially.
			# It will expand as the operator types text in the box.
		panel._opTextEvent = opTextEvent	# Operator's text event.
			
			# Create the prompt timer thread (see above).
			# Its job will be to update the time displayed in the
			# operator's input prompt.
		timerThread = PromptTimer(panel)
		panel._promptTimer = timerThread
		
			# Grab the keyboard focus.
		panel.grabFocus()

	#__/ End instance initializer method inputPanel.__init__().


	def updatePrompt(thisInputPanel:InputPanel):
		
		panel	= thisInputPanel
		client	= panel.client
		display	= client.display
		driver	= display.driver
		event	= panel.textEvent
		
		event.updateTime()			# Tell the text event to update its creation time.
		
		# At this point, we actually want the new time to be visible, so we go
		# ahead and tell this panel to update its display, in the driver thread.
		
		driver(panel.redisplayContent, desc="Redisplay input panel contents with new time.")


	@property
	def textEvent(thisInputPanel:InputPanel):
		panel = thisInputPanel
		return panel._opTextEvent

	@property
	def text(thisInputPanel:InputPanel):
		panel = thisInputPanel
		return panel.textEvent.text

	def setText(thisInputPanel:InputPanel, text:str=None):
		
		panel = thisInputPanel
		client	= panel.client
		display	= client.display
		driver	= display.driver
		
		textEvent = panel.textEvent
		textEvent.text = text
		
		driver(panel.redisplayContent, desc="Redisplay input panel contents with new text.")
			# Update the panel display.

	def promptLen(thisInputPanel:InputPanel):
		panel 		= thisInputPanel
		textEvent	= panel.textEvent
		promptLen	= textEvent.promptLen()
		

	def launch(thisInputPanel:InputPanel):
	
		"""This standard Panel method is called automatically by the Panel 
			to start up any associated threads at the time of first display.  
			In our case, we use it to start the prompt-update timer."""
		
		_logger.debug("inputPanel.launch(): Starting the prompt timer thread.")
		thisInputPanel._promptTimer.start()
		
	#__/ End instance method inputPanel.launch().
	
	
	def drawContent(thisInputPanel:InputPanel):
	
		"""This standard Panel method is called automatically when the panel's
			content needs to be redrawn.  The context is that the window's 
			display buffer has already been erased, and that the screen will
			be refreshed sometime after this method returns.
		
			For the input panel, the behavior is simply to display the input
			text event being constructed.
		"""
		
		panel	= thisInputPanel
		client	= panel.client
		display	= client.display
		win 	= panel.win		
			# This is the panel's internal window, for displaying content.
			# It already has appropriate padding around it.
		
			# Get the text event, to display in the panel.
		textEvent = panel.textEvent
		
			# Get the displayable text representing that event.
		displayText = textEvent.display()	# Uses event's default format.
		
			# Sweet; now have the display render it in the window.
		(yx2pos, pos2yx) = display.renderText(displayText, win=win)
			# Note this method does special stuff with various control
			# and whitespace characters. The return values map screen
			# locations to positions in the string.
		panel._yx2pos = yx2pos
		panel._pos2yx = pos2yx

		# Sync the cursor position upwards in window hierarchy.
		win.cursyncup()

			# Call the original drawContent() method in Panel, which does 
			# some general bookkeeping work needed for all panels.
		super(InputPanel, panel).drawContent()
			
	#__/ End instance method inputPanel.drawContent().


	@property
	def yx2pos(thisInputPanel:InputPanel):
		return thisInputPanel._yx2pos

	@property
	def pos2yx(thisInputPanel:InputPanel):
		return thisInputPanel._pos2yx


	def handle(thisInputPanel:InputPanel, keyEvent:KeyEvent):
	
		"""This standard panel method handles an input key event
			that is dispatched to the panel when it has the keyboard
			focus.  The implementation of this method in InputPanel 
			facilitates text entry and editing."""

		panel = thisInputPanel
		event = keyEvent
		
		keycode	= keyevent.keycode
		keyname	= keyevent.keyname
		ctlname	= keyevent.ctlname

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	Special editing keys are as follows:
		#|
		#|		Ctrl-A, Home		- Go to leftmost editable column in row.
		#|		Ctrl-B, Left		- Move cursor left, with wrapping if appropriate.
		#|		Alt-B, Ctrl-Left	- Move cursor to start of previous word.
		#|		Ctrl-D, Del			- Delete character under cursor.
		#|		Ctrl-Del			- Delete to end of word under cursor.
		#|		Ctrl-E, End			- Go to rightmost editable column in row.
		#|		Ctrl-F, Right		- Move cursor right, with wrapping if appropriate.
		#|		Alt-F, Ctrl-Right	- Move cursor to start of next word.
		#|		Ctrl-H, Backspace	- Delete character to the left.
		#|		Ctrl-J, Return		- Insert newline (LF).
		#|		Ctrl-K				- Delete to end of line.
		#|		Ctrl-N, Down		- Move down one line to an editable character.
		#|		Ctrl-O				- Insert newline, but leave cursor where it is.
		#|		Ctrl-P, Up			- Move up one line to an editable character.
		#|		Ctrl-U				- Clear all input.
		#|		KP_Enter			- Enter on keypad.  Send text as an action.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		if keycode == KEY_HOME or keycode == KEY_BEG:		# ^A also maps to this.
			panel.keyHome()
			
		elif keycode == KEY_LEFT:		# ^B also maps to this.
			panel.keyLeft()
			
		elif keycode == alt(ord('b')) or keycode == KEY_CTRL_LEFT:
			panel.keyLeftWord()
			
		elif keycode == KEY_DELETE or keycode = KEY_DC:		# ^D also maps to this, also Del.
			panel.keyDelete()
			
		elif keycode == alt(ord('d')):	# We would like to accept Ctrl-Del for this also but we don't have a keycode for it yet.
			panel.keyDeleteWord()
			
		elif keycode == KEY_END:		# ^E also maps to this.
			panel.keyEnd()
			
		elif keycode == KEY_RIGHT:		# ^F also maps to this.
			panel.keyRight()
			
		elif keycode == alt(ord('f')) or keycode == KEY_CTRL_RIGHT:
			panel.keyRightWord()
			
		elif keycode == KEY_BACKSPACE:	# ^H also maps to this.
			panel.keyBackspace()
			
		elif keycode == KEY_RETURN or keycode == KEY_ENTER:		# ^J (KEY_LINEFEED) also maps to KEY_ENTER.
			panel.keyEnter()
			
		elif keycode == KEY_EOL			# ^K also maps to this.
			panel.keyKillToEOL()
			
		elif keycode == KEY_DOWN:		# ^N also maps to this.
			panel.keyDown()
			
		elif keycode == KEY_IL or keycode == KEY_IC:	# ^O also maps to this, and also Ins.
			panel.keyInsertLine()
			
		elif keycode == KEY_UP:			# ^P also maps to this.
			panel.keyUp()
			
		elif keycode == KEY_CLEAR:		# ^U also maps to this.
			panel.keyClear()
		
		# All other keys are just self-inserting by default.
		else:
			panel.insertKey(event)
		
		#__/ End if/elif/else block for keycode-based event dispatching.
		
	#__/ End instance method panel.handle().

	def _adjustPos(thisInputPanel:InputPanel):
		"""This method adjusts the cursor position as needed to make
			sure it's in a valid location."""

		panel		= thisInputPanel
		win			= panel.win
		
		(cy, cx) = win.getyx()		# Get current cursor position.
		
			#-------------------------------------------------
			# First, make sure the cursor's in a position that 
			# actually maps to one of the characters in the 
			# panel text.  If not, keep moving it back till it is.
			
		while not (cy, cx) in panel.yx2pos:
			if cx > 0:
				cx = cx - 1
			else:
				if cy > 0:
					cy = cy - 1
					(height, width) = win.getmaxyx()
					cx = width - 2
				else:
					_logger.warn("inputPanel._adjustPos(): No valid data back to (0,0).")
					return
		
			# Now get the corresponding position in the text.
		pos = panel.yx2pos[(cy, cx)]
		
			# Now we have to make sure the position isn't inside the prompt.
		promptLen = panel.promptLen()
		if pos < promptLen:
			pos = promptLen
			
			# Now convert the position back to cursor coordinates, and move the cursor there.
		(cy, cx) = panel.pos2yx[pos]
		win.move(cy, cx)
		win.cursyncup()

	def cursorPos(thisInputPanel:InputPanel):
		
		"""Returns the current cursor's position in the text."""
		
		panel	= thisInputPanel
		win		= panel.win
		
		panel._adjustPos()			# Make sure cursor position is OK.
		(cy, cx) = win.getyx()		# Get current cursor position.
		
			# Now get the corresponding position in the text.
		pos = panel.yx2pos[(cy, cx)]
		
		return pos

	def insertKey(thisInputPanel:InputPanel, event:KeyEvent):
		
		"""Inserts the given keypress at the current cursor position."""
		
		panel	= thisInputPanel
		pos		= panel.cursorPos()			# Get (valid) current position in text.
		txpos	= pos - panel.promptLen()	# Adjust for length of prompt.
		text	= panel.text
		keycode = event.keycode				# Numeric keycode for current key.
		char	= chr(keycode)				# Convert code to a character.
		
		# This inserts the character at the text position.
		text = text[:txpos] + char + text[txpos:]
		
		# Update the panel's text (this also updates the display).
		panel.setText(text)

	def keyHome(thisInputPanel:InputPanel):
		"""This method handles the 'Home' key, and also ^A = go to start of line.
			It moves the cursor to the leftmost editable column in the current row."""
		pass
	
	def keyLeft(thisInputPanel:InputPanel):
		"""This method handles the left arrow key, and also ^B = go back one character.
			It moves the cursor to one position earlier in the text."""
		pass
	
	def keyLeftWord(thisInputPanel:InputPanel):
		"""This method handles control-left arrow, and also Alt-B = go back one word.
			It moves the cursor to the start of the previous word."""
		pass
	
	def keyDelete(thisInputPanel:InputPanel):
		"""This method handles the 'Delete' key, and also ^D = delete character under cursor.
			It deletes the character under the cursor."""
		pass
	
	def keyDeleteWord(thisInputPanel:InputPanel):
		"""This method handles control-delete (maybe), and also Alt-D = delete word.
			It deletes the word under the cursor."""
		pass
	
	def keyEnd(thisInputPanel:InputPanel):
		"""This method handles the 'End' key, and also ^E = go to end of line.
			It moves the cursor to the rightmost editable column in the current row."""
		pass
	
	def keyRight(thisInputPanel:InputPanel):
		"""This method handles the right arrow key, and also ^F = go forward one character.
			It moves the cursor to one position later in the text."""
		pass

	def keyRightWord(thisInputPanel:InputPanel):
		"""This method handles control-right arrow, and also Alt-F = go forward one word.
			It moves the cursor to the start of the next word."""
		pass
	
	def keyBackspace(thisInputPanel:InputPanel):
		"""This method handles the Backspace key, and also ^H = BS.
			It deletes the character to the left of the cursor."""
		pass
	
	def keyEnter(thisInputPanel:InputPanel):
		"""This method handles the Return (^M) and Enter keys, and also ^J = LF.
			It inserts a newline (LF) before the cursor."""
		pass
	
	def keyKillToEOL(thisInputPanel:InputPanel):
		"""This method handles the EOL key, and also ^K = Kill to End of Line.
			It deletes the remainder of the current line of text, from the cursor to EOL (LF)."""
		pass
	
	def keyDown(thisInputPanel:InputPanel):
		"""This method handles the down arrow key, and also ^N = go to next line.
			It moves the cursor down one line to an editable character."""
		pass
	
	def keyInsertLine(thisInputPanel:InputPanel):
		"""This method handles the Ins key, and also ^O = insert line at cursor.
			It inserts a newline character at the current cursor position."""
		pass
	
	def keyUp(thisInputPanel:InputPanel):
		"""This method handles the Up arrow key, and also ^P = go to previous line.
			It moves the cursor up one line to an editable character."""
		pass
	
	def keyClear(thisInputPanel:InputPanel):
		"""This method handles the Clear key, and also ^U = undo all typing.
			It clears all the text that has been typed."""
		pass

#__/ End class InputPanel.

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					END OF FILE:	console/inputPanel.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%