#|==============================================================================
#|                                  TOP OF FILE
#|==============================================================================
#|
#|  FILE:  communicator.py                          [python module source file]
#|
#|  SYNOPSIS:
#|  ---------
#|      This file defines a module which provides a useful abstraction 
#|	for a special type of TCP server that can be asynchronously 
#|	commanded to deliver messages along its reply connection, and 
#|	can be monitored by multiple customers.
#|
#|      Variations to support line-buffered I/O, including streams
#|      other than TCP sockets, are also provided.
#|
#|  SYSTEM CONTEXT:
#|  ---------------
#|	This module was originally written to be a component of the 
#|	COSMICi Central Server application.  However, it is designed
#|	to be useful & easily reused within other future applications.
#|
#|  REVISION HISTORY:
#|  -----------------
#|      v0.1 (2009)   - Original version developed by M. Frank.
#|      v0.2 (2/2/11) - Adding StreamLineConnection class to
#|                          support non-TCP-socket-based I/O.
#|
#|  PROGRAMMING LANGUAGE:	Python 3.1.1
#|					(other versions not yet tested)
#|
#|  OPERATING SYSTEMS:		Microsoft Windows Vista Ultimate SP1
#|					(others not yet tested)
#|
#|  DESCRIPTION:
#|  ------------
#|
#|	A Communicator is a multithreaded server object that is told
#|	to listen for incoming connections on a particular TCP port.
#|
#|	The entity that creates the Communicator, as well as other
#|      entities, can register with the communicator to be informed
#|      when new connections come in.
#|
#|	When a connection request comes in, a new Connection object 
#|	is created to handle that connection.  This new Connection
#|	object is also given to the entities who registered to be
#|	informed of new connections.
#|
#|	A customer of the Connection can register to be informed
#|	of incoming (or outgoing) messages on that connection.
#|
#|	A new thread is created to handle incoming messages on the
#|	connection.  Each message that comes in is bundled together
#|	into a new Message object.  This Message object is sent
#|      (via message handler callbacks) to all the consumers who
#|      have registered to be informed of the incoming message.
#|
#|	A message consumer, or any other entity with a handle to
#|	the connection, may at any time create and send an outgoing
#|	message on that same connection.  This may be done 
#|	asynchronously from other threads.  Locking is used to
#|	make sure that only one outgoing message at a time is sent
#|	using the given connection.
#|
#|      In general, for all handler lists, the most recently added
#|      handler will be invoked last.  And when broadcasting a
#|      message to all open client connections for a given server,
#|      the message will be sent to the most recently-added
#|      connection last.
#|
#|	This file also provides a subclass LineCommunicator (and
#|	associated classes LineConnection, etc.) which is just like
#|	Communicator except that it is designed for line-buffered
#|	text I/O as opposed to raw binary (byte stream) I/O.
#|
#|
#|  CODING TO-DO:
#|  -------------
#|
#|	 [ ] Add StreamLineConnection class to provide a 
#|           LineConnection-like interface to arbitrary I/O
#|           stream pairs, that is, where the streams do not
#|           necessarily interface to an underlying TCP socket.
#|           This permits STDIO, for example, to be utilized in
#|           the same manner as a connection from a remote node.
#|
#|       [,] Inform message handlers for a given connection of
#|           the outgoing messages on that connection, as well as
#|           the incoming messages.  (Coded, not yet tested.)
#|
#|       [ ] Handle closing of connections cleanly.  All connection
#|           handlers should be informed appropriately.
#|
#|       [ ] Override methods of ThreadedTcpServer superclass to
#|           use a temporary client connection (instead of periodic
#|           wakeups) to check for asynchronous server shutdown
#|           requests.
#|
#|  PROVIDES:
#|  ---------
#|
#|      Special globals:
#|          __all__             List of module's public names.
#|
#|      Public globals:
#|
#|          DIR_IN, DIR_OUT     Tokens for message directions.
#|
#|      Public classes:
#|
#|          SocketBroken            Exception: Broken TCP connection.
#|
#|          Message                 Incoming/outgoing message object.
#|
#|          BaseMessageHandler      Base class for message handling classes.
#|
#|          Connection              Represents an open TCP connection.  Passes
#|                                      messages between customer & socket.
#|                                      Connections are active worker threads.
#|
#|          BaseConnectionHandler   Base class for classes that handle newly-
#|                                      created connections.
#|
#|          CommRequestHandler      Handler for a given incoming connection
#|                                      request from a remote client nodes.
#|
#|          Communicator            A server that listens for connection
#|                                      requests on a given TCP port.
#|
#|          LineConnection          Subclass of Connection for doing line-
#|                                      buffered text I/O.
#|
#|          StreamLineConnection    Subclass of LineConnection for doing
#|                                      line-buffered I/O to streams that
#|                                      don't originate from TCP requests.
#|
#|          LineCommReqHandler      Subclass of CommRequestHandler for
#|                                      handling line-buffered requests.
#|
#|          LineCommunicator        Subclass of Communicator specialized
#|                                      for serving line-buffered connections.
#|
#|
#|   USAGE:      (the below documentation is obsolete & needs updating)
#|   ------
#|
#|       import communicator
#|
#|           # Define my application-specific message-handling subclass.
#|
#|       class MyMessageHandler(communicator.BaseMessageHandler):
#|           def handle(msg): ...    # Does whatever
#|
#|           # Define my application-specific connection-handling subclass.
#|
#|       class MyConnHandler(communicator.BaseConnectionHandler):
#|           def handle(conn):
#|               self.msgHandler = MyMessageHandler()    # Create a specialized message handler for this connection.
#|               conn.addMsgHandler(self.msgHandler)     # Register it.
#|
#|           # Create a Communicator server on the IP and port number I want to listen to.
#|
#|       comm = communicator.Communicator((listen_to_ip, listen_to_port))
#|
#|           # Create and register an instance of my application-specific connection handler.
#|
#|       myConnHandler = MyConnHandler()
#|       comm.addConnHandler(myConnHandler)
#|
#|           # Tell the Communicator to go ahead and start accepting connections.
#|
#|       comm.startListening()       # Starts work in background thread; returns immediately.
#|
#|
#|   Classes we provide:    (also obsolete and/or incomplete; needs updating)
#|   -------------------
#|
#|       BaseMessageHandler      - Base class for MessageHandler objects.
#|       ------------------
#|               handle(msg)          - Default handle() method does nothing - override it.
#|
#|       Message                 - A single incoming (or outgoing) message on a connection.
#|       -------
#|               .__init__(...)       - Constructor for new messages.
#|               .data                - The raw data contained in the message.
#|               .conn                - What connection this message came in on (if an incoming message).
#|               .replyWith(msg)      - Reply to this message (on its connection) with a given new message.
#|               .sendOut(conn)       - Send this message out on a given connection.
#|               .replyTo(msg)        - Send this message as a reply to given message received earlier.
#|
#|       BaseConnectionHandler       - Base class for ConnectionHandler objects.
#|       ---------------------
#|               handle(conn)            - Default handle() method does nothing.  Override it!
#|
#|       Connection              - Represents a single TCP connection to a client.
#|       ----------
#|               .__init__(...)      - Constructor for new connections.
#|
#|           Private members:
#|
#|               ._announce(msg)     - Announce a given message to the registered message handlers.
#|               ._wlock             - Multithreading write lock to fields of this object.
#|
#|           Public members:
#|
#|               .comm               - The communicator that this connection is from.
#|               .req                - The socket for the requested connection.
#|               .thread             - The thread handling this connection.
#|               .msgHandlers        - List of registered message handlers.
#|               .addMsgHandler()    - Register a new message handler.
#|               .sendOut(msg)       - Send a given message outwards on this connection.
#|
#|       Communicator        - Provides bidirectional access to TCP connections.
#|       ------------
#|               .__init__()         - Constructor for new communicators.
#|
#|           Private members:
#|
#|               ._wlock             - Multithreading write lock to fields of this object.
#|               ._addConn()         - Add a new connection (& announce it to the registered connection handlers).
#|               ._announce()        - Call the registered connection handlers on a new connection.
#|
#|           Public members:
#|
#|               .connHandlers       - List of registered connection handlers.
#|               .addConnHandler()   - Register a new connection handler.
#|
#|               .conns              - Currently active connections.
#|               .sendAll(msg)       - Send a given message out on ALL currently active connections.
#|
#|               .startListening()   - Starts the communicator listening (in a new daemon thread).
#|               .thread             - Main thread handling this communicator.
#|
#|
#|   Classes user should subclass:
#|   -----------------------------
#|
#|       BaseConnectionHandler   - Handles new incoming connection requests.
#|
#|       BaseMessageHandler      - Handles individual incoming messages.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#|=============================================================================================
#|
#|  Imports.                                                                    [code section]
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|==============================================
    #|  Imports of standard python library modules.
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
                        # User                          Uses
                        # ----                          -----
