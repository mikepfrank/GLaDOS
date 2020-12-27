# console.py
# Implements the main GLaDOS system console display

# Here is a rough sketch of the display layout (not actual size or to scale):
#
#		/--------------------------------------------------+--------------------------------------------------\
#		| [This area is used to display a human-readable   | [The receptive field display continues here.
#		|  rendition of the AI's entire receptive field.   |  Lines are word-wrapped to the width of the display column, which is half of
#		|  Any normally-nonprintable ASCII characters are  |
#		|  rendered using special display codes & styles.  |
#		|  E.g., whitespace characters are grayed-out      |
#		|  regular characters: SP='.', HT='>' (followed by |
#		|  0 or more spaces until we get to the next tab   |
#		|  stop), VT='v' (followed by a downward cursor    |
#		|  movement), CR='<' (followed by cursor movement  |
#		|  to the start of the next line, if the next      |
#		|  character is anything but LF), LF=',' followed  |
#		|  by cursor movement to the start of the next     |
#		|  line, FF='V' (acts same as LF).  Other ASCII    |
#		|  characters are displayed using, say, black text |
#		|  on a bright red background.
#		|   
#		|  the screen width, unless the screen width is 
#		|  less than 120 columns, in which case we only
#		|  display the receptive field in a single column.]
#		|
#		|
#		+--------------------------------------------------+
#		| (This area is for real-time display of detailed log lines being spooled to the system log file.
#		|
#		|
#		\
#
#	Control character rendering:
#
#					Rendering as a single black-on-red character.
#					|
#  Dec	Hex	Abb CC	R	Full name / description.
#  ---	--- ---	--	-	------------------------
#	 0	x00	NUL	^@	_	Null character.
#	 1	x01	SOH	^A	:	Start of heading (console interrupt?).
#	 2	x02	STX	^B	[	Start of text.
#	 3	x03	ETX	^C	]	End of text.
#	 4	x04	EOT	^D	.	End of transmission.
#	 5	x05	ENQ	^E	?	Enquiry (used with ACK).
#	 6	x06	ACK	^F	Y	Acknowledgement (used with ENQ). ("Y" is for "Yes!")
#	 7	x07	BEL	^G	*	Bell.
#	 8	x08	BS	^H	<	Backspace.
#	 9	x09	HT	^I	>	Horizontal tabulation [Tab]. (Whitespace; render as gray on black.)
#	10	x0A	LF	^J	/	Line feed [Enter]. (Whitespace; render as gray on black.)
#	11	x0B	VT	^K	v	Vertical tabulation. (Whitespace; render as gray on black.)
#	12	x0C FF	^L	V	Form feed. (Whitespace; render as gray on black.)
#	13	x0D CR	^M	<	Carriage return [Return]. (Whitespace; render as gray on black)
#	14	x0E SO	^N	(	Shift-out; begin alt. char. set.
#	15	x0F SI	^O	)	Shift-in; resume default char. set.
#	16	x10 DLE	^P	/	Data-link escape. (Like my command-line escape character.)
#	17	x11 DC1	^Q	o	Device control 1 (XON), used with XOFF.  Turn on/resume.  ('o' is for "on.")
#	18	x12 DC2	^R	@	Device control 2.  Special mode.
#	19	x13 DC3	^S	=	Device control 3 (XOFF), used with XON.  Secondary stop (wait, pause, standby, halt).
#	20	x14 DC4	^T	-	Device control 4.  Primary stop (interrupt, turn off).
#	21	x15 NAK	^U	N	Negative acknowledgement. (N is for "No!")
#	22	x16	SYN	^V	~	Synchronous idle.	
#	23	x17	ETB	^W	;	End transmission block.
#	24	x18	CAN	^X	X	Cancel.
#	25	x19	EM	^Y	|	End of medium.
#	26	x1A	SUB	^Z	$	Substitute.
#	27	x1B	ESC	^[	^	Escape.
#	28	x1C	FS	^\	F	File separator.	(F is for "file.")
#	29	x1D	GS	^]	G	Group separator. (G is for "group.")
#	30	x1E	RS	^^	&	Record separator. (And, here's another record!  Or, 'P' looks like an end-paragraph marker.)
#	31	x1F	US	^_	,	Unit separator. (In CSV, separates fields of a database row.)
#	32	x20	SP	^`	_	Space. (Whitespace; render as gray on black.)
#  127	x7F	DEL	^?	#	Delete. (Looks like RUBOUT hash.)
#
#	For character codes from 128-255, 