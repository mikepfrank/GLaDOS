#|=========================================================================
#|   flag.py                                 [python module source code]
#|
#|       Checkable, waitable Boolean condition variables.
#|
#|       A Flag is a Boolean condition variable that can be
#|       waited on.  A customer can check (non-blocking) whether
#|       the flag is raised, or he can wait (blocking, with
#|       optional timeout) for it to be raised.  Many other
#|       checkable/waitable flag conditions are also provided -
#|       lowering the flag, changing it, touching it but leaving
#|       its value unchanged (we call this "waving" the flag)
#|       and just touching it (whether it is changed or not).
#|
#|       Most of these options are likely to be used at most
#|       rarely; we could improve Flag's performance by
#|       separating out the rarely-used features into a subclass
#|       named FancyFlag or the like.
#|
#|       NOTE: The standard library class threading.Event() does
#|       part of what we're doing here.  We should perhaps re-
#|       implement Flag as a subclass of threading.Event that
#|       extends it in various ways.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

"""Checkable, waitable Boolean condition variables."""

    # Note: Since this module is so simple and low-level, we do not
    # bother to do any logging (even debug-level logging) within it.
    # So if it were buggy, we'd be screwed.  Fortunately it isn't.  :)

    #|---------------------------------------------------------------------------------
    #| Import all names from the Python standard library's high-level threading module.
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from threading import *

    #|--------------------------------------------------------------------
    #| Our public (exported) names.  These are all the names that will
    #| get imported to another module that does "from flag import *".
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

