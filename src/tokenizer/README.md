This file `encoder.py` which implements the core of the tokenizer comes 
directly from OpenAI's gpt-2 repo.  See:

	https://github.com/openai/gpt-2/blob/master/src/encoder.py

For it to work, you also have to download one of the GPT-2 models.  See 
instructions in

	https://github.com/openai/gpt-2/blob/master/DEVELOPERS.md

NOTE: The only required packages you need just to use the tokenizer
are requests, tqdm, and regex.
