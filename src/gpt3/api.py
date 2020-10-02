# TODO: Write functionality for:
#	- Getting the API key from a file
#	- Configuring API parameters
#	- Calling the API.

import openai
import backoff

# This does graceful retries in case of REST failures.
# See https://pypi.org/project/backoff/
 
@backoff.on_exception(backoff.expo,
                      (openai.error.APIError))

def retry_openai(prompt):
    return openai.Completion.create(
            prompt=prompt,
            n=6,
            engine='davinci',
            max_tokens=700,
            stop=["\n\n\n"],
            temperature=0.7,
            logprobs=0,
        )
		

class GPT3Config:

    """This class gathers together a set of parameter values for passing to the 'completions'
	and/or 'completions/browser_stream' API calls."""

    #-----------------------------------------------------------------------
    #	Instance public data members.
    #
    #	engineId		[string]
    #	maxTokens		[intger]
    #	temperature		[number]
    #	topP			[number]
    #	nCompletions		[integer]
    #	stream			[boolean]
    #	logProbs		[integer]
    #   echo			[boolean]
    #	stop			[string or array]
    #	presencePenalty		[number]
    #	frequencyPenalty	[number]
    #	bestOf			[integer]

    pass
