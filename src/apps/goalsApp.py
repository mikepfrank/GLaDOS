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

from	commands.commandInterface	import	Command,CommandModule	# We'll subclass these.

from	helpsys.helpSystem			import	HelpModule	# We'll subclass this.

from	.application				import	Application_
		# Base class from which we derive subclasses for specific applications.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class The_Goals_App: pass		# Anchor point for this module.

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
		return f"{goal.num}.\t{goal.text}"
		

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

		displayStr = ""

		for goal in goals:
			
			displayStr = displayStr + '\t' + str(goal) + '\n\n'

		return displayStr

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class	The_Goals_Command(Command):

	"""The '/Goals' command launches the Goals app (if not already launched),
		moves its window to the bottom of the receptive field, and """

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@singleton
class The_Goals_CmdModule(CommandModule):

	"""This singleton class implements the command module for the
		Goals app. It provides the '/Goals' command (which launches
		the app), as well as the '/goal' command which is used 
		within the app, and its subcommands."""

	def __init__(theNewGoalsCmdModule:The_Goals_CmdModule):

		"""Singleton instance initializer for the The_Goals_CmdModule class.
			Its job is to construct the command module by adding all of its
			individual commands and subcommands to it."""
		
		pass

	pass	# TO DO: Fill in implementation.

@singleton
class The_Goals_HelpModule(HelpModule):

	"""This singleton class implements the help module for the Goals
		app. It provides an overview of the app, and documents its
		associated commands and subcommands."""

	pass	# TO DO: Fill in implementation.

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

				/goal (add|change|delete|insert|move) <N> [to <M>]

				/goal add

					Adds a new goal at the end of the list.

				/goal change <N>

					Allows the AI to update the text of goal #<N>.

				/goal delete <N>

					Deletes goal #<N>.

				/goal insert <N>

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

		win.addText(goalsText)

		#|==================================================
		#| Our next major initialization task is to create
		#| & install our command module & our help module.

			# Create our command module (self-installs).
		app._cmdModule = The_Goals_CmdModule()

			# Create our help module (self-installs).
		app._helpModule = The_Goals_HelpModule()

	def parseGoals(theGoalsApp:The_Goals_App, goalsRec:dict):

		app = theGoalsApp

		goalRecsList = goalsRec['goal-list']

		goalList = GoalList(goalRecsList)

		return goalList

	
