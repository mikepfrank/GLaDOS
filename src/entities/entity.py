#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 entities/entity.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------

# entity.py
# Main file for the entity system.

# This is a collection of classes to facilitate representing and working with 
# so-called entities.  An 'entity,' within GLaDOS, denotes *any* active agent, being, 
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#	Class hierarchy for the entity system:
#	--------------------------------------
#
#	Entity (abstract)
#		|
#		+->	AI_Entity_ (abstract)
#		|		|
#		|		+-> AI_Persona (concrete)
#		|		|		|
#		|		|		+-> Gladys (singleton)
#		|		|		|
#		|		|		+-> Samson (singleton)
#		|		|
#		|		+->	AI_LanguageModel (concrete)
#		|		|		|
#		|		|		+->	GPT3_Model (abstract)
#		|		|		|		|
#		|		|		|		+-> DaVinci (singleton)
#		|		|		|
#		|		|		+-> GPT2_Model (abstract)
#		|		|
#		|		+->	AI_Subsystem (concrete) 
#		|				|
#		|				+-> Cognitive_System (singleton)
#		|
#		+-> Human_Entity_ (abstract)
#		|		|
#		|		+-> Operator_Entity (concrete)
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
#		+-> System_Entity_ (abstract)
#		|		|
#		|		+-> The_GLaDOS_System (singleton)
#		|		|
#		|		+->	GLaDOS_Subsystem (concrete)
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
#		|		+->	GLaDOS_Application (concrete)
#		|				|
#		|				+->	(objects for individual apps)
#		|
#		+-> Host_Entity (abstract)
#		|
#		+-> External_Entity (abstract)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from	os	import path

from	infrastructure.decorators import singleton, classproperty
	# This provides a @classproperty (getter) decorator.

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from	gpt3.api 	import	CHAT_ROLE_SYSTEM, CHAT_ROLE_USER, CHAT_ROLE_AI

from	auth.authority import (
			theBaseAuthority,
			theAIUserAuthority,
			theHumanUserAuthority,
			theOperatorAuthority,
			theSystemAuthority,
		)

#=====================================================
# Forward class declarations. (For use in type hints.)

class	Entity_:			pass	# Abstract base class (ABC) for general entities.

	#~~~~~~~~~~~~~~~~~
	# System entities.

class	System_Entity_:					pass
	# Abstract base class (ABC) for entities associated with the GLaDOS system.

class	Subsystem_Entity(System_Entity_):	pass
	# 	- Class of entities that are subsystems of the whole system.

class	The_GLaDOS_Entity:				pass	# This is the entire GLaDOS system.

class	The_SettingsFacility_Entity:	pass	#	- This is a subsystem of GLaDOS.
class	The_ConfigSystem_Entity:		pass	#	- This is a subsystem of GLaDOS.
class	The_Supervisor_Entity:			pass	#	- This is a subsystem of GLaDOS.
class	The_ActionSystem_Entity:		pass	#		This is a subsystem of the Supervisor.
class	The_CommandInterface_Entity:	pass	#	- This is a subsystem of GLaDOS.
class	The_ProcessSystem_Entity:		pass	#	- This is a subsystem of GLaDOS.
class	The_WindowSystem_Entity:		pass	#	- This is a subsystem of GLaDOS.
class	The_AppSystem_Entity:			pass	#	- This is a subsystem of GLaDOS.
# In addition to these, the Cognitive_System (below) can also be considered a subsystem of GLaDOS.

	#~~~~~~~~~~~~~~~~~~~~~~
	# Application entities.

class	Application_Entity_:		pass	# ABC for entities representing applications within GLaDOS.

class	The_InfoApp_Entity:			pass	#	- This is a specific application within GLaDOS.
class	The_ClockApp_Entity:		pass
class	The_HelpApp_Entity:			pass
class	The_GoalsApp_Entity:		pass
class	The_SettingsApp_Entity:		pass
class	The_MemoryApp_Entity:		pass
class	The_ToDoApp_Entity:			pass
class	The_DiaryApp_Entity:		pass
class	The_BrowseApp_Entity:		pass
class	The_CommsApp_Entity:		pass

	# AI entities.

