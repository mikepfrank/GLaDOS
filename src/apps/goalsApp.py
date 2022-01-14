# goalsApp.py

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [ 'The_Goals_App' ]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from os import path
from json import load as json_load
from hjson import load as hjson_load

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from infrastructure.logmaster	import getLoggerInfo, ThreadActor

global _logger		# Logger serving the current module.
global _component	# Name of our software component, as <sysName>.<pkgName>.
			
(_logger, _component) = getLoggerInfo(__file__)		# Fill in these globals.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from	infrastructure.decorators	import	singleton, classproperty
		# A simple decorator for singleton classes.

from	config.configuration		import	TheAIPersonaConfig
		# Singleton that provides the configuration of the current AI persona.

from	commands.commandInterface	import	(
				Command,
				Subcommand,
				CommandModule,
				TheCommandInterface
			)

from	helpsys.helpSystem			import	HelpModule	# We'll subclass this.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Forward declarations that allow us to use these names as type hints early on.

class The_Goals_App: pass		# Anchor point for this module.

class The_Goals_Command: pass		# The /Goals command.
class The_Goals_CmdModule: pass		# Command module for the Goals app.
class The_Goals_HelpModule: pass	# Help module for the Goals app.

class GoalList: pass			# List-of-goals structure.
class Goal: pass				# And individual goal

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Goal:

		# Class variable: How many goals have been created?
	_nGoals = 0
	
	@classproperty
	def nGoals(thisCls):
		return thisCls._nGoals

	@classmethod
	def inc_nGoals(thisCls):
		thisCls._nGoals = thisCls.nGoals + 1

	def __init__(goal, goalRec:dict):

		goalText = goalRec['goal-text']
		goal.text = goalText

		goal.inc_nGoals()		# Increment seq no
		goal.num = goal.nGoals	# Assign sequence number

	def setNum(goal, n:int):
		goal.num = n

	def __str__(goal):
		return f"{goal.num}.  {goal.text}"
		

class GoalList:

	def __init__(goalList, goalRecsList:list):

		goalList._goals = goals = []

		for goalRec in goalRecsList:

			realGoal = Goal(goalRec)

			goals.append(realGoal)

	def display(goalList):

		"""Generates a textual 'display' of this goal list.
			Default format has a blank line between the goals."""

		goals = goalList._goals

		displayStr = "\n"

		for goal in goals:
			
			displayStr = displayStr + '  ' + str(goal) + '\n\n'

		return displayStr




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class	Goals_Subcommand_: pass
class	Goals_Subcommand_(Subcommand):

	"""Abstract base class for /Goals subcommand classes."""

	def __init__(newGoalsSubcommand:Goals_Subcommand_,
			subcmdWord:str):	# A single word naming the subcommand (e.g. 'add').

			# Fetch the arglist regex & docstr from the subclass.

		super().__init__()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Definitions for specific /Goals subcommands.

numRegex = r"\s+([1-9][0-9]*)"		# Matches a goal number argument " <N>".
	# Whitespace, then a digit 1-9, then optional additional digits.
	# Capture the number in a group.

toNumRegex = r"\s+to" + numRegex	# Matches " to <M>".
	# Whitespace, then "to", then a number.

strRegex = r'\s+"([^"]*)"'	# Matches a string argument ' "<str>"'.
	# Whitespace, then a double quotation mark, then any number of
	# characters that are not double quotation marks, then another
	# double quotation mark. Capture everything inside the quotation
	# marks as a group.

@singleton
class	The_GoalsAdd_Subcommand(Goals_Subcommand_):

	name			= 'goals-add'

	argListRegex	= strRegex		# '"<desc>"' argument.

	argListDoc		= ' "<desc>"'	# Documentation of arglist format.
	
	def handle(this, groups:list):

		sc = this	# This subcommand.

		desc = groups[0]
		
		_logger.info(f"Subcommand {sc.name} got desc=[{desc}].")


@singleton
class	The_GoalsChange_Subcommand(Goals_Subcommand_):

	name			= 'goals-change'

	argListRegex	= numRegex + strRegex		# '<N> "<desc>"' arguments.

	argListDoc		= ' <N> "<desc>"'			# Documentation of that.

	def handle(this, groups:list):
		
		goalNum = int(groups[0])

		desc = groups[1]

		_logger.info(f"Subcommand {sc.name} got goalnum={goalNum}, desc=[{desc}].")


