#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					TOP OF FILE:	infrastructure/worklist.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		infrastructure/worklist.py		 [Python module source file]
		
	MODULE NAME:	infrastructure.worklist
	IN PACKAGE:		infrastructure
	FULL PATH:		$GIT_ROOT/GLaDOS/src/infrastructure/worklist.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.server.work (Multithreaded work management facility)


	MODULE DESCRIPTION:
	===================
	
		Originally developed as part of the COSMICi project, this module 
		provides a "work-management facility" for use in multithreaded 
		environments.
		
		Rationale: Often, in a multithreaded environment, there is a piece
		of work (a task) that needs to be done within a certain predesignated 
		thread to avoid concurrency issues (such as manipulating the state of 
		a complex UI), but meanwhile there are other, asynchronously running 
		threads that are providing the work items, and ordering (triggering) 
		the work items (tasks) to be carried out.
		
		Or, a similar scenario, a certain thread (e.g. a UI event handler) 
		generates a sequence of tasks that need to get done (in a certain 
		order), but the thread does not want to itself wait for the tasks to 
		be completed before going on to other urgent tasks (like redrawing UI 
		elements).	So it would like to pass the tasks to some other, 
		background thread whose job it is to accomplish them.
		
		The idea of the Worklist abstraction is that it makes it "easy" to pass 
		bits of work from one thread to another, and get work done in the 
		background.
		
		In the context of the GLaDOS server, the primary use of worklists is
		to keep track of a queue of curses-associated tasks to be carried out,
		where these tasks typically involving updating the curses display.	A
		single thread called the "display driver" then executes these tasks.
		This effectively serializes execution of these tasks, and ensures that 
		the curses library itself always remains in a self-consistent state.
		Other threads can submit tasks to the display driver's worklist for 
		processing, including background processing, so that the other threads
		don't have to wait for the display to finish updating to continue their
		own work.

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


#	Classes provided:
#
#		Flag - A Boolean condition that can be waited on.
#			A customer can check (non-blocking) whether the
#			flag is raised, or he can wait (blocking, with
#			optional timeout) for it to be raised.	All
#			waiters are notified when the flag is raised.
#			(Note: This one has since been moved out to its
#			own module, called "flag".)
#
#		WorkItem - A specific task that needs to be done.
#			It carries various flags for requesting and
#			reporting various actions.
#
#		Worklist - A FIFO queue of work items that need
#			doing. A worklist can have one or more workers
#			assigned to follow it.	The presumption is
#			that any worker assigned to the worklist
#			could do any item that might appear on it.
#			(Although if a worker gets a task it can't
#			do, it could put it back on the bottom of
#			the list - though this could lead to task
#			starvation, so is not recommended.)
#
#		Delegator - A special kind of thread whose job
#			it solely to delegate work items on a given
#			worklist to individual workers -
#			preferentially, ones who are not already
#			busy (if any).
#
#			The general process for a delegator is as
#			follows:  Wait for a work item to appear on
#			the work list.	Once we have gotten a work
#			item, check all workers assigned to this
#			worklist to see if any are free.  If one is,
#			drop the work item on his desk.	 If none are
#			free, then find the worker who has the
#			smallest total number of items waiting on all
#			his incoming assignments plus his inbox, and
#			drop the item onto the assignment between our
#			worklist and that worker.
#			
#		Assignment - A medium-sized queue of work items
#			from a given worklist that have been delegated
#			to a given worker.	Assignments allow tasks
#			from a given worklist that have been assigned
#			to one worker to be taken over by another worker
#			assigned to that worklist who is wandering
#			around looking for some work to do.
#
#		Inbox - A small queue of work items that are
#			"owned" by a specific worker, i.e., that cannot
#			be reassigned to other workers.	 
#
#		Desk - A very small queue of work items that are
#			about to be done by a specific worker.	
#
#		Worker - A thread whose sole job is to wait for work
#			items to appear on its desk, in its inbox, or on
#			any of the worklists it is following.
#
#				free - A flag: Is the worker available
#						(i.e., not currently busy)?
#
#			The general process for each worker is as follows:
#			If there is a work item on my desk then do it;
#			otherwise, check my inbox, and if there is a work
#			item there, then move it to my desk; next, check
#			all my incoming assignments for work; next, check
#			all the outgoing assignments of all my worklists
#			for work.  If no work is found, then just stare at
#			my desk and wait for someone to drop a piece of
#			work on it.
#
#==============================================================

	#---------------------------------------
	# Import some standard python modules.

import sys, traceback	# To facilitate debugging.

from threading import Thread, RLock, current_thread	   # High-level threading module.

from numbers import Number		# Used in some argument type hints.

	#-----------------------------------------
	# Import some of our own custom modules.

from .flag import *		   # Waitable Boolean condition variables.

from .desque import *	# Say "desk" - Double-ended synchronized queues.
	#-We import the public names of desque because our Worklist
	# class effectively extends the Desque class.

import infrastructure.logmaster			   # For accessing logmaster.initialized
from .logmaster import *	 # Our customized logging facility.
	# - Names imported for convenience.

from .utils import bind		 # We use the bind() function in HireThread

_logger = getLogger(appName + ".work")

	#--------------------------------------------------------------------
	# Our public (exported) names.	These are the names that will get
	# imported to another module that does "from worklist import *".

__all__ = ['Empty', 'Full',		# Exceptions inherited from Desque.
		   'WorkItemException', 'NotOwner', 'AlreadyStarted',	# new exceptions
		   'WorkAborted', 'EarlyCompletion', 'ExitingByRequest',
		   'WorkerExiting', 'NullCallable', 'WorklistClosed',
		   'WorklistClosedForever', 'WorkerException', 
		   'WorkItem',		# Other classes
		   'Worklist',
		   'Worker', 'RPCWorker',
		   'HireThread',		   # Functions
		   ]

	#--------------------------------------------------------------------
	#	Exception classes.	Define the specific new types of exceptions
	#		that may be raised within this module.
	#--------------------------------------------------------------------

		# This base class for all exceptions in this module simply
		# sets the default logger for these exceptions to this
		# module's logger.

class WorklistModuleException(LoggedException):
	defLogger = _logger

		#-----------------------------------------------------------------
		#	WorkItemException [module public class] - The superclass of
		#		special exceptions raised by objects of class WorkItem.

class WorkItemException(WorklistModuleException): pass

		#-----------------------------------------------------------------
		#	NotOwner [module public class] - Exception indicating that a 
		#		thread that did not own this work item tried to execute
		#		certain methods only allowed to be executed by its owner.

class NotOwner(WorkItemException, ErrorException): pass

		#-----------------------------------------------------------------
		#	AlreadyStarted [module public class] - An exception declaring
		#		that a WorkItem (task) could not be started, or could not
		#		be assigned to a new owner, because work on it has already
		#		been started previously.

class AlreadyStarted(WorkItemException, ErrorException): pass

		#-----------------------------------------------------------------
		#	WorkAborted [module class] - An exception declaring that we
		#		quit work early on a given WorkItem b/c the abortRequested
		#		flag was raised.

class WorkAborted(WorkItemException, InfoException): pass

	#-----------------------------------------------------------------
	#	EarlyCompletion [module class] - A special class of exceptions
	#		That simply denotes that a task has used the statement
	#		"raise EarlyCompletion" to break out of itself early,
	#		somewhere deep down inside the call stack.	This invokes
	#		'finally' clauses as needed on the way out to do clean-up.
	#		EarlyCompletion does indicate completion of the task, so
	#		a worker should mark that the work item as complete when
	#		catching this exception.  This is taken care of
	#		automatically by WorkItem's do() method.  To denote that
	#		the work item is NOT complete, the task should raise
	#		some other class of exception.

class EarlyCompletion(WorkItemException, InfoException): pass

	#-------------------------------------------------------------------
	#	NullCallable [module class] - Callable in the worklist is None.

class NullCallable(WorkItemException, ErrorException): pass


	#-----------------------------------------------------
	# Special exceptions that worklists might raise.

class WorklistException(WorklistModuleException): pass

		# Worklist is closed (temporarily or permanently).

