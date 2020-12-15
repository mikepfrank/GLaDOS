#|==============================================================================
#|                TOP OF FILE:    windows/windowSystem.py
#|------------------------------------------------------------------------------
#|   The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    FILE NAME:      windows/windowSystem.py     [Python module source file]

    IN PACKAGE:		windows
	MODULE NAME:    windows.windowSystem
    FULL PATH:      $GIT_ROOT/GLaDOS/src/windows/windowSystem.py
    MASTER REPO:    https://github.com/mikepfrank/GLaDOS.git
    SYSTEM NAME:    GLaDOS (General Lifeform and Domicile Operating System)
    APP NAME:       GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.commands (command interface component)


	MODULE DESCRIPTION:
	-------------------

		This module initializes the GLaDOS command interface. This is the
		interface that allows the AI to type commands to the GLaDOS system
		and have them be executed by the system.
		
		The command interface is organized into "command modules" associated
		with specific facilities or processes within the GLaDOS system.  New
		command modules can be added dynamically into the interface.  In the
		main loop of the system, when the A.I. generates a text event, it is
		parsed to see if it matches a command template, and if so, then 
		control is dispatched to an appropriate command handler.

"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|------------------------------------------------------------------------------


        # A simple decorator for singleton classes.
from infrastructure.decorators  import  singleton

class TextBuffer:       # A text buffer.

        # A text buffer has:
        #       - A maximum length in rows.
        #       - A list of lines of text.
        
        def __init__(self, maxLen:int = 100):
                self._maxLen = maxLen
                self._rows = None               # Buffer is empty initially. No row data.
        
        def addText(self, text:str = None):
                pass


class Window:   # A text window within the GLaDOS window system.

        # A window has:
        #       - A title (textual label).
        #       - A text history buffer.
        #       - A list of snapshots.
        #       - Whether it is the currently active window.
        #       - An associated process.
        #       - Its state (open, minimized, or closed)
        #       - Its current size (number of lines to view)
        #       - Whether it is trying to stay in the receptive field
        #       - Whether it anchors to the top or bottom of the receptive field or is gloating.
        
        def __init__(self, *args):
                self._snapshots = []

        def addText(self, text:str):
                pass

class Windows:
        def Windows(self):
                self._windowList = []

class WindowSnapshot:   # A static image of a text window at a given point in time.

        # A snapshot has:
        #       - A text history buffer.
        #       - The window it's a snapshot of.
        #       - The time it was taken.
        #       - Its location in the text stream.
        #       - Its state (open or minimized).
        #       - Its current size (number of lines to inspect).
        
        pass

@singleton      
class WindowSystem:

        # The WindowSystem has:
        #       - Set of all windows in the system.
        #       - List of windows present in the receptive field.
        #       - List of windows anchored to the top of the receptive field.
        #       - List of windows anchored to the bottom of the receptive field (usually there is just one, the presently active window).

        def __init__(self):
                self._windows = Windows()
                

# Window system classes:
#
#       TextBuffer                      - An adjustable-sized buffer of text spooled to the window.
#       Window                          - A text window within the GLaDOS window system.
#       Windows                         - A collection of text windows.
#       WindowSnapshot          - A static image of a text window at a given point in time.
#       WindowSystem                            - The entire window subsystem in a given GLaDOS system instance.