import io               # LineCommReqHandler.setup()    BufferedRWPair
import time             # CommRequestHandler.handle()   time()
    # -We record receipt time of incoming messages ASAP in case handlers need an accurate value.
import socket           # For recv() and send() calls.
#import logging          # For logging support. (superseded by logmaster below)
import threading        # Provides high-level multithreading support.
import socketserver     # Provides the general framework for threaded TCP servers that we use.

    #|==============================
    #|  Imports of custom modules.
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import timestamp            # Message.__init__()            CoarseTimeStamp
from appdefs import *       # Defines systemName, appName
import logmaster
from logmaster import *     # Note: This only gets pre-configuration copies of globals!
from worklist import *      # Defines Worker class.
import flag

#|=============================================================================================
#|
#|      Globals.                                                            [code section]
#|
#|          The module's global constants and global variables are defined in
#|          this section.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|===================
    #|  Special globals.
    #|vvvvvvvvvvvvvvvvvvv

__all__ = ['Message',               'BaseMessageHandler', 	# Public classes.
	   'Connection',            'BaseConnectionHandler', 
	   'CommRequestHandler',    'Communicator',
           'LineConnection',        'StreamLineConnection',
           'LineCommReqHandler',    'LineCommunicator',
	   'DIR_IN', 'DIR_OUT',		                        # Public constants.
	   ]


    #|===================
    #|  Public globals.
    #|vvvvvvvvvvvvvvvvvvv

global DIR_IN, DIR_OUT      # Message directions (string constants).
DIR_IN  = 'in'                  # Means: This message is coming IN to the server, from a client.
DIR_OUT = 'out'                 # Means: This message is going OUT to one or more clients, from the server.


    #|====================
    #|  Private globals.
    #|vvvvvvvvvvvvvvvvvvvv

# getLogger() below is from logmaster, not the regular logging module
logger = getLogger(appName + '.comm')
    #-We consider ourselves to be within the application's logging domain.

# The below is commented out because it is no longer used.  Instead of a global,
# it is now a data member in the Communicator class.
## ncons = 0   # Private global used to generate unique connection IDs.


#|===================================================================================================
#|
#|      Classes.                                                            [code section]
#|
#|          This module's public and private classes (although none of the latter
#|          exist yet in this module) are defined in this section.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|===================
    #|  Public classes.
    #|vvvvvvvvvvvvvvvvvvv

        #|========================================================================
        #|
        #|   CLASS:  SocketBroken                       [public exception class]
        #|
        #|       A socket we are trying to use for communication is giving
        #|       errors on send or receive attempts, and so the whole thread
        #|       whose job is managing that socket should exit.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class SocketBroken(logmaster.ExitException):  # Reported at INFO level (without a traceback), but causes thread exit.
    defLogger = logger
# End class SocketBroken.

        #|=========================================================================
        #|
        #|   CLASS:  Message                                     [public class]
        #|
        #|       Represents a single incoming (or outgoing) message.
        #|
        #|       Note that a "Message" may or may not correspond to a complete
        #|       command or data object from the application's perspective; it
        #|       is just a low-level entity representing a single bundle of data
        #|       bytes, as might be received (or sent) by a single low-level TCP
        #|       recv()/send() operation.  If the application needs to reassemble
        #|       these messages into a "complete" object of whatever form, that
        #|       job is application-specific, and is entirely up to the user.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Message:               # Represents a single incoming (or outgoing) message.

    #----------------------------------------------------------------------------------
    #   Data members:
    #       .lock   - A reentrant threading lock on fields of this object.
    #	    .dir    - In what direction is this message heading - 'in' or 'out'?
    #       .conn   - What connection this message arrived on (if an incoming message).
    #                   Or, what connection is it being sent to (if an outgoing message).
    #       .data   - The raw data contained in this message, as an array of bytes.
    #       .time   - What time message was received/created (float secs past epoch).
    #       .sent   - For outgoing messages, a flag announcing this message has been sent.
    #       .announced - Has this message been announced to the message handlers yet?
    #-----------------------------------------------------------------------------------

        # Construct a message, given its raw data.
        # (& for received messages: Connection received on, receipt time.)
        # (& for outgoing messages: Connection being sent to, creation time.)
        
    def __init__(self, data, conn=None, curtime=0, dir=DIR_IN):
        
        if curtime == 0:
            curtime = time.time()           # Message creation time is now.

        self.lock = threading.RLock()
        with self.lock:
            self.data = data
            
#        logger.debug("Message.__init__(): Constructing new message object [%s]..." % msg)
            self.conn = conn
            self.time = timestamp.CoarseTimeStamp(curtime);
            self.sent = flag.Flag()
            self.dir = dir
            self.announced = flag.Flag()
            if (conn != None): conn._announce(self)
                #- Announce the existence of this new message to the message handlers for this connection.

    def asStr(self):        # Return the message contents as a string.

        if not hasattr(self, 'data'):
            logger.error("Message.asStr(): Message's data attribute has not been initialized.")
            return ""

        if self.data == None:
            logger.error("Message.asStr(): Message's data attribute is null.")
            return ""
        
        if isinstance(self.data, str):          # If they're already a string,
            return self.data                    # just return them.
        
        if isinstance(self.data, bytes):        # If they're a byte-sequence,
            return self.data.decode()           # decode them first.

    def __str__(self):      # If someone applies the str() function to this message,
        return self.asStr().strip()   # just return the message data as a string, extra chars stripped

    def sendOut(self, conn):          # Send this message out on the given connection.
        logger.debug("Message.sendOut(): Sending this message out on the given connection...")
        conn.sendOut(self)

    def replyWith(self, msg):         # Reply to this message with the given other message.
        logger.debug("Message.replyWith(): Replying to this message with the given other message...")
        self.conn.sendOut(msg)      # Tell our connection to send out that message.

    def replyTo(self, msg):           # Send this message in reply to the given other message.
        logger.debug("Message.replyTo(): Sending this message in reply to the given other message...")
        msg.replyWith(self)         # Tell that message to reply with us.

    def sender_ip(self):            # Return the IP address of the message's sender.  (This used to be a data member before we recoded.)
        if (self.dir == DIR_IN):
            return self.conn.req_hndlr.client_address[0]   # Message's connection's request-handler's client-address's first element. (2nd is port)
        else:
            logger.warn("Message.sender_ip(): IP address requested for outgoing message!  Returning bogus IP 000.000.000.000 instead.\n");
            return "000.000.000.000"

# end class Message

