# receptiveField.py

# 	This module implements the input to the AI's main receptive field; 
# 	that it, it displays everything that the A.I. can "see."  This generally
# 	consists of the following:
#
#		1. Any windows that are anchored to the top of the receptive field.
#
#		2. As much as possible of the A.I.'s recent cognitive stream.  This 
#			consists of a sequence of events, labeled with timestamp and author.
#			some events may be window snapshots, or floating windows.  Most 
#			events will simply be blocks of text.
#
#		3. Any windows that are anchored to the bottom of the receptive field.
#
#		4. A separator bar with reminders of important top-level commands.
#
#		5. A prompt or partial event, with the current time and the A.I.'s 
#			name.  Hopefully it responds with a command or text that it wants
#			to add to its cognitive stream.
#
#	The base receptive field can render itself to two different output buffers:
#
#		1. The view of the field (raw field text data) that will be sent to the 
#			AI.  This has the feature that the line length is not limited.
#
#		2. The human-readable field.  This is distinguished by being limited
#			in width for display purposes; overlong lines are wrapped around.
#
#			Further, the human-readable field can be scrolled (by a human
#			terminal user), and it can also be rendered in two-column format,
#			for purposes of displaying more content on wide terminals.
#

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	The following modules, although custom, are generic utilities,
			#|	not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton


	#|==========================================================================
	#|
	#|	3. Classes.												  [code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Classes:
#
#	FieldSlot			- A "slot" in the display order for the receptive field.
#							A slot holds an object that will be displayed at that
#							spot in the field.  Slots can be rearranged in several 
#							ways:  Moved to the top of the field, moved to the 
#							bottom, anchored to the top (after all other slots 
#							anchored to the top), anchored to the bottom (before 
#							all other slots anchored to the bottom.  A slot can 
#							also be marked as "adjustable", which means that when 
#							the field is underfull, the field will tell the slot 
#							to expand itself, and when the field is overfull, the 
#							field will tell the slot to shrink itself.  Slots can
#							also be added and removed (e.g. when a window opens or
#							closes.  A slot can also be "pinned" to the top or
#							bottom of the field, meaning it can't be moved (normally),
#							or "anchored" to the top or bottom of the field, meaning
#							that it won't normally be displaced by slots that are 
#							only slid to the top or bottom.
#
#	TheBaseFieldData		- The base data object containing everything that's 
#							intended to be viewed by the A.I. in its 
#							receptive field.
#
#	FieldView_			- Base class for rendered views of the receptive field.
#
#	AI_FieldView		- The view of the field to be sent to the AI.
#
#	Human_FieldView		- A rendering of the field's contents for purposes 
#							of human viewing.
#
#	TheReceptiveField	- Singleton; the entire receptive field system as a whole.

class TheBaseFieldData: pass	# Forward declaration.

