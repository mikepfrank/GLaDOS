#|==============================================================================
#|                   TOP OF FILE:    supervisor/supervisor.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""

	FILE NAME:		supervisor/supervisor.py			[Python module source file]
	
    IN PACKAGE:		supervisor
	MODULE NAME:    supervisor.supervisor
    FULL PATH:      $GIT_ROOT/GLaDOS/src/supervisor/supervisor.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
    SW COMPONENT:   GLaDOS.supervisor (server configuration component)


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
			
			(2) The process subsystem (`processes/`). This subsystem
				manages a set of GLaDOS 'processes' that the AI can
				interact with to communicate to the outside world,
				to human users, to other local systems or to various
				subsystems of GLaDOS itself. Processes come with 
				associated command modules, and the AI interacts with
				each process through a dedicated text 'window.'
			
			(3) The cognitive subsystem (`mind/`). This subsystem 
				maintains the A.I.'s mental state, described in terms
				of a long-term memory bank, a real-time event history, 
				a receptive field, and a dynamic API configuration.
				Windows appear in the receptive field and the A.I. uses
				them to interact with various processes & subsystems.
				The main event loop of the A.I. also happens here.
			
			(4) The windowing subsystem (`windows/`). This subsystem
				manages various text-based 'windows' that appear in the
				A.I.'s visual field that the A.I. can use to interact 
				with various processes.
	
	
	USAGE:
	------
	
		from supervisor.starter	import Supervisor
		...
		# Server configuration should be loaded first, then call:
		supervisor = Supervisor()	# Create & start supervisor (and various threads).
		...
		supervisor.waitForExit()	# Waits for the Supervisor to exit.
	
	
	MODULE PUBLIC CLASSES:
	----------------------
		
		Supervisor											[class]
			
			Singleton class, whose sole instance is the single
			object which is the system supervisor.
																			"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


    #|==========================================================================
    #|
    #|   1. Module imports.                                [module code section]
    #|
    #|          Load and import names of (and/or names from) various
    #|          other python modules and pacakges for use from within
    #|          the present module.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|  1.1. Imports of standard python modules.    [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from os		import	path  	# Manipulate filesystem path strings.


        #|======================================================================
        #|  1.2. Imports of custom application modules. [module code subsection]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|  The following modules, although custom, are generic utilities,
			#|  not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.  (This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)    			# Create the component logger.


			#|----------------------------------------------------------------
			#|  The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from config.configuration			import	Configuration
	# The singleton class that gives the system configuration.

from commands.commandInterface		import	CommandInterface
	# This class manages initialization of the command interface.
	# (That is, the command interface used by the AI to control GLaDOS.)

from windows.windowSystem			import	WindowSystem
	# This class manages initialization of the text window system.

from processes.processSystem        import  ProcessSystem
    # This class manages launching of all essential 'background' 
	# GLaDOS processes.

from apps.appSystem					import	AppSystem
	# This class manages startup of the applications system, including
	# all applications that need to begin running at system startup.

from mind.mindSystem				import	MindSystem
	# This class manages starting up the A.I.'s mind on server startup.



    #|==========================================================================
    #|
    #|   Globals					    						[code section]
    #|
    #|      Declare and/or define various global variables and
    #|      constants.  Top-level global declarations are not
    #|      strictly required, but they serve to verify that
    #|      these names were not previously used, and also
    #|      serve as documentation.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|
        #|  Special globals.                              	[code subsection]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__		# List of public symbols exported by this module.
__all__ = [
	'Supervisor',		  	# Singleton class for the supervisor object.
    ]


	#|==========================================================================
	#|
	#|	Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


