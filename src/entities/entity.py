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
#		|		|		|
#		|		|		+->	GPT3_Model (abstract)
#		|		|		|		|
#		|		|		|		+-> DaVinci (singleton)
#		|		|		|
#		|		|		+-> GPT2_Model (abstract)
#		|		|
#		|		+->	AI_Subsystem (abstract) 
#		|				|
#		|				+-> Cognitive_System (singleton)
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
#		|		+-> The_GLaDOS_System (singleton)
#		|		|
#		|		+->	GLaDOS_Subsystem (abstract)
#		|		|		|
#		|		|		+-> The_Configuration_System_Entity
#		|		|		|
#		|		|		+->	The_Supervisor_System_Entity
#		|		|		|
#		|		|		+->	The_Window_System_Entity
#		|		|		|
#		|		|		+-> The_Subprocess_System_Entity
#		|		|		|
#		|		|		+-> The_App_System_Entity
#		|		|
#		|		+->	GLaDOS_Application
#		|				|
#		|				+->	(objects for individual apps)
#		|
#		+-> Host_Entity (abstract)
#		|
#		+-> External_Entity (abstract)

from infrastructure.decorators import singleton, classproperty
	# This provides a @classproperty (getter) decorator.

# Forward class declarations.

class	Entity_:		pass

	# AI entities.

class	AI_Entity_:		pass
class	AI_Persona_:	pass
class	AI_System_:		pass
class	AI_Subsystem_:	pass

class	Cognitive_System:	pass	# This AI subsystem is the entire cognitive system in GLaDOS.
class	Cognitive_Stream:	pass	# This AI subsystem is a subsystem of the cognitive system.
class	Receptive_Field:	pass	# This AI subsystem is a subsystem of the cognitive system.
class	Memory_System:		pass	# This AI subsystem is a subsystem of the cognitive system.
class	History_Buffer:		pass	# This AI subsystem is a subsystem of the cognitive system.

	# System entities.

class	System_Entity_:		pass
class	Subsystem_Entity_:	pass

class	The_GLaDOS_Entity:		pass

class	The_SettingsFacility_Entity:	pass
class	The_ConfigSystem_Entity:		pass
class	The_Supervisor_Entity:			pass
class	The_CommandInterface_Entity:	pass
class	The_ProcessSystem_Entity:		pass
class	The_WindowSystem_Entity:		pass
class	The_AppSystem_Entity:			pass

	# Application entities.

class	Application_Entity_:		pass

class	The_HelpApp_Entity:			pass
class	The_InfoApp_Entity:			pass
class	The_GoalsApp_Entity:		pass
class	The_SettingsApp_Entity:		pass
class	The_MemoryApp_Entity:		pass
class	The_ToDoApp_Entity:			pass
class	The_DiaryApp_Entity:		pass
class	The_BrowseApp_Entity:		pass
class	The_CommsApp_Entity:		pass

	# External entities.

class	External_Entity_:		pass
class	Human_Entity_:			pass

#-------------Class definitions.

# Entity within the world of GLaDOS, for reference from within the actions, 
# events, and permissions systems.

