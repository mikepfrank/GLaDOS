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

from logmaster import getComponentLogger

	# Go ahead and create or access the logger for this module.

_component = path.basename(path.dirname(__file__))		# Our package name.
_logger = getComponentLogger(_component)    			# Create the component logger.


			#|----------------------------------------------------------------
			#|  The following modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from commands.initializer			import	CommandInterfaceInitializer
	# This class manages initialization of the command interface.
	# (That is, the command interface used by the AI to control GLaDOS.)

from windows.initializer			import	WindowSystemInitializer
	# This class manages initialization of the text window system.

from processes.launcher             import  ProcessLauncher
    # This class manages launching of all GLaDOS processes.

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

	"""Supervisor"""

#__/ End class Supervisor.

	# # Move the below into SupervisorStarter().
	# CommandInterfaceInitializer()	# Initializes the command interface.
	# WindowSystemInitializer()		# Initializes the text windowing system.
	# ProcessLauncher()				# Launch all of the GLaDOS processes.
	# MindStarter()					# Start up the A.I.'s mind, itself.
	
