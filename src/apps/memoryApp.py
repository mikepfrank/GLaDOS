# memoryApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Memory_App(Application_):

	"""
	Memory - The memory tool allows the A.I. to browse and search
	a database of records of its past conversations, thoughts, and
	actions.
	"""

	pass

