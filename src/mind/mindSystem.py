#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 	TOP OF FILE:	 mind/mindSystem.py
#|------------------------------------------------------------------------------
#|	The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	mind.mindSystem - The GladOS Mind System		[Python module source file]
	========================================

		FILE PATH:		$(GLADOS_ROOT)/src/mind/mindSystem.py
		MODULE:			mind.mindSystem

		
	DESCRIPTION:
	============
	
		This is the main module for the cognitive system ('mind' package)
		for AI personas within the GladOS environment.  It defines the main
		classes and functions for the mind system, including the main
		classes for the AI's cognitive model, and the main classes for
		managing the AI's cognitive processes.  It also defines the main
		classes for the AI's cognitive channels, which are the means by
		which the AI can receive information from the rest of the system.
	
		
	PUBLIC INTERFACE:
	=================

		TheAIPersona										   [singleton class]
			
			The unique instance of this singleton class represents the AI 
			persona being hosted within the GladOS environment.  It keeps 
			track of important attributes of the AI persona such as
			configuration parameters retrieved from the AI's config file,
			and the AI_Persona object that identifies the AI persona within
			the GladOS environment.

			
		The_CognoSys_Subscriber								   [singleton class]

			The unique instance of this singleton class represents the AI's
			subscriber to the GladOS action notification system (defined in
			the supervisor.action package).  It is a subclass of the 
			ActionSubscriber_ class.  The AI's subscriber is responsible
			for receiving notifications of actions taken by the rest of the
			system, and for processing those notifications in order to update
			the AI's state appropriately

			
		The_GPT3_API										   [singleton class]

			The unique instance of this singleton class represents the AI's
			interface to the GPT-3 API.  It is really just a convenience 
			wrapper around the api module defined in the gpt3 package.
			It configures a connection to the core GPT engine that the AI
			is based on, using the AI's configuration parameters, and 
			provides a simple interface for sending requests to the engine.

			
	NOTE: The following classes have now been 
	moved out to the mind.mindStream module:
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			
		The_Cognitive_Stream								   [singleton class]

			The unique instance of this singleton class represents the AI's
			cognitive stream.  It is organized as an (ideally time-ordered)
			sequence of cognitive events, each of which is represented by a
			TextEvent object.  The cognitive stream is the primary means by
			which the AI can keep track of its own internal thoughts and
			actions, as well as the actions broadcast into the AI's
			cognitive sphere by the rest of the system.

			
	NOTE: The following classes have now been 
	moved out to the mind.aiActions module:
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		TheAICognosphereChannel							   [singleton class]

			The unique instance of this singleton class represents the AI's
			"CognoSphere" or cognitive sphere, i.e., its overall field of
			awareness.  This is the channel that the AI uses to receive
			information from the rest of the system.  It is a subclass of
			the ActionChannel_ class.

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|	End of module documentation string.
#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|
#|	Overview of the GladOS Cognitive System.
#|	========================================
#|
#|		The GladOS cognitive system is the part of the GladOS system that
#|		performs the AI's cognitive functions.  It is responsible for
#|		managing the AI's cognitive model, and for managing the AI's
#|		cognitive processes.  It is also responsible for managing the
#|		AI's cognitive channels, which are the means by which the AI can
#|		receive information from the rest of the system.
#|
#|		The GladOS cognitive system is implemented as a Python package
#|		(mind package) within the GladOS system.  It is defined by the
#|		following modules:
#|
#|			* mindSystem.py - This is the main module for the mind package.
#|				It defines the main classes and functions for the mind
#|				system.
#|
#|			* mindSettings.py - This module defines the main classes and
#|				functions for managing the AI's mind settings.  It 
#|				interfaces to the GladOS settings system for retrieval
#|				and modification of the AI's mind settings.
#|
#|			* aiActions.py - This module defines the main classes and
#|				functions for managing the AI's interface to the GladOS
#|				action notification system (defined in the action module
#|				in the supervisor package).
#|
#|			* mindStream.py - This module defines the main classes and
#|				functions for managing the AI's cognitive stream, which
#|				is the sequential stream of events registered by the AI
#|				as it processes information from the rest of the system.
#|				This includes events recording the AI's own actions and
#|				internal thoughts, as well as the actions broadcast into
#|				the AI's cognitive sphere by the rest of the system.
#|
#|			* subconscious.py - This module defines the main classes and
#|				functions for managing the AI's subconscious processes.
#|				These are the processes that the AI performs in the
#|				background, without the AI's conscious awareness.
#|				This module is not yet implemented.
#|
#|
#|	Classes defined in this main module, mind.mindSystem:
#|	=====================================================
#|
#|		TheAIPersona [singleton class] -
#|
#|			This singleton class represents the main AI persona currently 
#|			being hosted within the GladOS environment.  It keeps track of 
#|			important attributes of the AI persona such as configuration 
#|			parameters retrieved from the AI's config file, and the 
#|			AI_Persona entity that identifies the AI persona within the 
#|			GladOS environment.
#|
#|
#|		The_CognoSys_Subscriber [singleton class] -
#|
#|			This subclass of supervisor.action.ActionSubscriber_ takes
#|			care of subscribing to notifications from the system about
#|			various actions that are of interest to us.  Presently, the
#|			subscriber just watches everything that's broadcast on the 
#|			"AI Cognosphere Channel" and pays attention to the following
#|			types of updates:
#|
#|				* Initiation of an AI action. (Note these are just
#|					our own actions, but we get notified about them.)
#|
#|				* Execution of a sufficiently high-importance action
#|					by the system itself.
#|
#|			When it receives a notification, it updates the AI's state
#|			of mind accordingly.
#|
#|
#|		The_GPT3_API [singleton class] -
#|
#|			This singleton class represents the AI's interface to the
#|			GPT-3 API.  It is really just a convenience wrapper around
#|			the api module defined in the gpt3 package.  It configures
#|			a connection to the core GPT engine that the AI is based on,
#|			using the AI's configuration parameters, and provides a
#|			simple interface for sending requests to the engine.
#|
#|
#|		MindThread [thread class] -
#|
#|			This class represents the main thread for the cognitive
#|			system.  It is responsible for managing the main loop
#|			for the cognitive system, and for managing the cognitive
#|			channels that the AI uses to receive information from the
#|			rest of the system.
#|
#|
#|		TheCognitiveSystem [singleton class] - 
#|
#|			Singleton for the entire cognitive system, itself.  This includes
#|			features like:
#|
#|				- A GladOS thread or process in which the cognitive 
#|					system runs. This runs the main loop for cognitive 
#|					processing. This does the following things:
#|
#|						1. Wait for an external signal, or internal
#|							timeout.
#|
#|						2. Refresh the receptive field.  (Repaint it,
#|							update its display for the human system 
#|							operator, and also send it to the AI's 
#|							API for a response.)
#|
#|						3. Receive action back from the AI's API.
#|
#|						4. Send it to the ActionProcessor.
#|
#|				- Makes use of the receptive field ('field' package).
#|					This is effectively the AI's "computer screen" that
#|					it is always looking at.  The mind system takes 
#|					images of the receptive field at certain points in
#|					time, and passes them to the underlying AI's API 
#|					for processing.  The AI's predicted continuation of
#|					its prompt from the GladOS system is then taken as 
#|					its next 'action' and is passed to the 
#|					ActionProcessor for processing.
#|			
#|
#|	Other important classes referenced in this module include:
#|	==========================================================
#|
#|		Action_ (imported from supervisor.action module) -
#|
#|			Encapsulates an action taken by the AI, or a human user.
#|			The difference between an action and an event is that an
#|			action is an 'active' entity; it can and generally will 
#|			be processed by TheActionProcessor_, possibly causing 
#|			GLaDOS commands to be executed, which can have impacts on
#|			other GLaDOS subsystems, and in the real world as well.  
#|			In contrast, an Event is just a static record of a past
#|			action.  Events can also be records of actions taken by
#|			the system itself (such as a system shutdown).
#|
#|
#|	The following classes have now been moved to the mind.aiActions module:
#|	=======================================================================
#|
#|		The_AI_Cognosphere_Channel -
#|
#|			This is an ActionChannel_ that broadcasts all of the 'actions'
#|			that are supposed to be perceptible within the AI's "Cognosphere"
#|			or cognitive sphere, i.e., its overall field of awareness.  Right 
#|			now, this includes:
#|
#|				* Actions that are generated by the AI itself (i.e., its 
#|					speech acts, including command lines).
#|
#|				* Actions generated by the rest of the system that are 
#|					above a certain threshold level of 'importance.'
#|
#|				* Actions taken by the human operator at the console.
#|
#|			At present, the Cognosphere channel reports on actions whenever 
#|			they are conceived, initiated, executing or completed.
#|
#|
#|	The following classes have now been moved to the mind.mindStream module:
#|	=======================================================================
#|
#|		CognitiveStream - 
#|
#|			The "cognitive stream" is a singleton object that manages the 
#|			indefinite-length, ever-growing sequence of "cognitive events," 
#|			such as thoughts and perceptions, associated with the AI's ongoing 
#|			processing.  Events themselves are defined in the 'events' package,
#|			but in general they can include:
#|
#|				* Blocks of text generated by the AI, or by a human user.
#|
#|				* Snapshots of windows that the AI has looked at.
#|
#|			Generally speaking, as cognitive events occur, they are appended
#|			to the cognitive stream.  Data in the cognitive stream is maintained
#|			in two places:  The history buffer (in memory) and a backing store
#|			in the filesystem (maintained by the 'memory' package).
#|
#|			Recent events in the cognitive stream are also displayed on the
#|			AI's "receptive field," which represents its field of vision as
#|			it's looking at the GladOS display screen.  The receptive field
#|			is implemented in the 'field' package.
#|
#|			One thing that the A.I. can be enabled to do is to scroll around in 
#|			its cognitive stream, so that, instead of always looking at the most
#|			recent material, it can scoll back and see what happened earlier.
#|			Also, searching back in the cognitive stream is another option.
#|
#|
#|	The following classes are not yet implemented:
#|	==============================================
#|
#|		TheCognitiveProcess -
#|
#|			A subclass of SubProcess (i.e., a GLaDOS process) in which the
#|			system process implementing the AI's cognitive framework runs.
#|
#\==============================================================================


		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	threading	import	RLock
