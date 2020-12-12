#===============================================================================
#   heart.py                                            [python module source]
#
#       Virtual "heart" organ.  Purpose: To generate periodic heartbeats
#       which are logged to the main server log file.  The point of this
#       is just to provide a way to confirm that the main server process
#       is still running over a period when it is not seeing any other
#       activity.
#
#       The rate of heartbeats is adjustable, but currently it is set by
#       default to beat once every 5 minutes - a compromise that doesn't
#       require waiting too long to see a heartbeat, and also that doesn't
#       fill the log file with too much junk.
#
#       The heart is implemented very simply as a ThreadActor that
#       repeatedly waits on a "pause" flag to be raised, with a
#       timeout equal to the heartbeat interval.  In between waits
#       it beats once.  While stopped, it waits for the flag to be
#       touched again.  If the next touch lowers the flag, the beat
#       resumes.  Otherwise the heartbeat thread exits entirely.
#
#       The external interface to this is through methods .start(),
#       .pause(), .resume(), and .die().
#
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    # Standard modules.
    
import time
import threading

    # Custom modules.
    
import flag
import logmaster

global __all__, logger, MINS_PER_BEAT

__all__ = ['Heart', 'MINS_PER_BEAT']

logger = logmaster.getLogger(logmaster.appName + '.heart')

MINS_PER_BEAT = 5