class Entity_:	
	# This final underscore denotes that this is an abstract class, and should 
	# not normally be instantiated directly.

	#|==========================================================================
	#|  Private class data members.					  [class definition section]
	#|
	#|		Below we define data members associated with this lexical 
	#|		class, its subclasses, and their instances.  Subclasses may 
	#|		override these definitions.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	_ENTITY_TYPE_NAME = "entity"	# Entity type name, if not overridden.
	_ENTITY_NAME = None		# Instances of an abstract class don't have names.

		#|----------------------------------------------------------------------
		#|	Entity_._isAbstract						 [private class data member]
		#|
		#|		This is set to True to denote that 'Entity_' itself is an
		#|		abstract class that should not be directly instantiated.
		#|		Concrete subclasses should override this value with 'False'.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
	_isAbstract = True		# Class is abstract, unless this is overridden.

	
		#|----------------------------------------------------------------------
		#|	.entityType									 [public class property]
		#|
		#|		For subclasses of Entity_ (or their instances), evaluating 
		#|		their '.entityType' property is intended to return the most 
		#|		immediate superclass that can be considered to represent 
		#|		what 'type' of entity any instance of the current class
		#|		can be considered to be, as opposed to a specific entity.
		#|
		#|		This class property definition needs to be overridden 
		#|		appropriately within any subclass of Entity_ that is itself 
		#|		supposed to represent an entity type, as opposed to a specific 
		#|		entity.
		#|		
		#|		NOTE: Generally speaking, it would *not* be appropriate for 
		#|		any subclass that is defined as a singleton class to override 
		#|		the definition of this property to return that singleton class,
		#|		since an instance of a singleton class would by definition be 
		#|		a specific entity.
		#|
		#|		Please also note that the @classproperty decorator that we're 
		#|		using here is not built into Python, but is imported from the
		#|		infrastructure.decorators module.
		#|
		#|		Note that we can't just assign to a class data member here 
		#|		because at the time this 'def' statement is evaluated, the 
		#|		lexical class Entity_ hasn't finished being defined yet.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	@classproperty
	def entityType(dynamicClass):
		"""By default, just return Entity_.  Subclasses can override this."""
		return Entity_
	

	@property
	def name(thisEntity):
		return thisEntity._name		# Set in instance initializer.

	#/--------------------------------------------------------------------------
	#|	Private instance data members.					   [class documentation]
	#|
	#|		Instances of concrete subclasses of Entity_ should have the
	#|		following attributes set to appropriate data values:
	#|
	#|			._name -	Proper name of this entity instance.
	#|
	#\--------------------------------------------------------------------------
	
	def __init__(inst, name=_ENTITY_NAME):

			# Remember our name.
		_name = name
	
	partOf = None
	#def partOf():
	#	"""If this entity is conceptually part of a larger entity, return 
	#		the larger entity of which it is a part."""
	#	pass

class AI_Entity_(Entity_):

	"""An entity that is an AI or an aspect of an AI."""
	
	_ENTITY_TYPE_NAME = "artificial intelligence"
	
		#|----------------------------------------------------------------------
		#|	.entityType									 [public class property]
		#|
		#|		Note this overrides the definition in Entity_; see there 
		#|		for additional documentation.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	@classproperty
	def entityType(dynamicClass):
		"""By default, just return AI_Entity_.  Subclasses can override this."""
		return AI_Entity_

class AI_Persona_(AI_Entity_):
	_ENTITY_TYPE_NAME = "AI persona"
	@classproperty
	def entityType(dynClass):
		return AI_Persona_

class AI_System_(AI_Entity_):
	"""A complete artificially-intelligent system."""
	_isAbstract = False
	_ENTITY_NAME = "The AI"

class AI_Subsystem_(AI_Entity_):
	"""An entity that is a subsystem of an AI system."""
	_ENTITY_TYPE_NAME = "subsystem of an AI"


	@classproperty
	def entityType(dynamicClass):
		return AI_Subsystem_

#====================================================================
# Entities for the AI's cognitive system and its various components.

class Cognitive_System(AI_Subsystem_):

	"""An instance of the cognitive system would mean, the cognitive system
		when configured for a specific AI persona."""

	_isAbstract = False
	_ENTITY_NAME = "Cognitive System"
	partOf = AI_System_
	
	def __inst__(thisCognitiveSystem:Cognitive_System, personaEntity:AI_Persona_):
		thisCognitiveSystem._personaEntity = personaEntity

class Cognitive_Stream(AI_Subsystem_):
	_isAbstract = False
	_ENTITY_NAME = "Cognitive Stream"
	partOf = Cognitive_System

class Receptive_Field(AI_Subsystem_):
	_isAbstract = False
	_ENTITY_NAME = "Receptive Field"
	partOf = AI_System_

class Memory_System(AI_Subsystem_):
	_isAbstract = False
	_ENTITY_NAME = "Memory System"
	partOf = AI_System_

class History_Buffer(AI_Subsystem_):
	_isAbstract = False
	_ENTITY_NAME = "Memory System"
	partOf = AI_System_

