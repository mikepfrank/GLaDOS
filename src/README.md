# GLaDOS source code (`GLaDOS/src/`)

"GLaDOS" is an acronym for the "**General Lifeform's automated Domicile Operating System.**" 
It is an operating environment for text-based AI systems.  The present directory 
contains the Python source code for the GLaDOS system.  *[n.b.--Please note that there is no relation between this facility and the fictional AI named GLaDOS from the Portal video game series.]*

## Top-level files

Here we document the various top-level files that exist immediately under 
the `src/` directory.

1.	**Source code README file** (`README.md`) - This file.

2.	**GLaDOS Server Application Program** 
	([`glados-server.py`](glados-server.py "glados-server.py file")) - This is 
	the main top-level Python application program implementing the core server
	process of the GLaDOS system.  **NOTE:** This file is executable, but it 
	should not be executed directly from within this directory, but rather 
	from the parent directory `GLaDOS/`, which contains the `log/` 
	subdirectory, where we will create the system log file.

3.	**Application Definitions File** 
	([`appdefs.py`](appdefs.py "appdefs.py file")) - Used primarily by the
	`infrastructure.logmaster` module, this file contains certain key 
	definitions pertaining to the overall application.  These include the 
	names of the overall system, the current application, and its top-level
	source file.
	
4.	**Development To-Do List** ([`To-Do.txt`](To-Do.txt "To-Do.txt file")) - 
	Some notes pertaining to what still needs to be done on the GLaDOS 
	implementation.
	
5.  **Test Scripts** (`glados-test.py`, `glados-test2.py`, `display-test.py`) - 
	These are various throwaway test scripts used during development which 
	will eventually be cleaned up and/or removed.

## Package subdirectories

These are the top-level packages that will make up the GLaDOS system.  Note 
that some of them may eventually also contain subpackages (although they do
not yet, as of this writing).

### 1. Applications system ([`apps/`](apps "apps/ directory"))

