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
		purposes.  The name is not displayed in the help window.  If there 
		is no name, the help item is anonymous and is not accessible by name.
		Finally, a help item may have a verbose description, which is used
		to populate the intro text when creating a temporary help module
		to describe just this one item in greater detail.  This is used
		when the user requests help on a specific item by name."""

	def __init__(newHelpItem:HelpItem, 
			name:str=None,	# By default, the help item is anonymous.]
			text:str="(missing help item text)",
			verboseDesc:str=None
		):
			# NOTE: Callers should really always supply the 'text' parameter.
			# name should be supplied if the item needs to be searchable.
			# verboseDesc should be supplied if the item needs to be
			# able to be described in greater detail in its own help screen.

		"""Instance initializer for new help items. The <text> argument should
			always be provided."""
		
		item = newHelpItem

		item._name = name	# Store the name (if any) for later use.
		item._text = text	# Store the text for later use.
		item._verboseDesc = verboseDesc	# Store the verbose description (if any).

	@property
	def name(thisHelpItem:HelpItem):
		return thisHelpItem._name

	@property
	def text(thisHelpItem:HelpItem):
		return thisHelpItem._text

	@property
	def verboseDesc(thisHelpItem:HelpItem):
		return thisHelpItem._verboseDesc


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HelpModule:

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
	#| 			should be unique among all modules.
	#|
	#| 		topicName - The name of the topic that this help module describes.
	#| 			This is used as a /help subcommand name for displaying this 
	#|			help module.
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
					name		:str = None,	# The name of this module.
					topicName	:str = None,	# The name of the module's topic.
					topicDesc	:str = None,	# A short description of the topic.
					introText	:str = None,	# The introductory text for this module.
					helpItems	:List[HelpItem] = None,	
						# The list of help items in this module.
					subModules	:List[HelpModule] = None,
						# The list of sub-modules in this module.
					parentModule:HelpModule = None,
						# The parent module of this module, if any.
				):
			# NOTE: Callers should really always supply most of these argument 
			# values, unless they are defined as subclass attributes. The
			# helpItems and subModules arguments are optional; individual
			# help items and sub-modules may be added later via the addItem()
			# and addSubModule() methods.
			# 
			# Note the topicDesc string specifies how this module is described 
			# when it appears as a sub-module of higher-level modules; it may 
			# also be used as a title string at the top of the screen for this 
			# module. 
			#
			# The 'intro' argument, if provided, gives text that should appear 
			# as a "module introduction" at the top of its screen.

		"""Instance initializer for new help modules. The <name> argument should
			always be provided, and is a module name used in debugging. The 
			<topicName> argument should also always be provided, as it is the
			subcommand name used to access the module via the /help command."""


		module = newHelpModule		# This new help module being initialized.


		# For arguments that are not provided, check to see if they are
		# defined as class attributes, and if so, use those values instead.

		if name is None and hasattr(module, 'name'):
			name = module.name

		if topicName is None and hasattr(module, 'topicName'):
			topicName = module.topicName
		
		if topicDesc is None and hasattr(module, 'topicDesc'):
			topicDesc = module.topicDesc
		
		if introText is None and hasattr(module, 'introText'):
			introText = module.introText
		
		if helpItems is None and hasattr(module, 'helpItems'):
			helpItems = module.helpItems
		
		if subModules is None and hasattr(module, 'subModules'):
			subModules = module.subModules

		if parentModule is None and hasattr(module, 'parentModule'):
			parentModule = module.parentModule


		# Initialize any remaining uninitialized arguments to placeholder values.

		if name is None:
			name = "(unnamed help module)"

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


		# Store the values obtained above as instance attributes.

		module.name = name
		module.topicName = topicName
		module.topicDesc = topicDesc
		module.introText = introText
		module.helpItems = helpItems
		module.subModules = subModules
		module.parentModule = parentModule

		# Call the .genHelpText() method to generate the help text for this
		# module and store it in the 'helpScreenText' attribute.

		module.genHelpText()

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

		# Start with the topic name and description.

		helpText = module.topicName + " - " + module.topicDesc + "\n\n"

		# Add the intro text for this module.

		helpText += module.introText + "\n\n"

		# Add the help items in this module.

		for helpItem in module.helpItems:
			helpText += helpItem.helpText + "\n\n"

		# Add the sub-modules in this module.
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

		if module.parentModule is not None:
			helpText += "\nUse '/up' to return to the " \
				+ module.parentModule.topicName + " topic.\n"

		# Store the generated help text in the 'helpScreenText' attribute.

		module.helpScreenText = helpText


	def lookupModule(thisHelpModule:HelpModule, moduleName:str=None, topicName:str=None):

		"""Lookup a help module by name and/or topic. The <moduleName> argument
			should be a module name, and the <topicName> argument should be a
			topic name. If either argument is not provided, it is ignored. If
			both arguments are provided, the first module matching either name
			is returned. If no module is found, None is returned. This help
			module and its recursive tree of sub-modules are searched in depth-
			first order. We also search the helpItems list of this module for
			any help items that are not proper sub-modules, and if there is one
			with a name attribute that matches moduleName or topicName, we
			return that help item as a temporary help module."""

		# NOTE TO SELF: We need to rethink whether it makes sense to have help
		# items as distinct from help modules.  It seems like it might be better
		# for each help item to also be a help module, and for the help module
		# to have its introText set to the topicDesc attribute of the help item.
		# I suppose we could just dynamically convert help items to temporary 
		# help modules as needed, while still keeping the help items in the 
		# helpItems list to distinguish them from proper sub-modules (which can
		# have recursive structures of their own).  This would also allow us to
		# still have help items that are not sub-modules, which might be useful 
		# for extra things like "See also" links.

		module = thisHelpModule		# This help module.

		# If both moduleName and topicName are None, return None.
		
		if moduleName is None and topicName is None:
			return None

		# If either of them matches this module directly, we'll just return 
		# this module.

		if moduleName == module.name or topicName == module.topicName:
			return module

		# We'll next search the helpItems list of this module for any help
		# items that are not proper sub-modules, and if there is one with a
		# name attribute that matches moduleName or topicName, we return that
		# help item as a temporary help module.

		for helpItem in module.helpItems:
			if helpItem.name == moduleName or helpItem.name == topicName:
				return ItemHelpModule(helpItem, parent=module)

		# If we get here, we didn't find a matching help item, so we'll search
		# the sub-modules of this module. For each, we check its name and
		# topic, and if it isn't a direct match, we then recursively search
		# its sub-modules.

		for subModule in module.subModules:
			if subModule.name == moduleName or subModule.topicName == topicName:
				return subModule
			else:
				subModuleResult = subModule.lookupModule(moduleName, topicName)
				if subModuleResult is not None:
					return subModuleResult

		# If we get here, we didn't find a matching module or help item.

		return None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

class ItemHelpModule(HelpModule):

	"""This is a temporary help module that is generated for a help item
		that is not a proper sub-module. It is used by the lookupModule()
		method of the HelpModule class. It is not added to the module
		hierarchy, but it may be set as the current help module and 
		displayed in the help window."""

	def __init__(self, helpItem:HelpItem, parent:HelpModule=None):

		"""Initialize the temporary help module."""

		# Set the name and topicName attributes to the .name attribute of the
		# help item.

		self.name = helpItem.name
		self.topicName = helpItem.name

		# Set the topicDesc attribute to the .text attribute of the help item.

		self.topicDesc = helpItem.text

		# Set the introText attribute to the .verboseDesc attribute of the
		# help item, if it is not None, or else set it to "No further
		# information is available for this item."

		if helpItem.verboseDesc is not None:
			self.introText = helpItem.verboseDesc
		else:
			self.introText = "No further information is available for this item."

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
	#|		showHelpScreen(thisHelpSystem:TheHelpSystem, moduleName:str=None, topicName:str=None)
	#|
	#|			Displays the help screen for the given module or topic name (if 
	#|			provided).  If neither a module name or a topic name is 
	#|			provided, the current module is used.  If the indicated module
	#|			is not found, a temporary error help module is displayed.  Note
	#|			that this method invokes the Help application, which must be
	#|			installed in the system and available, and the windowing system
	#|			must already be initialized and running.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def setAppSystem(thisHelpSystem:TheHelpSystem, theAppSystem:AppSystem_):
		thisHelpSystem.appSystem = theAppSystem

	def addToplevelItem(thisHelpSystem:TheHelpSystem, helpItem:HelpItem):
		thisHelpSystem.rootModule.addItem(helpItem)

	def addToplevelModule(thisHelpSystem:TheHelpSystem, helpModule:HelpModule):
		thisHelpSystem.rootModule.addModule(helpModule)

	def lookupModule(thisHelpSystem:TheHelpSystem, moduleName:str=None, topicName:str=None) -> HelpModule:

		"""Searches the help module hierarchy for a module with the given
			name (if provided) or topic name (if provided).  This will first
			search all sub-modules of the current module, in depth-first order,
			and then search all sub-modules of the root module, in depth-first
			order.  If no module is found, this method returns None."""

		helpSys = thisHelpSystem

		# First, check the module sub-hierarchy under the current module.
		if helpSys.currentModule is not None:
			module = helpSys.currentModule.lookupModule(moduleName, topicName)
			if module is not None:
				return module

		# If that fails, check the module sub-hierarchy under the root module.
		if helpSys.rootModule is not None:
			module = helpSys.rootModule.lookupModule(moduleName, topicName)
			if module is not None:
				return module

		# If we get here, we didn't find the module.
		return None