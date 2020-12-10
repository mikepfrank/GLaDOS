#|==============================================================================
#|                   TOP OF FILE:    commands/initializer.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:      commands/initializer.py       	[Python module source file]

    IN PACKAGE:		commands
	MODULE NAME:    commands.initializer
    FULL PATH:      $GIT_ROOT/GLaDOS/src/commands/initializer.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.server.commands (command interface component)


	MODULE DESCRIPTION:
	-------------------

		This module initializes the GLaDOS command interface. This is the
		interface that allows the AI to type commands to the GLaDOS system
		and have them be executed by the system.
		
		The command interface is organized into "command modules" associated
		with specific facilities or processes within the GLaDOS system.  New
		command modules can be added dynamically into the interface.  In the
		main loop of the system, when the A.I. generates a text event

"""


# commands/initializer.py

# Classes:
#	
#	* Command
#	* CommandList
#	* CommandModule
#	* CommandModules
#	* CommandInterface
#	* CommandInterfaceInitializer
#


