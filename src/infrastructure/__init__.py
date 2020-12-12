#|==============================================================================
#|                  TOP OF FILE:    infrastructure/__init__.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:    infrastructure/__init__.py    [Python package initialization module]

    FULL PATH:          $GIT_ROOT/GLaDOS/src/infrastructure/__init__.py
    MASTER REPO:    	https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:        GLaDOS (Generic Lifeform and Domicile Operating System)
	APPLICATION NAME:   GLaDOS.server (GLaDOS server application)
    COMPONENT NAME:     GLaDOS.infrastructure
    PACKAGE NAME:       infrastructure


    FILE DESCRIPTION:
    -----------------

        This Python file is the package-initialization module for
        the 'infrastructure' package within the GLaDOS software system.
        
        For general background on Python packages, see the comments
        within this file, or the online documentation at:
        [https://docs.python.org/3/tutorial/modules.html#packages].


    PACKAGE DESCRIPTION:
    --------------------

        The purpose of the 'infrastructure' package is to gather together
        the modules implementing the infrastructure facility, which is
		a set of general-purpose (reusable) modules supporting GLaDOS.
		
		This particular infrastructure would be useful for implementing
		almost any complex multithreaded Python application.  In GLaDOS
		we use it to support the various interactive subsystems and 
		processes making up the GLaDOS system.
		
		The modules included within the infrastructure package include:
		
			1.	utils			Miscellaneous simple utilities.
			
			2.	logmaster		Advanced logging support.
			
			3.	flags			A useful concurrency primitive.
			
			4.	desque			Double-ended synchronous queues,
									useful for communicating between
									different threads.
			
			5.	heart			A simple module that facilitates
									system 'liveness' monitoring.
			
			6.	worklist		Allows delegation/handoff of work 
									items between different threads.
			
		Additional modules may be added to this package as needed.
    

    PACKAGE DEPENDENCIES:
    ---------------------

        The infrastructure package uses the _____ and ______ packages, and
        is used by the ______ package.
        
    
    MODULE HIERARCHY:
    -----------------

        The approximate hierarchy of modules within this package (also
        shown in the package's README.md file) is as follows:

			[to fill in later]
                                                                             """
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string for infrastructure/__init__.py.
#|------------------------------------------------------------------------------

    #/--------------------------------------------------------------------------
    #|
    #|  GENERAL COMMENTS ON PYTHON PACKAGE INITIALIZATION FILES:
    #|
    #|          A package in Python is defined by a subdirectory of the
    #|      Python program's top-level directory, whose name is the package
    #|      name, and which contains an __init__.py file, like this one.
    #|      That file defines a module named <package>, which is the package.
    #|      Any other .py files in the directory are modules in the package.
    #|      Packages may also contain nested sub-packages in subdirectories.
    #|
    #|          When a package's __init__.py file is loaded, the namespace
    #|      gets pre-loaded with the attribute __path__, which contains
    #|      the full filesystem path to the package's directory, which (in
    #|      this case) is the "infrastructure/" subdirectory of the top-level
    #|      source directory for the GLaDOS system.
    #|
    #|          Then, the package may define __all__, which is a list of
    #|      the module names that would be automatically imported if the
    #|      user of the package did "from <package> import *".
    #|
    #|          However, the stylistically-preferred way to import modules
    #|      from a package is one at a time, as in the syntax
    #|
    #|                  from <package> import <module>                  ,
    #|
    #|      or you can also import specific module attributes like this:
    #|
    #|                  from <package>.<module> import <attr>           .
    #|
    #|          Modules in packages can import other "sibling" modules
    #|      residing in the same ("parent") package as themselves using
    #|      the abbreviated syntax,
    #|
    #|                  from .<siblingModule> import <attr>             ,
    #|
    #|      and from other "cousin" modules residing in "uncle" packages
    #|      (i.e., packages that are siblings of the module's parent
    #|      package) using syntax like
    #|
    #|                  from ..<unclePackage> import <cousinModule>     .
    #|
    #|      However, that syntax is not advantageous except from within
    #|      nested packages, because otherwise the '..' can be omitted.
    #|
    #\--------------------------------------------------------------------------

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

from os		import	path  		# Manipulate filesystem path strings.


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


    #|==========================================================================
    #|
    #|   2. Globals					    				   [module code section]
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
        #|  2.1. Special globals.                              [code subsection]
        #|
        #|      These globals have special meanings defined by the
        #|      Python language.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#/------------------------------------------------------------------
			#|
			#|      __all__                             [special package global]
			#|
			#|              Within the __init__ file of a package, the
			#|              __all__ global defines the list of module
			#|              names that will be automatically imported
			#|              if the user does "from <package> import *".
			#|              These can be considered to be the "public"
			#|              modules of the package.  A package may also
			#|              include private modules (whose names would
			#|              conventionally start with underscores).
			#|              Those modules would not be listed here.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global  __all__         # List of public symbols exported by this module.
__all__ = [
		# These are listed roughly in order of low-level to high-level.
		'utils',		# Miscellaneous simple utilities.
		'logmaster',	# Advanced logging support for multithreaded apps.
		'flags',		# A synchronization primitive for concurrent programs.
		'desque',		# Double-ended synchronous queues for inter-thread comms.
		'heart',		# A simple system liveness monitor.
		'worklist',		# Support for handing off executable code between threads.
		# No more public modules yet; if more are created, add them here.
    ]


        #|======================================================================
        #|
        #|  2.1. Private globals.                              [code subsection]
        #|
		#|		These globals are not intended to be accessed from outside
		#|		of the present package.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# These globals are initialized in the main body section, below.
	
global _component	# The name of the software component this package is part of.
global _logger		# The logger associated with this package.


    #|==========================================================================
    #|
    #|   3. Main body code.			    				   [module code section]
    #|
	#|		The main body of this module executed at import time.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|----------------------------------------------------------------------
		#|   Consider this package to be a software component, and create a
		#|   logger for it.  Child modules may access this logger using the
		#|   syntax "from . import _logger" rather than calling getLogger().
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

_component = path.basename(__path__[0])		# Our package name.
_logger = getComponentLogger(_component)	# Create the component logger.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                   END OF FILE:    infrastructure/__init__.py
#|==============================================================================