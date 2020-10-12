#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|  FILE NAME:      gpt3/api.py                         [Python 3 module file]
"""
    MODULE NAME:    gpt3.api                                [Python 3 module]

    DESCRIPTION:

        This module implements a convenience wrapper around OpenAI's API
        for accessing their GPT-3 language models.  The main feature that
        this wrapper provides at the moment is remembering the current
        values of various API parameters.

    PUBLIC CLASSES:

        GPT3Core - A connection to the core GPT-3 system that maintains
            its own persistent API parameters.

        GPT3APIConfig - Tracks a set of API parameter settings.
            These can also be modified dynamically.

    PUBLIC GLOBALS:

        Note: The following global module 'constants' can be modified 
        dynamically by the user. They will affect the properties of
        subsequently-created instances of GPT3Core, but not of the
        existing instances.  To modify an existing instance, access
        its .conf property.

            DEF_ENGINE  - GPT-3 engine name (default 'davinci').
            DEF_TOKENS  - Number of tokens to output (def. 42).
            DEF_TEMP    - Default temperature (default is 0.5).
            DEF_STOP    - Stop string or strings (3 newlines).

    EXAMPLES:

        /----------------------------------------------------------\
        | #!/usr/bin/python3                                       |
        |                                                          |
        | from pprint   import pprint                              |
        | from gpt3.api import GPT3Core                            |
        |                                                          |
        | gpt3 = GPT3Core()                                        |
        |   # Makes a new instance w. default parameter values.    |
        |                                                          |
        | result = gpt3.genCompletion("Mary had a little lamb, ")  |
        |                                                          |
        | pprint(result)                                           |
        \----------------------------------------------------------/
            |
            V 
            
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

"""
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
DEF_STOP    = "\n\n\n"  # Use 3 newlines (two blank lines) as stop.


