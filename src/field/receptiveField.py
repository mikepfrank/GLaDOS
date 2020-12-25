#|==============================================================================
#|				  TOP OF FILE:	  field/receptiveField.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
"""

# receptiveField.py
#
#	Please note that conceptually, this module is considered part of the AI,
#	since some of its basic properties, such as its size, are associated with
#	the AI.  However, we place it in its own package since much the rest of the 
#	system talks to it directly (and to the rest of the AI, less directly).
#
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


from	os	import path

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	1.2.1. The following modules, although custom, are generic 
			#|		utilities, not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# A simple decorator for singleton classes.
from 	infrastructure.decorators	import	singleton

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.


			#|----------------------------------------------------------------
			#|	1.2.2. The following modules are specific to GLaDOS.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from 	mind.aiActions			import 	ActionByAI_
	# This is an abstract class for actions that we might want to take,
	# which should then be automatically handled by the Supervisor.

			#|----------------------------------------------------------------
			#|	1.2.3. The following modules are "sibling" modules to the 
			#|		present module within its package.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	.placement					import	Placement		
	# A placement specifies an initial location for new slots on the field.

from	.fieldElement				import	FieldElement_
	# Field elements are conceptually independent parts of the field display.

	#|==========================================================================
	#|
	#|	2. Globals.												  [code section]
	#|
	#|		Module-level (global) constant and variable data members.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global _DEFAULT_NOMINAL_WIDTH	# Default nominal displayed width of field elements, in characters.
_DEFAULT_NOMINAL_WIDTH	= 60	# Keeping it narrow-ish reduces tokens wasted on decorators.
	# Note that this default may not be respected in all field elements or views.
	# (Does it make more sense conceptually to set this in the window system?)
	# NOTE: We still need to add a config setting to override this.

	#|==========================================================================
	#|
	#|	3. Forward declarations.								  [code section]
	#|
	#|		Forward declarations to classes that will be defined later
	#|		in this module.  (This is mainly only useful for use in type 
	#|		hints; you can't actually construct an *instance* of a class
	#|		at top level until the class has actually been defined.)
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class ReceptiveField_:		pass	# For use in type hints.
	# Abstract base class for receptive fields.

class TheReceptiveField:	pass
	# This singleton anchors the whole module.


	#|==========================================================================
	#|
	#|	4. Classes.												  [code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#	AnnounceFieldExistsAction(ActionByAI) -
#
#		This is a class of action that is taken by the AI as soon as its 
#		receptive field has been created, and is ready for entities outside
#		of itself to begin writing information into it.  Like all actions, 
#		as soon as it gets created and initiated, it gets automatically 
#		processed by the supervisor's ActionProcessor.  This responds 
#		appropriately, for example, by telling the application system that 
#		its windows that want to auto-open can now open themselves on the 
#		field.

class AnnounceFieldExistsAction(ActionByAI_):
	pass
	
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

class FieldElement_: pass	# Forward declaration.

class FieldSlot:
	# Data members:
	#
	#	- A placement designator for this slot, which determines how its
	#		position will be set/maintained within the field ordering.
	#
	#	- An index giving the slot's current sequential position within
	#		the receptive field.
	#
	#	- A reference to the field element that's being held in this slot.
	#
	# Properties:
	#
	#	- Height (in rows). This just comes from the element that's being 
	#		held in the slot.
	#
	# Methods:
	#
	#	- fieldSlot.place() - Tells the field slot to place itself 
	#		appropriately within the given base field data object.
	
	def __init__(
			thisFieldSlot, 
				# How to place the new slot on the field:
			placement:Placement=Placement.SLIDE_TO_BOTTOM,	
				# By default, we slide new slots to the bottom without anchoring 
				# them (thereby displacing pre-placed unanchored slots upwards).
			forElement:FieldElement_=None,	
				# The field element we're creating this slot to hold (if it 
				# exists already).
			field:ReceptiveField_=TheReceptiveField()
		):
		"""
			FieldSlot.__init__()						  [Instance initializer]
			
				This is the instance initialization method that is used in
				constructing field slots (instances of the FieldSlot class).
				
				When a new field slot is created, it is assigned an initial
				placement, specifying how it will be positioned relative to
				other slots in the ordering of field slots (top to bottom).
				
				Later, after the field slot has been constructed, the 
				fieldSlot.place() method, below, can be used to actually
				place it within the field ordering, after which the field
				display should be refreshed.  (But managing the field 
				refreshment is a responsibility of higher-level classes.)
		"""
			# Remember our placement and our element and our field.
		thisFieldSlot._placement = placement
		thisFieldSlot._posIndex = None			# Slot isn't placed yet.
		thisFieldSlot._element = forElement

	def place(thisFieldSlot, 
				# Where to place the slot on the field?
			where:Placement=None, 
				# By default, we'll just use the element's initial placement.
			field=TheReceptiveField()):
		pass

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
		
	def addElement(theBaseFieldData:TheBaseFieldData, 
					element:FieldElement_,
					location:Placement):
		"""
			In this context, an 'element' just means an object that 
			can be displayed in the AI's receptive field.
			
			The 'location' is value of the Placement enumerable, which
			has the following possible values (see placement.py):
			
				PIN_TO_BOTTOM - The element is pinned to the bottom
					of the receptive field (above elements previously 
					pinned to the bottom).  This means it cannot be
					moved from this position in the order by 'normal'
					placement requests.  Examples of elements pinned
					to the bottom:  Prompt, separator.
					
				PIN_TO-TOP - The element is pinned to the bottom of 
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

# In the following design pattern, before designing a singleton class,
# we put as much of that class's functionality as possible into an abstract
# base class, and derive the singleton class from it.  This will help us to 
# identify the amount of re-coding effort that will be needed later if we 
# need to change this class to no longer be a singleton.

class ReceptiveField_:

	"""Abstract base class from which to derive the receptive field 
		singleton class."""
	
	def refreshViews(thisReceptiveField):
		thisReceptiveField._aiFieldView.render()
		thisReceptiveField._humanFieldView.render()
	
	def addElement(thisReceptiveField, elem:object):
	
			# First just add the element.
		thisReceptiveField._baseFieldData.addElement(elem)
		
			# Now, automatically refresh the field views.
		thisReceptiveField.refreshViews()
			

@singleton
class TheReceptiveField(ReceptiveField_):
	
	"""Singleton class for the entire receptive field management system."""
	
	def __init__(inst, fieldSize:int, 
		nominalWidth:int):
	
		"""fieldSize - Specifies the nominal size of the receptive field in tokens."""
	
		_logger.info("Receptive field:  Initializing with field size = {fieldSize} tokens.")
	
			# Create the base field data object & store it.
		baseFieldData 			= BaseFieldData(fieldSize)
		inst._baseFieldData		= baseFieldData
		
			# Create and store field views for the AI & for humans.
		inst._aiFieldView		= inst.TheAIFieldView(baseFieldData)
		inst._humanFieldView	= inst.HumanFieldView(baseFieldData)

			# Create the "field topper" element, which automatically pins
			# itself to the very top edge of the receptive field.
		TheFieldHeader()
		
			# Create the "input area" element, which automatically pins 
			# itself to the very bottom edge of the receptive field.
		TheInputArea()
		
			# Create the "prompt separator" element, which separates the
			# "context" part of the receptive field (above the separator)
			# from the "prompt" part of the receptive field (below the
			# separator). It automaticaly pins itself to the bottom of the
			# receptive field (just below the input box we just placed).
		ThePromptSeparator()