class Connection: pass  # Temporary forward declaration for use by BaseMessageHandler.

        #|==================================================================================
        #|
        #|   CLASS:  BaseMessageHandler                                 [public class]
        #|
        #|       Abstract base class for message handling classes.
        #|
        #|       Users should create their own derived MessageHandler classes
        #|       that derive from this base class, to do what they want with new
        #|       messages (coming in or out).  A typical message handler would
        #|       process the message in an application-specific way, and then
        #|       (for an incoming message) possibly generate one or more
        #|       response messages to be sent back along the same connection.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class BaseMessageHandler:           # Base class for message handling classes.

    defHandlerName = "unnamed"      # The default message-handler name string.

    def __init__(inst, conn:Connection = None, name:str=None):
        inst.conn = conn    # Remember what connection we were created to handle messages on.

        if name == None:                
            name = inst.defHandlerName      # Revert to instance's class's default name.
            
        inst.name = name    # Remember what name we were given on creation, if any.
        
    def handle(inst, msg:Message): pass          # This does nothing.  Subclass needs to override it!



        #|=====================================================================
        #|
        #|  CLASS:     Connection                              [public class]
        #|
        #|       A Connection object represents an active TCP connection
        #|       (i.e. session) between a Communicator server and a client.
        #|
        #|       Connections support asynchronous sends from multiple
        #|       threads, using a thread lock to avoid overlapping data.
        #|       However, for this to work, the user must ensure that a
        #|       message that is not supposed to be interrupted gets
        #|       bundled into a single sendOut() request.  If atomic
        #|       messages need to be very large, we might have to change
        #|       this class to automatically break them up into smaller
        #|       (e.g., 1024-byte) chunks for sending.
        #|
        #|       Currently, Connection is defined as a subclass of Worker.
        #|       The associated thread is responsible for sending outgoing
        #|       messages to the connection.  (Incoming messages are
        #|       handled in the thread that Communicator created for
        #|       handling the connection request.)
        #|
        #|  METHODS:
        #|  --------
        #|      (Inherited Worker methods, plus...)
        #|
        #|      Special methods:
        #|      ----------------
        #|          __init__()          New instance initializer.
        #|
        #|      Public methods:
        #|      ---------------
        #|
        #|          update_component()  Updates the component field of the
        #|                                  sender & receiver thread contexts.
        #|
        #|          addMsgHandler()     Registers a new message handler for
        #|                                  this connection.
        #|
        #|          sendOut()           Sends a given message out through this
        #|                                  connection.
        #|
        #|      Private methods:
        #|      ----------------
        #|
        #|          work_catcherrs()    Target callable for the worker thread
        #|                                  created to send outgoing messages.
        #|                                  Catches SocketBroken exceptions.
        #|
        #|          _announce()         Announce a new incoming or outgoing
        #|                                  message to our message handlers.
        #|
        #|          _send()             Sends a chunk of outgoing data to the
        #|                                  underlying TCP socket.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class  Connection(Worker):      # Represents an active TCP connection (session) to a client.

    #|-----------------------------------------------------------------------------
    #|   Data members:
    #|
    #|       ._wlock         - Reentrant threading lock for access to object data.
    #|       .cid             - Numeric sequence identifier for this connection.
    #|       .comm           - The Communicator server that this connection is
    #|                           connecting to.
    #|       .req            - The underlying request (incoming TCP connection,
    #|                           socket) which established this connection.
    #|       .req_hndlr      - The request handler that is handling this request.
    #|       .thread         - The thread tasked with processing incoming messages
    #|                           on this connection.
    #|       .msgHandlers    - The sequence of message handlers registered on
    #|                           this connection.
    #|       .closed         - Flag for announcing when this connection is closed.
    #|-----------------------------------------------------------------------------

        #|-------------------------------------------------------------------------------------
        #|  Special methods.                                            (of class Connection)
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

            #|---------------------------------------------------------------------------------------
            #|
            #|      Connection.__init__()                               [special instance method]
            #|
            #|          Initializer (constructor) for new instances of class Connection.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def  __init__(self, cid, comm, req, req_hndlr, thread=None, role=None, component=None):
            # \_ Creates a new Connection object in a Communicator, for a request, in a thread.

        logger.debug("Connection.__init__():  Constructing a new Connection object with ID#%d..." % cid)
        self._wlock         = threading.RLock()  # Create a new re-entrant threading lock object to be our write lock.
        with self._wlock:

                # Initialize receiver thread to current thread if not provided by caller.

            if thread==None:
                thread = threading.current_thread()

                # Initialize sender thread's role, if not provided by caller.

            if role==None:
                if comm!=None:
                    role = comm.role + '.con' + str(cid) + '.sndr'
                        # I.e., this is the sender thread for this connection of this communicator.
                else:
                    role = 'con' + str(cid) + '.sndr'
                        # No communicator context, so just say, "connection number so-and-so's sender".

                # Initialize sender thread's component, if not provided by caller.

            if component==None:
                component = 'conn #' + str(cid)
                        # We don't yet know which client we're connected to...
                        # So just set the component to connection number so-and-so.
            
            self.cid            = cid               # Numeric identifier for this connection.
            self.comm           = comm              # The communicator this connection is from.
            self.req            = req               # The request socket (for incoming TCP connection) socket.
            self.req_hndlr      = req_hndlr         # The request handler that is handling this request.
            if self.req_hndlr != None:              # If our request handler is defined,
                self.req_hndlr.conn = self          # Give the request handler a link to this connection.
            self.thread         = thread            # Thread responsible for receiving data on this connection.
            self.msgHandlers    = []                # Set the list of message handlers to the empty list.
            self.closed         = flag.Flag()       # Create the flag for announcing when we're closed.

                # If this connection has a request handler associated with it,
                # and that request handler has an associated iostrm, infer that
                # this connection's input and output streams are both the request
                # handler's iostream.

            if self.req_hndlr and hasattr(self.req_hndlr, 'iostrm'):
                self.in_stream = self.out_stream = self.req_hndlr.iostrm

                # Initialize our underlying Worker entity with the appropriate
                # ThreadActor role & component, and our desired thread target method.

            Worker.__init__(self, start=True, role=role, component=component,                          
                            target = self.work_catcherrs)
                # \_ Do normal worker initialization for this connection.
                #       Goes ahead & starts the writer thread.

            if comm!=None:
                comm._addConn(self)                     # Tell the communicator this connection is now part of it.
                    # - This also announces the new connection to all of the communicator's connection handlers.
    #<------

            #|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #|  End method Connection.__init__().
            #|------------------------------------
    
        #|-------------------------------------------------------------------------------------
        #|  Public methods.                                             (of class Connection)
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

            #|-------------------------------------------------------------------------------------
            #|
            #|      Connection.update_component()                       [public instance method]
            #|
            #|          Call this from within the RECEIVER thread (conn.thread) to
            #|          update the '.component' field of the context info for BOTH
            #|          the sender and receiver threads.  This is useful to allow us
            #|          to make sure the component field of our log records correctly
            #|          reflects which system component this connection is servicing -
            #|          which sometimes cannot be determined except by the receiver
            #|          thread once it first starts receiving data on the connection.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def  update_component(self, comp:str):

#        logger.debug("Connection.update_component(): About to update current component name to [%s]..." % comp)
#        logger.debug("Connection.update_component(): Making sure the logger hasn't hung for some reason!")

        if threading.current_thread() != self:                # Are we in this connection's sender-thread?

#            logger.debug("Connection.update_component(): OK, we're not in the connection's sender-thread...")

            if threading.current_thread() != self.thread:         # No?  OK, then are we at least in this connection's receiver-thread?
                    # No? Then we can't do the job.

