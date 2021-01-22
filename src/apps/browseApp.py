# browseApp.py 

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Browse_App(Application_):

	"""
	Browse - This is a simple text-based tool to facilitate simple web
	browsing and searching.
	"""

	pass