#=========================================================================
# Abstract and concrete classes for system entities, which in this context
# means, entities that are part of or associated with the GLaDOS system,
# but that are not considered part of the AI itself.

class System_Entity_(Entity_):
	"""An entity that is the GLaDOS system, or a component of the system."""
	
	_ENTITY_TYPE_NAME = "system"	
	
		#|----------------------------------------------------------------------
		#|	.entityType									 [public class property]
		#|
		#|		Note this overrides the definition in Entity_; see there 
		#|		for additional documentation.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	@classproperty
	def entityType(dynamicClass):
		"""By default, just return System_Entity_.  Subclasses can override this."""
		return System_Entity_

@singleton
class The_GLaDOS_Entity(System_Entity_):
	_isAbstract = False
	_ENTITY_NAME = "GLaDOS System"

class Subsystem_Entity_(System_Entity_):

	_ENTITY_TYPE_NAME = "subsystem of GLaDOS"	

	@classproperty
	def entityType(dynamicClass):
		return Subsystem_Entity_

	#|===================================================================
	#| Here, we define entities representing the various major subsystems 
	#| of GLaDOS that are not considered aspects of the AI itself.

@singleton
class The_SettingsFacility_Entity(Subsystem_Entity_):
	_isAbstract = False
	_ENTITY_NAME = "Settings Facility"
	partOf = The_GLaDOS_Entity

@singleton
class The_ConfigSystem_Entity(Subsystem_Entity_):
	_isAbstract = False
	_ENTITY_NAME = "Configuration System"
	partOf = The_GLaDOS_Entity

@singleton
class The_Supervisor_Entity(Subsystem_Entity_):
	_isAbstract = False
	_ENTITY_NAME = "Supervisor"
	partOf = The_GLaDOS_Entity

@singleton
class The_CommandInterface_Entity(Subsystem_Entity_):
	_isAbstract = False
	_ENTITY_NAME = "Command Interface"
	partOf = The_GLaDOS_Entity
	
@singleton
class The_ProcessSystem_Entity(Subsystem_Entity_):
	_isAbstract = False
	_ENTITY_NAME = "Process System"
	partOf = The_GLaDOS_Entity
	
@singleton
class The_WindowSystem_Entity(Subsystem_Entity_):
	_isAbstract = False
	_ENTITY_NAME = "Window System"
	partOf = The_GLaDOS_Entity
	
@singleton
class The_AppSystem_Entity(Subsystem_Entity_):
	_isAbstract = False
	_ENTITY_NAME = "Applications System"
	partOf = The_GLaDOS_Entity
	

#=====================================================================
# Entities associated with the host computer on which we are running.

class Host_Entity_(Entity_):
	"""An entity that is the host on which the GLaDOS system is running, or a component of the host"""
		#|----------------------------------------------------------------------
		#|	.entityType									 [public class property]
		#|
		#|		Note this overrides the definition in Entity_; see there 
		#|		for additional documentation.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	@classproperty
	def entityType(dynamicClass):
		"""By default, just return Host_Entity_.  Subclasses can override this."""
		return Host_Entity_
	

#=======================================================================
# Entities associated with the external world, outside of this computer.

class External_Entity_(Entity_):
	"""Some other entity out in the outside world, beyond the current host."""
		#|----------------------------------------------------------------------
		#|	.entityType									 [public class property]
		#|
		#|		Note this overrides the definition in Entity_; see there 
		#|		for additional documentation.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	@classproperty
	def entityType(dynamicClass):
		"""By default, just return External_Entity_.  Subclasses can override this."""
		return External_Entity_
	
#====================================================================
# Abstract and concrete classes for human entities.

class Human_Entity_(Entity_):
	"""An entity that is a human, or an aspect of a human."""
	_ENTITY_TYPE_NAME = "human"
	
		#|----------------------------------------------------------------------
		#|	.entityType									 [public class property]
		#|
		#|		Note this overrides the definition in Entity_; see there 
		#|		for additional documentation.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	@classproperty
	def entityType(dynamicClass):
		"""By default, just return AI_Entity_.  Subclasses can override this."""
		return AI_Entity_
	