class	AI_Entity_:			pass	# ABC for entities that represent an AI, or an aspect of an AI.
class	AI_Persona:			pass	# 	- Class of entities representing specific AI personas.
class	AI_System:			pass	#	- Class of entities representing entire AI systems.
class	AI_Subsystem:		pass	#	- Class of entities representing subsystems of larger AI systems.
class	AI_LanguageModel:	pass	#	- Class of entities representing AI language model subsystems.

class	Cognitive_System:	pass	# This AI subsystem is the entire cognitive system in GLaDOS.
class	Cognitive_Stream:	pass	# 	- This AI subsystem is a subsystem of the cognitive system.
class	Receptive_Field:	pass	# 	- This AI subsystem is a subsystem of the cognitive system.
class	Memory_System:		pass	# 	- This AI subsystem is a subsystem of the cognitive system.
class	History_Buffer:		pass	# 	- This AI subsystem is a subsystem of the cognitive system.

	# External entities.

class	External_Entity_:		pass
class	Human_Entity_:			pass
class	Operator_Entity:		pass

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
	_ENTITY_ID = None		# No ID's either
	_ENTITY_AUTHS = {theBaseAuthority}	# We only have the base authority by default.
	_ENTITY_CHAT_ROLE = None	# No chat role by default.
	_ENTITY_CHAT_NAME = None	# No chat name by default.

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

	@property
	def ID(thisEntity):
		return thisEntity._id
	
	@property
	def auths(thisEntity):
		return thisEntity._auths
	
	@property
	def chatRole(thisEntity):
		return thisEntity._chatRole
	
	@property
	def chatName(thisEntity):
		return thisEntity._chatName

	def __str__(thisEntity):

		# Preferentially, use the entity's short ID.
		if thisEntity.ID is not None:
			return thisEntity.ID	# Return the short ID string.

		# If we don't have a short ID, use the entity's name instead.
		return thisEntity.name

	#/--------------------------------------------------------------------------
	#|	Private instance data members.					   [class documentation]
	#|
	#|		Instances of concrete subclasses of Entity_ should have the
	#|		following attributes set to appropriate data values:
	#|
	#|			._name -	Proper name of this entity instance.
	#|
	#|			._id - 		Short name of entity for use in prompts.
	#|
	#\--------------------------------------------------------------------------
	
	def __init__(inst, name=None, eid=None, auths=None, chatRole=None, chatName=None):

		if name is None:
			name = inst._ENTITY_NAME

		if eid is None:
			eid = inst._ENTITY_ID

		if auths is None:
			auths = inst._ENTITY_AUTHS
			
		# Make sure the base authority is in our auth list 
		# (in case we're in a subclass that left it out).
		auths.add(theBaseAuthority)

		if chatRole is None:
			chatRole = inst._ENTITY_CHAT_ROLE

		# Default chatName to the entity ID if not specified in argument or subclass.
		# Except for system role.
		if chatName is None and chatRole is not CHAT_ROLE_SYSTEM:
			if inst._ENTITY_CHAT_NAME is None:
				chatName = eid
			else:
				chatName = inst._ENTITY_CHAT_NAME

			# Remember our name and ID & authority list, etc.
		inst._name		= name
		inst._id		= eid
		inst._auths		= auths
		inst._chatRole	= chatRole
		inst._chatName	= chatName

		_logger.debug(f"Entity.__init__(): Created entity [{name}], ID [{eid}], chatRole [{chatRole}], chatName [{chatName}]")

	# Move this closer to top of class
	partOf = None
	#def partOf():
	#	"""If this entity is conceptually part of a larger entity, return 
	#		the larger entity of which it is a part."""
	#	pass

#=========================================================================
# Abstract and concrete classes for system entities, which in this context
# means, entities that are part of or associated with the GLaDOS system,
# but that are not considered part of the AI itself.

class System_Entity_(Entity_):
	"""An entity that is the GLaDOS system, or a component of the system."""
	
	_ENTITY_TYPE_NAME = "system"	
	_ENTITY_AUTHS = {theSystemAuthority}

	_ENTITY_CHAT_ROLE = CHAT_ROLE_SYSTEM
	#_ENTITY_CHAT_NAME = "System"			# No name by default.
	
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
	_isAbstract			= False
	_ENTITY_NAME		= "GladOS System"
	_ENTITY_ID			= "GladOS"
	#_ENTITY_CHAT_NAME	= "GladOS"	# Let's just call it 'system'

