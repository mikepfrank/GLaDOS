#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 settings/settings.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		settings/settings.py		 	 [Python module source file]
		
	MODULE NAME:	settings.settings
	IN PACKAGE:		settings
	FULL PATH:		$GIT_ROOT/GLaDOS/src/settings/settings.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.settings (Settings management facility)


	MODULE DESCRIPTION:
	===================
	
		This Python module provides an implementation of the settings 
		management facility, one of the subsystems of the GLaDOS server.
		
		The purpose of the settings management facility is to provide the 
		underlying infrastructure that is required in order for the AI to 
		be enabled to browse and modify the settings of GLaDOS and its major
		subsystems within the 'Settings' GLaDOS app.
		
		The settings facility is intended to be initialized by a call to 
		the singleton class constructor TheSettingsFacility(), after config
		files are loaded but before any other subsystems are initialized.
		
		The facility maintains a hierarchy of "settings modules," rooted at
		the top-level module (singleton class) TheRootSettingsModule().
		
		As the various other subsystems of GLaDOS are created and initialized,
		they should each construct their own settings modules and Settings 
		objects, and insert them at the appropriate locations within the 
		existing settings module hierarchy.  Thus, after the system has 
		finished initializing, all of the settings modules will be in place. 
		
		The settings facility will eventually support a full suspend/resume
		capability, in which all settings are saved to a file when the system
		suspends operation, and reloaded when the system resumes operation.
		However, in general, suspend/resume is not implemented in GLaDOS yet.
	
	
	PUBLIC DEFINITIONS:
	-------------------
	
		TheSettingsFacility 								   [singleton class]
	
			This singleton class anchors the entire settings facility.  It
			should be initialized (after config files are loaded) by calling
			the class constructor TheSettingsFacility().  This initializes 
			a settings module hierarchy that is initially empty, except for 
			a root module _TheRootSettingsModule which is given appropriate
			name/description/docstring parameters.  After TheSettingsFacility
			has been initialized, other subsystems of GLaDOS may create their
			own settings modules, and plug them into the hierarchy.
			
		Setting 														 [class]
		
			GLaDOS subsystems should create subclasses/instances of this 
			class at initialization time to define their individual settings.  
			Subsystems should specify a hard-coded default value for each 
			setting, but (for configurable settings) should also reference 
			config values as needed to override the hard-coded defaults.
		
		SettingsModule													 [class]
		
			GLaDOS subsystems should organize their settings into "settings
			modules" which get installed into the hierarchical settings 
			module tree that is rooted at the root settings module.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------

	# An earlier file header comment block follows:
#|==============================================================================
#|	settings.py
#|
#|		This module defines a facility that provides organized access to 
#|		various system and application settings.  This faculity is utilized 
#|		by the 'Settings' GLaDOS app (defined in the 'apps' package).
#|
#|		The module is anchored in the singleton class TheSettingsFacility.
#|		The main class of the module is called SettingsModule, and it 
#|		provides essentially a 'directory' of related settings.  Instances 
#|		of SettingsModule can be nested inside of each other.  Each instance 
#|		has a short name \(identifier used in commands), a longer decription 
#|		used at the top of the headings window, and an even longer docstring.
#|
#|		The bottommost element in the settings hierarchy is called a Setting.  
#|		Each setting has a short name (identifier), a longer description, and 
#|		an even longer docstring.  It also has a SettingType_, and an iterable 
#|		ValueList (except for settings with very large or continuous ranges).
#|
#|		Settings types include the following (these are classes that should
#|		be instantiated as needed to set various type-specific parameters):
#|
#|			ToggleType		- Boolean value; toggle switch or checkbox.
#|			EnumeratedType	- Short enumerated list of possible values.
#|			RangeType		- Short range of integers.
#|			IntegerType		- Wide range of integers.
#|			ContinuousType	- Continuous ranges of numbers.
#|
#|		In the future, types may be associated with 'widgets' within the 
#|		settings app which are used to display/adjust their options.  (Or, is 
#|		this going overboard, perhaps?  Instructions to the AI may suffice.)
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#/-------------- IDIOM TO ACCESS THE CURRENT PACKAGE'S LOGGER -----------------\
from os	import path		# We use this to parse out the current package name.
from infrastructure.logmaster import getComponentLogger	# Used below.
  # Now go ahead and create (or access) the component logger for this package:
global _component, _logger	# Software component name, logger for component.
_component = path.basename(path.dirname(__file__))	# Infers our package name.
_logger = getComponentLogger(_component)  # Create/access the component logger.
#\----------------------- END PACKAGE LOGGER IDIOM ----------------------------/

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
	# Type hints that we use for settings-update methods & settings lists.

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from 	infrastructure.decorators 	import singleton


	#|==========================================================================
	#|
	#| 	2. Forward class declarations. 							  [code section]
	#|
	#|		Here we declare classes to be defined later in this module.
	#|		(Basically, this is only useful to facilitate type hints.)
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# Top-level classes of this module.
class	_SettingsFacility_:		pass	# Abstract base class for settings facility.
class	TheSettingsFacility:	pass	# Singleton class to anchor this module.

	# Classes for the settings hierarchy.
