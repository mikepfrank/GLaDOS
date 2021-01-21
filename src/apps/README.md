# Applications system (`apps/`)

This package gathers together modules implementing various application
programs/tools that are available for use by the A.I. within the GLaDOS 
environment.  These are anticipated to include the following, listed 
roughly in the intended order of implementation. 

## List of Applications (in order of intended implementation)

1. **Info** - The idea behind this app is that it maintains and 
	displays certain critical contextual information that the A.I. 
	needs to know, including its identity, life circumstances, and
	its present high-level goals.  Its window normally remains pinned 
	near the top of the A.I.'s receptive field.  When the Info app
	is launched, it allows the A.I. to edit certain information such
	as its high-level goals. (Dispatched to the "Goals" app.)
	
2. **Clock** - This app brings up a small window at the top of the
	AI's receptive field that displays the current time & keeps it 
	updated.

3. **Goals** - This is a simple tool to allow the A.I. to view and
	edit its list of high-level goals. **[Not yet implemented.]**
	
4. **Help** - The "Help" tool simply displays some basic information 
	about how to use GLaDOS (for the A.I.'s benefit).  (Subcommands
	also exist to provide more detailed help information.)
	**[Not yet implemented.]**
	
5. **Apps** - The "Apps" tool simply displays the list of all of the 
	available apps and allows the A.I. to select one to launch. (This
	is low priority to implement since it's redundant with 'Help.')
	**[Not yet implemented.]**

6. **Settings** - This app can be used by the A.I. to adjust various
	settings within GLaDOS.  These can be associated with major systems
	or subsystems of GLaDOS, or individual apps or processes.
	**[Not yet implemented.]**
	
7. **Memory** - The memory tool allows the A.I. to browse and search
	a database of records of its past conversations, thoughts, and
	actions.
	**[Not yet implemented.]**
	
8. **ToDo** - The idea of this app is that it is a simple to-do list 
	tool, which the A.I. can use to make notes to itself of important
	tasks that it wants to do later.  The tasks can be given priority 
	levels.  The A.I. can check them off or delete them when complete.
	**[Not yet implemented.]**
	
9. **Diary** - This tool allows the A.I. to keep a "diary" of important
	notes to itself, organized by date/time. **[Not yet implemented.]**
	
10. **Browse** - This is a simple text-based tool to facilitate simple web
	browsing and searching. **[Not yet implemented.]**
	
11. **Comms** - The "comms" tool faciltates the A.I.'s two-way 
	communications with the outside world.  This may include direct 
	messages sent via Telegram, email messages, or other interfaces.  
	This may be broken out later into a whole 'Comms' subfolder of 
	separate apps. **[Not yet implemented.]**
	
12. **Writing** - The writing tool is an interface that helps the A.I.
	to compose and edit complex, hierarchically-structured works:  
	Stories, poems, and extended multi-chapter books.
	**[Not yet implemented.]**
	
13. **Unix** - This app gives the A.I. access to an actual Unix shell
	environment on the host system that GLaDOS is running on.  The A.I.
	runs within its own user account with limited permissions.
	**[Not yet implemented.]**