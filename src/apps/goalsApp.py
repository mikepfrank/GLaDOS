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

from	entities.entity				import	The_GoalsApp_Entity		# Us!

from	config.configuration		import	TheAIPersonaConfig
		# Singleton that provides the configuration of the current AI persona.

from	supervisor.action			import	(

				output,		# Used for normal output.
				info,		# Used for info output.
				warn,		# Output a warning message.
				error		# Output an error message.

			)

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

	@property
	def goals(goalList):
		return goalList._goals

	@property
	def nGoals(goalList):
		return len(goalList.goals)

	def __init__(goalList, goalRecsList:list=[]):

		goalList._goals = goals = []

		for goalRec in goalRecsList:

			realGoal = Goal(goalRec)

			goals.append(realGoal)

	def __str__(goalList):
		return str(goalList.goals)

	def _fixnums(goalList):

		"""This is a kludge to fix up the data structure when
			things get a little inconsistent."""

		goals = goalList.goals

		nGoals = goalList.nGoals

		for i in range(nGoals):

			goal = goals[i]

			goal.setNum(i+1)
			
		Goal._nGoals = nGoals


	def display(goalList):

		"""Generates a textual 'display' of this goal list.
			Default format has a blank line between the goals."""

		goals = goalList.goals

		if len(goals) == 0:
			displayStr = "\nNo goals have been added yet.\n\n"
			return displayStr

		displayStr = "\n"

		for goal in goals:
			
			displayStr = displayStr + '  ' + str(goal) + '\n\n'

		return displayStr

	def includes(goalList, goalDesc:str):

		"Returns True if the goal list already includes the given goal exactly."

		goals = goalList.goals
		for goal in goals:
			if goal.text == goalDesc:
				return True
		return False

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Commands to edit the goal list.

	def addGoal(goalList:GoalList, newGoalDesc:str):

		if goalList.includes(newGoalDesc):

			warn(The_GoalsApp_Entity(),
				 f"Can't add the goal \"{newGoalDesc}\", because it is already in your goals list.")

			return

		goals = goalList.goals

		goalRec = {'goal-text': newGoalDesc}
		newGoal = Goal(goalRec)

		goals.append(newGoal)

		output(The_GoalsApp_Entity(),
			   f"Added new goal #{newGoal.num}: {newGoalDesc}")

	def changeGoal(goalList:GoalList, goalNum:int, newGoalDesc:str):
		
		if goalList.includes(newGoalDesc):

			warn(The_GoalsApp_Entity(),
				 f"Can't change goal #{goalNum} to \"{newGoalDesc}\" because it is already in your goals list.")

			return

		goals = goalList.goals
		nGoals = goalList.nGoals

		if goalNum < 1 or goalNum > nGoals:
			error(The_GoalsApp_Entity(),
				  f"Can't change goal #{goalNum} because it doesn't exist!")
			return

		goal = goals[goalNum - 1]

		goal.text = newGoalDesc

		#goalList._fixnums()		# Temporary hack

		output(The_GoalsApp_Entity(),
			   f"Changed goal #{goal.num} to \"{newGoalDesc}\".")


	def deleteGoal(goalList:GoalList, goalNum:int):
		
		_logger.debug(f"goalList.deleteGoal(): Deleting goal #{goalNum}...")

		goals = goalList.goals
		nGoals = goalList.nGoals

		_logger.debug(f"goalList.deleteGoal(): There are {nGoals} before delete.")

		if goalNum < 1 or goalNum > nGoals:
			
			error(The_GoalsApp_Entity(),
				  f"Can't delete goal #{goalNum} because it doesn't exist!")

			return

		oldText = goals[goalNum-1].text

		for i in range(goalNum, goalList.nGoals):
			goals[i-1].text = goals[i].text

		goals = goals[:-1]			# Drops last element.
		goalList._goals = goals		# Need a cleaner way to do this.

		_logger.debug(f"goalList.deleteGoal(): There are {goalList.nGoals} after delete.")

		Goal._nGoals -= 1

		output(The_GoalsApp_Entity(),
			   f"Deleted old goal #{goalNum}, which was \"{oldText}\".")
		

	def insertGoal(goalList:GoalList, goalNum:int, newGoalDesc:str):

		if goalList.includes(newGoalDesc):

			warn(The_GoalsApp_Entity(),
				 f"Can't insert the goal \"{newGoalDesc}\", because it is already in your goals list.")

			return

		goalList.addGoal(newGoalDesc)

		if goalNum >= goalList.nGoals:	# User wanted it at end.
			return						# We're done.

		goals = goalList.goals

		# Pull goals forward.
		i = goalList.nGoals - 1
		while(1):
			goals[i].text = goals[i-1].text
			i -= 1
			if i < goalNum:
				goals[i].text = newGoalDesc		# Plop new guy down here.
				break

		output(The_GoalsApp_Entity(),
			   f"Inserted new goal at position #{goalNum}: {newGoalDesc}")


	def moveGoal(goalList:GoalList, fromGoal:int, toGoal:int):

		movingGoalText = goalList.goals[fromGoal-1].text

		info(The_GoalsApp_Entity(),
			"Moving goal by first deleting, then inserting...")

		goalList.deleteGoal(fromGoal)
		goalList.insertGoal(toGoal, movingGoalText)

		output(The_GoalsApp_Entity(),
			   f"Moved goal \"{movingGoalText}\" from #{fromGoal} to #{toGoal}.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class	Goals_Subcommand_: pass
class	Goals_Subcommand_(Subcommand):

	"""Abstract base class for /Goals subcommand classes."""

	def __init__(newGoalsSubcommand:Goals_Subcommand_,
				 subcmdWord:str,		# A single word naming the subcommand (e.g. 'add').
				 parent:Command=None):	

		#sc = newGoalsSubcommand
		#sc.word = subcmdWord

			# Fetch the arglist regex & docstr from the subclass.

		super().__init__(subcmdWord=subcmdWord, parent=parent)

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

	#word			= 'add'

	argListRegex	= strRegex		# '"<desc>"' argument.

	argListDoc		= ' "<desc>"'	# Documentation of arglist format.
	
	def handle(this, groups:list):

		sc = this	# This subcommand.

		desc = groups[0]
		
		_logger.info(f"Subcommand {sc.name} got desc=[{desc}].")

		The_Goals_App().addGoal(desc)


@singleton
class	The_GoalsChange_Subcommand(Goals_Subcommand_):

	name			= 'goals-change'

	#word			= 'change'

	argListRegex	= numRegex + r"(?:\s+to)?" + strRegex		# '<N> [to] "<desc>"' arguments.

	argListDoc		= ' <goalNum> [to] "<desc>"'			# Documentation of that.

	def handle(this, groups:list):
		
		sc = this	# This subcommand.

		goalNum = int(groups[0])

		desc = groups[1]

		_logger.info(f"Subcommand {sc.name} got goalnum={goalNum}, desc=[{desc}].")

		The_Goals_App().changeGoal(goalNum, desc)
		

@singleton
class	The_GoalsDelete_Subcommand(Goals_Subcommand_):

	name			= 'goals-delete'

	#word			= 'delete'

	argListRegex	= numRegex					# <N> argument.

	argListDoc		= ' <goalNum>'					# Document that.

	def handle(this, groups:list):

		sc = this	# This subcommand.

		goalNum = int(groups[0])
	
		_logger.info(f"Subcommand {sc.name} got goalnum={goalNum}.")

		The_Goals_App().deleteGoal(goalNum)
		


@singleton
class	The_GoalsInsert_Subcommand(Goals_Subcommand_):

	name			= 'goals-insert'

	#word			= 'insert'

	argListRegex	= numRegex + strRegex		# '<N> "<desc>"' arguments.

	argListDoc		= ' <goalNum> "<desc>"'			# Documentation of that.

	def handle(this, groups:list):
		
		sc = this	# This subcommand.

		goalNum = int(groups[0])

		desc = groups[1]

		_logger.info(f"Subcommand {sc.name} got goalnum={goalNum}, desc=[{desc}].")
	
		The_Goals_App().insertGoal(goalNum, desc)
		


@singleton
class	The_GoalsMove_Subcommand(Goals_Subcommand_):

	name			= 'goals-move'

	#word			= 'move'

	argListRegex	= numRegex + toNumRegex		# '<N> to <M>' arguments.

	argListDoc		= ' <fromNum> to <toNum>'				# Documentation of that.

	def handle(this, groups:list):
		
		sc = this	# This subcommand.

		fromGoal = int(groups[0])

		toGoal = int(groups[1])

		_logger.info(f"Subcommand {sc.name} got "
					 f"fromGoal={fromGoal}, toGoal={toGoal}.")

		The_Goals_App().moveGoal(fromGoal, toGoal)


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

				/goal change <N> [to] "<desc>"

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

	#usageHint = "To edit, type: '/goal (add|change|delete|insert|move) [<N> [to <M>]] [\"<desc>\"]'."
	#usageHint = "USAGE: /goal (add|change|delete|insert|move) <arguments>"
	usageHint = "USAGE: '/goal (add|change|delete|insert|move) [<N> [to <M>]] [\"<desc>\"]'."

	def appSpecificInit(theGoalsApp:The_Goals_App, appConf:dict):

		"""The is a standard Application_ method that is called
			to perform application-specific initalization at app
			creation time.  When this is called, our window has
			already been created, but is not yet displayed."""

		app = theGoalsApp

		_logger.debug("goalsApp.appSpecificInit(): Initializing Goals app...")

		app.entity = The_GoalsApp_Entity()

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

		win.addText(goalsText + app.usageHint)

		#|==================================================
		#| Our next major initialization task is to create
		#| & install our command module & our help module.

			# Create our help module (self-installs).
		app._helpModule = The_Goals_HelpModule()


	@property
	def goalList(app):
		return app._goalList


	def updateWindow(theGoalsApp:The_Goals_App):

		app = theGoalsApp

		goalList = app.goalList

		goalsText = goalList.display()
		win = app.window

		win.clearText()		# Clear old window text (but postpone update).

		win.addText(goalsText + app.usageHint)

		win.redisplay(loudly=False)


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

	
	#|======================================================================
	#| Below here are the actual subcommands supported by the Goals app.
	#| Or rather, their internal implementations.

	def addGoal(theGoalsApp:The_Goals_App, newGoalDesc:str):

		app = theGoalsApp
		goalList = app.goalList

		goalList.addGoal(newGoalDesc)

		app.updateWindow()


	def changeGoal(theGoalsApp:The_Goals_App, goalNum:int, newGoalDesc:str):

		app = theGoalsApp
		goalList = app.goalList

		goalList.changeGoal(goalNum, newGoalDesc)

		app.updateWindow()


	def deleteGoal(theGoalsApp:The_Goals_App, goalNum:int):

		app = theGoalsApp
		goalList = app.goalList

		goalList.deleteGoal(goalNum)

		app.updateWindow()


	def insertGoal(theGoalsApp:The_Goals_App, goalNum:int, newGoalDesc:str):

		app = theGoalsApp
		goalList = app.goalList

		goalList.insertGoal(goalNum, newGoalDesc)

		app.updateWindow()


	def moveGoal(theGoalsApp:The_Goals_App, fromGoal:int, toGoal:int):

		app = theGoalsApp
		goalList = app.goalList

		goalList.moveGoal(fromGoal, toGoal)

		app.updateWindow()
