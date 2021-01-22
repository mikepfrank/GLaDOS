#|==============================================================================
#|				  TOP OF FILE:	  apps/appActions.py
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		apps/appActions.py				 [Python module source file]

	MODULE NAME:	apps.appSystem
	IN PACKAGE:		apps
	FULL PATH:		$GIT_ROOT/GLaDOS/src/apps/appActions.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (Generic Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.apps (application system component)


	MODULE DESCRIPTION:
	===================

		This module provides the application system's interface to the
		action system, which is the subsystem of the system Supervisor
		that manages communication of "action news reports" between the
		various subsystems of GLaDOS.
		
		The two parts of any system's interface to the action system are
		the following:
		
			(1) INPUT FROM THE ACTION SYSTEM.  This takes the form of
				a subclass of ActionSubscriber_ which is responsible for
				subscribing to the specific "action channels" that the
				present subsystem is interested in watching.  It's also
				possible to define our own custom channels.  The subscriber
				is then notified of action reports (action status updates)
				appearing on the channel and can dispatch responses appro-
				priately to other parts of the local system.  In our case, 
				our system's subscriber subclass is our private class called
				_The_AppSystem_Subscriber.
				
			(2) OUTPUT TO THE ACTION SYSTEM.  This takes the form of 
				subclasses of Action_ (or ActionBySystem_, for automated-
				system type subsystems, as opposed to AI subsystems) that
				define the specific types of actions that can be generated
				by this particular subsystem.  In our case, so far we have
				the _AppSystemAction_ private abstract base class, and the
				AutoOpenWindowAction public concrete leaf class, which is
				specifically for the action of auto-opening an app's window
				on the AI's receptive field at system startup, which we 
				make an explicit action so that the AI can be cognizant of
				its having taken place.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#|==========================================================================
	#|
	#|	 0. Public names exported from this module.		   [module code section]
	#|
	#|			Special Python global structure defining the list of 
	#|			public names that dependent modules will import if 
	#|			they do 'from apps.application import *'.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	__all__		# List of public symbols exported by this module.
__all__ = [
			#---------
			# Classes.
			
		'The_AppSystem_Subscriber'	
			# Public singleton class for the application system's action subscriber.
		
		'AutoOpenWindowAction'
			# This is an action that we conceive, initiate, and execute to auto-open app windows.
	]


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

		#|======================================================================
		#|	1.2. Imports of custom application modules. [module code subsection]
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|==================================================================
			#|	1.2.1. The following modules, although custom, are generic 
			#|		utilities, not specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

				#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				#| 1.2.1.1. The logmaster module defines our logging framework.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.logmaster	import getLoggerInfo, ThreadActor

	#----------------------------------------------------------
	# Go ahead and create or access the logger for this module,
	# and obtain the software component name for our package.

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.


				#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				#| 1.2.1.2. Here are some other infrastructure modules we use.
				#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from infrastructure.decorators	import	singleton
		# A simple decorator for singleton classes.


			#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			#|	1.2.2. These modules are specific to the present application.
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#---------------------------------------------------------------------------
	# In general, applications need to be able to access the action subsystem
	# of the supervisory system, so that they can inject actions into the action
	# broadcasting facility, as well as receive action updates from other parts
	# of the system.  We import just the specific definitions that we require.
	
from supervisor.action			import	(

			# We are going to be generating system actions, and we need this to do that.
		
		ActionBySystem_,		# We subclass this with our own _AppSystemAction_ ABC.
		
			# We require action-subscriber capability to be able to receive action news updates.
		
		ActionSubscriber_, 		# We subclass this with our own The_AppSystem_Subscriber.
		
			# Until a channel is developed that narrows down the news to only those things
			# that applications might need to know about, we'll just subscribe to this channel
			# to make sure we don't miss anything important.
			
		TheEverythingChannel	# This channel broadcasts all action news updates in the system.
		
	)

from mind.aiActions				import	AnnounceFieldExistsAction
	# We need this so that we can watch for actions of this class,
	# because that's what tells us that it's safe to go ahead and
	# start opening up the windows for apps marked as auto-open.
	# Used in the .notify method of _AppSystem_Subscriber_.


	#|==========================================================================
	#|
	#|	 2. Globals										   [module code section]
	#|
	#|		Declare and/or define various global variables and
	#|		constants.	Note that top-level 'global' statements are
	#|		not strictly required, but they serve to verify that
	#|		these names were not previously used, and also serve as
	#|		documentation.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	2.1. Private globals.							   [code subsection]
		#|
		#|		These globals are not supposed to be accessed from
		#|		outside of the present module.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#|------------------------------------------------------------------
			#|	_APP_LIST						[module private global constant]
			#|
			#|		This is a structure (list of dicts) that defines 
			#|		the full list of (intended-to-be-) supported 
			#|		applications.  See the definition at the end of 
			#|		the file for further documentation.
			#|
			#|		Note that some apps may not yet be implemented.
			#|
			#|		The structure of each dict in the list is:
			#|
			#|			name	- Short text name of the application.
			#|						This must match the name used in the
			#|						app-configs attribute of the system
			#|						config file (glados-config.hjson).
			#|
			#|			class	- Class defining the application.  This
			#|						must be a subclass of Application_.
			#|
			#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global _APP_LIST	# We could put this into the AppSystem class instead.
	# Note the value of this is not defined until near the end of the file,
	# because it needs to be able to reference the various application classes.


	#|==========================================================================
	#|
	#|	3. Class forward declarations.					   [module code section]
	#|
	#|			Pre-declare classes to be defined later in this module.
	#|			(Such dummy definitions are really only useful in type 
	#|			hints, which don't really do anything, but are useful
	#|			as documentation in argument lists.)
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class _AppSystem_Subscriber_: pass
	# Private abstract base class for AppSystem's action subscriber class.

class The_AppSystem_Subscriber: pass
	# Concrete singleton leaf class for the AppSystem's action subscriber.
	
class _AppSystemAction_: pass
	# Private abstract base class for the AppSystem's action classes.

class AutoOpenWindowAction: pass
	# Concrete leaf class for an action of auto-opening a window.


	#|==========================================================================
	#|
	#|	4. Class definitions.							   [module code section]
	#|
	#|			Define the classes provided by this module.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#|======================================================================
		#|	4.1. General classes.							   [code subsection]
		#|
		#|		These classes are not application-specific, but apply
		#|		generally to the entire application system.
		#|
		#|			The_AppSystem_Subscriber		    [public singleton class]
		#|
		#|				Subscribes to the AppSystem's favorite channels
		#|				within the Action News Network.
		#|
		#|			
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class _AppSystem_Subscriber_(ActionSubscriber_):

	"""Private abstract base class for an AppSystem's subscriber class.  This 
		should only have one concrete leaf class, called The_AppSystem_Subscri-
		ber, which should be a singleton class with only one instance, The_App-
		System_Subscriber().
		
		This subscribes to action news channels that the application system
		is potentially interested in watching."""

	def __init__(newSubscriber:AppSystem_Subscriber_, appSys, name="AppSys"):

		_logger.debug("appSysSubscriber.__init__(): Initializing the AppSystem's subscriber...")

		sub = newSubscriber		# Shorter name for this new subscriber.
		
		sub._appSys = appSys	# Remember how to get to the whole app system.

			# Do generic initialization for any ActionSubscriber_ instance.
		super(_AppSystem_Subscriber_, sub).__init__(name=name)

		_logger.debug("appSysSubscriber.__init__(): Subscribing to The Everything Channel...")

			# For now, we'll just subscribe to the everything-channel.
		TEC = TheEverythingChannel()	# Defined in the action module.
		sub.subscribe(TEC)

	def notify(thisSub:AppSystem_Subscriber_, status, action):
	
		"""This method is called when this subscriber is being notified 
			of an action report; i.e., an action status update."""

		appSys = thisSub._appSys	# The application system.

		# If the action report was that an announcement of the receptive
		# field's existence was just completed, then we'll take that as
		# our cue that it's a good time to display all of our app windows
		# that are supposed to be open.

		if status=='completed' and isinstance(action, AnnounceFieldExistsAction):

			_logger.info("[Apps/Open] Received field-existence notification.")

			appSys.displayWindows()
				# This tells the application system, "OK, you can go ahead now and
				# display all of your existing open windows on the receptive field."


@singleton
class The_AppSystem_Subscriber(AppSystem_Subscriber_):

	"""This singleton subscribes to action news channels that the 
		application system is potentially interested in watching."""

	pass	# Code is in AppSystem_Subscriber_ above.


class _AppSystemAction_(ActionBySystem_):

	"""This is a private (leading '_') and abstract (trailing '_') base class
		for actions taken by the application system.  Its functions include
		setting the conceiver (the AppSystem)."""

	defaultConceiver = The_AppSystem_Entity()

	def __init__(new_AppSys_Action:_AppSystemAction_,

			description:str="A generic action was taken by the application system.",
				# REQUIRED. A description string. SUBCLASSES SHOULD OVERRIDE THIS VALUE.

			conceiver:AI_Entity_=None,
				 # The AI entity that conceived of taking this action.
				 # If not provided, we'll default it to The_AppSystem_Entity().

			importance:int=None

		):

		asAction = new_AppSys_Action

		if conceiver is None:
			conceiver = asAction.defaultConceiver

		super(_AppSystemAction_, asAction).__init__(description, conceiver=conceiver)


class AutoOpenWindowAction(_AppSystemAction_):

	"""Class for the action of automatically opening an application's
		window on application-system startup.  We make this an explicit
		action to aid the AI's understanding of the fact that opening
		this particular window was done as an automatic system action."""

	def __init__(newAOWA:AutoOpenWindowAction, app:Application_):

		"""This instance initializer for new auto-open-window actions
			simply sets the textual description of the action, and
			remembers which app we are intending to auto-open the
			window of."""

		newAOWA._app = app		# Remember which app we're opening.

		appName = app.name		# Get the name of the app.

		description=f"Auto-opening the '{appName}' app's window..."

		super(AutoOpenWindowAction, newAOWA).__init__(description)

	#__/ End instance initializer for class _AutoOpenWindowAction.

	def executionDetails(thisAOWA:AutoOpenWindowAction):

		"""Since this is a system action, the action processor will
			automatically execute it by calling this method.  In this
			case, all we need to do is call the app's .openWins()
			method, to tell it to actually open its windows."""

		app = thisAOWA._app		# Get the app that this action is for.
		app.openWins()			# Tell that app to open its windows.

	#__/ End instance method aowa.executionDetails().

#__/ End action class AutoOpenWindowAction.


#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					 END OF FILE:	apps/appActions.py
#|=============================================================================