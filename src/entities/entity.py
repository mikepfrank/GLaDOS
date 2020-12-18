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

class Entity:	# Entity within the world of GLaDOS, for reference from within the actions, events, and permissions systems.
	# An entity has a name
	
	_isAbstract = True
	
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