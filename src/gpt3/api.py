#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|						TOP OF FILE:	gpt3/api.py
#|------------------------------------------------------------------------------
#|	 The below module documentation string will be displayed by pydoc3.
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
    MODULE NAME:    gpt3.api                                [Python 3 module]

	IN PACKAGE:		gpt3
	FULL PATH:		$GIT_ROOT/GLaDOS/src/gpt3/api.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (GLaDOS server application)
	SW COMPONENT:	GLaDOS.gpt3 (GLaDOS GPT-3 interface component)


	MODULE DESCRIPTION:
	-----------------

        This module implements a convenience wrapper around OpenAI's API
        for accessing their GPT-3 language models.  The main feature that
        this wrapper provides at the moment is keeping track of the current
        values of various API parameters.  It also provides handy functions
        for things like measuring string lengths in tokens.


    PUBLIC CLASSES:

        GPT3APIConfig - Keeps track of a set of API parameter settings.
            These can also be modified dynamically.

        GPT3Core - A connection to the core GPT-3 system that maintains
            its own persistent API parameters.
            
        Completion - For objects representing results returned by the 
            core API.


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


	PUBLIC FUNCTIONS:
	
			countTokens()	- Counts tokens in a string using the
								API.  Note that this operation is
								expensive.  For most applications
								you should use the method in the
								tokenizer.tokenizer module instead.

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
        | pprint(result.complStruct)                               |
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


    #|--------------------------------------------------------------------------
    #|  __all__                                     [special module attribute]
    #|
    #|      These are the names that will be imported if you do 
    #|      'from gpt3.api import *'.  This in effect declares what
    #|      the public interface to this module consists of.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global __all__
