# fieldDisplay.py
# Contains a panel type to display all or part of the receptive field,
# and a class FieldDisplay to manage this/these panels.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from os import path
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from display.panel import (

		Panel,			# Base class that FieldPanel inherits from.
	
		FILL_RIGHT,		# Placement designator for right field panel.
		FILL_LEFT		# Placement designator for left field panel.

	)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConsoleClient:	pass

class FieldPanel:		pass
class FieldDisplay:		pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FieldPanel(Panel):

	def __init__(newFieldPanel:FieldPanel, fieldDisp:FieldDisplay, column=None):
		# column should be 'right' or 'left' to specify positioning of this panel

		panel = newFieldPanel
		
			# Initialize key private data members.

		panel._fieldDisplay 	= fieldDisp
		panel._column			= column		# 'left' or 'right'
		
		panel._texts			= []			# Array of text strings in panel.
		panel._nChars			= 0				# Number of characters of text data (includes newlines, etc.).
		panel._nLines			= 0				# Numbers of lines' worth of text data (to make sure we don't overflow panel).

			# Select panel placement.

		if column == 'right':
			placement = FILL_RIGHT		# Fill available space in right column.

		elif column == 'left':
			placement = FILL_LEFT		# Fill available space in left column.

			# General panel initialization.
		super(FieldPanel, panel).__init__(title=None, initPlacement=placement)
			# Field panels are untitled by default, since they are the main focus
			# of the server application in any case.
		

class FieldDisplay:

	def __init__(newFieldDisplay:FieldDisplay, client:ConsoleClient):

		"""Initialize the field display, including creating its panels."""
		
		_logger.info("[FieldDisplay] Initializing field display.")

		fieldDisp = newFieldDisplay
		
		fieldDisp._client = client
		
		fieldDisp._rFieldPanel	= rightFieldPanel 	= FieldPanel(fieldDisp, column='right')
		fieldDisp._lFieldPanel	= leftFieldPanel	= FieldPanel(fieldDisp, column='left')

	@property
	def client(thisFieldDisplay:FieldDisplay):
		return thisFieldDisplay._client

	def addPanels(thisFieldDisplay:FieldDisplay):
		
		"""Tells this field display to add its panels to the given
			console client."""
		
		fieldDisplay	= thisFieldDisplay
		rFieldPanel		= fieldDisplay._rFieldPanel
		lFieldPanel		= fieldDisplay._lFieldPanel
		client			= fieldDisplay.client
		
		client.addPanel(rFieldPanel)	# This fills the rest of the right-hand column.
		client.addPanel(lFieldPanel)	# This fills the rest of the left-hand column.

	
