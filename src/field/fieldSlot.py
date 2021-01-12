class FieldElement_: pass	# Forward declaration.

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
			field:ReceptiveField_=None
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
		thisFieldSlot._field = field

			# Go ahead and place this slot.
		thisFieldSlot.place()

	@property
	def element(this):	# Field element contained in this slot.
		return this._element

	def place(thisFieldSlot, 
				# Where to place the slot on the field?
			where:Placement=None):
				# By default, we'll just use the element's initial placement.

		if placement is None:
			placement = thisFieldSlot._placement

		# TODO: Need to keep working here 