#|==============================================================================
#|  Module public classes.                                      [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|---------------------------------------------------------------------------
    #|
    #|  gpt3.api.GPT3APIConfig                             [module public class]
    #|
    #|      This class provides an abstraction for a 'configuration' of
    #|      GPT-3 API parameter values.  These can be modified dynamically
    #|      at runtime (i.e., in between different API calls).
    #|
    #|  Public interface:
    #|
    #|      .modify(params)                         [instance method]
    #|
    #|          Modify the specified parameters of the configuration.
    #|
    #|  Special methods:
    #|
    #|      __init__    - Instance initializer.
    #|      __str__     - Display as a human-readable string.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class GPT3APIConfig:

    """This class gathers together a set of parameter values for passing to the
        'completions' and/or 'completions/browser_stream' API calls."""

    #/--------------------------------------------------------------------------
    #|  Instance public data members for class GPT3APIConfig. (See API docs.)
    #|
    #|      .engineId            [string]
    #|      .maxTokens           [intger]
    #|      .temperature         [number]
    #|      .topP                [number]
    #|      .nCompletions        [integer]
    #|      .stream              [boolean]
    #|      .logProbs            [integer]
    #|      .echo                [boolean]
    #|      .stop                [string or array]
    #|      .presencePenalty     [number]
    #|      .frequencyPenalty    [number]
    #|      .bestOf              [integer]
    #|
    #\--------------------------------------------------------------------------

        #|----------------------------------------------------------------------
        #|  Initializer for class GPT3APIConfig.    [special instance method]
        #|
        #|  Arguments:
        #|      
        #|      engineId                                            [string]
        #|
        #|          The name of the specific GPT-3 model/engine to use.
        #|          Choices as of 10/11/2020 are:  ada, ada-beta, babbage,
        #|          babbage-beta, content-filter-alpha-c4, curie, 
        #|          curie-beta, davinci, davinci-beta.  Earlier names
        #|          alphabetically are smaller models.  The default value
        #|          is davinci.
        #|
        #|      maxTokens                                           [integer]
        #|
        #|          The maximum number of tokens to return in the response.
        #|          Defaults to 42.
        #|
        #|      temperature                                         [number]
        #|
        #|          A floating-point number between 0 and 1 that roughly
        #|          indicates the degree of randomness in the response.
		#|			Default value: 0.5.
        #|
        #|      topP                                                [number]
        #|
        #|          A floating point number between 0 and 1 that restricts
        #|          answers to the top percentage of probability mass.
        #|          Do not use this and temperature in the same query.
        #|          Default value: None.
        #|          [NOTE: This parameter is yet supported by this module.]
        #|
        #|      nCompletions                                        [integer]
        #|
        #|          How many completions to return.  Default value is 1.
        #|
        #|      stream                                              [boolean]
        #|
        #|          If true, then the result will be streamed back incre-
        #|          mentally as a sequence of server-sent events.
		#|			Default: False.
        #|
        #|      logProbs                                            [integer]
        #|
        #|          Return the log-probabilities of this many of the top
        #|          most likely tokens, in addition to the sampled token
        #|          (which may or may not be in this set). Default: None.
		#|			(Meaning, don't return log-probabilities.)
        #|
        #|      echo                                                [boolean]
        #|
        #|          Includes the prompt in the response. Default: False.
        #|
        #|      stop                                                [object]
        #|
        #|          A string or an array of up to 4 strings, such that
        #|          the first occurrence of any of these strings in the 
        #|          output will terminate the response just before it.
		#|			Default value: Three newlines (two blank lines).
        #|
        #|      presencePenalty                                     [number]
        #|
        #|          Number between 0 and 1 that penalizes new tokens
        #|          based on whether they appear in the text so far.
		#|			Default value: 0 (no penalty).
        #|
        #|      frequencyPenalty                                    [number]
        #|
        #|          Number between 0 and 1 that penalizes new tokens
        #|          based on how often they appear in the text so far.
		#|			Default value: 0 (no penalty).
        #|
        #|      bestOf                                              [integer]
        #|
        #|          Number of candidate completions to generate 
        #|          server-side; the best nCompletions ones of those 
        #|          are returned.  Default: Not set (i.e., don't do).
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __init__(inst, engineId:str=DEF_ENGINE, maxTokens:int=DEF_TOKENS, 
                    temperature:float=DEF_TEMP, topP:float=None, 
                    nCompletions:int=1, stream:bool=False,
                    logProbs:int=None, echo:bool=False, stop=DEF_STOP,
                    presPen:float=0, freqPen:float=0, bestOf:int=None):

        """Initialize a GPT-3 API configuration, reverting to
                default values for un-supplied parameters."""
                    
        inst.engineId           = engineId
        inst.maxTokens          = maxTokens
        inst.temperature        = temperature
        inst.topP               = topP
        inst.nCompletions       = nCompletions
        inst.stream             = stream
        inst.logProbs           = logProbs
        inst.echo               = echo
        inst.stop               = stop
        inst.presencePenalty    = presPen
        inst.frequencyPenalty   = freqPen
        inst.bestOf             = bestOf
    
    
        #|----------------------------------------------------------------------
        #|  .modify(params)                             [instance public method]
        #|
        #|      Modify the specified parameters of the configuration to
        #|      the given values.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
    def modify(self, engineId:str=None, maxTokens:int=None, 
                    temperature:float=None, topP:float=None, 
                    nCompletions:int=None, stream:bool=False,
                    logProbs:int=None, echo:bool=None, stop=None,
                    presPen:float=None, freqPen:float=None, bestOf:int=None):

        """Modify one or more parameter values in the configuration."""
        
        if engId        != None:    inst.engineId           = engId
        if maxTokens    != None:    inst.maxTokens          = maxTokens
        if temperature  != None:    inst.temperature        = temperature
        if topP         != None:    inst.topP               = topP
        if nCompletions != None:    inst.nCompletions       = nCompletions
        if stream       != None:    inst.stream             = stream
        if logProbs     != None:    inst.logProbs           = logProbs
        if echo         != None:    inst.echo               = echo
        if stop         != None:    inst.stop               = stop
        if presPen      != None:    inst.presencePenalty    = presPen
        if freqPen      != None:    inst.frequencyPenalty   = freqPen
        if bestOf       != None:    inst.bestOf             = bestOf


    def __str__(self):
    
        """A human-readable string description of the parameter values."""
        
        return f"""
GPT3 Configuration:
    engine_id         = {self.engineId}
    max_tokens        = {self.maxTokens}
    temperature       = {self.temperature}
    top_p             = {self.topP}
    n                 = {self.nCompletions}
    stream            = {self.stream}
    logprobs          = {self.logProbs}
    echo              = {self.echo}
    stop              = {repr(self.stop)}
    presence_penalty  = {self.presencePenalty}
    frequency_penalty = {self.frequencyPenalty}
    best_of           = {self.bestOf}"""[1:]

