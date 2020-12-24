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

	# Forward declarations.

	# Top-level classes of this module.
class	SettingsFacility_:		pass	# Abstract base class for settings facility.
class	TheSettingsFacility:	pass	# Singleton class to anchor this module.

	# Classes for the settings hierarchy.
class	TheRootSettingsModule:	pass	# Singleton: Root of the settings module hierarchy.
class	SettingsModule:			pass	# A directory of settings.
class	Setting:				pass	# An individual setting.

	# Setting type classes.
class	Type_:					pass	# Abstract base class for setting types.
class	Toggle:					pass	# Setting types for two-valued settings.
class	Enumerated:				pass	# Setting types for short enumerated lists.
class	Range:					pass	# Setting types for short integer ranges.
class	Integer:				pass	# Setting types for wide integer ranges.
class	Continuous:				pass	# Setting types for continues number ranges.

	# Value list classes.
class	ValueList:				pass	# List of possible values, available for some types.

@singleton
class	TheSettingsFacility(SettingsFacility_):
	"""This singleton class anchors the settings module."""
	pass