@singleton
class TheBaseFieldData:
	#---------------------------------------------------------------------------
	"""
	TheBaseFieldData 							 [module public singleton class]
	
		This singleton class keeps track of the raw data that is currently
		visible in the AI's receptive field.  This consists of a sequence 
		of objects that, when rendered, are aspirationally supposed to fit 
		in the field.
		
		In practice, the fit may not be exact.  The base field data object 
		can report to using objects whether its currently overfull or 
		underfull, and by how much.  Those objects can then potentially 
		adjust how much information they are currently displaying, in an 
		attempt to optimally fill the field.
		
		The field data is organized as a sequence of "slots", where each 
		slot can hold one object.
	
	"""
	def __init__(theBaseFieldData:TheBaseFieldData, maxTokens:int):
		inst._maxTokens = maxTokens
		inst._slots = []
		
	def addElement(theBaseFieldData:TheBaseFieldData, element:object,
					location:string):
		"""
			In this context, an 'element' just means an object that 
			can be displayed in the AI's receptive field.
			
			The 'location' string has the following possible values:
			
				PIN-TO-BOTTOM - The element is pinned to the bottom
					of the receptive field (above elements previously 
					pinned to the bottom).  This means it cannot be
					moved from this position in the order by 'normal'
					placement requests.  Examples of elements pinned
					to the bottom:  Prompt, separator.
					
				PIN-TO-TOP - The element is pinned to the bottom of 
					the receptive field (below elements previously 
					pinned to the top).  Examples of elements pinned 
					to the top:  Info window.
					
				MOVE-TO-BOTTOM - The element is moved to the bottom of
					the receptive field, just above all of the elements
					pinned to the bottom.  Examples of elements moved
					to the bottom:  The current active application 
					window.  After moving it there, it is anchored.
					
				MOVE-TO-TOP - The element is moved to the top of the 
					receptive field, just below all of the elements 
					pinned to the top.  Examples of elements moved to
					the top:  A window that the AI doesn't want to 
					focus its attention on, but wants to remain visible.
					After being moved, it is anchored.
					
				ANCHOR-TO-BOTTOM - This is like MOVE-TO-BOTTOM but the
					element's location is just above all elements that
					were only moved to the bottom.
					
				ANCHOR-TO-TOP - This is like MOVE-TO-TOP but the element's
					location is just below all elements that were only
					moved to the top.
					
				SLIDE-TO-BOTTOM - Just above all elements pinned  
					or anchored to the bottom, but the new element is not 
					anchored.  That is, the element can be displaced by a 
					new SLIDE-TO-BOTTOM.  This is the usual mode for 
					adding new elements: All previously added elements are 
					displaced upwards.
					
				SLIDE-TO-TOP - Similar to SLIDE-TO-BOTTOM, but for the top.
		"""
		pass
		
	def measure(inst):
		"""Measure the size of the field in tokens.  This works by
			Asking the AI's field view (which is the real view) to
			render itself, then counting its size in tokens."""
		
		aiFieldView = TheAIFieldView()
		aiFieldView.render()
		
	

class FieldView_:

	"""Abstract base class from which to derive more specific views of the 
		receptive field."""
		
	def __init__(inst, base):
		inst._baseFieldData = base
		inst._textBuffer = TextBuffer()
		
	# Subclasses should define .render() to render themselves from the
	# base data.


@singleton
class TheAIFieldView(FieldView_):
	
	"""Derived class for views of the receptive field to be sent to AIs."""
	
	def render(inst):
		# This works by iterating through elements in the base data,
		# and adding their text to an unbounded-length text field.
		pass
		
	def nTokens(inst):
		"""Returns the number of tokens in the current field view."""
		# This works by concatenating together all the rows of 
		# the text buffer, and then we run that
		# through the tokenizer.
		pass


# Not a singleton because maybe we have several humans connected to the
# system viewing the field and maybe they have their views configured 
# slightly differently.

class HumanFieldView(FieldView_):
	"""Derived class for views of the receptive field to be shown to
		human users."""
	def render(inst):
		pass

@singleton
class TheReceptiveField:
	
	"""Singleton class for the entire receptive field management system."""
	
	def __init__(inst, fieldSize:int):
		"""fieldSize - Specifies the nominal size of the receptive field in tokens."""
	
		_logger.info("Receptive field:  Initializing with field size = {fieldSize} tokens.")
	
			# Create the base field data object & store it.
		baseFieldData 			= BaseFieldData(fieldSize)
		inst._baseFieldData		= baseFieldData
		
			# Create and store field views for the AI & for humans.
		inst._aiFieldView		= inst.TheAIFieldView(baseFieldData)
		inst._humanFieldView	= inst.HumanFieldView(baseFieldData)
	
	def refreshViews(inst):
		inst._aiFieldView.render()
		inst._humanFieldView.render()
	
	def addElement(inst, elem:object):
	
			# First just add the element.
		inst._baseFieldData.addElement(elem)
		
			# Now, automatically refresh the field views.
		inst.refreshViews()