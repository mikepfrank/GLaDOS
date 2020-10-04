#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|  FILE NAME:      events/author.py              		[Python 3 module file]
"""
	MODULE NAME:	events.author
	
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
	
