# tokenizer.py

	# A simple decorator for singleton classes.
from infrastructure.decorators	import	singleton

	# Load OpenAI's GPT-2 tokenizer module.
from .encoder 					import 	get_encoder

# Gather our module-level constants and objects into a singleton
# class, because it's simpler & more elegant than using globals.

__all__ = [
	'Tokenizer',	# Singleton class for our tokenizer object.
	'countTokens'	# Utility method to quickly count tokens.
]

@singleton
class Tokenizer:
	"""
		This is a singleton class defining the tokenizer object.
		It provides .textToTokens() and .tokensToText() methods.
	
			USAGE:
			------
		
				from tokenizer.tokenizer import Tokenizer
			
				text = "Mary had a little lamb,"
			
				tokens = Tokenizer().textToTokens(text)
			
					# Reconstitute the original text.
				retext = Tokenizer().tokensToText(tokens)
			
				print(retext)
	"""

		# The below model dir should be built out starting
		# from a clone of https://github.com/openai/gpt-2
	_DEFAULT_MODEL_DIR = '/opt/gpt-2/models'
	
		# The tokenizer for each GPT-2 model is the same;
		# it's sufficient to just download the smallest one.
	_DEFAULT_MODEL_NAME = '124M'

	def __init__(theTokenizer):
		
		# We could do something here to allow overriding the 
		# above defaults using environment variables, or from
		# the GLaDOS system config, but we're lazy.
		
			# Figure out the model directory and name.
		model_dir = theTokenizer._DEFAULT_MODEL_DIR
		model_name = theTokenizer._DEFAULT_MODEL_NAME
		
			# Remember them, just for our records.
		theTokenizer.modelDir 	= model_dir
		theTokenizer.modelName 	= model_name
		
			# Now create our encoder.
		theTokenizer.encoder	= get_encoder(model_name, model_dir)
		
		# That's it! That's all the setup we need to do.
		
	def textToTokens(me, text:str):
		return me.encoder.encode(text)
		
	def tokensToText(me, tokens:list):
		return me.encoder.decode(tokens)

def countTokens(text:str):
	return len(Tokenizer().textToTokens(text))