#                logger.debug("Connection.update_component(): And we're not in the connection's receiver-thread either!!")

                logger.warn("Connection.update_component():  Updating the connection's component field from threads other than the receiver thread is not allowed.  Ignoring request.")
                    # P.S. The REASON it's not allowed is because a connection's receiver
                    # thread isn't actually a worker thread (since it just sits in a recv()
                    # loop), so there's no way to command it to update its own component
                    # field.  Thus, it must be the thread that initiates the request.

                return

            # OK, we are in the receiver thread.

 #           logger.debug("Connection.update_component(): ...but we are in the connection's receiver thread, apparently...")
 #           logger.debug("Connection.update_component(): Updating this connection's receiver thread's component name to [%s]..." % comp)

            self.thread.component = comp    # Remember this receiver thread is connected with the given component.
            self.thread.update_context()    # This works b/c we installed this method earlier in CommReqHandler.setup().

 #           logger.debug("Connection.update_component(): Testing the new component name (check component field in log)...")
 #           logger.debug("Connection.update_component(): Commanding sender thread to update its component name as well...")

            self.getResult(lambda: self.update_component(comp)) # Tell the sender thread it's receiving from the given component.

 #           logger.debug("Connection.update_component(): Component name for this connection has been updated.")
            return

        # OK, we are in the sender thread.

 #       logger.debug("Connection.update_component(): OK, we're in the connection's sender-thread...")
 #       logger.debug("Connection.update_component(): Updating this connection's sender thread's component name to [%s]..." % comp)

        self.component = comp   # Remember that this sender thread is talking to the given component.
        self.update_context()   # This ThreadActor method updates this thread's (thread-local version of) loggingContext. 

 #       logger.debug("Connection.update_component(): Testing the new component name (check component field in log)...")
    #<--

            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # End method update_component().
            #-------------------------------


            #|---------------------------------------------------------------------------------------
            #|
            #|      Connection.addMsgHandler()                          [public instance method]
            #|
            #|          Adds a given message handler to this connection's list of
            #|          registered message handlers.  The argument should be an
            #|          object that supports the BaseMessageHandler interface.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def  addMsgHandler(self, handler):   # Add a given message handler to our list of registered handlers.
        logger.debug("Connection.addMsgHandler():  Registering a new [" + handler.name + "] message handler...")
        self._wlock.acquire()               # Acquire our write lock.
        self.msgHandlers[0:0] = [handler]   # Insert new handler at head of list.
        self._wlock.release()               # Release our write lock.
    #<--


            #|---------------------------------------------------------------------------------------
            #|
            #|      Connection.sendOut()                                [public instance method]
            #|
            #|          Sends the given message or data out to the remote client over
            #|          the TCP connection that is being managed/represented by this
            #|          Connection object.
            #|
            #|          Makes sure we are in the right thread, packages data into
            #|          a Message object (if not already so encapsulated), announces
            #|          the message to our message handlers, sends the message, and
            #|          raises a "message sent" flag when this is complete.
            #|
            #|          If this method is called from a thread other than this
            #|          connection's sender thread, the send happens asynchronously
            #|          in the background (i.e., the sendOut() call is non-blocking),
            #|          but the caller can always then wait for the msg.sent flag to
            #|          rise if synchronous behavior is desired.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        
    def sendOut(self, msg):         # Send the given message out to client over this connection.

            # First,

        if threading.current_thread() != self:        # If this method is not called from the sender thread itself,
            self(lambda: self.sendOut(msg))     # Put this task on the sender thread's worklist. (But don't wait for send completion.)
            return                              # Return to caller right away.

            # If we make it to here, then we must be in the actual sender thread.
            # Go ahead and start doing the real work.
        
        if not isinstance(msg, Message):    # If the message is in raw (e.g. bytes, string) data form,
            msg = Message(msg, dir=DIR_OUT)                  # Wrap it in a Message object before sending. (Announces also.)
        else:
            msg.dir = DIR_OUT               # This message is outgoing.

            # This 'with' enforces consistency between msg.conn, the act of actually
            # sending the message, and the raising of the msg.sent flag.
            
        with  msg.lock:
            
            msg.conn = self                 # Make a note in the message that we're sending it on this connection.
                # - Note if the same message is broadcast to multiple connections,
                #   the value of msg.conn will change at unpredictable times relative
                #   to other threads, and be left pointing to an unpredictable connection.

            logger.debug("Connection.sendOut():  Announcing outgoing message [%s]..." % msg.data.strip())
            self._announce(msg)             # Announce it, if not already announced.

            logger.debug("Connection.sendOut():  Sending a message out on this connection...")

            self._send(msg.data)     # Send the message data over the connection.
                # - We really should wrap a do/try loop around this, so if the send fails,
                #   that will be handled gracefully.  (E.g., if the send fails, do we really
                #   want to raise the 'sent' flag?)

            msg.sent.rise()     # Announce that this message has been sent (if anyone cares).
    #<------


        #|-------------------------------------------------------------------------------------
        #|  Private methods.                                            (for class Connection)
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

            #|-------------------------------------------------------------------------------------
            #|
            #|      Connection.work_catcherrs()                         [private instance method]
            #|
            #|          Target method for the worker thread created to handle this
            #|          connection, which is responsible for sending data out to the
            #|          connection.  Basically, this just wraps exception handling
            #|          for socket errors around the normal work() method.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def  work_catcherrs(self):    # This is the target method for the new Worker thread created for this connection, responsible for sends.
        logger.debug("Connection.run_catcherrs(): About to do Worker.run() wrapped inside a try/except...")
        try:
            self.work()          # Normal Worker.work() method.  This worker serializes sendOut() requests.
        except SocketBroken:
            logger.warn("Connection.run_catcherrs(): Socket malfunctioned during send; exiting sender thread...")
            return
            # Don't re-raise because we want to just exit relatively quickly.
    #<------

            #|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #|  End method Connection.work_catcherrs().
            #|------------------------------------------


            #|--------------------------------------------------------------------------------------
            #|
            #|      Connection._announce()                              [private instance method]
            #|
            #|          Announces an incoming (or outgoing) message to this connection's
            #|          list of message handlers.
            #|
            #|          (Does LineConnection need to override this to get the debug
            #|          messages right?)
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
    def  _announce(self, msg:Message):      # Announce an incoming (or outgoing) message to our list of message handlers.

        with msg.lock:
            
            already = msg.announced.rise()      # Atomically, was it already announced? & mark it announced.
            if already: return                  # If it was already announced, nothing left to do.
            
            way = 'incoming' if msg.dir == DIR_IN else 'outgoing'
            if isinstance(msg.data, str):
                plain = msg.data
            else:
                plain = msg.data.decode()
                
            logger.debug("Connection._announce():  Announcing %s message [%s] to our message handlers..."
                         % (way, plain.strip()))

            for h in self.msgHandlers[::-1]:    # For each handler in the list (oldest to newest),
                
                logger.debug("Connection._announce():  Announcing %s message [%s] to a [%s] message handler..."
                             % (way, plain.strip(), h.name))

                h.handle(msg)                       # Tell it to handle the message.
                
            logger.debug("Connection._announce():  Finished announcing %s message [%s] to message handlers..."
                         % (way, plain.strip()))

    #<------

            #|---------------------------------------------------------------------------------------
            #|
            #|      Connection._send()                                  [private instance method]
            #|
            #|          Sends a raw chunk of message data to the remote client over
            #|          this connection.  If there is a socket error while sending,
            #|          we raise a flag and throw a SocketBroken() exception.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def _send(self, data):       # Send the given raw data to the client over this connection.
        try:
            self.req.send(data)     # Tell the socket to send the message data.
        except socket.error as e:
            logger.warn()
            self.closed.rise()     # Consider the socket closed.
                # Here, we should probably make sure it is really closed.
            raise SocketBroken("Connection._send(): Socket error [%s] while trying to send to socket... Assuming connection is closed." % e)
    #<------


#<--

#|^^^^^^^^^^^^^^^^^^^^^^^^
#|  End class Connection.
#|------------------------


class Communicator: pass    # Temporary forward declaration for use by BaseConnectionHandler


        #|==============================================================================
        #|
        #|   CLASS:  BaseConnectionHandler                      [public abstract class]
        #|
        #|      Base class from which connection-handling classes should derive.
        #|    
        #|      Users should create their own derived ConnectionHandler classes
        #|      that derive from this base class, to do what they want with new
        #|      connections.  A typical connection handler might register one or
        #|      more application-specific message handlers, and/or may initiate
        #|      other message-producing processes that will insert messages into
        #|      the connection's outgoing message stream as needed.
        #|
        #|  ABSTRACT METHODS:       (Subclasses should implement these.)
        #|
        #|      handle()    Given a connection object, the handler object should
        #|                      do whatever it needs to do with that connection.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class BaseConnectionHandler:    # Base class for connection handling classes.

    # I commented out the below because in the handle() method 
    # we can just do conn.comm to get the communicator.  So we
    # don't really need a direct .comm data member here.

##    def __init__(inst, comm:Communicator):
##        inst.comm = comm    # What Communicator were we created to handle new connections for.

        #|---------------------------------------------------------------------------------------
        #|
        #|  BaseConnectionHandler.handle()                  [abstract public instance method]
        #|
        #|      This is an abstract method, not implemented here.  It is part of the
        #|      generic interface to connection handlers.  Classes derived from
        #|      BaseConnectionHandler should implement this method.  The method
        #|      should accept a newly-created Connection object, then do whatever
        #|      the connection handler wants to do with that connection.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def handle(inst, conn:Connection): pass              # This does nothing.  Subclass needs to override it!
#<--
#  End class BaseConnectionHandler


        #|==========================================================================
        #|
        #|   CLASS:  CommRequestHandler                          [public class]
        #|
        #|       A request handler (in the sense defined by the module
        #|       socketserver) that is specific to the needs of the
        #|       present (communicator) module.
        #|
        #|       This public subclass of the socketserver module's
        #|       BaseRequestHandler class creates a new Connection
        #|       object representing the connection request, gives it
        #|       to all our connection handlers, and then proceeds to
        #|       indefinitely receive and process messages on the new
        #|       connection, calling the message handlers for each.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class CommRequestHandler(socketserver.BaseRequestHandler):

        # Extend BaseRequestHandler's __init__ method to accept extra arg conid.
    def __init__(self, request, client_address, server, conid):
        self.conid = conid
        try:
            socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        except:
                # OK, if the BaseRequestHandler's constructor (which does all the real
                # work of handling the request inside this request-handling thread)
                # exits by throwing an exception, it probably exited straight from
                # .handle() due to a socket error or some such, and therefore the
                # .finish() method (which we need to close the terminal window!)
                # has no chance to get called.  So we call it here.
            self.finish()

        #-------------------------------------------------------------------
        # Method for doing initial setup when the request is first received.
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def setup(self, connClass=Connection):

