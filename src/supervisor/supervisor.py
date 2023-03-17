#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 supervisor/supervisor.py
#|------------------------------------------------------------------------------
#|
#|	FILE NAME:		supervisor/supervisor.py		 [Python module source file]
#|	
#|	MODULE NAME:	supervisor.supervisor
#|	IN PACKAGE:		supervisor
#|
#|	FULL PATH:		$GIT_ROOT/GLaDOS/src/supervisor/supervisor.py
#|	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
#|
#|	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
#|	APP NAME:		GLaDOS.server (Main GLaDOS server application)
#|	SW COMPONENT:	GLaDOS.supervisor (Principal supervisory subsystem)
#|
#|	CODE LAYER:		Layer #13 (the only module that imports appSystem).
#|
#|	IMPORTS THESE MODULES:
#|	======================
#|		Layer #12:	apps.appSystem
#|		Layer #9:	windows.windowSystem, mind.mindSystem
#|		Layer #8:	commands.commandInterface
#|		Layer #6:	supervisor.action
#|		Layer #2:	entities.entity, settings.settings
#|		Layer #1:	infrastructure.logmaster, process.processSystem
#|		Layer #0:	infrastructure.{decorators,flag}
#|
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	MODULE DESCRIPTION:
	===================
	
		This module is responsible for starting up the top-level
		'supervisor' subsystem of the GLaDOS system.  The supervisor
		is responsible for starting up and managing the other main
		subsystems of GLaDOS:
				
			(1) The GLaDOS command interface (`commands/`). This
				facility allows for pluggable command-and-control
				of the entire GLaDOS system by the artificially
				intelligent mind residing within it.
						
			(2) The windowing subsystem (`windows/`). This subsystem
				manages various text-based 'windows' that appear in the
				A.I.'s visual field that the A.I. can use to interact 
				with various processes.
		
			(3) The process subsystem (`processes/`). This subsystem
				manages a set of GLaDOS 'processes' that the AI can
				interact with to communicate to the outside world,
				to human users, to other local systems or to various
				subsystems of GLaDOS itself. Processes come with 
				associated command modules, and the AI interacts with
				each process through a dedicated text 'window.'

			(4)	The application subsystem (`apps/`).  This subsystem 
				manages the various "applications" running within 
				GLaDOS that can be used by the AI.  This includes the
				Help system, Info app, Settings app, Memory app, and
				the ToDo, Diary, Comms, Browse, Writing, and Unix
				tools.
						
			(5) The cognitive subsystem (`mind/`). This subsystem 
				maintains the A.I.'s mental state, described in terms
				of a long-term memory bank, a real-time event history, 
				a receptive field, and a dynamic API configuration.
				Windows appear in the receptive field and the A.I. uses
				them to interact with various processes & subsystems.
				The main event loop of the A.I. also happens here.
					   
		
		USAGE:
		~~~~~~
		
			from supervisor.starter import TheSupervisor
			...
			# Server configuration should have been loaded first, then call:
			supervisor = TheSupervisor()	# Create & start supervisor (and various threads).
			...
			supervisor.waitForExit()	# Waits for the TheSupervisor to exit.
		
		
		MODULE PUBLIC CLASSES:
		~~~~~~~~~~~~~~~~~~~~~~
				
			TheSupervisor						 [module public singleton class]
						
				Singleton class, whose sole instance is the single
				object which is the system supervisor subsystem.
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

from threading	import	RLock	# Re-entrant mutex locks.
from os			import	path	# Manipulate filesystem path strings.


		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	1.2.1. The following modules, although custom, are generic
			#|		utilities, not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| LAYER 0:	Modules that don't import any other custom modules.

	# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton

from infrastructure.flag 		import	Flag	# Waitable flags.

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| LAYER 1: Modules that only import modules from layer #0.

from infrastructure.logmaster import getComponentLogger, ThreadActor, sysName

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.

global _sw_component	# Full name of this software component.
_sw_component = sysName + '.' + _component


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	1.2.2. The following modules are specific to the present
			#|		application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| LAYER 1: Modules that only import modules from layer #0.

from 	processes.processSystem		import	TheProcessSystem
	# This class manages launching of all essential 'background' 
	# GLaDOS processes.

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| LAYER 2: Modules that don't import any modules from above Layer 1.

from	entities.entity				import	System_Entity_, The_Supervisor_Entity
	# This is a singleton entity denoting the supervisor subsystem itself.

