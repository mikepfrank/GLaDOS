#|==============================================================================
#|                    TOP OF FILE:    supervisor/starter.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""

	FILE NAME:		supervisor/starter.py			[Python module source file]
	
    IN PACKAGE:		supervisor
	MODULE NAME:    supervisor.starter
    FULL PATH:      $GIT_ROOT/GLaDOS/src/supervisor/starter.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
    SW COMPONENT:   GLaDOS.server.supervisor (server configuration component)


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
	
		from supervisor.starter	import SupervisorStarter
		...
		# Server configuration should be loaded first, then call:
		SupervisorStarter()		# Starts supervisor (and various threads).
		...
		SupervisorStarter.waitForExit()	 # Waits for the Supervisor to exit.
	
	
	MODULE PUBLIC GLOBALS:
	----------------------

		starter.supervisor							[constant object]
		
			The Supervisor instance that comprises the system
			supervisor.
	
	
	MODULE PUBLIC CLASSES:
	----------------------
		
		Supervisor											[class]
			
			Class of supervisor objects.  Normally there is 
			only one instance of this class in the system
			(stored in starter.supervisor).
		
		
		SupervisorStarter									[class]
			
			Dummy class for starting up the supervisor.
			Instances don't mean anything.  The constructor
			does all the work.  It could have just been a
			function instead, but oh well.  It includes a
			helper function, and maybe we'll also want to 
			move some other stuff into here eventually.  
			(Like stuff to load/save the server config.)

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

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)    			# Create the component logger.


			#|----------------------------------------------------------------
			#|  The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from config.loader					import	Configuration, serverConfiguration
	# The server configuration (of class Configuration) that is used
	# in case no other configuration is supplied on supervisor creation.

from commands.initializer			import	CommandInterfaceInitializer
	# This class manages initialization of the command interface.
	# (That is, the command interface used by the AI to control GLaDOS.)

from windows.initializer			import	WindowSystemInitializer
	# This class manages initialization of the text window system.

from processes.launcher             import  ProcessLauncher
    # This class manages launching of all essential 'background' 
	# GLaDOS processes.

from apps.startup					import	AppSystemStarter
	# This class manages startup of the applications system, including
	# all applications that need to begin running at system startup.

from mind.startup					import	MindStarter
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

global  __all__         # List of public symbols exported by this module.
__all__ = [
	'Supervisor',		  	# Class for supervisor objects.
    'supervisor',    		# Object which is the GLaDOS supervisor.
    'SupervisorStarter',    # Creates & starts up the supervisor.
    ]


        #|======================================================================
        #|
        #|  Public globals.                              		[code section]
        #|
        #|      These globals are specific to the present module
        #|      and exported publicly to other modules that use it.
        #|
		#|      User modules should do "from appdefs import *"
		#|      to get immediate copies of these globals.
		#|
		#|      If users wish to modify these globals, they must also
		#|      do "import appdefs" and then "appdefs.<global> = ..."
		#|      (Warning: This will not affect the values of these
		#|      globals seen by other modules that have already
		#|      imported this module!)
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global supervisor	# The supervisor object for the server.
supervisor = None	# None created yet at module import time.


	#|==========================================================================
	#|
	#|	Classes.												[code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


class Supervisor:	# A GLaDOS supervisor.

	"""
		Supervisor													[class]
		
			An object of this class implements the supervisor function
			within the GLaDOS system; that is, it is the executive 
			entity that creates and manages all of the other subsystems.
			
			Its constructor optionally takes an object of class 
			Configuration (defined in config.loader) which specifies the 
			GLaDOS configuration being used (if not the system-wide one).
			
			On startup, the supervisor starts the other primary subsystems
			of GLaDOS: The command interface, window system, process system,
			and the AI's mind. It then monitors and manages these systems,
			and shuts them down if/when needed (generally only when the AI
			requests it).
																			"""

	def __init__(self, config:Configuration = systemConfiguration):
		
			#|-------------------------------------------------------------
			#| First, we start up all of the GLaDOS subsystems, passing the 
			#| system configuration we're using in to each of them.  
			#|
			#| NOTE: Do we also need to pass each of them a link to 
			#| ourselves and remember each of them in an instance data 
			#| member? I think we do. [TODO]
		
		cii = CommandInterfaceInitializer(config)	# Initializes the command interface.
		wsi = WindowSystemInitializer(config)		# Initializes the text windowing system.
		pl  = ProcessLauncher(config)				# Launch all of the essential background GLaDOS processes.
		ass = AppSystemStarter(config)				# Start up the application system.
		ms	= MindStarter(config)					# Start up the A.I.'s mind, itself.
	
			# TODO: At this point, I think that we may need to retrieve a handle into 
			# each of the subsystems from the entities (cii, etc.) that started them
			# and store them in instance attributes.
	
			#|------------------------------------------------------------
			#| Next, we just start the supervisor main loop. This runs in
			#| its own background thread that is created for this purpose.
			
		self.startSupervisorMainloop()
	
	#__/ End Supervisor initializer.

#__/ End class Supervisor.


class SupervisorStarter:

	"""Dummy class that exists for the sole purpose of starting up the 
		Supervisor.  This could probably just be made into a module-level 
		function, but whatevs.  Maybe we'll add more stuff to it later."""

	def __init__(self):	# Note the caller can just throw away this instance after initialization.
	
			# Create a supervisor using the existing system configuration.
			# We remember this in an instance attribute so we can access 
			# it later.
	
		self.supervisor = Supervisor()
	
			# This also sets the module global 'supervisor' to remember
			# the last supervisor that we created.
			
		supervisor = self.supervisor
		
	#__/ End SupervisorStarter initializer.

	def waitForExit(self):
	
		"""This method just waits for the supervisor instance that we created to exit."""
	
		self.supervisor.waitForExit()
	
#__/ End class SupervisorStarter.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                    END OF FILE:   supervisor/starter.py
#|=============================================================================