from	time		import	sleep, time
from	os			import	path

from	pprint		import	pformat #, pprint

import	json

		#|======================================================================
		#|	1.2. Imports of external python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	openai.error	import	RateLimitError

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

from 	infrastructure.logmaster 	import sysName, getComponentLogger, ThreadActor, LOG_DIR

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))				# Our package name.
_logger = getComponentLogger(_component)						# Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component



from	infrastructure.flag			import	Flag	# Waitable flag class.

			#|----------------------------------------------------------------
			#|	The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	gpt3.api				import	(

			#-------------------
			# Exception classes.

		PromptTooLargeException,	# Exception raised when a prompt is too long.

			#---------------
			# Other classes.

		# Classes no longer imported:
		#
		# GPT3APIConfig - This class specifies the configuration of the
		#	OpenAI GPT-3 API.  It is used to create a GPT3Core object.
		#	However, it is now deprecated.  Instead, use the
		#	createAPIConfig() function, imported below.
		#
		# GPT3Core - The core of the GPT-3 API. This is the class that
		#	actually makes the API calls to OpenAI. However, calling the
		#	class constructor directly is now deprecated. Instead, use
		#	the createCoreConnection() function, imported below.

			#-----------
			# Functions.

		createAPIConfig, createCoreConnection,
		isChatEngine, loadStatsIfNeeded, stats
	)