from	settings.settings			import	TheSettingsFacility
	# This facility is for keeping track of all the available settings.

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| LAYER 6: Modules that don't import any modules from above Layer 5.

from .action import (
		TheActionSystem,
		ActionBySystem_,		# Abstract base class for subsystem actions we define.
		TheActionNewsNetwork,
		AnnouncementAction_		# Abstract base class for announcement actions specifically.
	)
	# The action system is one of our major subsystems. We need these names from it.

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| LAYER 8: Modules that don't import any modules from above Layer 7.

from 	commands.commandInterface	import	TheCommandInterface
	# This class manages initialization of the command interface.
	# (That is, the command interface used by the AI to control GLaDOS.)

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| LAYER 9: Modules that don't import any modules from above Layer 8.

from 	windows.windowSystem		import	TheWindowSystem
	# This class manages initialization of the text window system.

from 	mind.mindSystem				import	TheCognitiveSystem
	# This class manages starting up the A.I.'s mind on server startup.
	# NOTE: The receptive field gets created in here; as soon as it
	# exists, it generates an AnnounceFieldExists action, which gets
	# passed to the Supervisor, which then tells the application system
	# to please place all of its open windows on the field.

#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#| LAYER 12: Modules that don't import any modules from above Layer 11.

from 	apps.appSystem				import	TheAppSystem
	# This class manages startup of the applications system, including
	# all applications that need to begin running at system startup.


	#|==========================================================================
	#|
	#|	2.	Dummy/forward class declarations.			   [module code section]
	#|
	#|			Declare dummy/empty class definitions for classes that
	#|			are either defined in another module that we don't
	#|			import, or that are defined later in the current module.
	#|			This is only needed for type hints; it's documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	2.1.  Dummy declarations for classes defined in other modules.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class	ConsoleClient				:	pass		
	# Note that we don't need to import the actual class definition, because 
	# the console instance gets created before the supervisor in the main
	# program, and is passed into the initializer for TheSupervisor as an 
	# argument.

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	2.2.  Forward declarations for classes defined later in this module.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class	_ActionBySupervisor_		:	pass
class	_SuperAnnouncementAction	:	pass
class	_AnnounceStartupAction		:	pass
class	SupervisorThread			:	pass
class	TheSupervisor				:	pass


	#|==========================================================================
	#|
	#|	3.  Globals.									   [module code section]
	#|
	#|			Declare and/or define various global variables and
	#|			constants.  Top-level global declarations are not 
	#|			strictly required, but they serve to verify that 
	#|			these names were not previously used, and also 
	#|			serve as documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|
		#|	3.1.  Special globals.						[module code subsection]
		#|
		#|			These globals have special meanings defined by the
		#|			Python language.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__		# List of public symbols exported by this module.

__all__ = [
		'TheSupervisor',	# Singleton class for the supervisor object.
	]


	#|==========================================================================
	#|
	#|	4.	Classes.									   [module code section]
	#|
	#|			Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	4.1.	Private classes.					[module code subsection]
		#|
		#|		These classes are only used internally to this module.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class _ActionBySupervisor_(ActionBySystem_):

	"""Abstract base class for any and all actions generated by the
		supervisory subsystem."""

	def __init__(thisSupervisorAction:_ActionBySupervisor_,
			description:str="The supervisor took a generic system action.",
			importance:int=0,	# Importance level (integer); default is 0 (neutral).
		):

			# The conceiver is set implicitly.
		actor = The_Supervisor_Entity()

		super(_ActionBySupervisor_, thisSupervisorAction).__init__(
			description, actor, importance)


class _SuperAnnouncementAction(_ActionBySupervisor_, AnnouncementAction_):

	"""Class for system announcements generated by Supervisor."""

	def __init__(thisAnnouncementAction:_SuperAnnouncementAction,
			announcementText:str="Generic system announcement.",
			importance:int=5,	# Default level for supervisor announcements.
			**kwargs
		):

		annAct = thisAnnouncementAction

		description=f"The supervisory subsystem announces: \"{announcementText}\""

		_logger.debug("_SuperAnnouncementAction.__init__(): Initializing "
					  f"announcement action. Description: '{description}'")

		super(_SuperAnnouncementAction, annAct).__init__(
			description, importance=importance, **kwargs)
			

