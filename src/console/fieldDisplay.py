# fieldDisplay.py
# Contains a panel type to display all or part of the receptive field,
# and a class FieldDisplay to manage this/these panels.



class ConsoleClient:	pass

class FieldPanel:		pass
class FieldDisplay:		pass


class FieldPanel:

	def __init__(newFieldPanel:FieldPanel, fieldDisp:FieldDisplay, column=None):
		# column should be 'right' or 'left' to specify positioning of this panel
		fieldPanel = newFieldPanel
		
		fieldPanel._fieldDisplay 	= fieldDisp
		fieldPanel._column			= column		# 'left' or 'right'
		
		fieldPanel._texts			= []			# Array of text strings in panel.
		fieldPanel._nChars			= 0				# Number of characters of text data (includes newlines, etc.).
		fieldPanel._nLines			= 0				# Numbers of lines' worth of text data (to make sure we don't overflow panel).

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
		
		fieldDisp = newFieldDisplay
		
		fieldDisp._client = client
		
		fieldDisp._rFieldPanel	= rightFieldPanel 	= FieldPanel(fieldDisp, column='right')
		fieldDisp._lFieldPanel	= leftFieldPanel	= FieldPanel(fieldDisp, column='left')

	@property
	def client(thisFieldDisplay:FieldDisplay):
		return thisFieldDisplay._client

	def addPanels(thisFieldDisplay:FieldDisplay, client:ConsoleClient):
		
		"""Tells this field display to add its panels to the given
			console client."""
		
		fieldDisplay	= thisFieldDisplay
		client			= fieldDisplay.client
		rFieldPanel		= client._rFieldPanel
		lFieldPanel		= client._lFieldPanel
		
		client.addPanel(rFieldPanel)	# This fills the rest of the right-hand column.
		client.addPanel(lFieldPanel)	# This fills the rest of the left-hand column.

	
