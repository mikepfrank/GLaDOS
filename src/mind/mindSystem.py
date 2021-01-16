#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 	TOP OF FILE:	 mind/mindSystem.py
#|------------------------------------------------------------------------------
#|	The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|	End of module documentation string.
#|------------------------------------------------------------------------------


# Stuff to put in the 'mind' package (in this file mindSystem.py, for now)
#
# Classes to be defined here (or that, at least, are used here):
#
#
#		Action_ (imported from supervisor.action module) -
#
#			Encapsulates an action taken by the AI, or a human user.
#			The difference between an action and an event is that an
#			action is an 'active' entity; it can and generally will 
#			be processed by TheActionProcessor_, possibly causing 
#			GLaDOS commands to be executed, which can have impacts on
#			other GLaDOS subsystems, and in the real world as well.  
#			In contrast, an Event is just a static record of a past
#			action.  Events can also be records of actions taken by
#			the system itself (such as a system shutdown).
#
#
#		The_AI_Cognosphere_Channel -
#
#			This is an ActionChannel_ that broadcasts all of the 'actions'
#			that are supposed to be perceptible within the AI's "Cognosphere"
#			or cognitive sphere, i.e., its overall field of awareness.  Right 
#			now, this includes:
#
#				* Actions that are generated by the AI itself (i.e., its 
#					speech acts, including command lines).
#
#				* Actions generated by the rest of the system that are 
#					above a certain threshold level of 'importance.'
#
#			At present, the Cognosphere channel reports on actions whenever 
#			they are conceived, initiated, executing or completed.
#
#
#		AI_ActionSubscriber -
#
#			This subclass of supervisor.action.ActionSubscriber_ takes
#			care of subscribing to notifications from the system about
#			various actions that are of interest to us.  Presently, the
#			subscriber just watches everything that's broadcast on the 
#			"AI Cognosphere Channel" and pays attention to the following
#			types of updates:
#
#				* Initiation of an AI action. (Note these are just
#					our own actions, but we get notified about them.)
#
#				* Execution of a sufficiently high-importance action
#					by the system itself.
#			
#		
#
#
#		
#
#		CognitiveStream - 
#
#			The "cognitive stream" is a singleton object that manages the 
#			indefinite-length, ever-growing sequence of "cognitive events," 
#			such as thoughts and perceptions, associated with the AI's ongoing 
#			processing.  Events themselves are defined in the 'events' package,
#			but in general they can include:
#
#				* Blocks of text generated by the AI, or by a human user.
#
#				* Snapshots of windows that the AI was looking at.
#
#			Generally speaking, as cognitive events occur, they are appended
#			to the cognitive stream.  Data in the cognitive stream is maintained
#			in two places:  The history buffer (in memory) and a backing store
#			in the filesystem (maintained by the 'memory' package).
#
#			One thing that the A.I. can be enabled to do is to scroll around in 
#			its cognitive stream, so that, instead of always looking at the most
#			recent material, it can scoll back and see what happened earlier.
#			Also, searching back in the cognitive stream is another option.
#
#
#		TheCognitiveProcess -
#
#			A subclass of SubProcess (i.e., a GLaDOS process) in which the
#			process implementing the AI's cognitive framework runs.
#
#
#		TheCognitiveSystem	- 
#
#			Singleton for the entire cognitive system, itself.  This includes
#			features like:
#
#				- A GLaDOS process in which the cognitive system runs.
#					This runs the main loop for cognitive processing.
#					This does the following things:
#
#						1. Wait for an external signal, or internal
#							timeout.
#
#						2. Refresh the receptive field.  (Repaint it,
#							update display for human, send it to the
#							AI's API.)
#
#						3. Receive action back from the AI's API.
#
#						4. Send it to the ActionProcessor.
#
#				- Makes use of the receptive field ('field' package).
#					This is effectively the AI's "computer screen" that
#					it is always looking at.  The mind system takes 
#					images of the receptive field at certain points in
#					time, and passes them to the underlying AI's API 
#					for processing.  The AI's predicted continuation is
#					then taken as its next 'action' and is passed to
#					the ActionProcessor for processing.
#					

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	os	import path

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# A simple decorator for singleton classes.
from	infrastructure.decorators	import	singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from 	infrastructure.logmaster 	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))				# Our package name.
_logger = getComponentLogger(_component)						# Create the component logger.

			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from 	config.configuration 	import	TheAIPersonaConfig
	# This class specifies the configuration of the AI's persona.

from	supervisor.action		import	(
		Action_, CommandAction_, ActionChannel_, AnnouncementAction_, ActionSubscriber_
	)
	# Abstract base classes for general actions, command-type actions, and action channels.

from	entities.entity			import	AI_Persona	# We need to construct this entity.

