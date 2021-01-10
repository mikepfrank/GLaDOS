#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 display/keys.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		display/keys.py				 [Python module source file]
	
	MODULE NAME:	display.keys
	IN PACKAGE:		display
	FULL PATH:		$GIT_ROOT/GLaDOS/src/display/keys.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.display (Display screen management)


	MODULE DESCRIPTION:
	===================
	
		This module provides for keyboard input processing that is
		considerably more sophisticated than what is built into curses--
		at least for use with Windows/Putty terminals.
		
		Features include support for:
		
			* Numeric keypad keys, named 'Num_Lock', 'KP_0'-'KP_9', 
				'KP_DIVIDE', 'KP_TIMES', 'KP_MINUS', 'KP_PLUS', 'KP_DOT',
				and 'KEY_ENTER' (that one already existed).
				
			* Control-arrow keys, named 'Ctrl-Up', 'Ctrl-Down', 'Ctrl-Left',
				'Ctrl-Right'.
			
			* Shifted function keys, 'Shift-F3' through 'Shift-F10'.

			* New keycodes for all of the above keys.

			* 'Home', 'End', and F1-F4 keys.  These also have the corresponding
				(already existing) keycodes. 

			* "Alt" or "Meta" versions of almost all keys; named "Alt-<keyname>"
				and with keycodes identical to the originals, but with bit 7 set.
	
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|
	#|	1.  Exported name list. 		   				   [module code section]
	#|
	#|			Here we list all of the public names that are standardly
	#|			exported from this module, if the using module does:
	#|
	#|						from display import *
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
global __all__ 
__all__ = [		# List of all public names exported from this module.

			#|---------
			#| Classes.
		
		'TheKeyBuffer',		# Singleton class; anchor for key processing.
		
			#|--------------------
			#| "Type" definitions.
		
		'KeyEvent',		# An event caused by a keypress. 		   [simple type]
			
			#|-----------
			#| Constants.
		
				# Numeric keypad keycodes.
				
		'KEY_NUM_LOCK', 'KEY_PAD_PLUS', 'KEY_PAD_DOT', 'KEY_PAD_0', 'KEY_PAD_1',
		'KEY_PAD_2', 'KEY_PAD_3', 'KEY_PAD_4', 'KEY_PAD_5', 'KEY_PAD_6', 
		'KEY_PAD_7', 'KEY_PAD_8', 'KEY_PAD_9', 'KEY_PAD_DIVIDE', 'KEY_PAD_TIMES',
		'KEY_PAD_MINUS',
		
				# Control-arrow keycodes.
				
		'KEY_CTRL_UP', 'KEY_CTRL_DOWN', 'KEY_CTRL_RIGHT', 'KEY_CTRL_LEFT',
		
				# Shift-function keycodes.
		
		'KEY_SHIFT_F3', 'KEY_SHIFT_F4', 'KEY_SHIFT_F5', 'KEY_SHIFT_F6', 
		'KEY_SHIFT_F7', 'KEY_SHIFT_F8', 'KEY_SHIFT_F9', 'KEY_SHIFT_F10'
		
	]


	#|==========================================================================
	#| 	2.	Imports.									   [module code section]
	#|
	#|		2.1.  Standard Python modules imported into this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|======================================================================
		#| 	Locale setup. Here we obtain the system's default string encoding.
		#|	Used in _keystr().
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from locale import (setlocale, LC_ALL, getpreferredencoding)

	#-----------------------------------------------------------------------
	# This sets the locale for all categories to the user's default setting, 
	# e.g., from the LANG environment variable, if that is specified.
	
setlocale(LC_ALL, '')

	#--------------------------------------------------------------------
	# This gets the preferred encoding configured by the user preferences 
	# (the exact method for this is system-dependent).
	
global _encoding	
_encoding = getpreferredencoding()
	# We'll use this wherever we need to encode/decode strings to bytes.


		#|======================================================================
		#| Import a bunch of stuff that we need from the curses package.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from curses import (
		keyname,
		ERR, KEY_HOME, KEY_END, KEY_RESIZE,
		KEY_F1, KEY_F2, KEY_F3, KEY_F4,
		KEY_BEG, KEY_LEFT, KEY_DC, KEY_END, KEY_RIGHT, KEY_BACKSPACE,
		KEY_ENTER, KEY_EOL, KEY_DOWN, KEY_IC, KEY_IL, KEY_UP, KEY_CLEAR,
		KEY_MAX
	)