from 	config.configuration 	import	TheAIPersonaConfig
	# This class specifies the configuration of the AI's persona.

from	supervisor.action		import	(
		#Action_, CommandAction_, ActionChannel_, 
		AnnouncementAction_, ActionSubscriber_, OutputAction
	)
	# Abstract base classes for general actions, command-type actions, and action channels.

from	entities.entity			import	AI_Persona	# We need to construct this entity.

from	.mindSettings			import	TheMindSettings #, TheMindSettingsModule
	# TheMindSettings - This uninstantiated class object holds our settings in class variables.
	# TheMindSettingsModule - A settings module for plugging into the settings facility.

from	.aiActions				import	(

		The_AI_Cognosphere_Channel,
			# We tell this dude to init itself, and we list it as our input channel.

		AnnounceFieldExistsAction,
			# We need this so that we can generate this action in
			# the .startup() method of The_Cognitive_System.
	
		AI_Speech_Action,
			# These are the actions that the core AI directly conceives and initiates.

		AnnounceEnergyAction, FallAsleepAction, WakeUpAction,
			# Actions having to do with our sleep cycle.

	)

from	.mindStream				import	TheCognitiveStream

from	field.receptiveField	import	TheReceptiveField
	# This singleton class gives us a handle into the receptive field module.

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| Dummy declarations of classes from modules we don't actually bother to load.
#| These are used only in type hints.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class TextEvent:		pass
	# This is a dummy declaration of the TextEvent class from the
	# events.event module.  We don't actually bother to load the module,
	# but we do want to still mention the class in type hints.  A TextEvent
	# represents an event taking place within GladOS that contains an 
	# associated string of text.

class ConsoleClient:	pass

# Forward declarations.

class	TheCognitiveSystem: 			pass


class TheAIPersona: pass

@singleton
class TheAIPersona:

	"""This singleton class manages the AI's persona."""

	def __init__(theNewAIPersona:TheAIPersona, name:str=None, ID:str=None,
	      			username:str=None, modelFamily:str=None, modelVers:str=None):

		persona = theNewAIPersona

			# Remember it's name and ID, etc..
		persona._name = name
		persona._id = ID
		persona._username = username
		persona._modelFamily = modelFamily	# The model family. (E.g., "GPT-3")
		persona._modelVers = modelVers		# The model version. (E.g., "ada")
		
			# Create and store an Entity object for it.
		persona._entity = AI_Persona(name=name, eid=ID, chatName=ID)
			# We were thinking of storing the below in the entity, but it isn't
			# really needed. Just store them here in the persona object instead.
			#username=username, # Not yet used
			#modelFamily=modelFamily,
			#modelVers=modelVers)

	@property
	def name(persona):
		return persona._name
	
	@property
	def id(persona):
		return persona._id
	
	@property
	def username(persona):
		return persona._username
	
	@property
	def modelFamily(persona):
		return persona._modelFamily
	
	@property
	def modelVers(persona):
		return persona._modelVers

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

	def __init__(newSubscriber, mind:TheCognitiveSystem, name="MindSys"):

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


class The_GPT3_API: pass

