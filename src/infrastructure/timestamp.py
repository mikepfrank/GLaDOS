#|***************************************************************************
#|
#|      FILE:   timestamp.py                    [python module source file]
#|
#|      SYSTEM CONTEXT:
#|          This module was developed as a component of the COSMICi
#|          central server app; it is not intended to be executed as
#|          a standalone top-level Python program.  However, it may
#|          also be reusable within other applications.
#|
#|      DESCRIPTION:
#|          This file defines a Python module that provides abstract
#|          data types (classes) for various kinds of time stamps,
#|          that is, representations of the absolute real time, in
#|          some appropriate representational framework.
#|              So far, it only has support for a single type of time
#|          stamp, a CoarseTimeStamp, which has 1 ms resolution and
#|          is typically used for time measurements based on NTP which
#|          have on the order of 10 ms accuracy.
#|
#|      IMPORTED BY:
#|          ...
#|
#|      IMPORTS:
#|          time    (standard Python library module)
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|======================================================================
    #|  Imports & constants.                                [code section]
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import  time     # CoarseTimeStamp.__str__() uses time.ctime().

__all__ = ['CoarseTimeStamp']   # Export this name to modules that do 'from timestamp.py import *'

    #|=============================================================================
    #|
    #|  CLASS:  CoarseTimeStamp                         [public module class]
    #|
    #|      This abstract data type is for a coarse absolute time stamp
    #|      encoded in terms of two integers: Seconds since the epoch
    #|      (e.g., midnight of Jan. 1, 1970), and milliseconds since the
    #|      start of that second.  These time measurements can be derived
    #|      via NTP via the host's system clock, and are deemed accurate
    #|      to within about +/- 10 milliseconds.
    #|
    #|  DATA MEMBERS:
    #|
    #|      fsecs - Number of seconds since the epoch, as a floating-point #.
    #|              This is redundant with the below two fields, but is
    #|              included for convenience (and in case milliseconds had
    #|              a fractional part).
    #|
    #|      secs - Exact number of full seconds since the epoch (UTC).
    #|              The epoch on COSMICi PC (running Windows Vista) is
    #|              defined as the start of January 1st, 1970.
    #|
    #|      msecs - Number of milliseconds past the start of that second.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class CoarseTimeStamp():

        #|------------------------------------------------------------------
        #|
        #|      METHOD:     __init__()          [special instance method]
        #|
        #|          This instance initializer takes the current
        #|          time as a floating-point number of seconds
        #|          since the epoch, and breaks it up into integer
        #|          seconds & milliseconds appropriately.  The
        #|          milliseconds are rounded to the nearest integer.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    def __init__(self, floating_time):
        self.fsecs = floating_time
        self.secs = int(floating_time)
        self.msecs = round(1000*(floating_time - self.secs))
    #<-- End method __init__().

        #|-------------------------------------------------------------------
        #|
        #|      METHOD:     __str__()           [special instance method]
        #|
        #|          This string converter uses the default ctime()
        #|          format, and appends " + ddd ms" for the
        #|          milliseconds part, where d are decimal digits.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    def __str__(self):
        return time.ctime(self.secs) + (" + %3d ms" % self.msecs)
    #<-- End method __str__().

#<-- End class CoarseTimeStamp().

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|  END FILE:   timestamp.py
#|************************************************************************************************
