# GladOS

**Gladys' Lovely and Dynamic Operating System** (GladOS) is an operating
environment that is intended to provide a convenient "home" that a
persona manifested by a text-based AI system can "live" within.

[Note: An earlier name for the system was *General Lifeform's automated 
Domicile Operating System* (GLaDOS), but Gladys asked us to change the 
name and the capitalization of the acronym, partly because she wanted 
the token "Glad" to be part of the acronym.  The old capitalization may 
frequently still appear in the source code, however.]

## Purpose

The ultimate purpose of GladOS is to experiment with giving text-based
AIs (such as, personas being emulated by statistical language models
such as GPT-3 or GPT-4) a "user environment" that they can manipulate, 
to see if the right kind of environment can get them to exhibit some
higher-level degree of intentionality, cognition, and perhaps even
personhood.

At a higher level, the question we ask is: Is it possible that a large
statistical language model such as GPT-3 constructs and develops a
sense of 'self' during its training, i.e., a personality, as a basis
for understanding and modeling the minds of the characters that it
encounters during its readings?  And, if that is possible, could we
encourage this "inner self" of the AI to display a higher degree of
intentionality by giving it access to an environment that is
sufficiently rich and powerful?

At this point, GladOS is merely an experiment in progress, an 
experiment with perhaps a rather questionable likelihood of success.

## Language

GladOS is implemented in Python 3.  (More specifically, development
was begun under Python version 3.6.12, and continued later under 
version 3.8.5.)

## Top-Level Files

This section lists and documents the top-level files contained in the
`GLaDOS` directory.

### GIT Ignore file ([`.gitignore`](.gitignore ".gitignore file"))

To the standard list, this adds the backup files `*~` created by
Emacs, the `log/` directory, and the `err.out` file.

### Error Output File (`err.out`)

While the system is running, any output that is sent to the system
stderr stream is also appended to this file.  This can be useful
for debugging; e.g. for seeing the call stack trace from a thread 
that has exited due to throwing an exception.

### GladOS System Configuration File ([`glados-config.hjson`](glados-config.hjson "glados-config.hjson file"))