class	Setting:				pass	# An individual setting.
class	SettingsModule:			pass	# A directory of settings.
class	_TheRootSettingsModule:	pass	# Singleton: Root of the settings module hierarchy.

	# Setting type classes.
class	SettingType_:			pass	# Abstract base class for setting types.
class	ToggleType:				pass	# Setting types for two-valued settings.
class	EnumeratedType:			pass	# Setting types for short enumerated lists.
class	RangeType:				pass	# Setting types for short integer ranges.
class	IntegerType:			pass	# Setting types for wide integer ranges.
class	ContinuousType:			pass	# Setting types for continuous number ranges.
class	StringType:				pass	# Setting types for strings.

	# Value list classes.
class	ValueList:				pass	# List of possible values, available for some types.


	#|==========================================================================
	#|
	#| 	3. Class definitons. 							  		  [code section]
	#|
	#|		Here we define the classes that this module is providing.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class	Setting:
	"""
	"""

	def __init__(newSetting:Setting,
			name:str=None,					# This is a short identifier string that can be used to name this setting e.g. in a /set command line.
			settingType:SettingType_=None,	
			defaultValue:object=None,		# This is the default value that should be used for this setting.
			description:str=None,
			docstring:str=None,
			inModule:SettingsModule=None,
			updateMethod:Callable=None,		# This method is called to cause the new setting value to actually take effect in the system.
		):
		"""
		"""
		newSetting._name 			= name
		newSetting._type 			= settingType
		newSetting._defaultValue	= defaultValue
		newSetting._description		= description
		newSetting._docstring		= docstring
		newSetting._inModule		= inModule
		newSetting._updateMethod	= updateMethod
		
			# Initialize current value of setting.
		newSetting._curValue		= defaultValue

	def setValue(thisSetting:Setting, newValue:object):
		"""Sets the value of the setting to the given value, then calls the 
			setting's 'update' method to cause the new value to take effect."""
		
			# First, we make sure that the value is really changing.
		if newValue != thisSetting._curValue:
				# It really is a new value!  Store it and update the system.
			thisSetting._curValue = newValue	# Remember the setting's new value.
			thisSetting._updateMethod()			# Call this setting's update method.

	def resetToDefault(thisSetting:Setting):
		"""This causes the setting to reinitialize itself to its default
			value, as specified in the relevant (system or AI) config file."""
		thisSetting.setValue(thisSetting._defaultValue)
		
#__/ End class Setting.


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

	def resetToDefaults(thisSettingsModule:SettingsModule, recursive:bool=False):
	
		"""This tells this settings module that all of our settings should be 
			reset to their default values.  If recursive=True is specified, 
			then all descendant modules in the hierarchy are also reset."""
		
			# First reset the top-level settings of this module.
		settings = thisSettingsModule._settings
		if settings != None:
			for setting in settings:
				setting.resetToDefault()
				
			# If we're in recursive mode, then recursively reset all submodules.
		if recursive is True:
			submodules = thisSettingsModule._subModules
			for module in submodules:
				module.resetToDefaults(recursive)

	def reconfigure(thisSettingsModule:SettingsModule):
		"""This tells the settings module to reconfigure itself, which means,
			apply new configuration parameters obtained from the (system and/or 
			AI) configuration file(s).  This could, for example, have the effect
			of changing the default values of the settings in this module.  This
			could be useful if the config file was changed since the system was
			booted up, and we have reloaded the config file and want to apply the
			changes and then reset the settings to the new defaults."""
		pass

@singleton
class	_TheRootSettingsModule(SettingsModule):

	def __init__(theRootSettingsModule:_TheRootSettingsModule,
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
		super(_TheRootSettingsModule.__wrapped__, theRootSettingsModule).__init__(
				name=name, description=description, docstring=docstring,
				inModule=None, settings=None, subModules=None
			)
				# Note that in the above, we make sure that there is no
				# parent settings module, and no settings or submodules
				# initially.


@singleton
class	TheSettingsFacility(_SettingsFacility_):

	"""This singleton class anchors the settings module."""

	def __init__(theSettingsFacility:TheSettingsFacility, *args, **kwargs):

		_logger.debug("Settings facility: Initializing settings facility.")

			# Call the constructor for the private singleton class 
			# _TheRootSettingsModule, which initializes the root 
			# setings module.  Link it from an instance attribute.
		theSettingsFacility.rootSettingsModule = _TheRootSettingsModule()
	
	def addToplevelModule(theSettingsFacility:TheSettingsFacility,
			settingsModule=SettingsModule	# The settings module to add at top level.
		):
		
			# Install the provided module directly under the root module.
		theSettingsFacility._rootSettingsModule.installSubmodule(settingsModule)

	def resetAllToDefaults(theSettingsFacility:TheSettingsFacility):
		"""Resets all settings in the system back to their default values."""
		rootModule = theSettingsFacility._rootSettingsModule
		rootModule.resetToDefaults(recurive=True)
		
