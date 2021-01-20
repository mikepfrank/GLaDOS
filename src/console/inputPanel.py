# inputPanel.py

from time		import	sleep		# Causes thread to give up control for a period.  Used in BlinkTimer.
from os 		import 	path

from curses.ascii import (
		
		SOH,	# ^A = Start of line. (Start of Heading)
		STX,	# ^B = Move back to the left. (Start of Text)
		ETX,	# ^C = We use this to terminate the input string. (End of Text)
		EOT,	# ^D = Delete character. (End-of-Transmission)
		ENQ,	# ^E = End of line. (Enquiry.)
		ACK,	# ^F = Forward to the right. (Acknowlegement)
		BS,		# ^H = Delete to the left. (Backspace)
		LF,		# ^J = Insert newline. (Line Feed)
		VT,		# ^K = Kill to end of line. (Vertical Tab)
		FF,		# ^L = Let's refresh the display. (Form Feed)
		CR,		# ^M = Insert carriage return. (Carriage Return)
		SO,		# ^N = Down to next line. (Shift Out)
		SI,		# ^O = Insert newline at cursor. (Shift In)
		DLE,	# ^P = Up to previous line. (Data Link Escape)
		NAK,	# ^U = Clear all text. (Negative Acknowlegement)
		
		isalpha,	# Returns True for alphabetic character codes.
		alt,		# Returns the meta (8th bit set) version of a key code.
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

from	entities.entity	import (

		Operator_Entity,	# An entity representing the console operator (human).

	)
	
from	events.event 	import (

		TextEvent,			# For an event representing the operator's text input.
		MinuteEventFormat,	
			# The format we use by default for displaying this text event in 
			# the inputPanel.  Includes the date/time and author (Operator).
		
	)

from	supervisor.action	import (

		Operator_Speech_Action		# We create these when the operator sends the panel text.

	)

from	display.keys	import (

		#-------------------------------
		# Special keys used for editing.

			# Maybe some keywords will generate this one natively.
		KEY_BACKSPACE,

			# These ones are also normal ASCII A0 controls (& ASCII RUBOUT/DEL).
		KEY_DELBACK, KEY_TAB, KEY_LINEFEED, KEY_FORMFEED, KEY_RETURN, KEY_ESCAPE, KEY_DELETE,
		
			# These ones are found on the little keypad for special controls.
		KEY_HOME, KEY_BEG, KEY_END, KEY_DC, KEY_IC,	# KEY_DC = Del, KEY_IC = Ins.
		
			# Arrow keys.
		KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
		KEY_CTRL_LEFT, KEY_CTRL_RIGHT,
		
			# Numeric keypad keys.
		KEY_ENTER,	# This is actually the same as KEY_LINEFEED, unfortunately.
			
			# Other "special" (synthesized) keys.
			
		KEY_IL, 		# Insert line.  Keycode synthesized from ^O = open new line at cursor.
		KEY_EOL,		# Delete to end of line.  Keycode synthesized from ^K = kill to end of line.
		KEY_CLEAR,		# Clear entire contents of text data.
		KEY_REFRESH,	# Refresh the display.

			# Function keys that we use for special purposes.

		KEY_F1,		# "Soft-poke" the AI, to get its attention if it's already awake.
		KEY_F2,		# Send the contents of the text panel to the system.

		# Classes.

		KeyEvent,

	)

from	display.panel	import (

		Panel,			# This is the base class from which we derive the InputPanel.
		LOWER_RIGHT		# This is the panel placement specifier we use for the input panel.
		
	)
	
TERMINATOR = chr(ETX)	# This is a control-C or End-of-Text character.

class PromptTimer: pass
class InputPanel: pass

class PromptTimer(ThreadActor):
	
	"""The purpose of this thread is to update the operator's prompt once
		per second with an updated time and date."""
	
	defaultRole = 'PromptTmr'
	defaultComponent = _sw_component
	updatePeriod = 60	# Update prompt once every 60 secs. = once per minute.
	
	def __init__(newPromptTimer:PromptTimer, inputPanel:InputPanel):
	
		_logger.debug("[Input Panel] Creating thread to update prompt. ")

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

			# The prompt update cycle is 1 minute.  Update time in prompt,
			# wait 1 minute, update time in prompt again, etc.
		
			timer.updatePrompt()		# Update prompt with current time.
			
			sleep(timer.updatePeriod)	# Sleep for one minute.
			
	def updatePrompt(thisPromptTimer:PromptTimer):
		timer = thisPromptTimer
		timer.panel.updatePrompt()	# Let the main Panel class do the work.
		

def isword(ch:int):
	return isalpha(ch)

class InputPanel(Panel):

	"""Panel for prompting for and accepting input from the operator."""

	_DEFAULT_HANGING = 4				# Default hanging indent. (Is 8 better?)
	eventFormat = MinuteEventFormat		# Format for displaying the working "input event."
	
	def __init__(newInputPanel:InputPanel, hanging:int=None):
			
		_logger.info("    [Console/InputPanel] Initializing input panel.")
		#_logger.debug("inputPanel.__init__(): Initializing input panel.")

			# Use a shorter name for this new log panel.
		panel = newInputPanel
		
			# First we do general panel initialization.
		super(InputPanel, panel).__init__("Operator Input", LOWER_RIGHT, 4)
			# By default, the input panel appears at the bottom of the right column.
			# A default height of 4 for this panel is fine.  It can grow if needed.
		
			# Configure the hanging indent spacing.
		if hanging is None:
			hanging = panel._DEFAULT_HANGING

		panel._hanging = hanging

			# Create and store the operator entity.
		operator = Operator_Entity()
		panel._operatorEntity = operator
		
			# Create and store the draft text input event.
		opTextEvent = TextEvent(TERMINATOR, author=operator, defaultFormat=panel.eventFormat)
			# Note the text of the event is just a single End-Of-Text (^C) character initially.
			# It will expand as the operator types text in the box.
		panel._opTextEvent = opTextEvent	# Operator's text event.
			
			# Set the initial cursor position within the input text.
		panel._txpos = 0

			# Create the prompt timer thread (see above).
			# Its job will be to update the time displayed in the
			# operator's input prompt.
		timerThread = PromptTimer(panel)
		panel._promptTimer = timerThread
		
			# Does panel need updating because a key handler changed its text?
		panel._needsUpdate = False	# No, no keys have been processed yet.

	#__/ End instance initializer method inputPanel.__init__().

	def configWin(thisInputPanel:InputPanel):
		panel = thisInputPanel

			# Do generic Panel configWin stuff.
		super(InputPanel, panel).configWin()

			# Make sure leaveok is true so cursor doesn't move too much.
		win = panel.win
		win.leaveok(True)


	@property
	def txpos(thisInputPanel:InputPanel):
		panel = thisInputPanel
		return panel._txpos


	@property
	def pos(thisInputPanel:InputPanel):
		panel = thisInputPanel
		txpos = panel.txpos
		pos = txpos + panel.promptLen()
		return pos


	def grabCursor(thisInputPanel:InputPanel):

		panel 	= thisInputPanel
		win		= panel.win
		txpos 	= panel.txpos

			# Convert text position to a position in the window contents.
		pos = txpos + panel.promptLen()

			# Set the cursor position based on that.
		panel.setPos(pos)
		

	def setTxPos(thisInputPanel:InputPanel, txpos:int):
		panel = thisInputPanel
		panel._txpos = txpos

		panel.grabCursor()	# Make sure cursor is at txpos.


	def setPos(thisInputPanel:InputPanel, pos:int):

		"""Sets the cursor position based on the given position
			within the window content string."""

		panel = thisInputPanel
		win = panel.win

			# Remember the new position (relative to start of text).
		panel._txpos = pos - panel.promptLen()
	
			# Now convert the position back to cursor coordinates, and move the cursor there.
		(cy, cx) = panel.pos2yx[pos]
		win.move(cy, cx)
		win.cursyncup()
		
			# We need to update the panel display to draw the cursor in the right location.
		panel._needsUpdate = True


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
		
		"""Modifies the text content of the panel.  Marks the panel
			so that we remember that we need to update its display."""

		panel = thisInputPanel
		
		textEvent = panel.textEvent
		textEvent.text = text
		
		panel._needsUpdate = True

		# Note: We now wait to do this in .handle().
		#driver(panel.redisplayContent, desc="Redisplay input panel contents with new text.")
			# Update the panel display.

	def promptLen(thisInputPanel:InputPanel):
		panel 		= thisInputPanel
		textEvent	= panel.textEvent
		promptLen	= textEvent.promptLen()
		return promptLen
		

	def launch(thisInputPanel:InputPanel):
	
		"""This standard Panel method is called automatically by the Panel 
			to start up any associated threads at the time of first display.  
			In our case, we use it to grab the keyboard focus and start the
			prompt-update timer."""
		
		panel = thisInputPanel

			# Grab the keyboard focus.
		panel.grabFocus()

			# Pull in the cursor's position to where it should be.
		panel.grabCursor()

			# Start the prompt timer thread.
		_logger.debug("inputPanel.launch(): Starting the prompt timer thread.")
		panel._promptTimer.start()
		
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
		(yx2pos, pos2yx) = display.renderText(
			displayText, win=win, hang=panel._hanging, promptChar='>')
			# Note this method does special stuff with various control
			# and whitespace characters. Also it puts the prompt in a
			# different color.  The return values map screen
			# locations to positions in the string.

		panel._yx2pos = yx2pos
		panel._pos2yx = pos2yx

			# Make sure the cursor is positioned where it should
			# be according to the current text position.
		panel.grabCursor()

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
		keyevent = keyEvent
		
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

		if keycode == SOH or keycode == KEY_HOME or keycode == KEY_BEG:
			# ^A = Actually, please go to the start of the line.
			panel.keyHome()
			
		elif keycode == STX or keycode == KEY_LEFT:
			# ^B = Back to previous character.
			panel.keyLeft()
			
		elif keycode == alt(ord('b')) or keycode == KEY_CTRL_LEFT:
			panel.keyLeftWord()
			
		elif keycode == EOT or keycode == KEY_DELETE or keycode == KEY_DC:
			# ^D = Delete character.
			panel.keyDelete()
			
		elif keycode == alt(ord('d')):	# We would like to accept Ctrl-Del for this also but we don't have a keycode for it yet.
			panel.keyDeleteWord()
			
		elif keycode == ENQ or keycode == KEY_END:
			# ^E = End of line, go to.
			panel.keyEnd()
			
		elif keycode == ACK or keycode == KEY_RIGHT:
			# ^F = Forward to the right.
			panel.keyRight()
			
		elif keycode == alt(ord('f')) or keycode == KEY_CTRL_RIGHT:
			panel.keyRightWord()
			
		elif keycode == BS or keycode == KEY_DELBACK or keycode == KEY_BACKSPACE:
			# ^H = Hey, undo that.
			panel.keyDeleteBack()
			
		elif keycode == alt(BS) or keycode == alt(KEY_BACKSPACE):
			# Alt-^H = Delete a word backwards.
			panel.keyDelWordBack()

		elif keycode == LF or keycode == KEY_LINEFEED:
			# ^J = Jump to new line. "Return" key on keyboard normally generates this.
			panel.keyLineFeed()

		elif keycode == VT or keycode == KEY_EOL:
			# ^K = Kill line.
			panel.keyKillToEOL()
			
		elif keycode == FF or keycode == KEY_REFRESH:
			# ^L = Let's refresh the display.
			panel.keyRefresh()

		elif keycode == CR or keycode == KEY_ENTER:
			# ^M = Move cursor to start of next line.
			panel.keyEnter()
			
		elif keycode == SO or keycode == KEY_DOWN:
			# ^N = Next line.
			panel.keyDown()
			
		elif keycode == SI or keycode == KEY_IL or keycode == KEY_IC:
			# ^O = Open line. (Ins)
			panel.keyInsertLine()
			
		elif keycode == DLE or keycode == KEY_UP:
			# ^P = Previous line.
			panel.keyUp()
			
		elif keycode == NAK or keycode == KEY_CLEAR:		
			# ^U = Clear all text.
			panel.keyClear()
		
		elif keycode >= 0xc0 and keycode <= 0xdf:	# Alt-Shift-'@' through Alt-Shift-'_' - Remap these to self-insert all A0 controls.

			newkeyevent = KeyEvent(keycode - 0xc0)
			panel.insertKey(newkeyevent)

			_logger.info(f"Input Panel: Remapped {keyname} to literal {newkeyevent.ctlname}.")

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Below we handle function keys that we have mapped to special behaviors.
		#|
		#|	- F1 (Attention) - Provoke the AI to respond.
		#|	- F2 (Send) - Sends the entered text to GLaDOS as a speech action.
		#|  - F3...
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		elif keycode == KEY_F1:		# F1 = Get AI's attention.

			panel.keyAttention()

		elif keycode == KEY_F2:		# F2 = Send text to GLaDOS.

			panel.keySend()

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Catch-all case: All other keys are just self-inserting by default.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		else:
			panel.insertKey(keyevent)
		
		#__/ End if/elif/else block for keycode-based event dispatching.

			#/--------------------------------------------------------
			#| At this point, we check whether whatever the user did
			#| caused some change to the panel text, and if so, we
			#| request the display driver to show the updated text.

		panel.updateIfNeeded()

	#__/ End instance method panel.handle().


	def updateIfNeeded(thisInputPanel:InputPanel):

		"""Updates the panel display, but only if our internal record-keeping
			indicates that an update is needed."""

		panel	= thisInputPanel
		client	= panel.client
		display	= client.display
		driver	= display.driver

		if panel._needsUpdate:	# Does the panel display need updating?

			panel.redisplayContent()

			# Not needed since we should already be in the display driver thread.
			#driver(panel.redisplayContent, desc="Redisplay input panel contents after key handling.")

			panel._needsUpdate = False	# That's taken care of now.
		

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

			# Now set the cursor position based on that.
		panel.setPos(pos)
 

	def cursorPos(thisInputPanel:InputPanel):
		
		"""Returns the current cursor's position in the text."""
		
		panel	= thisInputPanel
		win		= panel.win
		
		panel._adjustPos()			# Make sure cursor position is OK.
		(cy, cx) = win.getyx()		# Get current cursor position.
		
			# Now get the corresponding position in the text.
		pos = panel.yx2pos[(cy, cx)]
		
		return pos


	def setYxPos(thisInputPanel:InputPanel, cursY:int, cursX:int):

		"""Sets the (y,x) cursor coordinates as given, with any
			adjustments needed."""
		
		panel		= thisInputPanel
		win			= panel.win
		
			# First, just move the cursor to the requested coordinates.
		win.move(cursY, cursX)
		
			# Next, adjust the cursor position as needed to make sure 
			# we're actually sitting on an editable character.
		panel._adjustPos()
		

	def insertChar(thisInputPanel:InputPanel, char):

		"""Inserts a given character at the current cursor position,
			and moves the cursor to the right one space."""

		panel	= thisInputPanel
		txpos	= panel.txpos

		panel.insertAfter(char)

		# We go ahead and update the panel now, to make sure that the new cursor
		# location actually exists before we try to move the cursor there.

		panel.updateIfNeeded()

		# This increments the text position.
		panel.setTxPos(txpos + 1)


	def insertAfter(thisInputPanel:InputPanel, char):

		"""Inserts a given character at the current cursor position,
			leaving the cursor at the newly inserted character."""

		panel	= thisInputPanel
		txpos	= panel.txpos
		text	= panel.text

		# This inserts the character at the text position.
		text = text[:txpos] + char + text[txpos:]
		
		# Update the panel's text.
		panel.setText(text)


	def insertKey(thisInputPanel:InputPanel, event:KeyEvent):
		
		"""Inserts the given keypress at the current cursor position."""
		
		panel	= thisInputPanel
		keycode = event.keycode				# Numeric keycode for current key.
		char	= chr(keycode)				# Convert numeric code to a character.
		
		panel.insertChar(char)


	def keyHome(thisInputPanel:InputPanel):
	
		"""This method handles the 'Home' key, and also ^A = go to start of line.
			It moves the cursor to the leftmost editable column in the current row."""
		
		panel = thisInputPanel
		
		pos = panel.pos					# Get current cursor position in content text.
		(cy, cx) = panel.pos2yx[pos]
		cx = panel._hanging				# Try setting x coordinate to 0.
		panel.setYxPos(cy, cx)			# Move cursor to there.
	
	
	def keyLeft(thisInputPanel:InputPanel):
	
		"""This method handles the left arrow key, and also ^B = go back one character.
			It moves the cursor to one position earlier in the text."""
		
		panel = thisInputPanel
		
		txpos = panel.txpos
		if txpos > 0:
			txpos = txpos - 1
			panel.setTxPos(txpos)
	
	
	def atWordStart(thisInputPanel:InputPanel):
	
		panel = thisInputPanel
		
		txpos = panel.txpos
		text = panel.text
		
		if txpos == 0:
			return True
			
		prevCh = ord(text[txpos - 1])
		thisCh = ord(text[txpos])
		
		if not isword(prevCh) and isword(thisCh):
			return True
	
	
	def keyLeftWord(thisInputPanel:InputPanel):
	
		"""This method handles control-left arrow, and also Alt-B = go back one word.
			It moves the cursor to the start of the previous word."""
		
		panel = thisInputPanel
		
		panel.keyLeft()
		while not panel.atWordStart():
			panel.keyLeft()					# Could do this more efficiently.
	
	
	def keyDelete(thisInputPanel:InputPanel):

		"""This method handles the 'Delete' key, and also ^D = delete character under cursor.
			It deletes the character under the cursor."""

		panel = thisInputPanel
		
		txpos = panel.txpos
		text = panel.text

		txlen = len(text)

		if txpos >= txlen - 1:	# If = then sitting on ETX. Should never be >.
			return

			# Actually delete the character.
		text = text[:txpos] + text[txpos + 1:]
	
		panel.setText(text)

	
	def keyDeleteWord(thisInputPanel:InputPanel):

		"""This method handles control-delete (maybe), and also Alt-D = delete word.
			It deletes the word under (or after) the cursor."""
		
		panel = thisInputPanel

		txpos  = panel.txpos
		text   = panel.text
		thisCh = ord(text[txpos])

		if isword(thisCh):	# Are we in a word?

			# Make sure we're at the start of this word.
			if not panel.atWordStart():
				panel.keyLeftWord()		

		else:	# We're not in a word.

			# Delete characters until we are, or we run out of string.
			while not isword(thisCh) and txpos < len(panel.text) - 1:
				panel.keyDelete()
				txpos = panel.txpos
				text = panel.text
				thisCh = ord(text[txpos])

		# From start of word, delete until we run out of word/string.
		txpos = panel.txpos
		text = panel.text
		thisCh = ord(text[panel.txpos])
		while isword(thisCh) and txpos < len(text) - 1:
			panel.keyDelete()
			text = panel.text
			thisCh = ord(text[txpos])
			

	def keyEnd(thisInputPanel:InputPanel):
		
		"""This method handles the 'End' key, and also ^E = go to end of line.
			It moves the cursor to the rightmost editable column in the current row."""
		
		panel = thisInputPanel
		win = panel.win
		(height, width) = win.getmaxyx()

		pos = panel.pos					# Get current cursor position in content text.
		(cy, cx) = panel.pos2yx[pos]
		cx = width - 2					# Try setting x coordinate to rightmost non-pad column.
		panel.setYxPos(cy, cx)			# Move cursor to there.
			# This should automatically limit us to existing text.

	
	def keyRight(thisInputPanel:InputPanel):

		"""This method handles the right arrow key, and also ^F = go forward one character.
			It moves the cursor to one position later in the text."""

		panel = thisInputPanel
		text = panel.text
		tlen = len(text)

		txpos = panel.txpos
		if txpos < tlen - 1:	# tlen - 1 is final ETX.

			txpos = txpos + 1
			
			panel.setTxPos(txpos)


	def keyRightWord(thisInputPanel:InputPanel):

		"""This method handles control-right arrow, and also Alt-F = go forward one word.
			It moves the cursor to the start of the next word."""

		panel = thisInputPanel
		
		panel.keyRight()
		while not panel.atWordStart() and panel.txpos < len(panel.text) - 1:
			panel.keyRight()

	
	def keyDeleteBack(thisInputPanel:InputPanel):

		"""This method handles the Backspace key, and also ^H = BS.
			It deletes the character to the left of the cursor."""

		panel = thisInputPanel
		txpos = panel.txpos

		if txpos > 0:
			text = panel.text

			# Delete character to the left.
			text = text[:txpos-1] + text[txpos:]

			# Move cursor position left.
			txpos = txpos - 1
			panel.setTxPos(txpos)

			# Update the text.
			panel.setText(text)


	def keyDelWordBack(thisInputPanel:InputPanel):

		"""Deletes the entire word that the cursor is after, or in."""

		panel = thisInputPanel
		txpos = panel.txpos
		text = panel.text

		# Backspace till we get to a word.
		while txpos > 0:
			prevCh = ord(text[txpos - 1])
			if isword(prevCh):
				break
			panel.keyDeleteBack()
			txpos = panel.txpos

		panel.keyLeftWord()
		panel.keyDeleteWord()


	def keyLineFeed(thisInputPanel:InputPanel):

		"""This method handles the Return key and also ^J = LF.
			It inserts a newline (LF) before the cursor (moving the cursor)."""

		thisInputPanel.insertChar('\n')
		
	
	def keyEnter(thisInputPanel:InputPanel):

		"""This method handles the keypad Enter key.
			It inserts a carriage return (CR) before the cursor (moving the cursor)."""

		thisInputPanel.insertChar('\r')
		
	
	def keyKillToEOL(thisInputPanel:InputPanel):

		"""This method handles the EOL key, and also ^K = Kill to End of Line.
			It deletes the remainder of the current line of text, from the cursor to EOL (CR or LF)."""

		panel = thisInputPanel
		txpos = panel.txpos
		text = panel.text
		
		# If the position is on a line break (CR, LF, or CRLF), delete the line break.
		if text[txpos] == '\r':
			panel.keyDelete()
			if panel.text[txpos] == '\n':
				panel.keyDelete()
		elif text[txpos] == '\n':
			panel.keyDelete()
		else:

			whereTo = len(text)-1
			for i in range(txpos+1, len(text)-2):
				if text[i] == '\r' or text[i] == '\n':
					whereTo = i
					break

			text = text[:txpos] + text[whereTo:]

			panel.setText(text)

	
	def keyRefresh(thisInputPanel:InputPanel):

		"""This method handles the FF key, which is ^L = Let's refresh the display.
			It redisplays the entire screen."""
		
		panel = thisInputPanel
		client = panel.client

			# Tells the client to regenerate its entire display.
		client.redisplay()


	def keyDown(thisInputPanel:InputPanel):

		"""This method handles the down arrow key, and also ^N = go to next line.
			It moves the cursor down one line to an editable character."""

		panel = thisInputPanel
		win = panel.win
		(height, width) = win.getmaxyx()
		
		pos = panel.pos					# Get current cursor position in content text.
		(cy, cx) = panel.pos2yx[pos]
		if cy < height - 1:
			cy = cy + 1						# Try increasing y coordinate by 1.
			panel.setYxPos(cy, cx)			# Move cursor to there.

	
	def keyInsertLine(thisInputPanel:InputPanel):

		"""This method handles the Ins key, and also ^O = insert line at cursor.
			It inserts a newline character at the current cursor position."""

		thisInputPanel.insertAfter('\n')

	
	def keyUp(thisInputPanel:InputPanel):

		"""This method handles the Up arrow key, and also ^P = go to previous line.
			It moves the cursor up one line to an editable character."""

		panel = thisInputPanel
		
		pos = panel.pos					# Get current cursor position in content text.
		(cy, cx) = panel.pos2yx[pos]
		if cy > 0:
			cy = cy - 1						# Try increasing y coordinate by 1.
			panel.setYxPos(cy, cx)			# Move cursor to there.

	
	def keyClear(thisInputPanel:InputPanel):

		"""This method handles the Clear key, and also ^U = undo all typing.
			It clears all the text that has been typed."""

		panel = thisInputPanel

		panel.setTxPos(0)
		panel.setText(TERMINATOR)


	def keyAttention(thisInputPanel:InputPanel):

		"""This method handles the F1 key, which means, get the AI's attention."""

		panel = thisInputPanel
		client = panel.client
		mind = client.mind
		mindThread = mind.thread
		
		mindThread.softPoke()	# Just enough to get its attention if awake.


	def keySend(thisInputPanel:InputPanel):

		"""This method handles the F2 key, which means, send the text to the
			system, by creating and initiating a speech action."""

		panel = thisInputPanel
		client = panel.client
		text = panel.text
		
		_logger.info(f"[Input Panel] Operator is sending: [{text}]")


		# Strip off the terminating ETX character to produce the actual
		# intended content of the text to send.
		textBody = text[:-1]

			# Construct the speech action representing our input to the system.
		opSpeechAct = Operator_Speech_Action(textBody)

			# Go ahead and initiate the action. This injects it into the
			# supervisor's action-processing subsystem.
		opSpeechAct.initiate()

			# Finally, we clear the panel contents.
		panel.keyClear()

#__/ End class InputPanel.

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					END OF FILE:	console/inputPanel.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
