
from	infrastructure.decorators	import	singleton

from	entities.entity				import	(
		AI_Entity_,			# Abstract base class for AI entities.
		Cognitive_System	# The AI's cognitive subsystem specifically.
	)

from	config.configuration		import	TheAIPersonaConfig

from	supervisor.action			import	(
		Action_, SpeechAction_, CommandAction_, ActionChannel_, ActionBySystem_
	)

class	ActionByAI_:					pass
class	AI_Speech_Action:				pass
class	CommandByAI_:					pass
class	The_AI_Cognosphere_Channel:		pass

#---------------------------------------------------------------------------------------
# The following classes are for various types of actions that could be taken by the AI.


class ActionByAI_(Action_):
	def __init__(thisAiAction, 
			description:str="A generic action was taken by the AI.",
				# REQUIRED. A description string. SUBCLASSES SHOULD OVERRIDE THIS VALUE.
			conceiver:AI_Entity_=None,		# The AI entity that conceived of taking this action.
			importance:int=0,			# Importance level that we declare this action to have. Default 0.
		):
		
			# Remember the declared importance level of this AI action.
		thisAiAction._importance = importance

			# Set the conceiver implicitly.
		if conceiver is None:
			conceiver = Cognitive_System
			# We ascribe AI actions to the AI's cognitive system unless they're more specifically
			# attributed to its persona, API, or other aspect of the AI.

		super(ActionByAI_, thisAiAction).__init__(description, conceiver=conceiver)


class AI_Speech_Action(SpeechAction_, ActionByAI_):

	"""Class for actions by the AI that consist of it producing some text output.
		At the moment, all actions taken by the AI start out as this type of action,
		and then other types of actions are derived from them as they are 
		interpreted by the system (in particular, the command interface).
	
		AI_Speech_Action instances get created in the main loop of the cognitive
		system upon receiving a completion from the AI; they are then automatically
		initiated. Credit for their conception goes to the persona (annotated as 
		running on the language model); credit for their initiation goes to the 
		cognitive system (on behalf of the persona); credit for their execution 
		goes to the cognitive system as well I guess.  
		
		For resulting command actions, we can credit conception to the AI, initiation
		to the Supervisor, and execution to whatever subsystem/app implements them.
		They can also link back to the speech action they were derived from.
	"""
		
	def __init__(this,
			aiTextOut:str=None,		# Text output by the AI.
			theAI:AI_Entity_=None,	# The AI entity that conceived of taking this action.
		):
		
			# Get a string denoting the AI.
		this._aiStr = aiStr = str(theAI)
		
			# Store the AI's output text for later reference.
		this._aiTextOut = aiTextOut
		
			# Compose a description, pretty generic but that's fine for now. 
		description = f"AI {aiStr} generated the text: [{aiTextOut}]"
			# (Later on, if this speech action ends up getting parsed as a command string,
			# then this action may get transmuted into a command action of some sort.)
			
			# Dispatch to next class in inheritance chain to finish initialization.
		super(AI_Speech_Action, this).__init__(aiTextOut, description, theAI)
			# Note dispatch order goes first to SpeechAction_, then to ActionByAI_.

	# Note to self: Should we go ahead and add AI speech actions to the cognitive stream 
	# immediately upon conception? Or wait until the command (if any) is interpreted?
	# I'm thinking yes, we should go ahead and add them at execution time, and the 
	# command (if any) should be treated as a second action that is consequent on the 
	# first action. Use ".interpretedAs" and ".triggeredBy" members as appropriate.

class CommandByAI_(AI_Speech_Action, CommandAction_):
	pass
	


# Consider moving this to the mind package since it depends on configuration
# parameters for the AI persona.
@singleton
class The_AI_Cognosphere_Channel(ActionChannel_):

	"""The action system creates this specific action channel which is for 
		reporting actions that we consider eligible for entering into the
		AI's sphere of awareness.  Such actions include:
		
			(1) All actions that were conceived/initiated by the AI 
				itself.
			
			(2) All actions that were conceived/initiated by a human
				user who has logged into GLaDOS to interact with the AI.
			
			(3) All high-importance system actions, which the AI might
				need to be aware of.  The threshold importance level can
				be configured in the system/AI configuration."""

	channelName = "AICC (AI Cognosphere Channel)"

	def willReport(thisChannel, status:str, action:Action_):
		
			# At present, we report all status updates for actions, including
			# 'conceived', 'initiated', 'executing', and 'completed'.  However,
			# the individual subscriber can choose to ignore most of these.
			
		#if status != 'completed': return False
		
			# Next, see if this is an action by the AI itself.  An easy way
			# to check this is to see if this action is an ActionByAI_. 
			# (Instance of this class, or a subclass derived from it.)  A 
			# more sophisticated way would be to actually look at the entity
			# specified in the ._conceivedBy and/or ._initiatedBy members.
			# However, we'll just use the simple method for now.
			
		isAIAction = isinstance(action, ActionByAI_)
		if isAIAction: 	return True
		
		# FUTURE: Check for actions by human users here (not implemented yet
		# because we haven't implemented the login system).
		
			# Next, check to see if this is a system-initiated action.
			
		isSystemAction = isinstance(action, ActionBySystem_)
		if not isSystemAction:	return False
		
			# Get its importance, and our threshold level.
		
		importance = action._importance
		threshold = TheAIPersonaConfig().sysNotifyThresh
		
		return importance >= threshold
		
	