class Subsystem_Entity(System_Entity_):

	_isAbstract = False
	_ENTITY_TYPE_NAME = "subsystem of GLaDOS"	

	@classproperty
	def entityType(dynamicClass):
		return Subsystem_Entity

	#|===================================================================
	#| Here, we define entities representing the various major subsystems 
	#| of GLaDOS that are not considered aspects of the AI itself.

@singleton
class The_SettingsFacility_Entity(Subsystem_Entity):
	_isAbstract = False
	
	_ENTITY_NAME = "Settings Facility"
	_ENTITY_CHAT_NAME = "Settings"

	partOf = The_GLaDOS_Entity()


@singleton
class The_ConfigSystem_Entity(Subsystem_Entity):
	_isAbstract = False
	_ENTITY_NAME = "Configuration System"
	_ENTITY_CHAT_NAME = "ConfigSys"
	partOf = The_GLaDOS_Entity()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Supervisor_Entity(Subsystem_Entity):

	"""The_Supervisor_Entity		         [singleton class--subsystem entity]

			This entity singleton represents the Supervisor or Supervi-
			sory Subsystem, which is a subsystem of GLaDOS.  It is the
			subsystem that is in charge of starting up and managing the
			other major subsystems.  Its code objects are contained in
			the 'supervisor' package within the GLaDOS codebase.

			The explicit actions (detectable by other subsystems) that
			the Supervisor conceives/initiates include the following:

				* Announcing that the system is starting up.
					(supervisor._AnnounceStartupAction)

			Subsystems of the Supervisory system include the following:

				* The Action Processing Subsystem.							 """

	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	_isAbstract		= False		# Not an ABC. The instance is a specific entity.

	_ENTITY_NAME	= "Supervisory Subsystem"
	_ENTITY_ID		= "Supervisor"	# The ID is a short name used e.g. in prompts.

	_ENTITY_CHAT_NAME = "Supervisor"	# The chat name is the name used in chat API.

	partOf			= The_GLaDOS_Entity()	# This system is a subsytem of GLaDOS.

#__/ End singleton subsystem entity class The_Supervisor_Entity.


@singleton
class The_CommandInterface_Entity(Subsystem_Entity):
	_isAbstract 		= False
	_ENTITY_NAME 		= "Command Interface"
	_ENTITY_ID 			= "CmdIface"
	_ENTITY_CHAT_NAME 	= "CmdIface"
	partOf 				= The_GLaDOS_Entity()
	
@singleton
class The_ProcessSystem_Entity(Subsystem_Entity):
	_isAbstract 		= False
	_ENTITY_NAME 		= "Process System"
	_ENTITY_ID 			= "ProcessSys"
	_ENTITY_CHAT_NAME 	= "ProcessSys"
	partOf 				= The_GLaDOS_Entity()
	