@singleton
class	The_GoalsDelete_Subcommand(Goals_Subcommand_):

	name			= 'goals-delete'

	argListRegex	= numRegex					# <N> argument.

	argListDoc		= ' <N>'					# Document that.

	def handle(this, groups:list):

		goalNum = int(groups[0])
	
		_logger.info(f"Subcommand {sc.name} got goalnum={goalNum}.")


@singleton
class	The_GoalsInsert_Subcommand(Goals_Subcommand_):

	name			= 'goals-insert'

	argListRegex	= numRegex + strRegex		# '<N> "<desc>"' arguments.

	argListDoc		= ' <N> "<desc>"'			# Documentation of that.

	def handle(this, groups:list):
		
		goalNum = int(groups[0])

		desc = groups[1]

		_logger.info(f"Subcommand {sc.name} got goalnum={goalNum}, desc=[{desc}].")
	

@singleton
class	The_GoalsMove_Subcommand(Goals_Subcommand_):

	name			= 'goals-move'

	argListRegex	= numRegex + toNumRegex		# '<N> to <M>' arguments.

	argListDoc		= ' <N> to <M>'				# Documentation of that.

	def handle(this, groups:list):
		
		fromGoal = int(groups[0])

		toGoal = int(groups[1])

		_logger.info(f"Subcommand {sc.name} got "
					 f"fromGoal={fromGoal}, toGoal={toGoal}.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class	The_Goals_Command(Command):

	"""
		The '/Goals' command just dispatches to any of several subcommands:

			/goal add "<desc>"
			/goal change <N> "<desc>"
			/goal delete <N>
			/goal insert <N> "<desc>"
			/goal move <N> to <M>

		These are defined in their respective subcommand classes.

	"""

	name = 'Goals'	# Case-insensitive though. Prefix-invocable.

		# Override the default value of this class-level variable,
		# because we do have subcommands.
	hasSubcmds = True

		# The following class-level constant dict maps the symbolic words
		# for the /Goals subcommands to their corresponding subcommand objects.
	subcommand_classMap = {
			'add':		The_GoalsAdd_Subcommand,
			'change':	The_GoalsChange_Subcommand,
			'delete':	The_GoalsDelete_Subcommand,
			'insert':	The_GoalsInsert_Subcommand,
			'move':		The_GoalsMove_Subcommand
#			'add':		The_GoalsAdd_Subcommand.__wrapped__,
#			'change':	The_GoalsChange_Subcommand.__wrapped__,
#			'delete':	The_GoalsDelete_Subcommand.__wrapped__,
#			'insert':	The_GoalsInsert_Subcommand.__wrapped__,
#			'move':		The_GoalsMove_Subcommand.__wrapped__
		}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Goals_CmdModule(CommandModule):

	"""This singleton class implements the command module for the
		Goals app. It provides the version of the '/Goals' command
		that takes arguments, which dispatches to the various
		subcommands that may be used to edit the goal list."""

	def __init__(theNewGoalsCmdModule:The_Goals_CmdModule):
	
		"""Singleton instance initializer for the The_Goals_CmdModule class.
			Its job is to construct the command module by adding all of its
			individual commands and subcommands to it."""
		
		thisCmdModule = theNewGoalsCmdModule

		_logger.info("Initializing the Goals app's command module...")

		super().__init__(desc="Goals app's command module")
			# Default initialization for command modules.

			# Install this module in the command interface.
		cmdIF = TheCommandInterface()
		cmdIF.installModule(thisCmdModule)

	def populate(theGoalsCmdModule:The_Goals_CmdModule):

		_logger.info("Populating the Goals app's command module with commands...")

		goalsCmdMod = theGoalsCmdModule

			# This initializes the Goals command.
		The_Goals_Command(cmdModule=goalsCmdMod)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Goals_HelpModule(HelpModule):

	"""This singleton class implements the help module for the Goals
		app. It provides an overview of the app, and documents its
		associated commands and subcommands."""

	pass	# TO DO: Fill in implementation.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Goals_App(Application_):

	"""
		The_Goals_App			    [public singleton class--GLaDOS application]
		=============

			This is a singleton class implementing the 'Goals App' or
			"goal-maintenance application" that is available in GLaDOS.

			The idea behind this app is that it allows the A.I. to view
			and edit its list of high-level goals.

			Its window normally is moved, upon first being opened, to an
			anchoring position near the bottom of the AI's receptive field,
			just above the pinned elements such as the input area and the
			prompt separator.

			The Goals app lists the current goals in its window, and when
			its window is open, it enables its commend module, which
			provides the following commands:

				/goal (add|change|delete|insert|move) <N> [to <M>] ["<desc>"]

				/goal add "<desc>"

					Adds a new goal at the end of the list with description <desc>.

				/goal change <N> "<desc>"

					Allows the AI to update the text of goal #<N> to <desc>.

				/goal delete <N>

					Deletes goal #<N>.

				/goal insert <N> "<desc>"

					Inserts a new goal at position #<N> (displacing others down).
				
				/goal move <N> to <M>

					Moves goal #N to position #M in the list (moving others as needed).
			

			The 'Goals' app can be used by the A.I. to modify its list
			of high-level goals.
	"""

	def appSpecificInit(theGoalsApp:The_Goals_App, appConf:dict):

		"""The is a standard Application_ method that is called
			to perform application-specific initalization at app
			creation time.  When this is called, our window has
			already been created, but is not yet displayed."""

		app = theGoalsApp

		_logger.debug("goalsApp.appSpecificInit(): Initializing Goals app...")

			#----------------------------------------------------------
			# First, get the AI persona configuration, because it
			# contains key information we need, such as the location
			# of the AI's data directory.

		aiConf = TheAIPersonaConfig()
			# Note this retrieves the singleton instance
			# of the TheAIPersonaConfig class.

			#------------------------------------------------------
			# Next, get the location of the AI's data directory,
			# which is in the AI persona configuration object.

		aiDataDir = aiConf.aiDataDir

			#-----------------------------------------------------
			# Next, we need to get the name of the goals file
			# (relative to that directory). This comes from our
			# app-specific configuration data.

		goalsFilename = appConf['goals-filename']
			# Usually this is just cur-goals.json.
		from json import load	# Make sure that's the load we're using.

			#------------------------------------------------------
			# Next, we need to construct the full pathname of the
			# goals JSON file.

		goalsPathname = path.join(aiDataDir, goalsFilename)

			#------------------------------------------------------
			# Next, we need to actually load the info text from the
			# appropriate data file in that directory.

		try:

			_logger.debug(f"[GoalsApp] Attempting to open {goalsPathname}...")

			with open(goalsPathname) as goalFile:

				_logger.debug(f"[GoalsApp] Loading goals from {goalsPathname}...")
					
				goalsRecord = json_load(goalFile)

		except:	# Assume this is a file not found error.

				_logger.warn(f"[GoalsApp] Unable to open {goalsPathname}; reverting to init-goals.hjson.")

					# Revert to this file if cur-goals.json doesn't exist.
				goalsPathname = path.join(aiDataDir, 'init-goals.hjson')

				with open(goalsPathname) as goalFile:
					
					_logger.debug(f"[GoalsApp] Loading goals from {goalsPathname}...")
					
					goalsRecord = hjson_load(goalFile)

			#-----------------------
			# Parse the goal record.

		app._goalList = goalList = app.parseGoals(goalsRecord)

		goalsText = goalList.display()

		_logger.info(f"[GoalsApp] Loaded the following list of goals from {goalsPathname}:\n\n" + goalsText)

			#---------------------------------
			# Add the goal list to the window.

		win = app.window

		win.wordWrap = True		# Turn on word-wrapping.
		win.autoSize = True		# Turn on auto-sizing

		_logger.info(f"Window {win.title} has wordWrap={win.wordWrap}.")

			#----------------------------------------------
			# Finally, we have our window display the text.

		win.addText(goalsText + "To edit, type: '/goal (add|change|delete|insert|move) [<N> [to <M>]] [\"<desc>\"]'.")


		#|==================================================
		#| Our next major initialization task is to create
		#| & install our command module & our help module.

			# Create our help module (self-installs).
		app._helpModule = The_Goals_HelpModule()


	def createCommandModule(theGoalsApp:The_Goals_App):
		
		app = theGoalsApp

			# Create our command module (self-installs).
		app._cmdModule = cmdMod = The_Goals_CmdModule()

		return cmdMod


	def parseGoals(theGoalsApp:The_Goals_App, goalsRec:dict):

		app = theGoalsApp

		goalRecsList = goalsRec['goal-list']

		goalList = GoalList(goalRecsList)

		return goalList

	
