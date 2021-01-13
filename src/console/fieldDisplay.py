# fieldDisplay.py
# Contains a panel type to display all or part of the receptive field,
# and a class FieldDisplay to manage this/these panels.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from os import path
from infrastructure.logmaster import (
		sysName,			# Used just below.
		ThreadActor,		# Blink timer thread is subclassed from this.
		getComponentLogger,	# Used just below.
		LoggedException,
		WarningException,
	)

global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)  # Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from display.exceptions import (

		RenderExcursion

	)

from display.panel import (

		Panel,			# Base class that FieldPanel inherits from.
	
		FILL_RIGHT,		# Placement designator for right field panel.
		FILL_LEFT		# Placement designator for left field panel.

	)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConsoleClient:	pass

class FieldPanel:		pass
class FieldDisplay:		pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConsoleException(LoggedException):

	"""This is an abstract base class for all exception types generated
		by the console client."""

	defLogger = _logger

class FieldUnavailable(ConsoleException, WarningException):

	"""This is an exception type that is thrown by the field display
		when it is unable to access the receptive field facility."""

	pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FieldPanel(Panel):

	def __init__(newFieldPanel:FieldPanel, fieldDisp:FieldDisplay, column=None):
		# column should be 'right' or 'left' to specify positioning of this panel

		panel = newFieldPanel
		
			# Initialize key private data members.

		panel._fieldDisplay 	= fieldDisp
		panel._column			= column		# 'left' or 'right'
		panel._launched			= False			# Not yet launched.
		
			# Select panel placement.

		if column == 'right':
			placement = FILL_RIGHT		# Fill available space in right column.

		elif column == 'left':
			placement = FILL_LEFT		# Fill available space in left column.

			# General panel initialization.
		super(FieldPanel, panel).__init__(title=None, initPlacement=placement)
			# Field panels are untitled by default, since they are the main focus
			# of the server application in any case.


	def configWin(this):
		
			# Do generic Panel configWin stuff.
		super(FieldPanel, this).configWin()

			# Make sure leaveok is true so cursor doesn't move too much.
		#win = panel.win
		#win.leaveok(True)

		this.clear()	# Clears the data content of the panel.
		

	@property
	def fieldDisplay(thisFieldPanel:FieldPanel):
		return thisFieldPanel._fieldDisplay
	
	@property
	def column(thisFieldPanel:FieldPanel):
		return thisFieldPanel._column	# 'left' or 'right'
	
	@property
	def launched(thisFieldPanel:FieldPanel):
		return thisFieldPanel._launched

	def clear(thisFieldPanel:FieldPanel):
		
		"""Clear the data content of this panel."""

		panel = thisFieldPanel
		client = panel.client
		display = client.display

		panel._data				= []			# Array of items (text strings) in panel.
		panel._nChars			= 0				# Number of characters of text data (includes newlines, etc.).
		panel._nLines			= 0				# Numbers of lines' worth of text data (to make sure we don't overflow panel).		
		panel._filled			= False			# Not yet filled up with data, obviously.

			# Actually go ahead and erase the panel's window too, in its backing store.
		if client.dispRunning:
			with display.lock:
				win = panel.win
				if win is not None:
					win.erase()

	@property
	def data(thisFieldPanel:FieldPanel):
		"Returns the entire current dataset."
		return thisFieldPanel._data
	
	@property
	def nChars(thisFieldPanel:FieldPanel):
		"Returns the total number of characters in the data."
		return thisFieldPanel._nChars

	@property
	def filled(thisFieldPanel:FieldPanel):
		return thisFieldPanel._filled
	
	def hasRoom(thisFieldPanel:FieldPanel, item:str):
	
		"""Returns True if the panel has room to contain the data item,
			False otherwise."""
	
		pass
	
	def addItem(thisFieldPanel:FieldPanel, item:str):
	
		"""Adds one item to the data content of this panel."""
		
		panel = thisFieldPanel
		client = panel.client
		display = client.display
		win = panel.win
		
		nChars = len(item)
		
		# If the display isn't running yet, or there's no sub-window yet,
		# we can't actually to a trial display of the item, so just finish up.
		if not client.dispRunning or win is None:
			# Go ahead and add the item onto the end of the data list.
			panel._data.append(item)
				# Accumulate the total number of characters.
			panel._nChars = panel._nChars + nChars
			return

		# Go ahead and try rendering the item.
		try:
			with display.lock:
				display.renderText(item, win=win)
		
		except RenderExcursion as excursion:
			# If we get here, this means that we went outside the window,
			# and the whole item didn't get added.  Instead, we just added
			# some piece of it.
			
			pos = excursion._pos	# The position in the item where we went out.
			
			# Remember that we only had room for part of the item, up until
			# the position that choked.
			if pos > 0:
				item = item[:pos]
				nChars = pos
			
			# Re-raise the excursion exception so that our caller will know
			# that the entire item wasn't added.
			raise excursion
		
		finally:
			# After all that mess, on the way out, we need to make sure
			# we remember what we actually added to the panel.
		
			# Go ahead and add the item onto the end of the data list.
			panel._data.append(item)
				# Accumulate the total number of characters.
			panel._nChars = panel._nChars + nChars
		
		#__/ End try/except/finally for rendering an item to the panel.

	def markFull(thisFieldPanel:FieldPanel):
		
		"""Mark this panel as having been filled, so that we don't try to 
			put any more data into it."""
			
		thisFieldPanel._filled = True

	def launch(thisFieldPanel:FieldPanel):
	
		"""This gets called automatically in Panel's .drawContent method
			when the panel is first displayed.  We use it to tell us when
			the overall field display should be ready to launch."""
			
		panel = thisFieldPanel
		fdisp = panel.fieldDisplay
		whichCol = panel.column

		# Mark this panel as having been launched.
		panel._launched = True
		
			# Tell the field display that this panel has launched.
		fdisp.notifyLaunch(whichCol)

	def drawContent(thisFieldPanel:FieldPanel):
	
		"""This is a standard Panel method that is called to fill in
			the content of a blank panel."""

		panel = thisFieldPanel
		client = panel.client
		display = client.display
		win = panel.win
		
		data = panel.data

		for item in data:
			display.renderText(item, win=win)

			# Now call the original method in Panel, which does some 
			# general bookkeeping work needed for all panels.		
		super(FieldPanel, panel).drawContent()
		

