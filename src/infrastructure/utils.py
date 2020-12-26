#|*****************************************************************************
#|                              TOP OF FILE
#|*****************************************************************************
#|
#|      FILE NAME:  utils.py                        [python module source code]
#|
#|          Miscellaneous utilities.  These include the
#|          following network-related utility functions:
#|
#|              get_hostname()  - Get first (pre-".") component of current
#|                               machine's hostname.
#|
#|              get_my_ip() - Get the IP address (in standard format) of
#|                               the current machine.
#|
#|          as well as the following class/object related functions/classes:
#|
#|              bind() - Bind a class method to a specific instance.
#|
#|              become() - Reassign the given object to a new class.
#|
#|              MutableClass - Base class for objects that can change class.
#|
#|          and the string functions:
#|
#|              unsplit() - Concatenate a list of strings with a given
#|                              delimiter in between.
#|
#|          and another useful class:
#|
#|              WatchBox - A watchable storage location.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    # Imports from standard python modules.

import threading    # RLock
from socket import gethostname, gethostbyname
    # these are used in get_hostname(), get_my_ip()

import infrastructure.flag     # Flag

    # Public names we export from this module to other modules that do
    # "from utils import *"

__all__ = ['get_hostname', 'get_my_ip',         # Networking functions.
           'bind', 'become', 'MutableClass',    # Class manipulation.
           'countLines', 'unsplit', 			# String manipulation.
		   'WatchBox' ]                         # Watchable storage box.

    #|=====================================================================
    #|
    #|   get_hostname()                          [module public function]
    #|
    #|       Get the name of the host (computer) this server is
    #|       running on - the part before the first dot (if any), only.
    #|
    #|       So far, it has been tested under Windows Vista as well as
    #|       Mac OS X (Darwin).
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
def get_hostname():
    full_hostname = gethostname()
    first_part = full_hostname.partition('.')[0]
    return first_part

    #|======================================================================
    #|
    #|   get_my_ip()                             [module public function]
    #|
    #|       Gets the IP address of the default interface of the
    #|       host (computer) this server application is running on.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def get_my_ip():
    full_hostname = gethostname()
    my_ip = gethostbyname(full_hostname)
    return my_ip

    #|======================================================================
    #|
    #|      bind()                                      [public function]
    #|
    #|          Given an object instance and a class method (or any
    #|          function), binds the instance as the first argument
    #|          of the method (the one whose formal name is usually
    #|          something like "self", "this", or "inst"), and returns
    #|          the newly-created lambda, which can then serve as an
    #|          instance method.  For an example of usage, see the
    #|          HireCurThread() function in worklist.py.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def bind(inst:object, classMethod):
    return lambda *args, **kwargs: classMethod(inst, *args, **kwargs)

    #|======================================================================
    #|
    #|      become()                            [universal object method]
    #|
    #|          This new custom special method can be installed as a
    #|          method that applies to an object of any user-defined
    #|          or otherwise-mutable class.  It changes the object's
    #|          class to the new class given.  The new class
    #|          <newClass> must supply a special method
    #|          .__convertFrom(oldClass) which mutates instances of
    #|          the origin class <oldClass> into instances of the new
    #|          class <newClass> by applying any necessary additional
    #|          initialization.  Any extra arguments are passed thru
    #|          to the .__convertFrom() method.
    #|
    #|      Example usage:
    #|
    #|          class A:
    #|              def __init__(this):
    #|                  this.become = bind(this, become)
    #|
    #|          class B:
    #|              def __convertFrom(this, oldClass:type): pass
    #|
    #|          obj = A()
    #|          obj.become(B)
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def become(obj:object, newClass:type, *args, **kwargs):
    oldClass = obj.__class__
    #print("About to switch object %s from class %s to class %s...\n" % (str(obj), str(oldClass), str(newClass)))
    obj.__class__ = newClass
    if hasattr(obj, '_convertFrom'):
#        print("About to _convertFrom %s to %s...\n" % (str(oldClass), str(newClass)))
        obj._convertFrom(oldClass, *args, **kwargs)
        
    else:
        print("WARNING: utils.become(): Destination class has no .__convertFrom() method.")
    
#    if '__convertFrom' in newClass.__dict__:
#    newClass.__convertFrom(obj, oldClass, *args, **kwargs)


    #|=======================================================================
    #|
    #|      MutableClass                            [module public class]
    #|
    #|          An instance of class MutableClass can be
    #|          changed to be a direct instance of any
    #|          other subclass of class MutableClass using
    #|          the .become() method.
    #|
    #|          Subclasses should override the _convertFrom()
    #|          method as necessary to meet their specific
    #|          conversion needs.
    #|
    #|      Example usage:
    #|
    #|          class A(MutableClass): pass
    #|          class B(MutableClass): pass
    #|
    #|          obj = A()           # Create new object of class A.
    #|          obj.become(B)       # Object is now in class B.
    #|          obj.become(A)       # Object is now in class A again.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class MutableClass:

    def become(this, newClass:type, *args, **kwargs):
        become(this, newClass, *args, **kwargs)         # call function
        
#    def __init__(this):
#        this.become = bind(this, become)

        # Convert this object from its previous class <oldClass>
        # to the new class.  This placeholder method should be
        # overridden by subclasses of MutableClass as necessary.
        
    def _convertFrom(this, oldClass:type):   pass


