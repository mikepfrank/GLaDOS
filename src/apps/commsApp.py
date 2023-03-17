# commsApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Comms_App(Application_):

	"""
	The "comms" tool faciltates the A.I.'s two-way
	communications with the outside world.	This may include direct
	messages sent via Telegram, email messages, or other interfaces.
	This may be broken out later into a whole 'Comms' subfolder of
	separate apps.
	"""

	pass

