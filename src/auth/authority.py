# authority.py

# Authority classes. Part of the authorization system for managing permissions.

#	Authority - An authority is an object that abstractly represents a given
#		set of capability access permissions; namely, whichever ones that have
#		been conferred upon this authority.  Entities may be granted authorities.
#		Authorities have inclusion relations.  Important singleton authorities 
#		include:
#
#			Null_Authority - This is a special authority that SHOULD NOT
#				BE GIVEN ANY PERMISSIONS WHATSOEVER.  Every authority 
#				automatically includes this authority.  This authority 
#				includes no other authorities.
#
#			Base_Authority - This is a special authority that is granted
#				to every entity that exists (or could possibly exist).
#				It only includes Null_Authority, and every other authority
#				(other than Null_Authority) implicitly includes this 
#				authority.
#
#			Generic_User_Authority - All entities that can be considered
#				GLaDOS users (whether human or AI) have this authority,
#				which gives them permission to access commands that are
#				intended to be accessible to all users.
#
#			AI_User_Authority - All AI personas have this authority, which
#				gives them permission to execute commands, modify settings
#				and files, and launch apps as per our intent for AI users.
#		
#			Human_User_Authority - All human users who are logged into the
#				system (whether locally or remotely) have this authority,
#				which grants them capabilities intended for human users.
#
#			Operator_Authority - The operator using the main server console
#				is granted this authority, which allows him/her to perform
#				actions intended for the system operator.  Operator authority
#				includes human user authority.
#
#			System_Authority - This is a special authority that is granted to
#				the entities representing automated subsystems of GLaDOS.  (Not
#				sure yet what we'll use it for.)
#
#			Omniscient_Authority - This is a special authority upon which we
#				automatically confer permission to access all 'passive' 
#				capabilities ('read', etc.) that exist in the system.
#
#			Omnipotent_Authority - This is a special authority upon which we
#				automatically confer permission to access all 'active' 
#				capabilities ('modify', etc.) that exist in the system.
#				
#			Godlike_Authority - Includes both the omniscient & omnipotent 
#				authorities.
#
#			Uber_Authority - This is a special authority which implicitly
#				includes *all* of the authorities that have been defined in 
#				the system.  It also implicitly has all possible permissions
#				conferred upon it.
#

from 	enum						import	Enum	# Support for enumerated types.
from	collections.abc				import	Iterable
from	infrastructure.decorators	import	singleton
#from	entities.entity				import	Entity_
from	.capability					import	Capability

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Authority_: pass
class Authority_:	# Abstract base class.

	name = "(abstract authority)"	# Subclasses should override this.

		# List of included authorities.
	_includes = None		# None defined by default.
			# Subclasses should override this.

	def includes(thisAuth:Authority_, otherAuth:Authority_):
	
		"""This method returns True if this authority includes the given
			other authority, otherwise it returns false.  Note inclusion
			is reflexive and transitive."""
		
		auth = thisAuth
		
		# Base case #1: The auths are the same. Return True.
		if otherAuth is thisAuth:
			return True

		# Base case #2: We immediately include the other auth.
		if otherAuth in auth._includes:
			return True
			
		# Recursive case. Return True if any of our immediate includes,
		# includes the other auth.
		for incAuth in auth._includes:
			if incAuth.includes(otherAuth):
				return True
				
		# If we get here, then we couldn't find the other auth in our
		# includes, even recursively, so return False.
		return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Null_Authority:

	"""This is a special authority that SHOULD NOT BE GIVEN ANY PERMISSIONS 	
		WHATSOEVER.  Every authority automatically includes this authority.  
		This authority includes no other authorities."""

	name = "Null Authority"
	_includes = []				# Includes no other authorities.

theNullAuthority = The_Null_Authority()		# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Base_Authority:

	"""This is a special authority that is granted to every entity that exists 
		(or could possibly exist).  It only includes Null_Authority, and every 
		other authority (other than Null_Authority) automatically includes this 
		authority."""

	name = "Base Authority"
	_includes = [theNullAuthority]	# Only includes the null authority.

theBaseAuthority = The_Base_Authority()		# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Generic_User_Authority:

	"""All entities that can be considered GLaDOS users (whether human or AI) 
		have this authority, which gives them permission to e.g. access commands
		that are intended to be accessible to all users."""

	name = "Generic User Authority"
	_includes = [theBaseAuthority]	# Includes the base authority.

theGenericUserAuthority = The_Generic_User_Authority()		# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_AI_User_Authority:

	"""All AI personas have this authority, which gives them permission to 
		execute commands, modify settings and files, and launch apps as per 
		our intent for AI users."""

	name = "AI User Authority"
	_includes = [theGenericUserAuthority]	# Includes generic-user authority.

theAIUserAuthority = The_AI_User_Authority()		# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Human_User_Authority:

	"""All human users who are logged into the system (whether locally or 
		remotely) have this authority, which grants them capabilities intended 
		for human users."""

	name = "Human User Authority"
	_includes = [theGenericUserAuthority]	# Includes generic-user authority.

theHumanUserAuthority = The_Human_User_Authority()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Operator_Authority:

	"""The operator using the main server console is granted this authority, 
		which allows him/her to perform actions intended for the system 
		operator.  Operator authority includes human user authority."""

	name = "Operator Authority"
	_includes = [theHumanUserAuthority]	# Includes human-user authority.

theOperatorAuthority = The_Operator_Authority()		# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_System_Authority:

	"""This is a special authority that is granted to entities 
		representing automated subsystems of GLaDOS.  (Not sure yet what 
		we'll use it for.)"""

	name = "System Authority"
	_includes = [theBaseAuthority]	# Includes the base authority.

theSystemAuthority = The_System_Authority()		# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Omniscient_Authority:

	"""This is a special authority upon which we automatically confer 
		permission to access all 'passive' capabilities (e.g., 'read', 
		etc.) that exist in the system."""

	name = "Omniscient Authority"
	_includes = [theBaseAuthority]	# Includes the base authority.

theOmniscientAuthority = The_Omniscient_Authority()		# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Omnipotent_Authority:

	"""This is a special authority upon which we automatically confer permission 
		to access all 'active' capabilities ('modify', 'invoke', etc.) that 
		exist in the system."""

	name = "Omnipotent Authority"
	_includes = [theBaseAuthority]	# Includes the base authority.

theOmnipotentAuthority = The_Omnipotent_Authority()		# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Godlike_Authority:

	"""Includes both the omniscient & omnipotent authorities."""

	name = "Godlike Authority"
	_includes = [theOmniscientAuthority, theOmnipotentAuthority]
		# The Godlike authority is both omniscient and omnipotent, by definition.

theGodlikeAuthority = The_Godlike_Authority()	# Create the singleton.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Uber_Authority:

	"""This is the highest authority in the system, in that it
		automatically includes all other authorities, and it 
		implicitly has all possible permissions."""

	name = "Uber Authority"
	_includes = [
			theAIUserAuthority, 	# Also includes generic user authority.
			theOperatorAuthority,	# Also includes human user authority.
			theSystemAuthority, 	# Also includes base & null authorities.
			theGodlikeAuthority		# Also includes omniscient & omnipotent auths.
		]
		# The above list should cover everything, but to make sure,
		# any time we create any other new authorities, we should 
		# automatically add them to the Uber authority's include list.