from curses.ascii import (
			
			# The following are both control character code points, and valid key codes.
			
		HT, TAB,		# Horizontal tab character.
		CR, LF,	FF,		# Carriage return, line feed and form feed.
		BS, DEL, 		# Backspace and delete.
		ESC,			# Escape character; used in KeyBuffer.
		
			# Other names.
		
		controlnames, 	# Array: Names of characters 0-33, used in _ctlname().
		iscntrl, 		# Function: Is this code a 7-bit ASCII control? Used in KeyEvent.
		isdigit,		# Function: Is this code a digit 0-9?  Used in kb._get_bracket_escape().
		alt,			# Set 8th bit (bit 7) in code.
	)



from infrastructure.decorators	import	singleton	# Class decorator.  Used by TheDisplay.


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	3. Globals.										   [module code section]
	#|
	#|		This section defines various global constants, variables, and
	#|		arrays provided and/or used by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	New key codes.  Note this extends the standard list of key codes
		#|	that ships with curses.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|----------------------------------------------------------------------------
	#| Key code synonyms for existing control code points that we don't repurpose.
	
KEY_BACKSPACE	= BS	# ^H = Back space.
KEY_TAB			= HT	# ^I = Horizontal tab.
KEY_LINEFEED	= LF	# ^J = Line feed.			NOTE: This is also KEY_ENTER
KEY_FORMFEED	= FF	# ^L = Form feed.
KEY_RETURN		= CR	# ^M = Carriage return.
KEY_ESCAPE		= ESC	# ^[ (27) = Escape
KEY_DELETE		= DEL	# ^? (127) = Delete

	#--------------
	# Key pad keys.

global KEY_NUM_LOCK, KEY_PAD_PLUS, KEY_PAD_DOT, KEY_PAD_0, KEY_PAD_1, KEY_PAD_2
global KEY_PAD_3, KEY_PAD_4, KEY_PAD_5, KEY_PAD_6, KEY_PAD_7, KEY_PAD_8
global KEY_PAD_9, KEY_PAD_DIVIDE, KEY_PAD_TIMES, KEY_PAD_MINUS
		
KEY_NUM_LOCK	= KEY_MAX + 0
KEY_PAD_PLUS	= KEY_MAX + 1		# Above normal range of curses key codes.
KEY_PAD_DOT		= KEY_MAX + 2
KEY_PAD_0		= KEY_MAX + 3
KEY_PAD_1		= KEY_MAX + 4
KEY_PAD_2		= KEY_MAX + 5
KEY_PAD_3		= KEY_MAX + 6
KEY_PAD_4		= KEY_MAX + 7
KEY_PAD_5		= KEY_MAX + 8
KEY_PAD_6		= KEY_MAX + 9
KEY_PAD_7		= KEY_MAX + 10
KEY_PAD_8		= KEY_MAX + 11
KEY_PAD_9		= KEY_MAX + 12
KEY_PAD_DIVIDE	= KEY_MAX + 13
KEY_PAD_TIMES	= KEY_MAX + 14
KEY_PAD_MINUS	= KEY_MAX + 15


	#--------------------
	# Control-arrow keys.
	
global KEY_CTRL_UP, KEY_CTRL_DOWN, KEY_CTRL_RIGHT, KEY_CTRL_LEFT

KEY_CTRL_UP		= KEY_MAX + 16
KEY_CTRL_DOWN	= KEY_MAX + 17
KEY_CTRL_RIGHT	= KEY_MAX + 18
KEY_CTRL_LEFT	= KEY_MAX + 19


	#-----------------------
	# Shifted function keys.

global KEY_SHIFT_F3, KEY_SHIFT_F4, KEY_SHIFT_F5, KEY_SHIFT_F6, KEY_SHIFT_F7
global KEY_SHIFT_F8, KEY_SHIFT_F9, KEY_SHIFT_F10

KEY_SHIFT_F3	= KEY_MAX + 20
KEY_SHIFT_F4	= KEY_MAX + 21
KEY_SHIFT_F5	= KEY_MAX + 22
KEY_SHIFT_F6	= KEY_MAX + 23
KEY_SHIFT_F7	= KEY_MAX + 24
KEY_SHIFT_F8	= KEY_MAX + 25
KEY_SHIFT_F9	= KEY_MAX + 26
KEY_SHIFT_F10	= KEY_MAX + 27


