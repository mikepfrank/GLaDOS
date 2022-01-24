#|==============================================================================
#|						TOP OF FILE:   	events/author.py
#|------------------------------------------------------------------------------
#|
#|	FILE NAME:      events/author.py               [Python 3 module source code]
#|	================================
#|
#|		FULL PATH:      $GIT_ROOT/GLaDOS/src/appdefs.py
#|		MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
#|
#|	FILE DESCRIPTION:
#|	=================
#|
#|		This file defines the 'author' module within the 'events' package.
#|		(See the module docstring below for more details.)
#|
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	MODULE NAME:	events.author							   [Python 3 module]
	=============================

		IN PACKAGE:		events - Cognitive event records.

		SYSTEM NAME:    GLaDOS (Generic Lifeform and Domicile Operating System)
		APP NAME:       GLaDOS.server (GLaDOS server application)
		SW COMPONENT:   GLaDOS.logging (GLaDOS logging framework)

		CODE LAYER:		0 (bottommost layer; no imports of custom modules)
	
	
    MODULE DESCRIPTION:
    -------------------


	
	DESCRIPTION:
	
		This module defines classes for designating the author (creator,
		source) of a given event.  There are subclasses for representing
		the AI itself, for representing specific human beings that the 
		AI may be interacting with, for representing various automated 
		processes that the AI may be interacting with, and so forth.
		
"""
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#|==============================================================================
#|  Global constants.                                           [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|----------------------------------------------------------------------
    #| These are the names you get if you do 'from events.author import *'. 
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__
__all__ = [
	'Author',			# Abstract superclass of author classes.
	'HumanAuthor',		# Represents some real-world human being.
	'AIAuthor',			# Represents some AI persona or engine.
	'ProcessAuthor',	# Just some simple dumb automated program.
    ]

#|==============================================================================
#|  Module public classes.                               		[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Author:

	"""This is the top-level abstract superclass of classes in the
		Author hierarchy.  One should not instantiate this class 
		directly, but only one of its subclasses such as 
		HumanAuthor, AIAuthor, or ProcessAuthor.
	"""
	#/--------------------------------------------------------------------------
	#|	Private data members of the Author class:
	#|
	#|		_name [string] - A short text string identifying this Author.
	#|		_fullName [string] - A longer, more descriptive name of this author.
	#|
	#\--------------------------------------------------------------------------
	
	def __init__(inst, name:str=None, fullName:str=None):
	
		inst._name = name
		inst._fullName = fullName

	@property
	def name(self):
		return _name
		
	@property
	def fullName(self):
		return _fullName
		
	def __str__(self):
		return self.name
	
class HumanAuthor(Author):
	
	def __init__(inst, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
class AIAuthor(Author):

	def __init__(inst, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
class ProcessAuthor(Author):

	def __init__(inst, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
