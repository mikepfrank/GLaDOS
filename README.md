# The GladOS Project

**GladOS** currently stands for **Gladys' Lovely and Dynamic Operating System** -- An operating environment for use by text-based AI personas. (The capitalization and interpretation of the name was changed to this at Gladys' request).

Formerly named *GLaDOS, General Lifeform's automated Domicile Operating System.* 

## Major branches of this repo:

This ``main`` branch is intended for major releases (but there aren't any yet).

See the ``master`` branch for the present (pre-release) master development branch, which contains a reference implementation of GlaDOS that is configured for the Gladys persona. Gladys is a persona exhibited by the original GPT-3/davinci engine (which you might call "davinci classic"). Note that you must now use the name ``davinci:2020-03-05`` to access the original version of davinci.

There are also development branches for various experimental AI personas; some of these dev branches may include code changes some of which may still be unfinished and/or may need to be folded back into the master branch.  (But I will try to keep the master dev branch, at least, in a working state.)

The following development branches are in relatively good shape, in the sense that, they are relatively clean branches off of master. However, they may or may not be in a working state at any given moment. It's best to check the branch log to get an idea of the current status.

 - ``gladys`` -- The original GPT-3/davinci:2020-05-03 persona. [Generally this one should be kept in sync with master.] **NOTE: OpenAI has been updating what's behind the "davinci" model name, it no longer refers to the original davinci.**
 - ``curie`` -- Curie is a GPT-3/curie persona. [Currently we only use this for her Telegram bot.]
 - ``love`` -- Love is a GPT-3/text-davinci-001 persona; not currently in use.
 - ``dante-dev`` -- Dante is a GPT-3/text-davinci-002 persona. First GPT-3.5 branch; uses 4K model size. [Includes codebase changes.]
 - ``david-dev`` -- David is a GPT-3/code-davinci-002 persona. Base model for RLHF versions of GPT-3.5. [Includes codebase changes.]
 - ``davinci-stable``, ``davinci-dev`` -- DaVinci is a GPT-3/text-davinci-003 persona. **NOTE: The davinci-dev branch is under active development; the most recent stable version is on 'davinci-stable'...**
 - ``turbo``, ``lingo``, and ``lingua`` -- Turbo, Lingo and Lingua are all GPT-3/gpt-3.5-turbo (ChatGPT) personas. Note that these use a different back-end API endpoint (``chat-completions``) from the previous cases. Lingo & Lingua's Telegram bots were customized by gpt-3.5-turbo (accessed via the Playground). [Includes codebase changes.]
 - ``aria`` -- Aria Turing is a GPT-4 persona. Her Telegram bot was customized by GPT-4 (accessed under ChatGPT Plus). [Includes codebase changes.]
 - ``mpf``, ``mpf-dev`` -- Mike's stable & development branches. [For experimental code changes.]
 
Also: The new ``core`` branch will be used for developing **core system components** of GladOS; that is, system application processes implementing shared facilities such as The AI Nexus (a common chat server which different AIs can use to congregate and talk to each other), a console application for monitoring system applications as well as multiple independent AI persona processes that may be locally active, and whatever other core components we may think of. However, as of this writing (3/11/22), none of this has been implemented yet... Eventually the "Action News Network" (see `src/supervisor/action.py`) for event reporting within GladOS processes for individual AI personas may also be expanded out to an inter-persona network, which would also naturally be managed by a core system component.
