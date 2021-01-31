# authSystem.py - Authorization system for managing fine-grained permissions.

# Important classes include:
#
#	Permissions - A permissions object keeps track of the authorities
#		upon which we currently have conferred the permission to access 
#		specific capabilities, relative to some specific context (namely,
#		whichever object owns this permissions object). You can think of
#		a permissions object as being like a dict that maps a capability
#		name to a list of authorities that have that permission.
#

from enum	import	Enum			# Support for enumerated types.

from collections.abc	import	Iterable

from infrastructure.decorators	import	singleton

from entities.entity	import	Entity_

from	.capability		import	Capability
from	.authority		import	(
		theOmniscientAuthority,
		theOmnipotentAuthority
	)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Permissions: pass
class Permissions:
	
	"""A permissions object keeps track of the authorities upon which we have	
		conferred all of the various capability access permissions that are 
		associated with a given resource (e.g., file, setting, command, app).
		(Most generally, a 'resource' could be any object supporting the .name
		attribute, which is used for diagnostic purposes.)  If the 'capmap'
		argument is provided, it should be a dictionary mapping capabilities 
		to the set of authorities upon which permission to access the given
		capability is conferred."""
		
	def __init__(newPerms:Permissions, resource:object=None, capmap:dict=None):
		
		perms = newPerms
		
			# Store the provided resource and capability map.
		perms._resource = resource
		perms._capMap = capmap
	
	def capAuths(thisPerms:Permissions, cap:Capability):
	
		"""Returns the set of authorities that currently have permission
			to access the specified capability for the underlying resource
			conferred upon them.  Automatically ensures that the appropriate
			high-powered authorities are included in the returned set."""
			
		perms = thisPerms		# This permissions object.
		capmap = perms._capMap	# Our capability map.

		# Get the capability's authority set.
		if cap in capmap:
			authSet = capmap[cap]
		else:
			authSet = set()		# Empty set.

		# The omniscient authority gets all passive capabilities.
		if cap.isPassive:
			authSet.add(theOmniscientAuthority)
			
		# The omnipotent authority gets all active capabilities.
		if cap.isActive:
			authSet.add(theOmnipotentAuthority)
	
	def conferOn(thisPerms:Permissions, caps:Iterable, auths:Iterable):
	
		"""Modify this permissions object by conferring permission to access
			each of the given capabilities upon each of the given authorities."""

		perms = thisPerms		# This permissions object.
		capmap = perms._capMap	# Our capability map.

		for cap in caps:
			
			# Get the current authority set.
			if cap in capmap:
				authSet = capmap[cap]
			else:
				authSet = set()		# Empty set.
				
			# This adds all of the given authorities into the authority set.
			authSet.update(auths)
			
			# Update the capability map with the new authority set.
			capmap[cap] = authSet
			
		# Remember our new capability map.
		perms._capMap = capmap
	
	# The permissions.mayAccess(entity,capability) method is the heart of the
	# permissions system. It is what is ultimately responsible for figuring out
	# whether a given entity currently has permission (through the authorities 
	# that it holds, at the moment) to access a given capability for a resource.
	
	def mayAccess(thisPerms:Permissions, entity:Entity_, cap:Capability):
		
		"""Returns True if the given entity currently has permission to
			access the given capability of the underlying resource, otherwise
			False."""
		
		perms = thisPerms
		
			# Get the authority sets for the entity, and the capability.
			
		entityAuths = entity.authorities	# Entities should define this property.
		cap_auths = perms.capAuths(cap)		# This includes implicit authorities.
		
		# Now our task is simple. We go through all of the entity's authorities,
		# and if any of them includes any of the capability's authorities, then 
		# that means yes, this entity *does* currently have permission to access
		# the given capability of the underlying resource.
		for entityAuth in entityAuths:
			for capAuth in cap_auths:
				if entityAuth.includes(capAuth):
					return True
					
		return False
		