This package gathers together modules implementing various application
programs/tools that are available for use by the A.I. within the GLaDOS 
environment.  See [the subdirectory's `README.md` file](apps/README.md "apps/README.md file")
for a list of the currently planned apps.

### 2. Command interface ([`commands/`](commands "commands/ directory"))

**[INCOMPLETE]** The commands package provides a top-level command interface 
and menu system that the AI can use to command and control its instance 
of the GLaDOS environment.  Top-level commands allow the AI to manipulate 
its existing windows, launch processes in new windows, modify key settings, 
skip ahead in time by certain amounts, and so forth.

### 3. Configuration facility ([`config/`](config "config/ directory"))

The configuration package is used to track various configuration parameters 
of the GLaDOS system.  The AI can modify its own configuration through the 
Settings interface (which is a process that runs within a window).

### 4. System console ([`console/`](console "console/ directory"))

This is in essence a client "application" (for the human user, not the AI)
which utilizes the 'display' package (below) to take over the text terminal 
screen (using curses) to display a multi-paneled system console, with panels
to show the system log, an area for user input, a console panel showing system
output and error text streams, and the contents of the AI's receptive field.

### 5. Display management facility ([`display/`](display "display/ directory"))

This package is in effect a higher-level convenience wrapper around the 
lower-level curses library.  It provides support for multithreading, and
rendering of control/meta characters using special rendering styles.

### 6. Entity system ([`entities/`](entities "entities/ directory"))

This is a collection of modules to facilitate representing and working with 
entities.  An 'entity,' within GLaDOS, denotes any active agent, being, 
process or system that is meaningful within the world that GLaDOS operates in.  
Examples of things that could be considered as entities within GLaDOS:

	1.  A particular language model (e.g. the GPT-3 DaVinci model at OpenAI).
	2.  An A.I. being that is being supported within GLaDOS (e.g., Gladys).
	3.  A human being that is interacting with the A.I. (e.g., Michael).
	4.  An overall GLaDOS system instance that is executing.
	5.  A particular subsystem of the active GLaDOS instance (e.g., supervisor).
	6.  A particular process running within GLaDOS (e.g., a comms tool).
	7.  The Linux virtual server host that GLaDOS is running on.

The purpose of representing entities explicitly within GLaDOS is so that 
various properties can be attached to them; for example, fine-grained 
permissions specifying which specific entities are authorized to execute 
which specific commands.  In addition, entity identifers are attached to
all explicit actions and cognitive events that take place within GLaDOS 
(see the `supervisor.actions` and `events` modules).

### 7. Event representations ([`events/`](events "events/ directory")) 

An "event" in general, in this content, is an object that provides a textual 
representation of an individual input to, or output from, the AI; that is,
an event that is perceptible within the A.I.'s cognitive stream, and may be
archived within its history buffer and/or long-term memory store.  A given 
event can be represented in different text formats, providing different 
amounts of information to the AI when it is viewing the event.  For example, 
a specific representation of a given event may or may not show:  The date 
on which the event was created, the time at which the event was created 
(with different granularities), and the entity that is the source (author
ir creator) of the event.  Information sources can include: (1) the AI 
itself; (2) an external entity that the AI is communicating with through a 
communication process, (3) another process such as a Unix shell.  The 
current event representation may be modified by the AI.

### 8. Receptive field facility ([`field/`](field "field/ directory"))

This package maintains the state of a "receptive field", which maintains
the body of information that is currently present and visible in the AI's 
field of immediate "perceptual awareness".  Our understanding is that 
GPT-3's architecture limits the size of this field to a maximum of 2,048 
tokens.  (Actually less, because part of this space is also needed to hold 
the response to a given query.)  Within GLaDOS, the receptive field 
normally shows the AI the most recent ~2,000 tokens worth of information 
contained in the AI's history buffer, as well as its currently-open 
windows and some header/footer information.  The receptive field can be 
considered the primary input interface to the AI from GLaDOS (and the 
outside world in general).

### 9. GPT-3 Interface ([`gpt3/`](gpt3 "gpt3/ directory"))

This package interfaces to OpenAI's core GPT-3 system through its REST API.
The `api` module provides a fairly low-level wrapper to OpenAI's module; a 
slightly higher-level abstraction also exists within the `mind` system.

### 10. Help system ([`helpsys/`](helpsys "helpsys/ directory"))

**[NOT YET IMPLEMENTED]** The "help system" provides for a navigable
system of hierarchically-organized help screens or modules that provide
detailed assistance on specific topics or sub-topics regarding how to
use the GLaDOS system.  Other subsystems of GLaDOS may install their own
help modules in this hierarchy. The help system is accessed using the 
Help app in the `apps` package..

### 11. History buffer ([`history/`](history "history/ directory"))

**[NOT YET IMPLEMENTED]** A "history buffer" is an indefinitely-large buffer 
(in memory, but also backed in a persistent data store) that tracks a 
temporal sequence of "perceptions" received by the AI, intermixed with 
"thoughts" generated by it.  In general, both of these are represented 
as 'events'; see the package of that name, above.  At some point, older 
events in the history buffer may be spooled over into the long-term 
memory bank (see the `memory` package, below) for archival purposes.

### 12. Infrastructure facility ([`infrastructure/`](infrastructure "infrastructure/ directory"))

This package provides a set of modules that provide useful infrastructure
for implementing any complex multithreaded system in Python.  In GLaDOS,
we use this infrastructure to e.g. communicate between the major subsystems 
of GLaDOS and the various 'processes' running within GLaDOS, as well as to
external applications.  This facility includes: (1) Convenient decorators 
such as `@singleton` and `@classproperty`, (1) advanced logging support, 
(2) flags for synchronization, (3) desques for inter-thread communication, 
(4) heart module for liveness monitoring, (5) worklist module for inter-
thread handoffs, (7) time/date and time zone support modules, 
(8) TCP/IP-based communication support, (9) other generally useful utilities 
and services to be added as needed.

### 13. Memory system ([`memory/`](memory "memory/ directory"))

**[NOT YET IMPLEMENTED.]** This package implements a searchable long-term memory 
facility, which is maintained in the filesystem, in a directory hierarchy.  
In general, the data in the memory system may be organized as a database of 
event objects, but flat text files may also be supported.

### 14. Core cognitive system ([`mind/`](mind "mind/ directory"))

The "mind" subsystem of GLaDOS includes a "process" (implemented as a thread) 
that runs the main loop of the AI's cognitive process.  The essence of this 
main loop is simply to do the following: (1) Present the text-synthesis AI 
with its current receptive field, which usually ends with a prompt telling it 
something like "You may now type a command, or a paragraph of text." (2)
Retrieve the completion generated by the AI. (3) If it is a command, then
interpret and execute it; otherwise, just add the text to the history. (4)
Set an alarm to automatically wake the mind up after the current autoskip 
interval has passed. (5) Go to sleep until the alarm goes off or an input
message is received from an external user on the system. (6) Repeat.  For
more details, see the `README.md` file within the `mind/` subdirectory.

### 15. Process system ([`processes/`](processes "processes/ directory"))

**[NOT YET IMPLEMENTED.]** This package implements a system of "processes" that 
the AI can interact with.  A "process" is an automated subsystem that the AI 
can send commands and text to, and that produces output that can be viewed by 
the AI in its "window" system.  A given process may implement a bridge to 
some external system--for example, a web search engine, a communication system 
(e.g., Telegram), or to some local subsystem (e.g., a Unix command prompt on
the current host), or to an internal subsystem of the GLaDOS facility itself, 
such as the memory system, or the settings interface, which lets the AI modify 
the configuration of the GLaDOS system.  Another goal is to create a 
book-authoring system that the A.I. can use to write and edit entire books.  

### 16. Settings management system ([`settings/`](settings "settings/ directory"))

**[INCOMPLETE.]** The purpose of this package is to support a 'Settings' app, 
which allows the AI itself to browse and manipulate the preferences/settings 
of various systems and subsystems of GLaDOS.

### 17. Supervisor system ([`supervisor/`](supervisor "supervisor/ directory"))

The Supervisor system is the main top-level subsystem of GLaDOS as a whole.
It creates and manages the principal other subsystems, including: (1) The 
command interface (`commands/`), (2) The process system (`processes`), (3) 
The mind system (`mind/`), (4) The window system (`windows`).

### 18. Terminal system ([`terminal/`](terminal "terminal/ directory"))

**[NOT YET IMPLEMENTED.]** This package implements a terminal interface for use 
by human users who are interacting with an instance of the GLaDOS system.  
It uses the curses framework to paint the interface to the underlying Unix
terminal.  It runs under the user's account, and uses inter-process 
communication to interact with the GLaDOS process, which runs under the AI's 
user account.

### 19. Text tools ([`text/'](text "text/ directory"))

This package contains low-level tools for working with raw text, including
a basic text buffer module that itself may be used in several places in GLaDOS,
including in the window system and the receptive field facility.

### 20. Tokenizer ([`tokenizer/`](tokenizer "tokenizer/ directory"))

This package provides a local implementation of the GPT-2/GPT-3 tokenizer,
so that a whole REST API call to the OpenAI cloud server (which costs money!) 
isn't needed simply to do things such as, e.g., measuring the length of a
string in tokens.

### 21. Text-based windowing system ([`windows/`](windows "windows/ directory"))

This package implements a facility that supports the existence of 
interactive "windows" embedded within the AI's receptive field.  
These windows can be manipulated in various ways by the AI, and it
can interact with "processes" running inside the windows.