#__/ End class GPT3APIConfig.


    #|--------------------------------------------------------------------------
    #|  
    #|  gpt3.api.GPT3Core                                 [module public class]
    #|
    #|      This class abstracts a connection to the core GPT-3 system.  
    #|      An instance of this class remembers its API configuration 
    #|      options.
    #|
    #|  Public interface:
    #|
    #|      .conf                                   [instance property]
    #|
    #|          Current API configuration of this core connection.
    #|
    #|      .adjustConf(params)                     [instance method]
    #|
    #|          Modify one or more API parameters of the connection.
    #|
    #|      .genCompletion(prompt)                  [instance method]
    #|
    #|          Generate a completion object from the given prompt.
    #|
    #|      .genString(prompt)                      [instance method]
    #|
    #|          Generate a single out string from the given prompt.
    #|      
    #|  Special methods:
    #|
    #|      __init__    - Instance initializer.
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
        #|  USAGE:
        #|
        #|      core = GPT3Core()           # Uses default parameter values.
        #|      core = GPT3Core(config)     # Use this GPT3APIConfig object.
        #|      core = GPT3Core(params)     # List of keyword arguments.
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


        #|----------------------------------------------------------------------
        #|  .conf                                   [instance public property]
        #|
        #|      Returns the API configuration object (instance of class
        #|      GPT3AIConfig) that is associated with this connection to
        #|      the core GPT-3 system.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    @property
    def conf(self):
        """Get our current API configuration."""
        return self._configuration


        #|----------------------------------------------------------------------
        #|  .adjustConf(params)                     [instance public method]
        #|
        #|      Adjusts the API parameter values of this connection to 
        #|      the core GPT-3 system as specified by the argument list.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def adjustConf(self, *args, **kwargs):
        """Adjust the API configuration as specified."""
        self.conf.modify(*args, **kwargs)


        #|----------------------------------------------------------------------
        #|  .genCompletion(prompt:string)           [instance public method]
        #|
        #|      This method returns the raw completion of the given prompt,
        #|      using the core's present API configuration.  We do graceful
        #|      backoff and retry in case of REST call failures.
        #|
        #|      To do: Provide the option to do a temporary modification of
        #|      one or more API parameters in the argument list.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

            #------------------------------------------------------
            # This does graceful retries in case of REST failures.
            # See https://pypi.org/project/backoff/
 
    @backoff.on_exception(backoff.expo,
                          (openai.error.APIError))

    def genCompletion(self, prompt=None):
    
        """With automatic exponential backoff, query the server
                for a completion object for the given prompt using the
                connection's current API configuration."""
    
        kwargs = dict() # Empty dict for building up argument list.
        
        conf = self.conf    # Get our current configuration.
        
        if prompt                   != None:    kwargs['prompt']            = prompt
        if conf.maxTokens           != None:    kwargs['max_tokens']        = conf.maxTokens
        if conf.temperature         != None:    kwargs['temperature']       = conf.temperature
        if conf.topP                != None:    kwargs['top_p']             = conf.topP
        if conf.nCompletions        != None:    kwargs['n']                 = conf.nCompletions
        if conf.stream              != None:    kwargs['stream']            = conf.stream
        if conf.logProbs            != None:    kwargs['logprobs']          = conf.logProbs
        if conf.echo                != None:    kwargs['echo']              = conf.echo
        if conf.stop                != None:    kwargs['stop']              = conf.stop
        if conf.presencePenalty     != None:    kwargs['presence_penalty']  = conf.presencePenalty
        if conf.frequencyPenalty    != None:    kwargs['frequency_penalty'] = conf.frequencyPenalty
        if conf.bestOf              != None:    kwargs['best_of']           = conf.bestOf
        
        if conf.temperature != None and conf.topP != None:
            # Do some better error handling here. Warning and/or exception.
            print("WARNING: Setting both temperature and top_p is not recommended.")
    
        return openai.Completion.create(engine = conf.engineId, **kwargs)
            # Call the completion creation with the required argument, and whichever 
            # ones of the optional arguments were supplied.
        
    #__/ End method GPT3Core.genCompletion().

        #|----------------------------------------------------------------------
        #|  .genString(prompt:string)               [instance public method]
        #|
        #|      This method returns a completion of the given prompt
        #|      as a single string.  Uses .genCompletion() internally.
        #|
        #|      To do: Provide the option to do a temporary modification of
        #|      one or more API parameters in the argument list.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
    def genString(self, prompt):
    
        """Generate a single completion string for the given prompt."""
            
        result = genCompletion(prompt)
        return ''.join(result['choices'][0]['text'])

#__/ End class GPT3Core.

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|  END FILE:   gpt3/api.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
