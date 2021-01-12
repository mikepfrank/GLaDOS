#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 console/console.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		console/console.py				 [Python module source file]
		
	MODULE NAME:	console.console
	IN PACKAGE:		console
	FULL PATH:		$GIT_ROOT/GLaDOS/src/console/console.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.console (GLaDOS System Console)


	MODULE DESCRIPTION:
	===================

		This module implements the main system console of the GLaDOS server.
		This runs on the tty where the server process is started.  A human 
		operator can use this console to monitor the system status, and enter
		maintenance commands.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	This module implements the main GLaDOS system console display client,
	#|	which provides the main user interface for the server application.
	#|
	#|	Here is a rough sketch of the console display layout (please note that
	#|	this is not actual size, or to scale):
	#|
	#|		/---------------------------------------- GLaDOS System Console ----------------------------------------\
	#|		| [This area is used to display a human-readable	| [The receptive field display flows around to		|
	#|		|  rendition of the AI's entire receptive field.	|  this column, if it doesn't fit in the first		|
	#|		|  Any normally-nonprintable ASCII characters are	|  column.]											|
	#|		|  rendered using special display codes & styles.	|													|
	#|		|  The view of the receptive field is also word-	|													|
	#|		|  wrapped to fit within the column.  The screen	|													|
	#|		|  is divided into two roughly equal-size columns,	|													|
	#|		|  unless the screen width is less than 120 char-	|													|
	#|		|  acter cells, in which case we use only a single	|													|
	#|		|  column.  If the receptive field doesn't fit in	|													|
	#|		|  the allotted area, a scrollable curses "pad"		|													|
	#|		|  larger than the visible area is utilized to		|													|
	#|		|  allow the user to browse the entire field.]		+--- Diagnostic Output -----------------------------+
	#|		|													| [This area is used to display what would norm-  	|
	#|		|  													|  ally be the STDOUT/STDERR streams from the 	  	|
	#|		|   												|  server process.  STDERR output is rendered	  	|
	#|		|   												|  in red.  STDOUT text comes out in green.		  	|
	#|		|  													|  Operator can scroll back in this window.			|
	#|		|  													+--- Operator Input --------------------------------+
	#|		|													| [This area is a text box that the human operator  |
	#|		|													|  can use to input commands/text to the system.]	|
	#|		+--- System Log ------------------------------------+---------------------------------------------------+
	#|		| [This area is for real-time display of detailed log lines being spooled to the system log file.		|
	#|		|																										|
	#|		|																										|
	#|		\-------------------------------------------------------------------------------------------------------+
	#|
	#|
	#|	Within the field display areas, we use a special character rendering method, so that we can see all of the 
	#|  specific control and whitespace characters that the A.I. is seeing and producing.  The following table shows
	#|	how this rendering is done:
	#|
	#|
	#|							Rendering as a single (usually black-on-red) 8-bit character.
	#|							|
	#|							|	Rendering as a single (usually black-on-red) 7-bit character.
	#|							|	|
	#|	 	Dec	Hex	Abb CC		8	7	Full name / description.
	#| 	 	---	--- ---	--		-	-	------------------------
	#|		 0	x00	NUL	^@		_	_	Null character.
	#|		 1	x01	SOH	^A		$	:	Start of heading (console interrupt?).
	#|		 2	x02	STX	^B		«	[	Start of text.
	#|		 3	x03	ETX	^C		»	]	End of text.
	#|		 4	x04	EOT	^D		.	.	End of transmission.
	#|		 5	x05	ENQ	^E		?	?	Enquiry (used with ACK).
	#|		 6	x06	ACK	^F		!	Y	Acknowledgement (used with ENQ). ("Y" is for "Yes!")
	#|		 7	x07	BEL	^G		¢	*	Bell.
	#|		 8	x08	BS	^H		<	<	Backspace.
	#|		 9	x09	HT	^I		>	>	Horizontal tabulation [Tab]. (Whitespace; render as gray on black.)
	#|		10	x0A	LF	^J		/	/	Line feed [Enter]. (Whitespace; render as gray on black.)
	#|		11	x0B	VT	^K		v	v	Vertical tabulation. (Whitespace; render as gray on black.)
	#|		12	x0C FF	^L		§	V	Form feed. (Whitespace; render as gray on black.)
	#|		13	x0D CR	^M		®	<	Carriage return [Return]. (Whitespace; render as gray on black)
	#|		14	x0E SO	^N		(	(	Shift-out; begin alt. char. set.
	#|		15	x0F SI	^O		)	)	Shift-in; resume default char. set.
	#|		16	x10 DLE	^P		±	/	Data-link escape. (Like my command-line escape character.)
	#|		17	x11 DC1	^Q		°	o	Device control 1 (XON), used with XOFF.  Turn on/resume.  ('o' is for "on.")
	#|		18	x12 DC2	^R		©	@	Device control 2.  Special mode.
	#|		19	x13 DC3	^S		=	=	Device control 3 (XOFF), used with XON.  Secondary stop (wait, pause, standby, halt).
	#|		20	x14 DC4	^T		-	-	Device control 4.  Primary stop (interrupt, turn off).
	#|		21	x15 NAK	^U		¬	N	Negative acknowledgement. (N is for "No!")
	#|		22	x16	SYN	^V			~	~	Synchronous idle.	
	#|		23	x17	ETB	^W		;	;	End transmission block.
	#|		24	x18	CAN	^X		×	X	Cancel.
	#|		25	x19	EM	^Y		|	|	End of medium.
	#|		26	x1A	SUB	^Z		¿	$	Substitute.
	#|		27	x1B	ESC	^[		^	^	Escape.
	#|		28	x1C	FS	^\		¦	F	File separator.	(F is for "file.")
	#|		29	x1D	GS	^]		÷	G	Group separator. (G is for "group.")
	#|		30	x1E	RS	^^		¶	&	Record separator. (And, here's another record!  Or, 'P' looks like an end-paragraph marker.)
	#|		31	x1F	US	^_		·	,	Unit separator. (In CSV, separates fields of a database row.)
	#|		32	x20	SP	^`		·	_	Space. (Whitespace; render as gray on black.)
	#|	   127	x7F	DEL	^?		#	#	Delete. (Looks like RUBOUT hash.)
	#|
	#|	For character codes from 128-255, we render them as above (but in a 
	#|	different color) if they are controls, and as themselves if they are 
	#|	printable Western font (Latin-1) characters.  For codes above 255, 
	#|	how we handle them is not really defined yet.  Maybe we just send 
	#|	them to the terminal unmodified, and just hope that they are 
	#|	supported.  This seems to work for characters up to 383 (ſ) in most 
	#|	fonts.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#/==========================================================================
	#|	1. Module imports.								   [module code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from os 		import 	path

		#|----------------------------------------------------------------------
		#|	Imports and related globals to support logging facility.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.logmaster import (
		sysName,			# Used just below.
		getComponentLogger,	# Used just below.
		set_alt_stdout,		# used in consoleClient.start().
		set_alt_stderr,
	)

