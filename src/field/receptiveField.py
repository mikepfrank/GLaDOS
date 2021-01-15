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

from	events.event			import	TextEvent

from	text.buffer				import	TextBuffer

from	tokenizer.tokenizer		import	countTokens

from	entities.entity			import	AI_Persona
	# We need to be given an instance of AI_Persona in order to appropriately
	# configure the prompt string for it in the input area field element.

from 	mind.aiActions			import 	ActionByAI_
	# This is an abstract class for actions that we might want to take,
	# which should then be automatically handled by the Supervisor.

			#|----------------------------------------------------------------
			#|	1.2.3. The following modules are "sibling" modules to the 
			#|		present module within its package.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	.placement					import	(
	
			# Types.
		Placement,		# A placement specifies an initial location for new slots on the field, or a persistent placement.
		
			# Constants (placement values).
		PINNED_TO_BOTTOM, PINNED_TO_TOP, MOVE_TO_BOTTOM, MOVE_TO_TOP,
		ANCHORED_TO_BOTTOM, ANCHORED_TO_TOP, SLIDE_TO_BOTTOM, SLIDE_TO_TOP,
		FLOATING,
		
			# Constant structures.
		GRAVITY_MAP, MODE_MAP
		
	)
	

from	.fieldSettings				import	TheFieldSettings, TheFieldSettingsModule
	# TheFieldSettings - This uninstantiated class object holds our settings in class variables.
	# TheFieldSettingsModule - A settings module for plugging into the settings facility.


	# Field elements are conceptually independent parts of the field display.

from .fieldElement import (

	FieldSlot,
	FieldElement_,
	TheFieldHeader,
	ThePromptSeparator,
	TheInputArea,
	TextEventElement,

)
	

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

class ConsoleClient: pass

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

class _TheBaseFieldData:		pass
	# Singleton for the core field data structure.

	#|==========================================================================
	#|
	#|	4. Classes.												  [code section]
	#|
	#|		Classes defined by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class FieldElement_: pass	# Forward declaration.


