# capability.py

# Important classes include:
#
#	Capability - An enumerated type of predefined capability names.
#		Examples of capabilities include:
#
#			'launch' - Capability to start an app.
#
#			'invoke' - Initiate execution of a command in the command interface.
#
#			'read' - Open and examine the contents of a specific memory file or record.
#						(E.g., the AI persona's cur-goals.json file.)
#
#			'modify' - Alter the contents of a specific memory file or record.
#
#			'delete' - Delete a given memory file or record.
#


from enum	import	Enum			# Support for enumerated types.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Capability: pass
class Capability(Enum):
	
	"""An enumerated type listing the abstract capabilities for which
		we support assignment of their access permissions.  Note that 
		not all capabilities may be meaningful relative to a given 
		object for which a permissions list is defined."""
	
	LAUNCH	= 'launch'	# The capability to launch (open) an application.
	INVOKE	= 'invoke'	# The capability to invoke (initiate) a command.
	READ	= 'read'	# The capability to open/read a given file or record.
	MODIFY	= 'modify'	# The capability to modify a given file or record.
	DELETE	= 'delete'	# The capability to delete a given file or record.
	
	@property
	def isPassive(cap:Capability):
	
		"""Return True if this is a 'passive' capability. This is only
			important because we automatically confer permission to 
			access all passive capabilities on The_Omniscient_Authority."""

		return cap == Capability.READ

	@property
	def isActive(cap:Capability):

		"""Return True if this is an 'active' capability. This is only
			important because we automatically confer permission to 
			access all active capabilities on The_Omnipotent_Authority."""

		return not cap.isPassive