class WorklistClosed(WorklistException, WarningException): pass

		# Worklist is closed forever.

class WorklistClosedForever(WorklistClosed, WarningException): pass

		# Argument to addItem() is not a work item.

class NotAWorkItem(WorklistException, ErrorException, TypeError): pass

	#--------------------------------------------------------
	# Special exceptions that worker objects might raise.

class WorkerException(WorklistModuleException): pass

		# Raising this exception denotes that the worker thread
		# is exiting because its exitRequested flag was raised.

class ExitingByRequest(WorkerException, InfoException): pass

		# A request of a worker could not be satisfied because
		# that worker is currently in the process of exiting,
		# and/or its worklist has been closed to new items.

class WorkerExiting(WorkerException, WarningException): pass

	#-----------------------------------------------------------------
	# Worklist [module public class] - This early base class
	#		declaration is so that WorkItem can refer to a generic
	#		Worklist type in argument type declarations, even though
	#		the actual worklist classes are defined later.	It is
	#		overridden later by a more detailed class definition.

class Worklist(Desque): pass


	#--------------------------------------------------------------------
	# WorkItem [module class] - An item that may be put on a worklist;
	#		a task that needs to be done at some point in the future.
	#		Normally, a WorkItem may only be on one worklist at a time.
	#
	#		Work items include flags to keep track of whether they
	#		have been done yet or not, so that when they are
	#		completed, their customers can be notified.	 They also
	#		keep track of whether work on them has started, whether
	#		they failed, their results, etc.
	#
	#		A work item also has a flag called pauseRequested; the
	#		intent of this is that the thread working on the task
	#		should check this flag periodically (when convenient),
	#		and if it is up, it should then raise the paused flag,
	#		and wait for the pauseRequested flag to be lowered.
	#		This allows the worker thread to be externally
	#		paused.	 However, there is no guarantee that the
	#		worker will check for pause requests frequently (or
	#		at all).
	#
	#		Similarly, a flag called abortRequested requests the
	#		worker thread to please abort work on this item.
	#
	#		Currently, there is no easy way that a work item can be
	#		suspended in the middle, put back on some work queue,
	#		and completed later by some other thread.  This could
	#		possibly be implemented using generators, but that
	#		would require the task's code to be written in a special
	#		way using periodic yield statements, and an enclosing
	#		loop to run through the iterator until suspended.
	#
	#		However, work on a task could be suspended and then
	#		resumed later within the SAME worker thread by simply
	#		suspending the thread itself.