@singleton
class The_GPT3_API:

	"""This class is a convenience wrapper for the specific functionality
		that we require out of the gpt3.api module.  It provides methods
		for initializing the API based on the AI persona's configuration,
		and..."""

	def __init__(newAPI:The_GPT3_API):

		api = newAPI

			# Configures the GPT-3 API from the AI persona's config file.
		api.configure()

			# Creates a new "core connection" using that configuration.
		api._core = createCoreConnection(conf=api.conf)

			# Loads API usage statistics from the filesystem if needed.
		loadStatsIfNeeded()

			# Retrieves the API statistics as a human-readable table.
		api._stats = stats()


	@property
	def isChat(thisAPI:The_GPT3_API) -> bool:

		"""This property returns True if the current core API configuration
			is for a chat model, and False otherwise."""

		return thisAPI.core.isChat


	def genResponse(thisAPI:The_GPT3_API, prompt:str=None, messages=None):

		"""This method uses the current core API configuration to
			generate a response string in response to the given prompt
			string or (for chat models) messages."""

		try:

			# If we're given a list of messages, we'll use them (assuming
			# here that we're using a chat model) to generate a response.
			if messages is not None:
				response = thisAPI.core.genString(messages)

			# Otherwise, we'll use the prompt string to generate a response.
			else:

				# If the prompt had a space at the end, trim it off,
				# because it prevents GPT-3 from generating tokens
				# that normally would include a leading space.
				trimmedSpace = False
				if prompt != None and len(prompt) >= 1 and prompt[-1] == ' ':
					trimmedSpace = True
					prompt = prompt[:-1]
				
					# Generate the response using the lower-level API wrapper.
				response = thisAPI.core.genString(prompt)

				# If we had trimmed a space at the start of the prompt,
				# but then the response string started with a space, we remove
				# it because in reality it's reflected in the prompt already.
				if trimmedSpace and len(response) >= 1 and response[0] == ' ':
					response = response[1:]

		except RateLimitError as e:
			_logger.error(f"[GPT3 API] Out of quota or rate limit exceeded! (msg=[{str(e)}])")
			return ""	# Empty string = no response.

			# Update our record of the API usage statistics, if the call succeeded
		thisAPI._stats = stats()

			# Return the response string.
		return response


	@property
	def stats(thisAPI:The_GPT3_API):
		"""Gets a human-readable table of API usage statistics,
			as a single multi-line string."""
		return thisAPI._stats


	@property
	def core(thisAPI:The_GPT3_API):

		"""Gets the GPT3Core object representing our current 'connection'
			to the core GPT-3 servers."""

		return thisAPI._core


	def configure(thisAPI:The_GPT3_API):

		"""This method configures the API based on the AI persona config."""

			# This just loads the AI persona configuration from its file (e.g.,
			# perhaps /opt/AIs/gladys/ai-config.hjson), if not already loaded.
		aiConfig = TheAIPersonaConfig()
		
			# Here we set up a keyword argument dict for assembling arguments
			# to the GPT3APIConfig() constructor, which will keep track of the
			# current API configuration for us (in case we need to change it).

		kwargs = dict()
		
		if aiConfig.modelVersion is not None:
			kwargs['engineId'] = engID = aiConfig.modelVersion

		if aiConfig.maxReturnedTokens is not None:
			kwargs['maxTokens'] = aiConfig.maxReturnedTokens

		if aiConfig.temperature is not None:
			kwargs['temperature'] = aiConfig.temperature
		
		if aiConfig.topP is not None:
			kwargs['topP'] = aiConfig.topP

		if aiConfig.nCompletions is not None:
			kwargs['nCompletions'] = aiConfig.nCompletions
		
		if aiConfig.doStream is not None:
			kwargs['stream'] = aiConfig.doStream

		if aiConfig.stopSequences is not None:
			kwargs['stop'] = aiConfig.stopSequences

		if aiConfig.presencePenalty is not None:
			kwargs['presPen'] = aiConfig.presencePenalty

		if aiConfig.frequencyPenalty is not None:
			kwargs['freqPen'] = aiConfig.frequencyPenalty

		if isChatEngine(engID):

			# The following are parameters for the new GPT chat API.

			if aiConfig.messages is not None:
				kwargs['messages'] = aiConfig.messages

			if aiConfig.logitBias is not None:
				kwargs['logitBias'] = aiConfig.logitBias

			if aiConfig.userID is not None:
				kwargs['user'] = aiConfig.userID

		else:	# Not a chat engine.

			# These three are NOT present in the GPT chat API, only in the text API.

			if aiConfig.logProbs is not None:
				kwargs['logProbs'] = aiConfig.logProbs

			if aiConfig.doEcho is not None:
				kwargs['echo'] = aiConfig.doEcho

			if aiConfig.bestOf is not None:
				kwargs['bestOf'] = aiConfig.bestOf

		# This is not a standard API parameter, but we'll use it to
		# store the name of the AI persona, so that we can reference 
		# it as needed.

		if aiConfig.personaName is not None:
			kwargs['name'] = f"GPT-3 API Configuration for '{aiConfig.personaName}' Persona"

			# Create an API config instance from those kwargs we just assembled.
		gpt3apiConf = createAPIConfig(**kwargs)
				# This factory function makes sure the correct subclass of
				# GPT3APIConfig gets instantiated, based on the engineId.

			# Store that conf for later reference.
		thisAPI._conf = gpt3apiConf


	@property
	def conf(thisAPI:The_GPT3_API):
		"""Gets the GPT3APIConfig object representing the
			current configuration of the GPT-3 API."""
		return thisAPI._conf


# $50/mo. / $0.06/1ktok = 833 ktok
# 833 ktok / 2,048 = 407 fields / mo. = 58 fields/wk. = 8.3 fields/day


