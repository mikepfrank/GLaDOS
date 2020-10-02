#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#|

import openai
import backoff

#|==============================================================================
#|  Global constants.                                           [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|------------------------------------------------------------------
    #|  These constants provide default values for GPT-3's parameters.
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global  DEF_ENGINE          # Default GPT-3 engine name.
DEF_ENGINE  = 'davinci'     # I believe this is the biggest one.

global  DEF_TOKENS  # Default number of tokens to return.
DEF_TOKENS  = 42    # Of course.

global  DEF_TEMP    # Default temperature value.
DEF_TEMP    = 0.5   # Is this reasonable?

global  DEF_STOP        # Default stop string (or list of up to 4).
DEF_STOP    = "\n\n\n"  # Use two blank lines as stop.


    #|==========================================================================
    #|
    #|  GPT3APIConfig                                   [module public class]
    #|
    #|      This class provides an abstraction for a 'configuration' of
    #|      GPT-3 API parameter values.  These can be modified dynamically
    #|      at runtime (i.e., in between different API calls).
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3APIConfig:

    """This class gathers together a set of parameter values for passing to the
        'completions' and/or 'completions/browser_stream' API calls."""

    #|--------------------------------------------------------------------------
    #|  Instance public data members for class GPT3APIConfig. (See API docs.)
    #|
    #|      engineId            [string]
    #|      maxTokens           [intger]
    #|      temperature         [number]
    #|      topP                [number]
    #|      nCompletions        [integer]
    #|      stream              [boolean]
    #|      logProbs            [integer]
    #|      echo                [boolean]
    #|      stop                [string or array]
    #|      presencePenalty     [number]
    #|      frequencyPenalty    [number]
    #|      bestOf              [integer]
    #|
    #|--------------------------------------------------------------------------

        #|----------------------------------------------------------------------
        #| Initializer for class GPT3APIConfig.
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __init__(inst, engId:str=DEF_ENGINE, maxTokens:int=DEF_TOKENS, 
                    temp:float=DEF_TEMP, topP:float=None, 
                    nCompletions:int=1, stream:bool=False,
                    logProbs:int=0, echo:bool=False, stop=DEF_STOP,
                    presPen:float=0, freqPen:float=0, bestOf:int=0):
    # def __init__(inst, engId=DEF_ENGINE, maxTokens=DEF_TOKENS, temp=DEF_TEMP, 
    #                 topP=None, nCompletions=1, stream=False, logProbs=0, 
    #                 echo=False, stop=DEF_STOP, presPen=0, freqPen=0, bestOf=0):
                    
        inst.engineId           = engId
        inst.maxTokens          = maxTokens
        inst.temperature        = temp
        inst.topP               = topP
        inst.nCompletions       = nCompletions
        inst.stream             = stream
        inst.logProbs           = logProbs
        inst.echo               = echo
        inst.stop               = stop
        inst.presencePenalty    = presPen
        inst.frequencyPenalty   = freqPen
        inst.bestOf             = bestOf
    
#--------1---------2---------3---------4---------5---------6---------7---------8

    #|==========================================================================
    #|  
    #|  GPT3Core                                        [module public class]
    #|
    #|      This class abstracts the core GPT-3 system.  An instance of 
    #|      this class remembers its API configuration options.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3Core:

    #|--------------------------------------------------------------------------
    #|  Instance private data members for class GPT3Core.
    #|
    #|      _configuration  [GPT3APIConfig]     - Current API configuration.
    #|
    #|--------------------------------------------------------------------------

        #|----------------------------------------------------------------------
        #| Initializer for class GPT3Core.
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __init__(inst, config:GPT3APIConfig=GPT3APIConfig()):
    
        inst._configuration = config        # Remember our configuration.

    @property
    def conf(self):
        """Get our current API configuration."""
        return self._configuration

        #|----------------------------------------------------------------------
        #|  genCompletion(prompt:string)                    [instance method]
        #|
        #|      This method returns the raw completion of the given prompt,
        #|      using the core's present API configuration.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        	#------------------------------------------------------
        	# This does graceful retries in case of REST failures.
        	# See https://pypi.org/project/backoff/
 
    @backoff.on_exception(backoff.expo,
                          (openai.error.APIError))

    def genCompletion(self, prompt):
    
            # The following code currently assumes that temperature is set,
            # and ignores top_p, stream, logprobs, echo, presence_penalty,
            # frequency_penalty, and best_of (uses default values for these).
    
        return openai.Completion.create(
            prompt      = prompt,
            n           = self.conf.nCompletions,
            engine      = self.conf.engineId,
            max_tokens  = self.conf.maxTokens,
            stop        = self.conf.stop,
            temperature = self.conf.temperature,    # Assuming this is set.
        )
            
