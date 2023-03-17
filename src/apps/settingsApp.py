# settingsApp.py

from	infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Settings_App(Application_):

	"""
	Settings - This app can be used by the A.I. to adjust various
	settings within GLaDOS.	 These can be associated with major
	systems or subsystems of GLaDOS, or individual apps or
	processes.
	"""

	pass

