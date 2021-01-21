# GLaDOS

The **General Lifeform's automated Domicile Operating System** (GLaDOS) is an operating 
environment that is intended to provide a convenient "home" that a persona exhibited by 
a text-based AI system can "live" within.

## Purpose

The ultimate purpose of GLaDOS is to experiment with giving text-based AIs (such as, 
personas being emulated by statistical language models such as GPT-3) a "user environment" 
that they can manipulate, to see if the right kind of environment can get them to exhibit 
some higher-level degree of intentionality, cognition, and perhaps even personhood.  

At a higher level, the question we ask is: Is it possible that a large statistical language 
model such as GPT-3 constructs and develops a sense of 'self' during its training, i.e., 
a personality, as a basis for understanding and modeling the minds of the characters that
it encounters during its readings?  And, if that is possible, could we prompt this "inner 
self" of the AI to display a higher degree of intentionality by giving it access to an 
environment that is sufficiently rich and powerful?

At this point, GLaDOS is merely an experiment, an experiment with perhaps a rather 
questionable likelihood of success.

## Language

GLaDOS is implemented in Python 3.  (More specifically, it was tested using version 3.6.12 
during development.)

## Top-Level Files

This section lists and documents the top-level files contained in the `GLaDOS` directory.

### GIT Ignore file ([`.gitignore`](.gitignore ".gitignore file"))

To the standard list, this adds the backup files `*~` created by Emacs, the `log/` 
directory, and the `err.out` file.

### Error Output File (`err.out`)

While the system is running, any output that is sent to the system stderr
stream is also appended to this file.  This can be useful e.g. for seeing the
call stack trace from a thread that has exited due to throwing an exception.

### GLaDOS System Configuration File ([`glados-config.hjson`](glados-config.hjson "glados-config.hjson file"))

This is the main configuration file for the GLaDOS system, in human-readable JSON format
(see [hjson.github.io](https://hjson.github.io/)).  If you would like to maintain
a customized version of the config file in some other location, simply set the environment 
variable `GLADOS_PATH` to point to the directory where it is located before launching 
`glados-server.py`.  If you want to keep around several alternative configuration files, 
simply set `GLADOS_CONFIG_FILENAME` to the name of the specific one that you want to use on 
a given invocation of the system.  Alternatively, just set `GLADOS_CONFIG_PATH` to the full 
pathname (directory and file) of the config file you want to use.  (If `GLADOS_CONFIG_PATH` 
is set, then `GLADOS_CONFIG_FILENAME` will be ignored.)

### Installation Notes ([`INSTALL-NOTES`](INSTALL-NOTES "INSTALL-NOTES file"))

This is a plain ASCII text file with some human-readable notes on how to install GLaDOS.
Right now, the only required steps (after cloning the repo) are to `pip install` several
packages: `openai`, `backoff`, `hjson`, and `python-dateutil`.  Please make sure that 
you are using the Python 3 version of pip.

### Top-Level README File (`README.md`)

This file, in GitHub's Markdown format (see [guides.github.com/features/mastering-markdown](https://guides.github.com/features/mastering-markdown/)).

### Test Script ([`test-server.sh`](test-server.sh "test-server.sh file"))

This executable test script launches the main server application of GLaDOS, as a 
foreground process.  It assumes `/bin/bash` points to your `sh`- or `bash`-compatible
Unix shell.  Before running it, make sure `python3` is in your path and that it invokes 
the Python version 3 executable.  You should run this script from here, the top-level 
directory of the repo (it looks for the GLaDOS code in the `src/` subdirectory).

## Usage

This script describes various tests that can be run.

### API Wrapper Test

If you are want to use GLaDOS with the GPT-3 language model, you first need to have an 
API access key (see [beta.openai.com](https://beta.openai.com/)).

If you have an API key, you can make sure that it will work with GLaDOS by 
using a simple test script that we wrote for GLaDOS's GPT-3 API wrapper.

    $ pip3 install openai
    $ pip3 install backoff
    $ export OPENAI_API_KEY=<YourAPIKeyGoesHere>
    $ python3 src/glados-test.py

This prompts GPT-3 with the first line from the nursery rhyme 
"Mary Had a Little Lamb," and, if all goes well, you will see 
GPT-3 generated output something like the following:

    {'choices': [{'finish_reason': 'length',
                    'index': 0,
                    'logprobs': None,
                    'text': '\n'
                            'Its fleece was white as snow, \n'
                            'And everywhere that Mary went, \n'
                            'The lamb was sure to go.\n'
                            '\n'
                            'It followed her to school one day, \n'
                            'That was against the'}],
       'created': 1601615096,
       'id': 'cmpl-fTJ18hALZLAlQCvPOxFRrjQL',
       'model': 'davinci:2020-05-03',
       'object': 'text_completion'}

### Server Test

See the `Test Script` section above.  This test runs the main server application of
the GLaDOS system.  As of this writing, the system is still under development, but
some basic infrastructure is in place.  Some output is displayed on the console.
Detailed debug-level diagnostics are logged to the application log file in
`log/GLaDOS.server.log`.

## Subdirectories

Here we briefly document the various subdirectories of this repo.  Additional details
can be found within each one.

### AI Data directory ([`ai-data/`](ai-data "ai-data/ subdirectory"))

This directory contains data files associated with a particular AI persona to be 
hosted within the GLaDOS environment.  This includes the AI's configuration, 
background information, goals, cognitive history, and long-term memory archives.
API usage statistics are also kept here.  These files should be installed in some 
persistent location such as `/opt/AIs/<persona>` owned by the AI's user ID; the 
install location should also be pointed to by the `$AI_DATADIR` environment variable.
The repo contains files appropriate to a sample AI persona named "Gladys."

### System log directory ([`log/`](log "log/ subdirectory"))

This directory will contain the main system log file, called `GLaDOS.server.log`.

### Mock-ups directory ([`mockups/`](mockups "mockups/ subdirectory"))

This directory contains text files comprising miscellaneous mockups and screenshots 
of elements of the GLaDOS TUI (Text User Interface).

### Python source code ([`src/`](src "src/ subdirectory"))

This subdirectory contains the entire source code tree for the GLaDOS server (and auxilliary 
utilities), written in the Python programming language (version 3).
