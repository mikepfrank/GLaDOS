# goalsApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Goals_App(Application_):

	"""
	The 'Goals' app can be used by the A.I. to modify its list
	of high-level goals.
	"""

	pass

