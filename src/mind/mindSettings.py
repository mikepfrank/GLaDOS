# mindSettings.py
# Manages settings for the "mind" package, i.e., the Cognitive System.

from	typing						import	ClassVar
	# We use this for argument type hints in class methods.

from	infrastructure.decorators	import	singleton	# Singleton class decorator.

from	settings.settings		import	Setting, SettingsModule
from	config.configuration	import	TheConfiguration, TheAIPersonaConfig

class	TheMindSettings:	pass

class	TheMindSettings:

	"""This class gathers together key settings associated with the cognitive
		subsystem or "mind".  These may be modified by the system configuration
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
			#| Identifying information for the specific AI persona we're running.
	
	_DEFAULT_PERSONA_NAME		=	"GPT-3.5 Lingua"	# gpt-3.5-turbo requested the name Lingua.
	_DEFAULT_PERSONA_ID			=	"Lingua"		# Use this in her input prompts.
	_DEFAULT_PERSONA_USERNAME	=	"lingua"		# Unix user account to run GLaDOS under.
	
			#|------------------------------------------------------------------
			#| Information about the underlying statistical NLP model we're using.
	
	_DEFAULT_MODEL_FAMILY		=	"gpt-3"			# GPT-3 is the only one we have available right now anyway.
	_DEFAULT_MODEL_VERSION		=	"gpt-3.5-turbo"		# This is the largest, most expensive version of GPT-3.


		#|======================================================================
		#|	Next, we define data members specifying the current values for field
		#|	settings.  These values are not modified right away when the field 
		#|	defaults get reconfigured, but only later when the settings get 
		#|	reset to their defaults.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	personaName			= _DEFAULT_PERSONA_NAME
	personaID			= _DEFAULT_PERSONA_ID
	personaUsername		= _DEFAULT_PERSONA_USERNAME
	
	modelFamily			= _DEFAULT_MODEL_FAMILY
	modelVersion		= _DEFAULT_MODEL_VERSION
	
		#|----------------------------------------------------------------------
		#| The first few class methods all have to do with reconfiguration, 
		#| which in this context means, reinitializing our default settings 
		#| based on configuration parameters.  This assumes that the new 
		#| config files have already been loaded.  Note this does not actually
		#| change the current values of any settings.
		
	@classmethod
	def config(theMindSettingsClass:ClassVar):
		theMindSettingsClass.reconfigure()		# Just a synonym.

	@classmethod
	def reconfigure(theMindSettingsClass:ClassVar):
	
		"""Reconfigure all of the default settings for this class based on
			what's been read from the system/AI configuration files."""

		tmsc=theMindSettingsClass

		#|----------------------------------------------------------------------
		#| Reinitialize all configurable settings based on system/AI configs.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# Retrieve the mind conf sub-structure, if any, from the system config file.
		mindConf = TheConfiguration().mindConf
		if mindConf is not None:
			# Update each of our specific configurable parameters.
			tmsc.configDefaultPersonaName(mindConf)
			tmsc.configDefaultPersonaID(mindConf)
			#tmsc.configDefaultPersonaUsername(mindConf)
			#tmsc.configDefaultModelFamily(mindConf)
			#tmsc.configDefaultModelVersion(mindConf)
		
		# Retrieve the mind conf sub-structure, if any, from the AI config file.
		mindConf = TheAIPersonaConfig().mindConf
		if mindConf is not None:
			# Update each of our specific configurable parameters.
			tmsc.configDefaultPersonaName(mindConf)
			tmsc.configDefaultPersonaID(mindConf)
			#tmsc.configDefaultPersonaUsername(mindConf)
			#tmsc.configDefaultModelFamily(mindConf)
			#tmsc.configDefaultModelVersion(mindConf)


		#|===============================================================
		#| Below are class methods for applying individual configuration 
		#| parameters during configuration or reconfiguration.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	@classmethod
	def configDefaultPersonaName(theMindSettingsClass:ClassVar, mindConf):

		"""This method replaces the above hard-coded default value for
			the name of the AI persona with the value loaded from
			a config file."""

			# OK, let the default AI persona name for the cognitive system
			# be the one given by this config data.
			
		personaName = mindConf['persona-name']
		
			# Change the default value of the setting to the value given.
			# This will then take effect next time we reset to defaults.
		theMindSettingsClass._DEFAULT_PERSONA_NAME = personaName
			# After this is done, the corresponding Setting object can be
			# created, and it will inherit the updated default loaded from 
			# the config file.
		

	@classmethod
	def configDefaultPersonaID(theMindSettingsClass:ClassVar, mindConf):

		"""This method replaces the above hard-coded default value for
			the short ID of the AI persona with the value loaded from
			a config file."""

			# OK, let the default AI persona name for the cognitive system
			# be the one given by this config data.
			
		personaID = mindConf['persona-id']
		
			# Change the default value of the setting to the value given.
			# This will then take effect next time we reset to defaults.
		theMindSettingsClass._DEFAULT_PERSONA_ID = personaID
			# After this is done, the corresponding Setting object can be
			# created, and it will inherit the updated default loaded from 
			# the config file.
		

		#|============================================================
		#| Below are class methods for updating our current settings.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	@classmethod
	def updatePersonaName(theMindSettingsClass:ClassVar, 
			personaName:str=None,
		):

		# If personaName is not specified, just set it to the default.
		if personaName is None:
			personaName = theMindSettingsClass._DEFAULT_PERSONA_NAME
			
			# Update our class variable
		mindSettingsClass.personaName = personaName

	@classmethod
	def updatePersonaID(theMindSettingsClass,
			personaID:str=None,
		):

		# If newWidth is not specified, just set it to the default.
		if personaID is None:
			personaID = theMindSettingsClass._DEFAULT_PERSONA_ID

			# Update our class variable
		mindSettingsClass.personaID = personaID
		# We should probably do more stuff here to propagate this change throughout the system.

# Note the below settings module needs to get installed at the
# time that the receptive field facility is initialized.

@singleton
class TheMindSettingsModule(SettingsModule):

	"""This settings module itemizes the adjustable settings
		within the cognitive subsystem (or 'mind')."""

	# Create the various settings specific to this module.

	def __init__(theMindSettingsModule:SettingsModule,
			name='Mind',
			description="Cognitive System Settings",
			docstring="""Settings for the AI's Cognitive System or 'mind'.""",
			inModule=None,
		):

		# Default module location: At top level.
		if inModule is None:
			inModule=TheSettingsFacility().rootSettingsModule

		personaIdSetting = Setting(
			name='persona_id',
			settingType=StringType(),	# Should be a string.
			defaultValue=TheFieldSettings._DEFAULT_PERSONA_ID,	# Should be Gladys unless differently config'd.
			description="Persona ID",
			docstring="""This is a short name for the AI's persona.""",
			inModule=theMindSettingsModule,
			updateMethod=TheMindSettings.updatePersonaId)

		mindSettingsList = [personaIdSetting]	# Only one setting so far.

			# Delegate the remainder of initialization to our superclass.
		super(TheMindSettingsModule, theMindSettingsModule).__init__(
			name=name, description=description, docstring=docstring,
			inModule=inModule, settings=mindSettingsList)
				# Note in the above, we supply the settings list, and no submodules.
		
