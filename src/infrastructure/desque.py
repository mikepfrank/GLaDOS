#===================================================================
#   desque.py                           [python module source code]
#
#       Double-Ended Synchronized QUEue.  (Say "desk.")
#
#       This is similar to a collections.deque (say "deck"), but
#       it is thread-safe, supporting multiple simultaneous
#       producer and consumer threads.
#
#       It is also similar to a queue.Queue, but it supports
#       pushing items onto either end of the queue.
#
#       The rationale for a desque is as follows:  A consumer
#       thread or worker thread pops items off the front of the
#       queue.  Usually, producer threads provide items that need
#       to be processed in ordinary FIFO order.  But occasionally,
#       a producer thread has a high-priority item (such as a
#       command stopping the consumer thread) that needs to be
#       processed by the consumer thread ahead of everything else.
#       In such cases, the producer should be able to just stick
#       the item onto the head of the queue, "cutting in line"
#       ahead of everyone else.  A regular Queue doesn't allow this.
#       And a priority queue is too much overhead if all we need is
#       a front vs. rear push option.
#
#       The Desque is implemented by subclassing Queue and over-
#       riding its put() and put_nowait() methods to add an extra
#       argument (front=False), and adding a new internal method
#       _putleft(), which does the actual insert using the under-
#       lying Deque object's appendleft().  We also add putfront()
#       and putfront_nowait() methods, as more concise alterna-
#       tives to the extra argument.
#
#===================================================================

"""A double-ended, synchronized (thread-safe) queue."""

    # These imports are copied from queue.py.

from time import time as _time
try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading
#from collections import deque  # I don't think we're using this.
#import heapq                    # I don't think we're using this.

    # We also import everything from the queue module - since
    # we're trying to extend it.

from queue import *

# Note: For the moment, we consider desque to be too low-level
# to bother trying to do any debug logging within it.  However,
# if we experience problems with it later, we might change this.

    # We re-export queue's Empty and Full exceptions, as well as our
    # new Desque class.  If the user needs any of the other queue.py
    # classes, he should import * from queue, or import desque and
    # explicitly use desque.Queue, etc.

__all__ = ['Empty', 'Full', 'Desque']


class Desque(Queue):

        # We override Queue's initializer.  This is because Queue creates
        # a primitive lock, but we want to use a re-entrant lock (RLock).
        # This should be the same as queue.Queue.__init__() except for
        # the assignment to self.mutex.  It may need to be updated in
        # the future for compatibility with future versions of the
        # queue module.

    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)
        
            # mutex must be held whenever the queue is mutating.  All methods
            # that acquire mutex must release it before returning.  mutex
            # is shared between the three conditions, so acquiring and
            # releasing the conditions also acquires and releases mutex.
        self.mutex = _threading.RLock()     # NEW TO DESQUE: USE RLock instead of Lock
        
            # Notify not_empty whenever an item is added to the queue; a
            # thread waiting to get is notified then.
        self.not_empty = _threading.Condition(self.mutex)
        
            # Notify not_full whenever an item is removed from the queue;
            # a thread waiting to put is notified then.
        self.not_full = _threading.Condition(self.mutex)
        
            # Notify all_tasks_done whenever the number of unfinished tasks
            # drops to zero; thread waiting to join() is notified to resume
        self.all_tasks_done = _threading.Condition(self.mutex)
        
        self.unfinished_tasks = 0
    #<-- end method Desque.__init__()
        
        # This new method (which depends on our re-entrant lock)
        # simply drains all items from the queue, one at a time, without
        # processing or returning any of them.  At the moment it returns,
        # the queue is guaranteed to be empty (although it may get re-
        # filled immediately afterwards if not still locked).

    def flush(self):
        with self.mutex:     # Blocks queue changes by other threads while in here.
            try:
                while True:
                    self.get(block=False)
            except Empty:
                return

        # Override Queue's put() method.  This implementation should be
        # identical to queue.Queue.put(), except for the extra "front"
        # argument, and how that is used.  It may need to be updated
        # in the future for compatibility with future versions of the
        # queue module.

    def put(self, item, block=True, timeout=None, front=False):
        """Put an item into the queue, at either end.

        If the optional argument front is True, then the new item
        is inserted at the front of the queue, rather than
        at the back.  This is useful for high-priority items.

        See queue.Queue.put() for remaining documentation.
        """
        self.not_full.acquire()
        try:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() == self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() == self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a positive number")
                else:
                    endtime = _time() + timeout
                    while self._qsize() == self.maxsize:
                        remaining = endtime - _time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            if front:
                self._putleft(item)
            else:
                self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
        finally:
            self.not_full.release()

        # Override put_nowait() in similar fashion.

    def put_nowait(self, item, front=False):
        """Put an item into the queue without blocking.

        Only enqueue the item if a free slot is immediately available.
        Otherwise raise the Full exception.

        If the optional argument front is True, then the new
        item is inserted at the front of the queue, rather
        than the back.
        """
        return self.put(item, False, front=front)

        # Provide new public putfront() and putfront_nowait() methods.

    def putfront(self, item, block=True, timeout=None):

        """Put an item onto the front of the queue.  See the
        documentation for desque.Desque.put() or queue.Queue.put()
        for the meaning of the options."""

        return self.put(item, block=block, timeout=timeout, front=True)

    def putfront_nowait(self, item):
        """Put an item onto the front of the queue without blocking.

        Only enqueue the item if a free slot is immediately available.
        Otherwise raise the Full exception.
        """

        return put_nowait(self, item, front=True)

        # Define new private _putleft() method to implement the
        # actual work of putting items at the front of the queue.
        # Subclasses may override this if needed to use a
        # different underlying data structure (we use a deque,
        # same as queue.Queue does).  USERS SHOULD NOT CALL
        # _putleft DIRECTLY, BUT ONLY THROUGH put(), etc. ABOVE.

    def _putleft(self, item):
        self.queue.appendleft(item)

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|  END FILE:   desque.py
#|============================================================================
