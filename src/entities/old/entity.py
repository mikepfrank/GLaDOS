# entity.py
# Main file for the entity system.

# This is a collection of modules to facilitate representing and working with 
# entities.  An 'entity,' within GLaDOS, denotes any active agent, being, 
# process or system that is meaningful within the world that GLaDOS operates in.  
# Examples of things that could be considered as entities within GLaDOS:
#
#	1.  A particular language model (e.g. the GPT-3 DaVinci model at OpenAI).
#	2.  An A.I. being that is being supported within GLaDOS (e.g., Gladys).
#	3.  A human being that is interacting with the A.I. (e.g., Michael).
#	4.  An overall GLaDOS system instance that is executing.
#	5.  A particular subsystem of the active GLaDOS instance (e.g., supervisor).
#	6.  A particular process running within GLaDOS (e.g., a comms tool).
#	7.  The Linux virtual server host that GLaDOS is running on.
#
# The purpose of representing entities explicitly within GLaDOS is so that 
# various properties can be attached to them; for example, fine-grained 
# permissions specifying which specific entities are authorized to execute 
# which specific commands.  Also, actions and events within GLaDOS are
# attributed to specific entities.

#	Class hierarchy for the entity system:
#	--------------------------------------
#
#	Entity (abstract)
#		|
#		+->	AI_Entity (abstract)
#		|		|
#		|		+-> AI_Persona (abstract)
#		|		|		|
#		|		|		+-> Gladys (singleton)
#		|		|		|
#		|		|		+-> Samson (singleton)
#		|		|
#		|		+->	AI_LanguageModel (abstract)
#		|				|
#		|				+->	GPT3_Model (abstract)
#		|				|		|
#		|				|		+-> DaVinci (singleton)
#		|				|
#		|				+-> GPT2_Model (abstract)
#		|
#		+-> Human_Entity (abstract)
#		|		|
#		|		+->	Mike (singleton)
#		|		|
#		|		+-> Matt (singleton)
#		|		|
#		|		+-> Coleman (singleton)
#		|		|
#		|		+-> Colin (singleton)
#		|
#		|
#		+-> System_Entity (abstract)
#		|		|
#		|		+-> GLaDOS_System (singleton)
#		|		|
#		|		+->	GLaDOS_Subsystem (abstract)
#		|		|		|
#		|		|		+-> Configuration_System
#		|		|		|
#		|		|		+->	Supervisor_System
#		|		|		|
#		|		|		+->	Window_System
#		|		|		|
#		|		|		+-> Subprocess_System
#		|		|		|
#		|		|		+-> App_System
#		|		|		|
#		|		|		+->	Congitive_System
#		|		|
#		|		+->	GLaDOS_Application
#		|				|
#		|				+->	(objects for individual apps)
#		|
#		+-> Host_Entity (abstract)
#		|
#		+-> External_Entity (abstract)

# Entity within the world of GLaDOS, for reference from within the actions, 
# events, and permissions systems.

class Entity_:	
	# This final underscore denotes that this is an abstract class, and should 
	# not normally be instantiated directly.

	#/--------------------------------------------------------------------------
	#|	Private class data members.					   	   [class documentation]
	#|
	#|		For this lexical class, and all of its subclasses, the 
	#|		following dynamic attributes should be set dynamically 
	#|		(as soon as possible after the class is defined).  Note 
	#|		that we cannot set these particular attributes dynamically 
	#|		*in* this class definition, itself, because their 
	#|		construction requires this class to already exist, and, at 
	#|		class definition time, it doesn't, yet.
	#|
	#|			._type [class] -	
	#|
	#|				This is the class object for the most immediate 
	#|				superclass of the current dynamic class (which may 
	#|				be the current dynamic class, itself) that can be 
	#|				considered to represent an 'entity type' (as opposed 
	#|				to a specific entity).  After you have defined a 
	#|				subclass of this lexical class that has redefined 
	#|				its ._setEntityType() class method appropriately to
	#|				set this class attribute, you should immediately 
	#|				call that class method to actually do the deed.
	#|							
	#|
	#\--------------------------------------------------------------------------
	
	

	#|==========================================================================
	#|  Private class data members.					  [class definition section]
	#|
	#|		Below we define data members associated with this lexical 
	#|		class, its subclasses, and their instances.  Subclasses may 
	#|		override these definitions.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|----------------------------------------------------------------------
		#|	Entity_._isAbstract						 [private class data member]
		#|
		#|		This is set to True to denote that 'Entity_' itself is an
		#|		abstract class that should not be directly instantiated.
		#|		Concrete subclasses should override this value with 'False'.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	_isAbstract = True


	#|==========================================================================
	#|	Private class functions.					  [class definition section]
	#|
	#|		Below we define pure functions that apply to this lexical
	#|		class, its subclasses, and their instances.  Subclasses may
	#|		override these definitions.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		#|----------------------------------------------------------------------
		#|	Entity_._setEntityType()					[private class function]
		#|
		#|		This function dynamically sets the '._type' attribute of
		#|		the Entity_, class to point to the Entity_ class, itself.
		#|
		#|		Subclasses of Entity_ that wish to reassign their entity
		#|		type to themselves should override this definition in the
		#|		appropriate way (changing Entity_ below to their class).
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	#|==========================================================================
	#|	Public class methods.						  [class definition section]
	#|
	#|		Below we define methods that apply to this lexical class,
	#|		its subclasses, and their instances.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		#|----------------------------------------------------------------------
		#|	Entity_.entityType()
		#|
		#|		This method returns the value of the ._type attribute of 
		#|		the current *dynamic* class.  It may be applied to any
		#|		subclass of Entity_ or to any of that class's instances.
		#|		
		#|		The intent is to return a class object corresponding to
		#|		that entity's "type."
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	@classmethod
	def entityType(thisClass):
		return thisClass._type   # Return value of this class-level data member.

	
	#/--------------------------------------------------------------------------
	#|	Private instance data members.					   [class documentation]
	#|
	#|		Instances of concrete subclasses of Entity_ should have the
	#|		following attributes set to appropriate data values:
	#|
	#|			._name -	Proper name of this entity instance.
	#|
	#\--------------------------------------------------------------------------
	
	
	

	def __new__(thisClass, *args, **kwargs):
	
			# Set the class-level data member '._entityType' of this class 
			
		thisClass._entityType = thisClass
		return super(Entity, thisClass, *args, **kwargs)
	
	def __init__(inst, name=None):

			# Remember our name.
		_name = name
	
	pass

class AI_Entity:
	"""An entity that is an AI or an aspect of an AI."""
	pass

class Human_Entity:
	"""An entity that is a human, or an aspect of a human."""
	pass

class System_Entity:
	"""An entity that is the GLaDOS system, or a component of the system."""
	pass

class Host_Entity:
	"""An entity that is the host on which the GLaDOS system is running, or a component of the host"""
	pass

class External_Entity:
	"""Some other entity out in the outside world, beyond the current host."""
	pass