#-------------------------------------------------------------------------------
# The below is commented out because (1) it doesn't work for some reason; and
# (2) now we are setting the thread's role & component in
# Communicator.process_request() instead.
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
##            # Generate a new unique connection ID number among connections to
##            # this server.  This is for labeling the terminal window for the
##            # connection until we determine what node we're connected to.
##
##        conid = self.server.conNum()    
##        logger.debug("CommRequestHandler.setup(): Setting up to handle a new connection request; connection ID#%d." % conid)
##
##            # Define the role of the new handler thread that we're in,
##            # for logging purposes.  
##
##        thread = threading.current_thread()
##        thread.role = self.server.role + '.con' + str(conid) + ".rcvr"
##            #- This means, the current thread is a connection receiving handler
##            #  for connection #conid for whatever role this communicator is playing.
##        logger.debug("CommRequestHandler.setup(): The role string for this receiver thread is declared to be [%s]." % thread.role)
##
##            # Also define 'component' which defines which system component
##            # is being handled.  (In general, we do not know which component
##            # it is until the connecting entity identifies itself, so we put
##            # 'unknown' for now.  Subclasses may override this.
##        
##        thread.component = 'unknown'
##        logger.debug("CommRequestHandler.setup(): The component string for this receiver thread is declared to be [%s]." % thread.component)
##
##            # Install the .update_context() method from ThreadActor onto this
##            # (non-ThreadActor) receiver thread object.  (Alternatively, we
##            # could have overridden the .process_request method of
##            # socketserver.TCPServer in Communicator to have it create a
##            # ThreadActor from the start, instead of a regular thread.  Would
##            # that have been a cleaner way to do it?)
##            
##        thread.update_context = bind(thread, logmaster.ThreadActor.update_context)
##            # Go ahead and update the current thread's logging context.
##        logger.debug("CommRequestHandler.setup(): Updating the current thread's logging context...")
##        thread.update_context()
        
            # Create the new Connection object representing this connection.
            # This is done using the connClass optional argument so that subclasses
            # of CommRequestHandler can substitute a different connection class
            # for the default class Connection, if desired.  This is done, for
            # example, by LineCommReqHandler.

        logger.debug("CommRequestHandler.setup(): Creating connection of class %s...", connClass.__name__)
        self.conn = connClass(self.conid,                    # Sequence number for this connection.
                              self.server,                  # The Communicator object invoking this handler.
                              self.request,                 # The socket for the request (incoming connection).
                              self,                         # This request-handler object itself.
                              threading.current_thread())   # The new thread for this connection that we are running in.
                #
                #-> This should, as a side effect, add this connection object to the
                #       communicator's list of connection objects, and call all of the
                #       communicator's connection handlers on it.
                #
                #-> Also, even before that, it should make self.conn a link to the
                #       newly created connection object, so that the handle()
                #       method below can access it.
                #
                #-> The 'self.conid' part only works because we extended .__init__()
                #       and Communicator overrode .process_request(),
                #       .process_request_thread(), and .finish_request().  Just to
                #       deliver one teensy extra piece of information about the connection!
                #       It goes to show that socketserver is not really so straightforwardly
                #       extensible.  We might have been better off just writing our own
                #       server classes from scratch rather than extending their classes.
                
    # End CommRequestHandler.setup()        
        
        #----------------------------------------------------------------------
        #   .handle()                               [public instance method]
        #
        #       Method for handling a new request; it indefinitely reads
        #       raw message chunks from the socket and passes them to
        #       message handlers.  We wrap this inside a try/except clause
        #       to make sure that any exceptions will get properly logged.
        #
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def handle(self):
            # We need to catch errors here to make sure we log them properly before the thread exits.
        try:
            # Infinite loop to receive & handle incoming messages on the connection.
            while (True):

                logger.debug("CommRequestHandler.handle(): Waiting for a message on the connection...")

                # Read one message's worth of raw data.

                data = self.request.recv(1024)      # 1024 = our max message length
                    # - It's our customer's responsibility to determine if 1024 bytes
                    #   is all the data there is (or that they want) or not.  If not,
                    #   they can always wait for more.

                thetime = time.time()  # float indicating time message was received

                # Create the Message object out of the raw data.
                # After being created, the message will automatically send itself to all the message handlers for this connection.

                msg = Message(data, self.conn, thetime)

                # Commented out b/c the constructor already does this 
                ## Tell the connection to call all of its message handlers on this new message.
                #
                #conn._announce(msg)

            # It might be a good idea to have code above to exit the while loop and
            # consider the connection closed if no data is received for a while
            # (connection timeout).
        except:
            logger.exception("CommRequestHandler.handle(): recv() loop exited by throwing an exception...")
        

# end class CommRequestHandler


        #|===================================================================================
        #|
        #|       CLASS:  Communicator                                       [public class]
        #|
        #|          A type of threaded TCP server that facilitates multiple
        #|          asynchronous replies and unprompted sends() to any client via
        #|          the return path of any connection to the server initiated by
        #|          the client.  A single incoming connection or message can also
        #|          be handled and processed by multiple handler callbacks
        #|          representing interests of different customers of the service.
        #|          (E.g., one might connect connection statistics, or log a copy
        #|          of the I/O stream to a file.)  However, handler callbacks for
        #|          output requests (as opposed to input requests) are not yet
        #|          supported.
        #|
        #|          NOTE: The superclass socketserver.ThreadingTCPServer, which
        #|          Communicator is currently based on, is a little suboptimal,
        #|          because it busts out of listen() briefly every half-second to
        #|          check for a shutdown request.  It could be shut down more
        #|          quickly (and without wasting CPU cycles polling) if instead
        #|          we had a little client that briefly connected to the server
        #|          just for purposes of waking it up from listen() long enough
        #|          to check for shutdown requests.  Consider overriding the
        #|          BaseServer's .serve_forever() and .shutdown() methods with ones
        #|          that use this approach.  However, in this approach, we have to
        #|          also cleanly handle closing of connections (shutting down all
        #|          the connection handlers), and we haven't addressed that yet -
        #|          so it might be a good idea to tackle that first.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Communicator(socketserver.ThreadingTCPServer):    # TCP server with asynchronous sends.

        #|------------------------------------------------------------------------------------------
        #|  Class variables.                                                    [class section]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

            #----------------------------------------------------------------------------
            #   defaultRole, defaultComp, defaultAddr               [class variables]
            #
            #       These data members specify default initial values for instance
            #       attributes, in case more specific values are not passed as
            #       arguments to the communicator's constructor.
            #
            #       Subclasses of Communicator that are designed for more specific
            #       purposes may wish to override these initial values.
            #
            #           Communicator.defaultRole:
            #
            #               This is used as the basis for the thread role
            #               context information for listener thread and
            #               connection handling threads, which add ".lsnr"
            #               and ".con" to the role names, respectively.
            #
            #           Communicator.defaultComp:
            #
            #               The default system component(s) that the communicator
            #               was created to serve.  Generically, this is "clients".
            #
            #           Communicator.defaultAddr:
            #
            #               Default listen address (IP, port) of class instances.
            #
            #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    defaultRole = 'comms'    # Class variable: The default role of Communicator class instances is for communications.
    defaultComp = 'clients'  # Generally, a Communicator may serve many clients of any generic sort.
        #\_ By default, we don't know which particular type of client the communicator is
        #   designated to connect to.  Subclasses may wish to override this.
        
    defaultAddr = None       # Class variable: Default listen address (IP, port) of class instances.
        # The above class variables can be overridden in subclasses.

        #|------------------------------------------------------------------------------------------
        #|  Instance data members.                                              [class section]
        #|
        #|       .addr           - The address (IP, port) this communicator is listening on.
        #|           (NOTE: We could just use .server_address supplied by BaseServer instead.
        #|
        #|       .role           - String describing the role this communicator in playing in the system.
        #|
        #|       .rqhnd_cls      - Class used to instantiate request handlers for individual requests.
        #|           (NOTE: We could just use .RequestHandlerClass supplied by BaseServer instead.
        #|
        #|       .connHandlers   - List of connection handlers registered to this communicator.
        #|
        #|       .conns          - List of currently active connections.
        #|
        #|       .ncons          - Number of connections that have been made since the server started.
        #|
        #|       .thread         - The main thread handling this communicator.
        #|
        #|       ._wlock         - Multithreading write lock.
        #|------------------------------------------------------------------------------------------

        #|------------------------------------------------------------------------------------------
        #|  Special methods of class Communicator.                                [class section]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __init__(self, myaddr=defaultAddr, role:str=defaultRole, reqhandler_class=CommRequestHandler, comp:str=defaultComp):
        logger.debug("Communicator.__init__(): Initializing new communicator server on address %s:%d." % myaddr)

        self._wlock = threading.RLock()  # Create a new threading lock object to be our write lock.

            # Save certain initializer arguments.  This is needed for annotations in log file.
        self.role      = role                # What purpose was the communicator created for; what role does it play.
        self.component = comp                # What system component is this communicator designated to connect to?
            #\_ These will later get copied to the listener thread, and from there to the connection threads. 

