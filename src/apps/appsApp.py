# appsApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		#----------------------------------------------------------
		# NOTE: At the moment, the 'Apps' app is not needed because
		# the help window already lists all the apps.

@singleton
class The_Apps_App(Application_):

	"""
	Apps - This tool simply displays the list of all the
	available apps, and allows the A.I. to select one to
	launch.
	"""

	pass