class Heart(logmaster.ThreadActor):

    defaultRole = 'heart'

    defMinsPerBeat = MINS_PER_BEAT

        #-------------------------------------------------------------------------
        #   .__init__()
        #
        #       Default initializer for objects of class Heart.
        #
        #       If period is provided, it sets the time between beats in minutes.
        #
        #       If start=False is provided, then the newly created heart does not
        #       start beating automatically, and the .start() method must be
        #       called by the user code to start it.  Otherwise, the heart starts
        #       beating automatically right away, as soon as it is initialized.

    def __init__(inst, period=None, start=True):
        if period==None: period = inst.defMinsPerBeat
        inst.lock = threading.RLock()
        with inst.lock:
            inst.secsPerBeat = 60*period
                # The following flags all share the same lock so that changes
                # to more than one of them at a time still happen atomically.
            inst.started    = flag.Flag(lock=inst.lock) # Has the heart started beating yet?
            inst.beating    = flag.Flag(lock=inst.lock) # Is the heart currently engaged in a beat?
            inst.pause      = flag.Flag(lock=inst.lock) # Should the heart pause?
            inst.paused     = flag.Flag(lock=inst.lock) # Is the heart paused?
            inst.dead       = flag.Flag(lock=inst.lock) # Is the heart dead?

                # Number of beats since we've started.
            inst.nbeats     = 0
            
                # Do normal ThreadActor initialization.
            logmaster.ThreadActor.__init__(inst)            
            if start:
                inst.start()            # Start this new thread.

        #------------------------------------------------------------------------
        #   .start()
        #
        #       Use this method to start the heart beating if you specified
        #       start=False as an argument to the heart's constructor.
        #       Otherwise, you do not need to call this because the heart will
        #       have already started automatically.
        #
        #       When the heart is paused, you cannot restart it with .start() -
        #       you must use .resume() instead.

    def start(inst):
        with inst.lock:
            if inst.started:
                logger.warn("Heart.start(): Can't start the heart because it has already been started.  (To unpause it, use .resume() instead.)")
            logger.info("Heart.start(): Heart is starting.")
            inst.started.rise()         # Announce the heart has started.
            logmaster.ThreadActor.start(inst)     # Really start it (this is the usual Thread.start() method).  

        #-----------------------------------------------------------------------
        #   ._beat():
        #
        #       This private method is called by the heart thread itself, to
        #       make itself "beat" once.  Currently, this just involves sending
        #       some messages to the log file.  However, in the future, it may
        #       do other routine, periodic server tasks.  It should not be
        #       called directly from other threads.
        #

    def _beat(self):
        with self.lock:
            try:
                logger.info("Heart.beat(): Heart is beating.  (Period between beats is %d minutes.)" % (self.secsPerBeat/60))
                self.beating.rise()
                self.nbeats += 1
                logger.normal("Server heartbeat #%d @ %s.  Next beat in %d minutes." % (self.nbeats, time.ctime(), self.secsPerBeat/60))
                logger.debug("Heart.beat(): Currently active threads are:")
                for t in threading.enumerate():
                    logger.debug("\t%30s: %-40s" % (str(t), repr(t)))
            finally:
                self.beating.fall()

        #-----------------------------------------------------------------
        #   .run():
        #
        #       This is the main code for the heart thread.  It will be
        #       called automatically after the thread is started by the
        #       thread startup code.  It should not be called directly
        #       from other threads.
        
    def run(self):
        with self.lock:
            try:                # Make sure to run finally clause on exit.
                while True:         # Indefinitely, 
                    self._beat()         # Beat the heart once.

                        # Wait till we are told to pause, but do not
                        # wait any more than the number of seconds
                        # that there's supposed to be between beats.
                        
                    pause = self.pause.wait(timeout = self.secsPerBeat)
                        #-> Return value indicates whether the flag was raised.
                    
                    if pause:   # If we were actually asked to pause,
                        logger.info("Heart.run(): Heart is pausing.")
                        self.paused.rise()  # Announce we are pausing.
                            # Wait indefinitely for the 'pause' flag to be
                            # touched (in any way) a second time.
                        self.pause.waitTouch()
                        if self.pause:      # If the pause flag is still up,
                            # then it was 'waved' (raised while raised), which
                            # means pause forever, or die.
                            return              # Do finally clause & exit thread.
                        # Otherwise, pause flag was lowered - we can resume.
                        logger.info("Heart.run(): Heart is resuming.")
                        self.paused.fall()
                        # Now we just go back to the start of the loop.

                    # If we get here, it means the pause flag was not
                    # raised, and instead we just timed out of the .wait().
                    # So, just go back up to the top of the loop & beat the
                    # heart again.

                # If the main loop exits, whether due to a .die() call or
                # just an uncaught exception, announce the heart has died.
            finally:
                logger.info("Heart.run(): Heart is dying.")
                self.dead.rise()    # Announce the heart has died.

        #---------------------------------------------------------------------------
        #   .suspend()
        #
        #       Ask the heart to please suspend its beating activity temporarily.
        #       When this routine returns, the heart has paused (although another
        #       thread could immediately restart it, if it's not locked).

    def suspend(inst):
        with inst.lock:
            if inst.dead:
                logger.warn("Heart.pause(): Can't pause the heart, 'cuz it's dead.  Ignoring request.")
                return
            if inst.paused:
                logger.warn("Heart.pause(): Pausing the heart while it's already paused would kill it.  Ignoring request.")
                return
            inst.pause.rise()   # Ask the heart to pause.
            inst.paused.wait()  # Wait for it to actually pause.

        #-------------------------------------------------------------------------
        #   .resume()
        #
        #       If the heart is paused, start it beating again.  When this
        #       returns, the heart has resumed.

    def resume(inst):
        with inst.lock:
            if inst.dead:
                logger.warn("Heart.resume(): Can't resume heartbeat b/c heart is dead.  Ignoring request.")
                return
            if not inst.paused:
                logger.warn("Heart.resume(): Can't resume heartbeat b/c it isn't paused.  Ignoring request.")
                return
            inst.pause.fall()       # Take down the pause flag.
            inst.paused.waitDown()  # Wait for the heart to no longer be paused.

        #---------------------------------------------------------------------
        #   .stutter()
        #
        #       This tells the heart to go ahead and beat now, even if the
        #       normal period between beats has not yet elapsed.  When this
        #       routine returns and the lock is released, the heart should
        #       actually beat immediately afterwards.  (The caller can wait
        #       for that if he has the heart locked in the meantime.) Then
        #       there will be the normal interval before its next beat.
        #       I.e., the phase of the beats will have been shifted.

    def stutter(inst):
        with inst.lock:
            inst.suspend()  # Pause the heart.
            inst.resume()   # Immediately restart it - this makes it beat right away.
            # Here we could wait for it to actually start its next beat, but
            # we'll leave that up to the caller.

        #------------------------------------------------------------------------
        #   .wait()
        #
        #       This default wait method just waits for the heart's
        #       next beat to finish.  Be aware that if you call this
        #       immediately after creating the heart, and you did not
        #       specify start=False, you may very well be too late to
        #       catch the first beat, and you will have to wait for the
        #       next one.  To catch the very first beat, do something
        #       like this:
        #
        #           heart = Heart(start=False)
        #           with heart.lock:
        #               heart.start()
        #               heart.wait()    # Waits for 1st beat to finish.
        #
        #       Also, you can wait on many other heart events, e.g.:
        #
        #           heart.started.wait()    - Waits for heart to be started.
        #           heart.paused.wait()     - Waits for heart to be paused.
        #           heart.paused.waitDown() - Waits for heart to be unpaused.
        #           heart.dead.wait()       - Waits for heart to be dead.
        #           heart.join()            - Waits for heart thread to actually terminate.
        #
        #       But, you can't wait for the beat to start (as opposed to finish),
        #       because throughout the beat, the heart holds onto its threading
        #       lock, so the other threads don't get a chance to return from
        #       their waits until the heart has finished beating anyway.
        
    def wait(inst):
        inst.beating.waitFall()    # Waits for the 'beating' flag to fall after being up.
                #-> NOTE: We can't just do .waitDown() because between beats,
                #       the 'beating' flag is already down.  We can't do waitRise()
                #       followed by waitFall() because the 'beating' flag gets
                #       raised & then lowered as an atomic action in ._beat(),
                #       so we get no chance to enter .waitFall() before the
                #       fall waiters get notified.  We COULD do waitRise()
                #       followed by waitDown(), but this is simpler.

        #--------------------------------------------------------------------------            
        #   .die()
        #
        #       Tell the heart to stop beating and permanently die.  Once dead,
        #       the heart cannot be re-started.
                             
    def die(inst):
        with inst.lock:
            if inst.dead:
                logger.warn("Heart.die(): Heart can't die b/c it's already dead.  Ignoring request.")
                return
            if not inst.started:
                logger.warn("Heart.die(): Can't kill the heart b/c it hasn't even started.  Ignoring request.")
                return
            if not inst.paused:
                inst.suspend()    # First, pause the heart.
            inst.pause.rise()   # Pause it while it's already paused - this kills it.
            inst.dead.wait()    # Wait for it to die.
            inst.join()         # Wait further for the heart thread to actually exit.