#        self.addr = myaddr              # Remember what address we were assigned to.
            #- NOTE: Not needed.  Base class BaseServer already assigns .server_address to this.
#        self.rqhnd_cls = reqhandler_class   # What is the class of the request handlers that are instantiated to handle connection requests?
            #- NOTE: Not needed.  Base class BaseServer already assigns .RequestHandlerClass to this.
        
        self.connHandlers = []          # Set the list of connection handlers to the empty list.
        self.conns = []                 # Set the list of active connections to the empty list.
        self.ncons = 0                  # We have not received any connections so far.
        socketserver.ThreadingTCPServer.__init__(self, myaddr, reqhandler_class)
                # - Do the rest of the default initialization for any threading TCP server,
                #   but tell the superclass to use our special request handler.

            # Optionally do post-initialization setup.  A subclass's setup() method would
            # typically do registration of connection handlers.
            
        if hasattr(self, 'setup'):      # If we're in a subclass that's defined a setup() method,
            self.setup()                    # then execute it.
    #<--
    # End Communicator.__init__().
    
    
        #|------------------------------------------------------------------------------------------
        #|  Private methods of class Communicator.                                 [class section]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

            #|----------------------------------------------------------------------------------
            #|
            #|      Communicator._announce()                        [private instance method]
            #|
            #|          Announces a given newly-opened Connection to all of this
            #|          Communicator's registered connection handlers.  The most
            #|          recently-registered handler will be notified first.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def _announce(self, conn):      # Call each of the connection handlers on a given connection.
        logger.debug("Communicator._announce(): Announcing new connection to our connection handlers.")

            #|  There seems to be some danger below that a connection handler might
            #|  take a long time or even block, and thereby cause this lock to be
            #|  held indefinitely and possibly cause a deadlock.  Therefore, users
            #|  of Communicator should ensure that all connection handlers finish
            #|  their work quickly.  If they need to do something time-consuming,
            #|  they should spawn or command a separate thread to go do the work
            #|  in the background.  Please see worklist.Worker for a class that is
            #|  ideal for this sort of thing.
            #V
        with self._wlock:
            for h in self.connHandlers[::-1]:   # For each handler in the list of connection handlers (reverse order),
                h.handle(conn)                      # Call the handler's handle() method with the conn.

    #<-- End Communicator._announce().


            #|------------------------------------------------------------------------------------
            #|
            #|      Communicator._addConn()                         [private instance method]
            #|
            #|          Adds a given newly-opened connection to our list of the
            #|          active connections that have been opened to this server.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
                
    def _addConn(self, conn):       # Add a connection to our list of active connections.
        
        logger.debug("Communicator._addConn(): Adding a new connection to our connection list.")
        
        with self._wlock:
            self.conns[0:0] = [conn]    # Insert new connection at head of list.
            
        self._announce(conn)         # Go ahead and call all the handlers on this new connection.
        
    #<-- End Communicator._addConn().

        #|------------------------------------------------------------------------------------------
        #|  Public methods.                                                     [class section]
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

            #|---------------------------------------------------------------------------------
            #|
            #|      Communicator.process_request()                  [public instance method]
            #|
            #|          Overrides ThreadingMixin's .process_request() method, so
            #|          that the newly created thread will be of type ThreadActor,
            #|          needed for our logging facility to work properly.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        
    def process_request(self, request, client_address):
        """Start a new thread to process the request."""
        
        conid = self.conNum()   # Generate a sequence number for this connection.

            # Create the new thread as a ThreadActor in order that we can initialize
            # certain context variables (role and component) which we include in our
            # log record format.
        
        t = logmaster.ThreadActor(role = self.role + ".con%d.rcvr"%conid,
                                  component = "conn #%d"%conid,
                                  target = self.process_request_thread,     # Defined below.
                                  args = (request, client_address, conid)
                                  )
        
        if self.daemon_threads:
            t.daemon = True
            
        t.start()   # Starts the new thread to handle the connection.
        
    #<-- End method Communicator.process_request().

            #|---------------------------------------------------------------------------------
            #|
            #|      Communicator.process_request_thread()           [public instance method]
            #|
            #|          Override ThreadingMixin's .process_request_thread() method.
            #|          We do this to add logging of exceptions, and to pass an extra
            #|          connection-request ID argument through to finish_request, so
            #|          that the newly-created Connection object will know its own ID.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        
    def process_request_thread(self, request, client_address, conid):
        """Same as in BaseServer but as a thread.

        In addition, exception handling is done here.

        """
        try:
            self.finish_request(request, client_address, conid)
            self.close_request(request)
        except:
                # The below used to be just a .debug() level log event.
            logger.exception("Communicator.process_request_thread(): The request handling thread exited by throwing an exception.  Calling error handler & closing the request...")
            self.handle_error(request, client_address)
            self.close_request(request)
    #<-- End method Communicator.process_request_thread().

            #|----------------------------------------------------------------------------------
            #|
            #|      Communicator.finish_request()                   [public instance method]
            #|
            #|          Override BaseServer's .finish_request() method.  This method
            #|          gets called to wrap up the process of accepting a newly-
            #|          received connection request.  It creates a new instance of
            #|          RequestHandlerClass to do the work.  The only reason we have
            #|          to override it is to add an extra argument to it -
            #|          specifically, the unique sequence-number ID associated with
            #|          this particular connection request.  This helps us to
            #|          distinguish connections from each other.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        
    def finish_request(self, request, client_address, conid):
        """Finish one request by instantiating RequestHandlerClass."""
        self.RequestHandlerClass(request, client_address, self, conid)
    #<--

            #|-----------------------------------------------------------------------------------
            #|
            #|      Communicator.conNum()                           [public instance method]
            #|
            #|          Generate & return a new sequential connection request
            #|          identification number.  Increments the sequence counter.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def conNum(self):
        with self._wlock:
            cn = self.ncons
            self.ncons += 1
            return cn
    #<--


            #|-----------------------------------------------------------------------------------
            #|
            #|      Communicator.addConnHandler()                   [public instance method]
            #|
            #|          Adds a new connection handler to our list of registered
            #|          connection handlers.  The new handler is added at the
            #|          front of the list, so that it will be the first one to
            #|          be notified of any newly-created connections.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def addConnHandler(self, handler):        # Register a given connection-handler.
        logger.debug("Communicator.addConnHandler(): Registering a new connection handler.")
        with self._wlock:
            self.connHandlers[0:0] = [handler]  # Insert new handler at head of list.
    #<--


            #|-----------------------------------------------------------------------------------
            #|
            #|      Communicator.listenLoop()                       [public instance method]
            #|
            #|          This method is our target method for the listener thread.
            #|          It just wraps the .serve_forever() method defined by our
            #|          base class within a try/except, to do some logging in the
            #|          event that an exception occurs in the listener thread.
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def listenLoop(this, *args, **kwargs):
        try:
            this.serve_forever(*args, **kwargs)
        except:
            logger.exception("Communicator.listenLoop(): this.serve_forever() exited by throwing an exception.  The listener thread will die now.")
    #<--


            #|-----------------------------------------------------------------------------------
            #|
            #|      Communicator.startListening()                   [public instance method]
            #|
            #|          Tells the Communicator object to go ahead and create its
            #|          listener thread, and have that new thread start listening
            #|          for connection requests to arrive at our port.  (This
            #|          effectively starts the Communicator server running.)
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
            
    def startListening(self):           # Create a new thread & start listening.
        logger.debug("Communicator.startListening(): Creating & starting a listener thread.")

            # Create the new Thread object (actually a ThreadActor, for extra logging features).
            
        self.thread = logmaster.ThreadActor(role = self.role + ".lsnr",     # This means, listener thread for whatever role the Communicator is for.
                                            component = self.component,     # Listener thread serves same component as overall Communicator.
                                            target = self.listenLoop)       # Use our own top-level listener thread method that catches exceptions.
        