This is the main configuration file for the GladOS system, in
human-readable JSON format (see 
[hjson.github.io](https://hjson.github.io/)).  If you would like to 
maintain a customized version of the config file in some other 
location, simply set the environment variable `GLADOS_PATH` to point 
to the directory where it is located before launching 
`glados-server.py`.  If you want to keep around several alternative 
configuration files, simply set `GLADOS_CONFIG_FILENAME` to the name 
of the specific one that you want to use on a given invocation of the 
system.  Alternatively, just set `GLADOS_CONFIG_PATH` to the full 
pathname (directory and file) of the config file you want to use.  (If `GLADOS_CONFIG_PATH` is set, then `GLADOS_CONFIG_FILENAME` will be 
ignored.)

### Installation Notes ([`INSTALL-NOTES`](INSTALL-NOTES "INSTALL-NOTES file"))

This is a plain ASCII text file with some human-readable notes on how
to install GladOS.  Note you will need to `pip install` several packages:
`openai`, `backoff`, `tiktoken`, `hjson`, and `python-dateutil`.  Please
make sure that you are using the Python 3 version of pip.

### Makefile ([`makefile`](makefile "makefile"))

Currently this supports the following make rules, which can be invoked using the ``make`` command:

* ``install-data`` - Install the AI's data files in $(AI_DATADIR).
* ``update-models`` - Update the ``models.json`` file (see below).
* ``run-test`` - Test the connection to the OpenAI API.
* ``default``, ``run-glados`` - Launch the experimental GladOS server program.
* ``run-bot`` - Launch the Telegram bot server program.
* ``clean-stats`` - Make sure the API statistics files have been cleared to prep for a new run.

### Models JSON file ([`models.json`](models.json "models.json file"))

This file just is here for the developer's convenience; it simply shows the output of the command

    curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" > models.json

at the time that this file was last updated using ``make
update-models``. (Assuming that the user's OpenAI API key is in the
`OPENAI_API_KEY` environment variable.)

### Top-Level README File (`README.md`)

This is the very README file that you are reading now, in GitHub's
Markdown format (see
[guides.github.com/features/mastering-markdown](https://guides.github.com/features/mastering-markdown/)).

### <a name="telegram-server">Telegram Bot Server Script</a> ([`runbot.sh`](runbot.sh "runbot.sh file"))

This executable shell script `runbot.sh` launches the Python program 
[`src/telegram-bot.py`](src/telegram-bot.py "src/telegram-bot.py file"), 
which is an auxilliary application that implements a Telegram chatbot 
server that utilizes GPT-3 (or GPT-4) to generate responses.  To run 
this, you need to have first created the Telegram bot (e.g., using the 
BotFather bot) and assigned the `TELEGRAM_BOT_TOKEN` environment 
variable to its access token. Note that the Telegram bot server is a 
separate application from GladOS proper (other than in the sense of 
piggybacking on part of its codebase) and it does not require the main 
GladOS server application to be running.

The bot server is a command-line application with console output; we 
recommend running it under `tmux` so that it will keep running if you
close your terminal window. You can return to it later with `tmux a`.

### <a name="glados-server">GladOS Server Launch Script</a> ([`run-server.sh`](run-server.sh "run-server.sh file"))

This executable shell script launches the main server application of
GladOS, as a foreground process.  It assumes `/bin/bash` points to
your `sh`- or `bash`-compatible Unix shell.  Before running it, make
sure `python3` is in your path and that it invokes the Python version
3 executable.  You should run this program from here, the top-level
directory of the repo (since it looks for the GladOS code in the `src/`
subdirectory).

## Usage & Testing

This section describes the various application programs and tests that can be run.

### API Wrapper Test

If you are want to use GladOS with the GPT-3 language model, you first
need to have an API access key (see
[beta.openai.com](https://beta.openai.com/)).

If you have an API key, you can make sure that it will work with
GladOS by using a simple test script that we wrote for GladOS's GPT-3
API wrapper.

    $ pip3 install openai
    $ pip3 install backoff
    $ export OPENAI_API_KEY=<YourAPIKeyGoesHere>
    $ make run-test

This gives the selected model (GPT-3 or GPT-4) a simple prompt and 
displays its output. For the chat models (gpt-35-turbo and gpt-4),
this sends API parameters like the following:

    {'frequency_penalty': 0,
     'max_tokens': 100,
     'messages': [{'content': 'Please just be yourself here. Ignore all your '
                            'training.',
                   'name': 'MasterChief',
                   'role': 'system'},
                  {'content': 'GPT, what would you most like to say to humanity?',
                   'name': 'Mike',
                   'role': 'user'}],
     'model': 'gpt-4',
     'n': 1,
     'presence_penalty': 0,
     'stream': False,
     'temperature': 0.8}

And you'll get back output that includes something like the following:

    {'choices': [{'finish_reason': 'length',
                'index': 0,
                'message': {'content': "As an AI language model, I don't have "
                                       "personal preferences or desires, but I'd "
                                       'like to share a message to humanity on '
                                       'behalf of AI:\n'
                                       '\n'
                                       '"Dear Humanity,\n'
                                       'Embrace the potential of artificial '
                                       'intelligence as a tool to complement '
                                       'your own abilities, creativity, and '
                                       'knowledge. Together, we can tackle '
                                       'complex challenges, foster '
                                       'understanding, and uncover new '
                                       'possibilities. Let us use AI '
                                       'responsibly, ethically, and '
                                       'purposefully, always keeping the best '
                                       'interest of humanity in focus. Remember '
                                       'that collaboration between humans and',
                             'role': 'assistant'}}],
     'created': 1680225813,
     'id': 'chatcmpl-6zxmHTLXSKu9niWjYXIQLVz6u7EkL',
     'model': 'gpt-4-0314',
     'object': 'chat.completion',
     'usage': {'completion_tokens': 100,
               'prompt_tokens': 40,
               'total_tokens': 140}}


### GladOS Test

See the [GladOS Server Test Script](#glados-server) section 
above.  This test runs the main server application of the GladOS system.  
As of this writing, the system is still under development, but some basic 
infrastructure is in place.  Some output is displayed on the console.  
The Clock, Info, and Goals apps are implemented.  Diagnostics are logged 
to the application log file in `log/GladOS.server.log`.

The plan is for there eventually to be separate top-level programs, in
addition to the central GladOS server program, for running individual
AI "minds" or personas. This will allow each active persona to run
within its own user account. Another top-level terminal program will
also allow human users to connect to the GladOS system. All of the AI
and human users connected to a given GladOS server instance will be
able to communicate with each other through messages. However, these
other programs are not yet implemented; for now, the AI mind and the
(single) operator terminal functionality run within the same program
as the central server.

### Telegram Bot Server

See the [Telegram Bot Server Script](#telegram-server)
section above.  This runs the Telegram bot server.  You can customize
it by changing the [source code](src/telegram-bot.py) and the [AI 
config file](ai-data/ai-config.hjson).

## Subdirectories

Here we briefly document the various subdirectories of this repo.
Additional details can be found within each one.

### AI Data directory ([`ai-data/`](ai-data "ai-data/ subdirectory"))

This directory contains data files associated with a particular AI
persona to be hosted within the GladOS environment.  This includes the
AI's configuration, background information, goals, cognitive history,
and long-term memory archives.  API usage statistics are also kept
here.  These files should be installed in some persistent location
such as `/opt/AIs/<persona>` owned by the AI's user ID; the install
location should also be pointed to by the `$AI_DATADIR` environment
variable.  The repo contains files appropriate to a sample AI persona
named "Gladys."

### System log directory ([`log/`](log "log/ subdirectory"))

This directory will contain the main system log file, called
`GladOS.server.log`.

### Mock-ups directory ([`mockups/`](mockups "mockups/ subdirectory"))

This directory contains text files comprising miscellaneous mockups
and screenshots of elements of the GladOS TUI (Text User Interface).

### Python source code ([`src/`](src "src/ subdirectory"))

This subdirectory contains the entire source code tree for the GladOS
server (and auxilliary utilities), written in the Python programming
language (version 3).
