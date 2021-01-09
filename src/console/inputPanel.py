# inputPanel.py

from time		import	sleep		# Causes thread to give up control for a period.  Used in BlinkTimer.
from os 		import 	path

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
		opTextEvent = Event("", author=operator, defaultFormat=FullEventFormat)
			# Note the text of the event is just the empty string initially.
			# It will expand as the operator types text.
		panel._opTextEvent = opTextEvent	# Operator's text event.
			
			# Create the prompt timer thread (see above).
			# Its job will be to update the time displayed in the
			# operator's input prompt.
		timerThread = PromptTimer(panel)
		panel._promptTimer = timerThread

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
		
		driver(panel.redisplayContent, "Redisplay input panel contents")

	@property
	def textEvent(thisInputPanel:InputPanel):
		panel = thisInputPanel
		return panel._opTextEvent


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
		display.renderText(displayText, win=win)
			# Note this method does special stuff with various control
			# and whitespace characters.

			# Call the original drawContent() method in Panel, which does 
			# some general bookkeeping work needed for all panels.
		super(InputPanel, panel).drawContent()
			
	#__/ End instance method inputPanel.drawContent().