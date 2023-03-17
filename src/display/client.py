#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 display/client.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""	FILE NAME:		display/client.py				 [Python module source file]
	
	MODULE NAME:	display.client
	IN PACKAGE:		display
	FULL PATH:		$GIT_ROOT/GLaDOS/src/display/client.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.display (Display screen management)


	MODULE DESCRIPTION:
	===================

		This module defines a general base class called DisplayClient;
		more specific display clients should inherit from this class.
		
		If DisplayClient is instantiated directly, it runs a simple 
		demo.
	
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	1.  Exported name list. 		   				   [module code section]
	#|
	#|			Here we list all of the public names that are standardly
	#|			exported from this module, if the using module does:
	#|
	#|						from display.client import *
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
global __all__ 
__all__ = [		# List of all public names exported from this module.

			#|---------
			#| Classes.
		
		'DisplayClient',	# Base class for display clients.
		
	]


	#|==========================================================================
	#| 	2.	Imports.									   [module code section]
	#|
	#|		2.1.  Standard Python modules imported into this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from os import path	# Manipulate filesystem path strings.

import curses
from curses import *
	# At some point we should change this to an explicit list of the
	# curses names that we actually use.

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	2.2.  Custom imports.						[module code subsection]
		#|
		#|		Here we import various local/application-specific 
		#|		modules that we need.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------
			#| Logging-related stuff.

from infrastructure.logmaster import (
		sysName,			# Used just below.
		getComponentLogger,	# Used just below.
	)
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.
global _sw_component
_sw_component = sysName + '.' + _component


#-------------------------------------------------------------------------------

from .display import TheDisplay		# Singleton class for curses display interface.