global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component


		#|----------------------------------------------------------------------
		#|	Import names we need from the display module.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	To implement the console, we will draw an arrangement of borders and 
	#|	separators, within which are different "panels", or curses sub-windows 
	#|	with specific functionality.  Each panel has a position and size.  In 
	#|	the event of a screen resize, we redo the panel arrangement and refresh 
	#|	the display.
	#|	
	#|	Most of the general infrastructure needed to implement a paneled display 
	#|	like this is provided in the display.panels module, but code specific to 
	#|	the console client in particular is gathered here in the console package.
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from	display.panel	import (

		Panel,			# This is the base class from which we derive various specific types of panels.
		PanelClient,	# This is the base class from which we derive our specific client, ConsoleClient.
		
	)

from .virterm import VirTerm	# Virtual terminal support.

from .logPanel import LogPanel			# Panel for displaying the system log.

from .inputPanel import InputPanel
	# Panel for prompting for and accepting input from the operator.

from .consolePanel import ConsolePanel	

from .fieldDisplay import FieldDisplay
	# FieldDisplay manages the display of the receptive field.

# There are just dummy classes for type hints.
class Supervisor: pass
class TheActionSystem: pass
class TheCognitiveSystem: pass

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|
	#|	Classes provided by the current 'console' module include the following:
	#| 	-----------------------------------------------------------------------
	#|
	#|		ConsoleClient	- Subclass of PanelClient for setting up the 
	#|							console display specifically.
	#|
	#|
	#|	Panel subclasses for specific panels:
	#|	.....................................
	#|
	#|		InputPanel		- This is the panel for gathering operator input.
	#|
	#|		DiagnosticPanel	- This is the panel for displaying STDOUT/STDERR 
	#|							streams.
	#|
	#|		FieldPanel		- This is a class used for panels that display
	#|							all or part of the AI's receptive field.
	#|
	#|
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# The following need to be moved out to their own modules once written.

