# mindStream.py

# The cognitive stream or "mind stream" corresponds roughly to the
# AI's "stream of consciousness".  It is a time-ordered sequence of
# "thoughts" and "perceptions" that float into the AI's sphere of
# awareness.
#
# The cognitive stream is structured as a sequence of "events."
# These are defined in the events.event module.
#
# The most common type of event (and perhaps the only type, initially)
# is the TextEvent.  It is very simple:  It has a creation date, an
# author entity, a textual content, and a display format.
#
# The typical appearance of a text event is like a prompt followed by
# the event content.  The prompt appears similar to the A.I.'s own input
# prompt.  The idea is that this cues the A.I. in to the fact that events
# in the system are being authored by a number of different entities, and
# it is one of them.
#
# Events can also include things like window snapshots, which may have
# a different appearance.
#
# The main CognitiveStream class in this module maintains the stream of
# events in memory.  Later, it will spool its data to more persistent 
# storage maintained by the 'history' package.  Eventually, we will give
# the AI the ability to scroll back through and review its own cognitive
# stream, back to the very start of its history buffer.
#
# The memory facility (maintained by the 'memory' package) will contain
# a more heterogenerous database of archival information accessible by 
# the AI.  Perodically, as the history file grows very large, it may be
# migrated out in chunks to the memory archives to make it easier to 
# manage.
#
# Before implementing all this, we may provide some simple backing store
# for the cognitive stream in a simple JSON file or some such.

from os import path
from 	infrastructure.logmaster 	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger		# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))				# Our package name.
_logger = getComponentLogger(_component)						# Create the component logger.


from infrastructure.decorators import singleton

from entities.entity import System_Entity_

from events.event import (
		BriefEventFormat,
		#SecondEventFormat,
		#DateEventFormat,
		TextEvent
	)

class Action_: pass
class TheCognitiveSystem: pass

class TheCognitiveStream: pass
@singleton
class TheCognitiveStream:

	"""This is a singleton class for maintaining the AI's cognitive
		stream.  It is organized as an (ideally time-ordered) sequence
		of events."""

	#defaultEventFormat = SecondEventFormat		# Gladys finds this distracting.
	defaultEventFormat = BriefEventFormat
		# Default format for new events.

	def __init__(newCogStream:TheCognitiveStream, cogSys:TheCognitiveSystem):

		_logger.debug("[Mind/Init] Initializing the AI's cognitive stream...")

		cs = newCogStream

		cs._mind = cogSys	# Pointer to top-level mind object.
		cs._events = []		# Empty list of events initially.
		cs._format = cs.defaultEventFormat	# Format for new events.


	@property
	def mind(thisCogStream:TheCognitiveStream):

		"""Gets a reference to the larger cognitive system that this
			cognitive-stream subsystem is a part of."""

		return thisCogStream._mind


	def addEvent(thisCogStream:TheCognitiveStream, textEvent:TextEvent):

		"""This adds the given event to (the end of) our cognitive stream."""

		cs = thisCogStream
		mind = cs._mind

		events = cs._events
		events.append(textEvent)
		
			# At this point, also make sure the higher-level mind object
			# becomes aware of this addition to our cognitive stream.
		mind.noticeEvent(textEvent)


	def noticeAction(thisCogStream:TheCognitiveStream, action:Action_):

		"""This causes the cognitive stream to become 'aware' of the
			given action which is now executing.  We respond to this
			by constructing an event object representing the event of
			this action's execution, and inserting it into our stream
			of events."""

		cs = thisCogStream
		mind = cs.mind	    # Our entire over-arching cognitive system.

		author = action.conceiver
			# We consider the action to have been authored by the entity
			# that originally conceived it.

		# This causes us to ignore system actions.
		#if isinstance(author, System_Entity_):
		#	return

		creationTime = action.conceptionTime
			# We consider the event to have been created at the time that
			# the action was originally conceived.

		text = action.text
			# We ask the action itself to provide us its own text.  How this
			# is generated, precisely, may depend on the class of action.

		textEvent = TextEvent(text, author, cs._format, creationTime, action)
			# This creates the new text-event object representing the event
			# of the action's execution.

		cs.addEvent(textEvent)
			# Go ahead and add this event to our cognitive stream.  (This
			# will, as a consequence, also make it appear on our receptive
			# field.)

