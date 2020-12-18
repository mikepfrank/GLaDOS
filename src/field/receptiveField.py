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
	def __init__(inst):
		pass

class FieldView_:
	"""Abstract base class from which to derive more specific views of the 
		receptive field."""
	pass

class AI_FieldView(FieldView_):
	"""Derived class for views of the receptive field to be sent to AIs."""
	pass
	
class Human_FieldView(FieldView_):
	"""Derived class for views of the receptive field to be shown to
		human users."""
	pass

@singleton
class TheReceptiveField:
	
	"""Singleton class for the entire receptive field management system."""
	
	def __init__(inst, fieldSize:int):
		""""""
	
			# Create the base field data object & store it.
		baseFieldData 			= BaseFieldData(fieldSize)
		inst._baseFieldData		= baseFieldData
		
			# Create and store field views for the AI & for humans.
		inst._aiFieldView		= inst.AI_FieldView(baseFieldData)
		inst._humanFieldView	= inst.Human_FieldView(baseFieldData)
		