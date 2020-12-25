# settings.py
#
# 	This module defines a facility that provides organized access to various 
# 	system and application settings.  This is utilized by the Settings app
# 	(in the 'apps' package).
#
#	The module is anchored in the singleton class TheSettingsFacility.
#	The main class of the module is called SettingsModule, and it provides
#	essentially a 'directory' of settings.  Instances of SettingsModule can
#	be nested inside of each other.  Each instance has a short name 
#	(identifier used in commands), a longer decription used at the top of
#	the headings window, and an even longer docstring.
#
#	The bottommost element in the Settings module is called a Setting.  Each
#	setting has a short name (identifier), a longer description, and an even 
#	longer docstring.  It also has a Type, and an iterable ValueList (except
#	for settings with very large or continuous ranges).
#
#	Types include the following:
#	
#		Toggle		- Boolean value; toggle switch or checkbox.
#		Enumerated	- Short enumerated list of possible values.
#		Range		- Short range of integers.
#		Integer		- Wide range of integers.
#		Continuous	- Continuous ranges of numbers.
#
#	Types are associated with 'widgets' which are used to display the options.
#	(Is this going overboard?)

	#|==========================================================================
	#|
	#|	1. Module imports.								   [module code section]
	#|
	#|		Load and import names of (and/or names from) various
	#|		other python modules and pacakges for use from within
	#|		the present module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	collections.abc		import	Callable, Iterable
	# Types for settings update methods, settings lists.

from 	os			import	path	# For manipulating filesystem paths.


		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from 	infrastructure.decorators 	import singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from 	infrastructure.logmaster 	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))				# Our package name.
_logger = getComponentLogger(_component)						# Create the component logger.


	#|==========================================================================
	#|
	#| 	Forward class declarations. 							  [code section]
	#|
	#|		Here we declare classes to be defined later in this module.
	#|		(Basically, this is only useful to facilitate type hints.)
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# Top-level classes of this module.
class	SettingsFacility_:		pass	# Abstract base class for settings facility.
class	TheSettingsFacility:	pass	# Singleton class to anchor this module.

	# Classes for the settings hierarchy.
class	Setting:				pass	# An individual setting.
class	SettingsModule:			pass	# A directory of settings.
class	TheRootSettingsModule:	pass	# Singleton: Root of the settings module hierarchy.

	# Setting type classes.
class	SettingType_:			pass	# Abstract base class for setting types.
class	ToggleType:				pass	# Setting types for two-valued settings.
class	EnumeratedType:			pass	# Setting types for short enumerated lists.
class	RangeType:				pass	# Setting types for short integer ranges.
class	IntegerType:			pass	# Setting types for wide integer ranges.
class	ContinuousType:			pass	# Setting types for continues number ranges.

	# Value list classes.
class	ValueList:				pass	# List of possible values, available for some types.


class	Setting:

	def __init__(newSetting:Setting,
			name:str=None,
			settingType:SettingType_=None,
			defaultValue:object=None,
			description:str=None,
			docstring:str=None,
			inModule:SettingsModule=None,
			updateMethod:Callable=None,
		):
		newSetting._name 			= name
		newSetting._type 			= settingType
		newSetting._defaultValue	= defaultValue
		newSetting._description		= description
		newSetting._docstring		= docstring
		newSetting._inModule		= inModule
		newSetting._updateMethod	= updateMethod


class	SettingsModule:

	def __init__(newSettingsModule:SettingsModule,
			name:str=None,
			description:str=None,
			docstring:str=None,
			inModule:SettingsModule=None,
			settings:Iterable=None,
			subModules:Iterable=None,
		):
		newSettingsModule._name			= name
		newSettingsModule._description	= description
		newSettingsModule._docstring	= docstring
		newSettingsModule._inModule		= inModule
		newSettingsModule._settings		= settings
		newSettingsModule._subModules	= subModules


	def installSubmodule(thisSettingsModule:SettingsModule,
			subModule:SettingsModule):

		if thisSettingsModule._subModules is None:
			thisSettingsModule._subModules = []

		thisSettingsModule._subModules = thisSettingsModule._subModules + [subModule]


@singleton
class	TheRootSettingsModule(SettingsModule):

	def __init__(theRootSettingsModule:SettingsModule,
			name:str='glados',
			description:str="GLaDOS Settings",
			docstring:str="""These are the top-level settings of the GLaDOS system.""",
			subModules:Iterable=None,
		):

		"""
		"""

		#/-----------------------------------------------------------
		#| At this point, we could go ahead and create the list of 
		#| top-level settings, but we're not quite ready to do that.
		#\-----------------------------------------------------------

		#/-----------------------------------------------------------
		#| At this point, we could go ahead and create the list of 
		#| top-level submodules, but we're not quite ready to do that.
		#| The eventual list of installed submodules will include:
		#|
		#|		- TheFieldSettingsModule (for the receptive field)
		#|			* Nominal field width.
		#|
		#|		- TheWindowSettingsModule (for the window system)
		#|			* Do windows have side borders by default?
		#|
		#|		- TheAppSettingsModule (for app-specific settings)
		#|
		#|		- TheMindSettingsModule (for the cognitive system)
		#|			* Includes e.g. autoskip settings.
		#|			* What event format to use.
		#|
		#|		- TheAPISettingsModule (for the GPT-3 API)
		#|
		#\-----------------------------------------------------------

			# Delegate completion of instance initialization to the 
			# next class in the class resolution sequence.
		super(TheRootSettingsModule, theRootSettingsModule).__init__(
				name=name, description=description, docstring=docstring,
				inModule=None, settings=None, subModules=None
			)
				# Note that in the above, we make sure that there is no
				# parent settings module, and no settings or submodules
				# initially.


@singleton
class	TheSettingsFacility(SettingsFacility_):

	"""This singleton class anchors the settings module."""

	def __init__(theSettingsFacility:TheSettingsFacility, *args, **kwargs):

		theSettingsFacility._rootSettingsModule = TheRootSettingsModule()
		
