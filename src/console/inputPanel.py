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

		Event,				# For an event representing the operator's input.
		
	)

class BlinkTimer: pass
class InputPanel: pass

class BlinkTimer(ThreadActor):
	
	defaultRole = 'BlinkTmr'
	defaultComponent = _sw_component
	
	def __init__(newBlinkTimer:BlinkTimer, inputPanel:InputPanel):
		timer = newBlinkTimer
		timer._inputPanel = inputPanel
		timer._defaultTarget = timer._main
		timer._exitRequested = False
		super(BlinkTimer, timer).__init__(daemon=True)	# ThreadActor initialization.
			# The daemon=True tells Python not to let this thread keep the process alive.
			
	def _main(thisBlinkTimer:BlinkTimer):
		timer = thisBlinkTimer

		while not timer._exitRequested:

			# The full blink cycle is 1 second.  Blink on, wait half abs
			# second, blink off, wait half a second.
		
			timer.blinkOn()		# Turn cursor A_BLINK on.
			
			sleep(0.5)			# Sleep half a second.
			
			timer.blinkOff()	# Turn cursor A_BLINK off.
			
			sleep(0.5)			# Sleep half a second.
			
	def blinkOn(thisBlinkTimer:BlinkTimer):
		timer = thisBlinkTimer
		
	def blinkOff(thisBlinkTimer:BlinkTimer)
		timer = thisBlinkTimer
			

class InputPanel(Panel):

	"""Panel for prompting for and accepting input from the operator."""
	
	def __init__(newInputPanel:InputPanel):
			
			# Use a shorter name for this new log panel.
		panel = newInputPanel
		
			# First we do general panel initialization.
		super(InputPanel, panel).__init__("Operator Input", FILL_BOTTOM, 4)
			# Default height of 4 is fine.
		
			# Create and store the operator entity.
		operator = Operator_Entity()
		panel._operatorEntity = operator
		
			# Create and store the draft input event.
		
