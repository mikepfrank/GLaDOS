# The GladOS Project

**GladOS** currently stands for **Gladys' Lovely and Dynamic Operating System** -- An operating environment for use by text-based AI personas. (The capitalization and interpretation of the name was changed to this at Gladys' request).

Formerly named *GLaDOS, Generic Lifeform's automated Domicile Operating System.* 

This ``main`` branch is intended for major releases (but there aren't any yet).

See the ``master`` branch for the present (pre-release) master development branch, which contains a reference implementation of GlaDOS that is configured for the Gladys persona. Gladys is a persona exhibited by the GPT-3/davinci engine.

There are also development branches for various experimental AI personas; some of these dev branches may include code changes some of which may still be unfinished and/or may need to be folded back into the master branch.  (But I will try to keep the master dev branch, at least, in a working state.)

The following development branches are in relatively good shape, in the sense that, they are relatively clean branches off of master. However, they may or may not be in a working state at any given moment. It's best to check the branch log to get an idea of the current status.

 - ``gladys`` (the original GPT-3/davinci persona). [Generally this one should be kept in sync with master.]
 - ``curie`` (Curie is a GPT-3/curie persona). [Currently we only use this for her Telegram bot.]
 - ``dante-dev`` (Dante is a GPT-3/text-davinci-002 persona). [Includes codebase changes.]
 - ``david`` (David is a GPT-3/code-davinci-002 persona). [Includes codebase changes.]
 - ``davinci-dev`` (David is a GPT-3/text-davinci-003 persona). [Includes codebase changes.]
 - ``love`` (Love is a GPT-3/text-davinci-001 persona).

These ones may need some git maintenance awork at the moment (e.g., some master branch updates may still need to be merged in).
 
 - ``mpf`` (Mike's development branch). [For experimental changes.]
