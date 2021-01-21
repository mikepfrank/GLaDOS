# AI Data Directory for the example "Gladys" Persona in the GLaDOS System

**Location within repo:** `$GIT_ROOT/GLaDOS/ai-data/`

**Suggested install location:** `/opt/AIs/gladys/` (directory owned by user `gladys`, group `ais`).

## Top-Level Files

This section lists and documents the files existing at top-level within this directory.

### AI Configuration File ([`ai-config.hjson`](ai-config.hjson "ai-config.hjson file"))

Human-readable JSON file with configuration settings specific to the individual AI persona.

### API Usage Statistics (`api-stats.json`, `api-stats.txt`)

JSON and human-readable versions of the API usage statistics; these are maintained by
the gpt3.api module, and are cumulative since the last time `api-stats.json` was deleted.
Example appearance of the `api-stats.txt` file:

	             Token Counts
	        -----------------------       USD
	 Engine   Input  Output   Total      Cost
	======= ======= ======= ======= =========
	    ada       0       0       0 $  0.0000
	babbage  262492    6149  268641 $  0.3224
	  curie  295297    5687  300984 $  1.8059
	davinci  167595    7773  175368 $ 10.5221
	------- ------- ------- ------- ---------
	TOTALS:  725384   19609  744993 $ 12.6504

### Text for the AI's Information application ([`info.txt`](info.txt "info.txt file"))

This file contains the text that is automatically displayed by the 'Info' app
within GLaDOS in a window near the top of the receptive field at the time that
the environment boots up.  It is intended to orient the AI to the context.

### Initial goals list ([`init-goals.hjson`](init-goals.hjson "init-goals.hjson file"))

This file is used to initialize the Goals app with that AI's initial list of
high-level goals.  After modification by the AI, the goal list is subsequently
maintained by the Goals app in the file `cur-goals.json`.

### README File for the AI's Data Directory (`README.md`)

This file.