__all__ = [

        # Module public global constants.
    'DEF_ENGINE',       # Default GPT-3 engine name ('davinci').
    'DEF_TOKENS',       # Default number of tokens to return (42).
    'DEF_TEMP',         # Default temperature value (normally 0.5).
    'DEF_STOP',         # Default stop string or list of strings.
    
        # Module public classes.
    'GPT3APIConfig',    # Class: A collection of API parameter settings.
    'Completion',       # Class: An object for a result returned by the API.
    'GPT3Core',         # Class: Instance of the API that remembers its config.
    
        # Module public functions.
    'countTokens'       # Function to count tokens in a string.
    
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
#|  Global objects.                                             [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global  _theTokenCounterCore    # A core connection for counting tokens.
_theTokenCounterCore = None     # Initially not yet created.

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
    #|      conf = GPT3AIConfig(params)                   [instance constructor]
    #|
    #|          Create a new configuration object with specified parameters.
    #|          Others not provided revert to defaults.
    #|
    #|      conf.modify(params)                                [instance method]
    #|
    #|          Modify the specified parameters of the configuration.
    #|
    #|      str(inst)                                   [special instance method]
    #|
    #|          Converts the configuration to a human-readable string
    #|          representation.
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
    #|  API parameters:
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
    #|  Other attributes:
    #|      .name [string] - Human-readable name for this configuration.
    #|
    #\--------------------------------------------------------------------------

        #|----------------------------------------------------------------------
        #|  Initializer for class GPT3APIConfig.       [special instance method]
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
        #|          Default value: 0.5.
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
        #|          Default: False.
        #|
        #|      logProbs                                            [integer]
        #|
        #|          Return the log-probabilities of this many of the top
        #|          most likely tokens, in addition to the sampled token
        #|          (which may or may not be in this set). Default: None.
        #|          (Meaning, don't return log-probabilities.)
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
        #|          Default value: Three newlines (two blank lines).
        #|
        #|      presencePenalty                                     [number]
        #|
        #|          Number between 0 and 1 that penalizes new tokens
        #|          based on whether they appear in the text so far.
        #|          Default value: 0 (no penalty).
        #|
        #|      frequencyPenalty                                    [number]
        #|
        #|          Number between 0 and 1 that penalizes new tokens
        #|          based on how often they appear in the text so far.
        #|          Default value: 0 (no penalty).
        #|
        #|      bestOf                                              [integer]
        #|
        #|          Number of candidate completions to generate 
        #|          server-side; the best nCompletions ones of those 
        #|          are returned.  Default: Not set (i.e., don't do).
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __init__(inst, 
                    engineId:str=DEF_ENGINE,    maxTokens:int=DEF_TOKENS, 
                    temperature:float=DEF_TEMP, topP:float=None, 
                    nCompletions:int=1,         stream:bool=False,
                    logProbs:int=None,          echo:bool=False, 
                    stop=DEF_STOP,              presPen:float=0, 
                    freqPen:float=0,            bestOf:int=None,
                    name=None):

        """Initialize a GPT-3 API configuration, reverting to
            default values for any un-supplied parameters."""
                    
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
        
        inst.name               = name
    
    #__/ End instance initializer for class GPT3APIConfig,
    
    
        #|----------------------------------------------------------------------
        #|  .modify(params)                             [public instance method]
        #|
        #|      Modify the specified parameters of the configuration to
        #|      the given values.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
    def modify(self, 
                engineId:str=None,      maxTokens:int=None, 
                temperature:float=None, topP:float=None, 
                nCompletions:int=None,  stream:bool=None,   
                logProbs:int=None,      echo:bool=None,         
                stop=None,              presPen:float=None, 
                freqPen:float=None,     bestOf:int=None):

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

    #__/ End instance method GPT3APIConfig.modify().

    
        #|----------------------------------------------------------------------
        #|  String converter.                          [special instance method]
        #|
        #|      Generates a human-readable string representation of this
        #|      API configuration.  This shows all the parameter values.
        #|      

    def __str__(self):
    
        """A human-readable string description of the parameter values."""
        
        if self.name == None:
            namestr = ""
        else:
            namestr = f" \"{self.name}\""
        
        return f"""
GPT3 Configuration{namestr}:
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


    # Forward declaration of GPT3Core so we can reference it 
    # from within the Completion class definition.
class GPT3Core:
    pass
    
#|------------------------------------------------------------------------------
#|  gpt3.api.Completion                                 [module public class]
#|
#|      This class is a wrapper for the completion data structure 
#|      returned by the underlying GPT-3 API.  The constructor calls
#|      the API to create this structure.  Various properties allow
#|      easy access to information contained in the structure.
#|
#|  Usage:
#|
#|      compl = Completion(prompt, core)
#|
#|          Creates a completion of the given prompt string using 
#|          the given GPT3Core instance.
#|
#|      compl = Completion(complStruct)
#|
#|          Creates a completion object wrapping the given 
#|          completion structure, previously generated.
#|
#|      text = compl.text
#|
#|          Returns the text of the completion as a single string.
#|
#|      nTok = compl.nTokens
#|
#|          Returns the total number of tokens in the completion.
#|          Note that this property only works if the core had
#|          'logprobs=0' at the time that the completion was 
#|          generated.
#|
#|      promptLen = compl.promptLen
#|
#|          Returns the length of the prompt in tokens. Note that 
#|          this property only works if the core had 'echo=True' 
#|          and 'logprobs=0' set at the time that the completion 
#|          was generated.
#|      
#|      complLen = compl.resultLen
#|
#|          Returns the length of the result (not including the 
#|          prompt) in tokens. Note that this property only works
#|          if 'logprobs=0' and is only useful if 'echo=True'
#|          since otherwise you could just use .nTokens.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class Completion:

    """An instance of this class represents a result returned from the
        GPT-3 API's completion creation call."""

    #/--------------------------------------------------------------------------
    #|  Public data members.                               [class documentation]
    #|
    #|      .prompt [string]
    #|
    #|          The prompt string from which this completion was
    #|          generated, if available. (Otherwise None.)
    #|
    #|      .core [GPT3Core]
    #|
    #|          The connection to the core API that was used to 
    #|          generate this completion, if available.
    #|
    #|      .complStruct [dict]
    #|
    #|          The raw completion data structure returned by 
    #|          the core API.
    #|
    #\--------------------------------------------------------------------------

    #|--------------------------------------------------------------------------
    #| Instance initializer.                        [special instance method]
    #|      
    #|      This takes a general argument list, and parses it to extract
    #|      the text of a prompt and the GPT3Core object that is provided.
    #|      Then are then used to call the underlying API to create the
    #|      actual completion data structure.  (Alternatively, if a 
    #|      structure is already provided, we just remember it.)
    #|
    #|  Usage:
    #|
    #|      compl = Completion(prompt, core)
    #|
    #|          Creates a completion of the given prompt string using 
    #|          the given GPT3Core instance.
    #|
    #|      compl = Completion(complStruct)
    #|
    #|          Creates a completion object wrapping the given 
    #|          completion structure, previously generated.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def __init__(inst, *args, **kwargs):
        
        """Instance initializer for class Completion."""
        
            # These are things we are going to try to find in our arguments,
            # or generate ourselves.
        
        prompt      = None
        core        = None
        complStruct = None
        
            # Scan our positional arguments looking for strings, core objects,
            # or pre-existing compleition structures.
        
        for arg in args:
        
                # If there's a string, add it to our growing prompt.
        
            if isinstance(arg,str):
                if prompt == None:
                    prompt = arg
                else:
                    prompt = prompt + arg

                # If there's a GPT3Core instance, remember it.

            if isinstance(arg,GPT3Core):
                core = arg
        
                # If there's a dict, assume it's a compleition object.
        
            if isinstance(arg,dict):
                complStruct = arg
            
        #__/ End for arg in args.

            # Also check any keyword arguments to see if a prompt, core, 
            # and/or struct are there.  If they are, we'll just override
            # any that were already extracted from positional arguments.

        if 'prompt' in kwargs:
            prompt = kwargs['prompt']
            
        if 'core' in kwargs:
            core = kwargs['core']
            
        if 'struct' in kwargs:
            complStruct = kwargs['struct']
        
            # Remember the prompt and the core that we found, for later use.
        
        inst.prompt = prompt
        inst.core = core
        
            # If we have no completion struct yet, we have to create it by 
            # calling the actual API.  Use an internal instance method for 
            # this purpose.
        
        if complStruct == None and core != None:      
        
                # First generate the argument list for passing to the API.
            apiArgs = core.genArgs(prompt)
            
                # This actually calls the API, with any needed retries.
            complStruct = inst._createComplStruct(apiArgs)
        
        #__/ End if we will generate the completion structure.
        
        inst.complStruct = complStruct      # Remember the compleition structure.
    
    #__/ End of class gpt3.api.Completion's instance initializer.
    
        #|---------------------------------------------------------------
        #| String converter: Just return the value of our .text property.
    
    def __str__(self):
    
        """Converts a Completion instance to a human-readable string."""
        
        return self.text
    
        #|----------------------------------------------------------------------
        #| .text                                      [public instance property]
        #|
        #|      Returns the text of this completion, as a single string.
        #|
        #|      At present, if there are multiple completitions present
        #|      in the completion structure, this only returns the text
        #|      of the first one.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    
    @property
    def text(self):
    
        """Returns the text of this completion, as a single string."""
        
        return ''.join(self.complStruct['choices'][0]['text'])
    
        #|----------------------------------------------------------------------
        #| .nTokens                                   [public instance property]
        #|
        #|      Returns the total number of tokens making up this 
        #|      completion.  For this information to be available, 
        #|      the completion has to have been created using the
        #|      'logprobs=0' parameter setting.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        
    @property   
    def nTokens(self):  # This is only defined if logprobs attribute is present.
    
        """Returns the total number of tokens in this completion."""
    
            # Do some error checking. Really we should be doing 
            # something more sophisticated here.
    
        if self.core != None:
            if self.core.conf.logProbs != 0:
                print("WARNING: .nTokens only works when logprobs=0!")
                
        return len(self.complStruct['choices'][0]['logprobs']['tokens'])

    @property
    def promptLen(self):
    
        """Returns the length of the prompt in tokens."""
        
        if self.prompt == None:
            print("ERROR: .promptLen: Prompt not available.")
            return None
            
        if self.core == None:
            print("ERROR: .promptLen: Core not available.")
            return None
            
        if self.core.conf.echo != True:
            print("ERROR: .promptLen: Echo not set.")
            return None
            
        if self.core.conf.logProbs != 0:
            print("WARNING: .promptLen: Logprobs is not 0.")
            
        resultPos = len(self.prompt)
        resultTokIndex = self.textPosToTokIndex(resultPos)
        return resultTokIndex
        
    @property
    def resultLen(self):
    
        """Returns the length of the result in tokens."""
        
        return self.nTokens - self.promptLen

    def textPosToTokIndex(self, pos:int):
    
        """Given a position in the completion text, returns the index 
            of the token that is at that position."""
            
        text_offsets = self.complStruct['choices'][0]['logprobs']['text_offset']

            # We could make this more efficient by doing a binary
            # search, but it's probably overkill at the moment.
        
        for tok_index in range(0, len(text_offsets)):
            if text_offsets[tok_index] > pos:
                return tok_index-1
                
        return len(text_offsets)-1

        #|----------------------------------------------------------------------
        #| ._createComplStruct(apiArgs)                [private instance method]
        #|
        #|      This internal method is what actually calls the core API
        #|      to retrieve the raw completion data structure.  We use the
        #|      backoff package (pypi.org/project/backoff) to handle retries
        #|      in case of REST failures.
        #|
        #|  Arguments:
        #|
        #|      apiArgs [dict] - API arguments as a single dict structure.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        # This decorator performs automatic exponential backoff on REST failures.
    @backoff.on_exception(backoff.expo,
                          (openai.error.APIError))
                          
    def _createComplStruct(self,apiArgs):
    
        """Private instance method to retrieve a completion from the
            core API, with automatic exponential backoff and retry."""
            
        return openai.Completion.create(**apiArgs)

#__/ End class Completion.

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
    
    #__/ End GPT3Core instance initializer.

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


        # Generate the argument list for calling the core API.
    def genArgs(self, prompt=None):
   
        kwargs = dict() # Empty dict for building up argument list.
        
        conf = self.conf    # Get our current configuration.

        kwargs['engine'] = conf.engineId    # This API arg. is required. Can't skip it.
                
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

        return kwargs

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

    def genCompletion(self, prompt=None):
    
        """With automatic exponential backoff, query the server
                for a completion object for the given prompt using the
                connection's current API configuration."""
        
        return Completion(self, prompt)
            # Calls the Completion constructor with the supplied prompt. This
            # constructor does all the real work of calling the API.
        
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
            
        resultCompletion = genCompletion(prompt)
        return resultCompletion.text

#__/ End class GPT3Core.


#|==============================================================================
#| Module object initialization.                                [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

_theTokenCounterCore = GPT3Core(echo=True, maxTokens=0, logProbs=0)
    # This connection provides functionality needed to count tokens.

#|==============================================================================
#| Module function definitions.                                 [code section]
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def countTokens(text:str=None):
    if text == None or text == "":
        return 0
    else:
            # Please note this is not free! It uses probably 2*text of quota.
        inputComplObj = _theTokenCounterCore.genCompletion(text)
        return inputComplObj.nTokens

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|  END FILE:   gpt3/api.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%