#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 supervisor/supervisor.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		supervisor/supervisor.py		 [Python module source file]
		
	MODULE NAME:	supervisor.supervisor
	IN PACKAGE:		supervisor
	FULL PATH:		$GIT_ROOT/GLaDOS/src/supervisor/supervisor.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.supervisor (Principal supervisory subsystem)


	MODULE DESCRIPTION:
	-------------------
	
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
		------
		
			from supervisor.starter import TheSupervisor
			...
			# Server configuration should have been loaded first, then call:
			supervisor = TheSupervisor()	# Create & start supervisor (and various threads).
			...
			supervisor.waitForExit()	# Waits for the TheSupervisor to exit.
		
		
		MODULE PUBLIC CLASSES:
		----------------------
				
			TheSupervisor												 [class]
						
				Singleton class, whose sole instance is the single
				object which is the system supervisor.
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

from os		import	path	# Manipulate filesystem path strings.


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

from	settings.settings			import	TheSettingsFacility
	# This facility is for keeping track of all the available settings.

from 	config.configuration		import	TheConfiguration
	# The singleton class that gives the system configuration.

from 	.action						import	TheActionSystem, ActionBySystem_
	# The abstract base class for subsystem actions that we'll process.

from 	commands.commandInterface	import	TheCommandInterface
	# This class manages initialization of the command interface.
	# (That is, the command interface used by the AI to control GLaDOS.)

from 	windows.windowSystem		import	TheWindowSystem
	# This class manages initialization of the text window system.

from 	processes.processSystem	import	TheProcessSystem
	# This class manages launching of all essential 'background' 
	# GLaDOS processes.

from 	apps.appSystem				import	TheAppSystem
	# This class manages startup of the applications system, including
	# all applications that need to begin running at system startup.

from 	mind.mindSystem			import	TheCognitiveSystem
	# This class manages starting up the A.I.'s mind on server startup.
	# NOTE: The receptive field gets created in here; as soon as it
	# exists, it generates an AnnounceFieldExists action, which gets
	# passed to the Supervisor, which then tells the application system
	# to please place all of its open windows on the field.


	#|==========================================================================
	#|
	#|	 2. Globals												  [code section]
	#|
	#|		Declare and/or define various global variables and
	#|		constants.	Top-level global declarations are not
	#|		strictly required, but they serve to verify that
	#|		these names were not previously used, and also
	#|		serve as documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|
		#|	Special globals.								   [code subsection]
		#|
		#|		These globals have special meanings defined by the
		#|		Python language.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__		# List of public symbols exported by this module.
__all__ = [
		'TheSupervisor',	# Singleton class for the supervisor object.
	]


	#|==========================================================================
	#|
	#|	3. Classes.												  [code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class AnnounceStartupAction(ActionBySystem_):
	pass