from	.mindSettings			import	TheMindSettings, TheMindSettingsModule
	# TheMindSettings - This uninstantiated class object holds our settings in class variables.
	# TheMindSettingsModule - A settings module for plugging into the settings facility.

from	.aiActions				import	(

		The_AI_Cognosphere_Channel,
			# We tell this dude to init itself, and we list it as our input channel.

		AnnounceFieldExistsAction,
			# We need this so that we can generate this action in
			# the .startup() method of The_Cognitive_System.
	
	)

from	.mindStream				import	TheCognitiveStream

from	field.receptiveField	import	TheReceptiveField
	# This singleton class gives us a handle into the receptive field module.

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| Dummy declarations of classes from modules we don't actually bother to load.
#| These are used only in type hints.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class TextEvent: pass
class ConsoleClient: pass

# Forward declarations.

class	TheCognitiveSystem: 			pass


class TheAIPersona: pass

@singleton
class TheAIPersona:

	"""This singleton class manages the AI's persona."""

	def __init__(theNewAIPersona:TheAIPersona, name:str, ID:str):

		persona = theNewAIPersona

			# Remember it's name and ID.
		persona._name = name
		persona._id = ID
		
			# Create and store an Entity object for it.
		persona._entity = AI_Persona(name=name, eid=ID)
		
	@property
	def entity(persona):
		return persona._entity


@singleton
class The_CognoSys_Subscriber(ActionSubscriber_):

	"""An 'action news' subscriber representing the interests of the
		cognitive system.  Its job is to decide which of the action
		news reports being broadcast into the AI's cognitive sphere
		are worthy of being permanently recorded as events that will
		be seen and remembered within the AI's cognitive stream."""

	def __init__(newSubscriber, mind:TheCognitiveSystem, name="CognoSys"):

		sub = newSubscriber

			# Remember how to find the whole cognitive system.
		sub._cognoSys = mind

			# First, do default initialization for all action subscribers.
		super(The_CognoSys_Subscriber.__wrapped__, sub).__init__(name=name)

			# Now we do initialization specific to us.

		TAICC = The_AI_Cognosphere_Channel()
			# This channel will be our main news source.
			# It informs us of announcements and other priority system events,
			# speech actions taken by ourselves (the AI) or by humans, and
			# system commands that are executed.

		sub.subscribe(TAICC)
			# So, go ahead and subscribe to it.

	def notify(thisSubscriber, status, action):

		_logger.debug("[Mind] Cognitive system is notified of status "
					  f"'{status}' for action '{action}'.")

		tcSub = thisSubscriber		# The cognitive system subscriber.
		tcSys = tcSub._cognoSys		# The cognitive system.
		tcStr = tcSys._cogStream	# The cognitive stream.
		
			# If this is an action that's actually executing,
			# let's bring it to the awareness of the cognitive stream.

		if status=='executed':
			tcStr.noticeAction(action)