class FieldDisplay:

	def __init__(newFieldDisplay:FieldDisplay, client:ConsoleClient):

		"""Initialize the field display, including creating its panels."""
		
		_logger.info("[FieldDisplay] Initializing field display.")

		fieldDisp = newFieldDisplay
		
		fieldDisp._client = client
		fieldDisp._launched = False 	# Becomes True after both panels are launched.
		fieldDisp._field = None			# Receptive field is not attached yet.
		fieldDisp._data = None			# No field data loaded yet.
		fieldDisp._nChars = None		# Field character count = undefined.
		fieldDisp._nTokens = None		# Field data size = undefined.
		
		fieldDisp._rFieldPanel	= rightFieldPanel 	= FieldPanel(fieldDisp, column='right')
		fieldDisp._lFieldPanel	= leftFieldPanel	= FieldPanel(fieldDisp, column='left')
	
	@property
	def client(thisFieldDisplay:FieldDisplay):
		return thisFieldDisplay._client

	@property
	def field(thisFieldDisplay:FieldDisplay):
		return thisFieldDisplay._field

	@property
	def data(fd):
		return fd._data

	@property
	def nChars(fd):
		return fd._nChars

	@property
	def nTokens(fd):
		return fd._nTokens

	@property
	def leftPanel(thisFieldDisplay:FieldDisplay):
		return thisFieldDisplay._lFieldPanel

	@property
	def rightPanel(thisFieldDisplay:FieldDisplay):
		return thisFieldDisplay._rFieldPanel

	def addPanels(thisFieldDisplay:FieldDisplay):
		
		"""Tells this field display to add its panels to the given
			console client."""
		
		fieldDisplay	= thisFieldDisplay
		rFieldPanel		= fieldDisplay._rFieldPanel
		lFieldPanel		= fieldDisplay._lFieldPanel
		client			= fieldDisplay.client
		
		client.addPanel(rFieldPanel)	# This fills the rest of the right-hand column.
		client.addPanel(lFieldPanel)	# This fills the rest of the left-hand column.

	def notifyLaunch(thisFieldDisplay:FieldDisplay, whichColumn:str):
	
		fdisp = thisFieldDisplay
		lpanel = fdisp.leftPanel
		rpanel = fdisp.rightPanel
		
			# Check whether this was the last field panel that we were waiting
			# to have been launched.
		if lpanel.launched and rpanel.launched:
			
				# Now, both panels have been launched. 
				# Time to launch the entire field display.
			fdisp.launch()
	
	def launch(thisFieldDisplay:FieldDisplay):
		"""Starts the field display actively working.  This is called automatically
			once both of the individual field panels have been launched."""
		
		fdisp = thisFieldDisplay
		client = fdisp.client
		display = client.display
		driver = display.driver
	
		_logger.info("[FieldDisplay] Launching field display.")
	
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	OK, at this point, both field panels are up and running, and are 
		#|	ready to begin displaying stuff.  So, this is a good time for us 
		#|	to query the cognitive system to say, "Please give us the current 
		#|	field contents."  We then store this information here, so that it 
		#|	can be referenced whenever the field panels need to be redrawn.  
		#|	We also go ahead and distribute the field information appropriately 
		#|	across the two panels, and tell the display driver to repaint both 
		#|	panels.  Most future panel updates will be driven by the cognitive
		#|	system's main loop:  Whenever the field contents change, this 
		#|	field display will be given the new data, and instructed to update 
		#|	itself.  Also, events like resizes may trigger us to redistribute
		#|	field data between the panels.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		if client.mind is not None:
			fdisp.refresh()		# Refresh the field display from source data.
		
			# Mark the field display as having been launched.
		fdisp._launched = True 

	def refresh(thisFieldDisplay:FieldDisplay):
	
		"""Tells the field display to refresh itself from field data."""
		
		fdisp = thisFieldDisplay
		client = fdisp.client
		display = client.display
		driver = display.driver

		fdisp.queryField()		# Query the receptive field for its contents.
		fdisp.refillPanels()	# Refill the field panels with data.
		driver.do(fdisp.repaintPanels, desc="Repaint field display panels.")
			# As a background task, have the display driver repaint both panels.
			# This needs to be a background task to avoid recursion.

	def attachField(thisFieldDisplay:FieldDisplay):

		fdisp	= thisFieldDisplay	# This field display.
		
		client	= fdisp.client		# The overall console client.
		mind	= client.mind		# The AI's cognitive system.
		field	= mind.field		# The AI's receptive field.
			
		fdisp._field = field		# Remember this reference.
	
	def queryField(thisFieldDisplay:FieldDisplay):
	
		"""Queries the receptive field to retrieve its current contents.
			This is then cached in the field display."""
		
		fdisp	= thisFieldDisplay	# This field display.
		
		# If the mind hasn't been set, we can't do anything yet.
		client	= fdisp.client		# The overall console client.
		mind	= client.mind		# The AI's cognitive system.
		
		if mind is None:
			_logger.warn("fieldDisplay.queryField(): Receptive field is not available yet.")
			raise FieldUnavailable("fieldDisplay.queryField(): Receptive field unavailable.")

		# Attach to the field if it's not already attached.
		if fdisp.field is None:
			fdisp.attachField()
		field = fdisp.field
		
		_logger.debug("fieldDisplay.queryField(): Querying receptive field for its data.")

			# Ask the receptive field to give us its data (list of items).
		fdisp._data = field.getData()
		
			# Also, go ahead and get the count of the number of tokens
			# and characters in the field data, for later reference.
		fdisp._nTokens = field.nTokens()
		fdisp._nChars = field.nChars()
		
	
	def refillPanels(thisFieldDisplay:FieldDisplay):
	
		"""Take our presently-cached field data (a list of strings)
			and re-distribute it over the available field panels."""
			
		fdisp = thisFieldDisplay	# This field display.
		data = fdisp.data			# Get current data.
		ntoks = fdisp.nTokens		# Get current data's # of tokens.
		nchars = fdisp.nChars		# Get current data's # of characters.
				
		fdisp.clearPanels()		# Empty out both of the panels.
		
		# Loop over the data items, adding them to the display.
		for item in data:
			fdisp.addItem(item)		# Add this item.

			# Add to the end of the visible dataset an item showing the 
			# current count of total characters and tokens in the field.
		fdisp.addItem(f"\n[{nchars} characters, {ntoks} tokens]")


	def clearPanels(thisFieldDisplay:FieldDisplay):
	
		"""Clears both panels, so that they contain no data yet."""
		
		fdisp 	= thisFieldDisplay	# This field display.
		lpanel	= fdisp.leftPanel	# Field panel in left column.
		rpanel	= fdisp.rightPanel	# Field panel in right column.
		
		lpanel.clear()
		rpanel.clear()
		
	def addItem(thisFieldDisplay:FieldDisplay, item:str):
	
		"""Given a field item (string), add it to the display.  This
			involves adding it to the left panel, unless the left panel
			has already filled, in which case we add it to the right panel."""
			
		fdisp 	= thisFieldDisplay	# This field display.
		lpanel	= fdisp.leftPanel	# Field panel in left column.
		rpanel	= fdisp.rightPanel	# Field panel in right column.
		
		# This "infinite loop" actually only iterates at most twice, if the
		# item overflows off the first panel and needs to spill over to the 2nd.
		while True:
		
			# Select which panel to try to add it to.
			if lpanel.filled:
				panel = rpanel
			else:
				panel = lpanel
			
			# Do this within a try/except so that if we run out of room for the item in 
			# the panel, we can handle that.
			try:
				panel.addItem(item)
			
			except RenderExcursion as excursion:
				
					# Remember that that panel is now full, so that we won't try to add
					# anything to it again.
				panel.markFull()
				
					# What we have left to add is the rest of the item after we ran out of room.
				item = item[pos:]
				
				continue	# Go back to top and try adding the rest of the item.
			
			else:		# No exceptions?
				break	# Then we're done adding the item; stop.
				
			#__/ End try/except/else for adding item to panel.

			#/---------------------------
			#|	We should never get here.
			#\---------------------------

		#__/ End while not done adding item.
		
			
	def repaintPanels(thisFieldDisplay:FieldDisplay):
		
		"""Redisplays both panels."""
		
		fdisp 	= thisFieldDisplay
		client	= fdisp.client
		display	= client.display
		
		lpanel	= fdisp.leftPanel	# Field panel in left column.
		rpanel	= fdisp.rightPanel	# Field panel in right column.

			# Regenerate drawn content of both panels.
		lpanel.regenerateContent()
		rpanel.regenerateContent()
		
			# Tell the physical display to update itself now.
		display.update()
		
