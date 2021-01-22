# writingApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Writing_App(Application_):

	"""
	The writing tool is an interface that helps the A.I.
	to compose and edit complex, hierarchically-structured works:
	Stories, poems, and extended multi-chapter books.
	"""

	pass

