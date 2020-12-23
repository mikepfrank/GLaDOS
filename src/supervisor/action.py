#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 supervisor/action.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		supervisor/action.py			 [Python module source file]
	
	MODULE NAME:	supervisor.action
	IN PACKAGE:		supervisor
	FULL PATH:		$GIT_ROOT/GLaDOS/src/supervisor/action.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.supervisor (Principal supervisory subsystem)


	MODULE DESCRIPTION:
	-------------------
	
		The "action" module provides the primary interface by which various
		subsystems of GLaDOS, in particular the AI's cognitive system,
		communicate to GLaDOS's primary supervisory subsystem, and thence,
		to the rest of GLaDOS's subsystems, and thence, to the outside world.
		
		The purpose of providing this (somewhat) centralized communications 
		hub (whose role could be considered roughly analogous to that of the 
		thalamus in the brain) is twofold:
		
			(1) It provides a mechanism via which actions that are supposed
				to be in the scope of the AI's awareness, in its cognitive 
				sphere, will automatically be added to its cognitive stream, 
				rendering them subsequently perceptible by the AI.
				
			(2) More generally, it provides a centralized mechanism by which 
				the system's response to any given action can be easily 
				customized.
		
		Please note that, although this particular module is referenced and 
		utilized throughout GLaDOS, it conceptually is a part of the principal
		supervisory subsystem.
		
		The primary class in this module is 'Action_' which is an abstract 
		base class for all action objects that will be created in the system.
		In general, an action represents in important, intentional act that 
		is initiated by some 'actor' (agent) within the system.  This could be
		the A.I. itself, or a human user who is logged in to the system, or it
		could be some GLaDOS application, process, or subsystem.  The objects 
		representing the actors should be subclassed from the Entity_ class 
		within the entities package.
		
		There could be up to (at least) four different important times 
		associated with each action, which are recorded automatically:
		
			(1) The time at which the action was conceived (that is,
				when the action object was first created & initialized).
			
			(2) The time at which the action was initiated (this means,
				when the action object was dispatched to the supervisory
				system for execution).
			
			(3) The time at which the action was executed, which means,
				when the supervisor began carrying out the steps required
				to complete the action.  (This could be later than the 
				initiation time if the action specified a start time in
				the future.)
			
			(4) The time at which the action was completed (this means,
				when the supervisor finished carrying out the steps 
				required to complete the action.  This is generally when
				the action becomes a recorded cognitive event.
		
		Besides Action_ and its subclasses, other important classes defined in 
		this module include the following:

			ActionChannel - An "action channel" is basically a specific feed 
				of information about some set of actions being executed within
				the system.  Individual entities in the system can subscribe
				to the channel in order to get notified about actions being
				reported on that channel.  Some action types create their own
				action channels to report all actions of that type.  The
				channel decides which action news it wants to report.
				
			TheActionNewsNetwork - This dude keeps track of all the action 
				channels that are in existence, and manages broadcasting of 
				all the action news on each channel that wants to report it.
		
			ActionProcessor - This is the main class that manages action 
				execution. An action is initiated when it is passed to the
				action processor for processing.  The action processor takes
				care of work that needs to be done to every action, and then
				dispatches to different places to handle other work that is 
				specific to the action subtype.

			ActionSystem - Singleton class that serves as a single point of
				reference into the entire action processing facility.
			
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


	#|==========================================================================
	#|
	#|	 1. Module imports.								   [module code section]
	#|
	#|			Load and import names of (and/or names from) various
	#|			other python modules and pacakges for use from within
	#|			the present module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from datetime			import	datetime
	# We use datetime objects to keep a record of times associated with an action.

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.


			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from config.configuration	import  TheAIPersonaConfig
	# Import the AI persona's configuration.

from entities.entity	import	Entity_, The_Supervisor_Entity
	# This is the abstract base class for all entity objects.

	# A couple of forward declarations.
class TheActionProcessor: 		pass
class TheActionNewsNetwork:		pass

class Action_:
	#---------------------------------------------------------------------------
	"""
		action.Action_								[public abstract base class]
		
			This is the abstract base class of the action class hierarchy.
			
			This class provides definitions for the following public methods.
			All subclasses of Action_ should implement these methods, either 
			directly or by inheritance from a superclass:
			
				.initiate() -
				
					Initiates the process of executing the action, either
					now or in the future.
					
				.execute() -
				
					Actually start executing the action.
		
	"""
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#/--------------------------------------------------------------------------
	#|	Private instance data members.			   [class documentation section]
	#|
	#|		._description [str]	- 
	#|
	#|			String to describe this action after it's been taken.  
	#|			(Complete sentence; using the past tense is preferred.)
	#|
	#|		._conceivedBy [Entity_]	- 
	#|
	#|			Instance of a subclass of Entity_; identifies the specific
	#|			entity that conceived of taking this action.
	#|
	#|		._conceivedAt [datetime] -
	#|
	#|			The time at which this action instance was created.
	#|
	#|		._initiatedBy [Entity_] -
	#|
	#|			Instance of a subclass of Entity_; identifies the specific
	#|			entity that initiated the process of taking this action.
	#|
	#|		._initiatedAt [datetime] -
	#|
	#|			The time at which the process of taking this action was
	#|			initiated.
	#|
	#|		._executedBy [Entity_] -
	#|
	#|			The entity handling the execution of this action.
	#|
	#|		._executedAt [datetime] -
	#|
	#|			The time at which the execution of this action commenced.
	#|
	#|		._completedAt [datetime] -
	#|
	#|			The time at which the execution of this action was completed.
	#|
	#\--------------------------------------------------------------------------

	def __init__(thisAction, 
			description:str="A generic action was taken.",
				# REQUIRED. A description string. SUBCLASSES SHOULD OVERRIDE THIS VALUE.
			conceiver:Entity_=None,		# The entity that conceived of taking this action.
		):
		#-----------------------------------------------------------------------
		"""
			action.__init__()	 [abstract class instance initialization method]
			
				This is the default initialization method for instances of
				subclasses of Action_, if not overridden.
				
				When an action is first 'conceived' (created), its conception
				time is recorded.  We also record its textual description, and
				the entity that conceived it.
				
				Later on, the action can be initiated (by calling its 
				.initiate() method), and then we record its initiation time 
				and (optionally) the entity that initiated it (if different 
				from the entity that created it).  At this point, it will get
				passed to the ActionProcessor for processing and subsequent 
				execution by the system.
		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		thisAction._conceivedAt = datetime.now()	# Use current time as conception time.
		thisAction._description	= description
		thisAction._conceivedBy	= actor
		
			# Report this action's conception on TheActionNewsNetwork.
		thisAction.__reportConception()
		
	#__/

	def initiate(thisAction,
			initiator:Entity_ = None	# OPTIONAL. Assume same as conceiver if not given.
			executeAt:datetime = None	# OPTIONAL. If not provided or None, execute now.
		):
		#-----------------------------------------------------------------------
		"""
			action.initiate()
			
				Tells the action to initiate its processing and subsequent 
				execution by the supervisor.  
				
			Arguments:
			----------
			
				initiator [Entity_]	- Optional argument.
				
					The entity initiating this action.  If not specified, 
					it is assumed to be the same entity that conceived the
					action.
		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		thisAction._initiatedAt	= datetime.now()	# Use current time as initiation time.

			# If initiator not provided, assume it's the same as the conceiver.
		if initiator is None:	initiator = thisAction._conceivedBy
		
		thisAction._initiatedBy = initiator		# Remember our initiator.
		
			# If execution time is not provided, set it to initiation time, meaning ASAP.
		if executeAt is None:	executeAt = thisAction._initiatedAt
		
		thisAction._executeAt = executeAt		# Remember when to execute this action.
		
			# Now, finally process the action.
		
		TheActionProcessor().process(self)		
			# This handles reporting of initiation, possible execution scheduling work, 
			# and all other general processing work that may be needed.
			
	def execute(thisAction, 
			executor:Entity_ = The_Supervisor_Entity	# OPTIONAL, default to supervisor (us).
		):
		
		thisAction._executedAt = datetime.now()		# Use current time as execution time.
		
		thisAction._executedBy = executor	# Remember our executor.
		
			# Route to TheActionProcessor to handle the actual execution details.
		TheActionProcessor().execute(self)				

	#|--------------------------------------------------------------------------
	#|	Private instance methods.					  [class definition section]
	#|
	#|		The following private instance methods are defined for all 
	#|		actions.  These are not intended to be overridden in derived
	#|		classes (thus the double underscores).
	#|		
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __reportConception(thisAction):	
		TheActionNewsNetwork.reportConception(thisAction)
		
	def __reportInitiation():	
		TheActionNewsNetwork.reportInitiation(thisAction)
		
	def __reportExecuting():		
		TheActionNewsNetwork.reportExecuting(thisAction)
		
	def __reportCompletion():	
		TheActionNewsNetwork.reportCompletion(thisAction)
	

#__/ End module public abstract base class Action_.

#-------------------------------------------------------------
# Important abstract subclasses of Action_. Various subsystems
# can/should derive from these.

class CommandAction_(Action_):
	pass
	
class ActionByHuman_(Action_):
	pass
	
class ActionBySystem_(Action_):
	def __init__(thisSystemAction, 
			description:str="A generic system action was taken.",
				# REQUIRED. A description string. SUBCLASSES SHOULD OVERRIDE THIS VALUE.
			conceiver:Entity_=None,		# The entity that conceived of taking this action.
			importance:int=0,			# Importance level (integer). Default is 0.
		):
	
			# Remember the declared importance level of this system action.
		thisSystemAction._importance = importance
	
		super(ActionBySystem_, thisSystemAction).__init__(description, conceiver)

class ActionBySupervisor_(ActionBySystem_):
	def __init__(thisSupervisorAction,
			description:str="The supervisor took a generic system action.",
			importance:int=0,			# Importance level (integer). Default is 0.
		):
			
		actor = The_Supervisor_Entity
		
		super(ActionBySupervisor_, thisSupervisorAction).__init__(description, actor, importance)

class SupervisorAnnouncementAction(ActionBySupervisor_):
	def __init__(this,
			announcementText:str="Generic accouncement.",
			importance:int=0,			# Importance level (integer). Default is 0.
		):
		
			# Remember the announcement text for reference in case needed in later 
			# inspection of this action object.
		
		this._announcementText = announcementText
		
			# Construct the action description text.
		
		description = "Supervisor announces: " + announcementText
		
		super(SupervisorAnnouncementAction, this).__init__(description, importance)
		
class StartupAnnouncementAction(SupervisorAnnouncementAction):
	def __init__(this):
		announcement = "System is starting up."
		importance = 10		# A system startup event seems pretty important, right?
			#(We could make this configurable, though.)
		super(StartupAccouncement, this).__init__(announcement, importance)

class CommandByHuman_(ActionByHuman, CommandAction):
	pass

#==================================================
# Classes making up the Action notification system.

class ActionSubscriber_:

	def __init__(thisSubscriber):
		thisSubscriber.subscribedChannels = set()

	def subscribe(thisSubscriber, channel):
		
			# Ask the channel to add us to their list of subscribers.
		channel.addSubscriber(thisSubscriber)
		
			# Add the channel to our list of our subscribed channels.
		thisSubscriber.subscribedChannels.add(channel)
		
	# Override this method in subclasses with your own notification handler method.
	def notify(thisSubscriber, status, action):
		pass	# Default notification method does nothing.

class ActionChannel_:

	def __init__(thisChannel, name:str=None):
		thisChannel._name = name
		thisChannel._subscribers = set()
	
	def addSubscriber(thisChannel, subscriber:Subscriber):
		thisChannel._subscribers.add(subscriber)
	
	def maybeReport(thisChannel, status:str, action:Action_):
		if thisChannel.willReport(status, action):
			thisChannel.report(status, action)

	def willReport(thisChannel, status:str, action:Action_):
		return False	# Don't report anything by default.
		
	def report(thisChannel, status, action):
		for subscriber in thisChannel._subscribers:
			subscriber.notify(status, action)

@singleton
class TheEverythingChannel(ActionChannel_):

	"""This is an action channel that reports every single update
		that comes out on TheActionNewsNetwork."""
		
	def willReport(thisChannel, status, action):
		return True

@singleton
class TheLogReporter(ActionSubscriber_):

	"""This singleton subscribes to "The Everything Channel" and
		then reports every update to the Supervisor's logger."""
	
	def __init__(theLogReporter):
		theLogReporter.subscribe(TheEverythingChannel)
	
	def notify(theLogReporter, status:str, action):
		_logger.

@singleton
class TheActionNewsNetwork:
	_actionChannels = set()
	
	def __init__(theANN):
		pass
	
	def addChannels(theANN, channels:Iterable):
		for channel in channels:
			theANN.addChannel(channel)
	
	def addChannel(theANN, channel:ActionChannel_):
		theANN._actionChannels.add(channel)
		
	def report(theANN, status:str, action:Action_):
		for channel in theANN._actionChannels:
			channel.maybeReport(status, action)

	def reportConception(theANN, action:Action_):
		pass
		
	def reportInitiation(theANN, action:Action_):
		pass

	def reportExecuting(theANN, action:Action_):
		pass
		
	def reportCompletion(theANN, action:Action_):
		pass

# To add:
#
#		TheActionProcessor -
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

@singleton
class TheActionProcessor:

	def process(action:Action_):
		"""Process the initiation of the given action."""
		
			# First, report the news of this action's initiation to 
			# TheActionNewsNetwork.
		action.__reportInitiation()
		
		# At this point, we need to do other work, like giving the command 
		# interface a chance to interpret the action, scheduling possible
		# future execution of the action, and performing any pre-processing 
		# steps that are specific to the particular action subclass and details 
		# of the action.
		
			# This asks the command interface to check the given action to seek
			# whether it can implicitly be interpreted as a command.  If so, then 
			# automatically create a corresponding command action, and initiate it
			# as well.  The resulting command action will have the same conceiver 
			# and initiator as the action it was derived from.
		TheCommandInterface.checkForCommand(action)
		
		# WRITE MORE CODE HERE
		
		# For now, just execute all actions immediately.
		action.execute()
		
	#__/ End public instance method action.process().
		
	def execute(action:Action_):
		"""Handle the actual execution of the given action."""
		
			# First, report the news of this action's execution to 
			# TheActionNewsNetwork.
		action.__reportExecuting()
		
		#------------------------------------------------------------------------
		# At this point, we need to do other work, like performing any execution
		# steps that are specific to the particular action subclass and details 
		# of the action.
		
			# First off, if it's a system action, we just go ahead and run
			# its more specific execution method. (We don't need to second-guess 
			# what else needs to be done.)
		
		if isinstance(action, SystemAction_):
			action.executionDetails()
			
			# For speech actions taken by the AI, we need to run them through
			# the command interface.
		elif isinstance(action, AI_Speech_Action):
		
			ci = CommandInterface()		# Get the command interface.
			isCommand = ci.isCommand
			
		
			# Finally, report the news of this action's completion to
			# TheActionNewsNetwork.
		action.__reportCompletion()
		
@singleton
class TheActionSystem:

	def __init__(inst):
		TheActionNewsNetwork()	# Initialize the "Action News Network"
		TheActionProcessor()	# Initialize the action processor.

