#|==============================================================================
#|				  TOP OF FILE:	  field/placement.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		field/placement.py				 [Python module source file]

	MODULE NAME:	field.placement
	IN PACKAGE:		field
	FULL PATH:		$GIT_ROOT/GLaDOS/src/field/placement.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (Generic Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.field (receptive field facility)


	MODULE DESCRIPTION:
	===================

		This module just provided a simple enumerated type, class 
		Placement, designed for denoting how a field element should
		be initially placed on the receptive field, or how its 
		position on the field, once placed, may be maintained.
		Initial placements may be any of the following values:
		
			PINNED_TO_BOTTOM, PINNED_TO_TOP, MOVE_TO_BOTTOM,
			MOVE_TO_TOP, ANCHORED_TO_BOTTOM, ANCHORED_TO_TOP,
			SLIDE_TO_BOTTOM, SLIDE_TO_TOP, FLOATING

		Any of these except the ones named with verbs (i.e., the 
		"MOVE_" and "SLIDE_" placements) can also be used to denote
		how (and whether) the element's position will be maintained
		after it is placed.  See the docstring for the Placement 
		class for more details.

	USAGE:
	------
	
		from field.placement import Placement
		...
		initPlacement = Placement.MOVE_TO_BOTTOM
		...
		if initPlacement.isPersistent:
			curPlacement = initPlacement
		else:
			curPlacement = initPlacement.convertsTo
		
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


	#|==========================================================================
	#|
	#|	 1. Module imports.								   [module code section]
	#|
	#|			Load and import names of (and/or names from) various
	#|			other python modules and pacakges for use from within
	#|			the present module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	1.1. Imports of standard python modules.	[module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from	enum	import	Enum	# Support for enumerated types.


		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|----------------------------------------------------------------
			#|	1.2.1. The following modules, although custom, are generic 
			#|		utilities, not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#-------------------------------------------------------------
				# The logmaster module defines our logging framework; we
				# import specific definitions we need from it.	(This is a
				# little cleaner stylistically than "from ... import *".)

from infrastructure.logmaster	import getComponentLogger

	# Go ahead and create or access the logger for this module.

global _component, _logger	# Software component name, logger for component.

_component = path.basename(path.dirname(__file__))	# Our package name.
_logger = getComponentLogger(_component)			# Create the component logger.


	#|==========================================================================
	#|	2. Globals										   [module code section]
	#|
	#|		Declare and/or define various global variables and constants.  
	#|		Top-level 'global' declarations are not strictly required, but 
	#|		they serve to verify that these names were not previously used, 
	#|		and also serve as documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|
		#|	2.1. Special globals.						[module code subsection]
		#|
		#|		These globals have special meanings defined by the
		#|		Python language.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__	# List of public symbols exported by this module.
__all__ = [
		'Placement',   # Enumerated type for field element placement values.
	]


	#|==========================================================================
	#|	3. Type definitions.							   [module code section]
	#|
	#|		Define some new 'types' (i.e., simple classes) that this module 
	#|		will provide.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Placement(Enum):
	#---------------------------------------------------------------------------
	"""Placement						   [module public enumerated type class]
	
			A Placement value specifies where in the receptive field the 
			slot for a given field element (such as a window) should be 
			(at least initially) placed.  Allowed values include:
			
				PINNED_TO_BOTTOM - The element is pinned to the bottom
					of the receptive field (above elements previously 
					pinned to the bottom).  This means it cannot be
					moved from this position in the order by 'normal'
					placement requests.  Examples of elements pinned
					to the bottom:  Prompt, separator.
				
				PINNED_TO_TOP - The element is pinned to the top of 
					the receptive field (below elements previously 
					pinned to the top).  Examples of elements pinned 
					to the top:  Info window.
				
				MOVE_TO_BOTTOM - The element is moved to the bottom of
					the receptive field, just above all of the elements
					pinned to the bottom.  Examples of elements moved
					to the bottom:  The current active application 
					window.  After moving it there, it is anchored.
				
				MOVE_TO_TOP - The element is moved to the top of the 
					receptive field, just below all of the elements 
					pinned to the top.  Examples of elements moved to
					the top:  A window that the AI doesn't want to 
					focus its attention on, but wants to remain visible.
					After being moved, it is anchored.
				
				ANCHORED_TO_BOTTOM - This is like MOVE-TO-BOTTOM but the
					element's location is just above all elements that
					were only moved to the bottom.
				
				ANCHORED_TO_TOP - This is like MOVE-TO-TOP but the element's
					location is just below all elements that were only
					moved to the top.
				
				SLIDE_TO_BOTTOM - Just above all elements pinned  
					or anchored to the bottom, but the new element is not 
					anchored.  That is, the element can be displaced by a 
					new SLIDE-TO-BOTTOM.  This is the usual mode for 
					adding new elements: All previously added elements are 
					displaced upwards.  After being slid, the element is
					converted to floating.
			
				SLIDE_TO_TOP - Similar to SLIDE-TO-BOTTOM, but for the top.
				
				FLOATING - The element may appear anywhere between the top
					and bottom anchored slots.  Not generally used as an
					initial placement, but 'slid' elements convert to 
					floating status after sliding.
		
			Please note that some (but not all) of these placement values
			may also be used to record a persistent placement state for a
			slot.  These are (in order from top to bottom):
			
				1. PINNED_TO_TOP
									<-- Newly PINNED_TO_TOP go here.
									<-- Newly MOVE_TO_TOP'd go here and then are in the ANCHORED_TO_TOP state.
				2. ANCHORED_TO_TOP
									<-- Newly ANCHORED_TO_TOP go here.
									<-- Newly SLIDE_TO_TOP'd go here and then are in the FLOATING state.
				3. FLOATING
									<-- Newly SLIDE_TO_BOTTOM'd go here and then are in the FLOATING state.
									<-- Newly ANCHORED_TO_BOTTOM go here.
				4. ANCHORED_TO_BOTTOM
									<-- Newly MOVE_TO_BOTTOM'd go here and then are in the ANCHORED_TO_BOTTOM state.
									<-- Newly PINNED_TO_BOTTOM go here.
				5. PINNED_TO_BOTTOM
		
		
		Public Properties:
		------------------
		
			placement.isPersistent [bool]	- 
			
				True if placement is persistent (can be maintained).
			
			placement.isConvertible [bool]	-
			
				This if placement is not persistent.
			
			placement.convertsTo [Placement]	-
			
				Defined only for non-persistent (i.e., convertible) 
				placements.  After this placement is completed, into 
				what other placement does it convert?
	"""
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#| Values.  Note that the order in which the values below are specified 
		#| corresponds to the order in which they would (initially) appear in a 
		#| receptive field.

			#|------------------------------------------------------------------
			#| PINNED_TO_TOP 								   [placement value]
			#|
			#|		Persistent placement.  The element is pinned to the 
			#|		top of the receptive field (below elements that were 
			#|		previously pinned to the top).  Elements subsequently
			#|		pinned to the top would appear below this one, and 
			#|		would not displace it.  
			#|
			#|		Examples of elements that would typically be pinned to 
			#|		the top of the field include:  The Info window.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	PINNED_TO_TOP		= 'pinned-to-top'		
		# Persistent placement (below previous pinned-to-top).

			#|------------------------------------------------------------------
			#| MOVE_TO_TOP 								   	   [placement value]
			#|
			#|		Initial placement.  The element is moved to near the 
			#|		top of the receptive field, specifically, to just 
			#|		below all of the elements that are currently pinned 
			#|		to the top.  However, instead of being pinned there,
			#|		the element is put into an 'anchored' state; thus, 
			#|		elements subsequently placed with MOVE_TO_TOP would
			#|		displace this one in the slot order.
			#|		
			#|		Examples of elements that would typically be moved to
			#|		the top:  Any window that the AI decides it doesn't 
			#|		want to focus its attention on, but wants to remain 
			#|		visible.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	MOVE_TO_TOP			= 'move-to-top'			
		# Initial placement; not persistent (converts to ANCHORED_TO_TOP after 
		# movement).
	
			#|------------------------------------------------------------------
			#| ANCHORED_TO_TOP							   	   [placement value]
			#|
			#|		Persistent placement.  The element is moved to the 
			#|		general vicinity of the top of the field, but below
			#|		all of the slots that were previously pinned, moved, 
			#|		or anchored to the top, and it is put into an 
			#|		'anchored' state.  Elements that are subsequently 
			#|		ANCHORED_TO_TOP would appear below this slot (and 
			#|		would not displace it).
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	ANCHORED_TO_TOP		= 'anchored-to-top'		# Persistent placement (below previous anchored-to-top).
	SLIDE_TO_TOP		= 'slide-to-top'		# Initial placement; not persistent (converts to FLOATING after movement).

	FLOATING 			= 'floating'			# Persistent placement (floating between anchored slots).
	
	SLIDE_TO_BOTTOM		= 'slide-to-bottom'		# Initial placement; not persistent (converts to FLOATING after movement).
	ANCHORED_TO_BOTTOM	= 'anchored-to-bottom'	# Persistent placement (above previous anchored-to-bottom).
	MOVE_TO_BOTTOM		= 'move-to-bottom'		# Initial placement; not persistent (converts to ANCHORED_TO_BOTTOM after movement).
	PINNED_TO_BOTTOM	= 'pinned-to-bottom'	# Persistent placement (above previous pinned-to-bottom).

		# This is declared global here so it doesn't get interpreted as a placement value.
		
	global _CONVERSION_MAP		# Maps convertible placements.
	_CONVERSION_MAP = {	
			Placement.MOVE_TO_TOP: 		Placement.ANCHORED_TO_TOP,
			Placement.MOVE_TO_BOTTOM:	Placement.ANCHORED_TO_BOTTOM,
			Placement.SLIDE_TO_TOP:		Placement.FLOATING,
			Placement.SLIDE_TO_BOTTOM:	Placement.FLOATING
		}

	@property
	def isPersistent(thisPlacement):
		"""Is this placement value the kind that is persistent (can be maintained)?"""
		return thisPlacement is not in _CONVERSION_MAP

	@property
	def isConvertible(thisPlacement):
		"""Is this placement value the kind that automatically converts to another on placement?"""
		return not thisPlacement.isPersistent
		
	@property
	def convertsTo(thisPlacement):
		"""Given a convertible (non-persistent) placement, what placement does 
			it convert to?"""
		return thisPlacement if thisPlacement.isPersistent else _CONVERSION_MAP[thisPlacement] 

#__/ End enumerated type class Placement.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					 END OF FILE:	field/placement.py
#|=============================================================================