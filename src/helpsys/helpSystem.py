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

from	infrastructure.decorators	import	singleton, classproperty
		# A simple decorator for singleton classes.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Forward class declarations (for use in type hints only).

class TheHelpSystem: pass	# Singleton for the entire help system as a whole.

class _TheRootHelpModule: pass	# The root node of the help-module hierarchy.
class HelpModule: pass		# An help module, which can contain items and sub-modules.
class HelpItem: pass		# An individual help item that may be contained in a module.

#===============================================================================
# Class definitions.

class HelpItem:

	"""A help item refers to an individual piece of guidance that may appear
		in a help module. This is as opposed to a sub-module, which may be
		further drilled down into. The most important property of a help item
		is its textual appearance, wich will appear in the help window when
		that item is displayed."""

	def __init__(newHelpItem:HelpItem, text:str="(missing help item text)"):
			# NOTE: Callers should really always supply the 'text' parameter.

		"""Instance initializer for new help items. The <text> argument should
			always be provided."""
		
		item = newHelpItem

		item._text = text	# Store the text for later use.

	@property
	def text(thisHelpItem:HelpItem):
		return thisHelpItem._text


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class HelpModule:

	"""A help module is a collection of help items and sub-modules (which are
		in turn also help modules). It corresponds roughly to a screen viewable
		in the Help app's window, which displays the items and sub-modules
		contained in the module."""

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| Class properties. May be overridden by subclasses.
	#|
	#| 		helpScreenText - The complete text of the help screen for this
	#| 			module. This is used when the module is displayed in the
	#| 			Help app's window. It is constructed from the module's
	#| 			intro text, the text of its help items, and the text of
	#| 			its sub-modules. This is a class property, so it may be
	#| 			overridden by subclasses.
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def __init__(newHelpModule:HelpModule, name:str="(unnamed help module)",
					topic:str="(unspecified topic)", intro:str=None):
			# NOTE: Callers should really always supply the 'name' and 'topic' parameters.
			# The topic string specifies how this module is described when it appears as
			# a sub-module of higher-level modules; it may also be used as a title string
			# at the top of the screen for this module. The 'intro' argument, if provided,
			# gives text that should appear as a "module introduction" at the top of its
			# screen.

		"""Instance initializer for new help modules. The <name> argument should
			always be provided, and is a module name used in debugging. The <topic>
			argument should also always be provided."""

		pass

	

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class _TheRootHelpModule(HelpModule):

	"""This is the unique help module that sits at the root of the help module
		hierarchy.  It is initialized when the help system is initialized.
		Other help modules will get installed somewhere under this module."""

	def __init__(theRootHelpModule:_TheRootHelpModule):

		rootModule = theRootHelpModule

		# This creates a default intro text string to appear in the root help
		# module. Note that may can be overridden later by the 'main-msg'
		# app-config parameter in the glados-config.hjson file when the Help
		# app initializes.

		intro=("Welcome to GLaDOS, the General Lifeform's automated Domicile "
			   "Operating System, (c)2020-23 Metaversal Constructions.  This "
			   "is the top-level screen of GLaDOS's interactive Help system.  "
			   "Topics and subtopics are organized in hiarchical menus, and "
			   "you can drill down into them by typing the topic number.")

			# This calls the default instance initializer for all help modules.
		super(_TheRootHelpModule.__wrapped__, rootModule).__init__(name='root-module',
		   topic="How to Use the GLaDOS Operating Environment", intro=intro)

		

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class TheHelpSystem:

	"""This singleton class anchors the help system. Other systems may
		access it by calling the class constructor TheHelpSystem(),
		which just returns the singleton instance."""

	def __init__(theHelpSystem:TheHelpSystem):

		helpSys = theHelpSystem
		
		# Create and store the root help module.
		helpSys._rootModule = _TheRootHelpModule()

	@property
	def rootModule(theHelpSystem:TheHelpSystem):
		return thehelpsystem._rootModule