@singleton
class TheCognitiveSystem:
	#---------------------------------------------------------------------------
	"""
	TheCognitiveSystem							 [mobule public singleton class]
	==================
	
		This singleton class implements the central cognitive framework for 
		AIs hosted by GLaDOS.  The cognitive system incorporates the 
		following singleton entities as sub-objects:
		
			TheReceptiveField -
			
				This is effectively the main 'screen' or 'display' that 
				constitutes the GLaDOS system's input interface to the AI.  
				Various processes within GLaDOS modify what appears on the 
				display, and the AI sees it and responds.
			
			TheCognitiveStream - 
			
				This is effectively the ever-growing, time-ordered record 
				of cognitive events (perceptions, thoughts, actions) that 
				are introduced into the AI's cognitive sphere.  Typically 
				the cognitive stream appears as a scrolling display that 
				dominates the AI's receptive field.  Internally, the 
				cognitive stream is implemented by a combination of the 
				'history' (recent history buffer) and 'memory' (long-term 
				backing store) packages working in concert.
			
			TheCognitiveProcess -
			
				A subclass of SubProcess, this is the GLaDOS process within
				which the main processing loop of the AI actually runs.
	"""
	def __init__(theCognitiveSystem:TheCognitiveSystem, console:ConsoleClient=None):
		#-----------------------------------------------------------------------
		"""
		theCognitiveSystem.__init__()		 [special singleton instance method]
		
			This is the singleton instance initializer for the cognitive 
			system class, TheCognitiveSystem.  It creates the singletons
			of our various subobjects, namely, our receptive field, our
			cognitive stream, and our main cognitive process.
		"""
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		mind = theCognitiveSystem
	
		_logger.normal("        [Mind/Init] The AI's cognitive system (Mind) is initializing...")
	
		mind._console = None		# The system console is not attached at first.
	
		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Step 0:  Fetch key configuration parameters from our config data.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			# First, configure all of the default settings for the mind system.
		settings = TheMindSettings.config()
		
			# Now, fetch the particular parameters that we need to know now.
		personaName = TheMindSettings.personaName
		personaID	= TheMindSettings.personaID
		
		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Step 0.5:  Create an object to manage the AI's persona, and an 
		#|	associated "entity" object to represent the persona.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		mind._persona = persona = TheAIPersona(personaName, personaID)
		mind._entity = entity = persona.entity
	
		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Step 1:  Create (the input interface to) our AI's receptive field.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
			# Next, we create the receptive field (which actually just means, 
			# the GLaDOS system's input interface to the core AI's real receptive 
			# field).
		
		_logger.info(f"            [Mind/Init] Creating receptive field...")
		field = TheReceptiveField(entity)		# This figures out its own size.
		mind._field = field				# Stash the field for later reference.
		
			# Now is probably a good time to attach ourselves to the console, so 
			# that the operator can immediately see the field we just created.
			
		_logger.info("            [Mind/Init] Attaching to console...")
		if console is not None:
			mind.setConsole(console)
			
		
		#|--------------------------------------
		#| Step 2:  Create our cognitive stream.
		
		_logger.info("            [Mind/Init] Initializing cognitive stream...")
		cogStream = TheCognitiveStream(mind)
		mind._cogStream = cogStream
		
		#|---------------------------------------
		#| Step 3:  Subscribe to notifications.
		
		_logger.info("            [Mind/Init] Subscribing to notifications for actions in our cognitive sphere...")
		mind._subscriber = The_CognoSys_Subscriber(mind)
			# This automatically subscribes itself to the AI Cognosphere Channel.
		
		#|---------------------------------------
		#| Step 4:  Create our cognitive process.
		
		## Not implemented yet.
	
	#__/ End singleton instance initializer theCognitiveSystem.__init__().

	def noticeEvent(mind, textEvent:TextEvent):
		
		"""When a new event gets appended to our cognitive stream, this method
			is called so that we notice the event at a higher level.  We respond
			by notifying our receptive field to add this event to its display."""

		#_logger.info(f"[Mind] Noticing text event: '{textEvent.text}'")

		field = mind._field
		field.addEvent(textEvent)

	@property
	def console(mind):
		return mind._console

	@property
	def field(theCognitiveSystem:TheCognitiveSystem):
		mind = theCognitiveSystem
		return mind._field


	def setConsole(mind:TheCognitiveSystem, console:ConsoleClient):
	
		"""This method is used to tell the mind where the system console
			is.  We need this so that we can automatically update the 
			receptive field display on the console whenever the contents 
			of the field are changed."""
			
		# If we already know it, we don't have to do anything.
		if console is mind.console:
			return

		mind._console = console		# Remember where the console is.
		
			# Also, tell the field where it is.
		mind.field.setConsole(console)
		
			#|------------------------------------------------------------------
			#| The console itself also needs to be given a pointer back into the 
			#| AI's mind because, in particular, it needs to be able to examine 
			#| the AI's receptive field on demand, so as to display its current
			#| state in the field display on the console.  We could have the 
			#| console just find the field directly from TheReceptiveField(), 
			#| but it's perhaps a little cleaner to do things this way.
			
		_logger.debug("                    [Mind] Giving console access to cognitive system...")
		console.setMind(mind)
		

	@property
	def inputChannels(theCognitiveSystem:TheCognitiveSystem):
		"""
			Returns a list of input channels that we would like to have filled 
			with information generated by the system.  Presently, this consists
			of a single action channel, to which the action subsystem should 
			deliver all actions created/initiated/executed/completed thoughout
			GLaDOS. At present, this channel filters this data to a limited 
			subset of interesting actions which are broadcast within the AI's 
			cognitive sphere, resulted in them being added to the AI's cognitive
			stream, and thereafter becoming able to be viewed in its receptive
			field.
		"""
		return [The_AI_Cognosphere_Channel()]


	def startup(theCognitiveSystem:TheCognitiveSystem):
		
		"""Starts up the cognitive system (which will create a background
			thread to run its main loop)."""
		
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Before we go into our main loop, we'll take care of some necessary
		#| startup tasks.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
			#--------------------------------------------------------------
			# First, here we conceive and initiate the action of announcing 
			# to the rest of the system that the receptive field is now up 
			# and running and is ready for other parts of the system to use 
			# it. This is one of our first major tests of the action system.
			# (Specifically, of using it from outside the Supervisor.)

		announcement = AnnounceFieldExistsAction()
		announcement.initiate()

		# TO DO: Write more code here, including starting up other
		# active subsystems of the cognitive system, and then creating
		# and starting up the thread that will run our main loop.

#__/ End singleton class TheCognitiveSystem.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					   END OF FILE:	  mind/mindSystem.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
