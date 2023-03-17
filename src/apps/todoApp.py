# todoApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_ToDo_App(Application_):

	"""
	ToDo - The idea of this app is that it is a simple to-do list
	tool, which the A.I. can use to make notes to itself of important
	tasks that it wants to do later.  The tasks can be given priority
	levels.	 The A.I. can check them off or delete them when complete.
	"""

	pass

