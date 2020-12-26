#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 field/fieldSettings.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		field/fieldSettings.py		 	 [Python module source file]
		
	MODULE NAME:	field.fieldSettings
	IN PACKAGE:		field
	FULL PATH:		$GIT_ROOT/GLaDOS/src/field/fieldSettings.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.server.settings (Settings management facility)


	MODULE DESCRIPTION:
	===================
	
		This module defines settings that are specific to the receptive 
		field facility.
		
		Unlike most subsystems of GLaDOS, the field settings may be 
		configured in either the top-level system configuration file,
		or the AI-specific config file, which overrides it.  Please note
		that in either case, the configuration parameters only apply when
		the system first starts up, or when it is reconfigured.  See the
		config package for instructions on how to reconfigure the system.
		
		This module works by first gathering all settable data members 
		that are specific to the receptive field facility into a single 
		non-instantiated class called TheFieldSettings.  Then we define
		the singleton class TheFieldSettingsModule which creates and 
		gathers together all of the corresponding Setting objects.
		
		At initialization time, all that the receptive field facility 
		needs to do to activate this module is to create the singleton
		instance of TheFieldSettingsModule (by calling the constructor) 
		and then install it in the settings facility by just adding it 
		at top level within TheSettingsFacility (by passing it to the
		.addToplevelModule() method).
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------

from	typing						import	ClassVar
	# We use this for argument type hints in class methods.

from	infrastructure.decorators	import	singleton

from	settings.settings		import	Setting, SettingsModule
from	config.configuration	import	TheConfiguration, TheAIPersonaConfig

class 	TheFieldSettings: 	pass

# Note the following class initializes its class variables to standard
# defaults at module load (import) time.  We don't use a singleton class
# here because we don't need to do any other (i.e., construct-time)
# initialization.