class WorkItem:
	
	#------------------------------------------------------------
	# Instance variables:
	#
	#		lock:RLock - A reentrant mutex lock that is designed
	#				to prevent more than one thread from working
	#				on a given work item at the same time.
	#
	#		maker:Thread - The thread (usually a worker thread)
	#				that created this work item.
	#
	#		task:callable - A callable object representing the
	#				work that needs to be done.	 We call it to
	#				do the actual work.	 It should take one
	#				argument, which will be the whole workItem
	#				structure of which it is a part.
	#
	#		worklist:Worklist - The work list that this
	#				particular work item is on, if any (or None).
	#
	#		owner:Thread - The worker thread that currently
	#				owns this WorkItem.	 Usually this will be
	#				a member of the Worker subclass of Thread.
	#
	#		result:object - The result, if any, that was
	#				returned by the callable which was invoked
	#				to execute this work item.
	#
	#		exception:BaseException - The exception, if any,
	#				that was raised by the callable which was
	#				invoked to execute this work item
	#
	#	The following are flags for various conditions; 
	#	customers can wait for any these flags to be raised
	#	using their wait() methods.	 The only ones that may
	#	be lowered are the ...Requested flags, and "paused".
	#	(I guess "owned" could also be lowered, if an
	#	unstarted item got moved back out to a project
	#	worklist.)	onWorklist could also go down.
	#
	#		owned:Flag - Declares that this task is owned
	#				(assigned to) a specific worker.
	#
	#		onWorklist:Flag - Declares that this task is on
	#				some worklist or other.
	#
	#		inProgress:Flag - Declares that some thread has started
	#				to work on this particular task.
	#
	#		pauseRequested:Flag - Declares that somebody wants
	#				work on this task to be suspended ASAP.
	#
	#		paused:Flag - Declares that work on this task has
	#				been suspended, and will remain suspended
	#				until the pauseRequested flag is lowered.
	#
	#		abortRequested:Flag - Declares that somebody wants
	#				work on this task to be terminated ASAP,
	#				regardless of successful completion of the
	#				task.  (May not be honored by task code.)
	#
	#		exitRequested:Flag - Declares that somebody wants
	#				the task to terminate as soon as it can
	#				do so normally. (And consider itself done.)
	#
	#		haveResult:Flag - Declares that this task has
	#				yielded a result (or an exception).
	#
	#		stopped:Flag - Declares that work on this task has
	#				stopped (either because it completed normally,
	#				or due to an abort or other exceptional
	#				condition).
	#
	#		done:Flag - Declares that this work item is finished.
	#				Customers can wait for the work to be done
	#				using workItem.wait().
	#
	#		failed:Flag - Declares that an attempt to complete
	#				this work item failed due to an exception
	#				other than EarlyCompletion.
	#
	#---------------------------------------------------------------
	
	def __init__(self, callable=None, owner=None, desc=None):
		self.lock = RLock()				# Reentrant lock for thread-safe access to class and instance variables.
		with self.lock:					# Go ahead and use it, just in case.
			self.maker = current_thread()
				#- Remember what thread created this work item.
			self.task = callable			# Callable object for carrying out this task.
			self.worklist = None			# Worklist this task is on.	 At creation, this task is not on any worklists yet.  It may be put on one later.
			self.owner = owner				# Worker assigned this task.  By default, this task has no owner initially (one may be assigned later).
			self.desc = desc				# Description of this task.  None by default.
			self.result = None				# Result returned by this task.	 Initially, none yet.
			self.exception = None			# Exception raised by this task.  Initially, none yet.

				# Waitable flags for announcing various conditions.
			self.owned			= Flag(owner)	# That this task is owned.	Raise flag initially if owner is not None.
			self.onWorklist		= Flag()	# That this task is on a worklist.
			self.inProgress		= Flag()	# That work on this task has started.
			self.pauseRequested = Flag()	# That someone requested that work on this task be suspended.
			self.paused			= Flag()	# That work on this task has been suspended.
			self.abortRequested = Flag()	# That someone requested that work on this task be aborted.
			self.exitRequested	= Flag()	# That someone requested that work on this task be completed.
			self.haveResult		= Flag()	# That this work item has produced a result (or exception).
			self.stopped		= Flag()	# That sork on this task has stopped.
			self.done			= Flag()	# That this task is done.
			self.failed			= Flag()	# That this task failed.

			#_logger.debug(f"Created work item '{desc}' with 'inProgress' flag state = '{self.inProgress()}'")

		# In the below, methods starting in underscore (_) may ONLY be called
		# by the thread that owns (is tasked with) this work item.	Use the
		# setOwner() method to set this up appropriately.

	def _verifyOwnership(self):			# Makes sure that the thread calling this method is really the owner of this work item.
		with self.lock:									# Thread-safely,
			if self.owner == None:							 # If this work item has no owner... 
				self.setOwner(current_thread())		  # Then make calling thread hereby be the owner!
			elif self.owner != current_thread():  # If it has an owner, but we're not it, then...
				raise NotOwner("WorkItem._verifyOwnership(): Current thread %s "
							   "is not %s, the owner of this work item." %
							   current_thread(), self.owner)
					#-> Raise an exception: We are not the owner of this work item!
				
		# Methods associated with starting work on a task.

	def _start(self):			# Announce the start of work on the task.
		self._verifyOwnership()		# Only the owner thread of this task can do this.
		self.inProgress.rise()		# Raise the flag announcing that we have started working on the task.

	def waitStart(self):	# Wait for some thread to start doing the task.
		self.inProgress.wait()		# Wait for the "started" flag to be raised.

		# Methods associated with suspending work on a task.

	def requestPause(self):		# Request the thread running the task to suspend its work.
		self.pauseRequested.rise()	# Raise the flag requesting the thread to suspend its work.

	def _checkPauseReq(self):	# Check for pause requests.
		if self.pauseRequested():	 # If someone is asking us to pause,
			self._pause()				# Then pause.

	def _pause(self):		 # Announce that the thread has paused, and pause it.
		self._verifyOwnership()		 # Only the owner thread of this task can do this.
		self.paused.rise()				# Raise the flag announcing that we've paused.
		self.pauseRequested.waitDown()		# Wait for the pauseRequested flag to go down.
		self.paused.lower()				# Lower the paused flag to announce that we've unpaused.

		# Methods associated with aborting work on a task.

	def requestAbort(self):		# Request the thread running the task to abort its work.
		self.abortRequested.rise()	# Raise the flag requesting the thread to abort its work.

	def _checkAbortReq(self):	# Check for abort requests.
		if self.abortRequested():	 # If someone is asking us to abort,
			self._abort()				# Then abort.

	def _abort(self):		# Abort the running of this task.
		self._verifyOwnership()		 # Only the owner thread of this task can do this.
		raise WorkAborted("WorkItem._abort(): Aborting work on this work item.")
				#-> Do it very simply - just raise a WorkAborted exception.
				#	This will be caught and trigger our _fail() method.

		# Methods associated with failure to complete a task normally.

	def _fail(self):		 # Announce that we failed to complete the task.
		self._verifyOwnership()		 # Only the owner thread of this task can do this.
		self.failed.rise()		# Raise the flag announcing that the task failed.
		self._end()				# Announce the end of work on the task.

	def waitFail(self):		# Wait for work on this task to fail.
		self.failed.wait()		# Wait for the "failed" flag to be raised.

		# Methods associated with exiting a task normally (but earlier than otherwise).

	def requestExit(self):		# Request the thread running the task to wrap things up as soon as it can.
		self.exitRequested.rise()	# Raise the flag requesting the thread to exit early if possible.

	def _checkExitReq(self):	 # Check for exit requests.
		if self.exitRequested():	 # If someone is asking us to exit early,
			self._exit()				# Then exit.

	def _exit(self):		# Exit this task early (but normally).
		self._verifyOwnership()		 # Only the owner thread of this task can do this.
		raise EarlyCompletion("WorkItem._exit(): Exiting early from this task.")
			#-> Simply raise an EarlyCompletion exception,
			#	which will be caught and trigger our _finish() method.

		# Methods associated with successful completion of a task.

	def _finish(self):		 # Announce that the task is finished.
		self._verifyOwnership()		 # Only the owner thread of this task can do this.
		self.done.rise()		# Raise the flag announcing that the task is done.
		self._end()				# Announce the end of work on the task.

	def waitFinish(self):	# Wait for some thread to finish doing the task.
		self.done.wait()		# Wait for the "done" flag to be raised.

		# Methods associating with the ending of a task (for any reason).

	def _end(self):			 # Announce the end of work on the task.
		self._verifyOwnership()		 # Only the owner thread of this task can do this.
		self.stopped.rise()		# Raise the flag announcing that we have stopped working on the task.

	def waitStop(self):		# Wait for work on the task to stop.
		self.stopped.wait()		# Wait for the "stopped" flag to be raised.
	
	def wait(self):			# Waiting for a work item generally means,
		self.waitStop()			# waiting for the work on it to stop.
		# Caller: You may want to check the done() and/or failed() flags.

	def _checkRequests(self):	# Check for flags requesting us to do something.
		self._verifyOwnership()		# Only the owner thread of this task can do this.
		self._checkAbortReq()		# Abort requests are handled first - highest priority.
		self._checkExitReq()		# Next, check for exit requests - next highest priority.
		self._checkPauseReq()		# Finally, check for pause requests - lowest priority.
		
		# Set the owner of a work item to a given thread (usually a Worker thread).
		# This cannot be done after the task has already been started.

	def setOwner(self, worker:Thread):		# Set the owner of this WorkItem to the given (worker) thread.
		with self.lock:							 # Thread-safely,
			if self.inProgress():						# If work on this task has already been started,
				raise AlreadyStarted("WorkItem.setOwner(): Can't change owner "
									 "of this work item b/c work on it has "
									 "already started!")
					#-> Cry foul.
			else:
				with self.owned.lock:		# Do the following atomically in context of the owned flag.
					self.owner = worker			# Set the owner to the given worker.
					self.owned.rise()			# Raise the owned flag to declare this task is owned.

		# A work item is callable.	The call method causes the calling thread to
		# take ownership of the work item (if it does not already have it).
		# Once the task has started, ownership of it may not be reassigned to
		# a new thread.

	def __call__(self):			# To do a work item,
		with self.lock:				 # Thread-safely for this work item,
			self._verifyOwnership()		# Make sure we're the owner (only the owner thread of this task can do this).
			if self.task == None:	# If our callable attribute is null,
				raise NullCallable("WorkItem.__call__(): Can't perform this "
								   "work item because its .task attribute is "
								   "null (None).")
					# complain about that.
			elif self.inProgress():		  # If some other thread has already started doing this task,

				desc = self.desc
				if desc is None:
					descstr = "this work item"
				else:
					descstr = f"work item \"{desc}\""

				raise AlreadyStarted(
					f"WorkItem.__call__(): Can't perform {descstr} because "
					"someone has already started working on it!")
					# Raise an exception to warn user about that.
			else:						# Otherwise,
				try:						# We'll try doing the task.
					#_logger.debug(f"Starting work on task '{self.desc}'...")
					self._start()				 # First, announce that we're starting to work on the task.
					self._checkAbortReq()		 # Go ahead and check for any early abort requests.
					self._checkPauseReq()		 # Go ahead and check for any early pause requests.
					try:
#						 print("worklist.WorkItem.__call__(): I'm trying to call this task: ", self.task)
						#_logger.debug(f"About to call internal callable of task '{self.desc}'...")
						self.result = self.task.__call__()	 # Then, actually do the task (it must be callable).
						self.haveResult.rise()			# Announce that we have a result.
					except BaseException as e:		# If it raises any kind of exception whatsoever,
						self.exception = e				# Remember what exception it was,
						self.haveResult.rise()			# Announce that we have a result.
						raise e							# and re-raise it.
					self._finish()				 # Finally, announce that we finished the task.
				except (EarlyCompletion, ExitingByRequest):		# If the task terminates by throwing an EarlyCompletion or ExitingByRequest exception, then
					self._finish()				 # Announce that we finished the task in that case as well.
					raise						 # And re-signal the early completion to our caller also.
				except:						# For all other exceptions,
					self._fail()				 # Announce that we failed to complete the task.
					raise					# And re-raise the exception.

	#---------------------------------------------------------------------------------
	#	Worker [module public class] - Generic base class for worker threads.
	#
	#		This early declaration is so that the Worklist class can
	#		refer to a generic Worker type, even though our worker
	#		subclasses are not defined till later.	This is overridden
	#		later by a more specific definition.

class Worker(ThreadActor): pass

	#---------------------------------------------------------------------
	#	Worklist [module private class] - Generic base class for
	#		worklists of various specific types.
	#
	#		(ProjectWorklist, AssignmentWorklist, InboxWorklist,
	#		DesktopWorklist) abbreviated (Worklist, Assignment, Inbox,
	#		Desk).
	#
	#		DesktopWorklist - A very small Desque, normally limited to just
	#			1 or a few items, representing work item(s) that a given
	#			worker is about to start work on (after finishing the
	#			current work item).
	#	
	#			The desktop is a Desque rather than a simple variable so
	#			that if a customer needs a task done urgently, he can put
	#			the item on top of the desk and it will be done as soon
	#			as the worker finishes his current task.  For faster
	#			response, the customer could also request the worker to
	#			exit, abort, or suspend his current task - if it can be
	#			supended it can be put back on the desk.  Items on a
	#			worker's desktop are owned by the worker.
	#
	#		InboxWorklist - A fairly small queue (usu. max 5-10 items),
	#			representing work items owned by the worker to be done in
	#			FIFO order, at lower priority than his DesktopWorklist.
	#
	#		AssignmentWorklist - A midsize FIFO queue (10-20 items)
	#			representing items from a given project that have been
	#			assigned to a given worker.	 Items are owned by the worker
	#			but can be taken over by other workers on the same team
	#			(i.e., working on the same project).
	#
	#		ProjectWorklist - A large (usu. unlimited) FIFO whose main
	#			worker is a ProjectManager, responsible for delegating
	#			project work items to individual team members via their
	#			AssignmentWorklists.