class Supervisor:	# Singleton class for the GLaDOS supervisor subsystem.

	"""
		Supervisor													[class]
		==========
		
			A singleton class whose sole instance implements the 
			supervisor function within the GLaDOS system; that is, 
			it is the executive entity that creates and manages all 
			of the other subsystems.
			
			On startup, the supervisor starts the other primary subsystems
			of GLaDOS: The command interface, window system, process system,
			and the AI's mind. It then monitors and manages these systems,
			and shuts them down if/when needed (generally only when the AI
			requests it).			
																			"""

		#|----------------------------------------------------------------------
		#|	Supervisor._supervisor					[private class data member]
		#|
		#|		This class-level attribute references the unique instance of
		#|		this class that exists in the system.  It is initialized the
		#|		first time the class's constructor is called.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	_supervisor = None		# Instance not yet created at module load time.


	def __new__(thisClass, *args, **kwargs):
		"""
			Configuration.__new__()						[special class method]
		
				This special method is called to create new instances of
				the class when the class constructor is invoked by calling
				the class itself, i.e., with the syntax Configuration(...).  
		
				The design pattern used here is what makes Configuration a 
				singleton class; that is, it only creates one instance.  
				Subsequent calls return the same instance.
		
				Please note that in this implementation, the private 
				instance method ._init(), which is the singleton instance 
				initializer method, is called when the instance is initially 
				created; it is *not* called on any subsequent calls to the 
				class constructor.
		
				At some point, we should abstract out this singleton 
				functionality as a metaclass, but that is lower priority.
		"""
		if thisClass._configuration is None:
			inst = super(Configuration, thisClass).__new__(thisClass)
			thisClass._configuration = inst
			inst._init(*args, **kwargs)		# Private one-time instance initializer.
		else:
			inst = thisClass._configuration
		return inst
	#__/ End singleton instance creation method for class Supervisor.
	
	
	def _init(self):
	
		"""
			supervisor._init()					  	   [private instance method]
		
				This is the singleton instance initializer for the 
				Supervisor class.
		
				This private instance method is invoked by the .__new__() 
				method (above) to initialize the newly-created singleton
				instance of Supervisor on the first call to the Supervisor 
				class.  Please note that subsequent calls to Supervisor() 
				do NOT invoke this initializer method.
			
				This method is responsible for creating and initializing 
				all of the other major subsystems of GLaDOS, including:
			
					* The command interface (command.CommandInterface).
					* The window system (windows.WindowSystem).
					* The process system (process.ProcessSystem).
					* The application system (apps.appSystem).
					* The mind system (mind.mindSystem).
		"""
		
			#|===============================================================
			#| First, we start up all of the GLaDOS subsystems.
			#|
			#| The assignments to local variables here are not really needed, 
			#| since these constructors all maintain their own singletons,
			#| but are included just to document that a value is returned.
		
				#|--------------------------------------------------------------
				#| (1) We start up the command interface subsystem first.  We do 
				#| this because, in general, every other subsystem of GLaDOS may 
				#| include an associated command module, which needs to be 
				#| installed in the command interface, so it needs to be 
				#| already available.
		
		ci = CommandInterface()		# Initializes the command interface.

		
				#|--------------------------------------------------------------
				#| (2) Next, we start up the text-based window system.  We do 
				#| this now because the next step will be to start up various 
				#| other subsystems that may launch associated GLaDOS processes, 
				#| and each process generally needs to have an associated window
				#| which will show its I/O stream.
		
		ws = WindowSystem()			# Initializes the text windowing system.
		
		
				#|--------------------------------------------------------------
				#| (3) Next, we start up the process system.  This is needed to
				#| support any processes that may need to be created to support
				#| individual apps that will be launched from within GLaDOS, and 
				#| furthermore, there may be some background processes started 
				#| here to support various internal housekeeping functions of 
				#| GLaDOS itself.
				
		ps = ProcessSystem()		
			# Start the process framework and launch any essential 
			# background GLaDOS processes.
		
		
				#|--------------------------------------------------------------
				#| (4) Now we can start the application subsystem.  This allows
				#| individual GLaDOS applications to be launched as needed, and
				#| some of them will even be launched automatically on startup.
				
		appSys = AppSystem()		# Start up the application system.
		
		
				#|--------------------------------------------------------------
				#| (5) Finally, we can start up the A.I.'s mind.
		
		mind = MindSystem()			# Start up the A.I.'s mind, itself.
	
	
			#|------------------------------------------------------------
			#| Next, we just start the supervisor main loop. This runs in
			#| its own background thread that is created for this purpose.
			
		self.startSupervisorMainloop()		# To be implemented.
	
	#__/ End singleton instance initializer for class Supervisor.

	def waitForExit(self):
	
		"""This method just waits for the supervisor instance that we created to exit."""
	
		# TODO: Implement this.
	
#__/ End class Supervisor.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                  END OF FILE:   supervisor/supervisor.py
#|=============================================================================