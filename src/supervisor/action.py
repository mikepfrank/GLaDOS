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

from	collections.abc		import	Iterable

	# We use datetime objects to keep a record of times associated with an action.
from 	datetime			import	datetime
from 	sys					import	stderr	# Used for displaying announcements.
from 	os					import	path	# For manipulating filesystem paths.


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

from events.event import tznow		# datetime.now() in user's time zone

from entities.entity	import	Entity_, The_GLaDOS_Entity, The_Supervisor_Entity
	# This is the abstract base class for all entity objects.

# Can't import this--circularity!!
#from commands.commandInterface	import	TheCommandInterface
	# We need to consult this when processing actions so that
	# we can check to see if they're interpretable as commands.



global	__all__
__all__ = [
		'Action_',		# Abstract base class for actions.
	]







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
		
		thisAction._conceivedAt = tznow()	# Use current time as conception time.
		thisAction._description	= description
		thisAction._conceivedBy	= conceiver
		
		_logger.debug(f"_Action.__init__(): Constructed action '{description}'.")

			# Report this action's conception on TheActionNewsNetwork.
		thisAction._reportConception()
		
	#__/

	@property
	def conceiver(thisAction):
		return thisAction._conceivedBy

	@property
	def conceptionTime(thisAction):
		return thisAction._conceivedAt

	@property
	def description(thisAction):
		return thisAction._description

	@property
	def text(thisAction):

		"""This attribute gives a textual representation of the action, in a
			form suitable for viewing by the AI.  May be overridden by subclasses."""

			# The simplest, and default, thing to do is just to provide the
			# action's description as its textual representation, followed by
			# a newline to indicate where the text ends.

		return thisAction.description + '\n'

	def __str__(thisAction):
		return thisAction.description

	def initiate(thisAction,
			initiator:Entity_ = None,	# OPTIONAL. Assume same as conceiver if not given.
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
		
		TheActionProcessor().process(thisAction)		
			# This handles reporting of initiation, possible execution scheduling work, 
			# and all other general processing work that may be needed.
			
	def execute(thisAction, 
			executor:Entity_ = The_Supervisor_Entity	# OPTIONAL, default to supervisor (us)
		):
		
		thisAction._executedAt = datetime.now()		# Use current time as execution time.
		
		thisAction._executedBy = executor	# Remember our executor.
		
			# Route to TheActionProcessor to handle the actual execution details.
		TheActionProcessor().execute(thisAction)				

	#|--------------------------------------------------------------------------
	#|	Private instance methods.					  [class definition section]
	#|
	#|		The following private instance methods are defined for all 
	#|		actions.  These are not intended to be overridden in derived
	#|		classes.
	#|		
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def _reportConception(thisAction):
		TheActionNewsNetwork().reportConception(thisAction)
		
	def _reportInitiation(thisAction):
		TheActionNewsNetwork().reportInitiation(thisAction)
		
	def _reportExecuting(thisAction):
		TheActionNewsNetwork().reportExecuting(thisAction)
		
	def _reportCompletion(thisAction):
		TheActionNewsNetwork().reportCompletion(thisAction)
	

#__/ End module public abstract base class Action_.

#-------------------------------------------------------------
# Important abstract subclasses of Action_. Various subsystems
# can/should derive from these.

class AnnouncementAction_: pass

class AnnouncementAction_(Action_):

	"""This is a type of action that, when executed, generates
		a message in several places (e.g., STDERR on each attached
		console or user terminal, in the A.I.'s cognitive stream)."""

	@property
	def text(thisAnnouncementAction:AnnouncementAction_):

		"""For announcement actions, we generate their text with a little
			highlighting (surroundings asterisks), and a newline."""

		annAct = thisAnnouncementAction
		text = f"~~~ {annAct.description} ~~~" + '\n'

		return text

	def executionDetails(thisAnnouncementAction:AnnouncementAction_):

		"""We don't need to do much here since an announcement is 
			self-executing, in virtue of having its execution
			reported to the cognosphere.  However, we also
			display the announcement text on attached (human)
			user terminals.  This includes the operator console
			and also any attached terminals of individual users."""

		annAct = thisAnnouncementAction

		_logger.debug(f"Carrying out execution details of announcement action '{annAct.description}'.")

			# Print the announcement to STDERR.
		print(annAct.text, file=stderr)	
			# This will actually go to the virterm and thence to the console panel.

		# Eventually we should also send it to all attached terminal sessions.

class CommandAction_(Action_):
	pass
	
class SpeechAction_(Action_):

	"""A speech action consists of some entity "saying something."
		The important thing about speech actions is that they can
		possibly sometimes be interpreted as commands to the system."""

	def __init__(this,
			speechText:str=None,	# Speech uttered by entity, as a text string.
			description:str=None,	# Description of the speech act.
			utterer:Entity_=None,	# The entity that is conceiving the speech act.
		):

			# Get a short string denoting the utterer.
		this._entityString = entStr = str(utterer)

			# Store the spoken/uttered text for later reference.
		this._speechText = speechText
		
			# Compose a description, pretty generic but acceptable.
		#description = f"{entStr} says: \"{speechText}\""
		description = speechText

			# Dispatch to Action_ base class to finish initialization.
		super(SpeechAction_, this).__init__(description, utterer)


	def setInvocationAction(this, commandAction:CommandAction_):

		"""Declares that when/if this speech act is committed (executed),
			the given command action shall also be invoked."""

			# Remember the command action to be invoked.
		this._invokesAction = commandAction
							

	def invokesAction(this):
		if hasattr(this, '_invokesAction'):
			return this._invokesAction
		else:
			return None


class ActionByHuman_(Action_):
	pass
	
class ActionBySystem_(Action_):

	defaultConceiver = The_GLaDOS_Entity()

	defaultImportance = 0
		# This sets the default importance level for system actions.
		# The default value of '0' is intended to represent a 'neutral'
		# importance level: Not particularly important, but not
		# particularly unimportant, either.  The default threshold for
		# the AI to be made aware of actions is also set at 0, so the
		# AI should be aware of these actions by default (but if it
		# turns up its threshold at all, they'll be suppressed).


	def __init__(thisSystemAction, 

			description:str="A generic system action was taken.",
				# REQUIRED. A description string. SUBCLASSES SHOULD OVERRIDE THIS VALUE.

			conceiver:Entity_=None,
				 # The system entity that conceived of taking this action. 
				 # If not provided, we'll default it to The_GLaDOS_Entity().

			importance:int=None,	# Importance level (integer).
				 # Default setting for this comes from 'defaultImportance' class variable.
		):
	
		sysAction = thisSystemAction

		if conceiver is None:
			conceiver = sysAction.defaultConceiver

		if importance is None:
			importance = sysAction.defaultImportance

			# Remember the declared importance level of this system action.
		thisSystemAction._importance = importance
	
		super(ActionBySystem_, thisSystemAction).__init__(description, conceiver)

class CommandByHuman_(ActionByHuman_, CommandAction_):
	pass

#==================================================
# Classes making up the Action notification system.

class ActionSubscriber_:

	def __init__(thisSubscriber, name="(generic subscriber)"):
		thisSubscriber.name = name
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

	channelName = "(generic action channel)"	# Override this.

	def __init__(thisChannel, name:str=None):

		if name is None:
			name = thisChannel.channelName

		_logger.info(f"        [ActionSystem/Init] Initializing action channel '{name}'.")

		thisChannel._name = name
		thisChannel._subscribers = set()
	
	def __str__(this):
		return this._name

	def addSubscriber(thisChannel, subscriber:ActionSubscriber_):
		
		_logger.debug(f"ActionChannel_.addSubscriber(): Subscribing {subscriber.name} to {thisChannel._name}.")

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
		
	channelName = "TEC (The Everything Channel)"

	def willReport(thisChannel, status, action):
		return True

@singleton
class TheLogReporter(ActionSubscriber_):

	"""This singleton subscribes to "The Everything Channel" and
		then reports every update to the Supervisor's logger."""
	
	def __init__(theLogReporter):

		_logger.info("        [ActionSystem/Init] Intializing the log reporter...")

		super(TheLogReporter.__wrapped__, theLogReporter).__init__(name="The Log Reporter")
		
		theLogReporter.subscribe(TheEverythingChannel())
	
	def notify(theLogReporter, status:str, action):
		_logger.debug(f"[ActionSystem] Log reporter: Action news update! Action [{action}] was {status}.")
			# Note: Need to make sure actions convert to strings OK. 

@singleton
class TheActionNewsNetwork:

	_actionChannels = set()
	
	#def __init__(theANN):
	# pass
	
	def addChannels(theANN, channels:Iterable):
		for channel in channels:
			theANN.addChannel(channel)
	
	def addChannel(theANN, channel:ActionChannel_):

		_logger.info(f"        [ActionSystem/Init] TANN (The Action News Network) is adding '{channel}' to its lineup.")
		
		theANN._actionChannels.add(channel)
		
	def report(theANN, status:str, action:Action_):
		for channel in theANN._actionChannels:
			channel.maybeReport(status, action)

	def reportConception(theANN, action:Action_):
		theANN.report('conceived', action)
		
	def reportInitiation(theANN, action:Action_):
		theANN.report('initiated', action)

	def reportExecuting(theANN, action:Action_):
		theANN.report('executed', action)
		
	def reportCompletion(theANN, action:Action_):
		theANN.report('completed', action)

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

	def process(theActionProcessor:TheActionProcessor, action:Action_):
		"""Process the initiation of the given action."""
		
		_logger.debug(f"actionProcessor.process(): Processing initiation of action '{action}'.")

			# First, report the news of this action's initiation to 
			# TheActionNewsNetwork.
		action._reportInitiation()
		
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
		commandIface = theActionProcessor._commandInterface
		commandIface.checkForCommand(action)
		
		# WRITE MORE CODE HERE
		
		# For now, just execute all actions immediately.
		action.execute()
		
	#__/ End public instance method action.process().
		
	def execute(theActionProcessor:TheActionProcessor, action:Action_):
		"""Handle the actual execution of the given action."""
		
		_logger.debug(f"actionProcessor.execute(): Processing execution of action '{action}'.")

			# First, report the news of this action's execution to 
			# TheActionNewsNetwork.
		action._reportExecuting()
		
		#------------------------------------------------------------------------
		# At this point, we need to do other work, like performing any execution
		# steps that are specific to the particular action subclass and details 
		# of the action.
		
			# First off, if it's a system action or any announcement action
			# (including announcements from the AI), we just go ahead and run
			# its more specific execution method. (We don't need to second-guess 
			# what else needs to be done.)
		
		if isinstance(action, ActionBySystem_) or isinstance(action, AnnouncementAction_):
			action.executionDetails()
			
			# For speech actions taken, we need to check whether committing
			# (executing) the speech act automatically invokes another action
			# (such as a command action).  If so, then execute that action too.
		elif isinstance(action, SpeechAction_):
		
				# Get the other action invoked by this speech act, if any.
			invocation = action.invokesAction()
			
				# If there is one, then execute that action as well.
			if invocation is not None:
				invocation.execute()

			# Finally, report the news of this action's completion to
			# TheActionNewsNetwork.
		action._reportCompletion()
		
	def commandInterfaceIs(inst, theCommandInterface):
		inst._commandInterface = theCommandInterface
		

@singleton
class TheActionSystem:

	def __init__(inst):
		
		_logger.info("        [ActionSystem/Init] Intializing the action system...")

		tann = TheActionNewsNetwork()	# Initialize the "Action News Network"
		tap = TheActionProcessor()		# Initialize the action processor.
		tec = TheEverythingChannel()	# Initialize the Everything Channel.
		tlr = TheLogReporter()			# Initialize the Log Reporter.

		tann.addChannel(tec)
			# Add The Everything Channel to TANN's lineup.

			# Remember these guys.
		inst._actionNewsNetwork = tann
		inst._actionProcessor = tap
		inst._everythingChannel = tec
		inst._logReporter = tlr

	def commandInterfaceIs(inst, theCommandInterface):

		"""After constructing all subsystems, call this method on the action
			system to inform it of how to find the command interface.  Note 
			that We can't just find it by importing the command interface
			module, because the command interface needs to import this modole,
			and so that would create an import circularity."""

			# Relly, it's our action processor that needs this info.
		inst._actionProcessor.commandInterfaceIs(theCommandInterface)