#	_TheBaseFieldData		- The base data object containing everything that's 
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
class _TheBaseFieldData:
	#---------------------------------------------------------------------------
	"""
	_TheBaseFieldData 								   [private singleton class]
	
		This singleton class keeps track of the raw data that is currently
		visible in the AI's receptive field.  This consists of a sequence 
		of objects that, when rendered, are aspirationally supposed to fit 
		in the field.
		
		In practice, the fit may not be exact.  The base field data object 
		can report to its customers whether its currently overfull or 
		underfull, and by how much.  Those objects can then potentially 
		adjust how much information they are currently displaying, in an 
		attempt to optimally fill the field.
		
		The field data is organized as a sequence of "slots", where each 
		slot can hold one object.
	
	"""
	def __init__(theBaseFieldData:_TheBaseFieldData, maxTokens:int):
	
		base = theBaseFieldData
	
		base._maxTokens = maxTokens
		base._slots = []
		base._nSlots = 0	# Zero slots on the field initially.


	@property
	def slots(this):
		return this._slots


	def insertSlotAt(base:_TheBaseFieldData, slot:FieldSlot, pos:int):
		"""Inserts a slot at a given position in the base field data."""
		base.slots.insert(pos, slot)		# Native Python list method.
		base._nSlots = base._nSlots + 1		# Increment number of slots.


	def move(base:_TheBaseFieldData, slot:FieldSlot, gravity:str, soft=False):
		
		"""Moves the slot to one side of the field (top or bottom, depending on 
			whether the gravity is 'up' or 'down'), excluding elements already 
			pinned (or anchored, if soft is True) to that side."""
		
		#/======================================================================
		#| The algorithm is to start at the extreme point of the side that we
		#| are heading towards, and move away from it (that is, moving against
		#| our gravity) until we have no more pinned (and possibly anchored) 
		#| elements to move past.  This way, when we plop ourselves down there,
		#| the existing pinned (and possibly anchored) elements aren't disturbed.
		#| 
		#| An alternative algorithm would be to start from the opposite side 
		#| and then move in the direction of gravity until we get to an obstacle, 
		#| but, assuming that the great majority of slots are going to be 
		#| floating, that could take a lot longer.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		
		slots = base.slots
		length = len(slots)
		
		pos 		= 0 	if gravity=='up' else length-1	# Extreme position.
		direction 	= +1 	if gravity=='up' else -1		# Opposite gravity.
		
			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| The following loop searches for the position that we're supposed
			#| to end up in.  If the pos >= 0 condition fails, when we went too
			#| far up.  If the pos < length condition fails, then pos=length and
			#| we went down off the end of the existing slot list.  We can also
			#| break out of the loop earlier (as soon as we get past all the 
			#| slots that we need to get past.
			
		while pos >= 0 and pos < length:
		
			# "He" = The existing slot at this position in the field data.
			
			hisPlacement	= slots[pos].placement			# Get his placement.
			hisMode 		= MODE_MAP[hisPlacement]		# Get his mode.
			hisGravity		= GRAVITY_MAP[hisPlacement]		# Get his gravity.

				#|--------------------------------------------------------------
				#| First, if that guy's gravity doesn't match ours, then we know 
				#| he's past the slots that we needed to get past, so, break out 
				#| of the loop.  Note this 'if' also triggers if we get into the 
				#| floating zone (where the gravity value is None).

			if hisGravity != gravity:
				break

				#|--------------------------------------------------------------
				#| Next, if we're doing a hard move (i.e., a pin or a normal 
				#| move) and that guy's mode is anchored, then we know he's past 
				#| the guys we needed to get past, so, break out of the loop.
				
			if not soft and hisMode == 'anchored':
				break
			
			#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| If we get here, then either we're doing a soft move (anchor or
			#| slide) and haven't yet reached the floating zone, or we're doing 
			#| a hard move, but we're still in the area that's already pinned to 
			#| our side.  In either case, we need to keep going.
			
			pos = pos + direction
		
		#__/ End while still on the field.
		
		
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| OK, by the time we get here, we have successfully moved past all of 
		#| the elements that we needed to get past to find our position.  So now,
		#| just insert us in the slots list at the position we just determined.
		#| (The only subtlety is because "insert" really means "insert before.")
		
		# Insert this slot just past the elements we're not displacing.
		if gravity=='down':
			pos = pos + 1	# This goes back down one, since we went too far up.
		slot.insertAt(pos)
		
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Now we need to re-index all the slots after the current one, because
		#| their indices have changed.
		
		for i in range(pos+1, length+1):
			slots[i]._posIndex = i
			
	#__/ End instance method baseFieldData.move().
	
	
	def slide(base:_TheBaseFieldData, slot:FieldSlot, gravity:str):
	
		"""A 'slide' simply means a 'soft' move, meaning that we don't 
			displace previously anchored elements."""
			
		base.move(slot, gravity, soft=True)
	
	def place(base:_TheBaseFieldData, slot:FieldSlot):
	
		where	= slot.placement
		mode	= slot.mode
		gravity = slot.gravity
	
		"""This tells the base to please insert the given slot into
			its slot list, using the specified placement designation."""
	
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| 'Pin' or 'move' requests are "hard moves." That is, they are strong
		#| enough to even shove their way past any elements that are "anchored," 
		#| meaning that their gravity is normally weighing them in place.
		
		if mode == 'pinned' or mode == 'move':
			# Move the slot roughly to be up against the already-pinned elements.
			base.move(slot,gravity)
		
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| 'Anchor' and 'slide' requests are "soft moves," which means, they are
		#| gentle enough that they don't disturb any already-anchored elements.
		
		elif mode == 'anchored' or mode == 'slide':
			# Move the slot gently to be up against already-pinned-or-anchored elements.
			base.slide(slot,gravity)
		
		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Next, 'moved' elements remain 'anchored', while elements that were
		#| only 'slid' into place are subsequently allowed to float.
		
			# Figure out what the persistent placement of this slot should be.
		persistentPlacement = where.persistsAs
		
			# Set its placement to the new value. (This also updates its mode.)
		slot.placement = persistentPlacement	
				# (This invokes a setter method to update the slot's mode.)

	#__/ End instance method theBaseFieldData.place().
	
	
	def addElement(base:_TheBaseFieldData, 
					element:FieldElement_,
					location:Placement):
		
		"""Adds the given element to the base field using the given placement
			specifier. (Note that in this context, an 'element' just means any 
			object that can be displayed in the AI's receptive field.)  Also:
			If the element was already placed, it gets re-placed."""
		
			# Get the element's slot.
		slot = element.slot
		
			# Tell the slot to re-place itself at the new location.
		slot.replace(location)
	
	
	
	def measure(inst):
		"""Measure the size of the field in tokens.  This works by
			Asking the AI's field view (which is the real view) to
			render itself, then counting its size in tokens."""
		
		aiFieldView = TheAIFieldView()
		aiFieldView.render()
		
	

class FieldView_:

	"""Abstract base class from which to derive more specific views of the 
		receptive field."""
		
	def __init__(inst, base:_TheBaseFieldData):

		"""Instance initializer for FieldView_ and its subclasses.
			The sole argument is a pointer to the base field data 
			structure that this is a view for."""

		inst._baseFieldData = base
		#inst._textBuffer = TextBuffer()

		inst._data = []		# Empty list of data items (strings).
		inst._nChars = 0	# No characters initially.
		inst._nTokens = 0	# No tokens initially.

	@property
	def baseData(this):
		return this._baseFieldData

	# Subclasses should define .render() to render themselves from the
	# base data.