class FieldPanel(Panel):
	"""Panel to display all or part of the receptive field."""
	pass


class ConsoleClient: pass

class ConsoleClient(PanelClient):

	"""The console display client controls the display 
		when the system console is active."""

	def __init__(newConsoleClient:ConsoleClient,
				 virterm:VirTerm, title:str="GLaDOS System Console"):
	
		client = newConsoleClient

		client._supervisor		= None		# We haven't been introduced to the supervisor yet.
		client._actionSystem	= None		# We haven't been told how to find the action system yet.
		client._hasTerminal		= False		# The console client doesn't yet control the terminal.

		client._virterm = virterm
		
			# First, do general initialization for panel clients.
		super(ConsoleClient, client).__init__(title)
		
			# Next, we need to create all our panels.
		
		_logger.debug("console.__init__(): Creating console panels.")

		client._logPanel		= logPanel 			= LogPanel()
		client._inputPanel		= inputPanel 		= InputPanel()
		client._consPanel		= consolePanel		= ConsolePanel(virterm)
		client._fieldDisplay	= fieldDisplay		= FieldDisplay(client)
		
			# This installs all the panels in this PanelClient.
			
		_logger.debug("console.__init__(): Adding panels to console.")

		client.addPanel(logPanel)			# Place this first, to occupy bottom of screen.
		client.addPanel(inputPanel)			# This goes next, at the bottom of the right column.
			# Note this panel automatically grabs the keyboard focus.
		client.addPanel(consolePanel)		# This goes next, just above the input panel.
		fieldDisplay.addPanels()			# Tells the field display to add its panels.

	@property
	def fieldDisplay(thisConsoleClient:ConsoleClient):
		return thisConsoleClient._fieldDisplay

	def grabTerminal(thisConsoleClient:ConsoleClient):

		"""This method sets up control of the terminal, in such a way
			that normal and error output messages will only go to the
			console panel, while curses has access to real stdout."""

		client = thisConsoleClient
		virterm = client._virterm

		virterm.release_stdout()
			# Release control of stdout, since curses needs it.

			# Untee out and err.
		virterm.untee()		# Remove the tee handlers from out/err streams.
			
		set_alt_stdout(virterm.out)
			# This tells the logging module to use virterm.out
			# in place of stdout.
		#set_alt_stderr(virterm.err)

		client._hasTerminal = True 


	def releaseTerminal(thisConsoleClient:ConsoleClient):

		"""This method releases control of the terminal, and dumps
			any remaining virtual stdout/stderr messages to real
			stdout/stderr."""

		client = thisConsoleClient
		virterm = client._virterm

			# Tell the console panel to stop consuming log messages.

			# Tell logger to stop using virterm streams.
		set_alt_stderr(None)
		set_alt_stdout(None)
		
			# Tell virterm to stop absorbing stderr.
		virterm.release_stderr()	# Release control of stderr.

			# Tell virterm to spit out any buffered output
		virterm.dump_all()			# Dump everything 

		client._hasTerminal = False


	def start(thisConsoleClient:ConsoleClient, waitForExit:bool=True):
		# NOTE: Here we override the default value of waitForExit 
		# while we're debugging basic console capabilities.
		# We can remove this override once that's done.
		
		_logger.debug("console.start(): Starting the console client...")

		client = thisConsoleClient
		
		# THIS IS VERY IMPORTANT. The superclass .start() method 
		# will start the curses display.  Before we do this, we
		# have to tell our virtual terminal to release control of
		# stdout, so that curses can use it to write directly to 
		# the screen.  At the same time, we have to tell the logging
		# facility to start using the virterm's virtual out stream
		# instead of normal stdout for normal-level messages, so
		# that those messages will appear in the console panel.

		client.grabTerminal()	# Configures stdio for console.

		# The following try/except is needed so we can see output
		# to the virtual terminal in case of exceptions.
		try:
			# Note: We do this last, because it will never return if
			# waitForExit is not False.
			super(ConsoleClient, client).start(waitForExit=waitForExit)
			# Calls DisplayClient's .start() method.

		# This code needs to be moved somewhere else.
		finally:
			if waitForExit:		# If true, then display has exited. Clean up.
				releaseTerminal()	# Restores normal stdio

		_logger.debug("console.start(): Returning.")
	
	#__/ End method console.start().
	

	def setSupervisor(thisConsoleClient:ConsoleClient, supervisor:Supervisor):
		"""Inform the console client of who is the system supervisor."""
		client = thisConsoleClient
		client._supervisor = supervisor
		
	@property
	def supervisor(thisConsoleClient:ConsoleClient):
		return thisConsoleClient._supervisor
	
	def setActionSystem(thisConsoleClient:ConsoleClient, actionSystem:TheActionSystem):
	
		"""Tell the console client what action system to use for reporting."""
		
		client = thisConsoleClient
		client._actionSystem = actionSystem

	def setMind(thisConsoleClient:ConsoleClient, cognoSys:TheCognitiveSystem):
	
		"""Give the console client a pointer to the cognitive system whose
			receptive field it will be displaying.  A side effect of this is
			that we then immediately "read the AI's mind" (receptive field) 
			and display its contents."""
			
		client = thisConsoleClient
		client._cognosys = cognoSys
		
		client.refreshFieldDisplay()
			# This tells the console client to update its receptive field display
			# now that it has access to the AI's mind.
			
	def refreshFieldDisplay(thisConsoleClient:ConsoleClient):
	
		client 	= thisConsoleClient
		fdisp	= client.fieldDisplay
		
		fdisp.refresh()		# Tells the field display to refresh itself.
	
	@property
	def mind(thisConsoleClient:ConsoleClient):
		return thisConsoleClient._cognosys
	
	def prepareForShutdown(thisConsoleClient:ConsoleClient):

		"""This method is called to notify the client that it should
			prepare for an imminent shutdown of the display."""

		# Tell the console panel to stop consuming messages from the VirTerm.
		client = thisConsoleClient
		consPanel = client._consPanel
		consPanel.stop()	# Stop what you're doing!


	def notifyShutdown(thisConsoleClient:ConsoleClient):

		"""This method is called to notify the client that the display
			has shut down, in case it doesn't know yet."""

		client = thisConsoleClient
		supervisor = client.supervisor

			# Do we still have control of the terminal?
		if client._hasTerminal:
			client.releaseTerminal()	# Release it.

			# Also, ask the supervisor to exit.
		supervisor.requestExit()
	
#__/ End class ConsoleClient.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	console/console.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