class TheFieldSettings():

	"""This class gathers together key settings associated with the receptive
		field subsystem.  These may be modified by the system configuration
		or the AI configuration.  In case of conflicting configuration data,
		settings in the AI configuration take priority."""

	#|==========================================================================
	#|	Class data members.						  	  [class definition section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		#|======================================================================
		#|	First, we define data members specifying default values for field
		#|	settings.  These values are utilized when the system first boots up, 
		#|	except note that the hard-coded values given below may be overridden
		#|	by config settings.  Also, the current defaults are used whenever 
		#|	the settings are reset to their default values.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
			#|------------------------------------------------------------------
			#| Default maximum field size, in tokens. This is actually 
			#| determined by the choice of underlying AI (NLP model). 
	
	_DEFAULT_MAX_SIZE		= 2048		# This is the actual maximum for GPT-3.
		
			#------------------------------------------------------------------
			# Default nominal displayed width of field elements, in characters.

	_DEFAULT_NOMINAL_WIDTH	= 60
		# (Keeping it narrow-ish reduces tokens wasted on decorators.)

		#|======================================================================
		#|	Next, we define data members specifying the current values for field
		#|	settings.  These values are not modified right away when the field 
		#|	defaults get reconfigured, but only later when the settings get 
		#|	reset to their defaults.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
			#|---------------------------------------
			#| Current maximum field size, in tokens.
			
	maxSize = _DEFAULT_MAX_SIZE
		# At import time, just initialize this to the hard-coded default above.
	
			#-------------------------------------------------------------------
			# Current nominal displayed width of field elements, in characters.
			# Note if this value is changed, it is not guaranteed to immediately
			# affect all elements that may have already been created before this 
			# value was changed. (If they want to be affected by changes to this 
			# value dynamically, then their implementation needs to be written 
			# in such a way as to explicitly support this capability.)

			# Note that this value may not be respected in all field elements or views.
			# NOTE: We still need to implement a config setting to override this.

	nominalWidth = _DEFAULT_NOMINAL_WIDTH		
		# At import time, just initialize this to the hard-coded default above.

	#|==========================================================================
	#|	Class methods.								  [class definition section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		#|----------------------------------------------------------------------
		#| The first few class methods all have to do with reconfiguration, 
		#| which in this context means, reinitializing our default settings 
		#| based on configuration parameters.  This assumes that the new 
		#| config files have already been loaded.  Note this does not actually
		#| change the current values of any settings.
		
	@classmethod
	def config(theFieldSettingsClass:ClassVar):
		theFieldSettingsClass.reconfigure()		# Just a synonym.

	@classmethod
	def reconfigure(theFieldSettingsClass:ClassVar):
	
		"""Reconfigure all of the default settings for this class."""

		#|----------------------------------------------------------------------
		#| Reinitialize all configurable settings based on system configuration.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
			# Retrieve the field conf structure from the system configuration.
		fieldConf = TheConfiguration().fieldConf

		if fieldConf is not None:
			# Update each of our specific configurable parameters.
			theFieldSettingsClass.configDefaultNominalWidth(fieldConf)
		
		#----------------------------------------------------------------------
		# NOTE: At this point we should do the same for the AI configuration.
		
		theFieldSettingsClass.configDefaultMaxSize()
		
	#__/ End class method TheFieldSettings.reconfigure().


		#|---------------------------------------------------------------
		#| Below are class methods for applying individual configuration 
		#| parameters during configuration or reconfiguration.
		
	@classmethod
	def configDefaultMaxSize(theFieldSettingsClass:ClassVar):

		"""This method replaces the above hard-coded default value for
			the maximum field size setting with the value loaded from
			the specific AI persona's config file."""

		aiConf = TheAIPersonaConfig()	# The AI persona's config data.
		
			# OK, let the default maximum size setting for this receptive 
			# field facility be the same as the size of the real AI's 
			# actual receptive field (or at least, our config data for that).
		maxSize = aiConf.maxVisibleTokens
		
			# Change the default value of the setting to the value given.
			# This will then take effect next time we reset to defaults.
		theFieldSettingsClass._DEFAULT_MAX_SIZE = maxSize
		
	
	@classmethod
	def configDefaultNominalWidth(theFieldSettingsClass:ClassVar, 
			fieldConf:dict	# This dict contains the field configuration.
		):
	
		"""This method replaces the above hard-coded default value 
			for the field nominal width setting with a value loaded 
			from the (system or AI) config file."""
		
		theFieldSettingsClass._DEFAULT_NOMINAL_WIDTH = fieldConf['nominal-width']
			# After this is done, the corresponding Setting object can be
			# created, and it will inherit the updated default loaded from 
			# the config file.

		#|---------------------------------------------------
		#| Below are class methods for updating our current settings.

	@classmethod
	def updateMaximumSize(theFieldSettingsClass:ClassVar, 
			maxSize:int=None,
		):

		# If maxSize is not specified, just set it to the default.
		if maxSize is None:
			maxSize = theFieldSettingsClass._DEFAULT_MAX_SIZE
			
			# Update our class variable
		fieldSettingsClass.maxSize = maxSize

	@classmethod
	def updateNominalWidth(theFieldSettingsClass,
			newWidth:int=None,
		):

		# If newWidth is not specified, just set it to the default.
		if newWidth is None:
			newWidth = theFieldSettingsClass._DEFAULT_NOMINAL_WIDTH

			# Update our class variable
		fieldSettingsClass.nominalWidth = newWidth
		# We should probably do more stuff here to propagate this change throughout the system.


# Note the below settings module needs to get installed at the
# time that the receptive field facility is initialized.

@singleton
class TheFieldSettingsModule(SettingsModule):

	"""This settings module itemizes the adjustable settings
		within the receptive field subsystem."""

	# Create the various settings specific to this module.

	def __init__(theFieldSettingsModule:SettingsModule,
			name='Field',
			description="Receptive Field Settings",
			docstring="""Settings for the display of input to the AI's receptive field.""",
			inModule=None,
		):

		# Default module location: At top level.
		if inModule is None:
			inModule=TheSettingsFacility().rootSettingsModule

		nominalWidthSetting = Setting(
			name='nom_width',
			settingType=IntegerType(10, None),	# Range 10 and up.
			defaultValue=TheFieldSettings._DEFAULT_NOMINAL_WIDTH,	# Should be 60 unless differently config'd.
			description="Nominal field width",
			docstring="""Specifies the nominal width of field elements
				in fixed-width character cells.""",
			inModule=theFieldSettingsModule,
			updateMethod=TheFieldSettings.updateNominalWidth)

		fieldSettingsList = [nominalWidthSetting]	# Only one setting so far.

			# Delegate the remainder of initialization to our superclass.
		super(TheFieldSettingsModule, theFieldSettingsModule).__init__(
			name=name, description=description, docstring=docstring,
			inModule=inModule, settings=fieldSettingsList)
				# Note in the above, we supply the settings list, and no submodules.