@singleton
class TheSupervisor:	# Singleton class for the GLaDOS supervisor subsystem.
	#---------------------------------------------------------------------------
	"""
	TheSupervisor														 [class]
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
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

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

	def __init__(theSupervisor):
		
		"""
			supervisor.__init__()					   [special instance method]
				
				This is the singleton instance initializer for the 
				TheSupervisor class.  Because this is a singleton class,
				this method will only get called once, to initialize
				the first and only instance of TheSupervisor.
				
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
		"""

		_logger.info("Initializing supervisory subsystem...")
		
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

		_logger.info("    Supervisor: Initializing our action processing facility...")
		tas = TheActionSystem()		# Initialize the action subsystem.
		
				#|--------------------------------------------------------------
				#| (1) We start up the command interface subsystem first.  We do 
				#| this because, in general, every other subsystem of GLaDOS may 
				#| include an associated command module, which needs to be 
				#| installed in the command interface, so it needs to be 
				#| already available.
		
		_logger.info("    Supervisor: Initializing the command interface...")
		ci = TheCommandInterface()		# Initializes the command interface.

				
				#|--------------------------------------------------------------
				#| (2) Next, we start up the text-based window system.	We do 
				#| this now because the next step will be to start up various 
				#| other subsystems that may launch associated GLaDOS processes, 
				#| and each process generally needs to have an associated window
				#| which will show its I/O stream.
				
		_logger.info("    Supervisor: Initializing the text windowing system...")
		ws = TheWindowSystem()			# Initializes the text windowing system.
		
		
				#|--------------------------------------------------------------
				#| (3) Next, we start up the process system.  This is needed to
				#| support any processes that may need to be created to support
				#| individual apps that will be launched from within GLaDOS, and 
				#| furthermore, there may be some background processes started 
				#| here to support various internal housekeeping functions of 
				#| GLaDOS itself.
		
		_logger.info("    Supervisor: Initializing the sub-process system...")
		ps = TheProcessSystem()			
			# Start the process framework and launch any essential 
			# background GLaDOS processes.
				
				
				#|--------------------------------------------------------------
				#| (4) Now we can start the application subsystem.	This allows
				#| individual GLaDOS applications to be launched as needed, and
				#| some of them will even be launched automatically on startup.
		
		_logger.info("    Supervisor: Initializing the applications system...")
		appSys = TheAppSystem()		# Initializes the application system.
		
		
				#|--------------------------------------------------------------
				#| (5) Finally, we can initialize the A.I.'s cognitive system.
		
		_logger.info("    Supervisor: Initializing the cognitive system...")
		mind = TheCognitiveSystem()			# Start up the A.I.'s mind, itself.
		
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
			#| Network."
		
		theSupervisor.connect_AI_inputs()	
			# Connects up all of the inputs to AI the from the rest of the system.
		
			#|---------------------------------------------------------
			#| At this point, we have finished initializing everything.
		
		_logger.info("    Supervisor:  All subsystems have been initialized.")
		
	#__/ End singleton instance initializer for class TheSupervisor.

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
	
		aiInputChannels = TheCognitiveSystem().inputChannels()
		
			#|------------------------------------------------------------------
			#| Tell our friends over at the Action News Network (ANN), "Hey, you 
			#| guys need to immediately add all of these channels to your 
			#| network of broadcase stations, and make sure that every bit of 
			#| the content that you produce gets distributed to all of them!"
		
		TheActionNewsNetwork.addChannels(aiInputChannels)

	def start(theSupervisor):
		"""This method 'starts' the supervisor, which puts it and all subsystems
			into an active operation mode.  This will kick off all of the various 
			background subprocesses/threads in the system."""
	
		theSupervisor.announceStartup()
			# This announces that the GLaDOS system is starting up.
	
		#TheActionSystem().start()		# No background functionality yet.
		#TheCommandInterface().start()	# No background functionality yet.
		#TheWindowSystem().start()		# No background functionality yet.
		#TheProcessSystem().start()		# No background functionality yet.
		#TheAppSystem().start()			# No background functionality yet.
		TheCognitiveSystem().start()	# Start the AI's cognitive system.
		
			#|------------------------------------------------------------
			#| Next, we just start the supervisor main loop. This runs in
			#| its own background thread that is created for this purpose.
		
		_logger.info("    Supervisor: Starting main loop...")
		theSupervisor.startSupervisorMainloop()		# To be implemented.
	
	def announceStartup():
	
			# This conceives of the action of announcing that that the 
			# system is starting up, then immediately initiates this 
			# action that we just conceived of taking.  The action 
			# processing system takes over from there.
		StartupAccouncementAction().initiate()
	
	
	def startSupervisorMainloop(theSupervisor):
		pass

	def waitForExit(theSupervisor):
		
		"""This method just waits for the supervisor instance that we created to exit."""
	
		pass
		# TODO: Implement this.
		
#__/ End class TheSupervisor.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					END OF FILE:   supervisor/supervisor.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