@singleton
class The_WindowSystem_Entity(Subsystem_Entity):
	_isAbstract 		= False
	_ENTITY_NAME 		= "Window System"
	_ENTITY_ID 			= "WindowSys"
	_ENTITY_CHAT_NAME 	= "WindowSys"
	partOf 				= The_GLaDOS_Entity()
	
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_AppSystem_Entity(Subsystem_Entity):

	"""The_AppSystem_Entity					 [singleton class--subsystem entity]

			This entity singleton represents the AppSystem or application
			subsystem of GLaDOS.  It is the subsystem that is responsible
			for starting up an managing individual end-user applications
			within GLaDOS.  (Note that in GLaDOS, the "end user" means the
			AI, not a human--since GLaDOS is an OS designed for use by AIs.)

			The explicit actions (detectable by other subsystems) that
			the AppSystem conceives/initiates include the following:

				* Auto-opening an application's window on startup.
					(appSystem._AutoOpenWindowAction)

			Subsystems of the Supervisory system include the following:

				* Each individual application within GLaDOS can be
					considered a subsystem of the application system.
																			 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	_isAbstract		= False		# Not an ABC. The instance is a specific entity.


	_ENTITY_NAME	= "Applications System"
	_ENTITY_ID		= "AppSystem"	# The ID is a short name used e.g. in prompts.

	_ENTITY_CHAT_NAME = "AppSystem"	# The chat name is the name used in chat API.

	partOf			= The_GLaDOS_Entity()	# This system is a subsytem of GLaDOS.
	
#__/ End singleton subsystem entity class.


class Application_Entity_(Subsystem_Entity):

	"""Abstract class for application entities."""

	_isAbstract		= True

	_ENTITY_TYPE_NAME = "application"

	partOf			= The_AppSystem_Entity()	# Each application is a subsystem of the AppSystem.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Entity singletons representing the various applications within GLaDOS.

@singleton
class The_InfoApp_Entity(Application_Entity_):

	"""Entity singleton representing the Info app."""

	_isAbstract			= False

	_ENTITY_NAME		= "Info App"
	_ENTITY_ID			= "InfoApp"
	_ENTITY_CHAT_NAME 	= "InfoApp"

@singleton
class The_ClockApp_Entity(Application_Entity_):

	"""Entity singleton representing the Clock app."""

	_isAbstract			= False

	_ENTITY_NAME		= "Clock App"
	_ENTITY_ID			= "ClockApp"
	_ENTITY_CHAT_NAME 	= "ClockApp"

@singleton
class The_HelpApp_Entity(Application_Entity_):

	"""Entity singleton representing the Clock app."""

	_isAbstract			= False

	_ENTITY_NAME		= "Help App"
	_ENTITY_ID			= "HelpApp"
	_ENTITY_CHAT_NAME 	= "HelpApp"

@singleton
class The_GoalsApp_Entity(Application_Entity_):

	"""Entity singleton representing the Goals app."""

	_isAbstract			= False

	_ENTITY_NAME		= "Goals App"
	_ENTITY_ID			= "GoalsApp"
	_ENTITY_CHAT_NAME 	= "GoalsApp"

	#partOf			= The_GLaDOS_Entity()	# Each application is a subsystem of GLaDOS.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AI_Entity_(Entity_):

	"""An entity that is an AI or an aspect of an AI."""
	
	_ENTITY_TYPE_NAME = "artificial intelligence"
	_ENTITY_AUTHS = {theAIUserAuthority}

	_ENTITY_CHAT_ROLE = CHAT_ROLE_AI
	#_ENTITY_CHAT_ROLE = CHAT_ROLE_USER
		# Tried this temporarily while debugging.
	
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

class AI_Persona(AI_Entity_):
	_isAbstract = False

	_ENTITY_TYPE_NAME = "The AI's persona"

	@classproperty
	def entityType(dynClass):
		return AI_Persona

class AI_System(AI_Entity_):

	"""A complete artificially-intelligent system."""

	_isAbstract = False
	_ENTITY_NAME = "The AI"

	def __inst__(newAiSystem:AI_System, personaEntity:AI_Persona):

		"""Initializes a new instance of an AI_System entity that
			represents an AI_System that is configured to work on
			behalf of a particular AI persona."""

		aiSystem = newAiSystem

		aiSystem._personaEntity = personaEntity
			# Record which AI persona this AI system is configured to exhibit.

#__/ End AI entity class AI_System.


class AI_Subsystem(AI_Entity_):

	"""An entity that is a subsystem of an AI system."""

	_isAbstract = False
	_ENTITY_TYPE_NAME = "subsystem of an AI"

	#_ENTITY_CHAT_ROLE = CHAT_ROLE_SYSTEM
		# Tried this temporarily while debugging.

	@classproperty
	def entityType(dynamicClass):
		return AI_Subsystem

	#====================================================================
	# Entities for the AI's cognitive system and its various components.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Cognitive_System(AI_Subsystem, Subsystem_Entity):

	"""Cognitive_System		         		 [singleton class--subsystem entity]

			This is a class for entities representing the AI's cognitive
			system.  Please note that this is not a singleton class--it
			can have different instances, which would correspond to the
			cognitive system when configured for use by a specific AI
			persona. (At present, GLaDOS does not yet support multiple
			simultaneously active AI personas, but, it may do so in some
			future version.)

			Please note that this entity is considered to be a subsystem
			both of the AI as a whole, and of the GLaDOS operating system.

			The explicit actions (detectable by other subsystems) that
			the Supervisor conceives/initiates include the following:

				* Announcing that the receptive field is available.
					(mindSystem._AnnounceFieldExistsAction)
																			 """
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	_isAbstract		= False		# Not an ABC. An instance is a specific entity.

	_ENTITY_NAME	= "Cognitive System"
	_ENTITY_ID		= "MindSys"	# The ID is a short name used e.g. in prompts.
	_ENTITY_CHAT_NAME = "MindSys"	# The chat name is the name used in chat API.
	
	# Note: The .partof attribute for this class is initialized on an
	# instance-by-instance basis in the instance initializer method, below.
	
	def __inst__(thisCognitiveSystem:Cognitive_System, personaEntity:AI_Persona):

		csEntity = thisCognitiveSystem

		csEntity._personaEntity = personaEntity

			#==================================================================
			# The congitive subsystem is special in that it is considered to be
			# a part of both the "artifically intelligent system" as a whole
			# (which includes the GPT-3 NLP model running in OpenAI's cloud),
			# and of the GLaDOS operating system, which itself runs locally.
			# Thus, our ".partof" attribute expresses a set of entities that 
			# this entity is part of, rather than a single entity.  However,
			# This doesn't matter very much right now, since the '.partof'
			# attribute isn't actually used for anything yet.  So, consider it
			# documentation for now.  In the future, we might enable the AI to
			# inspect these relations, though.

		csEntity.partof = supersystems = set()	# Initialize to empty set.
			# Next, we'll actually create and add the elements to this set.

			#-------------------------------------------------------------------
			# This creates an entity that represents the entire larger AI System
			# that this cognitive system instance is a part of.  It is working
			# on behalf of the same AI persona that we are.

		theAI = AI_System(personaEntity)

			#------------------------------------------------------------
			# This just retrieves the singleton entity defined above that
			# represents the entire GLaDOS operating system.
		
		GLaDOS = The_GLaDOS_Entity()		# Singleton representing GLaDOS.

			#-----------------------------------------------------------------
			# OK, now this actually adds those entities to the set of "parent"
			# entities that the present entity is declared to be a part of.

		supersystems.add(theAI)		# This entity is part of the AI as a whole.
		supersystems.add(GLaDOS)	# This entity is also a part of GLaDOS.
		
	#__/ End instance initializer for Cognitive_System class.

#__/ End AI/subsystem entity class Cognitive_System.


class Cognitive_Stream(AI_Subsystem):
	_isAbstract = False
	_ENTITY_NAME = "Cognitive Stream"
	
	partOf = Cognitive_System

@singleton
class Receptive_Field(AI_Subsystem):
	_isAbstract = False

	_ENTITY_NAME		= "Receptive Field"
	_ENTITY_ID			= "Field"
	_ENTITY_CHAT_NAME	= "Field"

	partOf = AI_System

class Memory_System(AI_Subsystem):
	_isAbstract = False
	_ENTITY_NAME = "Memory System"
	partOf = AI_System

class History_Buffer(AI_Subsystem):
	_isAbstract = False
	_ENTITY_NAME = "History Buffer"
	partOf = AI_System

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
	_ENTITY_AUTHS = {theHumanUserAuthority}

	_ENTITY_CHAT_ROLE = CHAT_ROLE_USER
	
		#|----------------------------------------------------------------------
		#|	.entityType									 [public class property]
		#|
		#|		Note this overrides the definition in Entity_; see there 
		#|		for additional documentation.
		#|		
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	@classproperty
	def entityType(dynamicClass):
		"""By default, just return Human_Entity_.  Subclasses can override this."""
		return Human_Entity_
	
# Instead of hard-coding the ID of the Operator entity, we really
# should get it from the config file.  But for now, we'll just
# hard-code it here.  (Note that this is a singleton entity, so
# it doesn't matter if we have multiple instances of the Operator
# class, they will all refer to the same entity.)

#@singleton
class Operator_Entity(Human_Entity_):
	_isAbstract		= False
	_ENTITY_NAME	= "System Operator"
	_ENTITY_ID		= "Mike" #"Operator"
	_ENTITY_AUTHS	= {theOperatorAuthority}

	_ENTITY_CHAT_NAME = _ENTITY_ID
		# We'll also use the ID as the chat name, for now.
