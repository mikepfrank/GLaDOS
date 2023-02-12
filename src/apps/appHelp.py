# appHelp.py 
#
# Generic help-system support for applications.
# This module facilitates putting together help system
# screens for applications. It provides a base class for
# help modules that are associated with an application,
# and for sub-modules that are typically associated with
# applications, such as help modules for subcommands of
# the application launch command, or for other commands
# that are associated with the application.

from helpsys.helpSystem import HelpModule, HelpItem

# A help module that is associated with an application
# generically gives an overview of the application, and
# documents its associated commands and subcommands.

class AppHelpModule(HelpModule):
    
        """This is the base class for help modules that are associated with an 
            application. It automatically constructs the module's name, topic,
            and introductory text from the application object, and constructs
            the module's help screen text from the application's main command
            module. It also provides a method for retrieving the application
            object that the module is associated with."""

        def __init__(self, 
                app,            # The application that this help module is associated with.
                name    =None,  # Name of the module (constructed automatically if None).
                topic   =None,  # Topic of the module (constructed automatically if None).
                intro   =None,  # Introductory text for the module (retrieved from the app if None).
                text    =None,  # Full text of the module's screen (constructed automatically if None).
                cmdMod  =None,  # Main command module for the application (retrieved from the app if None).
            ):
    
            """Instance initializer for the AppHelpModule class. The <app> 
                argument is the application that the help module is associated 
                with, the <name> argument is the name of the module, the <topic>
                argument is the topic of the module, and the <intro> argument is 
                the introductory text for the module. If any of these arguments 
                are None, they are constructed automatically from the 
                application object. The <cmdMod> argument is the main command 
                module for the application, and is used to construct the rest 
                of the module's help screen text. If this argument is None, it 
                is retrieved from the application object. If the <text> argument 
                is provided, or can be retrieved from the application object or
                config file parameters, it is used as the module's help screen 
                text, and the <intro> and <cmdMod> arguments are ignored."""

            self.app = app

            # Construct the module name if necessary.
            if name is None:
                name = app.name + " help"

            # Construct the module topic if necessary.
            if topic is None:
                topic = app.name + " application"
            
            # Construct the module intro text if necessary.
            # This is retrieved from the application object if possible,
            # or from the system config file (which takes precedence).
            if intro is None:
                intro = app.getHelpIntro()  # Try to get the intro from the app object.
                    # (This also checks the system config file.)
            
            # Retrieve the main command module for the application if necessary.
            if cmdMod is None:
                cmdMod = app.getCmdMod()    # Try to get the command module from the app object.
            
            # Construct the module's help screen text if necessary.
            # This is retrieved from the application object if possible,
            # or from the system config file (which takes precedence).
            if text is None:
                text = app.getHelpText()
                    # (This also checks the system config file.)
                if text is None:
                    # Assemble the help screen text from the intro and command module, if possible.
                    if intro is not None and cmdMod is not None:
                        text = intro + '\n\n' + cmdMod.getHelpText()
                    elif intro is not None:
                        text = intro
                    elif cmdMod is not None:
                        text = cmdMod.getHelpText()

            super(AppHelpModule, self).__init__(name, topic, intro, text)
                # Pass along the topic, intro, and text to the superclass initializer.

        