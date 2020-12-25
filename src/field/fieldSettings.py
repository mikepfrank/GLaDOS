
from	infrastructure.decorators	import	singleton

from	settings.settings	import	Setting, SettingsModule, TheRootSettingsModule


class TheFieldSettings: pass


class FieldSettings_:
	pass

# Note the following class initializes its static variables to standard
# defaults at module load (import) time.  We don't use a singleton class
# here because we don't need to do any other (i.e., construct-time)
# initialization.

class TheFieldSettings(FieldSettings_):

	"""This class gathers together key settings associated with the receptive
		field subsystem.  These may be modified by the system configuration
		or the AI configuration.  In case of conflicting configuration data,
		settings in the AI configuration take priority."""

		#------------------------------------------------------------------
		# Default nominal displayed width of field elements, in characters.

	_DEFAULT_NOMINAL_WIDTH	= 60
		# (Keeping it narrow-ish reduces tokens wasted on decorators.)

		# Note that this default may not be respected in all field elements or views.
		# (Does it make more sense conceptually to set this in the window system?)
		# NOTE: We still need to add a config setting to override this.

	_nominalWidth = _DEFAULT_NOMINAL_WIDTH


	#|---------------------------------------------------
	#| Below are class methods for updating our settings.

	@classmethod
	def updateNominalWidth(fieldSettingsClass,
			newWidth:int=fieldSettingsClass._DEFAULT_NOMINAL_WIDTH
		):
			# Update our class variable
		fieldSettingsClass._nominalWidth = newWidth


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
			inModule=TheRootSettingsModule()
		):

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
