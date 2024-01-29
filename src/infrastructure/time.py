# time.py
# Functions/data for working with times.

__all__ = {
	# Classes
		'DateTime',		# Just a new name for the datetime.datetime class.

	# Globals
		'envTZ'			# Pre-fetched value of the time-zone ('TZ') environment
						#	variable setting.

	# Functions
	
		'timeZone',		# Returns a TimeZone object expressing the user's
						#	time-zone preference (from TZ).

		'tzAbbr',		# Returns an abbreviation for the given time zone offset,
						#	which defaults to the user's time zone preference.

		'tznow',		# Returns a current datetime object localized to the
						#	user's timezone preference (from TZ).

		'get_current_date'	# Gets the current date in YYYY-MM-DD (relative to system timezone).
	}

from os import path, getenv

from datetime import	(
	# We're renaming these classes on import to conform to our
	# convention of capitalizing class names.
		
		timedelta	as	TimeDelta,
		timezone	as	TimeZone,
		datetime	as	DateTime,
		date		as	Date
		
	)

from dateutil.tz import (
		gettz	# Function to get time zone from name.
	)

#-------------------------------------------------------------------------------
from .logmaster import getComponentLogger, sysName

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component

#-------------------------------------------------------------------------------

from config.configuration		import	TheConfiguration

global envTZ	# Time-zone ('TZ') environment variable setting.
envTZ = getenv('TZ')

global _gotTZ, _tz
_gotTZ = False
_tzOff = None
_tz = None


_TZ_ABBRS = {	# Map of time zone abbreviations.

	# Note the contents of this map only represent
	# a reasonable guess as to the name of the user's
	# time zone, since time zone names are not unique.
	
	# Note: We have not yet bothered to include
	# in this list any time zones that are not
	# at integer hour offsets from UTC.
	
		-12:	'AoE',	# Anywhere on Earth
		-11:	'NUT',	# Niue Time
		-10:	'HST',	# Hawaii Standard Time
		-9:		'AKST',	# Alaska Standard Time
		-8:		'PST',	# Pacific Standard Time
		-7:		'MST',	# Mountain Standard Time
		-6:		'CST',	# Central Standard Time
		-5:		'EST',	# Eastern Standard Time
		-4:		'VET',	# Venezuelan Standard Time
		-3:		'ART',	# Argentina Time
		-2:		'GST',	# South Georgia Time
		-1:		'CVT',	# Cape Verde Time
		0:		'GMT',	# Greenwich Mean Time
		1:		'CET',	# Central European Time
		2:		'EET',	# Eastern European Time
		3:		'MSK',	# Moscow Standard Time
		4:		'GST',	# Gulf Standard Time
		5:		'UZT',	# Uzbekistan Time
		6:		'BST',	# Bangladesh Standard Time
		7:		'WIB',	# Western Indonesian Time
		8:		'HKT',	# Hong Kong Time (avoid CST since that's U.S. Central)
		9:		'JST',	# Japan Standard Time
		10:		'AEST',	# Australia Eastern Standard Time
		11:		'AEDT', # Australia Eastern Daylight Time
		12:		'NZST',	# New Zealand Standard Time
		13:		'NZDT',	# New Zealand Daylight Time
		14:		'LINT', # Line Islands Time

	}


def tzAbbr(tzOff:int=None):

	"""Return an abbreviation for the user's time-zone preference,
		or some other indicated time zone."""

	if tzOff is None:
		tzOff = tzOffset()		# Get user's time-zone preference.

	return _TZ_ABBRS[tzOff]


def tzOffset():

	"""Returns user's time-zone preference as an integer number of hours from UTC.
		Gets it out of the config file.  Note this method just guesses the time zone
		abbreviation. Really, it's better to set your TZ environment variable."""

	global _tzOff

	if _tzOff is not None:
		return _tzOff

	# Get the time zome preference from the system config.
	config = TheConfiguration()		# System configuration.
	tzOff = config.timezone		# User's time zone preference (hours vs. UTC).

	_tzOff = tzOff

	tzAbb = tzAbbr(tzOff)			# Abbreviation for time zone name.

	if tzOff < 0:
		tzStr = "UTC"+str(tzOff)
	elif tzOff >= 0:
		tzStr = "UTC+"+str(tzOff)
	
	_logger.debug(f"time.tzOffset(): System configured for time zone {tzStr} ({tzAbb})") 

	return tzOff
	

def timeZone():

	"""Returns a TimeZone object expressing the user's time-zone preference."""

	global _gotTZ, _tz

	# If we already got it, just return it.
	if _gotTZ:
		return _tz

	# If the TZ environment variable is set, just use that.
	if envTZ:
		_logger.debug(f"time.timeZone(): Using environment variable TZ={envTZ}.")
		tz = gettz(envTZ)

	else:
		# Get the time zome preference from the system config.
		tzOff = tzOffset()				# Retrieve user's time zone preference as hours vs. UTC.
		td = TimeDelta(hours=tzOff)		# Convert to a timedelta object.
		tz = TimeZone(td)				# Create the timezone object.

	_gotTZ = True
	_tz = tz

	return tz


def tznow():

	"""Returns a current datetime object localized to the user's timezone."""

	tz = timeZone()				# Get the user's time-zone preference.
	dtz = DateTime.now(tz)		# Return current DateTime with timezone specified.
		
	return dtz


def get_current_date():
	"""Returns the current date in ISO 8601 format (YYYY-MM-DD)."""
	return Date.today().isoformat()