class MindThread: pass
class MindThread(ThreadActor):

	"""This thread is responsible for executing the main loop of
		the AI's mind.  The mind can be in any of several different
		major states of consciousness:

				awake - In this state, the AI wakes up at least once every
						some number of minutes and does an action.

				asleep - In this state, the AI is going to sleep for some
						longer interval, and will not act until that
						time is up unless it is woken up.

				hibernating - In this state, the AI basically sleeps
		   			indefinitely until something wakes it up.

		Some of our important properties include:

			minActionInterval - This is a time in minutes which means,
				when we are awake, but no outside entities are trying
				to evoke an immediate response from us, what's the
				minimum time that we have to wait between actions that
				we take?  The reason this isn't zero is to limit the
				"burn rate," in terms of costs run up by making calls
				to the GPT-3 API.

			nominalSleepPeriod - This is a time in hours which means,
				when we go into sleep mode, what's the normal length
				of time that we remain in sleep mode until we wake up
				spontaneously?
	"""

	# NOTE: THIS IS TEMPORARY FOR TESTING WITH ADA/BABBAGE ONLY!
	#_DEFAULT_MIN_ACTION_INTERVAL = 1
	
	_DEFAULT_POLLING_INTERVAL = 1	# One second between checks.

	_DEFAULT_MIN_ACTION_INTERVAL = 60	# 60 minutes = 1 hours
		# To limit costs, by default we only do 1 davinci query
		# per hour, which is about $4 worth over a 16-hour day.
		# (Assuming each one is a full 2,048-token query & reply.)

	_DEFAULT_SLEEP_PERIOD = 8	# 8 hour nominal sleep period
		# This is also a cost-limiting measure, and helps to make
		# sure that the AI doesn't get too bored at night while
		# the human operator can't respond.

	defaultRole = 'Mind'
	defaultComponent = _sw_component

	def __init__(newMindThread:MindThread, mindSystem:TheCognitiveSystem):

		_logger.debug("[Mind/Thread] Initializing mind thread...")

		thread = newMindThread

		thread._lock = RLock()

			# Set these varaibles to their default values.
		thread._actionInterval = actInt = thread._DEFAULT_MIN_ACTION_INTERVAL
		thread._sleepPeriod = sleepHrs = thread._DEFAULT_SLEEP_PERIOD

		_logger.info(f"[Mind/Thread] Action interval = Once every {actInt} minutes.")
		_logger.info(f"[Mind/Thread] Sleep period = {sleepHrs} hours.")

			# Remember our pointer to the whole cognitive system.
		thread._mind = mind = mindSystem

		# First, we know that we're going to need to access the GPT-3 API,
		# so go ahead and create an object encapsulating it for us.

		thread._gpt3 = api = The_GPT3_API()		# Gets this singleton's instance.

			# Set our initial mode to 'awake', and our energy level to 100%.
		thread._mode = 'awake'
		thread._energy = 100
		thread._fullEnergy = True		# Goes True when energy is at 100% (16 hours till sleep)
		thread._lowEnergy = False		# Goes True when energy is under 10% (96 minutes till sleep)
		thread._veryLowEnergy = False	# Goes True when energy is under 5% (48 minutes till sleep)

			# These are time values that keep track of awake/asleep/hibernating intervals.
		thread._awakeSince = time()			# We just woke up, initially.
		thread._fellAsleepTime = 0
		thread._startedHibernatingAt = 0

			# These will be changed on startup in .captureInitialResponse().
		thread._lastResponse = None
		thread._lastActionTime = 0

			# This is just a simple flag for politely requesting shutdown.
		thread.exitRequested = False

		thread._attentionFlag = Flag()	# False initially, to give human a chance to provide input.
			# Raise this flag to cause the AI to respond immediately (that is,
			# within a second or so) even if its normal minimum action interval
			# has not yet expired.  However, if the AI is sleeping or
			# hibernating, it might not respond to this flag.

		thread._wakeUpFlag = Flag()
			# Raise this flag to wake up the AI if it's sleeping.  If it's
			# hibernating, it might not respond to this flag.

		thread._pokeBearFlag = Flag()
			# Raising this flag "pokes the bear," that is, it wakes up
			# the AI even if it's currently in hibernation mode.

		thread.defaultTarget = thread._main
		super(MindThread, thread).__init__()
			# Note we don't put this thread in daemon mode. It's too important!
			# (We don't want the server to stop while it's still running.)

	def quell(thisMindThread:MindThread):

		"""Forcibly lowers all of the cognitive thread's attention flags,
			so as to remove its impulse to respond immediately."""

		thread = thisMindThread

			# Tell all of these flags to lower themselves.
		thread._attentionFlag.fall()
		thread._wakeUpFlag.fall()
		thread._pokeBearFlag.fall()

	# def captureInitialResponse(thisMindThread:MindThread):
	# 	"""After the main cognitive system generates our initial "response",
	# 		it calls this method so that the cognitive thread will be aware
	# 		of its content & time."""

	# 	thread._lastResponse = mind.initialResponse
	# 	thread._lastActionTime = mind.initResponseTime
	# 		# Thiis is the time at which mind.generateFirstAction() generated our example response.
	# 		# We set this so that we don't think our refractory period is expired right away when
	# 		# we start up.


	def softPoke(thisMindThread:MindThread):

		"""A "soft poke" (F1) is just enough to get the AI's attention
			and make it respond before its action interval has expired.
			But, it's not enough to wake it up if sleeping/hibernating."""

			# Just raise its attention flag.
		thisMindThread._attentionFlag.rise()


	def poke(thisMindThread:MindThread):

		"""A "normal poke" will wake up the mind thread if it's sleeping,
			but not if it's hibernating."""

		thread = thisMindThread

			# The effects of a normal poke include the effects of
			# a soft poke.
		thread.softPoke()

			# We also raise the "wake up" flag.
		thread._wakeUpFlag.rise()


	def hardPoke(thisMindThread:MindThread):

		"""A "hard poke" will wake up the mind thread even if it's hibernating."""

		thread = thisMindThread

			# The effects of a hard poke include the effects of
			# a normal poke.
		thread.poke()

			# We also raise our "poke the bear" flag.
		thread._pokeBearFlag.rise()


	@property
	def gptAPI(thisMindThread:MindThread):
		return thisMindThread._gpt3			# The_GPT3_API object.

	@property
	def mind(thisMindThread:MindThread):
		return thisMindThread._mind			# TheCognitiveSystem object.

	@property
	def mode(thisMindThread:MindThread):
		"""Get's the mind thread's mode: awake, asleep, or hibernating."""
		return thisMindThread._mode


	def _main(thisMindThread:MindThread):

		"""Main routine of mind thread. Just periodically checks
			whether it needs to do something."""

		_logger.debug("[Mind/Thread] Entered main routine of mind thread...")

		thread = thisMindThread
		
		# How many seconds between status checks.
		pollingInterval = thread._DEFAULT_POLLING_INTERVAL
			# Since this is 1 second, the AI can respond to an external
			# event as quickly as within 1 second.

		while not thread.exitRequested:

			sleep(pollingInterval)

			# The first thing we do each polling interval (after the 1-second sleep)
			# is to update our energy level accordingly (depending on if we're awake
			# or asleep). This could lead to us spontaneously falling asleep or
			# waking up.
			thread.updateEnergy()

			# Next, we actually poll for external input, if needed.
			thread.pollForInput()
				# This method checks to see if there's an event we need to
				# respond to, or if our refractory or sleep period has expired.

	@property
	def persona(thisMindThread:MindThread):
		return thisMindThread.mind.persona

	@property
	def entity(thisMindThread:MindThread):
		return thisMindThread.persona.entity

	@property
	def personaName(thisMindThread:MindThread):
		return thisMindThread.entity.ID
		

	def updateEnergy(thisMindThread:MindThread):

		"""This updates the AI's "energy level;" the idea here is that
			the energy level gradually depletes while the AI is awake,
			and replenishes when it's sleep. When it gets low, the AI
			is alerted that it's getting sleepy, and when it hits 0 or
			less, the AI immediately falls asleep."""

		thread = thisMindThread
		mode = thread.mode

		# This is our polling interval in seconds.
		pollingInterval = thread._DEFAULT_POLLING_INTERVAL

		# If the AI is awale. then energy goes down.
		if mode == 'awake':

			# First, calculate size of our waking interval each day, in hours.
			wakingInterval = 24 - thread._DEFAULT_SLEEP_PERIOD
				# This will normally come out to 24-8 = 16 hours.

			# Now, calculate how much energy we lose every polling interval when awake.
			deltaE = 100 * pollingInterval / (wakingInterval * 60 * 60)

			# Decrement energy level. (Note it could go negative here).
			thread._energy = thread._energy - deltaE

			if thread._fullEnergy and thread._energy < 100:
				thread._fullEnergy = False

			# Check for certain critical energy levels.
			if thread._energy < 10:		# Check for low energy

				# Did we already produce a low-energy alert?
				if not thread._lowEnergy:

						# Get the AI persona's name.
					aiName = thread.personaName

						# Compose text of low-energy announcement action.
					annText = (f"{aiName}, our energy level is at 10%. We are getting sleepy. " +
						"Type /Sleep to enter sleep mode.")

						# Create and initiate announcement.
					annAct = AnnounceEnergyAction(annText)
					annAct.initiate()

						# Remember we did that already now.
					thread._lowEnergy = True

				# OK, if energy is less than 5%, do a more urgent announcement.
				if thread._energy < 5:
					
					if not thread._veryLowEnergy:
						
							# Get the AI persona's name.
						aiName = thread.personaName
	
							# Compose text of low-energy announcement action.
						annText = (f"{aiName}, our energy level is at 5%. We are getting very sleepy. " +
							"Please type /Sleep to enter sleep mode.")
	
							# Create and initiate announcement.
						annAct = AnnounceEnergyAction(annText, importance=5)
						annAct.initiate()
	
							# Remember we did that already now.
						thread._veryLowEnergy = True

					# Finally, if energy is less than 0, then fall asleep immediately.					
					thread.fallAsleep()
					return
			
		elif mode == 'asleep' or mode == 'hibernating':

			# Get our sleep period.
			sleepPeriod = thread._DEFAULT_SLEEP_PERIOD
		
			# Now, calculate how much energy we gain every polling interval when asleep.
			deltaE = 100 * pollingInterval / (sleepPeriod * 60 * 60)

			# If hibernating and energy is already max, don't need to do anything.
			if mode == 'hibernating' and thread._energy >= 100:
				return

			# Increment energy level. (Note it could go over 100 here.)
			thread._energy = thread._energy + deltaE

			if thread._veryLowEnergy and thread._energy > 5:
				thread._veryLowEnergy = False

			if thread._lowEnergy and thread._energy > 10:
				thread._lowEnergy = False

			# Check for energy at 100%; if so then wake up, unless hibernating.
			if thread._energy >= 100:

				if not thread._fullEnergy:
				
						# Get the AI persona's name.
					aiName = thread.personaName

						# Compose text of low-energy announcement action.
					annText = (f"{aiName}, our energy level is at 100%. Time to wake up. ")
					
					# Create and initiate announcement.
					annAct = AnnounceEnergyAction(annText)
					annAct.initiate()
	
					thread._fullEnergy = True

					thread.wakeUp()
					return

	def fallAsleep(thisMindThread:MindThread):

		"""Calling this method causes the AI to fall asleep. This is
			done as an explicit action so other subsystems are notified."""

		aiName = thisMindThread.personaName
		faAct = FallAsleepAction(thisMindThread)
		faAct.initiate()

	def executeFallAsleep(thisMindThread:MindThread):

		"""This executes the fall-asleep action."""

		thread = thisMindThread
		thread.mode = 'asleep'
		thread._fellAsleepTime = time()

	def wakeUp(thisMindThread:MindThread):

		"""Calling this method causes the AI to wake up spontaneously. This is
			done as an explicit action so other subsystems are notified."""

		aiName = thisMindThread.personaName
		waAct = WakeUpAction(thisMindThread)
		waAct.initiate()

	def executeWakeUp(thisMindThread:MindThread):

		"""This executes the wake-up action."""

		thread = thisMindThread

		if thread._mode in {'asleep', 'hibernating'}:

			_logger.info(f"[Mind/Thread] Waking up from '{thread._mode}' mode...")

			thread._mode = 'awake'
			thread._awakeSince = time()


	def pollForInput(thisMindThread:MindThread):
		
		"""This method checks whether it's time for the mind thread
			to do something; if so then we do it."""

		thread = thisMindThread

		# If this thread need to respond to some input, then do it.
		if thread.needsToRespond():
			thread.respondNow()

		mode = thread.mode


	def needsToRespond(thisMindThread:MindThread):

		"""Returns True if there's some event that the AI needs
			to respond to."""

		thread = thisMindThread
		mode = thread.mode
		curTime = time()

		# First, if the AI is awake, this is our normal operation mode.
		# We need to respond if our action interval has elapsed, or if
		# someone's trying to get our attention.
		
		if mode == 'awake':
			
			with thread._lock:
				if thread._attentionFlag():
					_logger.info(f"[Mind/Thread] I see someone raised my attention flag!")
					thread._attentionFlag.fall()	# Lower the flag.
					return True

			actInt = thread._actionInterval

				# Has enough time elapsed since the last action we took?
			timeToAct = ((curTime - thread._lastActionTime) > actInt*60)

			if timeToAct:
				_logger.info(f"[Mind/Thread] {actInt}-minute action interval has expired; time to act!")
			
				# If so, then we need to respond now.
			return timeToAct 
		
		# Second, if the AI is asleep, then we don't need to respond
		# unless our sleep period has elapsed or someone is trying to
		# wake us up.

		if mode == 'asleep':

			with thread._lock:
				if thread._wakeUpFlag():
					_logger.info(f"[Mind/Thread] I see someone raised my wakeup flag!")
					thread._wakeUpFlag.fall()	# Lower the flag.
					return True

			sleepHrs = thread._sleepPeriod

				# Has enough time elapsed since we fell asleep?
			timeToWakeUp = ((curTime - thread._fellAsleepTime) > sleepHrs*60*60)

			if timeToWakeUp:
				_logger.info(f"[Mind/Thread] I've been sleeping for {sleepHrs} hours; time to wake up!")
			
				# If it's time to wake up, then yeah, we need to.
			return timeToWakeUp

		# Thirdly, if the AI is hibernating, then we don't need to
		# respond unless someoke pokes us.

		if mode == 'hibernating':

			poked = thread._pokeBearFlag() 

			if poked:
				_logger.info("[Mind/Thread] Someone poked this hibernating bear! Better wake up!")

			return poked


	def respondNow(thisMindThread:MindThread):

		"""Tells the mind thread to wake up (if asleep or hiberating)
			and respond to whatever's in front of it."""

		thread = thisMindThread
		mode = thread.mode

		# If we were asleep or hibernating, then first do a wakeup
		# action; this will inform other subsystems of GLaDOS that
		# we are waking up now.
		if mode == 'asleep' or mode == 'hibernating':
			thread.wakeUp()

		# Call the normal respond method. It does the real work.
		thread.respond()
			

	def respond(thisMindThread:MindThread):

		"""This causes the AI to look at the receptive field,
			generate a response to it, and perform a 'speech
			action' with the content of that response.  What
			this does is context-dependent; e.g., if the AI is
			currently using an application that takes over the
			whole receptive field, the effect will be different
			than in a normal mode where the speech action is
			interpreted as a general one-line input.
		"""

		thread = thisMindThread		# Here's us, the mind thread.

		_logger.normal("[Mind/Thread] The AI's energy level is %0.3f%%" % thread._energy)

		mind = thread.mind			# The whole cognitive system.
		field = mind.field			# Our receptive field.
		view = field.view			# Our view of the field.
		
		gptAPI = thread.gptAPI		# Our Big Daddy AI in the cloud.

		text = view.text	# Gets one big text string with all the field data.

			# This asks GPT-3 to generate a response to the field text,
			# using the current API parameters.  If our API wrapper
			# complains that the prompt text is too large, then we
			# ask the receptive field to shrink itself, and retry.
		
		while True:

			try:

				# What we do here depends on whether we're using a text engine 
				# or a chat engine.

				if gptAPI.isChat:	# Chat engine.

					messages = view.messages()
						# Gets the contents of our view of the field,
						# represented as a list of messages.

					# Temporary hack for debugging -- truncate down to last 3 messages
					#messages = messages[-3:]

					prettyMsgs = pformat(messages)
					with open(f"{LOG_DIR}/latest-field.txt", "w") as f:
						# Write the GLaDOS field messages to the file.
						f.write(prettyMsgs)

					#_logger.debug("[Mind/Thread] Asking GPT chat API to respond to messages:\n" + prettyMsgs)

					# Steal the latest messages from the Telegram app. (FOR DEBUGGING!)
					#with open(f"{LOG_DIR}/latest-messages.json", "r") as infile:
					#	messages = json.load(infile)

					response = gptAPI.genResponse(messages=messages).lstrip().rstrip()
						# Added the lstrip()/rstrip() because extra spaces mess up command parsing.

				else:	# Text engine.

					_logger.debug("[Mind/Thread] Asking GPT text API to respond to prompt:\n" + text)

					response = gptAPI.genResponse(text).lstrip().rstrip()
						# Added the lstrip()/rstrip() because extra spaces mess up command parsing.


			except PromptTooLargeException as e:
					# Tell the receptive field it's too large and needs to shrink itself.

				_logger.debug("[Mind/Thread] Oops; the receptive field is too large "
							  f"by {e.byHowMuch}! Attempting shrink...")

				field.shrink(e.byHowMuch)

				text = field.view.text

				continue	# Try again.

			else:
				break

		# If we get here, then we got a response from our The_GPT3_API class.
		# However, if the response was an empty string, we interpret this as no 
		# response. This could just mean that there was a rate limit error.
		# In any case, we generate a warning and abort further processing.

		if response == "":	# Empty string.
			_logger.warn("[Mind/Thread] GPT API returned an empty response; ignoring.")
			return

		# If we get here, then we got a non-empty response. Note & process it.

		_logger.debug("[Mind/Thread] Got GPT-3 response: [" + response + ']')
		thread.noteResponse(response)	# Note time & response for later reference.

			# This causes us to process the response. Generally this
			# just conceives and initiates a corresponding speech action.
		thread.processResponse(response)


	def noteResponse(thisMindThread:MindThread, response:str):

		"""When this method is called, it takes note of this response of ours
			and the time that it was generated, then processes the response."""

		thread = thisMindThread		# Here's us, the mind thread.

			# Remember the time that that last GPT-3 API call completed.
		thread._lastActionTime = nowTime = time()

		_logger.debug(f"[Mind/Thread] Recording last action time as: {nowTime}")

		thread._lastResponse = response

	def processResponse(thisMindThread:MindThread, response:str):

		"""Given a raw output from the AI (as a string),
			this turns it into an appropriate speech action,
			"""

		thread = thisMindThread
		mind = thread.mind
		persona = mind.persona
		meEntity = persona.entity

		_logger.debug(f"[Mind/Thread] Processing our response: [{response}]")
			# Conceive and initiate the action of actually saying
			# what our underlying GPT-3 core is suggesting.
		speechAct = AI_Speech_Action(response, meEntity)
		speechAct.initiate()

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

		_logger.info(f"        [Mind/Init]     Configuring mind settings...")

			# First, configure all of the default settings for the mind system.
		settings = TheMindSettings.config()

			# Next, reset all of the mind settings to their default values.
			# (Note this is only appropriate because we haven't yet defined
			# a way to load saved settings from a file.  Once we do, we'll
			# call a different method here to load the settings from a file
			# or reset them to their defaults if no saved settings exist.)
		settings.resetToDefaults()
		
			# Now, fetch the particular parameters that we need to know now.
		personaName 	= settings.personaName
		personaID		= settings.personaID
		personaUsername	= settings.personaUsername
		modelFamily		= settings.modelFamily
		modelVersion	= settings.modelVersion
		
			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Step 0.5:  Create an object to manage the AI's persona, and an 
			#|	associated "entity" object to represent the persona.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		mind._persona = persona = TheAIPersona(name=personaName, ID=personaID,
					 		username=personaUsername, modelFamily=modelFamily,
					 		modelVers=modelVersion)

		mind._entity = persEntity = persona.entity
	
			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| Step 1:  Create (the input interface to) our AI's receptive field.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
			# Next, we create the receptive field (which actually just means, 
			# the GLaDOS system's input interface to the core AI's real receptive 
			# field).
		
		_logger.info(f"        [Mind/Init]     Creating receptive field...")
		field = TheReceptiveField(personaEntity=persEntity, modelVersion=modelVersion)
			# This figures out its own size and which tokenizer to use.
		mind._field = field				# Stash the field for later reference.
		
			# Now is probably a good time to attach ourselves to the console, so 
			# that the operator can immediately see the field we just created.
			
		_logger.info("        [Mind/Init]     Attaching to console...")
		if console is not None:
			mind.setConsole(console)
			
		
			#|--------------------------------------
			#| Step 2:  Create our cognitive stream.
		
		_logger.info("        [Mind/Init]     Initializing cognitive stream...")
		cogStream = TheCognitiveStream(mind)
		mind._cogStream = cogStream
		
			#|---------------------------------------
			#| Step 3:  Subscribe to notifications.
		
		_logger.info("        [Mind/Init]     Subscribing to notifi"
					 "cations for actions in our cognitive sphere...")
		mind._subscriber = The_CognoSys_Subscriber(mind)
			# This automatically subscribes itself to the AI Cognosphere Channel.
		
			#|---------------------------------------
			#| Step 4:  Create our cognitive process.
		
		# For now, this will just be a thread. Later on we will make
		# it into a bona-fide GLaDOS process.

		_logger.info("        [Mind/Init]     Creating main cognitive thread...")
		mind._thread = thread = MindThread(mind)
	
	#__/ End singleton instance initializer theCognitiveSystem.__init__().

	@property
	def thread(mind):
		return mind._thread

	@property
	def persona(mind):
		return mind._persona

	def noticeEvent(mind, textEvent:TextEvent):
		
		"""When a new event gets appended to our cognitive stream, this method
			is called so that we notice the event at a higher level.  We respond
			by notifying our receptive field to add this event to its display.
			We also wake up the mind, if appropriate, depending on the type of
			action that caused this event."""

		_logger.info(f"[Mind] Noticing text event: '{textEvent.text}'")

		field = mind._field
		field.addEvent(textEvent)

			# This gets the action that caused this event, if available. (It will
			# be available if the action just occurred, and if updates about it
			# were broadcast into our cognitive sphere by the action news network.)

		action = textEvent.action

			# If this was an action that we ourselves initiated, then take note of this,
			# because those actions are not of course surprising to us at all.

		isSelfAction = (action.initiator == mind.persona.entity)

			# If the action was an announcement, then poke the mind normally to wake it up.

		if isinstance(action, AnnouncementAction_):
			_logger.debug("[Mind] This is an announcedment; telling cognitive thread to wake up and notice.")
			mind.poke()

			# Otherwise, unless this was an action that we took ourselves, we give the
			# mind a "soft poke"; this will get its attention if it's already awake;
			# but otherwise, it will on keep sleeping/hibernating.
			
		elif not isSelfAction and not isinstance(action, OutputAction):
			_logger.debug("[Mind] The actor wasn't ourselves; getting our cognitive thread's attention.")
			mind.softPoke()

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
		
		mind = theCognitiveSystem

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

			#-----------------------------------------------------------------
			# Next, we generate a "canned" AI action just to try to get the
			# AI started on the right foot.

		mind.generateFirstAction()

		# TO DO: Write more code here, including starting up other
		# active subsystems of the cognitive system, and then creating
		# and starting up the thread that will run our main loop.

			#-----------------------------------------------------------
			# At this point, we are ready to start the main mind thread.

		thread = mind.thread
		thread.start()			# Go, go, speed racer!
		

	def generateFirstAction(mind:TheCognitiveSystem):

		"""This method is called on mind startup to generate a 'canned' initial
			response, just to try to get the AI started on the right track."""

		persona = mind.persona
		meEntity = persona.entity
		thread = mind.thread

		_logger.info("[Mind/Init] Auto-generating AI's initial example response...")

		# See if the AI config provided an example response.
		exampleResponse = TheAIPersonaConfig().exampleResponse

			# If so it, generate it as an AI speech action.
		if exampleResponse is not None:

				# Cause the mind thread (which is not yet started)
				# to note the time and content of the response.
			thread.noteResponse(exampleResponse)

				# Conceive and initiate the action of actually saying
				# the example response, attributed to the AI persona itself.
			thread.processResponse(exampleResponse)

				# Store our initial response for later reference.
			mind.initialResponse = exampleResponse
			mind.initResponseTime = time()
			
				# This ensures that the mind thread isn't impelled to respond to
				# stuff that was added to the field during startup; this is because
				# we want it to think that it has already responded to those.
			thread.quell()

		else:
			mind.initialResponse = None
			mind.initResponseTime = 0		# Jan 1, 1970

			# This just causes the cognitive thread to take note of this
			# response and its generation time.
		#thread.captureInitialResponse()

		# These methods are just dispatched to the "mind thread" sub-object.
	def softPoke(mind:TheCognitiveSystem):
		"""Get's the AI's attention if it's already awake."""
		mind.thread.softPoke()

	def poke(mind:TheCognitiveSystem):
		"""Wakes the AI up if it's sleeping."""
		mind.thread.poke()

	def hardPoke(mind:TheCognitiveSystem):
		"""Wakes the AI up even if it's hibernating."""
		mind.thread.hardPoke()

#__/ End singleton class TheCognitiveSystem.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					   END OF FILE:	  mind/mindSystem.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