class Worklist(Desque):	  # Extend my double-ended Queue class.

		#--------------------------------------------------
		#	Class data members:

	DEFAULT_MAX_SIZE = 0	# Default maximum size for worklists of this class.
		#- 0 means unlimited.
		#- Subclasses should override this as needed.

		#---------------------------------------------------------------------
		#	Instance data members:
		#
		#		lock:RLock - Reentrant mutex (mutual exclusion) lock for
		#			synchronizing manipulations of the worklist state.
		#			(This is just another reference to the mutex field of
		#			the underlying Desque, which we also made re-entrant.)
		#
		#		maxsize:int - Inherited from Queue.	 The maximum size of this
		#			worklist.  A maxsize of 0 means the size is unlimited.
		#			NOTE: Users should never modify this attribute directly!
		#			It can only be set once, in the initializer when the
		#			worklist is first created.	Changing it at other times
		#			may cause strange errors.
		#
		#		mainWorker - The main worker responsible for carrying out
		#			of tasks on this worklist.	Even project worklists have
		#			a mainWorker - namely, the project's ProjectManager.
		#
		#		closed - A flag stating that this worklist is now closed,
		#			that is, not accepting new work items (however,
		#			a worker may still be finishing up items already there).
		#			Also, a closed worklist may yet re-open.  However,
		#			a closedForever worklist may not.
		#
		#		closedForever - A flag stating that this worklist is closed
		#			and will never reopen.	However, a worker may still be
		#			finishing up work items that are already there.
		#		
		#---------------------------------------------------------------------
	
	def __init__(self, maxsize:int=DEFAULT_MAX_SIZE, worker:Worker = None):
		Desque.__init__(self, maxsize)
		self.lock = self.mutex				# desque.Desque.mutex is an RLock now, so we use it.
		with self.lock:
			self.mainWorker = worker		# Assign the main worker for this worklist, if any yet.
			self.closed = Flag(lock=self.lock)	 # Create a flag for announcing when we are closed.
			self.closedForever = Flag(lock=self.lock) # Create a flag for announcing when we've closed forever.

		#---------------------------------------------------------------------
		#	Instance methods:
		#
		#		addItem(item) - Adds the given work item to the worklist,
		#				at the end of the queue.  Use for lower-priority
		#				work items.	 Blocks till there is room on the list.
		#
		#		addItem_nowait(item) - Like addItem, but throws a Full
		#				exception instead of blocking if there's no room.
		#
		#		addItem_head(task) - Also adds the given work item to the worklist,
		#				but at the head of the queue.  Use for high-priority
		#				work items.
		#
		#		addItem_head_nowait(task) - Like addItem_head(), but throws
		#				a Full exception instead of blocking if there's no room.
		#
		#		empty() - Inherited from Queue.	 Returns True if the worklist
		#				is empty.  Otherwise, returns False.  Not guaranteed
		#				to remain stable except within the context of a
		#				"with worklist.lock:" statement.
		#
		#		full() - Inherited from Queue.	Returns True if and only if the
		#				worklist is full.  Not guaranteed to remain stable except
		#				within the context of a "with worklist.lock:" statement.
		#
		#		getItem() - Removes and returns the work
		#				item at the head of the worklist.  If no work items
		#				are there now, waits for one to appear.
		#
		#		getItem_nowait() - Removes the work item
		#				at the head of the worklist, if any; otherwise,
		#				raises the Empty exception.
		#
		#		close()/reopen()/closeForever() - For closing/unclosing/
		#				permanently closing the worklist from having new
		#				work items added to it.

		# The reason for adding these addItem()/getItem() methods, rather than
		# just having the user use the underlying Desque put()/get() methods
		# directly, is so that we can ensure that any changes are done in a
		# context where our mutex lock is being held.  Since the lock is
		# re-entrant, user code can take advantage of this.
		#
		# For example, a user who wants to add an item to a worklist if and
		# only if it is empty can simply write something like:
		#
		#		with worklist.lock:
		#			if worklist.empty():
		#				worklist.addItem(item)
		#
		# This works because no other thread that goes through our interface
		# can modify the worklist between the empty() test and the addItem().
		#
		# Another example: To get an item without blocking, and without having
		# to worry about handling a possible Empty exception, write:
		#
		#		with worklist.lock:
		#			if worklist.empty():
		#				item = None
		#			else
		#				item = worklist.getItem()
		#		if (item)
		#			...		# Process the item.
		#
		# That particular code works as long as None is never itself added
		# to the worklist - which we also enforce in the various addItem()
		# methods.
		#
		# Code like the above may be easier to read than the other approach,
		# using a try/except clause around getItem_nowait() that checks for
		# the Empty exception.

	def addItem(self, item:WorkItem, block:bool=True, timeout:Number=None, front:bool=False, override:bool=False):
		if isinstance(item, WorkItem):		# Make sure only WorkItems are added to a Worklist.
			with self.lock:
				if self.closedForever:
					raise WorklistClosedForever("Worklist.addItem(): Can't add item because this worklist is closed forever!")
				else:
					if self.closed and not override:
						if block:
							self.closed.waitDown()	# Wait for the "closed" flag to go down (worklist reopened!)
						else:
							raise WorklistClosed("Worklist.addItem(): Can't add item because this worklist is closed.")
					else:
						with item.onWorklist.lock:	# Want this flag to be consistent with the facts.
							self.put(item, block, timeout, front)	# Put it on the worklist (may block).
							item.onWorklist.rise()	# Announce that this item is on a worklist now.
		else:
			raise NotAWorkItem("Worklist.addItem(): argument to Worklist.addItem() must be a WorkItem.")
			
	def addItem_nowait(self, item:WorkItem):
		self.addItem(item, block=False)

	def addItem_head(self, item:WorkItem, block:bool=True, timeout:Number=None):
		self.addItem(item, block, timeout, front=True)

	def addItem_head_nowait(self, item:WorkItem):
		self.addItem(item, block=False, front=True)

		# The following code works ONLY because get() works by waiting
		# on a condition variable that's based on the same mutex lock as
		# self.lock.  Because of this, that lock gets temporarily
		# released while get() is doing its wait().	 If this were not
		# the case, it would block forever on an empty queue since
		# subsequent calls to addItem() above would be unable to
		# acquire the worklist lock.  (A similar remark holds to the
		# behavior of addItem() on a full queue, which while waiting
		# would block any calls to getItem(), if another lock was
		# used.)

	def getItem(self, block:bool=True, timeout:Number=None):
		with self.lock:
			item = self.get(block, timeout);  item.onWorklist.fall()
				#-There will be a tiny gap after the item is actually
				# removed from the worklist, and before this flag falls.
				# I don't think this will cause any problems though - no
				# harm if people think it's on the worklist slightly
				# longer than it really is.
			return item

	def getItem_nowait(self):
		return self.getItem(block=False)

		# The following methods are for temporarily (or permanently)
		# closing off the worklist so that new items cannot be added
		# to it.  This might be done, for example, if the worklist's
		# main worker is getting ready to exit.

	def close(self):
		self.closed.rise()

	def reopen(self):
		if self.closedForever:
			raise WaitlistClosedForever("Workitem.reopen(): Can't reopen "
										"this worklist because it has been "
										"declared to be forever closed.")
		else:
			self.closed.fall()

		#-----------------------------------------------------------------------
		#	reset()									[instance external method]
		#
		#		Closes the worklist & flushes all existing items from
		#		it (without executing them), and then reopens the worklist.
	
	def reset(self):
		with self.lock:
			self.close()	# Close the worklist so no new items will be added.
			self.flush()	# Flush its contents.
			self.reopen()	# Reopen it for new business.

	def closeForever(self):
		with self.lock:			# Do these both as one atomic action
			self.close(); self.closedForever.rise()

	#===========================================================
	#	Worklist subclasses.
	#
	#		We may do more with these later, but for now they
	#		don't do much.	ProjectWorklist, in particular, is
	#		highly incomplete.	(It needs an associated worker
	#		of type ProjectManager, a project team, and so forth.)