#        self.thread.setDaemon(True)     # If daemon, then process can return but leave server thread alive in bg.
        self.thread.start()             # Start the listener thread.
    #<--


            #|----------------------------------------------------------------------------------
            #|
            #|      Communicator.sendAll()                          [public instance method]
            #|
            #|          Broadcasts the given message out to ALL of this communicator's
            #|          client connections.  (This is useful for, for example, telling
            #|          all nodes to shut down via the MainServer communicator.)
            #|
            #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        
    def sendAll(self, msg):         # Send a given message to all of our client connections.

        logger.debug("Communicator.sendAll(): Sending message [%s] to all active connections." % msg)

            # | Since sendOut does its work in the background in a separate
            # | thread dedicated to each connection, this loop should reliably
            # | terminate quickly, so there is no danger of blocking while
            # | holding this lock and getting into a deadlock situation.
            # V
        with self._wlock:
            for c in self.conns[::-1]:      # For each connection in our list (reverse order),
                logger.debug("Communicator.sendAll(): Sending message [%s] to a connection." % msg)
                c.sendOut(msg)                  # send the message out on that connection.
    #<--
    #   End method Communicator.sendAll().
                
#<--
#   End class Communicator.


        #|====================================================================
        #|
        #|      CLASS:  LineConnection                      [public class]
        #|
        #|          This subclass of Connection differs only in how
        #|          it handles sends to the connection.  It treats
        #|          message data as text, and sends it via the request
        #|          object's I/O stream wrapper.  This is set up 
        #|          by class LineCommReqHandler, below.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class  LineConnection(Connection):

        #|--------------------------------------------------------------------
        #|
        #|      LineConnection._send()              [public instance method]
        #|
        #|          Overrides the method of the same name in our
        #|          parent class, Connection.
        #|
        #|          This method is used by Connection.sendOut() to
        #|          do the low-level sending of actual data via the
        #|          connection.
        #|
        #|          It differs from the parent's method in that it
        #|          assumes the given data is a string (not a byte
        #|          array) and that the request handler has set up
        #|          a text I/O stream for the connection.
        #|
        #|          It should not be called by anyone other than by
        #|          .sendOut(), and it should only be called from
        #|          within the connection's associated sender worker
        #|          thread.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def _send(self, data:str):

            # If string doesn't end with a line-end character, then add one.
        
        if data[-1] not in ('\r', '\n'): data += '\n'

            # Write the string to the line-buffered text I/O output stream
            # maintained by the connection's request handler (which is a
            # LineCommReqHandler, below).
        try:
            self.out_stream.write(data)
            
        except socket.error as e:
            self.closed.rise()     # Consider the socket closed.
                # Here, we should probably make sure it is really closed.
            raise SocketBroken("LineConnection._send(): Socket error [%s] while trying to write to socket stream... Assuming connection is closed." % e)

        except Exception as e:
            self.closed.rise()      # Consider the connection closed.
                # \_ It might be better to have separate closed flags
                #       for input vs. output.
            logger.error("LineConnection._send(): Exception [%e] while trying to write to output stream... Assuming connection is closed." % e)
            raise e
        
    #__/ End LineConnection.send().

#__/ End class LineConnection.


        #|========================================================================================
        #|
        #|      CLASS:  StreamLineConnection                            [public class]
        #|
        #|          This subclass of LineConnection provides a LineConnection-
        #|          like interface to an arbitrary pair of I/O streams which do
        #|          not necessarily have a TCP socket underlying them.  Instead,
        #|          we assume that the .readline() method on the input stream
        #|          and the .write() method on the output stream will throw an
        #|          exception if an unrecoverable I/O error occurs (such as if
        #|          the stream, whatever its source, is forcibly closed).  In
        #|          such an event, we supply our customers with an exception of
        #|          class StreamConnectionBroken.
        #|
        #|      PUBLIC METHODS:
        #|
        #|          
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class  StreamLineConnection(LineConnection):

    #|-----------------------------------------------------------------------------
    #|  Private nested classes.
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|-------------------------------------------------------------------------
        #|
        #|      CLASS: _StreamReader                        [private nested class]
        #|
        #|          A _StreamReader is a thread whose sole purpose in life
        #|          is to read lines of text, one at a time, from a
        #|          StreamLineConnection's input stream, and turn them into
        #|          Message objects, which are then announced to all of the
        #|          connection's registered message handlers.
        #|
        #|          Each StreamLineConnection creates and brings to life a
        #|          new _StreamReader to handle that connection as soon as
        #|          the connection object is created.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    class _StreamReader(ThreadActor):

            # Class variables.

        defaultRole = 'strmRdr'     # Our default role designation abbreviates "stream reader."
        defaultComponent = 'strm'   # Our default role designation is some generic "stream."

            # Instance variables.

        strcon = None               # The StreamLineConnection that this _StreamReader is working for.

            # Special methods.

        def __init__(self, *args, strcon=None, **kwargs):

            if strcon != None:          # If the strcon argument was provided,
                self.strcon = strcon    #   initialze our instance attribute with it.
            
            ThreadActor.__init__(self, *args, **kwargs)     # General ThreadActor initialization.
        #<--
    
            # Public methods.

        def readLines(self):        # Main loop of the _StreamReader thread.  Read & process lines.

            logger.debug("StreamLineConnection._StreamReader.readLines(): Starting line-input loop.")

            while True:

                    # Our strategy here is simply: Use readline() to read the line,
                    # then package it up into a message.  The newly-created message
                    # then automatically announces itself to our customers who have
                    # registered themselves with us using Connection.addMsgHandler().
                
                strcon = self.strcon        # Get this instance's StreamLineConnection object.
                in_str = strcon.in_stream   # Get the StreamLineConnection's input stream.
                line   = in_str.readline()  # Read the next line from the input stream.
                now    = time.time()        # Floating-point time in secs since the epoch.

                logger.debug("Got line [%s] from input at %s." % (repr(line), repr(now)))
                             
                    # Create the Message object representing the incoming line of text.
                    # We set its connection and time fields appropriately.  The direction
                    # defaults to DIR_IN, which is correct.

                msg    = Message(line, conn=strcon, curtime=now)
            #__/ End while.
        #__/ End method readLines().

            # Final class variables.
            # These go last b/c they depend on the above method definitions.

        defaultTarget = readLines   # Set this thread's default target to be our readLines() method.
        
    #__/ End class _StreamReader.

    #|-----------------------------------------------------------------------------
    #|
    #|  Private instance data members.
    #|
    #|      streamReader:_StreamReader   - Worker thread to read lines from
    #|                                      our input stream and process them.
    #|
    #|      in_stream, out_stream        - Streams for input & output.
    #|
    #|-----------------------------------------------------------------------------

        # Special methods.

    def __init__(self, cid, *args, instr=None, outstr=None, **kwargs):

            # Initialize our attributes for the input & output streams from the arguments.

        self.in_stream  = instr
        self.out_stream = outstr

            # Create our _StreamReader thread that will handle input to this connection.
            # We'll start it running in a moment.

        self.streamReader = self._StreamReader(strcon=self)

            # Invoke the initializer for our parent class.  Some notes:
            #   - The connection ID comes from our own initializer.
            #   - The communicator, request, and request-handler objects are all None,
            #       because this connection has nothing to do with TCP requests.
            #   - The receiver thread is set to our newly-created stream reader.

        LineConnection.__init__(self, cid, *args, comm=None, req=None, req_hndlr=None,
                                     thread=self.streamReader, **kwargs)

            # Start up the _StreamReader we created earlier.  We do this last to make
            # sure we are fully initialized before it starts, in case it might access
            # this structure.

        self.streamReader.start()

        
    #__/ End method StreamLineConnection.__init__().