__all__ = ['Flag']

    #|---------------------------------------------------------------------------------
    #|   Flag                                                   [module public class]
    #|
    #|       Waitable Boolean condition variable.
    #|
    #|       A flag is a boolean variable such that consumers can wait
    #|       for it to be raised (become true), lowered (become false),
    #|       changed (raised or lowered), waved (without changing its
    #|       state), or even for it to be touched in any way.
    #|
    #|       Usage example:
    #|       
    #|           flag = Flag()
    #|
    #|           In thread 1:        In thread 2:            In thread 3:
    #|           ------------        ------------            --------------
    #|            ...                flag.raised.wait()      flag.changed.wait()
    #|           flag.raise() ----->  ...               --->  ...
    #|            ...                flag.waved.wait()       flag.touched.wait()
    #|           flag.wave() ------>  ...               --->  ...
    #|            ...                flag.touched.wait()     flag.waved.wait()
    #|           flag.lower() ----->  ...
    #|           flag.lower() ----------------------------->  ...
    #|
    #|           A flag is created, and thread 2 waits for it to be raised,
    #|           while thread 3 waits for it to be changed.  Thread 1 raises
    #|           the flag, and threads 2 and 3 are both notified and wake up.
    #|           Next, thread 2 waits for the flag to be waved, while thread
    #|           3 waits for it to be touched in any way.  Thread 1 sets the
    #|           to True (up) again - even though it was already up - and so
    #|           it gets waved instead.  Threads 2 and 3 both wake up.
    #|           Finally, thread 2 waits for the flag to be lowered, while
    #|           thread waits 3 for it to be waved.  Thread 1 lowers the flag,
    #|           which wakes up thread 2 but not thread 3.  Then thread 1
    #|           lowers the flag again, which now means wave it back and forth
    #|           while already lowered, which finally causes thread 3 to
    #|           wake up.
    #|
    #|           If you want to wakeup ALL the waiters on a given flag, just
    #|           do a sequence like lower(), raise(), raise(), lower().  This
    #|           includes conditions raised, waved, lowered, changed, and of
    #|           course touch.  If this sequence is done thread-safely (e.g.,
    #|           within a "with flag.lock:" statement), every waiter will only
    #|           get woken up once.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Flag():
    
    """A checkable, waitable Boolean condition variable.
    To check the state of a Flag <flag>, just call it,
    i.e., "flag()", or use it in a boolean context:
    "if flag: ...".  flag.up is a property that may be
    used to query or modify the value of the flag:
    "if flag.up: ..." or "flag.up = True".  You can
    wait for various conditions using the wait...()
    methods provided."""
    
    #|--------------------------------------------------------------------
    #|   Instance data members (private):
    #|
    #|       lock:RLock      - Reentrant mutex lock on the state of this
    #|                               flag, to support atomic, thread-safe
    #|                               operations on it.
    #|       _up:bool        - Current state of this flag.  When true,
    #|                               states that this flag is currently up
    #|                               (i.e., raised).  Users should not
    #|                               modify this attribute directly, but
    #|                               only through the .up property setter
    #|                               or the various provided methods.
    #|
    #|       Available conditions:
    #|           raised      - The flag gets raised.
    #|           lowered     - The flag gets lowered.
    #|           changed     - The flag gets either raised or lowered.
    #|           waved       - The flag gets waved (touched but not raised or lowered).
    #|           touched     - The flag gets changed or waved.
    #|
    #|       We could also add conditions for "the flag gets waved
    #|       when up," and "the flag gets waved when down," but I
    #|       decided we have enough already.  Someone could always
    #|       wait for it to be waved, and then check right away
    #|       (within "with flag.lock:") whether it is up or not.
    #|-------------------------------------------------------------------

    #|--------------------
    #|  Public methods:
    #|vvvvvvvvvvvvvvvvvvvv

        #|---------------------------------------------------------------------
        #|
        #|   .__init__ (initializer)                 [special instance method]
        #|
        #|      Creates our underlying mutex lock and all the condition
        #|      objects associated with the state of this flag.
        #|      Optionally, the initial value of the flag can be passed
        #|      in the initiallyUp parameter, whose value defaults to
        #|      False.  A second optional parameter <lock> provides an
        #|      existing mutex lock to use, instead of creating a new
        #|      one.  The provided lock should be re-entrant (created
        #|      with RLock()).
        #|
        #|      Usage examples:
        #|
        #|          flag = Flag()
        #|          flag = Flag(True)
        #|          flag = Flag(lock = myLock)
        #|          flag = Flag(True, myLock)
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
    def __init__(self, initiallyUp:bool = False, lock:RLock = None):
        
        """Initializes the flag's thread synchronization mechanisms,
        and whether the flag is initially up.  Caller may also provide
        an existing RLock to be used in the condition variables."""
        
        if lock==None:      # If no existing lock is provided,
            lock=RLock()    # create a brand-new lock for this flag.
            
        self.lock = lock    # Remember the lock as an object attribute.
        
        with self.lock:
            self._up = bool(initiallyUp)     # Initialize up/down state.
            
            self.raised  = Condition(self.lock)     # Create conditions.
            self.lowered = Condition(self.lock)     # Note: All conditions
            self.changed = Condition(self.lock)     # share a single lock.
            self.waved   = Condition(self.lock)     # This is important.
            self.touched = Condition(self.lock)

        #|-----------------------------------------------------------------------
        #|  .__call__ (call handler)                 [special instance method]
        #|
        #|      This enables a flag to be called (invoked), like "flag()".
        #|      It returns the flag's value.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __call__(self):     # If a flag is called,
        """Returns a Boolean value indicating whether the flag is up."""
        return self._up         # just return its up-state boolean.

        #|-----------------------------------------------------------------------
        #|  .__bool__ (boolean context handler)      [special instance method]
        #|
        #|      This enables a flag to be used in a Boolean context, like
        #|      "if flag: ...".  It returns the flag's value.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __bool__(self):     # If a flag is used in a Boolean context,
        """Returns a Boolean value indicating whether the flag is up."""
        return self._up         # return its up-state boolean.
    
        #|--------------------------------------------------------------------------
        #|   .up                                    [public instance property]
        #|
        #|      Property methods.  These allow the user to query and assign
        #|      to "flag.up" as if it were just an attribute, and have the
        #|      appropriate notifications handled automatically.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        
    @property
    def up(self):
        """This is the property that the flag is up (raised)."""
        return self()

    @up.setter
    def up(self, value:bool):
        """This is the setter method for the flag.up property."""
        self.setTo(value)

        #|-----------------------------------------------------------------------------
        #|
        #|  .rise(), .fall(), .change(),                [public instance methods]
        #|  .touch(), .wave()
        #|
        #|      Extra modification methods.  Use these to send notifications
        #|      to specific classes of listeners.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def rise(self):         # Tells flag to raise itself.
        """Raise this flag (if already raised, waves it instead).
            Returns the previous value of the flag."""
        return self.setTo(True)              # Set the state & return old state.

    def fall(self):        # Tells flag to lower itself.
        """Lower this flag (if already lowered, waves it instead).
            Returns the previous value of the flag."""
        return self.setTo(False)             # Set the state & return old state.

    def change(self):       # Toggle the state of the flag; up->down, down->up.
        """Toggle the up/down state of this flag.
            Returns the previous value of the flag."""
        return self.setTo(not self.up)       # Set the state & return old state.

    def touch(self):        # Just touch the flag - do not wave it or change it.
        """Touch the flag, but do not change its up/down state.
            Returns the value of the flag."""
        with self.lock:                 # Thread-safely,
            self.touched.notify_all()       # Notice it was touched.
            return self()                   # Return the flag's state.

    def wave(self):         # Just wave the flag (but do not change its up/down state.
        """Wave the flag, but do not change its up/down state.
            Returns the value of the flag."""
        with self.lock:                 # Thread-safely,
            self.touch()                    # Touch the flag.
            self.waved.notify_all()         # Notice flag was waved.
            return self()                   # Return the flag's state.

        #|----------------------------------------------------------------------------------------
        #|
        #|      .setTo()                                            [public instance method]
        #|
        #|          This is the main method that handles all interactions
        #|          that possibly modify the flag's state.  It sets the flag's
        #|          "up" state to the given Boolean <beUp>, and does appropriate
        #|          notifications.  It returns the previous state of the flag.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def setTo(self, beUp:bool):
        """Set whether the flag is up to the given boolean value <beUp>."""
        beUp = bool(beUp)               # Convert argument to pure Boolean (type bool).
        with self.lock:                 # Thread-safely,
            wasUp = self._up                 # Remember whether the flag was up before.
            self._up = beUp                  # Go ahead and put it in its new state.
            if wasUp == beUp:                # If its state has not changed,
                self.wave()                     # just wave the flag instead (touches it too).
            else:                            # else
                self.touch()                    # Touch the flag.
                self.changed.notify_all()       # Notice its state was changed.
                if beUp:                        # If it was just raised,
                    self.raised.notify_all()        # notice that;
                else:                            # if it was just lowered;
                    self.lowered.notify_all()       # notice that.
            return wasUp                        # Return the previous state of the flag.

    #|------------------------------------------------------------
    #|  Below here are all our various wait methods.  A client
    #|  can also directly call .wait() on any of our condition
    #|  attributes directly.  But the following are more concise.
    #|  All <timeout> parameters are floating-point seconds, as
    #|  in Threading.Condition.wait().
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|--------------------------------------------------------------------------------------
        #|
        #|      .waitRise(), .waitFall(), .waitChange()             [public instance methods]
        #|
        #|          These wait methods wait for a change of a specific type
        #|          to happen.  E.g., if a flag is already up, waitRise() will
        #|          wait for it first to be lowered, and then to rise again.
        #|          I.e., they are "edge-sensitive" waits.
        #|
        #|          If a timeout is specified, these routines return False if
        #|          the wait timed out.  Otherwise they return True.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
 
    def waitRise(self, timeout=None):     # Wait for this flag to rise.
        """Wait for the flag to go from a down state to an up state."""
        with self.lock:         # Thread-safely,
            self.raised.wait(timeout)      # Wait for it to be raised.
            return self()   # Return True if the flag is up - otherwise we timed out.

    def waitFall(self, timeout=None):     # Wait for this flag to fall.
        """Wait for the flag to go from an up state to a down state..."""
        with self.lock:         # Thread-safely,
            self.lowered.wait(timeout)     # Wait for it to be lowered.
            return not self()           # Return True if flag is lowered - else we timed out.

    def waitChange(self, timeout=None):   # Wait for this flag to change.
        """Wait for the flag's state to be changed."""
        with self.lock:         # Thread-safely,
            oldstate = self()               # Remember the original value of the flag.
            self.changed.wait(timeout)      # Wait for its state to be changed.
            return self() != oldstate       # Did it actually change, or did we just time out?

        #|-----------------------------------------------------------------------------------------
        #|
        #|      .waitWave(), .waitTouch()                           [public instance methods]
        #|
        #|          These wait methods wait for events that do not necessarily
        #|          result in the state of the flag actually changing.
        #|
        #|          An optional timeout may be provided, but there is no way to
        #|          tell whether we timed out, or the event actually occurred.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def waitWave(self, timeout=None):     # Wait for this flag to be waved (touched but left unchanged).
        """Wait for the flag to be touched but left unchanged."""
        with self.lock:
            self.waved.wait(timeout)

    def waitTouch(self, timeout=None):    # Wait for this flag to be touched (whether changed or not).
        """Wait for the flag to be touched in any way, whether changed or not."""
        with self.lock:
            self.touched.wait(timeout)

        #|--------------------------------------------------------------------------------------
        #|
        #|      .waitUp(), .waitDown()                              [public instance methods]
        #|
        #|          These wait methods wait for a certain flag state to occur,
        #|          but they do not wait at all if the state is already present.
        #|          I.e., they are "level-sensitive" waits.
        #|
        #|          If the optional timeout is specified and the wait times out,
        #|          False is returned.  Otherwise, True is returned.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
    def waitUp(self, timeout=None):       # Wait for this flag to be up.
        """If the flag is not already up, wait for it to go up."""
        with self.lock:         # Thread-safely,
            if self.up:             # If the flag was already up,
                return True             # Return True.
            else:                   # If the flag's not already up,
                self.waitRise(timeout)  # Wait for it to be raised.
                return self.up          # Return True unless we just timed out.

    def waitDown(self, timeout=None):     # Wait for this flag to fall.
        """If the flag is not already down, wait for it to go down..."""
        with self.lock:         # Thread-safely,
            if self.up:             # If the flag is up,
                self.waitFall(timeout)         # Wait for it to be lowered.
                return not self.up             # Return true if we didn't just time out.
            else:
                return True             # Flag is already down.

        #|-------------------------------------------------------------------------------------
        #|
        #|      .wait()                                             [public instance method]
        #|
        #|          Default wait() method.  Waits for the flag to be up.  Note
        #|          this method returns right away if the flag is already up.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def wait(self, timeout=None):         # The default wait method on a flag
        """If the flag is not already up, wait for it to go up."""
        return self.waitUp(timeout)           # is to wait for it to be up.

    #|^^^^^^^^^^^^^^^^^^^^^^^^^^
    #|  END CLASS:  Flag
    #|--------------------------

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|  END FILE:   flag.py
#|=================================================================================================