class DesktopWorklist(Worklist):
		# Class data members:
	DEFAULT_MAX_SIZE = 2	# By default, a desktop only holds at
		#- most 2 items - the 1 or 2 urgent items the worker needs
		#  to work on right away.  If you have more than this many
		#  urgent items, you probably need to make another worker.

class InboxWorklist(Worklist):
		# Class data members:
	DEFAULT_MAX_SIZE = 5	# By default, an inbox only holds at
		#- most 5 items - things that have been assigned to the
		#  worker, for him to do pretty soon.  (If you have more
		#  than this many items that need to be done soon, you
		#  might want to create another worker.)

class AssignmentWorklist(Worklist):
		# Class data members:
	DEFAULT_MAX_SIZE = 10	# By default, an assignment only holds
		#  at most 10 items - work items on a specific project that
		#  have been assigned to the worklist's main worker, for him
		#  to do pretty soon.  There is probably not a need for
		#  more than this many project worklist items to be assigned
		#  to individual workers ahead of time.

		#	Instance data members:
		#
		#		project:WorkList - The main project worklist that
		#			the work items on assignment worklist came from.

class ProjectWorklist(Worklist):
		# Class data members:
	DEFAULT_MAX_SIZE = 0	# The size of a project worklist may
		# be arbitrarily large, although if it grows very large,
		# that might be a good indication that more team members
		# (worker threads) need to be created to work on the
		# project.

	#---------------------------------------------------------
	#	Instance data members:
	#
	#		team:list - List of Worker objects who make up the
	#			project team (not including the ProjectManager,
	#			who only delegates tasks, but never does them).
	#
	#			A given worker may be a team member on more than
	#			one project at the same time.
	#
	#-----------------------------------------------------------

	# TODO: Fill in much more code for ProjectWorklist here.

#--> END CLASS: ProjectWorklist
	
	#------------------------------------------------------------------
	# Worker [module class] - A thread that just follows a worklist.
	#
	#	A worker is a thread whole sole purpose in life is to wait for,
	#	claim ownership of, and carry out tasks that appear on a given
	#	worklist.  There may be multiple workers taking tasks from a
	#	given worklist, but in that case the order of completion of the
	#	tasks is undefined.	 If there is only one worker for a given
	#	worklist, then the tasks on that worklist are done in order.
	#
	#	Types of workers:
	#
	#		DeskWorker - Just does work items placed on his desk,
	#			which is a Desque (double-ended synchronized queue).
	#			Items may be placed on the Desque in either LIFO
	#			mode (at the front of the queue) or FIFO mode (at
	#			the back of the queue.	The point of this flexibility
	#			is so that high-priority work items can be inserted
	#			right at the front of the desk-worker's queue.	The
	#			capacity of the desk worklist is usually quite
	#			limited (1-10 items).  Too many items on the desk
	#			may make the worker feel overwhelmed!
	#
	#		OfficeWorker - An OfficeWorker has, in addition to his
	#			Desk, an Inbox, which is another Worklist that is
	#			normally FIFO.	An OfficeWorker first does the work
	#			on his desk; if there is nothing on his desk, he
	#			checks his Inbox, if there is nothing there either
	#			he goes back and waits on his desk.	 Someone giving
	#			work to an OfficeWorker should put it on his desk
	#			if it's empty, and on his Inbox otherwise.
	#
	#		ProjectWorker - An OfficeWorker who also works on one
	#			or more project teams.	When he runs out of work
	#			to do in his desk and inbox, he examines his
	#			assignments, and then his teammates' assignments,
	#			for work to take over.	He can also take work
	#			directly from the project worklist.	 However, if
	#			there's nothing to do, he goes back to staring at
	#			his desk, waiting for work to arrive.
	#
	#		ProjectManager - A.k.a. a Delegator.  He is like an
	#			office worker whose inbox represents all the tasks
	#			that need to be done on a certain project.	He takes
	#			tasks from the project worklist and delegates them
	#			to team members who appear to be the least busy.
	#
	#	NOTE:  None of the above special types of workers have been
	#	implemented yet.  So far, just the basic Worker class has been
	#	perfectly adequate for our purposes.
	#
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Worker(ThreadActor):

	#	Class data members.

	defaultRole = 'Worker'
	#defaultComponent = '(unset)'		# by not setting this, we inherit value from parent thread, or parent class

	defaultWaitByDefault = False		# By default, sending a task to a worker does not wait for a return value.

	defaultWrapper = None	# By default, no wrapper is wrapped around bare callables.

	#---------------------------------------------------------------------------------
	#	Instance data members:
	#
	#		initialTask:WorkItem - If present, a task to be added to the
	#			front of the work list first thing on worker creation.
	#			This attribute is not initialized in Worker itself,
	#			although subclasses may want to initialize it.
	#
	#		lock:RLock	- A re-entrant mutex lock on the worker object.
	#			used for thread-safety, to ensure that two threads don't
	#			try to modify the worker data structure at the same time
	#			in an inconsistent way.
	#
	#		todo:Worklist - The main worklist for this worker thread.
	#
	#		onexit:callable - Callback to be executed just before the thread exits.
	#
	#		Special flags used for communication between the worker thread
	#		and other threads:
	#
	#			started			- This worker has started running its main loop.
	#			pauseRequested	- Someone has requested the worker to pause.
	#			paused			- The worker has paused in the middle of his work.
	#			waiting			- The worker is waiting for new work to arrive in its queue.
	#			exitRequested	- Someone has requested the worker to exit & die.
	#			exitedByRequest - The worker exited because of the exitRequested flag.
	#			exitedAbnormally - The worker exited due to some uncaught exception.
	#			exited			- The worker has stopped working and exited.
	#
	#----------------------------------------------------------------------------------

	#----------------------------------------------------------------------------
	#	Instance methods.
	#
	#		In the below, we use "inst" as the instance variable for methods
	#		that are supposed to be called from other threads, such as the
	#		"maker" thread that constructed this worker object, or other
	#		threads that are just trying to control or communicate with this
	#		worker.
	#
	#		We use "self" as the instance variable of methods that are
	#		supposed to only be called from within this worker thread,
	#		itself.
	#
	#		We use "this" as the instance variable in methods that may
	#		be called either from other threads, or within this thread.
	#
	#-------------------------------------------------------------------------------

		#-------------------------------------------------------------------------
		#	Instance external methods.	These methods are supposed to be called
		#		from within OTHER threads - not from within this worker thread,
		#		itself.	 They use "inst" as their instance variable.
		#-------------------------------------------------------------------------

			#---------------------------------------------------------------------------
			#	Instance initializer.				 [special external instance method]
			#
			#		Takes an optional
			#		existing worklist that this worker should use; if none is provided,
			#		then the worker will create a generic worklist for itself when
			#		needed.	 Also takes a optional target callable that this worker
			#		thread should utilize in place of its built-in run() method (which
			#		just takes work items from the queue and does them).  If <start> is
			#		true, then the new worker thread will be started right away after
			#		being initialized, rather than waiting for the start() method to be
			#		called.	 <onexit> specifies a callback to be run when the main
			#		loop is exiting.
	
	def __init__(inst:Worker, worklist:Worklist=None, target=None, start=True, daemon=False,
				 onexit=None, role=None, component=None, waitByDefault=None, wrapper=None):	   
				 # Defaulting these to None gives parent class the responsibility to apply appropriate defaults.

			# First, do whatever initialization all ThreadActors need.
		
		ThreadActor.__init__(inst, target=target, role=role, component=component, daemon=daemon)

			# Next, do Worker-class-specific initialization.
		
		inst.init(worklist=worklist, start=start, onexit=onexit, waitByDefault=waitByDefault, wrapper=wrapper)

			#----------------------------------------------------------------------------
			#	init()										[external instance method]
			#
			#		Initialization specific to the Worker class.

	def init(inst:Worker, worklist:Worklist=None, start:bool=False, onexit=None, waitByDefault=None, wrapper=None):

			# In case this method is called on something that isn't really a Worker class instance.

		if not hasattr(inst, 'defaultWaitByDefault'):
			inst.defaultWaitByDefault = False
		if not hasattr(inst, 'defaultWrapper'):
			inst.defaultWrapper = None

			# Inherent default behavior from class variable.

		if waitByDefault == None:
			waitByDefault = inst.defaultWaitByDefault
		
		if wrapper == None:
			wrapper = inst.defaultWrapper
		
		_logger.debug("Initializing worker %s..." % inst)
		inst.lock = RLock()		  # Create our reentrant mutex lock.
		with inst.lock:						# Go ahead and use it, just in case.

			inst.waitByDefault	  = waitByDefault	# Initialize this parameter, which determines whether we do .do() or .getResult() by default.
			inst.wrapper		  = wrapper			# Function to wrap around bare callables.
			
			inst.started		  = Flag()		  # Create all of our waitable flags.
			inst.pauseRequested	  = Flag()
			inst.paused			  = Flag()
			inst.waiting		  = Flag()
			inst.exitRequested	  = Flag()
			inst.exiting		  = Flag()	# Worker is trying to exit.
			inst.exitedByRequest  = Flag()
			inst.exitedAbnormally = Flag()
			inst.exited			  = Flag()
			inst.assign(worklist)			# Assign us to work on the given worklist.
			
			inst.onexit = onexit			# Remember onexit callback.