class TheAIFieldView: pass

@singleton
class TheAIFieldView(FieldView_):
	
	"""Derived class for views of the receptive field to be sent to AIs."""
	
	def render(view:TheAIFieldView):
		# This works by iterating through elements in the base data,
		# and just adding their images as items in the data set.
		
		base = view.baseData	# Get the base data.
		slots = base.slots		# Get the list of field slots.
		
		data = []	# Initialize data array to empty list.
		for slot in slots:
			element = slot.element		# Get the field element.
			image = element.image		# Get that element's (text) image.
			data.append(image)			# Append it to our list.
			
		text = ''.join(data)		# Here's the data as one huge string.

		view._data = data			# Remember the data array.
		view._text = text
		view._nChars = None			# Mark nChars as not-yet-computed.
		view._nTokens = None		# Mark nTokens as not-yet-computed.
	
		_logger.debug(f"aiFieldView.render(): Just rendered field view as: [[{text}]]")

	@property
	def data(inst):
		return inst._data

	def text(inst):
		"""Returns the field view as one huge text string."""
		text = inst._text
		if text is None:		# Not computed yet?
			data = inst.data
			inst._text = text = ''.join(data)
		return text

	def nChars(inst):
		"""Returns the number of characters in the current field view."""
		nChars = inst._nChars
		if nChars is None:		# Not calculated yet?
			text = inst.text()
			inst._nChars = nChars = len(text)
		return nChars
		
	def nTokens(inst):
		"""Returns the number of tokens in the current field view."""
		# This works by concatenating together all the rows of 
		# the text buffer, and then we run that
		# through the tokenizer.
		nTokens = inst._nTokens
		if nTokens is None:		# Not calculated yet?
			text = inst.text()	# Put together the complete text.

			_logger.debug(f"About to count tokens in text: [{text}]")

			inst._nTokens = nTokens = countTokens(text)
		return nTokens
		
		