_esc_map = {	# Map from escape sequences to key names.

		"Ol":		'KP_PLUS',
		"On":		'KP_DOT',
		"Op":		'KP_0',
		"Oq":		'KP_1',
		"Or":		'KP_2',
		"Os":		'KP_3',
		"Ot":		'KP_4',
		"Ou":		'KP_5',
		"Ov":		'KP_6',
		"Ow":		'KP_7',
		"Ox":		'KP_8',
		"Oy":		'KP_9',

		"[A":		'Ctrl-Up',
		"[B":		'Ctrl-Down',
		"[C":		'Ctrl-Right',
		"[D":		'Ctrl-Left',
	
		"[1~":		'Home',
		"[4~":		'End',
		"[11~":		'F1',
		"[12~":		'F2',
		"[13~":		'F3',
		"[14~":		'F4',
	
		"[25~":	    'Shift-F3',
		"[26~":	    'Shift-F4',
		"[28~":	    'Shift-F5',
		"[29~":	    'Shift-F6',
		"[31~":	    'Shift-F7',
		"[32~":	    'Shift-F8',
		"[33~":	    'Shift-F9',
		"[34~":	    'Shift-F10',

	}

# This maps our own names to corresponding keycodes.
_name_codes = {

			# Home and end keys.
			
		'Home':			KEY_HOME,
		'End':			KEY_END,

			# True function keys 1-4.
			
		'F1':			KEY_F1,
		'F2':			KEY_F2,
		'F3':			KEY_F3,
		'F4':			KEY_F4,

			# Numeric keypad keys.
			
		'Num_Lock':		KEY_NUM_LOCK,
		'KP_PLUS':		KEY_PAD_PLUS,
		'KP_DOT':		KEY_PAD_DOT,
		'KP_0':			KEY_PAD_0,
		'KP_1':			KEY_PAD_1,
		'KP_2':			KEY_PAD_2,
		'KP_3':			KEY_PAD_3,
		'KP_4':			KEY_PAD_4,
		'KP_5':			KEY_PAD_5,
		'KP_6':			KEY_PAD_6,
		'KP_7':			KEY_PAD_7,
		'KP_8':			KEY_PAD_8,
		'KP_9':			KEY_PAD_9,
		'KP_DIVIDE':	KEY_PAD_DIVIDE,
		'KP_TIMES':		KEY_PAD_TIMES,
		'KP_MINUS':		KEY_PAD_MINUS,
		
			# Control-arrow keys.
			
		'Ctrl-Up':		KEY_CTRL_UP,
		'Ctrl-Down':	KEY_CTRL_DOWN,
		'Ctrl-Right':	KEY_CTRL_RIGHT,
		'Ctrl-Left':	KEY_CTRL_LEFT,
		
			# Shifted function keys.
			
		'Shift-F3':		KEY_SHIFT_F3,
		'Shift-F4':		KEY_SHIFT_F4,
		'Shift-F5':		KEY_SHIFT_F5,
		'Shift-F6':		KEY_SHIFT_F6,
		'Shift-F7':		KEY_SHIFT_F7,
		'Shift-F8':		KEY_SHIFT_F8,
		'Shift-F9':		KEY_SHIFT_F9,
		'Shift-F10':	KEY_SHIFT_F10,

			# Controls mapped to special keys for editing.
		
		'^A':			KEY_BEG,		# Go to beginning of line.
		'^B':			KEY_LEFT,		# Go back to the left.
		'^D':			KEY_DC,			# Delete character under cursor.
		'^E':			KEY_END,		# Go to end of line.
		'^F':			KEY_RIGHT,		# Go forward to the right.
		'^H':			KEY_BACKSPACE,	# Delete character backwards.
		'^J':			KEY_ENTER,		# Insert new line before cursor.
		'^K':			KEY_EOL,		# Clear to end of line.
		'^N':			KEY_DOWN,		# Go down to next line.
		'^O':			KEY_IL,			# Insert new line at cursor.
		'^P':			KEY_UP,			# Go up to previous line.
		'^U':			KEY_CLEAR,		# Clear entire input region.
	}