from .keys import KeyEvent

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	display.DisplayClient					   [public extensible class]
		#|
		#|		This class, which can and should be further subclassed 
		#|		by other modules that are using this module, defines the 
		#|		detailed behavior of the primary client process that is 
		#|		using the display.
		#|
		#|		Key methods that subclasses should override include
		#|		the following:
		#|
		#|
		#|			.paint() -
		#|
		#|				This method should repaint the entire display 
		#|				with (client-specific) content.
		#|
		#|
		#|			.handle_event()	-
		#|
		#|				This method is called by the display driver
		#|				for each input event that occurs.
		#|
		#|		
		#|		If this class is instantiated directly, the resulting
		#|		client just provides some simple demo functionality, 
		#|		displaying information about the window size, input
		#|		events, and a simple character table.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class DisplayClient:
	"""DisplayClient											  [public class]
	
				A display client is an entity that uses the display 
				as a server to interact with the user.	Only one 
				client may use the display at a time.						 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	newClient.__init__()						  	  [instance initializer]
	#|
	#|		Currently, this initializer for new client instances simply 
	#|		links up the client with the display (i.e., the singleton 
	#|		instance of TheDisplay class).
	#|
	#|		Subclasses that need override to this method to do application-
	#|		specific initialization should do it by extending this method, 
	#|		by first calling their superclass initializer using the 
	#|		standard idiom,
	#|
	#|			super(SubClassName, this).__init__(this, *args, **kwargs),
	#|
	#|		before doing their application-specific initialization work.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	def __init__(newClient):
		"""Initializes the client by linking it with the display."""
		
			# Connect us up with the display, creating it if needed.
		newClient._display = display = TheDisplay()
		display.setClient(newClient)
		
	#__/ End instance initializer for class DisplayClient.


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def start(thisClient, waitForExit:bool=False):		
		"""displayClient.start()						[public instance method]
		
				This method starts up the display client, which 
				implicitly also starts up the underlying curses-
				based display infrastructure.								 
			
			Arguments:
			
				waitForExit [boolean] - Optional argument.  If this is True, 
					then this method will not return until the display is 
					terminated; otherwise, it will lauch the display in the 
					background.  This option is False by default.			 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
		_logger.debug("displayClient.start(): Starting with " 
			f"waitForExit={waitForExit}...")

		client  = thisClient
		display = client.display
		
			# This starts up the display, and waits for it to exit if 
			# waitForExit is true.
		display.start(waitForExit = waitForExit)

		_logger.debug("displayClient.start(): Returning.")
		
	#__/ End instance method displayClient.start().

	def prepareForShutdown(thisClient):
		"""This method is called to notify the client that it should
			prepare for an imminent shutdown of the display."""
		pass

	def notifyShutdown(thisClient):
		"""This method is called to notify the client that the display
			has shut down."""
		pass

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	client.display					  	  	   		   [public property]
		#|
		#|		This retrieves the display that the client is connected
		#|		to (which should be the singleton instance of TheDisplay).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	@property
	def display(thisClient):
		"""The display to which this client is connected."""
		return thisClient._display

	@property
	def dispRunning(thisClient):
		"""This property is Boolean 'True' if this client's display is currently running."""
		return thisClient.display.isRunning
	
	@property
	def screen(thisClient):
		"""The screen (top-level window) of the display to which the client is 
			connected."""
		return thisClient.display.screen

	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def requestRefresh(thisClient):
		"""client.requestRefresh()			  [sensitive public instance method]
		
				This method tells the client to request the display to 
				refresh the client's screen as needed on the next update
				of the display screen.										 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
			# Marks the entire screen as needing refreshing.
		thisClient.screen.noutrefresh()
			# The actual (physical) external refresh of the display terminal will
			# occur on the next call to display.update().

	#__/ End sensitive public instance method client.requestRefresh().
	

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def redisplay(thisClient):
		"""client.redisplay()				  [sensitive public instance method]
		
				Tells the client to regenerate its display. This works by 
				calling the display's .paint() method, which then dis-
				patches the detailed drawing work back to the client.		 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		display = thisClient.display
		display.paint()

	#__/ End sensitive public instance method client.redisplay().
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def updateDisplay(thisClient):
		
		"""Updates the physical display to reflect any recent behind-the scenes
			changes to the client's main screen and/or other windows."""

		client = thisClient
		display = client.display

		display.update()

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	client.addChar()			  	  [sensitive public instance method]
		#|
		#|		This method can be used to send a character to the 
		#|		client's display, with special rendering features 
		#|		available for (normally) non-printing characters.
		#|
		#|		TO DO: Implement processing of optional loc and 
		#|		attr arguments (not yet supported).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def addChar(thisClient, char:int, *args, **argv):
		"""Puts a character on the display, with special rendering
			for normally non-printing characters."""
		display = thisClient.display
		display.renderChar(char, *args, **argv)


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	client.addText()			  	  [sensitive public instance method]
		#|
		#|		This method can be used to send plain text to the 
		#|		client's display.  By "plain text," we mean that 
		#|		non-printing characters are not handled specially.
		#|
		#|		TO DO: Add an option to enable special handling of
		#|		non-printing characters.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def addText(thisClient, text:str, *args, **argv):
		"""Puts the given plain text on the client's display screen."""
		display = thisClient._display
		display.add_str(text, *args, **argv)


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	client.drawOuterBorder()	  	  [sensitive public instance method]
		#|
		#|		This method draws a border just inside the edge of the
		#|		display screen, using the predefined BORDER render style.
		#|
		#|		Presently, this renders by default in a bright cyan text
		#|		color on a black background.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def drawOuterBorder(thisClient):
		"""Draw a border just inside the edge of the display screen."""

		client = thisClient
		display = client.display
		display.drawOuterBorder()	# Let the display do the actual work.

	#__/ End method displayClient.drawOuterBorder().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	client.paint()		  [placeholder sensitive public instance method]
		#|
		#|		This is the main method that subclasses should override
		#|		to draw their display contents.
		#|
		#|		The version defined here essentially implements a simple
		#|		demo, which displays a border and some diagnostics of the
		#|		window size, the last event received, and a character table.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def paint(thisClient):
		"""Subclasses should override/extend this method to paint their 
			client's display.  The display.paint() method calls this method
			when needed, so clients should not need to call it directly."""

			# Get some important guys.
		client = thisClient
		display = client.display
		screen = display.screen
		
			# First, if the display isn't even running, then there's nothing
			# to do, so just exit early.
		if not display.running:
			_logger.debug("client.paint(): Display is not yet running; returning early.")
			return

		_logger.debug("client.paint(): Painting client display...")
		
			# This is effectively a "lazy clear"--it waits until refresh to take effect.
		display.erase()		# Marks all character cells as empty (and no attributes).
				# (We do this so we don't have to worry about old text hanging around.)

			# Draw a border just inside the edges of the screen.
		display.drawOuterBorder()
		
			# Display information about the screen size.
		(height, width) = display.get_size()
		client.addText(f"Screen size is {height} rows high x {width} columns wide.", Loc(1,2))

			# If we've received any events yet, display the last one received.
		if hasattr(client, '_lastEvent'):
			client.displayEvent()

		#|----------------------------------------------------------------
		#| Next, draw a character table.  (Code points 0x0 through 0x17F.)

			# Iterate through all character codes in our displayable range.
		for ch in range(0, 384):	# This will fill 12 rows.
		
				# Calculate coordinates for this character.
			y = 7 + int(ch/32)
			x = 2 + 2*int(ch%32)
		
				# Render the character at the given location.
			screen.move(y, x)
			client.addChar(ch)		# TODO: Add an optional loc argument.
			
		#__/ End loop over code points.

		#/----------------------------------------------------------------------
		#| 	display.paint() handles refresh for us automatically, so we don't 
		#|	need to do it here. So, we're done!
		#\----------------------------------------------------------------------
	
	#__/ End method displayClient.paint().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.displayEvent()				[public instance method]
		#|
		#|		This method is just here to support the demo application; 
		#|		it displays some information about the last event received.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def displayEvent(thisClient):

		client 		= thisClient
		
		keyevent	= client._lastEvent
		keycode		= keyevent.keycode
		keyname		= keyevent.keyname
		ctlname		= keyevent.ctlname

			# Default behavior: Display information about key code received.
		client.addText(f"Received key code: #{keycode}.",	Loc(3,2))
		client.addText(f"Direct rendering is: ", 			Loc(4,2))
		client.addChar(keycode)		# What if we interpret keycode directly as a character?
		client.addText(f"Key name string is: ({keyname})",	Loc(5,2))
		client.addText(f"Control name is: ({ctlname})",		Loc(6,2))

	#__/ End method displayClient.displayEvent().


	def handle_resize(thisClient):
		"""When we have already figured out the new screen size, this method
			is called by the display to let us do client-specific adjustments."""
		# There is nothing to do here by default for the demo client, but 
		# subclasses should override this.
		pass
		

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.handle_event()	[placeholder public instance method]
		#|
		#|		This is the main event handler method.  It is called by
		#|		the display driver when there is a key event that needs
		#|		to be handled by the client.
		#|
		#|		Subclasses may want to override this method as appropriate
		#|		for their application.  The display (singleton instance of 
		#|		TheDisplay) will call this method whenever a new key event 
		#|		is received.  The implementation of this method should then
		#|		dispatch the event to sub-handlers as appropriate.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
	def handle_event(thisClient, keyevent:KeyEvent):
	
		"""Subclasses should override this method with their own event handler."""

			# Get some important guys.
		client = thisClient
		display = client.display
		
		keycode = keyevent.keycode		# Numeric code for key or other event.
		keyname = keyevent.keyname		# String name for key or event.
		ctlname = keyevent.ctlname		# If control/whitespace, standard name of control.
		
		_logger.debug(f"Got a key with code={keycode}, name={keyname}, ctl={ctlname}.")
		
			# This next line is just here to support our demo application, and may 
			# not be needed in all subclasses' replacements for this method.
		client._lastEvent = keyevent

			# The following code block or similar will be in most applications.
			# We call back to the display to tell it to resize itself.
		# This is commented out because resize is now dispatched automatically
		# from display._do1iteration().
		#if keycode == KEY_RESIZE:
		#	display.resize()

		# The following is commented out because generally there's no need to
		# repaint the entire display just because a key was pressed.
		#else:
		#	client.paint()

	#__/ End method displayClient.handle_event().


	#XXXXXXXXXXXXXXXXXXXXX		SCRAPS BELOW HERE	XXXXXXXXXXXXXXXXXXXXXXXX
	

	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	displayClient.run()						  	[public instance method]
		#|
		#|		This is the method that should be called to start the 
		#|		display client running.  It automatically starts up the
		#|		entire display facility as well, paints the screen, and 
		#|		starts up the main event loop.  It does not return until 
		#|		there is an application abort or quit, so, users should
		#|		probably create a new thread to run it in.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	# Commented out because display now runs in its own thread which is 
	# started automatically by .start().
	
	#def run(thisClient):
	#	display = thisClient.display
	#	display.run()


#__/ End class displayClient.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|						END OF FILE:	display/client.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