def countLines(text:str = None):

	if text == None:		# None has no lines.
		return 0
	else:
		return 1 + text.count('\n')
			# The above treats even an empty string as 1 line,
			# and each newline character adds an additional line.

    # Un-split a list of strings using a given delimiter character.
    # The list must be non-empty. NOTE: Obsoleted by .join()

def unsplit(strs, delim:str):
	return delim.join(strs)
#    result = strs[0]
#    for s in strs[1:]:
#        result = "%s%s%s" % (result, delim, s)      # There must be an easier way to concatenate strings!
#    return result

def overwrite(botStr:str, pos:int, topStr:str, extend:bool=False):

	"""Overwrite the given 'bottom string', starting at position 'pos', 
		with the given 'top string.'  The last argument specifies whether
		to extend the total length of the string if needed."""
		
	botLen = len(botStr)
	topLen = len(topStr)
	
	# Initialize result to first part of bottom string, before pos.
	res = botStr[:pos]
	
	if pos + topLen > botLen:		# Doesn't fit
		if extend:
			res = res + topStr
		else:
			res = res + topStr[:(botLen - pos)]
	else:
		res = res + topStr + botStr[(pos + topLen):]

	return res

    #|======================================================================
    #|
    #|      utils.WatchBox                          [module public class]
    #|
    #|          An object of class WatchBox is simply a place to
    #|          store things, with an associated flag that is raised
    #|          whenever the stored thing is replaced.  Threads can
    #|          then wait for the flag to be touched to be informed
    #|          when the stored thing has been updated.  All public
    #|          properties and methods are thread-safe.
    #|
    #|      Notes:
    #|
    #|          Should this go into a module by itself?
    #|
    #|      Private instance data members (user code should not access
    #|      these directly):
    #|
    #|          ._lock:threading.RLock -
    #|
    #|                  Reentrant mutex lock guarding access to
    #|                  the WatchBox structure for consistency.
    #|
    #|          ._contents:object -
    #|
    #|                  The object contained in the box.  A
    #|                  WatchBox can only contain one object
    #|                  at a time.
    #|
    #|          ._updated:flag.Flag -
    #|
    #|                  A flag that is raised (if not already
    #|                  raised) or waved (if already raised)
    #|                  whenever the box's contents are updated.
    #|          
    #|
    #|      Special methods:
    #|
    #|          .__init__(initialContents, lock)
    #|
    #|              New instance initializer.  The box's initial
    #|              contents and the RLock to use may be optionally
    #|              specified.  If not specified, the initial contents
    #|              are None and a new RLock is created.
    #|
    #|          .__call__()
    #|
    #|              Call method.  When the box is called, it simply
    #|              returns its current contents.
    #|
    #|      Public properties:
    #|
    #|          .contents -
    #|
    #|              The present contents of the WatchBox.  That is,
    #|              if box is a WatchBox, then box.contents evaluates
    #|              to the box's present contents, which you can
    #|              modify using "box.contents = <newValue>".
    #|              Waiters are alerted on modification.
    #|
    #|      Public methods:
    #|
    #|          .hold(newContents) -
    #|
    #|              Modifies the box's contents, causing it to hold
    #|              the given <newContents>.  Returns the previous
    #|              contents.
    #|
    #|          .wait(timeout) -
    #|
    #|              Waits for an optional timeout (which defaults to
    #|              None, meaning wait indefinitely) for the box's
    #|              contents to be updated.  When updated, returns
    #|              the new contents.
    #|
    #|      Example usage:
    #|
    #|          In thread 1:
    #|
    #|              box = WatchBox(1)       # create box w. initial contents
    #|              print(box())            # prints 1
    #|              box.contents = 2        # use property setter
    #|
    #|          In thread 2:
    #|
    #|              newVal = box.wait()     # wait for contents to be updated
    #|              print(newVal)           # prints 2
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class WatchBox:

    """A watchable storage location.  To check the state of
        a WatchBox <box>, just call it, i.e., "box()".
        box.contents is a property that may be used to
        retrieve or modify the contents of the box.  You
        can wait for the box's contents to be updated using
        the box.wait() method."""
    
    def __init__(this, initialContents:object=None, lock=None):
        """Instance initializer for objects of class WatchBox."""
        if lock == None:  lock=threading.RLock()
        this._lock = lock
        this._contents = initialContents
        this._updated = flag.Flag(lock=this._lock, initiallyUp=False)

    def __call__(this):
        """Calling a box just returns its current contents."""
        return this._contents

    def hold(this, newContents):
        """Causes the box to hold new contents.  Alerts any waiters.
            Returns the previous contents of the box."""
        with this._lock:
            oldContents = this._contents
            this._contents = newContents
            this._updated.rise()            # Raise or wave the 'updated' flag.
        return oldContents

    def wait(this, timeout=None):
        """Waits for the contents of the box to be updated.
            Takes an optional timeout argument.  Returns the
            new contents of the box."""
        with this._lock:
            this._updated.waitTouch(timeout)    # Wait for 'updated' flag to be touched.
            return this()

    @property
    def contents(this):
        """This is the box.contents property getter."""
        return this()

    @contents.setter
    def contents(this, newContents):
        """This is the setter method for the box.contents property."""
        this.hold(newContents)

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|  END FILE utils.py.
#|=============================================================================
