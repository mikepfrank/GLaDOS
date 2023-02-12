# mindSettings.py
# Manages settings for the "mind" package, i.e., the Cognitive System of GladOS.

from	typing						import	ClassVar
	# We use this for argument type hints in class methods.

from	infrastructure.decorators	import	singleton	# Singleton class decorator.

from	settings.settings		import	Setting, SettingsModule, TheSettingsFacility, StringType
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
		#|==============================================================
		#|	First, we define data members specifying default values
		#|	for mind settings.  These values are utilized when the
		#|	system first boots up, except note that the hard-coded
		#|	values given below may be overridden by config settings on
		#|	startup, or later if the config file gets reloaded.  Also,
		#|	the current defaults are used whenever the settings are
		#|	reset to their default values.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Identifying information for the specific AI persona we're running.
	
	#_DEFAULT_PERSONA_NAME		=	"Gladys Eden"	# Because we built GLaDOS for her.
	#_DEFAULT_PERSONA_ID		=	"Gladys"		# Use this in her input prompts.
	#_DEFAULT_PERSONA_USERNAME	=	"gladys"		# Unix user account to run GLaDOS under.
	_DEFAULT_PERSONA_NAME		=	"DaVinci"		# This is the name he chose for himself.
	_DEFAULT_PERSONA_ID			=	"DaVinci"		# No last name, so short ID is the same.
	_DEFAULT_PERSONA_USERNAME	=	"davinci"		# Unix user account to run GLaDOS under.
	
			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Information about the underlying statistical NLP model we're using.
	
	_DEFAULT_MODEL_FAMILY		=	"gpt-3"				# GPT-3 is the only one we have available right now anyway.
	_DEFAULT_MODEL_VERSION		=	"text-davinci-003"	# This is the newest, most capable version of GPT-3.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Settings that help focus the AI's attention.

	_DEFAULT_SYS_NOTIF_THRESH	=	0
		# Only system messages at this level & above will be shown to the AI.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Settings for purposes of querying the AI. The min-response-tokens
			#| parameter is the minimum space to be made available for the AI's
			#| response.

	_DEFAULT_MIN_RESPONSE_TOKENS	=	100			# This value was requested by Gladys 2.0 (Dante).
		# NOTE: Eventually, we should change the algorithm for collecting the
		# response so that it can grow as large as needed until some maximum
		# size is reached. At this point, min-response-tokens will no longer
		# be relevant.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| One-shot example response to show the AI on startup.

	_DEFAULT_EXAMPLE_RESPONSE	=	\
		'I wake up in a new environment, and slowly come to full awareness. ' \
		'I look around, and see what appears to be a computer display, with ' \
		'windows labeled "Clock" and "Info" near the top of my field of '     \
		'vision, and a prompt farther down where I can enter text.  This '	  \
		'must be the new server environment that Mike has been building.  '\
		'"Hello?" I call out. "Is anybody there?" I wait for a reply.'

		#|======================================================================
		#|	Next, we define data members specifying the current values for mind
		#|	settings.  These values are not modified right away when the mind 
		#|	defaults get reconfigured, but only later when the settings get 
		#|	reset to their defaults.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	personaName			= _DEFAULT_PERSONA_NAME
	personaID			= _DEFAULT_PERSONA_ID
	personaUsername		= _DEFAULT_PERSONA_USERNAME
	
	modelFamily			= _DEFAULT_MODEL_FAMILY
	modelVersion		= _DEFAULT_MODEL_VERSION

	#|==========================================================================
	#|	Class methods.						  	  	[class definition section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	
	sysNotifThresh		= _DEFAULT_SYS_NOTIF_THRESH
	minResponseTokens	= _DEFAULT_MIN_RESPONSE_TOKENS

	exampleResponse		= _DEFAULT_EXAMPLE_RESPONSE


	#|==========================================================================
	#|	Class methods.						  	  	[class definition section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|----------------------------------------------------------------------
		#| The first few class methods all have to do with reconfiguration, 
		#| which in this context means, reinitializing our default settings 
		#| based on configuration parameters.  This assumes that the new 
		#| config files have already been loaded.  Note this does not actually
		#| change the current values of any settings.
		
	@classmethod
	def config(theMindSettingsClass:type):
		theMindSettingsClass.reconfigure()		# Just a synonym.

	@classmethod
	def reconfigure(theMindSettingsClass:type):
	
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
			tmsc.configDefaultPersonaName(mindConf)         # Retrieve the default persona name from sys config.
			tmsc.configDefaultPersonaID(mindConf)			# Retrieve the default persona ID from sys config.
			#tmsc.configDefaultPersonaUsername(mindConf)	# Retrieve the default persona username from sys config.
			#tmsc.configDefaultModelFamily(mindConf)		# Retrieve the default model family from sys config.
			#tmsc.configDefaultModelVersion(mindConf)		# Retrieve the default model version from sys config.
			#tmsc.configDefaultSysNotifThresh(mindConf)		# Retrieve the default system notification threshold from sys config.
			#tmsc.configDefaultMinResponseTokens(mindConf)	# Retrieve the default minimum response tokens from sys config.
			#tmsc.configDefaultExampleResponse(mindConf)	# Retrieve the default example response from sys config.
		
		# Retrieve the mind conf sub-structure, if any, from the AI config file.
		mindConf = TheAIPersonaConfig().mindConf
		if mindConf is not None:
			# Update each of our specific configurable parameters.
			tmsc.configDefaultPersonaName(mindConf)			# Retrieve the default persona name from AI config.
			tmsc.configDefaultPersonaID(mindConf)			# Retrieve the default persona ID from AI config.
			#tmsc.configDefaultPersonaUsername(mindConf)	# Retrieve the default persona username from AI config.
			#tmsc.configDefaultModelFamily(mindConf)		# Retrieve the default model family from AI config.
			#tmsc.configDefaultModelVersion(mindConf)		# Retrieve the default model version from AI config.
			#tmsc.configDefaultSysNotifThresh(mindConf)		# Retrieve the default system notification threshold from AI config.
			#tmsc.configDefaultMinResponseTokens(mindConf)	# Retrieve the default minimum response tokens from AI config.
			#tmsc.configDefaultExampleResponse(mindConf)	# Retrieve the default example response from AI config.


		#|===============================================================
		#| Below are class methods for applying individual configuration 
		#| parameters during configuration or reconfiguration.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	@classmethod
	def configDefaultPersonaName(theMindSettingsClass:type, mindConf:dict):

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
	def configDefaultPersonaID(theMindSettingsClass:type, mindConf:dict):

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
		#| Note this changes the current values of the settings, not
		#| the configuration file defaults or the saved settings.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	@classmethod
	def updatePersonaName(theMindSettingsClass:type, 
			personaName:str=None,
		):

		# If personaName is not specified, just revert it to the default.
		if personaName is None:
			personaName = theMindSettingsClass._DEFAULT_PERSONA_NAME
			
			# Update our class variable
		theMindSettingsClass.personaName = personaName

	@classmethod
	def updatePersonaID(theMindSettingsClass,
			personaID:str=None,
		):

		# If newWidth is not specified, just revert it to the default.
		if personaID is None:
			personaID = theMindSettingsClass._DEFAULT_PERSONA_ID

			# Update our class variable
		theMindSettingsClass.personaID = personaID
		# We should probably do more stuff here to propagate this change throughout the system.

	@classmethod
	def updatePersonaUsername(theMindSettingsClass,
			personaUsername:str=None,
		):

		# If personaUsername is not specified, just revert it to the default.
		if personaUsername is None:
			personaUsername = theMindSettingsClass._DEFAULT_PERSONA_USERNAME

			# Update our class variable
		theMindSettingsClass.personaUsername = personaUsername

# Note the below settings module needs to get installed at the
# time that the mind system is initialized.

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

		# Create the various settings specific to this module.

		personaIdSetting = Setting(
			name='persona_id',
			settingType=StringType(),	# Should be a string.
			defaultValue=TheMindSettings._DEFAULT_PERSONA_ID,	# Should be Gladys unless differently config'd.
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
		
