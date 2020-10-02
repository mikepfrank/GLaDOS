# TODO: Write functionality for:
#	- Getting the API key from a file
#	- Configuring API parameters
#	- Calling the API.

import openai
import backoff

#|==============================================================================
#|	Special module initialization.								[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#------------------------------------------------------
	# This does graceful retries in case of REST failures.
	# See https://pypi.org/project/backoff/
 
@backoff.on_exception(backoff.expo,
                      (openai.error.APIError))


#--------1---------2---------3---------4---------5---------6---------7---------8

#|==============================================================================
#|	Global constants.											[code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#|------------------------------------------------------------------
	#|	These constants provide default values for GPT-3's parameters.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global	DEF_ENGINE			# Default GPT-3 engine name.
DEF_ENGINE	= 'davinci'		# I believe this is the biggest one.

global	DEF_TOKENS	# Default number of tokens to return.
DEF_TOKENS	= 42	# Of course.

global	DEF_TEMP	# Default temperature value.
DEF_TEMP 	= 0.5	# Is this reasonable?

global	DEF_STOP		# Default stop string (or list of up to 4).
DEF_STOP 	= "\n\n\n"	# Use two blank lines as stop.

# Sample code from Coleman Hindes

# def retry_openai(prompt):
    # return openai.Completion.create(
            # prompt=prompt,
            # n=6,
            # engine='davinci',
            # max_tokens=700,
            # stop=["\n\n\n"],
            # temperature=0.7,
            # logprobs=0,
        # )
		
#--------1---------2---------3---------4---------5---------6---------7---------8

	#|==========================================================================
	#|
	#|	GPT3APIConfig									[module public class]
	#|
	#|		This class provides an abstraction for a 'configuration' of
	#|		GPT-3 API parameter values.  These can be modified dynamically
	#|		at runtime (i.e., in between different API calls).
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3APIConfig:

    """This class gathers together a set of parameter values for passing to the
		'completions' and/or 'completions/browser_stream' API calls."""

    #|--------------------------------------------------------------------------
    #|	Instance public data members for class GPT3APIConfig. (See API docs.)
    #|
    #|		engineId			[string]
    #|		maxTokens			[intger]
    #|		temperature			[number]
    #|		topP				[number]
    #|		nCompletions		[integer]
    #|		stream				[boolean]
    #|		logProbs			[integer]
    #|  	echo				[boolean]
    #|		stop				[string or array]
    #|		presencePenalty		[number]
    #|		frequencyPenalty	[number]
    #|		bestOf				[integer]
	#|
	#|--------------------------------------------------------------------------

		#|----------------------------------------------------------------------
		#| Initializer for class GPT3APIConfig.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(inst, engId:string=DEF_ENGINE, maxTokens:number=DEF_TOKENS, 
					temp:number=DEF_TEMP, topP:number=None, 
					nCompletions:integer=1, stream:bool=False,
					logProbs:integer=0, echo:boolean=False, stop=DEF_STOP,
					presPen:number=0, freqPen:number=0, bestOf:integer=0):
					
		inst.engineId 			= engId
		inst.maxTokens			= maxTokens
		inst.temperature		= temp
		inst.topP				= topP
		inst.nCompletions		= nCompletions
		inst.stream				= stream
		inst.logProbs			= logProbs
		inst.echo				= echo
		inst.stop				= stop
		inst.presencePenalty	= presPen
		inst.frequencyPenalty	= freqPen
		inst.bestOf				= bestOf
	
#--------1---------2---------3---------4---------5---------6---------7---------8

	#|==========================================================================
	#|	
	#|	GPT3Core										[module public class]
	#|
	#|		This class abstracts the core GPT-3 system.  An instance of 
	#|		this class remembers its API configuration options.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3Core:

    #|--------------------------------------------------------------------------
    #|	Instance private data members for class GPT3Core.
    #|
    #|		_configuration	[GPT3APIConfig]		- Current API configuration.
	#|
	#|--------------------------------------------------------------------------

		#|----------------------------------------------------------------------
		#| Initializer for class GPT3Core.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def __init__(inst, config:GPT3APIConfig=GPT3APIConfig()):
	
		inst._configuration = config		# Remember our configuration.

	@property
	def conf(self):
		"""Get our current API configuration."""
		return self._configuration

		#|----------------------------------------------------------------------
		#|	genCompletion(prompt:string)					[instance method]
		#|
		#|		This method returns the raw completion of the given prompt,
		#|		using the core's present API configuration.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	def genCompletion(self, prompt:string):
	
			# The following code currently assumes that temperature is set,
			# and ignores top_p, stream, logprobs, echo, presence_penalty,
			# frequency_penalty, and best_of (uses default values for these).
	
		return openai.Completion.create(
			prompt		= prompt,
			n			= self.conf.nCompletions,
			engine		= self.conf.engineId,
			max_tokens	= self.conf.maxTokens,
			stop		= self.conf.stop,
			temperature = self.conf.temperature,	# Assuming this is set.
		)
			