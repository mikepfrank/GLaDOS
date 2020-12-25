
class FieldSettings_:
	pass

@singleton
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