#			 inst.daemon = True				 # Make this thread subordinate to the main thread.

				# If the present object's class (maybe a subclass of Worker)
				# happens to have a class variable named 'initialTask', use
				# it as an initial task to put on the worker's worklist.

			if hasattr(inst, 'initialTask'):	# If we have an initialTask attribute,
				inst.ensure_worklist()				# Make sure we have a worklist.
				inst.todo.addItem(inst.initialTask, front=True) # Add initial task to worklist.
					# We add it at the front in case the worklist already
					# had some things to do on it, b/c we really want this
					# to be the FIRST thing that the worker does.
				
			if start:				# If we're supposed to go ahead and start the worker thread running,
				inst.start()			# then do so.

			#------------------------------------------------------------------------------
			#	assign()										[instance external method]
			#
			#		Assigns this worker to get his tasks from the given worklist.
	
	def assign(inst, worklist=None):
		with inst.lock:					# Thread-safely,
			inst.todo = worklist			# assign worklist.

			#---------------------------------------------------------------------------------
			#	Call method.							[special instance external method]
			#
			#		Calling a worker with an argument that is a WorkItem (or other callable
			#		object) simply adds the item to the worker's main worklist, in FIFO mode.
			#		Optional arguments specify nonblocking mode, timeout values, and front
			#		(LIFO) mode.
	
	def __call__(inst, task, block:bool=True, timeout:Number=None, front:bool=False, override:bool=False, desc:str=None):

		if inst.waitByDefault:
			return inst.getResult(task, block=block, timeout=timeout, front=front, desc=desc)
		else:
			inst.do(task, block, timeout, front, override, desc)


			#----------------------------------------------------------------------------------
			#	do()											[instance external method]
			#
			#		This simply adds the given workitem to the worker's main worklist, in
			#		FIFO mode.	Optional arguments specify nonblocking mode, timeout values,
			#		and front (LIFO) mode.	This routine does not return a result - it exits
			#		as soon as the work item is added to the worker's queue.

	def do(inst, task, block:bool=True, timeout:Number=None, front:bool=False, override:bool=False, desc:str=None):
		if inst.exiting:			# If we are already in the process of exiting,

				# For this one, we can't use the logger because it can cause an
				# infinite recursion.

#			 _logger.warn("%s: Worker.do(): Request to do task %s ignored, because "
#						 "we are already in the process of exiting..."%(current_thread(),task))

				# We dispense with this plain printed warning as well, because
				# it seems overly verbose... By the time we get here, it's too
				# late to do anything about it anyway.

