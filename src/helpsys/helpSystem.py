# helpSystem.py
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
	The Help system of GLaDOS is a subsystem that supports the Help
	application.  Various other subsystems (in particular, apps and
	command modules) can install "help modules," each of which provides
	detailed assistance on a particular topic which is accessible
	through the Help app.  This is navigable through a series of sub-
	menus.  The Help system is hierarchically organized, in the sense
	that help modules can be installed as sub-modules of other modules,
	so in general there is a tree structure.  At the leaves of this tree
	are individual "help items", which one cannot drill down into for
	further detail.

"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [ 'HelpItem', 'HelpModule', 'TheHelpSystem' ]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from infrastructure.logmaster	import getLoggerInfo, ThreadActor

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from	typing		import	List

from	infrastructure.decorators	import	singleton, classproperty
		# A simple decorator for singleton classes.

from	infrastructure.utils		import	seqno

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dummy class declarations (for use in type hints only).

class AppSystem_ : pass		# Dummy abstract base class for application systems.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Forward class declarations (for use in type hints only).

class TheHelpSystem: pass	# Singleton for the entire help system as a whole.

class _TheRootHelpModule: pass	# The root node of the help-module hierarchy.
class HelpModule: pass		# An help module, which can contain items and sub-modules.
class HelpItem: pass		# An individual help item that may be contained in a module.

#/==============================================================================
#|  Class definitions.

class HelpItem:

	"""A help item refers to an individual piece of guidance that may appear
		in a help module.  This is as opposed to a sub-module, which may be
		further drilled down into and have other items within it. The most 
		important property of a help item is its textual appearance, wich 
		will appear in the help window when that item is displayed.  A help 
		item may also have a name, which is used for lookup and debugging 
		purposes.  The name is not necessarily displayed anywhere in the 
		help window displaying the item.  If there is no name, the help item 
		is anonymous and is not accessible by name.  Finally, a help item may 
		have a verbose description, which is used to help populate the intro 
		text when creating a temporary help module to describe just this one 
		item in greater detail.  This is used when the user requests help on 
		a specific item by name."""

	def __init__(newHelpItem:HelpItem, 
			name:str=None,	# By default, the help item is anonymous.]
			text:str="(missing help item text)",
			shortDesc:str=None,		# Short description of the item.
			verboseDesc:str=None	# Verbose description of the item.
		):
			# NOTE: Callers should really always supply the 'text' parameter.
			# name should be supplied if the item needs to be searchable.
			# verboseDesc should be supplied if the item needs to be
			# able to be described in greater detail in its own help screen.
			# shortDesc is only needed to serve as the topicDesc for a
			# temporary help module that is created to display the item
			# in greater detail.

		"""Instance initializer for new help items. The <text> argument should
			always be provided."""
		
		item = newHelpItem

		item._name 			= name			# Store the name (if any) for later use.
		item._text 			= text			# Store the text for later use.
		item._shortDesc 	= shortDesc		# Store the short description (if any).
		item._verboseDesc 	= verboseDesc	# Store the verbose description (if any).

	@property
	def name(thisHelpItem:HelpItem):
		return thisHelpItem._name

	@property
	def text(thisHelpItem:HelpItem):
		return thisHelpItem._text

	@property
	def shortDesc(thisHelpItem:HelpItem):
		return thisHelpItem._shortDesc

	@property
	def verboseDesc(thisHelpItem:HelpItem):
		return thisHelpItem._verboseDesc

	# Define a special property .topicDesc that will be used by ItemHelpModule
	# to retrieve the .topicDesc property of the temporary help module that 
	# will be created to display this item in greater detail.  This is set to
	# the shortDesc of the item here, but may be overridden by subclasses.

	@property
	def topicDesc(thisHelpItem:HelpItem):
		return thisHelpItem.shortDesc

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HelpModule_:	# Abstract base class for all help modules.
	pass

@singleton
class TheNullHelpModule(HelpModule_):	# Placeholder for a missing help module.
	pass

