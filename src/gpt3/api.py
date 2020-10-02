#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#|  FILE NAME:  gpt3/api.py                             [Python 3 module file]
#|
#|  DESCRIPTION:
#|
#|      This module implements a convenience wrapper around OpenAI's API
#|      for accessing their GPT-3 language model.  The main feature that
#|      this wrapper provides at the moment is remembering the current
#|      values of API parameters.
#|
#|  PUBLIC CLASSES:
#|
#|      GPT3Core - A connection to the core API w. persistent parameters.
#|
#|  PUBLIC GLOBALS:
#|
#|      Note: The following global 'constants' can be modified 
#|      dynamically by the user. They will affect the properties of
#|      subsequently-created instances of GPT3Core, but not of the
#|      existing instances.  To modify an existing instance, access
#|      its .conf property.
#|
#|          DEF_ENGINE  - GPT-3 engine name (default 'davinci').
#|          DEF_TOKENS  - Number of tokens to output (def. 42).
#|          DEF_TEMP    - Default temperature (default is 0.5).
#|          DEF_STOP    - Stop string or strings (3 newlines).
#|
#|  EXAMPLES:
#|
#|      /----------------------------------------------------------\
#|      | #!/usr/bin/python3                                       |
#|      |                                                          |
#|      | from pprint   import pprint                              |
#|      | from gpt3.api import GPT3Core                            |
#|      |                                                          |
#|      | gpt3 = GPT3Core()                                        |
#|      |   # Makes a new instance w. default parameter values.    |
#|      |                                                          |
#|      | result = gpt3.genCompletion("Mary had a little lamb, ")  |
#|      |                                                          |
#|      | pprint(result)                                           |
#|      \----------------------------------------------------------/
#|          |
#|          V 
#|          
#|      {'choices': [{'finish_reason': 'length',
#|                    'index': 0,
#|                    'logprobs': None,
#|                    'text': '\n'
#|                            'Its fleece was white as snow, \n'
#|                            'And everywhere that Mary went, \n'
#|                            'The lamb was sure to go.\n'
#|                            '\n'
#|                            'It followed her to school one day, \n'
#|                            'That was against the'}],
#|       'created': 1601615096,
#|       'id': 'cmpl-fTJ18hALZLAlQCvPOxFRrjQL',
#|       'model': 'davinci:2020-05-03',
#|       'object': 'text_completion'}
#|
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#|==============================================================================
#|  Module imports.                                           [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import openai       # OpenAI's Python bindings for their REST API to GPT-3.
import backoff      # Utility module for exponential backoff on failures.

#|==============================================================================
#|  Global constants.                                           [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|-----------------------------------------------------------------
    #| These are the names you get if you do 'from gpt3.api import *'. 
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__
__all__ = [
    'DEF_ENGINE',       # Default GPT-3 engine name ('davinci').
    'DEF_TOKENS',       # Default number of tokens to return (42).
    'DEF_TEMP',         # Default temperature value (normally 0.5).
    'DEF_STOP',         # Default stop string or list of strings.
    'GPT3APIConfig',    # A collection of API parameter settings.
    'GPT3Core'          # Instance of the API that remembers its config.
    ]

    #|------------------------------------------------------------------
    #|  These constants provide default values for GPT-3's parameters.
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global  DEF_ENGINE          # Default GPT-3 engine name.
DEF_ENGINE  = 'davinci'     # I believe this is the biggest one.

global  DEF_TOKENS      # Default number of tokens to return.
DEF_TOKENS  = 42        # Of course.

global  DEF_TEMP        # Default temperature value.
DEF_TEMP    = 0.5       # Is this reasonable?

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
    

    def __str__(inst):
        return f"""GPT3 Configuration:
    			engine_id         = {inst.engineId}
                        max_tokens        = {inst.maxTokens}
                        temperature       = {inst.temperature}
                        top_p             = {inst.topP}
                        n                 = {inst.nCompletions}
                        stream            = {inst.stream}
                        logprobs          = {inst.logProbs}
                        echo              = {inst.echo}
                        stop              = {repr(inst.stop)}
                        presence_penalty  = {inst.presencePenalty}
                        frequency_penalty = {inst.frequencyPenalty}
                        best_of           = {inst.bestOf}
    		   """


    #|==========================================================================
    #|  
    #|  GPT3Core                                        [module public class]
    #|
    #|      This class abstracts the core GPT-3 system.  An instance of 
    #|      this class remembers its API configuration options.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3Core:

    """An instance of this class represents a connection to the core GPT-3 
        API that remembers its parameter settings."""

    #|--------------------------------------------------------------------------
    #|  Instance private data members for class GPT3Core.
    #|
    #|      _configuration  [GPT3APIConfig]     - Current API configuration.
    #|
    #|--------------------------------------------------------------------------

        #|----------------------------------------------------------------------
        #| Initializer for class GPT3Core.
        #|
        #|	USAGE:
        #|
        #|		core = GPT3Core()
        #|		core = GPT3Core(config)
        #|		core = GPT3Core(params)
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __init__(inst, *args, **kwargs):

            # If keyword args 'config=' is present, use that as the config.
        
        if 'config' in kwargs:
            config = kwargs['config']
        else:
            config = None

            # Otherwise, if the first argument is a GPT3APIConfig, use that as the config.
    
        if config == None and len(args) > 0:
            if args[0] != None and isinstance(args[0],GPT3APIConfig):
                config = args[0]

            # If no config was provided, then create one from the arguments.
            # (In future, this should be changed to otherwise modify the provided
            # config based on the remaining arguments.)

        if config == None:
            config = GPT3APIConfig(*args, **kwargs)

        print("Creating new GPT3Core connection with configuration:\n", config)

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
            