#			 print("%s: Worker.do(%s, ...): Warning: Request to do task %s ignored, because "
#				   "that worker is already in the process of exiting..."%(current_thread(), inst, task),
#				   file=sys.__stderr__)

			if isinstance(task, WorkItem): # If task is already in a WorkItem wrapper,
				task.failed.rise()	# Declare that this work item has failed.
				task.stopped.rise() # And that it has stopped.

			raise WorkerExiting("Worker.do(): Could not execute task %s "
								"because I am already in the process of "
								"shutting down.	 Task failed." % task)
				#-> This tells caller that the "do" could not be 
				#	completed, b/c worker is in the process of shutting down.

		inst.ensure_worklist()		# First make sure we have a worklist.

		if not isinstance(task, WorkItem):		# Is the task just a plain callable (e.g. lambda)?
		
			#_logger.debug(f"Task '{desc}' is not already a WorkItem, so let's make it into one.")

			bareCallable = task

			# First, if we have a wrapper function to apply to all tasks, wrap the callable in it.
			wrapper = inst.wrapper
			if wrapper is None:
				theCallable = bareCallable
			else:
				#_logger.debug(f"First, wrapping task '{desc}' in a wrapper...")
				#task = lambda *args, **kwargs: wrapper(lambda: task(*args, **kwargs))	# Wrap the task in the wrapper
				wrappedCallable = lambda: wrapper(bareCallable)
				theCallable = wrappedCallable
		
			task = WorkItem(theCallable, owner=inst, desc=desc)	# Now, make a real WorkItem out of it.
			#_logger.debug(f"Just created a new background work item with description \"{desc}\"")

		inst.todo.addItem(task, block, timeout, front, override)  # Add it to the worker's queue.


			#----------------------------------------------------------------------------------
			#	getResult()										[instance external method]
			#
			#		This alternative call method differs from the former one in that it not
			#		only puts the work item on the worker's queue, but then also waits for
			#		the workitem to return a result (or exception), and returns (or
			#		re-raises) the result (exception) in the maker thread.	The timeout (if
			#		any) applies to both the addItem() operation, and the subsequent wait
			#		for result, so the maximum latency could be as large as 2*timeout, or
			#		even more, depending on how long it takes to acquire various locks.
			#
			#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def getResult(inst, task, block:bool=True, timeout:Number=None, front:bool=False, desc:str=None):

			# Ignore tasks being sent to workers that are in the process of exiting.
		
		if inst.exiting:	# If we are already in the process of exiting,
			raise WorkerExiting("Worker.getResult(): Request to do & return result from task "
								"%s ignored, because we are already in the process of exiting" % task,
								logmaster.logging.WARN)
				# Re-raise this handy little guy in the requesting thread.

			# Here is a clever little optimization.	 If the worker being requested to
			# do this task is the same as the current thread, then we just do the task
			# now, except that if front=False and there is other work in the queue, we
			# do that other work first. (Note, however, that this changes the
			# order of task completion if the present code is itself in a task.)

		if inst == current_thread():						# We are giving this task to ourselves!
			if not front:									# If this task is supposed to go at the back of our queue,
				catchup()									# go ahead and do all the tasks that are ahead of it.
			return task()									# Now do the task itself, and return its result.

			# OK, that optimization wasn't possible, so we have to go ahead and put the
			# task on a queue so it can be done later in another thread, and then we
			# wait for it to finish.  

		inst.ensure_worklist()		# First make sure we have a worklist.

		if not isinstance(task, WorkItem):		# Is the task just a plain callable (e.g. function, lambda)?

			#_logger.debug(f"Task '{desc}' is not already a WorkItem, so let's make it into one.")

			bareCallable = task

			# First, if we have a wrapper function to apply to all tasks, wrap the callable in it.
			wrapper = inst.wrapper
			if wrapper is None:
				theCallable = bareCallable
			else:
				#_logger.debug(f"First, wrapping task '{desc}' in a wrapper...")
				#task = lambda *args, **kwargs: wrapper(lambda: task(*args, **kwargs))	# Wrap the task in the wrapper
				wrappedCallable = lambda: wrapper(bareCallable)
				theCallable = wrappedCallable
		
			task = WorkItem(theCallable, owner=inst, desc=desc)	# If so, then make a real WorkItem out of it.
			#_logger.debug(f"Just created a new waitable work item with description \"{desc}\"")

		# Now we actually send the task, and then wait for & then reproduce the result.

		inst.todo.addItem(task, block, timeout, front)	 # Add the task to the worker's queue.
			# If this times out and throws a Full, that's fine, just let it fall out to our caller.

		task.haveResult.wait(timeout)			 # Wait till the worker produces a result (or exception).
			# If this times out, it is silent except for a note attached to the condition.

		# Reproduce the returned result in the maker thread context.

		if task.exception:		   # If there was an exception,
			raise task.exception		 # re-raise it within the current thread.
		else:					 # otherwise,
			return task.result			 # return the result.

			#--------------------------------------------------------------------------
			#	stopSoon()									[instance external method]
			#
			#		Tells the worker to stop working right after completing his next task.
			#		This doesn't wake up the worker if he is currently waiting for a task,
			#		however.  For that, use the stop() method defined later.

	def stopSoon(inst):
		if inst.exiting:
			_logger.warn("Worker.stopSoon(): [%s] worker is already exiting; nothing to do."%inst.role)
			return
		_logger.debug("Worker.stopSoon(): Asking [%s] worker to exit after next task..."%inst.role)
		inst.exitRequested.rise()

			#---------------------------------------------------------------------------
			#	putStop()									[instance external method]
			#
			#		Puts an item on the worker's worklist (if he has one) telling
			#		the worker to stop working.	 As soon as this item gets to the
			#		front of his queue, he will stop.  If he has no worklist yet
			#		(not running yet), just go ahead and raise his exit flag.

	def putStop(inst, front=False):
		if inst.exiting:
			_logger.warn("Worker.putStop(): [%s] worker is already exiting; nothing to do."%inst.role)
			return
		_logger.debug("Worker.putStop(): About to acquire [%s] worker lock..."%inst.role)
		with inst.lock:
			if inst.todo == None:
				_logger.debug("Worker.putStop(): The [%s] worker has no worklist.  About to call stopSoon()..."%inst.role)
				inst.stopSoon()
		_logger.debug("Worker.putStop(): Making sure [%s] worker has a worklist..."%inst.role)
		inst.ensure_worklist()	# Make sure we HAVE a worklist.
		_logger.debug("Worker.putStop(): About to close [%s] worker's worklist..."%inst.role)
		inst.todo.close()		# Close it so no new tasks can get onto it.
		_logger.debug("Worker.putStop(): Putting .exitByRequest() on front of [%s] worker's queue..."%inst.role)
		inst.do(inst.exitByRequest, front=front, override=True) # Put an item on this worker's
			# worklist to make him throw an exception and exit.


			#----------------------------------------------------------------------------
			#	stop()										[instance external method]
			#
			#		This method will stop the worker as soon as he completes his
			#		current task, if any (or right away if he's just waiting for
			#		a task).

	def stop(inst):
		if inst.exiting:
			_logger.warn("%s: Worker.stop(): %s is already exiting; nothing to do."%(current_thread(),inst))
			return
		inst.stopSoon()				# Even if the worker is currently busy,
			# make sure he'll stop as soon as he's done with his current work item.
		inst.putStop(front=True)	# Make sure there's a stop order at the FRONT
			# of the queue.


			#-----------------------------------------------------------------------------
			#	close()										[instance external method]
			#
			#		Tells the worker to stop accepting new work items on his
			#		worklist, and to stop working as soon as all of the existing
			#		items are completed.

	def close(inst):	# Tells a worker to close out his worklist and go home when he's done.
		if inst.exiting:
			_logger.warn("%s: Worker.close(): %s is already exiting; nothing to do."%(current_thread(),inst))
			return
		_logger.debug("Worker.close(): About to call putStop()...")
		inst.putStop()		# Puts a stop order at the back of the queue.

		#-------------------------------------------------------------------------
		#	Instance internal methods.	These methods are supposed to be called
		#		only from within this worker thread, itself.  To emphasize this,
		#		they use "self" as their instance variable.
		#-------------------------------------------------------------------------

			#------------------------------------------------------------------------------
			#	ensure_worklist() [instance internal method] - Make sure that this worker
			#		has SOME worklist assigned; if not, then we create a generic one and
			#		assign it to ourselves.

	def ensure_worklist(self):	   # Make sure we have a worklist!
		with self.lock:
			if self.todo == None:
				self.todo = Worklist(worker=self)

			#------------------------------------------------------------------------------
			#	exitByRequest() [instance internal method] - Raise an exception causing
			#		this worker thread to exit from its main event loop (if that is
			#		running).

	def exitByRequest(self):		# Use this to exit because it was requested.
		oldexiting = self.exiting.rise()			 # Announce that we are working on exiting.
		if oldexiting:
			_logger.warn("%s: Worker.putStop(): %s is already exiting; nothing to do."%(current_thread(),self))
			return		  
		raise ExitingByRequest("Worker.exitByRequest(): Exiting this worker thread by request.")
				# Get out by raising this special exception.

			#-------------------------------------------------------------------------------
			#	do1job() [instance internal method] - Do just one task from our worklist
			#		queue.	If block=False or timeout is set, throws an Empty exception if
			#		no work items are available in time.  We return any result to our caller
			#		(but they may ignore it).  Please only call this method from within
			#		this worker thread!

	def do1job(self, block:bool=True, timeout:Number=None):

			# If we have not been assigned a primary worklist yet,
			# then go ahead and create a generic one for ourselves.

		self.ensure_worklist()

			# Get a work item from the work list.  If block=False or a timeout is provided,
			# this may throw an Empty exception if no work items are available soon enough.

		with self.todo.lock:			# Keep worklist state consistent in here, except while waiting.
			if self.todo.empty():			# If worklist is empty, we'll need to wait,
				self.waiting.rise()				# so raise our waiting flag,
				task = self.todo.getItem(block, timeout) # get next task from worklist (blocks till it arrives, unless block is false).
				self.waiting.fall()				# and lower our waiting flag.
			else:							# else getItem shouldn't block, so don't bother with the waiting flag.
				task = self.todo.getItem(block=False)  # Get next task from worklist.

			# If we get here, then <task> definitely contains an item that was
			# extracted from our todo queue.  The following code is wrapped
			# in a try-finally to guarantee that no matter what happens inside
			# it, the task_done() method of the worklist queue will get called,
			# so that the queue can properly account for items processed.

		try:
			assert task		# The task at this point should never be None,
				# since addItem won't allow adding None to the queue.

			try:
				return task()	 # Do the task. (Must be callable, as a WorkItem is.)
					# Return any result to our caller.
					
			except (WorkAborted, EarlyCompletion) as e:		 # Early-termination workitem exception?
				_logger.warn(f"{str(current_thread)}: worker.do1job(): Task ended early: {str(e)}")
				# Just ignore it. (Don't re-raise.)

			except ExitingByRequest:
				_logger.debug("%s: Worker.do1job(): Task exited by request..." % current_thread())
				raise
				# No need to print the full traceback in this case.

			except ExitException as e:
				_logger.warn("%s: Worker.do1job(): Task exited early due to ExitException [%s]; reraising..."
							 % (current_thread(), e))
				raise

			except InfoException:
				_logger.warn("%s: Worker.do1job(): Task exited by throwing an INFO-level exception.	 Ignoring." % current_thread())

			except WarningException:
				_logger.warn("%s: Worker.do1job(): Task exited by throwing a WARNING-level exception.  Re-raising it in case caller wants to know about it." % current_thread())
				raise

			except:
				_logger.exception("%s: Worker.do1job(): Task threw an exception; reraising..." % current_thread())
				raise	# Within guibot, I think TkInter just swallows this up silently.
		
		finally:
			self.todo.task_done()	# Tell the queue that we are done with this particular
				# work item.  This is essential in case any other threads try to do join()
				# on the queue (that is, wait for all items on the queue to be processed).

	# End Worker.do1job().
	#-------------------------


	#	check_exitflag()										[instance internal method]

	def check_exitflag(self):
		if self.exitRequested:				# If someone yelled "die" at us, then do so.
			self.exitByRequest()			# Break out by raising an exception.
		
		#------------------------------------------------------------------------------------
		#	run() [instance internal method] - Run the default main loop of Worker threads.
		#		this just repeatedly gets work items from the queue and executes them.
		#		It can be caused to exit using the various stop methods, close(), etc.
		#
		#		Since we're overriding ThreadActor's run() method, to maintain its
		#		functionality of initializing the logging context, we have to call
		#		

	def run(self, *args, **kwargs):						 # Special run() method for worker threads.
		_logger.debug("Worker.run(): Starting %s thread's .run() method..." % self)

		if self._target:					# Is there an alternate target? (Setup in start()'s 'target=' kwarg.)
			_logger.debug("%s: Worker.run(): Invoking alternate target method..." % self)
				# Dispatch method call to parent class.
			logmaster.ThreadActor.run(self, *args, **kwargs)	 # Let Thread.run() take care of targeting.
			return

		self.starting()					# Do stuff needed when starting up (which ThreadActor.run() would normally do).
		_logger.debug("Worker.run(): Started %s thread's .run() method..." % self)

		_logger.debug("Worker.run(): Entering %s worker's .work() method..." % self)
		self.work()						# Otherwise, do our work() method.
		_logger.debug("Worker.run(): Returned from .work(); exiting .run() - This thread %s should go away now." % self)
	# End Worker.run().

		#|---------------------------------------------------
		#|	work_cycle() - Do one work cycle, which means,
		#|		check for exit/pause flags, & do one job.
		#|		If block=False then it returns if there is
		#|		no work to do; otherwise, it waits for work.

	def work_cycle(self, block=True):
		
			# First, check for any exit requests, and honor them.
		
		self.check_exitflag()

			# Next, check for any pause requests, and honor them.

		if self.pauseRequested:				# If someone yells "whoa there," then do so.
			self.paused.rise()					# Announce we're paused.
			self.pauseRequested.waitDown()		# Wait for the pauseRequested flag to go down.
			self.paused.fall()					# Announce we're no longer paused.

		try:
			self.do1job(block=block)			# Do just one task from our worklist queue.
		except WarningException:
			_logger.warn("Worker.work(): Job exited by throwing a "
						"WARNING-level exception; ignoring...")
				# The idea here being that mere warning-level
				# exceptions shouldn't prevent processing of
				# subsequent jobs.
				
		
		#|---------------------------------------------------
		#|	catchup() - Do all tasks in the work queue
		#|		until it is empty, then return.	 Note that
		#|		this might never return if some tasks result
		#|		in more tasks being added to the queue.

	def catchup(self):
		try:
			while True:						# Indefinitely,
				work_cycle(block=False)		# do a work cycle, but throw an Empty exception if there's no work left to do.
		except Empty as e:		# Work queue empty?
			return				# Return to caller.
		
		#------------------------------------------------
		#	work() - This does the actual work of run().

	def work(self):
		
		self.started.rise()					# Raise the flag announcing we have started.

		try:
			while True:							# Indefinitely,
				self.work_cycle()				# Do one work cycle.

		except ExitingByRequest:				# If we're exiting because of the exitRequested flag,
			_logger.info("Worker.work(): Exiting worker thread %s by request."%current_thread())
			self.exitedByRequest.rise()				# Raise a flag announcing this.

				# Here, we don't want to re-raise the exception because then the threading
				# infrastructure will report the exception, traceback and all.	But
				# "ExitingByRequest" is a "friendly" exception, not an error, and doesn't
				# really need to be reported.  Thus this line is commented out, and so we
				# just do the finally clause and then go to the last line in run() after the
				# whole try-except-finally.
			
