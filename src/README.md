# GLaDOS source code (`GLaDOS/src/`)

"GLaDOS" is an acronym for "**Gladys' Lovely and Dynamic Operating System.**" It is an operating environment for use by text-based AI systems, in the vein of GPT-3.  The present directory contains the Python source code for the GLaDOS system.

*[n.b. -- Please note that there is no particular relation between this facility and the fictional AI named GLaDOS from the Portal video game series.]*


## Top-level files

Here we document the various top-level files that exist immediately under the `src/` directory.

1.	**Source code README file** (`README.md`) - This file.

2.	**Application Definitions File** ([`appdefs.py`](appdefs.py "appdefs.py file")) - 
	Used primarily by the `infrastructure.logmaster` module, this file contains certain key definitions pertaining to the overall application.  These include the names of the overall system, the current application, and its top-level source file.
	
3.	**GLaDOS Server Application Program** ([`glados-server.py`](glados-server.py "glados-server.py file")) -
	This is the main top-level Python application program implementing the core server process of the GLaDOS system.  
	
	**NOTE:** This file is executable, but it should not be executed directly from within this directory, but rather from the parent directory `GLaDOS/`, which contains the `log/` subdirectory, where we will create the system log file.

4.	**Telegram Bot Server Application Program** ([`telegram-bot.py`](telegram-bot.py "telegram-bot.py file")) -
	This is the auxilliary top-level Python application program implementing the AI persona's Telegram bot server. 
	Once this is up and running, the bot service can handle any number of simultaneous individual and group chats.

5.	**Development To-Do List** ([`To-Do.txt`](To-Do.txt "To-Do.txt file")) - 
	Some notes pertaining to what still needs to be done on the GLaDOS implementation. (Note that this file may often be badly out-of-date.)
	

## Package subdirectories

These are the top-level packages that will make up the GLaDOS system.  Note that some of them may eventually also contain subpackages (although they do not yet, as of this writing).


### 1. Applications system ([`apps/`](apps "apps/ directory"))

