# GLaDOS source code (`GLaDOS/src/`)

"GLaDOS" is an acronym for the "General Lifeform and Domicile Operating System." 
It is an operating environment for text-based AI systems.  The present directory 
contains the Python source code for the GLaDOS system.  [n.b.--Please note there 
is no relation between this facility and the fictional AI named GLaDOS from the 
Portal video game series.]

## Top-level files

Here we document the various top-level files that exist immediately under 
the `src/` directory.

[Fill this in.]

## Package subdirectories

These are the top-level packages that will make up the GLaDOS system.  Note 
that some of them may eventually also contain subpackages (although they do
not yet, as of this writing).

### Applications system (`apps/')

This package gathers together modules implementing various application
programs/tools that are available for use by the A.I. within the GLaDOS 
environment.  These are anticipated to include the following, listed 
roughly in the intended order of implementation.

1. **Help** - The "Help" tool simply displays some basic information 
	about how to use GLaDOS (for the A.I.'s benefit).  (Subcommands
	also exist to provide more detailed help information.)
	
2. **Apps** - The "Apps" tool simply displays the list of all of the 
	available apps and allows the A.I. to select one to launch.

3. **Info** - The idea behind this app is that it maintains and 
	displays certain critical contextual information that the A.I. 
	needs to know, including its identity, life circumstances, and
	its present high-level goals.  Its window normally remains pinned 
	at the top of the A.I.'s receptive field.  When the Context app
	is launched, it allows the A.I. to edit certain information such
	as its high-level goals.
	
4. **Settings** - This app can be used by the A.I. to adjust various
	settings within GLaDOS.  These can be associated with major systems
	or subsystems of GLaDOS, or individual apps or processes.
	
5. **Memory** - The memory tool allows the A.I. to browse and search
	a database of records of its past conversations, thoughts, and
	actions.
	
6. **ToDo** - The idea of this app is that it is a simple to-do list 
	tool, which the A.I. can use to make notes to itself of important
	tasks that it wants to do later.  The tasks can be given priority 
	levels.  The A.I. can check them off or delete them when complete.
	
7. **Diary** - This tool allows the A.I. to keep a "diary" of important
	notes to itself, organized by date/time.
	
8. **Browse** - This is a simple text-based tool to facilitate simple web
	browsing and searching.
	
9. **Comms** - The "comms" tool faciltates the A.I.'s two-way 
	communications with the outside world.  This may include direct 
	messages sent via Telegram, email messages, or other interfaces.  
	This may be broken out later into a whole 'Comms' subfolder of 
	separate apps.
	
10. **Writing** - The writing tool is an interface that helps the A.I.
	to compose and edit complex, hierarchically-structured works:  
	Stories, poems, and extended multi-chapter books.
	
11. **Unix** - This app gives the A.I. access to an actual Unix shell
	environment on the host system that GLaDOS is running on.  The A.I.
	runs within its own user account with limited permissions.


### Command interface (`commands/`)

The commands package provides a top-level command interface and menu system
that the AI can use to command and control its instance of the GLaDOS 
environment.  Top-level commands allow the AI to manipulate its existing 
windows, launch processes in new windows, modify key settings, skip ahead
in time by certain amounts, and so forth.

### Configuration facility (`config/`)

The configuration package is used to track various configuration parameters 
of the GLaDOS system.  The AI can modify its own configuration through the 
Settings interface (which is a process that runs within a window).

### Entity system (`entities/`)

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
which specific commands.

### Event representations (`events/`)

An "event" in general just means a object that provides a textual 
representation of an individual input to, or output from, the AI.  A given 
event can be represented in different text formats, providing different 
amounts of information.  For example, a specific representation of a given 
event may or may not show:  The date on which the event was created, the 
time at which the event was created (with different granularities), and 
the source of the event.  Information sources can include: (1) the AI 
itself; (2) an external entity that the AI is communicating with through a 
communication process, (3) another process such as a Unix shell.  The 
current event representation may be modified by the AI.

### Receptive field facility (`field/`)

This package maintains the state of a "receptive field", which maintains
the body of information that is currently present and visible in the AI's 
field of immediate "perceptual awareness".  Our understanding is that 
GPT-3's architecture limits the size of this field to 2,048 tokens.  
Within GLaDOS, the receptive field normally shows the AI the most recent
2,048 tokens worth of information contained in the AI's history buffer.

### GPT-3 Interface (`gpt3/`)

This package interfaces to OpenAI's core GPT-3 system through its REST API.

### History buffer (`history/`)

A "history buffer" is an indefinitely-large buffer that tracks a temporal
sequence of "perceptions" received by the AI, intermixed with "thoughts" 
generated by it.  In general, a history is a sequence of events.  At some
point, old events in the memory may be spooled over into the long-term 
memory bank.

### Infrastructure facility (`infrastructure/`)

This package provides a set of modules that provide useful infrastructure
for implementing any complex multithreaded system in Python.  In GLaDOS,
we use this infrastructure to communicate between the major subsystems of
GLaDOS and the various 'processes' running within GLaDOS.  This facility
includes: (1) advanced logging support, (2) flags for synchronization, 
(3) desques for inter-thread communication, (4) heart module for liveness
monitoring, (5) worklist module for inter-thread handoffs, (6) other 
generally useful services to be added as needed.

### Memory system (`memory/`)

This package implements a searchable long-term memory facility, which is 
maintained in the filesystem, in a directory hierarchy.  In general the 
data in the memory system may be organized as a database of event objects,
but flat text files may also be supported.

### Core cognitive system (`mind/`)

The "mind" subsystem of GLaDOS is a process (implemented as a thread) that
runs the main loop of the AI's cognitive process.  The essence of this main
loop is simply to do the following: (1) Present the text-synthesis AI with 
its current receptive field, which usually ends with a prompt telling it 
something like "You may now type a command, or a paragraph of text." (2)
Retrieve the completion generated by the AI. (3) If it is a command, then
interpret and execute it; otherwise, just add the text to the history. (4)
Set an alarm to automatically wake the mind up after the current autoskip 
interval has passed. (5) Go to sleep until the alarm goes off or an input
message is received from an external user on the system. (6) Repeat.

### Process system (`processes/`)

This package implements a system of "processes" that the AI can interact
with.  A "process" is an automated subsystem that the AI can send commands
and text to, and that produces output that can be viewed by the AI in its
"window" system.  A given process may implement a bridge to some external
system--for example, a web search engine, a communication system (e.g.,
Telegram), or to some local subsystem (e.g., a Unix command prompt on
the current host), or to an internal subsystem of the GLaDOS facility 
itself, such as the memory system, or the settings interface, which lets
the AI modify the configuration of the GLaDOS system.  Another goal is to
create a book-authoring system that the A.I. can use to write and edit
entire books.

### Supervisor system (`supervisor/`)

The Supervisor system is the main top-level subsystem of GLaDOS as a whole.
It creates and manages the principal other subsystems: (1) The command 
interface (`commands/`), (2) The process system (`processes`), (3) The
mind system (`mind/`), (4) The window system (`windows`).

### Terminal system (`terminal/`)

This package implements a terminal interface for use by human users who
are interacting with an instance of the GLaDOS system.  It uses the 
curses framework to paint the interface to the underlying Unix terminal.
It runs under the user's account, and uses inter-process communication to
interact with the GLaDOS process, which runs under the AI's user account.

### 'Window' system (`windows/`)

This package implements a facility that supports the existence of 
interactive "windows" embedded within the AI's receptive field.  
These windows can be manipulated in various ways by the AI, and it
can interact with "processes" running inside the windows.