_code_map = {	# Map from curses' key codes to better key names.

		ERR:		'<ERROR>',
		KEY_RESIZE:	'Resize',

		KEY_F1:		'Num_Lock',
		KEY_F2:		'KP_DIVIDE',
		KEY_F3:		'KP_TIMES',
		KEY_F4:		'KP_MINUS',

	}


	#|==========================================================================
	#|	3.	Type definitions.							   [module code section]
	#|
	#|		In this section, we define various "types" that we provide.
	#|		Essentially, for us, a "type" just means a simple class, or
	#|		any way of using a structured object as a simple data type.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	(keys.)KeyEvent									[public simple type]
		#|
		#|		An instance of this class is a simple struct that
		#|		represents a "key event" received from curses.  The 
		#|		quotation marks here allude to the fact that some of 
		#|		these events may not correspond to actual keypresses; 
		#|		for example, window resize events.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class KeyEvent:

	"""
		Simple-type-like class for events received from the input terminal.
		
			Properties of a keyEvent instance include:
			------------------------------------------
			
				.keycode [int]	- Numeric code for key pressed.
				
				.keyname [str]	- String name for key pressed.
				
				.ctlname [str]	- Mnemonic name for key if a 7-bit control or
									whitespace character, else None.
	"""
	
	def __init__(thisKeyEvent, keycode=None, keyname=None):
	
		event = thisKeyEvent
	
		if keyname is None:
			keyname = _keystr(keycode)		# Convert to string name.

		# If we have a replacement keycode in the _name_codes lookup table,
		# let it override whatever keycode we were given.
		if keyname in _name_codes:
			keycode = _name_codes[keyname]

		event._keycode = keycode
		event._keyname = keyname
		event._ctlname = _ctlname(keycode)		# Convert to control mnemonic.

	#__/ End instance initializer for simple type class KeyEvent.


	@property
	def keycode(thisKeyEvent):
		return thisKeyEvent._keycode
		
	@property
	def keyname(thisKeyEvent):
		return thisKeyEvent._keyname
		
	@property
	def ctlname(thisKeyEvent):
		return thisKeyEvent._ctlname
	
#__/ End public simple type (keys.)KeyEvent.


	#|==========================================================================
	#|	4.	Function definitions.						   [module code section]
	#|
	#|		In this section we define the various functions provided by 
	#|		this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	_keystr()								   		  [private function]
		#|
		#|		Given a numeric keycode, returns a string representation
		#|		of the key.  This may be an escape sequence or a key name.
		#|
		#|		The special KEY_RESIZE 'key code' (which is really a signal 
		#|		that the terminal window has been resized by the user) is 
		#|		mapped to the string "Resize".  The error code ERR (= -1)
		#|		is mapped to the string "<ERROR>".
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _keystr(k):

	"""Returns a string representation of the given numeric keycode."""
	
	altstr = _alt_string(k)	# See if we have an alternate string representation for it.

	if altstr is not None:	# If so,
		return altstr		#	then just return that one.

	elif k == None:			# Or if k is None,
		return "(None)"		#	then return this string.

	else:		# Otherwise, we'll ask curses to find the string for us.
		try:
			return keyname(k).decode(_encoding)
		except ValueError as e:
			_logger.error(f"keystr(): {str(e)}: Received unknown key code {k}.")

#__/ End module private function _keystr().


def _ctlname(k:int = None):

	"""Returns a mnemonic symbol for a given numeric keynode, or None."""

	if k is None:
		return None

		#|--------------------------------------------------------------------
		#| The following code translates the nonprinting ASCII characters 0-33 
		#| and 127 (Delete), and the 8-bit character 160 (Nonbreaking Space) to 
		#| their corresponding (2-3 letter) mnemonics.
			
	if (iscntrl(k) and k <= 0x1f) or k == 0x20:
		cn = controlnames[k]
	elif k == 0x7f:
		cn = 'DEL'		# Special case; 'delete' not in controlnames array.
	elif k == 0xa0:
		cn = 'NBSP'	# Special case; 'nonbreaking space' not in controlnames array.
	else:
		cn = None

	return cn


def _alt_string(keycode):

	"""Given a keycode, look up and return an alternate string name
		for it.  If no alternate name is known, return None."""

	if keycode in _code_map:
		return _code_map[keycode]
	else:
		return None


	#|==========================================================================
	#|
	#|	5.	Class definitions.						   	   [module code section]
	#|
	#|		In this section we define the various classes provided by 
	#|		this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