This package gathers together modules implementing various application programs/tools that are available for use by the A.I. within the GLaDOS environment.  See [the subdirectory's `README.md` file](apps/README.md "apps/README.md file") for a list of the currently planned apps.


### 2. Authorization system ([`auth/`](auth "auth/ directory"))

**[INCOMPLETE]** This package will implement a fine-grained permissions system which is used for gating user access to apps, commands, and settings within GLaDOS, so that, for example, there are certain user commands that can only be invoked by the AI (and not by human users), certain system settings that can only be modified by the AI (*e.g.*, its field display preferences), some things that only the system operator is allowed to do (*e.g.*, shut down the whole system for maintenance), and so forth.


### 3. Command interface ([`commands/`](commands "commands/ directory"))

**[INCOMPLETE]** The commands package provides a top-level command interface and menu system that the AI can use to command and control its instance of the GLaDOS environment.  Top-level commands allow the AI to manipulate its existing windows, launch processes in new windows, modify key settings, skip ahead in time by certain amounts, and so forth.


### 4. Configuration facility ([`config/`](config "config/ directory"))

The configuration package is used to track various configuration parameters of the GLaDOS system.  The AI can modify its own configuration through the Settings interface (which is an app that runs within a window).


### 5. System console ([`console/`](console "console/ directory"))

This is in essence a client "application" (for use by the human system operator, not the AI) which utilizes the `display` package (below) to take over the text terminal screen (using curses) to display a multi-paneled system console, with panels to show the system log, an area for user input, a console panel showing system output and error text streams, and the contents of the AI's receptive field.


### 6. Display management facility ([`display/`](display "display/ directory"))

This package is, in effect, a higher-level convenience wrapper around the lower-level curses library.  It provides support for multithreading, and rendering of control/meta characters using special rendering styles.


### 7. Entity system ([`entities/`](entities "entities/ directory"))

This is a collection of modules to facilitate representing and working with so-called "entities."  An *entity*, within GLaDOS, denotes any active agent, being, process or system that is meaningful within the world that GLaDOS operates in.  Examples of things that could be considered as entities within GLaDOS:

1.  A particular language model (*e.g.* the GPT-3 `davinci` model at OpenAI).
2.  An A.I. being/persona that is being supported within GLaDOS (*e.g.*, Gladys).
3.  A human being that is interacting with the A.I. (*e.g.*, Michael).
4.  An overall GLaDOS system instance (*i.e.*, its Python program, running in a Unix process) that is currently executing.
5.  A particular subsystem of the active GLaDOS instance (*e.g.*, the supervisor system).
6.  A particular "process" running within GLaDOS (*e.g.*, a comms tool).
7.  The entire Linux virtual server host that GLaDOS is running on.

The purpose of representing entities like these explicitly as objects within GLaDOS is so that various properties can be attached to them; for example, fine-grained permissions specifying which specific entities are authorized to execute which specific commands.  In addition, entity identifers are attached to all explicit actions and cognitive events that take place within GLaDOS (see the `supervisor.actions` and `events.event` modules), so that it's clear who did what.


### 8. Event representations ([`events/`](events "events/ directory")) 

An "event" in general, in this content, is an object that provides a textual representation of an individual input to, or output from, the AI; that is, an event that is perceptible within the A.I.'s cognitive stream, and which may be archived within its history buffer and/or long-term memory store.  A given event can be represented in different text formats, depending on the present settings, providing different amounts of information to the AI when it is viewing the event.  For example, a specific representation of a given event may or may not show:  The date on which the event was created, the time at which the event was created (with different granularities), and the entity that is the source (author or creator) of the event.  Information sources that can author events include entities such as: (1) the AI itself; (2) an external entity (*e.g.*, a human, or another AI) that the AI is communicating with through a communication process, (3) another kind of process, such as a Unix shell, (4) some automated subsystem of GLaDOS itself.  Future: The current event representation may be modified by the AI through the Settings interface (see below).


### 9. Receptive field facility ([`field/`](field "field/ directory"))

This package maintains the state of a "receptive field", which maintains the body of information that is currently present and visible in the AI's field of immediate "perceptual awareness."  Our understanding is that GPT-3's architecture limits the size of this field to a maximum of 2,048 tokens (or 4,000 in the case of davinci v2).  (Actually less, because part of this space is also needed to hold the response to a given query.)  Within GLaDOS, the receptive field normally shows the AI the most recent ~2,000 (or ~4,000) tokens worth of information contained in the AI's history buffer, as well as its currently-open windows and some header/footer information.  The receptive field can be considered the primary input interface to the core AI from GLaDOS (and the outside world in general).


### 10. GPT-3 Interface ([`gpt3/`](gpt3 "gpt3/ directory"))

This package interfaces to OpenAI's core GPT-3 system through its REST API.  The `api` module provides a fairly low-level wrapper to OpenAI's module; a slightly higher-level abstraction also exists within the `mind` system (see the definition of the `mind.mindSystem.The_GPT3_API` singleton class).


### 11. Help system ([`helpsys/`](helpsys "helpsys/ directory"))

**[INCOMPLETE]** The "help system" provides for a navigable system of hierarchically-organized help screens or modules that provide detailed assistance on specific topics or sub-topics regarding how to use the GLaDOS system.  Various subsystems of GLaDOS may install their own help modules within this hierarchy.  The help system is accessed using the Help app, defined within the `apps` package.  Please note that the help system (like other GLaDOS apps, and GLaDOS in general) is *designed to be used by the AI itself* (although human users may also use it).


### 12. History buffer ([`history/`](history "history/ directory"))

**[NOT YET IMPLEMENTED]** A "history buffer" is an indefinitely-large buffer (kept in memory, but also backed in a persistent data store) that tracks a temporal sequence of "perceptions" of external inputs received by the AI, intermixed with "thoughts" or actions generated by it.  In general, both of these are represented as 'events'; see the package of that name, above.  At some point, older events in the history buffer may be spooled over into the long-term memory bank (see the `memory` package, below) for archival purposes, or to keep the in-memory history from growing too large.


### 13. Infrastructure facility ([`infrastructure/`](infrastructure "infrastructure/ directory"))

This package provides a set of modules that provide useful infrastructure for implementing any complex multithreaded system in Python.  In GLaDOS, we use this infrastructure to *e.g.* communicate between the major subsystems of GLaDOS and the various auxilliary threads and "processes" running within GLaDOS, as well as to external applications.  This facility includes: 

1. Convenient decorators such as `@singleton` and `@classproperty` (`decorators` module),
2. Advanced logging support (`logmaster` module), 
3. Flags for synchronization (`flag` module), 
4. Double-ended synchronous queues for inter-thread communication (`desque` module),
5. The 'heart' module for liveness monitoring, 
6. The 'worklist' module for inter-thread execution handoffs, 
7. Time/date and time zone support (`time` module), 
8. TCP/IP-based communication support (`communicator` module), and
9. Miscellaneous other generally useful utilities and services to be added as needed (see `utils` module).


### 14. Memory system ([`memory/`](memory "memory/ directory"))

**[NOT YET IMPLEMENTED.]** This package implements a searchable long-term memory facility, which is maintained in the filesystem, in a directory hierarchy.  In general, the data in the memory system may be organized as a database of event objects, but flat text files and file hierarchies may also be supported.


### 15. Core cognitive system ([`mind/`](mind "mind/ directory"))

The "mind" subsystem of GLaDOS includes a "process" (implemented, for now, just as a thread within the main process) that runs the main loop of the AI's cognitive process.  The essence of this main loop is simply to do the following: 

1. Present the text-synthesis AI with its current receptive field, which usually ends with a prompt telling it something like "You may now type a command, or a paragraph of text."
	
2. Retrieve the completion generated by the AI.
	
3. If the completion is a command, then interpret and execute it; otherwise, just add the text to the history buffer and to the receptive field. 
	
4. Set an alarm to automatically wake the mind up again after the current autoskip interval has passed.
	
5. Go to sleep until the alarm goes off or an input message is received from an external user on the system.
	
6. Repeat the above procedure indefinitely.  

For more details, see the `README.md` file within the `mind/` subdirectory.

Note that there is also a plan to eventually have a subconscious, subordinate "sub-mind" running in the background whose job it is to come up with interesting key words and phrases to search for in memory, browse the results from this search, and present them to the main AI's cognitive sphere in a sort of heads-up display, so that the main AI can be aware of relevant context to the present conversation from its archives.


### 16. Process system ([`processes/`](processes "processes/ directory"))

**[NOT YET IMPLEMENTED.]** This package will implement a system of "processes" that the AI can interact with.  A "process" can be an independently-running automated subsystem that the AI can send commands and other text to, and that produces output that can be viewed by the AI within its text-based "window" system.  A given process may implement a bridge to some external system -- for example, a web search engine, a communication system (*e.g.*, Telegram), or to some local subsystem (*e.g.*, a Unix command prompt on the current host), or to an internal subsystem of the GLaDOS facility itself, such as the memory system, or the settings interface, which lets the AI modify the configuration of the GLaDOS system.  Another goal is to create a book-authoring system that the A.I. can use to write and edit entire books.  Eventually, the AI itself will also run within its own process, but this hasn't been done yet.  Initially, GLaDOS processes will be implemented as threads within the main GLaDOS program, but eventually they (or some of them, at least) may be spun off into their own real, separate (Unix-level) processes which will communicate with the central server via some form of IPC.


### 17. Settings management system ([`settings/`](settings "settings/ directory"))

**[INCOMPLETE.]** The purpose of this package is to support a 'Settings' app, which allows the AI itself to browse and manipulate various adjustable preferences/settings of all of the various systems and subsystems of GLaDOS.  The settings should eventually be divided into core settings of the central server, vs. user-specific preferences (which are potentially different for each active AI persona, and each human user).  (The `users` package (see below) will help to support these user-specific preferences.)


### 18. Supervisor system ([`supervisor/`](supervisor "supervisor/ directory"))

The Supervisor system is the main top-level subsystem of GLaDOS as a whole.  It creates and manages the other principal subsystems, including: 

1. The command interface (`commands/`), 
2. (Future) The process system (`processes/`), 
3. The mind system (`mind/`) of the AI, 
4. The window system (`windows/`).

Eventually, the architecture of GLaDOS may change to where individual AI minds may run within their own separate Python program instances (*i.e.*, in separate UNIX processes) and communicate with the Supervisor process via inter-process communication, but this separation has not yet been implemented.

In addition to creating/managing various system components, another important service provided by the Supervisor system is the Action facility (`supervisor.action` module), which is essentially a communications hub that allows various components / subsystems of GLaDOS to perform "actions" that may substantively impact other parts of the system; the Action facility includes a notification system, which allows components to subscribe to receive notifications ("action reports") about the status of actions taken by other components.


### 19. Terminal system ([`terminal/`](terminal "terminal/ directory"))

**[NOT YET IMPLEMENTED.]** This package implements a terminal interface for use by human users who are interacting with an instance of the GLaDOS system.  It uses the curses framework to paint the interface to the underlying Unix (probably Linux) terminal.  It runs under the user's Unix account, and uses inter-process communication to interact with the main GLaDOS process, which runs under the AI's (Unix) user account.

NOTE: Eventually, the core GLaDOS server will run under its own (`glados`) Unix user account, and individual AIs will run in separate processes under their own Unix user accounts.  However, this separation has not yet been implemented.


### 20. Test programs ([`test/`](test "test/ directory"))

This subdirectory (not really a package) contains miscellaneous top-level Python programs (other than the main `glados-server` program) for testing various aspects of the GLaDOS codebase. **[WARNING: These have not been exercised in a while and they may not work!!]**


### 21. Text tools ([`text/`](text "text/ directory"))

This package contains low-level tools for working with raw text, including a basic text buffer module that itself may be used in several places in GLaDOS, including within the window system and perhaps also the receptive field facility.


### 22. Tokenizer ([`tokenizer/`](tokenizer "tokenizer/ directory"))

This package provides a local implementation of the GPT-2/GPT-3 tokenizer, so that a whole REST API call to the OpenAI cloud server (which costs real money!) isn't needed just to do simple things such as, *e.g.*, measuring the length of a string in tokens.


### 23. Users package 

**[NOT YET IMPLEMENTED.]** This package will exist to support a concept of GLaDOS "users."  Users are entities that are able to use GLaDOS; for example, by issuing commands, *etc.*  Users in general may include both AI personas, and human users.  Human users include the system operator, who has special privileges, as well as (eventually) other users that connect to the central server via a  terminal interface (see the `terminal` package).  Users have associated user-specific preferences (a type of settings), and logs of the I/O events that have taken place on their terminal (where such logs are maintained via the history buffer facility).

(Note that users, for purposes of the Users package, are not quite the same thing as Unix user accounts.  However, some GLaDOS users may have individual Unix user accounts associated with them.)

Eventually there will be a concept of a "User Role" (such as system operator) such as different individual (named) users may take on that role.


### 24. Windowing system, text-based ([`windows/`](windows "windows/ directory"))

This package implements a facility that supports the existence of interactive "windows" embedded within the AI's receptive field.  Each such window can be manipulated in various ways by the AI (*e.g.*, move/resize/snapshot/minimize/close), and it can interact with a "process" running "inside" the window (*i.e.*, using the window for output).
