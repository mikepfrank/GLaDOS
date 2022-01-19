#|==============================================================================
#|                      TOP OF FILE:    appdefs.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:      appdefs.py                     [Python module source code]

    SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
    SW COMPONENT:   GLaDOS.logging (GLaDOS logging framework)

	LAYER/LEVEL:	0 (bottom; no imports of custom modules)

    MODULE NAME:    appdefs
    FULL PATH:      $GIT_ROOT/GLaDOS/src/appdefs.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git


    MODULE DESCRIPTION:
    -------------------

          Application-specific definitions.

          This file defines some parameters specific to the present
          application.  It may be utilized from within general-
          purpose modules to customize those modules for this
          particular application.

          At present, we are only using this to define <systemName>
          and <appName> parameters, which are used to compose names
          of system-specific and application-specific loggers. Also,
          <topFile> is utilized in logger output.

          E.g., the logger for a module or component that is specific
          to the system (but not to the particular application program)
          would be called "<systemName>.<othername>", whereas the logger
          for a module specific to the present application would be
          called "<appName>.<othername>".  Further, <appName> itself
          should begin with "<systemName>."


    MODULE PUBLIC GLOBALS:
    ----------------------


        appdefs.systemName:str                  [global constant string]
        
                This string gives the name of the overall
                system that the present application is a
                part of.  Lexically it should be a standard
                identifier (alphanumeric string).

                
        appdefs.appName:str                     [global constant string]

                This string gives the name of the present
                application (as a component of the overall
                system).  It consists of the <systemName>
                followed by a "." and an identifier
                specifying this application (as distinct
                from other components of the system).


        appdefs.topFile:str                     [global constant string]
        
                This string gives the name of the top-level
                file of the present application, sans the .py
                extension.
    
                                                                            """
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------

    #|==========================================================================
    #|
    #|   Globals					    [code section]
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
        #|  Special globals.                                    [code section]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global  __all__         # List of public symbols exported by this module.
__all__ = [
    'systemName',    # Name of the system this application is part of.
    'appName',       # Name of the current application program.
    'topFile'        # The filename of the top-level file of this app.
    ]


        #|======================================================================
        #|
        #|  Module public globals.                              [code section]
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

global systemName, appName, topFile
    # Note this declaration doesn't really do anything at top level.

        #|----------------------------------------------------------------------
        #|
        #|      appdefs.systemName:str              [global constant string]
        #|
        #|          This string gives the name of the overall
        #|          system that the present application is a
        #|          part of.  Lexically it should be a standard
        #|          identifier (alphanumeric string).
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

systemName  =   "GLaDOS"       # This code is part of the "Dynamic" system.


        #|----------------------------------------------------------------------
        #|
        #|      appdefs.appName:str                 [global constant string]
        #|
        #|          This string gives the name of the present
        #|          application (as a component of the overall
        #|          sytem).  It consists of the <systemName>
        #|          followed by a "." and an identifier
        #|          specifying this application (as distinct
        #|          from other components of the system).
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

appName     =   systemName + ".server"
    #-This application program is the (main, central) component
    # of the system.

        #|----------------------------------------------------------------------
        #|
        #|      appdefs.topFile:str                 [global constant string]
        #|
        #|          This string gives the name of the top-level
        #|          file of the present application, sans the .py
        #|          extension.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

topFile 	= 	'glados-server'    # Note that the .py is implicit here.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                      END OF FILE:   appdefs.py
#|=============================================================================