class HelpModule(HelpModule_):

	"""A help module is a collection of help items and sub-modules (which are
		in turn also help modules). It corresponds roughly to a screen viewable
		in the Help app's window, which displays the items and sub-modules
		contained in the module."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| 	The following may be defined as class attributes/properties by 
	#|	specific subclasses of HelpModule; they may also be passed to the
	#|	instance initializer, and/or be overridden as instance attributes.
	#|
	#|      name - The name of this module. This is used for debugging and
	#| 			should be unique among all modules.  It may also be used
	#|			as a /help subcommand name for displaying this help module.
	#|
	#| 		topicName - The name of the topic that this help module describes.
	#| 			This may also be used as a /help subcommand name for displaying 
	#|			this help module.
	#|		
	#| 		topicDesc - A short description of the topic that this help module
	#| 			describes. This is used as a title string for this help module,
	#|			and also a description of the topic when it appears as a sub-
	#|			module of a higher-level module.
	#|
	#|		introText - The introductory text for this module. This is used
	#|			when the module is displayed in the Help app's window. It
	#|			should be a short paragraph that describes the topic of the
	#|			module. 
	#|
	#|		helpItems - A list of help items contained in this module. These
	#|			are displayed in the Help app's window when this module is
	#|			displayed, below the introductory text and above the list of
	#|			sub-modules.
	#|
	#|		subModules - A list of sub-modules contained in this module. Their
	#|			topic names and descriptions are displayed in the Help app's 
	#|			window when this module is displayed, below the list of help
	#|			items.
	#|
	#|		parentModule - The parent module of this module, if any. This is
	#|			used to construct the help screen text for this module.
	#|			It is typically displayed in the Help app's window when this\
	#|			module is displayed, below all other text.
	#|
	#| 		helpScreenText - The complete text of the help screen for this
	#| 			module. This is used when the module is displayed in the
	#| 			Help app's window. It is constructed from the module's
	#| 			intro text, the text of its help items, and the text of
	#| 			its sub-modules.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def __init__(newHelpModule:HelpModule, 
					name		:str = None,	# The symbolic name of this module.
					desc 		:str = None,	# A short description of the module. (For debugging; unused.)
					topicName	:str = None,	# The name of the module's topic.
					topicDesc	:str = None,	# A short description of the topic.
					introText	:str = None,	# The introductory text for this module.
					helpItems	:List[HelpItem] = None,	
						# The list of help items in this module.
					subModules	:List[HelpModule] = None,
						# The list of sub-modules in this module.
					parentModule:HelpModule = None,
						# The parent module of this module, if any.
					temporary	:bool = None,	# True if this is a temporary module.
				):
			# NOTE: Callers should really always supply most of these argument 
			# values, unless they are defined as subclass attributes, or as 
			# instance attributes by an initializer for a derived subclass. The 
			# helpItems and subModules arguments are optional; individual help 
			# items and sub-modules may be added later via the addItem() and 
			# addSubModule() methods.
			# 
			# Note the topicDesc string specifies how this module is described 
			# when it appears as a sub-module of higher-level modules; it may 
			# also be used in a header string at the top of the screen for this 
			# module. 
			#
			# The 'intro' argument, if provided, gives text that should appear 
			# as a "module introduction" at the top of its screen (but afer
			# the help screen header).

		"""Instance initializer for new help modules. The <name> argument should
			always be provided, and is a module name used in debugging. The 
			<topicName> argument should also always be provided, as it is the
			subcommand name used to access the module via the /help command."""


		hm = newHelpModule		# This new help module being initialized.


		# For arguments that are not provided, check to see if they are
		# defined as existing class or instance attributes, and if so, use 
		# those values instead.

		if name is None and hasattr(hm, 'name'):
			name = hm.name

		if topicName is None and hasattr(hm, 'topicName'):
			topicName = hm.topicName
		
		if topicDesc is None and hasattr(hm, 'topicDesc'):
			topicDesc = hm.topicDesc
		
		if introText is None and hasattr(hm, 'introText'):
			introText = hm.introText
		
		if helpItems is None and hasattr(hm, 'helpItems'):
			helpItems = hm.helpItems
		
		if subModules is None and hasattr(hm, 'subModules'):
			subModules = hm.subModules

		if parentModule is None and hasattr(hm, 'parentModule'):
			parentModule = hm.parentModule

		if temporary is None and hasattr(hm, 'temporary'):
			temporary = hm.temporary


		# Initialize any remaining uninitialized arguments to placeholder values.

		if name is None:
			name = "helpMod_" + str(seqno())

		if topicName is None:
			topicName = "(unspecified topic)"

		if topicDesc is None:
			topicDesc = "(unspecified description)"

		if introText is None:
			introText = "(missing module intro text)"

		if helpItems is None:
			helpItems = []		# Empty list of help items initially.
		
		if subModules is None:
			subModules = []		# Empty list of sub-modules initially.

		if temporary is None:
			temporary = False	# Default to non-temporary module.

		# As a special case, if we get here and the parentModule argument is 
		# still None, then we set the parentModule argument to the root help 
		# module. This helps us avoid creating non-temporary help modules that are not 
		# reachable from the root module. (And if this module is temporary, this at
		# least lets us use the '/up' command to get back to the root module.)
		if parentModule is None:
			parentModule = _TheRootHelpModule()	# Get the root help module.


		# Store the values obtained above as instance attributes.

		hm.name 		= name
		hm.topicName 	= topicName
		hm.topicDesc 	= topicDesc
		hm.introText 	= introText
		hm.helpItems 	= helpItems
		hm.subModules 	= subModules
		hm.parentModule = parentModule


		# Call the .genHelpText() method to generate the help text for this
		# module and store it in the 'helpScreenText' attribute.

		hm.genHelpText()


		# Go ahead and automatically add this module to the parent module's 
		# list of sub-modules, but only if this module is not temporary, and 
		# the parent module is not TheNullHelpModule().

		if temporary is False and parentModule is not TheNullHelpModule():
			parentModule.addSubModule(hm)


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|  Class public methods defined below:
	#|
	#|		addItem(thisHelpModule:HelpModule, helpItem:HelpItem)
	#|
	#|		addSubModule(thisHelpModule:HelpModule, subModule:HelpModule)
	#|
	#|		genHelpText(thisHelpModule:HelpModule)
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	def addItem(thisHelpModule:HelpModule, helpItem:HelpItem):

		"""Add a new help item to this help module. The <helpItem> argument
			should be a HelpItem instance."""

		module = thisHelpModule		# This help module.

		if not isinstance(helpItem, HelpItem):
			raise TypeError("The 'helpItem' argument must be a HelpItem instance.")

		module.helpItems.append(helpItem)

		# Re-generate the help text for this module.

		module.genHelpText()
	

	def addSubModule(thisHelpModule:HelpModule, subModule:HelpModule):

		"""Add a new sub-module to this help module. The <subModule> argument
			should be a HelpModule instance."""

		module = thisHelpModule		# This help module.

		if not isinstance(subModule, HelpModule):
			raise TypeError("The 'subModule' argument must be a HelpModule instance.")

		module.subModules.append(subModule)

		# Re-generate the help text for this module.

		module.genHelpText()
	

	def genHelpText(thisHelpModule:HelpModule):

		"""Generate the help text for this help module. This method is called
			automatically when the module is initialized, and also whenever
			items or sub-modules are added to the module."""

		module = thisHelpModule		# This help module.

		# Help screen header -- Start with the topic name and description.

		helpText = module.topicName + " - " + module.topicDesc + "\n\n"

		# Add the intro text for this module.

		helpText += module.introText + "\n\n"

		# Add the help items in this module, if any.

		for helpItem in module.helpItems:
			helpText += helpItem.helpText + "\n\n"

		# Add the sub-modules in this module, if any.
		# If there are sub-modules, add the text "Subtopics:" to the help
		# text, followed by a list of the sub-modules.

		if len(module.subModules) > 0:
			helpText += "Subtopics:\n\n"

		for subModule in module.subModules:
			helpText += subModule.topicName + " - " + subModule.topicDesc + "\n"

		# If there is a parent module, remind the user they can use the "up" 
		# command to return to it. (This command is in the command module for
		# the help application, and is available when that application has the
		# command focus.)

		parentModule = module.parentModule
		if parentModule is not None and parentModule is not TheNullHelpModule():
			helpText += "\nUse '/up' to return to the " \
				+ module.parentModule.topicName + " topic.\n"

		# Store the generated help text in the 'helpScreenText' attribute.

		module.helpScreenText = helpText


	def lookupModule(thisHelpModule:HelpModule, identifier:str=None):

		"""Lookup a help module by name or topic. The <identifier> argument
			should be a module name or a topic name. The first module with a
			matching name or topic name is returned. If no module is found,
			None is returned. This help module and its recursive tree of 
			sub-modules are searched in depth-first order. We also search the 
			helpItems list of each module for any help items (which are not 
			proper sub-modules), and if there is one with a name attribute that 
			matches <identifier>, we return that help item as a temporary help 
			module."""

		module = thisHelpModule		# This help module.

		# If the identifier is None, return None.
		
		if identifier is None:
			return None

		# If either of them matches this module directly, we'll just return 
		# this module. NOTE: Do case-insensitive comparisons.

		if identifier.lower() == module.name.lower() or \
			identifier.lower() == module.topicName.lower():
			return module
		
		# We'll next search the helpItems list of this module for any help
		# items that are not proper sub-modules, and if there is one with a
		# name attribute that matches moduleName or topicName, we return that
		# help item as a temporary help module. (But one with us as parent.)

		for helpItem in module.helpItems:
			# Case-insensitive comparisons.
			if identifier.lower() == helpItem.name.lower():
				return ItemHelpModule(helpItem, parent=module)

		# If we get here, we didn't find a matching help item, so we'll search
		# the sub-modules of this module. For each, we check its name and
		# topic, and if it isn't a direct match, we then recursively search
		# its sub-modules.

		for subModule in module.subModules:
			if identifier.lower() == subModule.name.lower() or \
				identifier.lower() == subModule.topicName.lower():
				return subModule
			else:
				subModuleResult = subModule.lookupModule(identifier)
				if subModuleResult is not None:
					return subModuleResult

		# If we get here, we didn't find a matching module or help item.

		return None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TemporaryHelpModule_(HelpModule):

	"""This is an abstract base class for temporary help modules. A temporary
		help module is a help module that is generated on the fly, and is not
		added to the help module hierarchy, but it may be viewed in the Help
		application. The purpose of a temporary help module is to provide
		help information for a help item that is not a proper sub-module, or
		other dynamically generated help information."""

	parentModule = TheNullHelpModule()		# We're an orphan by default.

	temporary = True						# We're temporary.


# The ItemHelpModule class generates a temporary help module for a help item;
# it is used by the lookupModule() method of the HelpModule class. It is
# not added to the help module hierarchy, but it may be displayed as a
# temporary help module when the user requests help on a help item that
# is not a proper sub-module. In such cases, the name and topicName of the
# temporary module will be based on the .name attribute of the help item,
# and the topicDesc will be based on the .text attribute of the help item.
# The introText of the temporary module will be based on the .verboseDesc
# attribute of the help item, if it is not None, or else it will be set
# to simply, "No further information is available for this item."

class ItemHelpModule(TemporaryHelpModule_):

	"""This is a temporary help module that is generated for a help item
		that is not a proper sub-module. It is used by the lookupModule()
		method of the HelpModule class. It is not added to the module
		hierarchy, but it may be set as the current help module and 
		displayed in the help window."""

	def __init__(self, helpItem:HelpItem, parent:HelpModule=None):

		"""Initialize the temporary help module."""

		# Set both the name and topicName attributes of the temporary module
		# to the .name attribute of the help item.

		self.name		= helpItem.name
		self.topicName	= helpItem.name

		# Set the topicDesc attribute to the .topicDesc property of the help item.
		# (This may be defined differently for different classes of help items.)

		self.topicDesc = helpItem.topicDesc

		# Set the introText attribute to the .shortDesc attribute of the 
		# help item followed by two newlines (to separate it from
		# the verboseDesc attribute), but only if it's set and different 
		# from topicDesc, then followed by the .verboseDesc attribute
		# of the help item, if it is not None, or else follow it with 
		# "No further information is available for this item."

		introText = ""
		if helpItem.shortDesc is not None and helpItem.shortDesc != self.topicDesc:
			introText += helpItem.shortDesc + "\n\n"
		if helpItem.verboseDesc is not None:
			introText += helpItem.verboseDesc
		else:
			introText += "No further information is available for this item."
		self.introText = introText	# Set the introText attribute.

		# Set the parentModule attribute to the parent module, if provided.

		if parent is not None:
			self.parentModule = parent

		# The rest of the initialization can be handled by our superclass.

		super().__init__()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@singleton
class _TheRootHelpModule(HelpModule):	# The root of the help module hierarchy.

	"""This is the unique help module that sits at the root of the help module
		hierarchy.  It is initialized when the help system is initialized.
		Other help modules will get installed somewhere under this module."""

	name = "root-module"		# Name of this module.
	topicName = "GladOS"		# Name of this module's topic.
	topicDesc = "How to Use the GLaDOS Operating Environment"	
		# Description of this module's topic.
	introText = ( \
		"Welcome to GlaDOS, Gladys' Lovely and Dynamic Operating System, " \
		"(c)2020-23 Metaversal Constructions.  This is the top-level screen " \
		"of GLaDOS's interactive Help system.  Help topics and subtopics are " \
		"organized in hiarchical menus, and you can drill down into them by " \
		"typing /help <topicName>.")

	parentModule = TheNullHelpModule()	# The parent module of this module.
		# This is the null module, which is a singleton that is used as the
		# parent of the root module, and as the parent of any module that
		# doesn't have a parent. We use this instead of None in order to
		# avoid automatically assigning the parent module to the root module
		# when the root module is initialized.

	# Nothing else to do here.  The rest of the initialization is done by the
	# HelpModule class initializer.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@singleton
class TheHelpSystem:

	"""This singleton class anchors the help system. Other systems may access it 
		by calling the class constructor TheHelpSystem(), which just returns the 
		unique singleton instance."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|  Data attributes.							 [class documentation block]
	#|  ================
	#|
	#|  The following are the private class/instance attributes used in this
	#|  class.  They are listed here for reference, but are not intended to be
	#|  accessed directly by other classes.  Instead, they should be accessed
	#|  via the public properties and methods defined below.
	#|
	#|		_rootModule:HelpModule - The root of the help module hierarchy.
	#|
	#|      _currentModule:HelpModule - The currently selected help module.
	#|			Initially, this is set to the root module. Later, it may be
	#|			set to other modules as the user drills down into the help
	#|			hierarchy. Generally, it is the module that is currently
	#|			displayed on the help screen or was most recently displayed,
	#|			although it may be set to a different module if the user
	#|			invokes the help system with a specific topic name. Also,
	#|          certain actions may cause the current module to be changed
	#|		    as a side effect, such as, closing the help window may cause
	#|			the current module to revert to the root module.
	#|
	#|		_appSystem:AppSystem - The application system. This is used to
	#|			access the Help application. The application system is 
	#|			initialized after the help system, so we can't get a reference
	#|			to it in the initializer, so we have to wait until later to
	#|			get the reference.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def __init__(theHelpSystem:TheHelpSystem):

		helpSys = theHelpSystem
		
		# Create and store a reference to the root help module.
		helpSys._rootModule = _TheRootHelpModule()

		# Set the current module to the root module.
		helpSys._currentModule = helpSys._rootModule

		# Initialize the application system reference to None, so we can
		# tell that it hasn't been set properly yet. We can initialize it
		# later after the application system is initialized by calling the
		# setAppSystem() method.
		helpSys._appSystem = None

	@property
	def rootModule(theHelpSystem:TheHelpSystem):
		return theHelpSystem._rootModule
	
	@property
	def currentModule(theHelpSystem:TheHelpSystem):
		return theHelpSystem._currentModule

	@currentModule.setter
	def currentModule(theHelpSystem:TheHelpSystem, newModule:HelpModule):
		theHelpSystem._currentModule = newModule
		# Should we automatically update the help window here?  Probably not,
		# since this is a setter method, and it's not clear that the caller
		# would expect the help window to be updated.  Instead, we'll leave
		# it up to the caller to update the help window if desired.
	
	@property
	def appSystem(theHelpSystem:TheHelpSystem):
		return theHelpSystem._appSystem

	@appSystem.setter
	def appSystem(theHelpSystem:TheHelpSystem, newAppSystem:AppSystem_):
		theHelpSystem._appSystem = newAppSystem

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|  Class public methods defined below:
	#|  ===================================
	#|
	#|		setAppSystem(thisHelpSystem:TheHelpSystem, newAppSystem:AppSystem)
	#|
	#|			Sets the application system reference. This is called by the
	#|			system supervisor after the application system is initialized.
	#|
	#|		addToplevelItem(thisHelpSystem:TheHelpSystem, helpItem:HelpItem)
	#|
	#|			Adds a new top-level help item to the root help module.
	#|
	#|		addToplevelModule(thisHelpSystem:TheHelpSystem, helpModule:HelpModule)
	#|
	#|			Adds a new top-level help module under the root help module.
	#|
	#|		lookupModule(thisHelpSystem:TheHelpSystem, moduleName:str=None, topicName:str=None)
	#|
	#|			Searches the help module hierarchy for a module with the given
	#|			name (if provided) or topic name (if provided).  This will 
	#|			first search all sub-modules of the current module, in depth-
	#|			first order, and then search all sub-modules of the root
	#|			module, in depth-first order.  If no module is found, this
	#|			method returns None.
	#|
	#|		showHelpScreen(thisHelpSystem:TheHelpSystem, helpModule:HelpModule=None)
	#|
	#|			Displays the help screen for the given help module.  If no
	#|			module is provided, the current module is used.  This method 
	#|			invokes the Help application, which must be installed in the 
	#|			system and available, and the windowing system must already 
	#|			be initialized and running.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def setAppSystem(thisHelpSystem:TheHelpSystem, theAppSystem:AppSystem_):
		thisHelpSystem.appSystem = theAppSystem

	def addToplevelItem(thisHelpSystem:TheHelpSystem, helpItem:HelpItem):
		thisHelpSystem.rootModule.addItem(helpItem)

	def addToplevelModule(thisHelpSystem:TheHelpSystem, helpModule:HelpModule):
		thisHelpSystem.rootModule.addModule(helpModule)

	def lookupModule(thisHelpSystem:TheHelpSystem, identifier:str=None) -> HelpModule:

		"""Searches the help module hierarchy for a module or item with the 
			given name or topic name.  This will first search all sub-modules of 
			the current module, in depth-first order, and then search all sub-
			modules of the root module, in depth-first order.  If no matching 
			module or item is found, this method returns None.  If an item is 
			found, it is converted to a temporary help module and returned.  If 
			a module is found, it is returned."""

		helpSys = thisHelpSystem

		# [NOTE: Eventually, we may want to extend this method to support
		# prefix matching, so that if the given identifier matches any prefix
		# of a module name or topic name, the such first module or item is 
		# returned.  For now, we'll just do exact (but case-insensitive) 
		# matching.]

		# First, check the module sub-hierarchy under the current module.
		if helpSys.currentModule is not None:
			module = helpSys.currentModule.lookupModule(identifier)
			if module is not None:
				return module

		# NOTE: Another thing we could do here is to proceed up the module
		# hierarchy to successive ancestor modules, searching the subtrees
		# of each ancestor module for the module we're looking for.  This
		# would give priority to 'sibling' or 'cousin' modules over distant
		# parts of the module hierarchy.  However, this is probably overkill
		# for now, and we can always add this feature later if we want to.

		# If that fails, check the module sub-hierarchy under the root module.
		if helpSys.rootModule is not None:
			module = helpSys.rootModule.lookupModule(identifier)
			if module is not None:
				return module

		# If we get here, we didn't find the module.
		return None

	def showHelpScreen(thisHelpSystem:TheHelpSystem, module:HelpModule=None):
		
		"""Displays the help screen for the given module (if provided).  If no 
			module name is provided, the current module is used.  Note that this 
			method works by invoking the Help application, which must be 
			installed in the system and available, and also the windowing system 
			must already be initialized and running."""

		helpSys = thisHelpSystem

		appSys = helpSys.appSystem
		if appSys is None:
			raise RuntimeError("No application system available")

		helpApp = appSys('Help')	# Get the help application.

		if helpApp is None:
			raise RuntimeError("No help application available")

		# Tell the help application to update its help screen (if needed).
		helpApp.updateHelpScreen(module)

		# Tell the help application to display the help screen (or refresh
		# it if it's already displayed).
		helpApp.launch()