#<--- End class StreamLineConnection.


        #|================================================================================
        #|
        #|      CLASS:  LineCommReqHandler                              [public class]
        #|
        #|          RequestHandler subclass to be used by the LineCommunicator
        #|          subclass of Communicator, below.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class LineCommReqHandler(socketserver.StreamRequestHandler, CommRequestHandler):

        #-------------------------------------------------------------------------
        #   setup()                                     [public instance method]
        #
        #       This method builds upon the setup() methods of both parent
        #       classes, StreamRequestHandler and CommRequestHandler.
        #
        #       This method is called by the BaseRequestHandler constructor
        #       immediately after the handler is first instantiated in
        #       socketserver.BaseServer.finish_request(), which is the first
        #       thing done in the new thread for handling the connection that
        #       is created by socketserver.ThreadingMixIn.process_request().
        #
        #       The job of this method is to do preliminary setup of the
        #       connection prior to the actual receive loop, which is done
        #       in the separate handle() method.
        #
        #       In the case of the LineCommReqHandler, setup() creates a
        #       bidirectional line-buffered text I/O stream built on top of
        #       the raw socket, assigns the role for the connection handler
        #       thread, and announces the existence of the new connection to
        #       the server's registered connection handlers.
        #
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def setup(self):


            # I'm not sure if the below line is really needed, so I have
            # commented it out for now, since that should improve performance.
            # However, if the server does not respond immediately to short
            # commands that are sent to it, it could be because some input
            # buffer isn't full yet, and input processing is being postponed
            # until it is.  If this happens, we might fix it by uncommenting
            # this line again.  [Update: I'm pretty sure, after reading the
            # docs for io.BufferedReader and io.TextIOBase, that allowing
            # the input stream to be buffered shouldn't cause any delays.]
            # [Update 10/1/09: This appears to be needed after all!]

        self.rbufsize = 0   # Tells StreamRequestHandler to set up the input
            # binary stream in unbuffered mode (to guarantee that we'll respond
            # to lines as soon as they're sent).

#        logger.debug("LineCommReqHandler.setup(): Doing StreamRequestHandler setup...")
            
        socketserver.StreamRequestHandler.setup(self)    # This creates (unbuf
            # fered) binary input and output streams called .rfile and .wfile.

#        logger.debug("LineCommReqHandler.setup(): Creating R/W pair of buffered io streams...")

        self.iofile = io.BufferedRWPair(self.rfile, self.wfile)     # This puts
            # together .rfile and .wfile into a single bidirectional binary stream.

#        logger.debug("LineCommReqHandler.setup(): Creating line-buffered text I/O wrapper...")
        
        self.iostrm = io.TextIOWrapper(self.iofile, newline=None, line_buffering = True)  # This
            # embeds the bidirectional binary stream into a text stream that talks
            # in strings rather than bytes, and automatically flushes the output
            # whenever a newline is output.  ('newline=None' activates universal newline
            # mode where \r and \r\n are translated to \n.)

#        logger.debug("LineCommReqHandler.setup(): Doing CommRequestHandler setup...")
            
        CommRequestHandler.setup(self, connClass=LineConnection)  # This should
            # assign the thread role and create the Connection object via the
            # constructor for the given connection class, which will announce
            # itself to the communicator's connection handlers.
    
    #<-- End method LineCommReqHandler.setup()
    

        #---------------------------------------------------------------------------
        #   handle()                                    [public instance method]
        #
        #       Method for receiving and processing connection data.
        #       It is called by the constructor right after setup().
        #
        #       In this class, instead of reading raw recv() byte-sequence
        #       messages from the socket, and packaging them into Message
        #       objects, instead we read lines of ASCII text from the
        #       higher-level line-buffered text I/O stream created in the
        #       setup method above, and package the lines into Message
        #       objects.
        #
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def handle(self):
        try:

                # Infinite loop to receive & handle incoming messages on the connection.

            logger.debug("LineCommReqHandler.handle(): About to enter reader loop...")

            while (True):

#                logger.debug("LineCommReqHandler.handle(): Waiting for a message on the connection...")

                try:
                        # OK, there is a minor problem with the stmt below.  What if the line
                        # is complete as far as it goes, but is not yet terminated by a
                        # newline character?  This might happen, for example, when printing
                        # a prompt for user input (such as "OK> "), but it could also happen
                        # more generally.  We would like to handle that situation gracefully,
                        # by, say, timing out after some interval and treating the data as
                        # complete for purposes of displaying it (while also still allowing
                        # for the possibility that more text on the same line may yet arrive).
                        # However, this will probably require breaking the abstraction barrier
                        # provided by line oriented iostrm input.  What to do.  One possibility
                        # is to simply not use LineCommunicator for data sources for which this
                        # scenario might happen.
                        
                    data = self.iostrm.readline()   # Read one line's worth of text data.
                    
                except socket.error as e:
                    logger.warn("LineCommReqHandler.handle(): Socket error [%s] during readline()... "
                                "Assuming connection is closed & returning." % e)
                    break  # Break out of infinite readline loop
#                    return
#                    raise SocketBroken("LineCommReqHandler.handle(): Socket error [%s] while trying to read from socket stream... Assuming connection is closed." % e)

                except Exception as e:      # Skip lines causing other exceptions (non-ascii characters, etc.)
                    logger.warn("LineCommReqHandler.handle(): Exception [%s] during readline()..."
                                "Ignoring it and continuing..." % e);
                    continue;

                if data == "":      # Empty string indicates EOF; i.e., the socket has been closed.
                    logger.info("LineCommReqHandler.handle(): Remote client closed the connection.")
                    break               # Non-exceptional exit from readline loop.

                thetime = time.time()  # float indicating time message was received

#                logger.debug("LineCommReqHandler.handle(): Received text line: [%s]."
#                             % data.strip())

                    # Create the Message object out of the line of text.

                msg = Message(data, self.conn, thetime)
                        #\_ Upon being created, the message will automatically send
                        #   itself to all the message handlers for this connection.
        except:
            logger.exception("LineCommReqHandler.handle(): readline() loop exited by throwing an exception...")

            # Stuff to always do on our way out of the connection request handler.  
        finally:
            logger.debug("LineCommReqHandler.handle(): Considering this connection closed & stopping sender thread.")
            self.conn.closed.rise()     # Consider the socket closed.
                # Here, we should probably make sure it is really closed.
            self.conn.stop()            # Ask the sender worker thread to exit.

    #<-- End method LineCommReqHandler.handle()
    

        #|=======================================================================================
        #|
        #|      CLASS: LineCommunicator                                        [public class]
        #|
        #|          A text-based, line-oriented version of the Communicator interface.
        #|
        #|          The difference between the regular Communicator and the
        #|          LineCommunicator is that in a LineCommunicator, all message sends
        #|          and receives are done in terms of ASCII strings and line-sized
        #|          chunks, rather than raw binary data chunks of some other size.
        #|
        #|          LineCommunicator is implemented as a subclass of Communicator that
        #|          uses a new RequestHandler class called LineCommReqHandler that is a
        #|          subclass of both StreamRequestHandler and CommRequestHandler to
        #|          handle each connection request; this subclass extends the setup()
        #|          methods of both StreamRequestHandler as well as CommRequestHandler
        #|          to create an io.TextIOWrapper around the rfile/wfile byte streams
        #|          created by StreamRequestHandler, and overrides the handle() method
        #|          of CommRequestHandler() so that instead of reading and handling raw
        #|          message chunks from the socket, it reads and handles line-sized
        #|          strings using .readline() on the text stream.  Further, Connection
        #|          is replaced with a subclass LineConnection that sends message
        #|          strings using the I/O stream interface.
        #|
        #|          As for the classes ConnectionHandler, Message, and MessageHandler,
        #|          those classes remain essentially unchanged in this context, except
        #|          that the ".data" field in the message is decoded into the form of
        #|          a text string (instead of being a byte sequence), and each message
        #|          contains a text line instead of a raw recv() call result chunk.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class LineCommunicator(Communicator):

        # Class variables.

    defaultRole = 'lncom'   # Default role designator string for LineCommunicator threads.

        # Special methods.
    
    def __init__(self, myaddr, role:str=defaultRole,
                 reqhandler_class=LineCommReqHandler,
                 comp:str=None):    # Component designator string for LineCommunicator threads.
                        #   \_ To override w. default if absent.

            # Use default component designator string if not provided.
        
        if comp==None:
            comp = self.defaultComp     # This gets its value from Communicator superclass.
            
        logger.debug("Initializing LineCommunicator for role %s, component %s..." % (role,comp))
        
        Communicator.__init__(self, myaddr, role, reqhandler_class, comp)
            # -This just does the default initialization for our Communicator parent class.
        
    #<-- End method LineCommunicator.__init__().
        
#<-- End class LineCommunicator.


    #|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #|  End of class declarations code section.
    #|======================================================================


    #|======================================================================
    #|
    #|      Main module body.                               [code section]
    #|
    #|          Main executable body of this module.  Just warns the 
    #|          user that this module is not intended to be executed 
    #|          as a standalone script.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

if __name__ == '__main__':
    print("This module is not meant to be run as a standalone script.")
    print("Exiting in 10 seconds...")
# Not needed b/c already done in header.
##    import time   
    time.sleep(10)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# End of file communicator.py.
#****************************************************************************************************