# Not a singleton because maybe we have several different humans connected
# to the system viewing the field and maybe they each have their views
# configured slightly differently.

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
	
	def __init__(theReceptiveField:TheReceptiveField, 
			entity:AI_Persona,		# Caller must specify an AI persona entity.
			fieldSize:int=None, 	# If supplied, this overrides config data.
			nominalWidth:int=None,	# If supplied, this overrides config data.
		):
		
		"""Arguments:
		
			entity - This entity represents the AI's persona.
		
			fieldSize - Specifies the maximum size of the receptive field in tokens.
			
			nominalWidth - Specifies the nominal width of the receptive field in 
				(assumed) fixed-width character columns.
		
		"""
	
		field = theReceptiveField

		field._console = None	# The console client is not yet connected to us.

			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| 1. The first part of receptive field initialization is to con-
			#| figure all of our parameter settings.  For non-provided argu-
			#| ments, we retrieve their values from the current field settings; 
			#| but for arguments that were provided, we use them to update the 
			#| current field settings.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
			
			# First, configure all of the default settings for the field facility.
		settings = TheFieldSettings.config()
		
		if fieldSize is None:
			fieldSize = TheFieldSettings.maxSize
		else:	# Change the maxSize setting to the value provided.
			TheFieldSettings.maxSize = fieldSize
			#TheFieldSettings.updateMaximumSize(fieldSize)	# Don't need this yet.
		
		if nominalWidth is None:
			nominalWidth = TheFieldSettings.nominalWidth
		else:
			TheFieldSettings.nominalWidth = nominalWidth
			#TheFieldSettings.updateNominalWidth(nominalWidth)	# Don't need yet
	
		_logger.info("[Receptive Field] Initializing with the following settings:")
		_logger.info(f"    Field size = {fieldSize} tokens.")
		_logger.info(f"    Nominal width = {nominalWidth} characters.")
	
			# Stash the important settings in instance data members.
		field._fieldSize		= fieldSize
		field._nominalWidth		= nominalWidth
	
			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| 2. Next, we initialize core sub-structures. Primarily, these are
			#| (a) the base field data object, which maintains the list of dis-
			#| played field elements; and (b) the AI's field view, which renders
			#| the field in a format that can be given to the AI, and that also
			#| can be easily be displayed on the console.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
		_logger.debug("[Receptive Field] Creating base field data object...")
	
			# Create the base field data object & store it.
		baseFieldData 			= _TheBaseFieldData(fieldSize)
		field._baseFieldData	= baseFieldData
		
		_logger.debug("[Receptive Field] Creating the AI's field view...")
	
			# Create and store field views for the AI & for humans.
		field._aiFieldView		= TheAIFieldView(baseFieldData)
		#field._humanFieldView	= HumanFieldView(baseFieldData)


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| 3. Third, we create various initial elements of our field display.
			#| These automatically place themselves on the field.  Later on, when
			#| we are connected to the console, it will show these to the human
			#| operator. They will also be shown to the AI in its main loop.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		_logger.info("[Receptive Field] Creating initial field elements...")

				#|--------------------------------------------------------------
				#| Create the "field header" element, which automatically pins
				#| itself to the very top edge of the receptive field.
				
		_logger.debug("[Receptive Field] Creating the field header element...")
	
		field._fieldHeader	= TheFieldHeader(field)
		
				#|--------------------------------------------------------------
				#| Create the "input area" element, which automatically pins 
				#| itself to the very bottom edge of the receptive field.
				
		#_logger.debug("[Receptive Field] Creating the input area element...")
	
		field._inputArea	= TheInputArea(field, entity)
			# We pass in the entity for the AI persona because its entity-id
			# (e.g., "Gladys") will be displayed in the prompt, to remind the
			# AI which persona it's supposed to be responding as.
		
				#|------------------------------------------------------------
				#| Create the "prompt separator" element, which separates the
				#| "context" part of the receptive field (above the separator)
				#| from the "prompt" part of the receptive field (below the
				#| separator). It automaticaly pins itself to the bottom of the
				#| receptive field (just below the input box we just placed).

		_logger.debug("[Receptive Field] Creating the prompt separator element...")
	
		field._promptSeparator	= ThePromptSeparator(field)


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| 4. Since we added several elements to the field, update the view
			#|		of the field.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		field.updateView()	# This updates the view from the base field data.


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#| 5. Now we're done with field initialization.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		_logger.info("[Receptive Field] Field initialization is complete.")

	#__/ End singleton instance initializer field.__init__().

	def addEvent(field:TheReceptiveField, event:TextEvent):
		"""Given a text event, this adds it as a new element of our receptive field."""

		# Create new text event element.
		teElem = TextEventElement(field, event)
			# This automatically adds itself to the field, sliding it to the bottom.

		# Since we just changed the field, tell the view to re-render itself.
		field.updateView()

	@property
	def base(field:TheReceptiveField):
		return field._baseFieldData
			# Our base field data object.

	@property
	def console(field:TheReceptiveField):
		return field._console	# Our console client.

	def setConsole(field:TheReceptiveField, console:ConsoleClient):
	
		"""Tells the field where to find the system console.  We 
			need to know this so that, whenever the field contents 
			change, we can update the field display on the console."""
			
		field._console = console
	
	def place(field:TheReceptiveField, slot:FieldSlot, where:Placement):
	
		"""This method tells the field to place the given slot onto itself.
			We delegate this work to the base field data structure."""

		base = field.base
		
			# Tell our base data structure to place this slot inside itself.
		base.place(slot, placement)


	@property
	def view(theReceptiveField:TheReceptiveField):
	
		"""Return's the receptive field's currently preferred view.  This 
			is generally the AI's field view."""
			
		field = theReceptiveField
		return field._aiFieldView


	def updateView(field:TheReceptiveField):

		"""Tells the field to update its views because the base data has changed."""

		field.view.render()		# Render the view of the field.

		# If the console's attached, ask it to refresh its field display.
		console = field.console
		if console is not None:
			console.refreshFieldDisplay()


	def getData(theReceptiveField:TheReceptiveField):
	
		"""This method retrieves and returns all of the text data currently 
			contained in the AI's receptive field.  This should have already
			been trimmed down to fit within the nominal size (in tokens) of 
			the field.  The format of the returned value is a simple list
			of items, each of which is a string.  Each item is conceptually
			a single, indivisible unit; however, they are concatenated 
			together for purposes of displaying them to the AI, or a human."""
			
		field	= theReceptiveField
		view	= field.view
		data	= view.data
		
		field._data = data	
			# Cache this in case needed for diagnostics.
		
		return data

	def nTokens(theReceptiveField:TheReceptiveField):
	
		field	= theReceptiveField
		view	= field.view
		ntoks	= view.nTokens()	# Counts the tokens.
		
		field._nTokens = ntoks
			# Cache this in case needed for diagnostics.
		
		return ntoks

	def nChars(theReceptiveField:TheReceptiveField):
	
		field	= theReceptiveField
		view	= field.view
		nchars	= view.nChars()		# Counts the characters.
		
		field._nChars = nchars
			# Cache this in case needed for diagnostics.
		
		return nchars

#__/ End singleton class TheReceptiveField.
