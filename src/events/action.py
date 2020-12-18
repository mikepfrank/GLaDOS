# action.py
#
#	Please note that, although this module is used throughout GLaDOS,
#	it conceptually is part of the supervisor subsystem.
#
# Class for an action, which represents an intentional act taken
# by some actor (agent) in the system.  This could be the A.I.,
# a human user, or a GLaDOS application, process, or subsystem.
#
# The actors are taken from the entities package.
#
# Actions have (at least) two associated times:
#	* When the action was 'conceived' (created).
#	* When the action was 'taken' (executed).
#
# Classes include:
#	* ActionSystem - Singleton class for processing actions.
#
#

# To add:
#
#		ActionProcessor -
#
#			Every time the AI generates an action, the supervisor decides
#			what to do with it  Generally, several things happen:
#
#				* An event for the action is created and appended to 
#					the AI's own cognitive stream.
#
#				* The event is handed to the GLaDOS command interface
#					for possible processing.
#
#			The ActionProcessor class should probably be defined in the
#			TheSupervisor module--but (for actions that take place in the
#			AI's cognitive sphere) executed in the mind process.
#

class TheActionProcessor: pass

class Action_:
	def __init__(self):
	
		"""The only thing that *every* Action_ object created in the
			system needs to do is report itself to the supervisory 
			subsystem's action processor.  This then implements the 
			action by dispatching its effects to the appropriate 
			subsystems.  Subclasses' init method should make sure 
			to invoke this super method."""
			
		TheActionProcessor().process(self)


class ActionByAI_(Action):
	pass 

class ActionByHuman_(Action):
	pass
	
class ActionBySystem_(Action):
	pass

class CommandAction_(Action):
	pass
	
class CommandByAI_(ActionByAI, CommandAction):
	pass
	
class CommandByHuman_(ActionByHuman, CommandAction):
	pass
	
@singleton
class TheActionProcessor:
	def process(action:Action_):
		pass
		
@singleton
class TheActionSystem:
	def __init__(inst):
		TheActionProcessor()