#			 raise									 # and re-raise the exception.

		except ExitException as e:
			_logger.warn("Worker.work(): Exiting worker thread %s early due to ExitException [%s]..."
						% (current_thread(), e)
						)
			# Don't re-raise, because we don't want to generate a traceback on thread exit.
			
		except:									# If we're exiting due to any other kind of exception,
			_logger.exception("Worker.work(): Exiting worker thread %s abnormally due to exception."%current_thread())
			self.exitedAbnormally.rise()			# Raise a flag annoucing that to other threads,
			raise									# and re-raise the exception.
		
		finally:
			self.exited.rise()					# Raise the flag announcing we have exited.
			nItemsLeft = self.todo.qsize()
			if nItemsLeft > 0:
				_logger.warn("Worker.work(): %s is exiting even though there "
							"are still %d unfinished tasks on its worklist!"
							% (current_thread(), nItemsLeft))
			if self.onexit:
				_logger.info("Worker.work(): Calling onexit callback: [%s]" % self.onexit)
				self.onexit.__call__()	# Call onexit callback, if specified.

		_logger.debug("Worker.work(): %s returning normally from its work() method; exiting..."%current_thread())

# End class Worker.

	#-------------------------------------------------------------
	#	HireThread()
	#
	#		Turn the given thread, one which is not already a
	#		Worker, into an imitation Worker, by copying the
	#		Worker class's method attributes to the current
	#		thread object as instance methods.

def HireThread(thread:Thread()):
	if isinstance(thread, Worker):
		_logger.warn("HireCurThread(): Can't hire thread %s because it's already a worker!" % thread)

		# Give the current thread all the instance methods that a Worker
		# instance would have.	The purpose of the bind() calls is to fill
		# in the first, 'self' (or 'this' or 'inst') argument of each class
		# method with the thread instance, to produce an instance method.
		
	thread.init				= bind(thread, Worker.init				)
	thread.assign			= bind(thread, Worker.assign			)
	thread.__call__			= bind(thread, Worker.__call__			)
	thread.do				= bind(thread, Worker.do				)
	thread.getResult		= bind(thread, Worker.getResult			)
	thread.stopSoon			= bind(thread, Worker.stopSoon			)
	thread.putStop			= bind(thread, Worker.putStop			)
	thread.stop				= bind(thread, Worker.stop				)
	thread.close			= bind(thread, Worker.close				)
	thread.ensure_worklist	= bind(thread, Worker.ensure_worklist	)
	thread.exitByRequest	= bind(thread, Worker.exitByRequest		)
	thread.do1job			= bind(thread, Worker.do1job			)
	thread.check_exitflag	= bind(thread, Worker.check_exitflag	)
	thread.run				= bind(thread, Worker.run				)
	thread.work				= bind(thread, Worker.work				)
	thread.starting			= bind(thread, Worker.starting			)
	thread.update_context	= bind(thread, Worker.update_context	)
	thread.catchup			= bind(thread, Worker.catchup			)
	thread.work_cycle		= bind(thread, Worker.work_cycle		)
	thread.__call__			= bind(thread, Worker.__call__			)

		# Go ahead and run the thread's new init() method, which
		# does Worker-specific initialization, which creates the
		# worker lock and flags.

	thread.init()
		#^^^^
		#	NOTE: Since start=True is not specified, this does not
		#		try to start the thread, because that would be
		#		inappropriate, since the thread is already
		#		running.  To go ahead and enter the usual main
		#		loop for worker threads, do something like:
		#
		#			worklist.HireThread(threading.current_thread())
		#			threading.current_thread().run()
		#----------------------------------------------
# End HireThread().
		

	#--------------------------------------------------------------
	#	RPCWorker									[module class]
	#
	#		This subclass of Worker differs only in that its
	#		default call method waits for and returns a result,
	#		unlike Worker, which spawns the task but by default
	#		does not wait for it to give a result.
	#
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class RPCWorker(Worker):
	defaultWaitByDefault = True

# old implementation of class RPCWorker had the following instead of the defaultWaitByDefault setting:	 
#	 def __call__(inst, task, block:bool=True, timeout:Number=None, front:bool=False):
#		 return inst.getResult(task, block=block, timeout=timeout, front=front)

# END MODULE worklist.py
#================================================================================================================
