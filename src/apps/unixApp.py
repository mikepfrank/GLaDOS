# unixApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Unix_App(Application_):

	"""
	This app gives the A.I. access to an actual Unix shell
	environment on the host system that GLaDOS is running on.  The A.I.
	runs within its own user account with limited permissions.
	"""

	pass