@singleton
class TheKeyBuffer:

	_skipNextEsc = False
	_bufferedKeys = ""

	def _get_next_rawkey(thisKeyBuffer, win):

		kb = thisKeyBuffer
		bk = kb._bufferedKeys

		if bk == "":		# No keys in buffer.

			return win.getch()
		
		else:

			ch = ord(bk[0])
			kb._bufferedKeys = bk[1:]

			return ch


	def _pushback_keys(thisKeyBuffer, keys):

		kb = thisKeyBuffer
		bk = kb._bufferedKeys

		bk = keys + bk

		kb._bufferedKeys = bk


	def _get_bracket_escape(thisKeyBuffer, win):

		kb = thisKeyBuffer

		s = '['

		while True:
		
			ch = kb._get_next_rawkey(win)
		
			if ch == ERR:	# Timeout.
				return s

			s = s + chr(ch)

			if ch == ord('~') or not isdigit(ch):
				return s

			if len(s) > 3:
				return s


	def _get_O_escape(thisKeyBuffer, win):

		kb = thisKeyBuffer

		s = 'O'

		ch = kb._get_next_rawkey(win)

		if ch == ERR:	# Timeout.
			return s

		s = s + chr(ch)

		return s


	def _get_candidate_escape_sequence(thisKeyBuffer, win):

		"""Call this function after getting an escape character to suck in
			an entire string that *might* be interpreted as an escape sequence."""

		kb = thisKeyBuffer

		win.timeout(500)	# Set timeout to 500 ms = 0.5 second

		ch = kb._get_next_rawkey(win)	# Get first char after escape.


		if ch == ord('['):

			seq = chr(ESC) + kb._get_bracket_escape(win)

		elif ch == ord('O'):

			seq = chr(ESC) + kb._get_O_escape(win)
		
		elif ch == ERR:		# Timeout.

			seq = chr(ESC)	# Bare ESC.

		else:

			seq = chr(ESC) + chr(ch)

		win.timeout(0)		# Go back to no-delay mode.

		return seq
	

	def _interpret_escape_sequence(thisKeyBuffer, win):

		"""Call this after seeing an escape character to get a string
			translation of the escape sequence.  If the returned string
			begins with \033 (ESC), then it is unknown; just process its
			raw characters individually instead."""

		kb = thisKeyBuffer

			# First, get the entire candidate escape sequence.
		seq = kb._get_candidate_escape_sequence(win)

		after = seq[1:]		# Everything after ESC char.

			# Is it one we recognize?  If so, then translate it.
		if after in _esc_map:
			return _esc_map[after]

			# OK, for all other escape sequences longer than just ESC,
			# map them to Alt-Stringname. We do this by pushing everything
			# after the ESC back, getting the new next key name, and then
			# prepending 'Alt-' to it.  Then return that name
			
		if after == "":		# All we had was ESC by itself.
			return seq		# Return that.

		else:
		
			kb._pushback_keys(after)
			nextEvent = kb.get_next_key(win)

			code = alt(nextEvent.keycode)
			name = 'Alt-' + nextEvent.keyname

			event = KeyEvent(keycode = code, keyname = name)

			return event

			# Otherwise, return it as a raw, untranslated string.
			# The application can just process the characters individually.
		#return seq


	def get_next_key(thisKeyBuffer, win):

		"""
			This gets the next key, either from the actual input stream,
			or from an earlier escape sequence that was found uninterpretable.
			It then does any needed escape-sequence processing returns a
			corresponding KeyEvent structure.
		"""

		kb = thisKeyBuffer

		while True:

			# Get the next raw key.
			ch = kb._get_next_rawkey(win)

			# Is it an escape? Process specially...
			if ch == ESC:

				# If we were asked to skip the next escape, then just do that.
				if kb._skipNextEsc:

					event = KeyEvent(keycode = ch)	# Treat it normally.
					kb._skipNextEsc = False

				else:	# OK, let's do the real work of escape processing.

					# Get the interpretation string or event.
					interp = kb._interpret_escape_sequence(win)

					# If the thing magically gave us a key event already, we're done.
					if isinstance(interp, KeyEvent):
						return interp

					# If it starts with an escape, that means it wasn't
					# really interpreted. Stuff it back in the buffer,
					# remember to skip that escape next time, & repeat.

					if ord(interp[0]) == ESC:

						kb._pushback_keys(interp)
						kb._skipNextEsc = True

						continue

					# Otherwise, if we get here, then the interpretation
					# is really the interpretation.  Create a key event
					# with an appropriate name and keycode.

					if interp in _name_codes:
						code = _name_codes[interp]
					else:
						code = None

					event = KeyEvent(keycode=code, keyname=interp)

				#__/ End if/else to process escape.

			else:	# Non-escape character.

				event = KeyEvent(keycode = ch)	# Convert to event normally.

			#__/ End if/else for if ch was an escape character.
				
			# If we get here, then we have an event, so break out.
			break

		#__/ End while loop.

			# At this point we should have an event. Just return it.
		return event

	#__/ End public singleton instance method keyBuffer.get_next_key().

#__/ End public singleton class TheKeyBuffer.

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/keys.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