class _AnnounceStartupAction(_SuperAnnouncementAction):

	"""Class for supervisor annoucing it's starting the system."""

	def __init__(thisAnnStartAction:_AnnounceStartupAction,
			announcementText:str="The system is starting up.",
			importance:int=10,	# System startup seems pretty important.
		):

		_logger.debug("_AnnounceStartupAction.__init__(): Initializing startup "
					  f"announcement action. Announcement text is: '{announcementText}'")

		super(_AnnounceStartupAction, thisAnnStartAction).__init__(
			announcementText, importance)
				 

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	4.2.	Public classes.						[module code subsection]
		#|
		#|		These classes may be referenced by other modules.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class SupervisorThread(ThreadActor):	# Does this even need to be public tho?

	"""A thread to run the supervisory subsystem.  Eventually, this should
		probably become a GLaDOS 'process', once we have support for those."""

	defaultRole = 'Supervise'
	defaultComponent = _sw_component
	
	def __init__(newSupervisorThread:SupervisorThread, supervisor:TheSupervisor):
	
		superthread = newSupervisorThread
		
		superthread._supervisor 	= supervisor
		superthread.exitRequested 	= Flag()
		superthread.running 		= Flag()
			# We raise this flag when we start running and lower it when we stop
			# running. Other threads can wait on this flag to rise or fall.

		superthread.defaultTarget = superthread._main
		super(SupervisorThread, superthread).__init__()
			# Note this thread is NOT a daemon because it's basically the central
			# thread of the entire GLaDOS server application.
	
	def _main(thisSupervisorThread:SupervisorThread):
		
		superthread = thisSupervisorThread
		
		_logger.info("  [Supervisor/Thread] Supervisor thread has started.")
		
			# Inform other threads that this thread is now running.
		superthread.running.rise()	# Raise our "running" flag.
		
			# We have nothing yet to do except wait for an exit to be requested.
		superthread.exitRequested.wait()
		
			# Inform other threads that this thread is no longer running.
		superthread.running.fall()	# Lower our "running" flag.
		
		_logger.info("  [Supervisor/Thread] Supervisor thread is exiting.")
		
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class TheSupervisor:	# Singleton class for the GLaDOS supervisor subsystem.

	"""
	TheSupervisor										   [module public class]
	=============
	
		A singleton class whose sole instance implements the supervisor 
		function within the GLaDOS system; that is, it is the executive 
		entity that creates and manages all of the other subsystems.
	
		On startup, the supervisor starts the other primary subsystems
		of GLaDOS: The command interface, window system, process system,
		and the AI's mind. It then monitors and manages these systems,
		and shuts them down if/when needed (generally only when the AI
		requests it).					
	"""

		#/----------------------------------------------------------------------
		#|	Private singleton instance data members		   [class documentation]
		#|
		#|		These data members keep references to the various 
		#|		subsystems that we manage:
		#|
		#|			._actionSystem
		#|			._commandInterface
		#|			._windowSystem
		#|			._processSystem
		#|			._appSystem
		#|			._cognitiveSystem
		#|
		#|		(We don't use any of these yet; using singletons instead.)
		#|
		#\----------------------------------------------------------------------

	def __init__(theSupervisor:TheSupervisor, console:ConsoleClient):
		
		"""
			supervisor.__init__()					   [special instance method]
				
				This is the singleton instance initializer for the 
				TheSupervisor class.  Because this is a singleton class,
				this method will only get called once, to initialize
				the first and only new instance of TheSupervisor.
				
				This method is responsible for creating and initializing 
				all of the other major subsystems of GLaDOS, including:
				
					* The command interface (command.CommandInterface).
					* The window system (windows.WindowSystem).
					* The process system (process.ProcessSystem).
					* The application system (apps.appSystem).
					* The mind system (mind.mindSystem).
				
				Once all the subsystems have been initialized, the whole
				system can be started (commence active operation); this is
				done in a separate call to supervisor.start().
			
			Arguments:
			~~~~~~~~~~
			
				There is one argument, the ConsoleClient which is the 
				GLaDOS system console; the main human-facing interface.
				We need it so we can link it up with other subsystems.
				We give it a handle to us so it can communicate with us.
				
		"""

		supervisor = theSupervisor

		_logger.info("  [Supervisor] Initializing supervisory subsystem...")
		
		# At this point, the main supervisor thread has not yet been started.
		supervisor._thread = None
			# (This will be done later, when it's time to run our main loop.)

		# As a small initial task, we link up the supervisor (i.e., ourselves) with the console client.
		supervisor.setConsole(console)
		
			#|===============================================================
			#| First, we initialize all of the major GLaDOS subsystems.
			#|
			#| The assignments to local variables here are not really needed, 
			#| since these constructors all maintain their own singletons,
			#| but are included just to document that a value is returned.
		
				#|--------------------------------------------------------------
				#| (0) We initialize our action system. This is a part of the
				#| supervisor subsystem that processes, and decides what to do 
				#| with, major actions taken by other subsystems. It constitutes
				#| the primary mechanism by which other subsystems talk to the 
				#| supervisor subsystem, and by which the supervisor subsystem
				#| maintains supervisory control over the rest of the system.

		_logger.info("    [Supervisor] Initializing our action processing facility...")
		supervisor._actionSystem = tas = TheActionSystem()		
			# Initialize the action processing subsystem.

			# Once that's done, we go ahead right away and inform the console of 
			# how to find the action subsystem, since it needs it in order to be 
			# able to create and execute new actions, e.g., ones taken by the 
			# system operator by entering them using the input panel.
		console.setActionSystem(tas)
			# NOTE: Maybe this isn't needed; the console could just import the 
			# action module and call TheActionSystem() directly?
		
		
				#|--------------------------------------------------------------
				#| (1) We start up the command interface subsystem next.  We do 
				#| this because, in general, every other subsystem of GLaDOS may 
				#| include an associated command module, which needs to be 
				#| installed in the command interface, so it needs to be 
				#| already available.
		
		_logger.info("    [Supervisor] Initializing the command interface...")
		supervisor._commandInterface = ci = TheCommandInterface()		
			# Initializes the command interface.
			
			# As soon as that's done, we give a handle to the command interface
			# back to the action system, because the action system needs to 
			# consult the command interface in the course of action processing.
		tas.commandInterfaceIs(ci)
				

				#|--------------------------------------------------------------
				#| (2) Next, we initialize the virtual text-based window system 
				#| for use by the AI.  (Note this is distinct from the curses-
				#| based window system being utilized by the console display.)  
				#| We do this now because the next step will be to initialize
				#| various other subsystems that may launch associated GLaDOS
				#| processes, and each process generally needs to have an 
				#| associated window which will show its I/O stream.
				
		_logger.info("    [Supervisor] Initializing the text windowing system...")
		ws = TheWindowSystem()			# Initializes the text windowing system.
		
		
				#|--------------------------------------------------------------
				#| (3) Next, we initialize the process system.  This is needed 
				#| to support any background GLaDOS sub-processes that may need 
				#| to be created in order to support individual apps that will 
				#| be launched from within GLaDOS, and furthermore, there may be 
				#| some background processes started by it to support various 
				#| internal housekeeping functions of GLaDOS itself.
		
		_logger.info("    [Supervisor] Initializing the sub-process system...")
		ps = TheProcessSystem()		# Initializes the process framework.
			# Later on, in .start(), below, we will actually start up the 
			# process framework, which will launch any essential background 
			# GLaDOS processes.
				
				
				#|--------------------------------------------------------------
				#| (4) Now we can initialized the application subsystem.  This 
				#| allows individual GLaDOS applications to be launched as 
				#| needed, and some of them will even be launched automatically 
				#| on system startup in .start(), below.
		
		_logger.info("    [Supervisor] Initializing the applications system...")
		appSys = TheAppSystem()		# Initializes the application system.
		
		
				#|--------------------------------------------------------------
				#| (5) Finally, we can initialize the A.I.'s cognitive system.
				#| We pass it a pointer to the console, because it will need to
				#| be able to update the console display when the field changes.
		
		_logger.info("    [Supervisor] Initializing the cognitive system...")
		mind = TheCognitiveSystem(console)	# Initializes the A.I.'s mind, itself.
		
		
			#|------------------------------------------------------------------
			#| At this point, all of the individual subsystems have been 
			#| initialized.  A final step, which we make explicit at top level 
			#| here, is we connect up the AI's input feed from the rest of the 
			#| system.  
			#|
			#| What this means is, we tell the cognitive system to go ahead and 
			#| create and subscribe to all of the "action channels" it wants (to
			#| get notifications from the rest of the system), and then we tell
			#| the action system to add these channels to the "Action News 
			#| Network" so that they will receive and broadcast all action update 
			#| reports.
			#|
			#| After this, the AI's cognitive system should start receiving 
			#| updates about various actions that are occurring in the 
			#| system, and it can respond in an appropriate way.  (Typically,
			#| by adding corresponding events to its cognitive stream, which 
			#| then makes these events visible in the AI's receptive field,
			#| which then allows the core AI (NLP system) to respond to them.)
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		theSupervisor.connect_AI_inputs()	
			# Connects up all of the inputs to AI the from the rest of the system.
		
		
			#|---------------------------------------------------------
			#| At this point, we have finished initializing everything.
		
		_logger.info("  [Supervisor] All subsystems have been initialized.")
		
	#__/ End singleton instance initializer for class TheSupervisor.

	def setConsole(theSupervisor:TheSupervisor, console:ConsoleClient):
		
		"""Connect ourselves up with the console, so it can communicate
			with us as needed."""
		
		supervisor = theSupervisor
		supervisor._console = console
		console.setSupervisor(supervisor)

	@property
	def console(theSupervisor:TheSupervisor):
		return theSupervisor._console

	def connect_AI_inputs(theSupervisor):
	
		"""Connect up all the input channels feeding from us (the supervisory 
			system) to the AI.  Right now, we basically give the cognitive
			subsystem full latitude to control this process; it creates all the 
			channels, and we just obligingly hook them all up.  Later versions
			of GLaDOS could move more of the responsibility for controlling 
			the information flow up to the Supervisor.  However, for now, it
			hardly matters, since they're both part of the same code base."""
	
			#|------------------------------------------------------------------
			#| Ask the cognitive system, "Excuse me, what are all of the input 
			#| channels that you would like me to fill up with information?"
	
		aiInputChannels = TheCognitiveSystem().inputChannels
		
			#|------------------------------------------------------------------
			#| Tell our friends over at the Action News Network (ANN), "Hey, you 
			#| guys need to immediately add all of these channels to your 
			#| network of broadcase stations, and make sure that every bit of 
			#| the content that you produce gets distributed to all of them!"
		
		TheActionNewsNetwork().addChannels(aiInputChannels)

	def startup(theSupervisor):
	
		"""This method 'starts up' the supervisor, which puts it and all subsystems
			into an active operation mode.  This will kick off all of the various 
			background subprocesses/threads in the system.  (Except for console-
			related threads, which will already have started running when the 
			console client started up earlier.)"""
	
		theSupervisor.announceStartup()
			# This announces that the GLaDOS system is starting up.
			# The announcement should be sent to STDERR, and be displayed in
			# red in the console panel on the operator's system console display.
			# It should also appear as an event in the AI's receptive field.
	
		#TheActionSystem().startup()		# No background functionality yet.
		#TheCommandInterface().startup()	# No background functionality yet.
		#TheWindowSystem().startup()		# No background functionality yet.
		#TheProcessSystem().startup()		# No background functionality yet.
		TheAppSystem().startup()		# This doesn't really do much yet.
		TheCognitiveSystem().startup()	# Start the AI's cognitive system.
		
			#|------------------------------------------------------------
			#| Next, we just start the supervisor main loop. This runs in
			#| its own background thread that is created for this purpose.
		
		_logger.info("  [Supervisor] Starting main loop...")
		theSupervisor.startMainloop()
		
	
	@staticmethod
	def announceStartup():	
			# This conceives of the action of announcing that that the 
			# system is starting up, then immediately initiates this 
			# action that we just conceived of taking.  The action 
			# processing system takes over from there.
		_logger.debug("  [Supervisor] Creating and initiating startup announcement action.")
		_AnnounceStartupAction().initiate()
	
	def startMainloop(theSupervisor):
		
		supervisor = theSupervisor
		
			# Create the main supervisor thread.
		supervisor._thread = superthread = SupervisorThread(supervisor)
		
		_logger.debug("theSupervisor.startMainloop(): Starting main supervisor thread.")
		superthread.start()

	@property
	def thread(theSupervisor):
		return theSupervisor._thread


	def requestExit(theSupervisor:TheSupervisor):

		"""Calling this method requests the supervisor subsystem to exit."""

		supervisor = theSupervisor
		supthread = supervisor.thread		

		if supthread is None:
			_logger.error("supervisor.requestExit(): Supervisor thread does not exist! Ignoring.")
			return

		supthread.exitRequested.rise()		# Raise the thread's exit request flag.
		

	def waitForExit(theSupervisor):
		
		"""This method just waits for the supervisor instance that we created to exit."""
	
		supervisor = theSupervisor
		superthread = supervisor.thread

			# Wait for the main thread to exit by doing a thread join.
		superthread.join()
		
		# TODO: Implement this.
		
#__/ End class TheSupervisor.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					END OF FILE:   supervisor/supervisor.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%