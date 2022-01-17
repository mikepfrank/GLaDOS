#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 supervisor/action.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""FILE NAME:		supervisor/action.py			 [Python module source file]
	
	MODULE NAME:	supervisor.action
	IN PACKAGE:		supervisor
	FULL PATH:		$GIT_ROOT/GLaDOS/src/supervisor/action.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.supervisor (Principal supervisory subsystem)


	MODULE DESCRIPTION:
	-------------------
	
		The "action" module implements the "action subsystem," a
		subsystem of GLaDOS's principal supervisory system.  The
		action subsystem provides the primary interface by which
		various other subsystems of GLaDOS, and in particular, the
		AI's cognitive system, communicate back to GLaDOS's primary
		supervisory subsystem, and thence, to the rest of GLaDOS's
		subsystems, and thence, to the outside world.
		
		The purpose of providing this (somewhat) centralized
		communications hub (whose role could be considered roughly
		analogous to that of the thalamus in the brain--which was
		Gladys' idea) is threefold:
		
			(1) It provides a mechanism via which actions that are
				supposed to be emcompassed within the scope of the
				AI's awareness, i.e., that are present within its
				cognitive sphere, will automatically be added to its
				cognitive stream, rendering them subsequently
				perceptible by the AI.
				
			(2) More generally, it provides a centralized mechanism by
				which the system's response to any given action can be
				easily customized.
			
			(3) It also provides for automated logging of actions to
				the system log file.
		
		Please note that, although this particular module is
		referenced and utilized from throughout GLaDOS, it
		conceptually is a part of the principal supervisory subsystem,
		not a part of other systems (although other systems may of
		course define their own classes building upon the action
		facility).
		
		The primary class in this module is 'Action_', which is an
		abstract base class for all action objects that will be
		created in the system.  In general, an action represents a
		significant, intentional act that is initiated by some 'actor'
		(agent) within the system.  This could be the A.I. itself, or
		a human user who is logged in to the system, or it could be
		some automated GLaDOS application, process, or subsystem.  The
		objects representing the actors should be subclassed from the
		Entity_ class within the entities package.
		
		Note that there could be up to (at least) four different
		important times that are associated with each action, which
		are recorded automatically:
		
			(1) The time at which the action was 'conceived' (that is,
				when the action object was first created &
				initialized).
			
			(2) The time at which the action was 'initiated' (this
				means, when the action object was dispatched to the
				supervisory system for execution)--this is the point
				in time at which the decision to take the action was
				made & committed.
			
			(3) The time at which the action was 'executed,' which
				means, when the supervisor began carrying out the
				steps required to complete the action.  (This could be
				later than the initiation time if the action specified
				a start time in the future; eventually we may support
				a cron-like system for scheduling of such future
				actions.)
			
			(4) The time at which the action was completed (this
				means, when the supervisor finished carrying out the
				steps required to complete the action.  This is
				generally when the action becomes a recorded cognitive
				event, although it's also possible for the cognitive
				system to notice unfolding actions at their earlier
				stages as well.
		
		Besides Action_ and its subclasses, other important classes
		defined in this module include the following:

			ActionChannel - An "action channel" is basically a
				specific feed of information about a subset of actions
				being executed within the system.  Individual entities
				in the system can subscribe to the channel in order to
				get notified about actions being reported on that
				channel.  Action types could create their own action
				channels to report all actions of that type.  The
				channel decides which action news updates it wants to
				report.
				
			TheActionNewsNetwork - This dude keeps track of all of the
				action channels that are in existence, and manages
				broadcasting of all the action news on each channel
				that wants to report it.
		
			ActionProcessor - This is the main class that manages
				action execution. An action is initiated when it is
				passed to the action processor for processing.  The
				action processor takes care of general work that needs
				to be done for every action, and then dispatches to
				different places to handle other work that is specific
				to the particular action subtype.

			TheActionSystem - Singleton class that serves as a single
				point of reference into the entire action processing
				facility.

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


global	__all__
__all__ = [
		'Action_',		# Abstract base class for actions.

			#~~~~~~~~~~~~~~~~~~~
			# Action subclasses.

		'ActionBySystem_',		# Abstract base class for actions initiated by system components.
		#'ActionByAI_',			# Abstract base class for actions initiated by the AI.
		#   \_ This is instead defined in mind/aiActions.py.
		'ActionByHuman_',		# Abstract base class for actions initiated by individual humans.
		'ActionByOperator_',	# Abstract base class for actions initiated by the system operator.

		'AnnouncementAction_',	# Abstract base class for (system) announcement actions.
		'CommandAction_',		# Abstract base class for command actions.
		'SpeechAction_',		# Abstract base class for speech actions.
	
		'OutputAction',		# Abstract base class for output messages from the system.
		'ErrorAction',			# Abstract base class for error-reporting actions.

		'Operator_Speech_Action',	# Class for speech actions taken by system operator.

		#'CommandByAI_'			# Abstract base class for commands issued by the AI.
		#   \_ This is instead defined in mind/aiActions.py.
		'CommandByHuman_',		# Abstract base class for commands issued by a human.

			#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			# Action notification system classes.

		'ActionSubscriber_',	# Abstract base class for subscribers to action channels.
		'TheLogReporter',		# A subscriber that records action reports in the system log.

		'ActionChannel_',		# A broadcast feed for notifying subscribers of action reports.
		'TheEverythingChannel',	# A channel that broadcasts all action reports in the system.

		'TheActionNewsNetwork',	# Central hub that dispatches action reports to all channels.

			# Action processing system.

		'TheActionProcessor',	# Handles initiation and execution of all actions.

			# Singleton class to anchor this entire module.

		'TheActionSystem',	# Singleton class for action system as a whole.
			# (Anchor point for this module.)

	]


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
from 	sys					import	stdout, stderr	# Used for displaying output/announcements.
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

from infrastructure.logmaster 	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.


			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from config.configuration	import  TheAIPersonaConfig
	# Import the AI persona's configuration.

from events.event 	import tznow		# datetime.now() in user's time zone

# Entity objects reify different components within the system for
# purposes of recording which parts of the system originated different actions.
from entities.entity	import	(
		Entity_,			# This is the abstract base class for all entity objects.
		The_GLaDOS_Entity,		# Refers to the GLaDOS system as a whole.
		The_Supervisor_Entity,	# Refers to the supervisory subsystem of GLaDOS.
		Human_Entity_,			# A generic human entity (abstract class).
		Operator_Entity			# Entity for the system operator.
	)
	

# Can't actually import this--circularity!!
#from commands.commandInterface	import	TheCommandInterface
	# We need to consult this when processing actions so that
	# we can check to see if they're interpretable as commands.


	#|==========================================================================
	#|
	#|	 2. Class definitions.							   [module code section]
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dummy/forward class declarations. (For documentation purposes in type hints.)

	#|----------------------------------------------------
	#| Dummy declarations for some Command module classes.
	#| (Since we can't actually import the command iface.)

class Command: pass		# Class for command-type objects


	#|----------------------------------------------
	#| A few forward declarations to classes
	#| defined later in this module.

class TheActionProcessor: 		pass
class TheActionNewsNetwork:		pass

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|
#|	Below, the following classes are defined, in this order:
#|
#|	Action classes:
#|
#|		Action_					- Abstract base class for all actions.
#|		AnnouncementAction_
#|		CommandAction_
#|		SpeechAction_
#|		ActionByHuman_
#|		ActionByOperator_
#|		Operator_Speech_Action
#|		ActionBySystem_
#|		CommandByHuman_
#|
#|	Action notification facility classes:
#|
#|		ActionSubscriber_
#|		ActionChannel_
#|		TheEverythingChannel
#|		TheLogReporter
#|		TheActionNewsNetwork
#|
#|	Core action system classes:
#|
#|		TheActionProcessor
#|
#|		TheActionSystem - Anchor singleton for the entire action system.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Action_: pass
class Action_:
	#---------------------------------------------------------------------------
	"""action.Action_								[public abstract base class]
		
			This is the abstract base class of the action class
			hierarchy.
			
			This class provides definitions for the following public
			methods.  All subclasses of Action_ should implement these
			methods, either directly or by inheritance from a
			superclass:
			
				.initiate() -
				
					Initiates the process of executing the action,
					either now or in the future.
					
				.execute() -
				
					Actually start executing the action.

			NOTE: "Conceiving" an action means constructing the action
			object. "Finishing" an action means completing its
			execution.

	"""
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		#|======================================================================
		#| Class-level variables.							[class code section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


		# NOTE: Actions are not self-executing by default. Some subclasses
		# override this.
	selfExecuting = False
		#  \
		#   \__ To say that an action is self-executing means that it handles
		#		all details of its own execution, without any other processing
		#		needed by the action processor.


	defaultDescription = "A generic action was taken."
		#	\
		#	 \__ Subclasses can and should override this value.


	#/--------------------------------------------------------------------------
	#|	Private instance data members.			   [class documentation section]
	#|  ==============================
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
	#|			Often (but not always), this will be the same entity as
	#|			._conceivedBy.
	#|
	#|		._initiatedAt [datetime] -
	#|
	#|			The time at which the process of taking this action was
	#|			initiated. (E.g., scheduled for immediate, or possibly
	#|			later execution.)
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

	def __init__(
			thisAction:Action_, # This new action object, to be initialized.
			description:str=None,
				# REQUIRED. A description string. SUBCLASSES SHOULD OVERRIDE THIS VALUE.
			conceiver:Entity_=None,		# The entity that conceived of taking this action.
				# REQUIRED. The conceiving entity. SUBCLASSES SHOULD OVERRIDE THIS VALUE.
		):

		#-----------------------------------------------------------------------
		"""action.__init__()	 [abstract class instance initialization method]
			
				This is the default initialization method for
				instances of subclasses of Action_, if not overridden.
				
				When an action is first 'conceived' (created), its
				conception time is recorded.  We also record its
				textual description, and the entity that conceived it.
				
				Later on, the action can be initiated (by calling its
				.initiate() method), and then we record its initiation
				time and (optionally) the entity that initiated it (if
				different from the entity that created it).  At this
				point, it will get passed to the ActionProcessor for
				processing and subsequent execution by the system.
																			 """
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		
			#-------------------------------------------------------------------
			# If caller didn't provide a description, we have to construct one.
			# Use the conceiver, if we know it.
			
		if description is None:

			if conceiver is None:

				description = defaultDescription

			else:

				description = f"{conceiver} took a generic action."

		#__/__/


			#-------------------------------
			# Initialize various attributes.

		thisAction._description	= description

		thisAction._conceivedBy	= conceiver	# Who conceived of taking this action?
		thisAction._conceivedAt = tznow()	# Use current time as conception time.

		thisAction._initiatedBy = None			# Not yet initiated.
		thisAction._initiatedAt = None

		thisAction._executedBy  = None			# Not yet executed.
		thisAction._executedAt	= None
		
		_logger.debug(f"_Action.__init__(): Constructed action '{description}'.")


			# Report this action's conception on TheActionNewsNetwork.
		thisAction._reportConception()
		
	#__/


		#|======================================================================
		#| Public instance property definitions.			[class code section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@property
	def conceiver(thisAction):
		"""Returns the entity that first conceived of taking this action."""
		return thisAction._conceivedBy

	@property
	def conceptionTime(thisAction):
		"""Returns the time at which this action was first conceived (constructed)."""
		return thisAction._conceivedAt

	@property
	def initiator(thisAction):
		"""Returns the entity that actually initiated the execution of this action."""
		return thisAction._initiatedBy

	@property
	def executor(thisAction):
		"""Returns the entity that actually executed this action."""
		return thisAction._executedBy

	@property
	def description(thisAction):
		"""Returns the description string for this action."""
		return thisAction._description

	@property
	def text(thisAction):

		"""This attribute gives a textual representation of the action,
			in a form suitable for viewing by the AI. Note this may be
			overridden by subclasses."""

			# The simplest, and default, thing to do is just to provide the
			# action's description as its textual representation, followed by
			# a newline to indicate where the text ends.

		return thisAction.description + '\n'

	#__/ End property action.text.



		#|======================================================================
		#| Special instance method definitions.				[class code section]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	def __str__(thisAction):
		"""Return the standard string representation of this action."""
		return thisAction.description


		#|======================================================================
		#| Public instance method definitions.				[class code section]
		#|
		#|	This includes the following methods:
		#|
		#|		action.initiate()
		#|		action.execute()
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	def initiate(thisAction,
			initiator:Entity_ = None,	# OPTIONAL. Assume same as conceiver if not given.
			executeAt:datetime = None	# OPTIONAL. If not provided or None, execute now.
		):

		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		"""action.initiate() 							[public instance method]
			
				Tells this action to initiate its processing and
				subsequent execution by the supervisory system's
				action processor.

				
			Arguments:
			==========
			
				initiator [Entity_]	- Optional argument.
				
					The entity initiating this action.  If not
					specified, it is assumed to be the same entity
					that conceived the action.

		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#----------------------------
			# Record some important data.

		thisAction._initiatedAt	= datetime.now()	# Use current time as initiation time.

			# If initiator not provided, assume it's the same as the conceiver.
		if initiator is None:	initiator = thisAction._conceivedBy
		
		thisAction._initiatedBy = initiator		# Remember our initiator.
		
			# If execution time is not provided, set it to initiation time, meaning ASAP.
		if executeAt is None:	executeAt = thisAction._initiatedAt
		
		thisAction._executeAt = executeAt		# Remember when to execute this action.
		
			#---------------------------------------------------------------
			# Now, finally tell the action processor to process this action.
		
		TheActionProcessor().process(thisAction)		
			# This handles reporting of initiation, possible execution scheduling work, 
			# and all other general processing work that may be needed.

	#__/ End instance method action.initiate().

			
	def execute(thisAction, 
			executor:Entity_ = The_Supervisor_Entity
				# OPTIONAL, default to supervisor (i.e., us)
		):
		
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		"""action.execute() 							[public instance method]

				Tells this action to have the action processor
				execute it immediately.

		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		thisAction._executedAt = datetime.now()		# Use current time as execution time.
		
		thisAction._executedBy = executor	# Remember our executor.
		
			# Route to TheActionProcessor to handle the actual execution details.
		TheActionProcessor().execute(thisAction)				

	#__/ End instance method action.execute().


	#|==========================================================================
	#|	Private instance method definitions.		  [class definition section]
	#|
	#|		The following private instance methods are defined for all 
	#|		actions.  These are not intended to be overridden in derived
	#|		classes.
	#|		
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def _reportConception(thisAction):
		"""Report this action's conception on the action news network."""
		TheActionNewsNetwork().reportConception(thisAction)
		
	def _reportInitiation(thisAction):
		"""Report this action's initiation on the action news network."""
		TheActionNewsNetwork().reportInitiation(thisAction)
		
	def _reportExecuting(thisAction):
		"""Report this action's execution on the action news network."""
		TheActionNewsNetwork().reportExecuting(thisAction)
		
	def _reportCompletion(thisAction):
		"""Report this action's completion on the action news network."""
		TheActionNewsNetwork().reportCompletion(thisAction)
	

#__/ End module public abstract base class supervisor.action.Action_.


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| Next up, we have some important abstract subclasses of
	#| Action_. Various subsystems can/should derive from these.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class OutputAction: pass
class OutputAction(Action_):

	"""An output action represents the result of a command or app
		or process generating output on the GLaDOS console. Note
		this is different from an announcement, which also has
		special highlighting and filtering characteristics."""

	selfExecuting = True

	def __init__(
			thisOutputAction:OutputAction,
			outputText:str=None,
			description:str=None,
			conceiver:Entity_=None):

		action = thisOutputAction

		action._outputText = outputText

		if description is None:
			description = f"Produce output: [{outputText}]."

		super().__init__(description=description, conceiver=conceiver)
			
			# Output actions are self-initiating upon conception.
		action.initiate()


	@property
	def text(thisOutputAction:OutputAction):

		"""For an output action, the text that ends up appearing will
			just be the output text."""

		action = thisOutputAction

		return action._outputText + '\n'	# To visually separate lines.
	
	def executionDetails(thisOutputAction:OutputAction):
		action = thisOutputAction
		print(action.text, file=stdout)
			# This will actually go to the virterm and thence to the console panel.

def output(who:Entity_, text:str):

	OutputAction(
			outputText = text,
			conceiver = who
		)

LEVEL_DEBUG 	= 0
LEVEL_INFO  	= 1
LEVEL_WARNING  	= 2
LEVEL_ERROR 	= 3
LEVEL_CRITICAL	= 4
LEVEL_FATAL		= 5

_level_names = {
		LEVEL_DEBUG:	'DEBUG',
		LEVEL_INFO:		'INFO',
		LEVEL_WARNING:	'WARNING',
		LEVEL_ERROR:	'ERROR',
		LEVEL_CRITICAL:	'CRITICAL ERROR',
		LEVEL_FATAL:	'FATAL ERROR'
	}

class ErrorAction: pass
class ErrorAction(OutputAction):

	def __init__(
			thisErrorAction:ErrorAction,
			level:int=LEVEL_ERROR,
			msgText:str=None,
			conceiver:Entity_=None):

		action = thisErrorAction

		action._level = level
		action._levelName = levelName = _level_names[level]

		action._msgText = msgText

		text = f"{levelName}: {msgText}"

		super().__init__(text, conceiver=conceiver)

	def executionDetails(thisErrorAction:ErrorAction):
		action = thisErrorAction
		print(action.text, file=stderr)
			# This will actually go to the virterm and thence to the console panel.
		
		# Also log it to the overarching logging system.

		level = action._level

		if level == LEVEL_DEBUG:
			_logger.debug(action._msgText)

		elif level == LEVEL_INFO:
			_logger.info(action._msgText)

		elif level == LEVEL_WARNING:
			_logger.warn(action._msgText)

		elif level == LEVEL_ERROR:
			_logger.error(action._msgText)

		elif level == LEVEL_CRITICAL:
			_logger.critical(action._msgText)

		elif level == LEVEL_FATAL:
			_logger.fatal(action._msgText)


def info(who:Entity_, msg:str):

	ErrorAction(
		level = LEVEL_INFO,
		msgText = msg,
		conceiver = who
	)

def warn(who:Entity_, msg:str):

	ErrorAction(
		level = LEVEL_WARNING,
		msgText = msg,
		conceiver = who
	)

def error(who:Entity_, msg:str):
	ErrorAction(msgText = msg, conceiver = who)


class AnnouncementAction_: pass
class AnnouncementAction_(Action_):

	"""This is a type of action that, when executed, generates a message
		in several places (e.g., STDERR on each attached console or
		user terminal & in the A.I.'s cognitive stream)."""

	selfExecuting = True
		#	\
		#	 \__ This tells the action processor that we don't need
		#		 any help with our execution; we can do it ourselves.

	@property
	def text(thisAnnouncementAction:AnnouncementAction_):

		"""For announcement actions, we generate their text with a little
			highlighting (surrounding asterisks), and a newline."""

		annHighlightChar = '*'
		annHighlight = annHighlightChar * 3

		annAct = thisAnnouncementAction
		text = f"{annHighlight} {annAct.description} {annHighlight}\n"

		return text
	#__/


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

	#__/

#__/ End module public abstract class supervisor.action.AnnouncementAction.


class CommandAction_: pass
class CommandAction_(Action_):

	"""Abstract base class for command actions."""

	# Definitely want these to be self-executing.
	selfExecuting = True

	# This simple default initializer just accepts <cmdLine> and <cmdType>
	# arguments and stores them for later use.
	def __init__(
				cmdAction:CommandAction_,	# This new command action, to be initialized.
				cmdLine:str,				# Required argument: The raw (unparsed) command line.
				cmdType:Command,			# Required argument: The command type that matches it.
				description:str=None,		# Optional argument: Command description.
				conceiver:Entity_=None		# The entity that originally conceived this command action.
			):

		cmdAction._cmdLine = cmdLine
		cmdAction._cmdType = cmdType

			# We generate an appropriate description.

		if description is None:
			if conceiver is None:
				description = f"The command line [{cmdLine}] was invoked."
			else:
				description = f"{conceiver} invoked the command line [{cmdLine}]."

		# Remaining initialization is handled by Action_ class.
		super(CommandAction_, cmdAction).__init__(
			description=description, conceiver=conceiver)

	#__/

	@property
	def cmdLine(cmdAction:CommandAction_):
		return cmdAction._cmdLine

	@property
	def cmdType(cmdAction:CommandAction_):
		return cmdAction._cmdType

	def executionDetails(thisCommandAction:CommandAction_):
		"""Execute the given command action."""

		cmdAction = thisCommandAction
		cmdType = cmdAction.cmdType
		cmdLine = cmdAction.cmdLine

		_logger.debug(f"Executing the '{cmdType}' command with command line [{cmdLine}]...")

		cmdType.execute(cmdLine)	# This does the deed.

#__/ End module public abstract class CommandAction_
	
class SpeechAction_(Action_):

	"""A speech action consists of some entity "saying something."
		An important thing about speech actions is that they can
		possibly sometimes be interpreted as commands to the system,
		which will then be automatically interpreted by the command
		interface."""

	def __init__(this,
			utterance:str=None,	# Speech uttered by entity, as a text string.
			description:str=None,	# Overall description of the speech act.
			utterer:Entity_=None,	# The entity that is conceiving the speech act.
		):

			# Remember who the utterer was.
		this._utterer = utterer

			# Get a short string denoting the utterer.
		this._uttererStr = uttererStr = str(utterer)

			# Store the spoken/uttered text for later reference.
		this._utterance = utterance
		
			# Compose a description, pretty generic but acceptable.
		description = f'{uttererStr} said: "{utterance}"'
		#description = utterance

			# Dispatch to Action_ base class to finish initialization.
		super(SpeechAction_, this).__init__(description=description, conceiver=utterer)


	@property
	def utterance(thisSpeechAction):
		return thisSpeechAction._utterance

	# NOTE: It's important for speech actions to override the "text" property,
	# which is used to generate a textual description of the action that's suitable
	# for viewing by the AI.  We modify it to just give the utterance itself,
	# rather than the complete description of the speech action.  This is because
	# The prompt on the event will already give sufficient context as to the
	# utterer.  It would confuse the AI to also give it "So-and-so said..."
	@property
	def text(thisSpeechAction):
		return thisSpeechAction.utterance + '\n'


	def possibleCommandLine(this):
		
		"""If someone queries this action to ask us, hey, do you contain some
			text that potentially could be a command line?  Then we
			answer with the actual text of the utterance. (As opposed
			to the action description, which has additional info.)"""
		
		return this._utterance


	def setInvocationAction(this, commandAction:CommandAction_):

		"""Declares that when/if this speech act actually gets committed
			(executed), then the given command action shall also be
			invoked."""

			# Remember the command action to be invoked.
		this._invokesAction = commandAction
							

	def invokesAction(this):

		"""Returns the consequent action invoked by this utterance.
			Normally, this would be a command action."""

		if hasattr(this, '_invokesAction'):
			return this._invokesAction
		else:
			return None


class ActionByHuman_(Action_):

	defaultConceiver = None
		# NOTE: No default conceiver, because we don't yet know
		# which human conceived this action. Subclasses may override this.

	def __init__(thisHumanAction, 

			description:str="A generic action was taken by a human.",
				# REQUIRED. A description string. SUBCLASSES SHOULD OVERRIDE THIS VALUE.

			conceiver:Human_Entity_=None,
				 # The human entity that conceived of taking this action. 

		):
	
		humanAction = thisHumanAction

		if conceiver is None:
			conceiver = humanAction.defaultConceiver

		super(ActionByHuman_, thisHumanAction).__init__(description=description, conceiver=conceiver)

	
class ActionByOperator_(ActionByHuman_):

	defaultConceiver = Operator_Entity()
		# This is an entity to represent the (possibly anonymous) human
		# operator that is physically sitting at the system console.


class Operator_Speech_Action: pass
class Operator_Speech_Action(SpeechAction_, ActionByOperator_):

	"""Class for speech actions by the system operator, which means text
		that the operator entered and sent to GLaDOS using, e.g., the input
		panel within the system console client.

		These actions are usually automatically initiated by the conceiver
		right after being conceived (created)."""

	def __init__(newOpSpeechAct:Operator_Speech_Action, opTextOut:str):
		
		action = newOpSpeechAct

			# The operator entity is the default conceiver for
			# all ActionByOperator_ instances; retrieve it.
		opEntity = newOpSpeechAct.defaultConceiver

			# Get a short string name representing the operator.
		action._opStr = opStr = str(opEntity)

			# Store the operators's output text for later reference.
		action._opTextOut = opTextOut
		
		_logger.debug(f"[Action System] {opStr} is creating a speech action with text: [{opTextOut}].")

			# Compose an action description, pretty generic but that's fine for now. 
		description = f"{opStr} sent the text: [{opTextOut}]."
			# (Later on, if this speech action ends up getting parsed as a command string,
			# then this action may end up also invoking a command action of some sort.)

			# Dispatch to next class in inheritance chain to finish initialization.
		super(Operator_Speech_Action, action).__init__(opTextOut, description, opEntity)
			# Note dispatch order goes first to SpeechAction_, then to ActionByOperator_.


class ActionBySystem_(Action_):

	defaultDescription = "A generic system action was taken."

	defaultConceiver = The_GLaDOS_Entity()

	selfExecuting = True

	defaultImportance = 0
		# This sets the default importance level for system actions.
		# The default value of '0' is intended to represent a 'neutral'
		# importance level: Not particularly important, but not
		# particularly unimportant, either.  The default threshold for
		# the AI to be made aware of actions is also set at 0, so the
		# AI should be aware of these actions by default (but if it
		# turns up its threshold at all, they'll be suppressed).


	def __init__(thisSystemAction, 

			description:str=defaultDescription,
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


class CommandByHuman_(CommandAction_, ActionByHuman_):
	# Note the superclass resolution order here is important: CommandAction_
	# parses out the cmdLine and cmdType arguments, then we pass the rest of
	# the arguments on to ActionByHuman_ for further processing.
	
	"""Class for commands invoked by a generic human user."""

	pass

class OperatorCommand(CommandAction_, ActionByOperator_):
	# Note the superclass resolution order here is important: CommandAction_
	# parses out the cmdLine and cmdType arguments, then we pass the rest of
	# the arguments on to ActionByOperator_ for further processing.

	"""Class for commands invoked by the system operator."""

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

		"""Process the initiation of the given action. For speech actions,
			this should check to see if this action can be interpreted as
			invoking a command. If so, then the invocation action of the
			speech act should be set to the appropriate command action."""
		
		_logger.debug(f"actionProcessor.process(): Processing initiation of action '{action}'.")

			# First off, report the news of this action's initiation to 
			# the action news network.
		action._reportInitiation()
		
		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| At this point, we need to do other work, like giving the command 
		#| interface a chance to interpret the action, scheduling possible
		#| future execution of the action, and performing any pre-processing 
		#| steps that are specific to the particular action subclass and details 
		#| of the action.
		
			#-------------------------------------------------------------------
			# This asks the command interface to check the given action to see
			# whether it can implicitly be interpreted as a command.  If so,
			# then automatically create a corresponding command action, and
			# initiate it as well.  The resulting command action will have the
			# same conceiver and initiator as the action it was derived from.

		commandIface = theActionProcessor._commandInterface
		cmdAction = commandIface.checkForCommand(action)

			#-------------------------------------------------------------------
			# If we actually found an invocable command action, then go ahead
			# and set the invocation action of the speech act to it.

		if cmdAction is not None:
			action.setInvocationAction(cmdAction)
		
		# For now, just execute all actions immediately. (No future scheduling yet.)
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
		
			# First off, if it's a self-executing action such as a system action
			# or any announcement action (including announcements from the AI),
			# we just go ahead and run its more specific execution method. (We
			# don't need to second-guess what else needs to be done.)
		
		#if isinstance(action, ActionBySystem_) or isinstance(action, AnnouncementAction_):
		if action.selfExecuting:

			action.executionDetails()
			
			# For any speech actions taken, we need to check whether committing
			# (executing) the speech act automatically invokes another action
			# (such as a command action).  If so, then execute that action too.
		if isinstance(action, SpeechAction_):
		
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
