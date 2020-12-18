# action.py
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

class Action:
	pass

class ActionByAI(Action):
	pass 

class ActionByHuman(Action):
	pass
	
class ActionBySystem(Action):
	pass

class CommandAction(Action):
	pass
	
class CommandByAI(ActionByAI, CommandAction):
	pass
	
class CommandByHuman(ActionByHuman, CommandAction):
	pass