#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|  FILE NAME:      events/event.py              		[Python 3 module file]
"""
	MODULE NAME:	events.event
	
	DESCRIPTION:
	
		This is the core module of the "events" package; it provides the
		definition of a class TextEvent, which keeps track of information 
		such as the date/time and source of an event consisting of a piece
		of text.  There are also classes for working with event formats, 
		which determine how TextEvent objects are translated to actual 
		displayed text.  The AI can select how events that it is viewing 
		in its receptive field will be formatted.
		

"""
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


#|==============================================================================
#|  Module imports.                                           [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from datetime import datetime
	# Needed for tracking the creation date and time of events.

#from .author import Author	# Abstract superclass of author objects.
from entities.entity import Entity_	# Abstract superclass for entity objects.

#|==============================================================================
#|  Module public classes.                               		[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|==========================================================================
	#| The following classes are for defining "event formats;" these control
	#| how an event gets displayed within the AI's receptive field.  If this 
	#| section gets large, we could move it to a separate file EventFormat.py.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class TextEvent: pass	# Forward declaration just so we can use it as a type descriptor.

class TextEventFormat:
	"""Abstract superclass for event formats."""
	# Subclasses should implement the display(event) class method.
	pass
	
class PlainEventFormat(TextEventFormat):
	
	"""A plain event format that only shows the raw text of the event, nothing else."""

	@classmethod
	def display(thisClass, event):
		return event.text

	@classmethod
	def promptLen(thisClass, event):
		return 0

class PromptedEventFormat(TextEventFormat):		# Abstract class for event formats that begin with a prompt-like structure

	"""Abstract superclass for event formats that begin with a prompt-like prefix.
		The .prompt() class method in these formats is useful for prompting the AI."""

	#/--------------------------------------------------------------------------
	#| Interface implementation requirements for concrete subclasses.
	#|
	#| Concrete subclasses should implement the following methods:
	#|
	#|		.prompt(thisClass, event)							[class method]
	#|
	#|			Returns a string which is in the style of a prompt that
	#|			should appear as a prefix at the start of the action 
	#|			display string.
	#|		
	#\--------------------------------------------------------------------------
	
		#|----------------------------------------------------------------------
		#|	PromptedEventFormat.display()						[class method]
		#|
		#|		In a PromptedEventFormat, we display an event by just 
		#|		displaying its prompt followed by the event text.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	@classmethod
	def display(thisClass, event):
		return thisClass.prompt(event) + event.text
	
	@classmethod
	def promptLen(thisClass, event):
		return len(thisClass.prompt(event))

class BriefEventFormat(PromptedEventFormat):

	@classmethod
	def prompt(thisClass,event):
		return f"{event.creator}> "
		
class FullEventFormat(PromptedEventFormat):

	@classmethod
	def prompt(thisClass, event):
		return f"{event.creationTime.strftime('%Y-%m-%d %H:%M:%S')} ({event.creator})> "

	
	#|--------------------------------------------------------------------------
	#|	events.event.Event								[module public class]
	#|
	#|		This is a class whose instances keep track of the date, time,
	#|		and creator of particular textual events in the AI's memory.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
class TextEvent: pass

class TextEvent:
	
	"""Class for objects that track the date, time, and creator of a 
		given chunk of text stored in the AI's history or memory."""

	#/--------------------------------------------------------------------------
    #|  Instance public data members for class Event. (See API docs.)
    #|
    #|      .creationTime	[datetime]	- When was the event first created.
	#|		.creator		[Author]	- The entity that wrote this event.
	#|		.text			[string]	- The actual text data of this event.
	#|
	#\--------------------------------------------------------------------------

	def __init__(inst, text:str=None, when:datetime=None, author:Entity_=None,
		defaultFormat=None):
	
			# Default the creation time to right now if not provided.
			
		if when is None:
			when = datetime.now()
		
		inst.creationTime	= when
		inst.creator		= author
		inst.text			= text
		inst.defaultFormat	= defaultFormat
	
	def updateTime(thisEvent):
		thisEvent.creationTime	= datetime.now()
	
	def display(inst, format:TextEventFormat=None):
	
		"""Returns a complete string for displaying the event, using
			the given format, or the event's default format if the
			format is not specified."""
	
		if format is None:
			format = inst.defaultFormat
	
		return format.display(inst)

	def promptLen(thisEvent:TextEvent, format:TextEventFormat=None):
		"""Returns the length of the prompt portion of the event."""

		event = thisEvent

		if format is None:
			format = event.defaultFormat
	
		return format.promptLen(event)
