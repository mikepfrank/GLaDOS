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
	)

from curses.ascii import (
		ESC,			# Keycode & code point for Escape character; used in KeyBuffer.
		controlnames, 	# Array: Names of characters 0-33, used in _ctlname().
		iscntrl, 		# Function: Is this code a 7-bit ASCII control? Used in KeyEvent.
		isdigit,		# Function: Is this code a digit 0-9?  Used in kb._get_bracket_escape().
		alt,			# Set 8th bit (bit 7) in code.
	)



from infrastructure.decorators	import	singleton	# Class decorator.  Used by TheDisplay.


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

		'Home':		KEY_HOME,
		'End':		KEY_END,

		'F1':		KEY_F1,
		'F2':		KEY_F2,
		'F3':		KEY_F3,
		'F4':		KEY_F4,

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

		win.timeout(1000)	# Set timeout to 1000 ms = 1 second

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
