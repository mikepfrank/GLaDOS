#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|  FILE NAME:      events/event.py              		[Python 3 module file]
"""
	MODULE NAME:	events.event
	
	DESCRIPTION:
	
		This is the core module of the "events" package; it provides the
		definition of a class Event, which keeps track of information such
		as the date/time and source of the event.  There are also classes
		for working with event formats, which determine how Event objects
		are translated to text.  The AI can select how events that it is
		viewing in its receptive field will be formatted.
		

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

class Event: pass	# Forward declaration just so we can use it as a type descriptor.

class EventFormat:
	"""Abstract superclass for event formats."""
	# Subclasses should implement the display(event) class method.
	pass
	
class PlainEventFormat:
	
	"""A plain event format that only shows the raw text of the event, nothing else."""

	@classmethod
	def display(thisClass,event):
		return event.text

class PromptedEventFormat:		# Abstract class for event formats that begin with a prompt-like structure

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
		return thisClass.prompt() + event.text;

class BriefEventFormat(PromptedEventFormat):

	@classmethod
	def prompt(thisClass,event):
		return f"{event.author}> "
		
class FullEventFormat:

	@classmethod
	def prompt(thisClass, event):
		return f"{event.creationTime.strftime('%Y-%m-%d %H:%M:%S')} | {event.author}> "

	
	#|--------------------------------------------------------------------------
	#|	events.event.Event								[module public class]
	#|
	#|		This is a class whose instances keep track of the date, time,
	#|		and creator of particular textual events in the AI's memory.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
class Event:
	
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

	def __init__(inst, text:str=None, when:datetime=None, author:Entity_=None):
	
			# Default the creation time to right now if not provided.
			
		if when=None:
			when = datetime.now()
		
		inst.creationTime	= when
		inst.creator		= author
		inst.text			= text
	
	def updateTime(thisEvent):
		thisEvent.creationTime	= datetime.now()
	
	def display(inst, format:EventFormat):
		format.display(inst)
	