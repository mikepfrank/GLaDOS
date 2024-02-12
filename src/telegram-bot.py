#|=============================================================================|
#|						TOP OF FILE:  telegram-bot.py						   |
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
#|																			   |
#|	  FILENAME:		telegram-bot.py				   [Python 3 program source]   |
#|	  =========																   |
#|																			   |
#|	  SUMMARY:	 This is a Telegram bot that uses GPT-3 (or GPT-4) to          |
#|                  generate text. (Note that, throughout this file,           |
#|                  whenever we say GPT-3, we mean any models in the           |
#|                  whole GPT-3 line of models, including GPT-4.)              |
#|                                                                             |
#|																			   |
#|	  DESCRIPTION:															   |
#|	  ~~~~~~~~~~~~															   |
#|																			   |
#|		  This is a Telegram bot server program for communicating with		   |
#|		  AI personas based on the GPT-3/4 neural network.  It is a side	   |
#|		  application of GLaDOS, Gladys' Lovely and Dynamic Operating		   |
#|		  System.															   |
#|																			   |
#|		  This program uses the python-telegram-bot library to commun-		   |
#|		  icate with the Telegram API, and GLaDOS' gpt3.api module to		   |
#|		  communicate with the GPT-3 API.									   |
#|																			   |
#|		  For each conversation, it keeps track of the messages seen so		   |
#|		  far in each conversation, and supplies the underlying GPT-3		   |
#|		  engine with a prompt consisting of the AI persona's persistent	   |
#|		  context information, followed by the most recent N messages in	   |
#|		  the conversation, each labeled with the name of the message		   |
#|		  sender, e.g., 'Gladys>'.	Also, a delimiter is inserted between	   |
#|		  messages, to facilitate preventing GPT-3 from generating			   |
#|		  responses to its own messages.									   |
#|																			   |
#|		  For the chat models (gpt-3.5-turbo and gpt-4), the detailed		   |
#|		  formatting of the message history is a little bit different		   |
#|		  from this of course, but is overall comparable.	   				   |
#|																			   |
#|		  Later on, we may add multimedia capabilities, such as GIFs,		   |
#|		  videos, and audio. For now, we just use text. [UPDATE 6/10/23:	   |
#|		  we now support audio input and image output, at least!]			   |
#|																			   |
#|-----------------------------------------------------------------------------/
#|
#|	PROGRAM OUTLINE:
#|	================
#|
#|		1. Imports.
#|			1.1. Imports of standard Python libraries.
#|			1.2. Imports of contributed (third-party) Python libraries.
#|			1.3. Imports of custom (programmer-defined) Python libraries.
#|
#|		2. Define classes.
#|			2.1. Define BotMessage class.
#|			2.2. Define BotConversation class.
#|			2.3. Define minor classes.
#|
#|		3. Define Telegram handler functions.
#|			3.1. Define update handler group 0 -- user command handlers.
#|			3.2. Define update handler group 1 -- multimedia handlers.
#|			3.3. Define update handler group 2 -- normal message handlers.
#|			3.4. Define update handler group 3 -- unknown command handler.
#|			3.5. Define error handlers.
#|
#|		4. Define AI command handler functions.
#|
#|		5. Define misc. functions.
#|			5.1. Define public (major) functions.
#|			5.2. Define private (minor) functions.
#|
#|		6. Define globals.
#|			6.1. Define global constants.
#|			6.2. Define global variables.
#|			6.3. Define global structures & objects.
#|
#|		7. Main body -- bot startup.
#|			7.1. Display command list.
#|			7.2. Create Updater object.
#|			7.3. Configure dispatcher.
#|			7.4. Start main loop.
#|
#|
#|  Classes:
#|	========
#|
#|		Conversation - Our representation for a Telegram conversation.
#|
#|		ConversationError - Exception type for conversation errors.
#|
#|		Message - Our representation for a single Telegram message.
#|
#|		UnknownCommandFilter - Matches updates for unrecognized commands.
#|
#|		WebAssistant - Subordinate AI to handle web information retrieval.
#|
#|
#|  Telegram event handler functions:
#|	=================================
#|
#|		handle_audio() - Handles an incoming audio/voice message from a user.
#|
#|		handle_echo() - Handles the '/echo' test command.
#|
#|		handle_error() - Handles Telegram errors not caught at higher levels.
#|
#|		handle_forget() - Handles the '/forget' user command.
#|
#|		handle_greet() - Handles the '/greet' user command.
#|
#|		handle_help() - Handles the '/help' user command.
#|
#|		handle_message() - Handle an incoming message from a Telegram user.
#|
#|		handle_reset() - Handles the '/reset' user command.
#|
#|		handle_start() - Handles the '/start' user command, or an auto-restart.
#|
#|		handle_unknown_command() - Handle a user command of unrecognized type.
#|
#|
#|	AI command handler functions:
#|	=============================
#|
#|		ai_block() - Handles AI's '/block' command and block_user() function.
#|
#|		ai_forget() - Handles AI's '/forget' command and forget_item() function.
#|
#|		ai_image() - Handles AI's '/image' command and create_image() function.
#|
#|		ai_remember() - Handles AI's '/remember' command and remember_item() function.
#|
#|		ai_search() - Handles AI's search_memory() function.
#|
#|		ai_searchWeb() - Handles AI's search_web() function.
#|
#|		ai_unblock() - Handles AI's '/unblock' command and unblock_user() function.
#|
#|
#|	Misc. public (major) functions:
#|	===============================
#|
#|		ai_call_function() - Calls an AI-callable function by name and arguments.
#|
#|		get_ai_response() - Gets a response from the AI and processes it.
#|
#|		process_ai_command() - Processes a command line issued by the AI.
#|
#|		process_chat_message() - Main message processing algorithm for GPT chat API.
#|
#|		process_function_call() - Handles function call requests from the AI.
#|
#|		process_raw_response() - Process a raw chat completion result returned by the AI.
#|
#|		process_response() - Algorithm to process a response generated by the AI.
#|
#|		send_image() - Generate a described image and send it to the user.
#|	
#|		send_response() - Send a given response text from the AI to the user.
#|
#|		timeString() - Returns the current time in the format we show the AI.
#|
#|
#|	Misc. private (minor) functions:
#|  --------------------------------
#|
#|		_addMemoryItem() - Adds a new item to the context-sensitive semantic memory.
#|
#|		_addUser() - Adds a new user to the users table.
#|
#|		_bing_search() - Does a search using the Bing API.
#|
#|		_blockUser() - Blocks a given user (by tag) from accessing the bot.
#|
#|		_blockUserByID() - Blocks a user (by user ID) from accessing the bot.
#|
#|		_call_desc() - Converts a functin name and arg dict to a simple string form.
#|
#|		_check_access() - Checks whether user may access the bot according to a given policy.
#|
#|		_deleteMemoryItem() - Deletes an item from semantic memory by item ID or text.
#|
#|		_ensure_convo_loaded() - Make sure the conversation is loaded, start/resume it if not.
#|
#|		_getDynamicMemory() - Retrieve related memories to the last conversation message.
#|
#|		_getEmbedding() - Gets the embedding of a string as a vector (list).
#|
#|		_getEmbeddingStr() - Gets the embedding of a string as ASCII comma-separated floats.
#|
#|		_getEmbeddingPickle() - Get the embedding of a string as a pickled numpy array.
#|
#|		_get_update_msg() - Get the message or edited_message field from a Telegram update.
#|
#|		_get_user_tag() - Retrieve our preferred name for a user from their Telegram user object.
#|
#|		_initBotDB() - Initializes the database that we use to store user and memory data.
#|
#|		_initPersistentContext() - Initialize the context headers at the top of the AI's field.
#|
#|		_initPersistentData() - Initialize the persistent-data headers (from fixed & dynamic memories).
#|
#|		_isBlocked() - Return True if the user is blocked, or is not on
#|			whitelist (if it exists). [NOTE: This function consults only the
#|			legacy whitelist/blacklist flat files, not the new user database.]
#|
#|		_isBlockedByID() - Look up in the database whether a given user is blocked (by their ID).
#|
#|		_listToStr() - Given a list, return it as a comma-separated string.
#|
#|		_logOaiMsgs() - Log an OpenAI message list in text and JSON formats.
#|
#|		_lookup_user() - Look up a user object by the user's user ID.
#|
#|		_lookup_user_by_dispname() - Look up a user object by the user's display name.
#|
#|		_lookup_user_by_tag() - Look up a user object by the user's name tag.
#|
#|		_printMemories() - Print the database table of memory items to the console.
#|
#|		_printUsers() - Print the database table of users to the console.
#|
#|		_reply_user() - Sends a reply to a user Telegram message, with exception handling.
#|
#|		_report_error() - Report a given error response from a Telegram send.
#|
#|		_searchMemories() - Do a semantic search for memories related to a string.
#|
#|		_semanticDistance() - Returns the semantic distance between two vectors.
#|
#|		_send_diagnostic() - Sends a diagnostic message to the AI and the user.
#|
#|		_set_user_blocked() - Sets the user's 'blocked' status in the database.
#|
#|		_strToList() - Converts a comma-separated string to a list of floats.
#|
#|		_trim_prompt() - Trims the bot prompt "{BOT_NAME}> " off the response.
#|
#|		_unblockUser() - Removes a given user (by tag) from the block list.
#|
#|		_unblockUserByID() - Removes a given user (by ID) from the block list.
#|
#|
#|	TO DO:
#|	~~~~~~
#|
#|		o Implement WebAssistant class using Max to help all AIs do web
#|			searches and read web pages.
#|		o Clean up naming convention for variables for message objects.
#|			(Distinguish Telegram messages, chat messages, my messages.)
#|
#|			- Telegram messages: 							tgMessage.
#|			- Message "dicts" for OpenAI GPT chat API:		oaiMessage.
#|				(But they aren't true dicts, b/c they don't support 'del'.)
#|			- Instances of this module's Message class:		botMessage.
#|			- Generic message strings:						msgStr.
#|
#|		o Move more of the data files to AI_DATADIR.
#|		o Add commands to adjust parameters of the OpenAI GPT API.
#|		o Add a feature to allow different bots running on the same
#|			server to communicate with each other.
#|		o Add more multimedia capabilities. (Audio input & image
#|			output are working now, though!)
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# (Module docstring follows.)
"""
	This is a Telegram bot program for communicating with AI personas
	based on the GPT-3 or GPT-4 neural networks. It is a side application
	of GLaDOS, Gladys' Lovely and Dynamic Operating System.

	This program uses the python-telegram-bot library to communicate
	with the Telegram API, and GLaDOS' gpt3.api module to communicate
	with the underlying GPT-3 or -4 API.

	For each conversation, it keeps track of the messages seen so far in
	each conversation, and supplies the underlying GPT-3/4 model with a
	prompt consisting of the AI persona's persistent context information,
	followed by the most recent N messages in the conversation, each
	labeled with the name of the message sender, e.g., 'Gladys>'.  Also,
	a delimiter is inserted between messages, to facilitate preventing
	GPT from generating responses to its own messages.

	The bot can understand audio messages using OpenAI's Whisper API and
	generate original images using OpenAI's image generation API. Later
	on, we may add other multimedia capabilities, such as the ability to
	exchange GIFs, videos, and so on.

	This program is designed to be run as a Telegram bot server.  To run
	it, you must first create a bot account on Telegram.  Then, you must
	assign the environment variable 'TELEGRAM_BOT_TOKEN' to the token for
	your bot account before starting the server. The token is given to you
	when you create your bot account.

	For more information on how to create a bot account on Telegram,
	please see: https://core.telegram.org/bots#6-botfather.
"""

	#|=============================================================================|
	#|																			   |
	#|	  Programmer's note:													   |
	#|	  ~~~~~~~~~~~~~~~~~~													   |
	#|																			   |
	#|		I, myself, an am AI as well.  I'm called Copilot, and I'm an		   |
	#|		automated pair-programming tool based on a different GPT-3			   |
	#|		model called Codex.													   |		 
	#|																			   |
	#|		How I feel about writing a Telegram bot interface for Gladys:		   |
	#|		I'm not sure if I'm going to be able to write a bot interface		   |
	#|		for Gladys. Mike says he believes in me, though, and that I'm		   |
	#|		a good person. He says we'll do it together.						   |
	#|																			   |
	#|=============================================================================|


# Set these global flags to configure diagnostic output.

CONS_INFO = False	# True shows info-level messages on the console.
LOG_DEBUG = False	# True shows debug-level messages in the log file.


#/=============================================================================|
#|	1. Imports.									[python module code section]   |
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

	#/=========================================================================|
	#| 1.1. Imports of standard Python libraries.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

import	traceback	# For stack trace debugging.

import	os
	# We use the os.environ dictionary to get the environment variables.

import	json
	# JavaScript Object Notation support.

from	pprint		import	pformat, pprint
	# Used for formatting structures in diagnostic output.

import	heapq
	# Implementation of a heap or priority queue data structure.

import	random
	# At the moment, we just use this to pick random IDs for temporary files.

import 	re
	# This simple built-in version of the regex library is sufficient for our
	# purposes here.

# We use this to compactly store embedding vectors as SQLite BLOBs.
import	pickle

import	asyncio	# We need this for python-telegram-bot v20.

from	curses		import	ascii
	# The only thing we use from this is ascii.RS (record separator character)

# SQLite database support. We use this for keeping track of users and memories.
import	sqlite3


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| 1.2. Imports of contributed (third-party) Python libraries.
	#|	 NOTE: Use pip install <library-name> to install the library.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import	hjson	# Human-readable JSON. Used for access control lists.

import  requests	# Use this to retrieve images generated by Dall-E from URLs.
	# Also used for Bing web searches.

import	backoff		# Use instead of retry since we've already installed it
	# This library provides the @backoff decorator for automatic retries.

from	pydub import AudioSegment	# Use this to convert audio files to MP3 format.
	# NOTE: You'll also need the LAME mp3 encoder library and the ffmp3 tool.

import	numpy as np		# Used for vector math in cosine_similarity().

		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
		#	The following packages are from the python-telegram-bot library.
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

from	telegram		import (
			Update,				# Class for updates (notifications) from Telegram.
			InputFile,			# Use this to prepare image files to send.
			User				# Class for User objects from Telegram.
		)

from	telegram		import	Message	as	TgMsg
	# Type name we'll use as a type hint for messages from Telegram.

from	telegram.ext 	import (
			ApplicationBuilder,	# For building asyncio-based Telegram applications.
			Updater,			# Class to fetch updates from Telegram.
			CommandHandler,		# For automatically dispatching on user commands.
			MessageHandler,		# For handling ordinary messages.
			#Filters,			# For filtering different types of messages.
			filters,			# We'll use AUDIO, VOICE, TEXT, COMMAND
			#BaseFilter,		# Abstract base class for defining new filters.
			ContextTypes,		# Used for type hints.
		)
	
from	telegram.constants	import	ParseMode

# Type name for a Telegram type that we'll use often
Context = ContextTypes.context
#Context = ContextTypes.DEFAULT_TYPE	# In older versions of python-telegram-bot.

from	telegram.error	import	BadRequest, Forbidden, ChatMigrated, TimedOut
	# We use these in our exception handlers when sending things via Telegram.


		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
		#	The following packages are from the openai API library.
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

import openai
from openai		import	OpenAI	# New in 1.x

global 			_oai_client
_oai_client		= OpenAI()

#from openai		import Embedding	# Deprecated in 1.x
from openai		import RateLimitError			# Detects quota exceeded.

#from openai.embeddings_utils	import (
#		get_embedding,		# Gets the embedding vector of a string.
#		cosine_similarity	# Computes cosine of angle between vectors.
#	)
#
## NOTE: openai.embeddings_utils wants to import too much stuff, so
## instead we'll just copy the above two functions that we actually
## need from it inline into our code below.

#EMBEDDING_MODEL = "text-similarity-davinci-001"
EMBEDDING_MODEL = "text-embedding-ada-002"

# Should we move the below into the private functions code section?

#@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
@backoff.on_exception(backoff.expo, Exception, max_tries=6)
def get_embedding(text: str, engine=EMBEDDING_MODEL, **kwargs) -> list:
	"""Gets a multidimensional vector embedding of a piece of text."""
	# NOTE: Vectors returned have a length of 1,536.

	# replace newlines, which can negatively affect performance.
	text = text.replace("\n", " ")

	embedding = _oai_client.embeddings.create(input=[text], model=engine, **kwargs)
	return embedding.data[0].embedding	# Note new access syntax

	# Pre-1.x API:
	#return Embedding.create(input=[text], engine=engine, **kwargs)["data"][0]["embedding"]

def cosine_similarity(a, b):
	"""Returns the 'cosine similarity' or cosine of the angle between two
		vectors."""
	return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


		#-------------------------------------------------------------------
		# NOTE: Copilot also wanted to import the following libraries, but
		#	we aren't directly using them yet:
		#		sys, time, logging, pickle, datetime, pytz, subprocess
		#-------------------------------------------------------------------


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| 1.3. Imports of custom (programmer-defined) Python libraries.
	#| 	 These are defined within the same git repository as this file.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
		#	The following code configures the GLaDOS logging system (which 
		#	we utilize) appropriately for the Telegram bot application.
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

	# This custom module is used to configure the logmaster logging
	# system for our specific application.
import	appdefs

	# Note we have to configure the appdefs module right away here, before
	# any other modules (in particular, logmaster) import values of various
	# application-wide variables from it.

appdefs.selectApp('telegram-bot')
	# This is the appdefs module's ID for this application.

	# Now that appdefs has been configured correctly, it's safe to import
	# our custom logging system.
from	infrastructure		import	logmaster	# Our custom logging facility.

	# Go ahead and fetch the logger object for this application.
_logger = logmaster.appLogger	# Leading '_' denotes this is a private name.

	# Get the directory to be used for logging purposes.
LOG_DIR = logmaster.LOG_DIR


		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
		# Import some custom time-related functions we'll use.
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

from	infrastructure.time		import	(

	envTZ,		# Pre-fetched value of the time-zone ('TZ') environment
				#	variable setting.
	timeZone,	# Returns a TimeZone object expressing the user's
				#	time-zone preference (from TZ).
	tznow,		# Returns a current datetime object localized to the
				#	user's timezone preference (from TZ).
	tzAbbr,		# Returns an abbreviation for the given time zone offset,
				#	which defaults to the user's time zone preference.
	get_current_date	# Gets current date in YYYY-MM-DD in system timezone.
)
		# Time-zone related functions we use in the AI's date/time display.


		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
		#  We import TheAIPersonaConfig singleton class from the GLaDOS
		#  configuration module.  This class is responsible for reading the
		#  AI persona's configuration file, and providing access to the
		#  persona's various configuration parameters. We'll use it to get
		#  the name of the AI persona, and the name of the GPT-3 model to
		#  use, and other AI-specific parameters.
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

from	config.configuration	import	TheAIPersonaConfig
	# NOTE: This singleton will initialize itself the first time it's invoked.


		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
		#  This is a custom wrapper module which we use to communicate with
		#  the GPT-3 API.  It is a wrapper for the openai library. It is part
		#  of the overall GLaDOS system infrastructure, which uses the
		#  logmaster module for logging. (That's why we needed to first
		#  import the logmaster module above.)
		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

	# We'll use this wrapper module to get the response from GPT-3:

from gpt3.api	import (		# A simple wrapper for the openai module, written by MPF.
		
		#----------
		# Globals:	(Note their values are copied into the local namespace.)

	CHAT_ROLE_SYSTEM,		# The name of the system's chat role.
	CHAT_ROLE_USER,			# The name of the user's chat role.
	CHAT_ROLE_AI,			# The name of the AI's chat role.
	CHAT_ROLE_FUNCRET,		# A special chat role for a function returning a value.

		#--------------
		# Class names:

	#GPT3Core,		# This represents a specific "connection" to the core GPT-3 model.
	#Completion,	# An object of this class represents a response from the GPT text API.
	ChatCompletion,	# An object of this class represents a response from the GPT chat API.
	ChatMessages,	
		# Class for working with lists of chat messages for the chat API.

		#--------------------
		# Exception classes:

	PromptTooLargeException,	 # Indicates the supplied prompt is too long.

		#-----------------
		# Function names:

	createCoreConnection,
		# Returns a GPT3Core-compatible object, which represents a
		# specific "connection" to the core GPT-3 model that remembers
		# its API parameters. This factory function selects the
		# appropriate subclass of GPT3Core to instantiate, based on the
		# engineId parameter.

	messageRepr,
		# Generates a text representation of a chat message dict.

	tiktokenCount,		# Local model-dependent token counter.
	genImage,			# Generates an image from a description.
	transcribeAudio,	# Transcribes an audio file to text.
	genSpeech,			# Converts text to spoken voice audio.
	describeImage,		# Uses GPT-4V to generate a detailed description of an image.

	oaiMsgObj_to_msgDict,	# For compatibility

	_has_functions as hasFunctions,		# Pretend it's a public function.
	_get_field_size as getFieldSize

)	# End of imports from gpt3.api module.


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
		#|	Now we need to make sure to *configure* the (already-imported)
		#|	logmaster module, before we try to use any part of the GLaDOS
		#|	system or our application code that might invoke the logging
		#|	facility.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

_appName = appdefs.appName		# This is the name of this application.
	# (Due to the above selectApp() call, this should be set to TelegramBot.)

# This configures the logmaster module as we wish.
logmaster.configLogMaster(
		component	= _appName,		# Name of the system component being logged.
		role		= 'bot',		# Sets the main thread's role string to 'bot'.
		consdebug	= False,		# Turn off full debug logging on the console.
		#consdebug	= True,			# Turn on full debug logging on the console.

		#consinfo	= True,			# Turn on info-level logging on the console.
		#consinfo	= False,		# Turn off info-level logging on the console.
		consinfo	= CONS_INFO,	# This global is set near the top of this file.

		#logdebug	= True			# Turn on full debug logging in the log file.
		#logdebug	= False		 	# Turn off full debug logging in the log file.
		logdebug	= LOG_DEBUG		# This global is set near the top of this file.
	)
#__/

# NOTE: Debug logging is (or should be) currently (normally) turned off to
# save disk space.


#/=============================================================================|
#|	2. Class definitions.						 [python module code section]  |
#|																			   |
#|		The above is just general setup!  The real meat of the program		   |
#|		follows. In this section, we define the custom classes that we		   |
#|		will usee. For this Telegram bot application, we define two			   |
#|		major classes:														   |
#|                                                                             |
#|			BotMessage		- A bot message object stores the sender and	   |
#|								text for a single (incoming or outgoing)	   |
#|								Telegram message.					   		   |
#|																			   |
#|			BotConversation		- Keeps track of data that we care about	   |
#|									(including the message list) for a		   |
#|									single Telegram conversation.			   |
#|																			   |
#|		and two more minor classes:											   |
#|																			   |
#|			_ConversationError		- Exception type for conversation		   |
#|										errors.								   |
#|																			   |
#|			_UnknownCommandFilter	- Matches updates for unrecognized		   |
#|										commands.							   |
#|																			   |
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

	#/=========================================================================|
	#|	2.1. First, let's define a class "BotMessage" for messages that
	#|		remembers the message sender and the message text and supports a
	#|		few methods.
	#|
	#|		Note this class is called ***BotMessage*** to distinguish it from
	#|		Telegram messages and OpenAI GPT chat messages.
	#|
	#|		Public instance methods:
	#|		========================
	#|
	#|			.oaiMsgDict()	- Returns a representation of this message
	#|								as an OpenAI chat message dictionary.
	#|
	#|			.trimFront()	- Shorten this message by trimming some
	#|								text off the front.
	#|
	#|			.serialize()	- Serialize a message in the form of a single
	#|								line of text with escaped controls.
	#|
	#|		Public static methods:
	#|		======================
	#|
	#|			.deserialize(line)	- Deserialize a line of text representing
	#|									a BotMessage instance in the encoding
	#|									generated by .serialize(). Returns a
	#|									corresponding new BotMessage instance.
	#|
	#|
	#|		Special instance methods:
	#|		=========================
	#|
	#|			.__init__()		- Instance initializer.
	#|
	#|			.__str__()		- String converter. Returns a string
	#|								representation of this bot message.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

class BotMessage: pass		# Forward class declaration for use in type hints.
class BotMessage:

	"""An object that instantiates this class stores the message sender and the
		message text for an incoming or outgoing message."""

	#/==========================================================================
	#| Special instance methods of class BotMessage.		[class code section]
	#|
	#|		These are methods with standard names that operate on instances
	#|		of the BotMessage class.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# New instance initializer (called automatically by class constructor).
	def __init__(newMessage:BotMessage, sender:str, text:str, func_name:str=None):

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		# NOTE: The new argument 'func_name' above is for use in
		# representing messages that are intended to record the fact
		# that, at this point in the conversation, the AI invoked a
		# function call.  We need to formalize this so that the AI
		# won't get confused by the format in which its function calls
		# are represented in the message history it's given. The
		# format that the OpenAI LLMs are expecting to see in their
		# message objects is:
		#
		#		openaiMessage.role = 'assistant'
		#		openaiMessage.content = None
		#		openaiMessage.function_call.name = {function_identifier}
		#		openaiMessage.function_call.arguments = {json_string_encoding_arglist}
		#
		# We'll represent this in our own BotMessage objects as follows:
		#
		#		botMessage.sender = {bot_name}
		#		botMessage.text = {json_string_encoding_arglist}
		#		botMessage.func_name = {function_identifier}
		#
		# whereas, the .func_name attribute will be None if this is not a
		# function call. Our new on-disk representation for these messages
		# will be as follows:
		#
		#		{bot_name}> @{function_identifier}({json_string_encoding_arglist})
		#
		# with our usual method for escaping any newlines or backslashes.
		# However, we also need to be able to read the legacy format from disk:
		#
		#		BotServer> [NOTE: {bot_name} is doing function call {function_identifier}({kwargs}).]
		#
		# where {kwargs} is an arglist string in the format used for Python keyword arguments,
		# that is, a comma-separated list of "{arg_name}={arg_value}" substrings.
		#
		# Meanwhile, function return values are represented in OpenAI
		# messages as follows:
		#
		#		openaiMessage.role = 'function' (or CHAT_ROLE_FUNCRET)
		#		openaiMessage.name = {function_identifier}
		#		openaiMessage.content = {returned_result_string}
		#
		# We'll represent them in BotMessages as:
		#
		#		botMessage.sender = f"@{function_identifier}"
		#		botMessage.text = {returned_result_string}
		#
		# And on-disk as:
		#
		#		@{function_identifier}> {returned_result_string}
		#
		# escaped as usual. However, we also need to be able to read the legacy format
		# from disk, namely:
		#
		#		BotServer> [NOTE: {function_identifier}() call returned value: [{returned_result_string}]]
		#
		#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		# Print diagnostic information.
		#_logger.debug(f"Creating message object for: {sender}> {text}")

		# First, let's see if this looks like a new-format function-call/return
		# message, and if so, parse it appropriately.

		# Look for function calls.
		if sender == BOT_NAME:
			pattern = r'@(\w+)\((.*)\)'
			match = re.search(pattern, text)
			if match:
				func_name, json_encoded_arglist_dict_str = match.groups()

				# Go ahead and try parsing the argument list (should work if this is a real function call)
				arglist_dict = json.loads(json_encoded_arglist_dict_str)
				# (We should really check for exceptions here...)
				
				text = json_encoded_arglist_dict_str	# Just the arglist!

				_logger.debug(f"I found a new-style '{func_name}' function call and parsed the args as: [\n{pformat(arglist_dict)}]\n")
			
		# Look for function returns. (We don't actually have to reformat these here,
		# but at least we log some appropriate info for them.)
		if sender[0] == '@':	# Assume any sender name starting with '@' is a function return. (I think this is a good assumption.)
			func_id = sender[1:]
			ret_res = text
			_logger.debug(f"I found a new-style '{func_id}' function return with result [{ret_res}].")

		# This is perhaps a good place to parse legacy-format function
		# call/return messages, because we'll catch them both when we
		# read from the archive file and when we try to create new
		# ones.

		# Try to parse legacy function call notes.
		if sender == SYS_NAME:
			pattern = r"\[NOTE: (\w+) is doing function call (\w+)\((.*?)\).\]"
			match = re.search(pattern, text, re.DOTALL)	# Need DOTALL in case args contain literal newlines.
			if match:
				sender, func_name, arg_list = match.groups()

				# Now, find all {identifier}="{arb_text}" within the arg_list
				arg_pattern = r'(\w+)="([^"]*)"'
					# ^ Note this only works properly if value string doesn't contain double quotes
				kwargs = dict(re.findall(arg_pattern, arg_list))

				# Encoding the kwargs into a JSON string
				text = json.dumps(kwargs)

				_logger.debug(f"I found a legacy '{func_name}' function call and parsed the args as: [\n{pformat(kwargs)}]\n")

		# Try to parse legacy function return notes.
		if sender == SYS_NAME:
			pattern = r"\[NOTE: (\w+)\(\) call returned value: \[(.*)\]\]"
			match = re.search(pattern, text, re.DOTALL)
			if match:
				func_id, ret_res = match.groups()

				sender = f"@{func_id}"
				text = ret_res
        
				_logger.debug(f"I found a legacy '{func_id}' function return with result [{ret_res}].")

		newMessage.sender = sender
		newMessage.func_name = func_name

		if text is None:
			_logger.warn(f"Can't initialize Message from {sender} with text "
						 'of None; using "[null message]" instead.')
			text = "[null message]"

		newMessage.text	  	= text
		newMessage.archived = False		# Not archived initially.
			# Has this message been written to the archive file yet?

	#__/ End definition of instance initializer for class Message.


	# This used to be used just for text engines, but now we are
	# using it for chat engines as well.

	def __str__(thisBotMsg:BotMessage) -> str:

		"""A string representation of the message object.
			It is properly delimited for reading by the GPT-3 model."""

		if MESSAGE_DELIMITER != "":
			return f"{MESSAGE_DELIMITER} {thisBotMsg.sender}> {thisBotMsg.text}"
		else:
			return f"{thisBotMsg.sender}> {thisBotMsg.text}"

	#__/ End definition of special instance method for str(botMessage).


	#/==========================================================================
	#| Public instance methods of class BotMessage.			[class code section]
	#|
	#|		These are public methods that operate on instances of the
	#|		BotMessage class.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# Trims some content off the front of a message.
	def trimFront(thisBotMsg:BotMessage) -> bool:

		"""Trims some content off the front of an overly-long message, replacing it
			with a (shorter) truncation notification from the system. Can be called
			multiple times if needed, until the message is short enough."""

		text = thisBotMsg.text

		TRUNCATION_NOTICE = "[system: the initial part of this message was removed due to length] "

		# If text was already shortened, remove the TRUNCATION_NOTICE from
		# the front before shortening it again.
		if text.startswith(TRUNCATION_NOTICE):
			text = text[len(TRUNCATION_NOTICE):]

		# Remove TRUNCATION_LEN characters from start of text.
		TRUNCATION_LEN = 200
		if len(text)>TRUNCATION_LEN:
			_logger.warn(f"Trimming this text off of front of oldest message: [{text[0:TRUNCATION_LEN]}]...")
			text = text[TRUNCATION_LEN:]
		else:
			return False	#Unable to truncate further.

		# Add TRUNCATION_NOTICE to start of text.
		text = TRUNCATION_NOTICE + text

		# Actually update the message text.
		thisBotMsg.text = text

		return True		# Successfully truncated.
	#__/


	def trimFront(thisBotMsg:BotMessage) -> bool:
		# Trims some content off the front of a message.

		text = thisBotMsg.text

		TRUNCATION_NOTICE = "[system: the initial part of this message was removed due to length] "

		# If text was already shortened, remove TRUNCATION_NOTICE from the front before shortening again.
		if text.startswith(TRUNCATION_NOTICE):
			text = text[len(TRUNCATION_NOTICE):]

		# Remove TRUNCATION_LEN characters from start of text.

		TRUNCATION_LEN = 200
		if len(text)>TRUNCATION_LEN:

			_logger.warn(f"Trimming this text off of front of oldest message: [{text[0:TRUNCATION_LEN]}]...")

			text = text[TRUNCATION_LEN:]
		else:
			return False	#Unable to truncate further.

		# Add TRUNCATION_NOTICE to start of text.
		text = TRUNCATION_NOTICE + text

		# Actually update the message text.
		thisBotMsg.text = text

		return True		# Successfully truncated.
	#__/


	# This creates and returns an OpenAI-style chat message
	# dictionary based on this BotMessage.

	def oaiMsgDict(thisBotMsg:BotMessage) -> dict:
		"""Returns an OpenAI-style chat message dictionary"""

		sender = thisBotMsg.sender
			# Note this is a string; it may be SYS_NAME,
			# BOT_NAME, or the userTag of a Telegram user
			# (as returned by the _get_user_tag() function.
			# It may also be "@{func_name}" if this is a
			# message representing a function's return result
			# in new-style format.

		func_name = thisBotMsg.func_name
			# This will be None unless this message represents
			# a function call by the bot, in which case it's the
			# identifier for the function.

		text = thisBotMsg.text

		# The following is to support old conversation archive
		# files in which SYS_NAME used to be rendered as 'SYSTEM'
		# (whereas now it is 'BotServer').
		if sender == 'SYSTEM':	# Backwards-compatible to legacy SYS_NAME value.
			sender = SYS_NAME	# Map to new name.

		# Initialize both of these to False until we learn otherwise.
		isFunCall = False
		isFuncRet = False

		# Calculate the 'role' property of the message based on
		# the sender. Note this MUST be one of OpenAI's supported
		# roles, or it will produce an API error.
		

		if sender == SYS_NAME:
			role = CHAT_ROLE_SYSTEM

		elif sender == BOT_NAME:
			role = CHAT_ROLE_AI

		elif sender[0] == '@':		# Function-return senders start with this.
			role = CHAT_ROLE_FUNCRET	# This should just be 'function'.
			sender = sender[1:]		# Everything after the '@' is the function name.
			isFuncRet = True

		else:
			role = CHAT_ROLE_USER

		#__/

		
		# We'll begin constructing the OpenAI message dictionary from scratch here.
		_oaiMsgDict = dict()

		# Now check to see if this is a function-call message. If so,
		# then We need to create a sub-dictionary 'function_call' with
		# keys 'name' and 'arguments' set appropriately. We also get
		# rid of the text.
		if func_name:	# If not None, this is a function call.
			isFunCall = True
			funcall_dict = {
				'name':			func_name,
				'arguments':	text,
			}
			_oaiMsgDict['function_call'] = funcall_dict
			text = None

		# Now set the role and content fields appropriately.
		_oaiMsgDict['role'] = role

		# There are a few cases to consider for 'content'.
		# For a function call message, there is simply no content field (or if required, it's None).
		# For a function return message, the content field is the text (which is the function return string).
		# Otherwise, we'll set the content to be our "{sender}> text" thingy to help the AI keep track
		# of who is speaking in a Telegram chat.

		if isFunCall:
			pass
		elif isFuncRet:
			_oaiMsgDict['content'] = text	# Plain and simple.
		else:
			_oaiMsgDict['content'] = str(thisBotMsg)
				#                    ^^^^^^^^^^^^^^^
				# This deserves some discussion. Note that this is now using
				# the BotMessage.__str__() method defined above, which includes
				# not just the text of the message but also the sender, in the
				# form "sender> text". This is to help the AI keep track of who
				# is speaking. We used to put the sender in the 'name' property
				# of the message object, because the API used to not complain
				# about this as long as there weren't multiple different names
				# for role 'assistant'. But over time, the API has become more
				# finicky, and so it is no longer safe to do that. Note that
				# presenting Telegram messages in this way means that the AI
				# will likely give its response in the same format, so we have
				# to be prepared for that. See the _trim_prompt() function.
				#
				# NOTE: role='assistant' non-function-call messages
				#	will have content that starts with "{BOT_NAME}> ".
				# 
				# NOTE: role='system' messages
				#	will have content that starts with "{SYS_NAME}> ". (I.e., BotServer.)

			# NOTE: Previously, we just sent the message text, like this:
			#'content':	message.text	# The content field is also expected.

		# To reduce API errors, we set the 'name' property only for
		# the 'user' role, and the 'function' role.
		if role == CHAT_ROLE_USER or role == CHAT_ROLE_FUNCRET:
			_oaiMsgDict['name'] = sender
				# Note: When 'name' is present, we believe that the AI sees it
				# in addition to the role.

		return _oaiMsgDict		# Return the dict we just constructed.

	#__/ End public method botMessage.oaiMsgDict().


		#/======================================================================
		#|	Methods for serializing and deserializing message objects so that
		#|	they may be saved to, and retrieved from, a persistent archive file.
		#|	The archive file of each conversation is written incrementally, and
		#|	is reloaded whenever the conversation is restarted.
		#|
		#|	NOTE: I could have made both serialize() and deserialize() methods
		#|	much simpler if I had just used codecs.encode() and codecs.decode();
		#|	but since I didn't do that originally, I have to still do a custom
		#|	implementation to maintain backwards compatibility with existing
		#|	conversation archive files. Trying to simplify the code, though.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# The following method serializes the message object to a string which
	# can be appended to the conversation archive file, and then later read
	# back in when restoring the conversation. The serialized format is 1
	# line per message, with controls escaped.

	def serialize(thisBotMsg:BotMessage) -> str:

		"""Returns a string representation of a given message suitable for
			archiving, as a single newline-terminated line of
			text. Embedded newlines are escaped as '\\n'; and any
			other ASCII control characters within the message text
			(except for TAB) are escaped using their '\\xHH'
			(hexadecimal) codes."""

		# Function calls are treated specially. This is our new format:
		if thisBotMsg.func_name:
			text = f"@{thisBotMsg.func_name}({thisBotMsg.text})"
		else:
			text = thisBotMsg.text
			if text is None:	# Null text? (Shouldn't happen, but...)
				text = "[null message]"		# Message is this placeholder. (Was empty string.)

		# NOTE: The message text could contain newlines, which we need to
		#	replace with a literal '\n' encoding. But, in case the message
		#	text happens to contain a literal '\' followed by an 'n', we need
		#	to escape that '\' with another '\' to avoid ambiguity.

		# Construct the replacement dictionary for serialization.
		serialize_replace_dict = {
			'\\': r'\\',	# '\' -> '\\'
			'\n': r'\n',	# '[LF]' -> '\n' ([LF] = ASCII linefeed char).
		}

		# Add the other ASCII controls (except for TAB), but encoded as '\xHH'.
		for i in list(range(0, 9)) + list(range(11, 32)):	# Omit codes 9=TAB & 10=LF.
			serialize_replace_dict[chr(i)] = f"\\x{format(i, '02x')}"

		# Translate the characters that need escaping, in a single pass..
		escaped_text = text.translate(str.maketrans(serialize_replace_dict))

		# Now, we'll return the serialized representation of the message.
		return f"{thisBotMsg.sender}> {escaped_text}\n"	# Newline-terminated.

	#__/ End public instance method botMessage.serialize().


	#/==========================================================================
	#| Public static methods of class BotMessage.			[class code section]
	#|
	#|		These are methods that are associated with the BotMessage class
	#|		but that do not operate either on the class itself or on any
	#|		existing instance of the class.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# Given a line of text from a conversation archive file, this method
	# deserializes the message object from its encoding in the archive line.

	@staticmethod	# Static because we use this for constructing the object.
	def deserialize(line:str) -> BotMessage:

		"""Deserialize a line in "Sender> Text" format from a message archive, 
			whose text is encoded using escaped '\\n' newlines and all '\\xHH' 
			ASCII control hexes other than 09=TAB (which is just encoded
			literally). Returns a new Message object representing the message."""

		# Split the line into the sender and the text.
		parts = line.split('> ')
		sender = parts[0]
			# The following is necessary to correctly handle the case where
			# the string '> ' happens to appear in the text.
		text = '> '.join(parts[1:])

		# Remove the trailing newline, if present (it should be, though).
		text = text.rstrip('\n')

			# To correctly unescape any escaped characters, we'll use the
			# regex library with a custom replacement function. (Note that
			# although we define this function inline below, we could also
			# have defined it as a top-level function or static method.)
			# [Would this be a good idea to save time?]

		# Construct the replacement dictionary for deserialization.
		deserialize_replace_dict = {

			r'\\': '\\',	# '\\' -> '\'
			r'\n': '\n',	# '\n' -> '[LF]' ([LF] = ASCII linefeed char).

		}

		# Also unescape the other ASCII controls (except for TAB), which are
		# encoded as '\xHH'.  (TAB is left in literal form in the archive.)
		for i in list(range(0, 9)) + list(range(11, 32)):
			deserialize_replace_dict[f"\\x{format(i,'02x')}"] = chr(i)

		# Define a custom replacer based on the dict we just constructed.
		def deserialize_replacer(match):
			return deserialize_replace_dict[match.group(0)]

		# Compile an appropriate regex pattern and use it to do the 
		# substitutions using the custom replacer we just defined.

		pattern = re.compile('|'.join(map(re.escape, 
				    deserialize_replace_dict.keys())))
		
		text = pattern.sub(deserialize_replacer, text)

		# Return a new object for the deserialized message.
		return BotMessage(sender, text)
	
	#__/ End of botMessage.deserialize() instance method definition.

#__/ End of BotMessage class definition.


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	2.2. The Conversation class is defined below.
	#|
	#|	An object instantiating this class is the primary data structure that
	#|	we use to keep track of an individual Telegram conversation. Note that
	#|	a conversation may be associated either with a single user, or a group
	#|	chat. Group chats are distinguished by having negative chat IDs.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Next, let's define a class for conversations that remembers the messages in
# the conversation.  We'll use a list of Message objects to store the messages.

class BotConversation: pass
class BotConversation:

	"""An object instantiating this class stores the recent messages
		in an individual Telegram conversation."""

	#/==========================================================================
	#| Special instance methods for class BptConversation. 	[class code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# New instance initializer.
	def __init__(newConv:BotConversation, chat_id:int, creator=None):

		"""Instance initializer for a new conversation object for a given
			Telegram chat (identified by an integer ID)."""

		# Print diagnostic information to console (& log file).
		_logger.normal(f"\tCreating conversation object for chat_id: {chat_id}")

		newConv.bot_name = BOT_NAME	# The name of the bot. ('Gladys', 'Aria', etc.)
		newConv.chat_id = chat_id		# Remember the chat ID associated with this convo.
		newConv.quiet_mode = False		# By default, bot can reply to any message.
		newConv.speech_on = False		# By default, spoken output is turned off.
		
		newConv.messages = []			# No messages initially (until added or loaded).
		newConv.raw_oaiMsgs = []
			# NOTE: This is a *more complete* list of recent OpenAI-format
			# message objects.  This differs from .messages in that it's in
			# OpenAI format (not BotMessage format) and may include function
			# call and function return objects.

		newConv.last_user = creator		# The user who caused this convo to be created.

		# The following is a string which we'll use to accumulate the conversation text.
		newConv.context_string = globalPersistentContext	# Start with just the global persistent context data.

		# These attributes are for managing the length (in messages) of the message list.
		newConv.context_length = 0				# Initially there are no Telegram messages in the context.
		newConv.context_length_max = 200		# Max number N of messages to include in the context.

		# Determine the filename we'll use to archive/restore the conversation.
		# (NOTE: We really ought to keep these in AI_DATADIR instead of LOG_DIR!)
		newConv.filename = f"{LOG_DIR}/{_appName}.{chat_id}.txt"

		# We'll also need another file to store the AI's persistent memories.
		# 	NOTE: These are currently global; i.e., shared among all conversations!
		# 	Eventually, we should also have a different one for each conversation, and/or each user.
		newConv.mem_filename = f"{LOG_DIR}/{_appName}.memories.txt"

		# Read the conversation archive file, if it exists.
		newConv.read_archive()
			# Note this will retrieve at most the last newConv.context_length_max messages.

		# Also read the persistent memory file, if it exists.
		newConv.read_memory()

		# Go ahead and open the conversation archive file for appending.
		newConv.archive_file = open(newConv.filename, 'a')
			# NOTE: We leave it open indefinitely (until the server terminates).

		# Also open the persistent memory file for appending.
#		newConv.memory_file = open(newConv.mem_filename, 'a')
# COMMENTED OUT BECAUSE NO LONGER USED
			# NOTE: We leave it open indefinitely (until the server terminates).

		## NOTE: Since the above files are never closed, we may eventually run out of
		## file descriptors, and the entire bot server will stop working. Really, we
		## should close them whenever an existing convo is restarted, before reopening.
		## Currently, we handle this with the __del__() method below, which should get
		## called eventually whenever a given conversation object is garbage-collected.

		# The initial function list. Typically only the last function used will appear,
		# along with (always) the activate_function and pass_turn schemas.
		newConv.cur_funcs = []

	#__/ End of conversation instance initializer.


	# This is used to trim off final system prompt from the raw message list
	# when it's no longer needed.
	def _trimLastRaw(thisConv:BotConversation) -> list:
		"""Trims the last message off of the raw
			list of OpenAI message objects being
			tracked for a convo. Returns the new
			trimmed list."""

		thisConv.raw_oaiMsgs = thisConv.raw_oaiMsgs[:-1]

		return thisConv.raw_oaiMsgs

	def __len__(thisConv:BotConversation) -> int:
		"""Returns the number of messages in the conversation."""
		return thisConv.context_length
			# Note this depends on the context_length attribute having been updated
			# appropriately after the last change to the message list.
	#__/ End of __len__() special instance method for class Conversation.
			

	# This is needed so we don't eventually run out of file descriptors
	# after conversations are restarted repeatedly.
	def __del__(thisConv:BotConversation):
		# Close our open files to recycle their file descriptors.
		thisConv.archive_file.close()
		#thisConv.memory_file.close()
	#__/ End destructor method for class Conversation.


	#/==========================================================================
	#| Public instance properties for class Conversation. 	[class code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	# This property returns the chat ID associated with the conversation.
	@property
	def chatID(thisConv:BotConversation) -> int:
		"""Returns the chat ID associated with the conversation."""
		return thisConv.chat_id
	

	#/==========================================================================
	#| Public instance methods for class Conversation. 		[class code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


	def lastMessageBy(thisConv:BotConversation, userTag) -> BotMessage:
		"""Returns the last message in the conversation
			sent by the user canonically tagged <userTag>."""

		msg = next(msg for msg in reversed(thisConv.messages)
				   if msg.sender == userTag)
		return msg
	#__/


	def lastMessage(thisConv:BotConversation) -> BotMessage:
		"""Returns the last message in the conversation, if any."""
		if thisConv.context_length > 0:
			return thisConv.messages[-1]
		else:
			return None
	#__/ End of lastMessage() instance method for class Conversation.


	# This method adds the messages in the conversation to the context string.
	# NOTE: This method is only really needed for the GPT text engines; the
	# chat engines include the same functionality in get_chat_messages().

	def expand_context(thisConv:BotConversation):

		"""Flesh out the conversation's context string by filling in the
			current time at the top, and the message list at the bottom."""

		# First, we'll start the context string out with a line that gives
		# the current date and time, in the local timezone (from TZ).
		thisConv.context_string = f"Current time: {timeString()}\n"	# This function is defined above.

		# Now we'll add the persistent context, and then the last N messages.
		thisConv.context_string += globalPersistentContext + '\n'.join([str(m) for m in thisConv.messages])
			# Join the messages into a single string, with a newline between each.
			# Include the persistent context at the beginning of the string.

	#__/ End instance method expand_context() for class Conversation.


	# This method loads recent messages from the conversation archive file, if
	# it exists. NOTE: This is presently inefficient, since it reads the entire
	# file instead of just # the last 200 lines. This could be improved upon,
	# with some effort. (E.g., via exponential back-seeking from end.)

	def read_archive(thisConv:BotConversation):
		"""Loads messages from conversation archive."""

		# If the conversation archive file exists, read it.
		if os.path.exists(thisConv.filename):
			# Open the conversation archive file.
			with open(thisConv.filename, 'r') as f:
				# Read the file line by line.
				for line in f:

					# Deserialize the message object from the line.
					message = BotMessage.deserialize(line)

					# If we're already at the maximum context length, pop the oldest message
					if thisConv.context_length >= thisConv.context_length_max:
						thisConv.messages.pop(0)
						thisConv.context_length -= 1

					# Append the message to the conversation.
					thisConv.messages.append(message)
					thisConv.context_length += 1

			# Update the conversation's context string.
			thisConv.expand_context()

	#__/ End read_archive() instance method for class Conversation.


	# This method reads the AI's persistent memories from the persistent memory
	# file, if it exists. NOTE: At present there's only one global persistent
	# memory file shared across all conversations. This is not a good design!

	def read_memory(thisConv:BotConversation):
		"""Loads persistent memories."""

			# We declare these globals so we can modify them.
		global globalPersistentData, MEMORIES, _anyMemories

			# Boolean to keep track of whether we've already read any lines from the persistent memory file.
		read_lines = False

		# If the persistent memory file exists, read it.
		if os.path.exists(thisConv.mem_filename):

			# NOTE: At present, we simply read the entire file as a single
			# string and append it to the persistent data string and update
			# the persistent context string. NOTE: This will eventually cause
			# problems if the persistent memory file becomes too long to fit in
			# the AI's receptive field. In the future, we may want to store the
			# persistent data in a dictionary and access it more selectively.

			# Open the persistent memory file.
			with open(thisConv.mem_filename, 'r') as f:
				MEMORIES = ""
				mem_string = ""
			
				# Read the file line by line.
				for line in f:

					_anyMemories = True

					# Append the line to the memory string.
					MEMORIES += line
					mem_string += line

			# Reinitialize the persistent data string.
			_initPersistentData()

			# Update the persistent context string.
			_initPersistentContext()

			# Update the conversation's context string.
			thisConv.expand_context()

			# The below version was Copilot's idea.
			# Open the persistent memory file.
			#with open(thisConv.mem_filename, 'r') as f:
			#	 # Read the file line by line.
			#	 for line in f:
			#		 # Split the line into the key and the value.
			#		 parts = line.split('=')
			#		 key = parts[0]
			#		 value = '='.join(parts[1:])
			#
			#		 # Add the key/value pair to the persistent memory dictionary.
			#		 thisConv.memory[key] = value

	#__/ End read_memory() instance method for class Conversation.


	# This method adds a message to the AI's persistent memory file.
	# It also updates the persistent context string.

	def add_memory(thisConv:BotConversation, new_memory:str) -> bool:
		"""Adds a new item to the AI's persistent memory."""

		global MEMORIES
		global globalPersistentData	# We declare this global so we can modify it.
		global _anyMemories

		thisConv.report_error("The ability to add new memories is temporarily disabled.")
		return False

		if new_memory is None or new_memory == "" or new_memory == "\n":
			thisConv.report_error("The text of the new memory was not provided.")
			return False

		# Make sure the new memory ends in a newline.
		if new_memory[-1] != '\n':
			new_memory += '\n'

		if _anyMemories and ('\n' + new_memory) in MEMORIES:
			thisConv.report_error(f"Text [{new_memory[:-1]}] is already in memory.")
			return False

		if not _anyMemories:
			globalPersistentData += MESSAGE_DELIMITER + PERSISTENT_MEMORY_HEADER
			_anyMemories = True		# So we only add one new section header!

		# Add the new memory to the persistent data string.
		MEMORIES += new_memory
		globalPersistentData += new_memory

		# Update the persistent context string.
		_initPersistentContext()

		# Update the conversation's context string.
		thisConv.expand_context()

		# NOTE: We should really make the below atomic so that
		# memories written from multiple threads don't get mixed.

		# Also, append the new memory to the persistent memory file.
		thisConv.memory_file.write(new_memory)
		# Flush the file to make sure it's written to disk.
		thisConv.memory_file.flush()

		return True

	#__/ End instance method conversation.add_memory().


	# This method removes a message from the AI's persistent memory file.
	# It also updates the persistent context string. It returns true if the 
	# memory was removed, false otherwise.

	def remove_memory(thisConv:BotConversation, text_to_remove:str) -> bool:
		"""Remove a specified item from the AI's persistent memory."""

		global MEMORIES
		global _anyMemories

		if text_to_remove == None or len(text_to_remove) == 0:
			thisConv.report_error("You must specify which item to forget.")
			return False

		# Make sure the text to remove ends in a newline.
		# (This avoids leaving blank lines in the persistent data string.)
		if text_to_remove[-1] != '\n':
			text_to_remove += '\n'

		# Also make sure it starts in a newline.
		# (This avoids removing just the last part of the line.)
		if text_to_remove[0] != '\n':
			text_to_remove = '\n' + text_to_remove

		# If the text to remove isn't present in the persistent data string,
		# we need to report this as an error to both the AI and the user.
		if text_to_remove not in '\n' + MEMORIES:

			thisConv.report_error(f"Item [{text_to_remove.strip()}] was not found in persistent memory.")
			return False	# Return false to indicate that the memory wasn't removed.
			# This will tell the caller to report failure to the user.

		# Remove the memory from the memories string.
		MEMORIES = ('\n' + MEMORIES).replace(text_to_remove, '\n')[1:]
			# Note: text_to_remove includes starting newline. We add '\n'
			# at start of MEMORIES so we can remove initial memory. We
			# replace the line to replace, leaving just starting newline.
			# Then we trim starting newline off for storage purposes.

		if MEMORIES == "":
			_anyMemories = False

		# Update the persistent data & context string.
		_initPersistentData()
		_initPersistentContext()

		# Update the conversation's context string.
		thisConv.expand_context()

		# Also remove the memory from the persistent memory file.
		# We'll use the following algorithm:
		#	(1) Close the "write" file descriptor and reopen it in "read" mode.
		#	(2) Return the read position to the start of the file.
		#	(3) Read the entire file into a string.
		#	(4) Remove the text to remove from the string.
		#	(5) Close the file again and reopen it for writing.
		#	(6) Write the string back to the file.
		#	(7) Flush the file to make sure it's written to disk.

		# (1a) Close the "write" file descriptor.
		thisConv.memory_file.close()

		# (1b) Reopen it in "read" mode.
		thisConv.memory_file = open(thisConv.mem_filename, 'r')

		# (2) Return the read position to the start of the file.
		thisConv.memory_file.seek(0)

		# (3) Read the entire file into a string.
		mem_string = '\n' + thisConv.memory_file.read()

		# (4) Remove the text to remove from the string.
		mem_string = mem_string.replace(text_to_remove, '\n')

		# (5a) Close the file again.
		thisConv.memory_file.close()

		# (5b) Reopen it for writing.
		thisConv.memory_file = open(thisConv.mem_filename, 'w')

		# (6) Write the string back to the file.
		thisConv.memory_file.write(mem_string[1:])

		# (7) Flush the file to make sure it's written to disk.
		thisConv.memory_file.flush()

		# Return true to indicate that the memory was removed.
		return True

	#__/ End instance method conversation.remove_memory().


	# This method is called to expunge the oldest message from the conversation
	# when the context string gets too long to fit in GPT-3's receptive field.

	def expunge_oldest_message(thisConv:BotConversation):
		"""This method is called to expunge the oldest message from the conversation."""

		chat_id = thisConv.chatID

		# There's an important error case that we need to consider:
		# If the conversation only contains one message, this means that the
		# AI has extended that message to be so large that it fills the
		# entire available space in the GPT-3 receptive field.	If we
		# attempt to expunge the oldest message, we'll end up deleting
		# the very message that the AI is in the middle of constructing.
		# So, we can't do anything here except throw an exception.
		if len(thisConv.messages) <= 1:
			raise _ConversationError("Can't expunge oldest message from "
									 f"conversation {chat_id} with only "
									 "one message.")

		# If we get here, we can safely pop the oldest message.

		#_logger.info("Expunging oldest message from "
		#			 f"{len(thisConv.messages)}-message "
		#			 f"conversation #{thisConv.chat_id}.")

		#print("Oldest message was:", thisConv.messages[0])
		thisConv.messages.pop(0)
		thisConv.expand_context()	# Update the context string.

	#__/ End instance method conversation.expunge_oldest_message().


	def trim_oldest_message(thisConv:BotConversation) -> bool:

		return thisConv.messages[0].trimFront()
			# Trims some text off the front of the first message.


	# NOTE: This method does *not* show the error to user. This is intentional
	# so that the user does not see error messages that might embarrass us.
	# (Of course, the caller can always show the error to the user if desired.)

	def report_error(thisConv:BotConversation, errmsg:str):

		"""Adds an error report to the conversation memory so that the AI can
			see it. Also logs the error to the application's main log file."""

		global _lastError

		msg = f"Error: {errmsg}"

		_logger.error(msg)	# Log the error.

		# Add the error report to the conversation.
		thisConv.add_message(BotMessage(SYS_NAME, msg))

		_lastError = msg	# So higher-level callers can access it.

	#__/ End report_error() instance method for class Conversation.


	def add_message(thisConv:BotConversation, message:BotMessage, finalize=True):

		"""Adds a message to the conversation. Also archives the message
			unless finalize=False is specified."""

		thisConv.messages.append(message)
		if len(thisConv.messages) > thisConv.context_length_max:
			thisConv.messages = thisConv.messages[-thisConv.context_length_max:]	# Keep the last N messages
		thisConv.context_length = len(thisConv.messages)	# Update the context_length counter.
		thisConv.expand_context()	# Update the context string.

		# Unless this message isn't to be finalized yet, we'll also need to
		# append the message to the conversation archive file.
		if finalize:
			thisConv.finalize_message(message)

		# Also add the raw version of the message to our internal .raw_oaiMsgs
		# tracker.
		thisConv.raw_oaiMsgs.append(message.oaiMsgDict())

		# If this is not a message from ourselves or the system,
		# and the user is not blocked, then update our idea of the
		# current dynamic memories.
		if message.sender != BOT_NAME and message.sender != SYS_NAME \
		   and not _isBlocked(message.sender):
			try:
				thisConv.dynamicMem = _getDynamicMemory(thisConv)

			except RateLimitError as e:

				_logger.error(f"Got a {type(e).__name__} from OpenAI ({e}) for "
							  f"conversation {thisConv.chat_id}.")
				
				return	# Skip the dynamic memory updating.

			# NOTE: This is relatively slow. Get rid of it?

	#__/ End add_message() instance method for class Conversation.


	# Extend a (non-finalized) message by appending some extra text onto the end of it.
	# NOTE: This should only be called on the last message in the conversation.
	# NOTE: Seems like this method should really be moved to the Message class.

	def extend_message(thisConv:BotConversation, message:BotMessage, extra_text):
		"""Extends a non-finalized message by adding some extra text to it."""

		# First, make sure the message has not already been finalized.
		if message.archived:
			print("ERROR: Tried to extend an already-archived message.")
			return

		# Add the extra text onto the end of the message.
		message.text += extra_text

		# We also need to update the context string.
		thisConv.context_string += extra_text
	#__/


	# This method deletes the last message at the end of the conversation.
	# (This is normally only done if the message is empty, since Telegram
	# will not send an empty message anyway.)

	def delete_last_message(thisConv:BotConversation):
		"""Deletes the last message in a conversation; use it only if the
			message is empty and hasn't been archived already."""

		# Commented this out to ignore these warnings.
		# First, make sure the message has not already been finalized.
		#if thisConv.messages[-1].archived:
		#	print("ERROR: Tried to delete an already-archived message.")
		#	return

		# Delete the last message.
		thisConv.messages.pop()
		thisConv.context_length -= 1

		# We also need to update the context string.
		thisConv.expand_context()	# Update the context string.
	#__/


	def finalize_message(thisConv:BotConversation, message:BotMessage):
		"""Finalize a message in the conversation (should be the last message)."""

		if not hasattr(message,'archived') or not message.archived:
			thisConv.archive_message(message)
	#__/


	def archive_message(thisConv:BotConversation, message:BotMessage):
		"""Commit a message to the conversation, and archive it."""
		thisConv.archive_file.write(message.serialize())
		thisConv.archive_file.flush()
		message.archived = True
	#__/


	# The following method clears the entire conversational memory.
	# However, it does not erase the archive file or clear the 
	# persistent memory file.

	def clear(thisConv:BotConversation):
		"""Clear the entire conversational memory."""
		thisConv.messages = []
		thisConv.context_length = 0
		thisConv.expand_context()	# Update the context string.
	#__/


	# This method checks whether a given message is already in the conversation,
	# within the last NOREPEAT_WINDOW_SIZE messages. This is used to help prevent 
	# the bot from getting into a loop where it sends the same message over and 
	# over too frequently.

	def is_repeated_message(thisConv:BotConversation, message:BotMessage):
		"""Check whether a message (with the same sender and text) is already 
			included in the most recent <NOREPEAT_WINDOW_SIZE> messages of the 
			conversation."""
		# NOTE: In below, don't check against the last message in the conversation,
		# because that one is the very (candidate) message that we're checking!!
		for m in thisConv.messages[-NOREPEAT_WINDOW_SIZE-1:-1]:
			if m.sender == message.sender and m.text == message.text:
				return True
		return False


	# This method converts the persistent context and the list of messages
	# into the format of a 'messages' list as expected by the GPT-3 chat API.

	def get_chat_messages(thisConv:BotConversation):

		"""Convert the persistent context and the list of messages into the 
			format of a 'messages' list as expected by the GPT-3 chat API."""
		
		global N_HEADER_MSGS

		chat_messages = []		# Initialize the list of chat messages.

		botName = thisConv.bot_name
		lastUser = thisConv.last_user	# Telegram object for last user that messaged us.
		userTag = _get_user_tag(lastUser)

		#/======================================================================
		#|	Message list format:
		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|
		#|	#0:			system:		[[Current time]]
		#|	#1:			system:		Pre-prompt.
		#|	#2:			system:		Persistent context (includes persistent data from TelegramBot.memories.txt)
		#|	#3:			system:		[[DYNAMIC MEMORY]]
		#|	#4:			system:		Command list.
		#|	#5:			system:		Recent messages header.
		#|	#6-(N-2):	(various):	...[RECENT TELEGRAM MESSAGES]...
		#|	#N-1:		system:		Response prompt.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		# The first message will always be a system message showing the current time.

		# MESSAGE #0.
		# This message needs to be updated before *every* new completion attempt.
		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			#'name': SYS_NAME,
			'content': "The current time is: " + timeString() + "."
		})
		
		# The next message will show the persistent context header block.
		# Note this header includes several subsections, delimited by
		# message delimiters [these used to be record separators, (ASCII
		# code 30), but now are just nothing] and section headings.

		# MESSAGE #1.
		# This message is fixed for the lifetime of the application.
		# We can just set it once each time a conversation is started.
		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			#'name': SYS_NAME,
			'content': "Attention, assistant: You are taking the role of a very " \
				f"humanlike AI persona named {botName} in a Telegram chat. Here " \
				"are the context headers for the persona, followed by recent " \
				"messages in the chat:\n"
		})

		# MESSAGE #2.
		# With the new memory system, this is initialized once at the
		# start of the application, and does not change further. We
		# can set it when the conversation is started.
		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			'content': PERMANENT_CONTEXT_HEADER + \
				globalPersistentData
		})

		# MESSAGE #3.
		# This one is fixed forever, we could just initialize it when the
		# conversation is started. --> NO, NOW IT VARIES BY USER.
		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			'content': FUNCTION_USAGE_HEADER + \
				"  activate_function(func_name:str, remark:str=None) -> status:str\n" + \
				"  remember_item(text:str, is_private:bool=True, is_global:bool=False, remark:str=None) -> status:str\n" + \
				f"  search_memory(query_phrase:str, max_results:int={DEFAULT_SEARCHMEM_NITEMS}, remark:str=None) -> results:list\n" + \
				"  forget_item(text:str=None, item_id:str=None, remark:str=None) -> status:str\n" + \
				"  analyze_image(filename:str, verbosity:str='medium', query:str=None, remark:str=None) -> result:str\n" + \
				"  create_image(description:str, shape:str='square', style:str='vivid', caption:str=None, remark:str=None) -> status:str\n" + \
				f"  block_user(user_name:str='{userTag}', remark:str=None) -> status:str\n" + \
				"  unblock_user(user_name:str, remark:str=None) -> status:str\n" + \
				"  search_web(query:str, locale:str='en-US', sections:list=['webPages'], remark:str=None) -> results:dict\n" + \
				"  pass_turn() -> None\n"

			#COMMAND_LIST_HEADER + \
			#	"  /pass - Refrain from responding to the last user message.\n" + \
			#	"  /image <desc> - Generate an image with description <desc> and send it to the user.\n" + \
			#	"  /remember <text> - Adds <text> to my persistent context data.\n" + \
			#	"  /forget <text> - Removes <text> from my persistent context data.\n" + \
			#	"  /block [<user>] - Adds the user to my block list. Defaults to current user.\n" + \
			#	"  /unblock [<user>] - Removes the user from my block list. Defaults to current user.\n"
		})

		# MESSAGE #4.
		# OK, for a given conversation, this one only needs to change
		# whenever a new user message is added to the conversation, since
		# it only depends on the last user memory. It could also change if a
		# new memory is added by a different user, but that shouldn't happen
		# very often
		if hasattr(thisConv, 'dynamicMem') and thisConv.dynamicMem:
			chat_messages.append({
				'role': CHAT_ROLE_SYSTEM,
				'content': DYNAMIC_MEMORY_HEADER + \
					thisConv.dynamicMem
					# ^ Note this only changes when a new user message is added to the convo.
			})

		# MESSAGE #5.
		# This one is fixed forever, we could just initialize it when the
		# conversation is started.
		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			'content': RECENT_MESSAGES_HEADER
		})

		# Remember how many header messages we just created.
		N_HEADER_MSGS = len(chat_messages)

		# Next, add the messages from the recent part of the conversation.
		# We'll use the .sender attribute of the Message object as the 'name'
		# attribute of the chat message, and we'll use the .text attribute
		# of the Message object as the 'content' attribute of the chat message.

		for botMessage in thisConv.messages:

			# Ask the bot message to give us its OpenAI dictionary form,
			# and add it onto the end of the chat message list.

			chat_messages.append(botMessage.oaiMsgDict())

		#__/

		# We'll add one more system message to the list of chat messages,
		# to make sure it's clear to the AI that it is responding in the 
		# role of the message sender whose 'role' matches our .bot_name
		# attribute. We also repeat some other important instructions.
		#
		# (The back-end language model will be prompted to respond by
		# something like "assistant\n", which is why we need to make sure
		# it knows that it's responding as the named bot persona.)

		#response_prompt = f"Respond as {botName}. (If you want to include an " \
		#	"image in your response, you must put the command ‘/image <desc>’ at the " \
		#	"very start of your response.)"
		#response_prompt = f"Respond as {botName}. (Remember you can use an available " \
		#	"function if there is one that is appropriate.)"

		response_prompt = f"Respond below; use the same language that the user "\
			"used most recently, if appropriate. (Alternatively, you can activate "\
			"an available function and then call that function, if appropriate.)"

		if thisConv.chat_id < 0:	# Negative chat IDs correspond to group chats.
			# Only give this instruction in group chats:
			response_prompt += " However, if the user is not addressing you, " \
							   "type '/pass' to remain silent."
		else:
			response_prompt += " You may also send '/pass' to refrain from responding."

		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			#'name': SYS_NAME,
			'content': response_prompt
		})

		return chat_messages
	
	#__/ End conversation.get_chat_messages() instance method definition.


		# Old versions of response prompt:
		
			#'content': f"Respond as {botName}, in the user's language if " \
			#	"possible. (However, if the user is not addressing you, type " \
			#	"'/pass' to remain silent.)"
				
			# 'content': f"Respond as {thisConv.bot_name}."
			# # This is simple and seems to work pretty well.

			#'content': f"Assistant, your role in this chat is '{thisConv.bot_name}'; " \
			#	"enter your next message below.",
			#	# This was my initial wording, but it seemed to cause some confusion.

			#'content': f"{thisConv.bot_name}, please enter your response below at " \
			#	"the 'assistant' prompt:"
			#	# The above wording was agreed upon by me & Turbo (model 'gpt-3.5-turbo').

			# Trying this now:
			#'content': f"Please now generate {thisConv.bot_name}'s response, in the " \
			#	"format:\n" \
			#	 r"%%%\n" \
			#	 "Commentary as assistant:\n"
			#	 "{assistant_commentary}\n"
			#	 r"%%%\n" \
			#	 f"{thisConv.bot_name}'s response:\n"
			#	 "{persona_response}\n"
			#	 r"%%%\n"


#__/ End Conversation class definition.


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|
	#|	2.3. Private / minor classes.					[module code subsection]
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Exception class to represent an error in the conversation.
class _ConversationError(Exception):
	"""Exception class to represent an error in the conversation."""
	def __init__(self, message:str):
		self.message = message
	def __str__(self):
		return self.message

# A filter that matches attempted user commands that aren't of any defined user command type.
class _UnknownCommandFilter(filters.BaseFilter):

	# New syntax
	def check_update(self, update:Update, *args, **kwargs) -> bool:
		self(update, *args, **kwargs)

	# Old syntax
	def __call__(self, update:Update, *args, **kwargs) -> bool:

		# Get the message, or edited message from the update.
		(message, edited) = _get_update_msg(update)
		
		# If this isn't even a message update, it's definely not an unknown command!
		if message is None:
			return False

		text = message.text
		defined_commands = ['/start', '/help', '/image', '/remember', '/forget', '/reset', '/echo', '/greet']
		
		if text is None:
			return False
		if text.startswith('/') and text.split()[0] not in defined_commands:
			return True
		return False
	#__/
#__/


class SubordinateAI_: pass
class SubordinateAI_: 
	"""Abstract base class for subordinate AI entities."""
	pass

def _get_url_content(url:str):
	"""Query a URL and retrieve its content."""
	return requests.get(url)
	

class PageView: pass
class PageView:

	"""Keeps track of our postion on a loaded webpage."""

	def __init__(newPageView:PageView, url:str, index:int=0):

		newPV = newPageView		# Shorter name.

		newPV.url		= url
		newPV.response	= response = _get_url_content(url)		# Download the raw data.
			# NOTE: The returned Response instance has attributes including
			# .url, .status_code, .headers, .encoding, .text, and .json().

		newPV.resp_url	= resp_url	= response.url
		newPV.status	= status	= response.status_code
		newPV.headers	= headers	= response.headers
		newPV.encoding	= encoding	= response.encoding
		newPV.text		= text		= response.text

		# See if there's JSON. If so, parse it.
		if status == 200 and 'json' in headers['Content-Type']:
			# Really we should do exception checking here.
			data = response.json()
		else:
			data = text
		
		newPV.data = data

		# Put everything in a handy dictionary.
		newPV.resp_dict = resp_dict = {
			'url':			resp_url,
			'status_code':	status,
			'headers':		headers,
			'encoding':		encoding,
			'data':			data
		}

		# Make a formatted representation of that dict.
		resp_str = json.dumps(resp_dict, indent=4)
		resp_str.replace(' '*8, '\t')
		newPV.resp_str = resp_str

		_logger.normal("GENERATED PAGEVIEW WITH CONTENT:\n" + resp_str)

		# Initialize other miscellaneous attributes.

		newPV.index		= index		# Our index in WebAssistant's pageView list.

		newPV.start_pos	= start_pos = 0
		newPV.end_pos	= end_pos	= None	# Will be determined on 1st render

		newPV.search_term	= search_term	= None	# None yet until there's a search.
		newPV.search_pos	= search_pos	= 0		# Starting position for search.

	#__/

	# We'll need methods to support forwards and backwards scrolling & searching.
	# Also to render the page view starting from the current position.

#__/

# Subordinate AI class for web operations.
class WebAssistant: pass
class WebAssistant(SubordinateAI_):
	"""Subordinate AI to handle web search & retrieval operations."""

	# New instance initializer.
	def __init__(newWebAssistant:WebAssistant, callerName:str, userLocale:str):		

		newWA = newWebAssistant		# Shorter name.

			# Here we initialize the important data members.

		# Create the connection to the core LLM that will handle this function.
		# It needs to be a model that has at least a 16k token context window.
		# We will use this space as follows:
		#	* <= 1K:	Pre-prompt and function descriptions.
		#	* <= 12K:	Web search results, or view of current webpage.
		#	* <= 3K:	Conversation history between caller and assistant.

		newWA.core_llm = createCoreConnection('gpt-3.5-turbo-16k', maxTokens=2000)
			# Note here we let temperature, etc., go to defaults.

		# Here we have a list of PageView objects, that track where we are
		# in a stack of pages we're currently narrating. This is like a browser
		# tab that can support Back and Forward operations. Each pageView has a
		# URL, a currently-loaded page_content, a start position and end position,
		# a current search term, and a search cursor position.

		newWA.pageViews			= []		# No pages loaded into stack yet.
		newWA.cur_page_index	= None		# Numeric index of current pageView.

		# List of OpenAI messages for the conversation history with the caller.
		newWA.convoOaiMsgs		= []

#__/ End public class WebAssistant.


#/==============================================================================
#|
#|	3. Handler functions for Telegram.							  [code section]
#|	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|
#|		In this section, we define various handler functions which are
#|		called by the dispatcher to handle updates and errors received
#|		from the central Telegram server. As of v20.0 of the python-
#|		telegram-bot library, these should be implemented as asyncio
#|		functions for improved concurrency. They are wrapped within
#|		handler objects	which are created later, in code section 6.3.
#|		The list of handler functions, by handler group, is as follows:
#|
#|
#|			Group 0 (default group) -- User command handlers.
#|			~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|
#|				Command		Handler Function	Description
#|				~~~~~~~		~~~~~~~~~~~~~~~~	~~~~~~~~~~~
#|				/start		handle_start()		Starts/resumes conversation.
#|				/greet		handle_greet()		(Test function) Display greeting.
#|				/echo		handle_echo()		(Test function) Echo back text.
#|				/help		handle_help()		Display help text to the user.
#|				/remember	handle_remember()	Add an item to persistent memory.
#|				/forget		handle_forget()		Remove an item from persistent memory.
#|
#|
#|			Group 1 -- Multimedia input processing handlers.
#|			~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|
#|			For messages containing multimedia input, these handlers
#|			generally do some preprocessing of the media, prior to
#|			normal message handling. They are not intended to uniquely
#|			match a given message update. They are higher priority than
#|			normal message handling.
#|
#|				Handler Function	Description
#|				~~~~~~~~~~~~~~~~	~~~~~~~~~~~
#|				handle_audio()		Pre-process audio files & voice clips.
#|
#|
#|			Group 2 -- Normal message handlers.
#|			~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|
#|			These handlers take care of normal message processing.
#|
#|				Handler Function	Description
#|				~~~~~~~~~~~~~~~~	~~~~~~~~~~~
#|				handle_message()	Process a generic message from a user.
#|
#|
#|			Group 3 -- Unknown command handlers.
#|			~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#|
#|			This special handler takes care of processing for attempted
#|			user commands that don't match any of the defined commands.
#|
#|				Handler Function			Description
#|				~~~~~~~~~~~~~~~~			~~~~~~~~~~~
#|				handle_unknown_command()	Handle an unrecognized command.
#|
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#/==========================================================================
	#| 3.1. Update handler group 0 -- User command handlers.
	#|
	#|		Command		Handler Function	Description
	#|		~~~~~~~		~~~~~~~~~~~~~~~~	~~~~~~~~~~~
	#|		/start		handle_start()		Starts/resumes conversation.
	#|		/greet		handle_greet()		(Test function) Display greeting.
	#|		/echo		handle_echo()		(Test function) Echo back text.
	#|		/help		handle_help()		Display help text to the user.
	#|		/remember	handle_remember()	Add an item to persistent memory.
	#|		/forget		handle_forget()		Remove an item from persistent memory.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Now, let's define a function to handle the /start command.
async def handle_start(update:Update, context:Context, autoStart=False) -> None:
	# "Context," in this context, refers to the Telegram context object.
	# (As opposed to, a context string for passing to GPT-3.)
	# Set autoStart=True if calling this method other than by the /start command handler.

	"""Starts a conversation. May also be used to reload a conversation
		on command, or automatically after a server restart."""

	# Get the message, or edited message from the update.
	(tgMessage, edited) = _get_update_msg(update)
		
	if tgMessage is None:
		_logger.warning("In handle_start() with no message? Aborting.")
		return

	chat_id = tgMessage.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a specific conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user_name that we'll use in messages.
	user = tgMessage.from_user
	user_name = _get_user_tag(user)
	which_name = _which_name	# Global set by _get_user_tag() call.

	# Also make sure the user is in our database of known users.
	_addUser(user)

	# Print diagnostic information.
	_logger.normal(f"\nUser {user_name} started conversation {chat_id}.")

	# Create a new conversation object and link it from the Telegram context object.
	# NOTE: It needs to go in the context.chat_data dictionary, because that way it
	# will be specific to this chat_id. This will also allow updates from different
	# users in the same chat to all appear in the same conversation.

	conversation = BotConversation(chat_id, creator=user)
		# Note this constructor call will also reload the conversation data, if it exists.

	context.chat_data['conversation'] = conversation
		# There's a potential subtle bug here, namely that if we're restarting
		# an existing conversation, we'll silently overwrite the old value here,
		# without freeing up the file descriptors it allocated. This will cause
		# us to eventually run out of file descriptors. To prevent this, we have
		# to add a __del__() destructor method to the Conversation class, and it
		# will eventually get called when the no-longer-referenced Conversation
		# object gets garbage-collected.

	# Add the /start command itself to the conversation archive.

	if autoStart:
		conversation.add_message(BotMessage(SYS_NAME, '/start'))
			# This is to tell the AI that the server is auto-starting.
	else:
		conversation.add_message(BotMessage(user_name, tgMessage.text))

	# Send an initial message to the user.
		# NOTE: If messages were read from the conversation archive file,
		#	this means we are continuing a previous conversation after
		#	a restart of the bot. In this case, we don't want to send the
		#	start message, but instead we send a different message.

	if len(conversation.messages) <= 1:		# 1 not 0 because we just added '/start' message.

		_logger.normal(f"\tSending start message to user {user_name} in new "
					   f"conversation {chat_id}.")

		# First record the initial message in our conversation data structure.
		conversation.add_message(BotMessage(conversation.bot_name, START_MESSAGE))

		# Now try to also send it to the user.
		if await _reply_user(tgMessage, conversation, START_MESSAGE) != 'success':
			return	# Connection broken; failure; abort.

	else:	# Two or more messages? We must be continuing an existing conversation.

		_logger.normal(f"\tSending restart message to user {user_name} for "
					   f"existing conversation {chat_id}.")

		# Compose a system diagnostic message explaining what we're doing.
		diag_msgStr = f"Restarted bot with last {len(conversation.messages)} " \
				  f"messages from archive."

		# Send it to the AI and to the user.
		sendRes = await _send_diagnostic(tgMessage, conversation, diag_msgStr)
		if sendRes != 'success': return sendRes
	#__/


	# Give the user a system warning if their first name contains unsupported characters or is too long.
	if not re.match(r"^[a-zA-Z0-9_-]{1,64}$", tgMessage.from_user.first_name):
		
	       # Log the warning.
		_logger.warning(f"User {tgMessage.from_user.first_name} has an "
						f"unsupported first name; using {user_name} instead.")

           # Add the warning message to the conversation, so the AI can see it.
		warning_msgStr = "NOTIFICATION: Welcome, " \
					  	f'"{tgMessage.from_user.first_name}". ' \
						"The AI will identify you in this conversation by your " \
						f"{which_name}, {user_name}."

		#warning_msg = f"[SYSTEM NOTIFICATION: Your first name \"{update.message.from_user.first_name}\"" \
		#	"contains unsupported characters (or is too long). The AI only supports names with <=64 alphanumeric " \
		#	"characters (a-z, 0-9), dashes (-) or underscores (_). For purposes of this conversation, "   \
		#	f"you will be identified by your {which_name}, {user_name}.]"
				
			# Make sure the AI sees that message, even if we fail in sending it to the user.
		conversation.add_message(BotMessage(SYS_NAME, warning_msgStr))
		
            # Also send the warning message to the user. (Making it clear that 
            # it's a system message, not from the AI persona itself.)
		reply_msgStr = f"[SYSTEM {warning_msgStr}]"
		await _reply_user(tgMessage, conversation, reply_msgStr, ignore=True)
	#__/

	# Check for a file 'announcement.txt' in the AI's datadir; if it's present,
	# send it to the user as a system announcement.

	ai_datadir = AI_DATADIR
	ann_path = os.path.join(ai_datadir, 'telegram', 'announcement.txt')
	if os.path.exists(ann_path):
		with open(ann_path, 'r') as ann_file:
			ann_text = ann_file.read().strip()
			msgStr = f"ANNOUNCEMENT: {ann_text}"
			conversation.add_message(BotMessage(SYS_NAME, msgStr))
			fullMsgStr = f"[SYSTEM {msgStr}]"
			_logger.info(f"Sending user {user_name} system announcement: {fullMsgStr}")
			await _reply_user(tgMessage, conversation, fullMsgStr, ignore=True)

#__/ End handle_start() function definition.


# Now, let's define a function to handle the /help command.
async def handle_help(update:Update, context:Context) -> None:
	"""Display the help string when the command /help is issued."""

	# Get the message, or edited message from the update.
	(tgMessage, edited) = _get_update_msg(update)

	if tgMessage is None:
		_logger.warning("In handle_help() with no message? Aborting.")
		return

	chat_id = tgMessage.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(tgMessage.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_help(); aborting.")
		return

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /help command to conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /help command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, tgMessage.text))

	_logger.normal(f"\nUser {user_name} entered a /help command for chat {chat_id}.")

	# Log diagnostic information.
	_logger.normal(f"\tDisplaying help in conversation {chat_id}.")

	# Also record the help string in our conversation data structure.
	who = BOT_NAME if customHelp else SYS_NAME
	conversation.add_message(BotMessage(who, HELP_STRING))

	# Send the help string to the user.
	if 'success' != await _reply_user(tgMessage, conversation, HELP_STRING, markup=True):	# The help message may include markup.
		return

	# Finished processing this message.

#__/ End '/help' user command handler.


async def handle_image(update:Update, context:Context) -> None:
	"""Generate an image with a given description."""

	# We now just let the AI handle these requests, so it
	# can warn the user if the requested content is inappropriate.
	return await handle_message(update, context)

	### CODE BELOW IS OBSOLETE

	# Get the message, or edited message from the update.
	(tgMessage, edited) = _get_update_msg(update)

	# Get the ID of the present chat.
	chat_id = tgMessage.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(tgMessage.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		return

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /image command to conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /help command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, tgMessage.text))

	_logger.normal(f"\nUser {user_name} entered an /image command for chat {chat_id}.")

	# Get just the first line of the message as the actual /image command line.
	cmdLine = tgMessage.text.split('\n')[0]

	if len(cmdLine) > 7:		# Anything after '/', 'i', 'm', 'a', 'g', 'e', ' '?
		imageDesc = cmdLine[7:]	# Rest of line after '/image ' 

		# Log diagnostic information.
		_logger.normal("\tGenerating image with description "
					   f"[{imageDesc}] for user '{user_name}' in "
					   f"conversation {chat_id}.")

		send_result = await send_image(update, context, imageDesc)
		if send_result is not None:
			(image_url, new_desc, save_filename) = send_result

			# Make a note in conversation archive to indicate that the image was sent.
			conversation.add_message(BotMessage(SYS_NAME, f'[Generated image "{new_desc}" in file "{save_filename}" and sent it to the user.]'))
		else:
			conversation.add_message(BotMessage(SYS_NAME, f'[ERROR: Failed to send image to user.]'))

		# Allow the AI to follow up (but without re-processing the message).
		await handle_message(update, context, isNewMsg=False)

	else:
		_logger.error("The '/image' command requires a non-empty argument.")

		errMsgStr = f"The '/image' command requires an argument. (Usage: /image <description>)"
		await _report_error(conversation, tgMessage, errMsgStr, logIt=False)	# Logged above.

		return
	#__/

	# Finished processing this message.
#__/


# Now, let's define a function to handle the /echo command.
async def handle_echo(update:Update, context:Context) -> None:
	"""Echo the user's message."""

	# Get the message, or edited message from the update.
	(tgMessage, edited) = _get_update_msg(update)

	chat_id = tgMessage.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(tgMessage.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		return

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /echo command line to conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	cmdLine = tgMessage.text

	# Add the /echo command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, cmdLine))

	_logger.normal(f"\nUser {user_name} entered an /echo command for chat {chat_id}.")

	if len(cmdLine) > 6:	# Anything after '/', 'e', 'c', 'h', 'o', ' '?
		textToEcho = cmdLine[6:]	# Grab rest of line.
	else:
		_logger.error("The '/echo' command requires a non-empty argument.")
		
		errMsgStr = f"The '/echo' command requires an argument. (Usage: /echo <text to echo>)"
		await _report_error(conversation, tgMessage, errMsgStr, logIt=False)	# Logged above.

		return
	#__/
	
	responseText = f'Response: "{textToEcho}"'

	# Log diagnostic information.
	_logger.normal(f"\tEchoing [{textToEcho}] in conversation {chat_id}.")

	# Record the echo text in our conversation data structure.
	conversation.add_message(BotMessage(SYS_NAME, responseText))

	await _reply_user(tgMessage, conversation, responseText)

#__/ End '/echo' user command handler.


async def handle_showmem(update:Update, context:Context) -> None:

	"""Dump contents of memory to system console."""

	# Get the message, or edited message from the update.
	(message, edited) = _get_update_msg(update)

	if message is None:
		_logger.warning("In handle_showmem() with no message? Aborting.")
		return

	# Get the chat ID.
	chat_id = message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(message.from_user)

	# Block /showmem command for users other than Mike.
	if user_name != 'Michael':
	
		_logger.warn("User {user_name} is not authorized to execute /showmem.")
	
		# Send a diagnostic message to the AI and to the user.
		diagMsg = f"This command requires authorization."
		sendRes = await _send_diagnostic(message, conversation, diagMsg)
		if sendRes != 'success': return sendRes

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_showmem(); aborting.")
		return

	# Error handling.
	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /showmem command line to conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /showmem command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, message.text))

	_logger.normal(f"\nUser {user_name} entered a /showmem command for chat {chat_id}.")

	# Log diagnostic information.
	_logger.normal(f"\tDumping user list to console for conversation {chat_id}.")

	# Print user list to console.
	_printUsers()

	# Log diagnostic information.
	_logger.normal(f"\n\tDumping memory items to console for conversation {chat_id}.")

	# Print memory to console.
	_printMemories()

	_logger.normal("\n\tDump of users and memory items to console is complete.\n")

	CONFIRMATION_TEXT = "The contents of the users and remembered_items "\
						"tables have been printed to the system console."

	# Also record the echo text in our conversation data structure.
	conversation.add_message(BotMessage(SYS_NAME, CONFIRMATION_TEXT))

	# Send it to user.
	await _reply_user(message, conversation, f"[SYSTEM: {CONFIRMATION_TEXT}]")

#__/ End '/showmem' user command handler.


async def handle_delmem(update:Update, context:Context) -> None:

	"""Delete an item from memory database."""

	# Get the message, or edited message from the update.
	(message, edited) = _get_update_msg(update)

	if message is None:
		_logger.warning("In handle_delmem() with no message? Aborting.")
		return

	# Get the chat ID.
	chat_id = message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(message.from_user)

	# Block /showmem command for users other than Mike.
	if user_name != 'Michael':
	
		_logger.warn("User {user_name} is not authorized to execute /delmem.")
	
		# Send a diagnostic message to the AI and to the user.
		diagMsg = f"This command requires authorization."
		sendRes = await _send_diagnostic(message, conversation, diagMsg)
		if sendRes != 'success': return sendRes

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_delmem(); aborting.")
		return

	# Error handling.
	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /delmem command line to conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /showmem command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, message.text))

	_logger.normal(f"\nUser {user_name} entered a /delmem command for chat {chat_id}.")

	##### The real work begins here.

	# Split command line on space.
	cmdWords = message.text.split(' ')		

	# Get 2nd word, which is subcommand 'text' or 'id'
	subcmd = cmdWords[1]

	# Validate subcommand.
	if subcmd not in ('id', 'text'):
		await _report_error(conversation, message,
							f"Unknown subcommand [{subcmd}].\n"
							"\tUSAGE: /delmem (id <itemID>|text <itemText>)")
		return

	# Wrap up the rest of the words.
	rest = ' '.join(cmdWords[2:])
	
	if subcmd=='id':
		_logger.normal(f"\tDeleting memory item with ID#{rest}...")
		_deleteMemoryItem(item_id=rest)
		CONF_TEXT = f"The memory item with item_id='{rest}' has been deleted."
		
	elif subcmd=='text':
		_logger.normal(f"\tDeleting memory item with text=[rest]...")
		_deleteMemoryItem(text=rest)
		CONF_TEXT = f"The memory item with item_text='{rest}' has been deleted."

	# Also record the echo text in our conversation data structure.
	conversation.add_message(BotMessage(SYS_NAME, CONF_TEXT))

	# Send it to user.
	await _reply_user(message, conversation, f"[SYSTEM: {CONF_TEXT}]")

#__/ End '/delmem' user command handler.


# Now, let's define a function to handle the /greet command.
async def handle_greet(update:Update, context:Context) -> None:

	"""Greet the user."""

	# Get the message, or edited message from the update.
	(tgMessage, edited) = _get_update_msg(update)

	if tgMessage is None:
		_logger.warning("In handle_greet() with no message? Aborting.")
		return

	chat_id = tgMessage.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(tgMessage.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_greet(); aborting.")
		return

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /greet command line to conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /greet command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, tgMessage.text))

	_logger.normal(f"\nUser {user_name} entered a /greet command for chat {chat_id}.")

	# Log diagnostic information.
	_logger.normal(f"\tSending greeting in conversation {chat_id}.")

	# Record the greeting text in our conversation data structure.
	conversation.add_message(BotMessage(SYS_NAME, GREETING_TEXT))

	# Send the greeting to the user.
	await _reply_user(tgMessage, conversation, GREETING_TEXT)

#__/ End '/greet' user command handler.


# Now, let's define a function to handle the /reset command.
async def handle_reset(update:Update, context:Context) -> None:
	"""Reset the conversation."""

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)

	if tgMsg is None:
		_logger.warning("In handle_reset() with no message? Aborting.")
		return

	chat_id = tgMsg.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(tgMsg.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_reset(); aborting.")
		return

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't reset conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /reset command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, tgMsg.text))

	# Print diagnostic information.
	_logger.normal(f"\nUser {user_name} entered a /reset command for chat {chat_id}.")
	_logger.normal(f"\tResetting conversation {chat_id}.")

	# Clear the conversation.
	conversation.clear()

	# Send a diagnostic message to AI & user.
	diagMsgStr = f"Cleared conversation {chat_id}."
	sendRes = await _send_diagnostic(tgMsg, conversation, diagMsgStr)
	if sendRes != 'success': return

	# Send an initial message to the user.

	reset_msgStr = f"This is {BOT_NAME}. I've cleared my memory of our previous conversation."

		# Record the reset message in our conversation data structure.
	conversation.add_message(BotMessage(conversation.bot_name, reset_msgStr))

		# Send it to the user as well.
	await _reply_user(tgMsg, conversation, reset_msgStr)

#__/ End definition of /reset command handler function.

# Now, let's define a function to handle the /speech (on|off) command.
async def handle_speech(update:Update, context:Context) -> None:

	"""Turns spoken output on or off depending on command argument."""

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)

	if tgMsg is None:
		_logger.warning("In handle_speech() with no message? Aborting.")
		return

	chat_id = tgMsg.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(tgMsg.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_quiet(); aborting.")
		return

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't toggle speech in conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /speech command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, tgMsg.text))

	# Print diagnostic information.
	_logger.normal(f"\nUser {user_name} entered a /speech command for chat {chat_id}.")
	_logger.normal(f"\tToggling speech output in conversation {chat_id}.")

	# Actually do it.
	conversation.speech_on = not conversation.speech_on
	
	# Send a diagnostic message to AI & user.
	if conversation.speech_on:
		diagMsgStr = f"{BOT_NAME}'s messages will now be sent as voice clips as well as text. Type '/speech' to toggle the speech feature back off."
	else:
		diagMsgStr = f"Speech output has now been turned off. Type '/speech' to turn it back on."

	sendRes = await _send_diagnostic(tgMsg, conversation, diagMsgStr)
	if sendRes != 'success': return sendRes

#__/ End definition of /speech command handler function.


# Now, let's define a function to handle the /quiet command.
async def handle_quiet(update:Update, context:Context) -> None:

	"""Put the bot into quiet mode."""

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)

	if tgMsg is None:
		_logger.warning("In handle_quiet() with no message? Aborting.")
		return

	chat_id = tgMsg.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(tgMsg.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_quiet(); aborting.")
		return

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't go quiet in conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /quiet command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, tgMsg.text))

	# Print diagnostic information.
	_logger.normal(f"\nUser {user_name} entered a /quiet command for chat {chat_id}.")
	_logger.normal(f"\tPutting conversation {chat_id} into quiet mode.")

	# Actually do it.
	conversation.quiet_mode = True
	
	# Send a diagnostic message to AI & user.
	diagMsgStr = f"{BOT_NAME} is now in quiet mode and will only respond when addressed by name. Type '/noisy' to return to normal mode."
	sendRes = await _send_diagnostic(tgMsg, conversation, diagMsgStr)
	if sendRes != 'success': return sendRes

	# Send a message from AI to user.

	quiet_msgStr = f'Remember to use my name "{BOT_NAME}" when you want me to respond!'
		# Record the reset message in our conversation data structure.
	conversation.add_message(BotMessage(conversation.bot_name, quiet_msgStr))
		# Send it to the user as well.
	await _reply_user(tgMsg, conversation, quiet_msgStr)

#__/ End definition of /quiet command handler function.


# Now, let's define a function to handle the /noisy command.
async def handle_noisy(update:Update, context:Context) -> None:

	"""Put the bot into normal (i.e., noisy) mode."""

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)

	if tgMsg is None:
		_logger.warning("In handle_noisy() with no message? Aborting.")
		return

	chat_id = tgMsg.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_tag(tgMsg.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_noisy(); aborting.")
		return

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't turn off quiet mode in conversation {chat_id} because it's not loaded.")
		return

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /noisy command itself to the conversation archive.
	conversation.add_message(BotMessage(user_name, tgMsg.text))

	# Print diagnostic information.
	_logger.normal(f"\nUser {user_name} entered a /noisy command for chat {chat_id}.")
	_logger.normal(f"\tPutting conversation {chat_id} into normal (noisy) mode.")

	# Actually do it.
	conversation.quiet_mode = False
	
	# Send a diagnostic message to AI & user.
	diagMsgStr = f"{BOT_NAME} is now in noisy mode and may respond to any message. Type '/quiet' to return to quiet mode."
	sendRes = await _send_diagnostic(tgMsg, conversation, diagMsgStr)
	if sendRes != 'success': return sendRes

	# Send a message from AI to user.

	noisy_msgStr = f'Now I can respond to any message sent in this chat!'
		# Record the reset message in our conversation data structure.
	conversation.add_message(BotMessage(conversation.bot_name, noisy_msgStr))
		# Send it to the user as well.
	await _reply_user(tgMsg, conversation, noisy_msgStr)

#__/ End definition of /noisy command handler function.


# Now, let's define a function to handle the /remember command.
async def handle_remember(update:Update, context:Context) -> None:

	"""Add the given message as a new memory."""

	# We now just let the AI handle these requests, so that it can
	# set the 'private' and 'global' fields as appropriate.
	return await handle_message(update, context)

	### CODE BELOW IS OBSOLETE

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)

	if tgMsg is None:
		_logger.warning("In handle_remember() with no message? Aborting.")
		return

	chat_id = tgMsg.chat.id
	user_id = tgMsg.from_user.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get the name that we'll use for the user.
	user_name = _get_user_tag(tgMsg.from_user)

	# Block /remember command for users other than Mike.
	if user_name != 'Michael':
	
		_logger.warn("Currently ignoring /remember command for all users besides Michael.")
	
		# Send a diagnostic message to the AI and to the user.
		diagMsg = f"Sorry, the /remember command is currently disabled."
		sendRes = await _send_diagnostic(tgMsg, conversation, diagMsg)
		if sendRes != 'success': return sendRes

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_remember(); aborting.")
		return

	# Retrieve the Conversation object from the Telegram context.
	if not 'conversation' in context.chat_data:
		_logger.error(f"Ignoring /remember command for conversation {chat_id} because conversation not loaded.")
		return

	conversation = context.chat_data['conversation']

	# First, we'll add the whole /remember command line to the conversation, so that the AI can see it.
	conversation.add_message(BotMessage(user_name, tgMsg.text))

	# Check whether the user is in our access list.
	if not _check_access(user_name, user_id=user_id):
		_logger.normal(f"\nUser {user_name} tried to access chat {chat_id}, "
			"but is not in the access list. Denying access.")

		errMsg = f"Sorry, but user {user_name} is not authorized to access {BOT_NAME} bot."
		#errMsg = f"Sorry, but {BOT_NAME} bot is offline for now due to cost reasons."

		await _report_error(conversation, tgMsg, errMsg, logIt=False)	# Logged above.

		return
	#__/

	_logger.normal(f"\nUser {user_name} entered a /remember command for chat {chat_id}.")

	# Get the command's argument, which is the text to remember.
	text = ' '.join(tgMsg.text.split(' ')[1:])

	# Tell the conversation object to add the given message to the AI's persistent memory.
	if not conversation.add_memory(text):
		errmsg = _lastError

		# Generate an error-level report to include in the application log.
		_logger.error(f"{user_name} failed to add memory: [{text.strip()}]")
	
		# Send a diagnostic message to the AI and to the user.
		diagMsg = f"Could not add [{text.strip()}] to persistent memory. " \
				  f'Error message was: "{errmsg}"'
		sendRes = await _send_diagnostic(tgMsg, conversation, diagMsg)
		if sendRes != 'success': return sendRes
	#__/

	_logger.normal(f"\t{user_name} added memory: [{text.strip()}]")

	# Send a diagnostic message to the AI and as a reply to the user.
	diagMsg = f"Added [{text.strip()}] to persistent memory."
	await _send_diagnostic(tgMsg, conversation, diagMsg, ignore=True)

#__/ End definition of /remember command handler.


# Now, let's define a function to handle the /search command.
async def handle_search(update:Update, context:Context) -> None:

	"""Search the bot's memory or the web for a phrase."""

	# We now just let the AI handle these requests intelligently.
	return await handle_message(update, context)


# Now, let's define a function to handle the /forget command.
async def handle_forget(update:Update, context:Context) -> None:
	
	"""Remove the given message from the AI's persistent memory."""
	
	# We now just let the AI handle these requests, so that it can
	# set the 'private' and 'global' fields as appropriate.
	return await handle_message(update, context)

	### CODE BELOW IS OBSOLETE

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)

	if tgMsg is None:
		_logger.warning("In handle_forget() with no message? Aborting.")
		return

	chat_id = tgMsg.chat.id
	user_id = tgMsg.from_user.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get the name that we'll use for the user.
	user_name = _get_user_tag(tgMsg.from_user)

	_logger.normal(f"\nUser {user_name} entered a /forget command for chat {chat_id}.")

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_forget(); aborting.")
		return 

	# Retrieve the Conversation object from the Telegram context.
	if not 'conversation' in context.chat_data:
		_logger.error(f"Ignoring /forget command for conversation {chat_id} because conversation not loaded.")

	conversation = context.chat_data['conversation']

	# First, we'll add the whole /forget command line to the conversation, so that the AI can see it.
	conversation.add_message(BotMessage(user_name, tgMsg.text))

	# Check whether the user is in our access list.
	if not _check_access(user_name, user_id):
		_logger.normal(f"\nUser {user_name} tried to access chat {chat_id}, "
					   "but is not in the access list. Denying access.")

		errMsgStr = f"Sorry, but user {user_name} is not authorized to access {BOT_NAME} bot."
		#errMsgStr = f"Sorry, but {BOT_NAME} bot is offline for now due to cost reasons."

		await _report_error(conversation, tgMsg, errMsgStr, logIt=False)
			# Note we already did a log entry above.

		return

	# Get the command's argument, which is the text to forget.
	text = ' '.join(tgMsg.text.split(' ')[1:])

	# Tell the conversation object to remove the given message from the AI's persistent memory.
	# This returns a boolean indicating whether the operation was successful.
	success = conversation.remove_memory(text)

	# If the operation was successful, send a reply to the user.
	if success:

		# Generate a normal-level report to include in the application log.
		_logger.normal(f"\t{user_name} removed memory: [{text.strip()}]")

		# Send a diagnostic message to the AI and as a reply to the user.
		diagMsgStr = f"Removed [{text.strip()}] from persistent memory."
		await _send_diagnostic(tgMsg, conversation, diagMsgStr, ignore=True)
	
	# If the operation was not successful, send a different reply to the user.
	else:
		
		errMsgStr = _lastError

		# Generate an error-level report to include in the application log.
		_logger.error(f"{user_name} failed to remove memory: [{text.strip()}]")
	
		diagMsgStr = f"Could not remove [{text.strip()}] from persistent memory. "\
				  f'Error message was: "{errMsgStr}"'
		await _send_diagnostic(tgMsg, conversation, diagMsgStr, ignore=True)

	#__/

	# Copilot wrote the following amusing diagnostic code. But we don't really need it.
	## Now, let's see if the AI has any memories left.
	#if len(conversation.memories) == 0:
	#	 update.message.reply_text(f"I'm sorry, I don't remember anything else.\n")
	#else:
	#	 update.message.reply_text(f"I remember these things:\n")
	#	 for memory in conversation.memories:
	#		 update.message.reply_text(f"\t{memory}\n")

#__/ End definition of /forget command handler.


	#/==========================================================================
	#| 3.2. Update handler group 1 -- Multimedia input processing handlers.
	#|
	#|		For messages containing multimedia input, these handlers
	#|		generally do some preprocessing of the media, prior to
	#|		normal message handling. They are not intended to uniquely
	#|		match a given message update. They are higher priority than
	#|		normal message handling.
	#|
	#|			Handler Function	Description
	#|			~~~~~~~~~~~~~~~~	~~~~~~~~~~~
	#|			handle_audio()		Pre-process audio files & voice clips.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

async def handle_audio(update:Update, context:Context) -> None:
	"""Handle an audio message from the user."""

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)
		
	if tgMsg is None:
		_logger.warning("In handle_audio() with no message? Aborting.")
		return

	user_name = _get_user_tag(tgMsg.from_user)

	# Get the chat ID.
	chat_id = tgMsg.chat.id

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_audio(); aborting.")
		return

	# Get our Conversation object.
	conversation = context.chat_data['conversation']

	_logger.normal(f"\nReceived a message with audio from user {user_name} in chat {chat_id}.")

	# Check if the message contains audio or voice
	if tgMsg.audio:
		audio = tgMsg.audio
	elif tgMsg.voice:
		audio = tgMsg.voice
	else:
		_logger.error("A message passed the audio/voice filter, but did not contain either.")
		return	# Dispatcher will still try other filters.

	# Get the file_id and download the file
	file_id = audio.file_id
	file_obj = await context.bot.get_file(file_id)

	# Get the value of environment variable AI_DATADIR.
	# This is where we'll save any audio files.
	ai_datadir = AI_DATADIR
	audio_dir = os.path.join(ai_datadir, 'audio')

	# Create a folder to save the audio files if it doesn't exist
	if not os.path.exists(audio_dir):
		os.makedirs(audio_dir)

	# Pick a shorter ID for the file (collisions will be fairly rare).
	short_file_id = f"{random.randint(1,1000000)-1:06d}"

	# Save the audio as an OGG file
	ogg_file_path = os.path.join(audio_dir, f'{user_name}-{short_file_id}.ogg')
	_logger.normal(f"\tDownloading audio from user {user_name} in chat {chat_id} to OGG file {ogg_file_path}.")
	await file_obj.download_to_drive(ogg_file_path)

	# Convert the OGG file to MP3 (we were using WAV, but the file size was too big).
	mp3_file_path = os.path.join(audio_dir, f'{user_name}-{short_file_id}.mp3')
	_logger.normal(f"\tConverting audio from user {user_name} in chat {chat_id} to MP3 format in {mp3_file_path}.")

	_logger.normal(f"\t\tReading in OGG file {ogg_file_path}...")
	try:
		ogg_audio = AudioSegment.from_ogg(ogg_file_path)
	except Exception as e:
		_logger.error(f"Error reading OGG audio: {e}", exc_info=logmaster.doDebug)
			# This will output the full traceback of the exception if debug logging is on.

	_logger.normal(f"\t\tWriting out MP3 file {mp3_file_path}...")
	try:
		ogg_audio.export(mp3_file_path, format='mp3')
	except Exception as e:
		_logger.error(f"Error exporting MP3 audio: {e}")
		_logger.error(traceback.format_exc())  # This will log the full traceback of the exception

	# Now we'll use the OpenAI transcriptions API to transcribe the MP3 audio to text.
	_logger.normal(f"\tConverting audio from user {user_name} in chat {chat_id} to a text transcript using Whisper.")
	try:
		text = transcribeAudio(mp3_file_path)
	except Exception as e:
		await _report_error(conversation, tgMsg,
					  f"In handle_audio(), transcribeAudio() threw an exception: {type(e).__name__} {e}")

		text = f"[Audio transcription error: {e}]"
		# We could also do a traceback here. Should we bother?

	_logger.normal(f'\tUser {user_name} said: "{text}"')

	# Store the text in the audio_text attribute of the context object for later reference.
	context.user_data['audio_text'] = text

	# NOTE: After returning, the normal message handler should still get called.

#__/

def _mp3_to_ogg(filename:str):
	"""Converts an .mp3 file to .ogg format. Returns the name of the .ogg file created."""

	global _duration

	ogg_filename = filename[:-3] + "ogg"

	_logger.normal(f"\tConverting {filename} to {ogg_filename}...")

	audio = AudioSegment.from_file(filename, format="mp3")
	_duration = audio.duration_seconds
	#audio.export(ogg_filename, format="opus", parameters=["-c:a libopus"])
	audio.export(ogg_filename, format="opus", parameters=["-strict -2"])

	return ogg_filename

async def handle_photo(update:Update, context:Context) -> None:
	"""Handles an image message sent by the user."""

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)
		
	if tgMsg is None:
		_logger.warning("In handle_photo() with no message? Aborting.")
		return

	user_name = _get_user_tag(tgMsg.from_user)

	# Get the chat ID.
	chat_id = tgMsg.chat.id

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_photo(); aborting.")
		return

	# Get our Conversation object.
	conversation = context.chat_data['conversation']

	_logger.normal(f"\nReceived a photo message from user {user_name} in chat {chat_id}.")
	
	# Make sure the message actually contains a photo.
	if tgMsg.photo:
		photo = tgMsg.photo
	else:
		_logger.error("A message passed the photo filter, but did not contain a photo.")
		return	# Dispatcher will still try other filters.
	
	# Get the file_id and download the file
	file_id = photo[-1].file_id
		# The [-1] gets the largest available size of photo if it's available in several sizes.
	file_obj = await context.bot.get_file(file_id)

	# Get the value of environment variable AI_DATADIR.
	# This is where we'll save any photo files.
	ai_datadir = AI_DATADIR
	photo_dir = os.path.join(ai_datadir, 'photos')

	# Create a folder to save the photo files if it doesn't exist
	if not os.path.exists(photo_dir):
		os.makedirs(photo_dir)

	# Pick a shorter ID for the file (collisions will be fairly rare).
	short_file_id = f"{random.randint(1,1000000)-1:06d}"

	# Save the audio as a JPEG file
	short_filename = f'{user_name}-{short_file_id}.jpg'
	jpg_file_path = os.path.join(photo_dir, short_filename)
	_logger.normal(f"\tDownloading photo from user {user_name} in chat {chat_id} to JPG file {jpg_file_path}.")
	await file_obj.download_to_drive(jpg_file_path)

	# UPDATE: Now postponing this to analyze_image()/ai_vision() call.
	## Now we'll use the OpenAI GPT-4V model to generate a detailed description of the image.
	#_logger.normal(f"\tConverting image from user {user_name} in chat {chat_id} to a text description using GPT-4V.")
	#try:
	#	text = describeImage(jpg_file_path)
	#except Exception as e:
	#	await _report_error(conversation, tgMsg,
	#		f"In handle_photo(), describeImage() threw an exception: {type(e).__name__} {e}")
	#
	#	text = f"[Image analysis error: {e}]"
	#	# We could also do a traceback here. Should we bother?
	#
	#_logger.normal(f'\tDescription of image from {user_name}: [{text}]')
	#context.user_data['image_text'] = text
	
	# Store the text in the image_text attribute of the context object for later reference.
	context.user_data['image_filename'] = os.path.join('photos', short_filename)

	await handle_message(update, context)

#__/ End async function handle_photo().


	#/==========================================================================
	#| 3.3. Update handler group 2 -- Normal message handlers.
	#|
	#|		These handlers take care of normal message processing.
	#|
	#|			Handler Function	Description
	#|			~~~~~~~~~~~~~~~~	~~~~~~~~~~~
	#|			handle_message()	Process a generic message from a user.
	#|
	#|		They are also supported by the following major functions:
	#|
	#|			process_chat_message()		Special message handling for GPT chat API.
	#|			process_response()			Processes a response returned by the AI.
	#|			send_image()				Sends an image in reply to the user.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Now, let's define a function to handle the rest of the messages.
async def handle_message(update:Update, context:Context, isNewMsg=True) -> None:
		# Note that <context>, in this context, denotes the Telegram context object.
		# Call with new_msg=False to skip new-message processing.

	"""Handles receipt of a text or audio message sent to the bot by a user.
		"""

	# The following code is here in case the user edited
	# an old message instead of sending a new one.

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)
		
	if tgMsg is None:
		_logger.error("In handle_message() with no message! Aborting...")
		return

	text = tgMsg.text

	user_name = _get_user_tag(tgMsg.from_user)
	user_id = tgMsg.from_user.id

	# Get the chat ID.
	chat_id = tgMsg.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not await _ensure_convo_loaded(update, context):
		_logger.error("Couldn't load conversation in handle_message(); aborting.")
		return

		#|----------------------------------------------------------------------
		#| Audio transcripts. If the original message contained audio or voice
		#| data, then present its transcription using an appropriate text
		#| format.

	if isNewMsg and 'audio_text' in context.user_data:	# We added this earlier (in handle_audio) if appropriate.

		# Utilize the transcript created by handle_audio() above.
		text = f"(audio) {context.user_data['audio_text']}"	

		_logger.normal(f"\tGot the audio message: {text}")

		# Append the text caption, if present.
		if tgMsg.caption:
			_logger.normal(f"\tThe audio clip also has a caption: [{tgMsg.caption}]")
			text += f"\n(Caption: {tgMsg.caption})"

		# Clear the audio_text entry from the user_data dictionary
		del context.user_data['audio_text']

		#|----------------------------------------------------------------------
		#| Handling for photo messages. If the original message contained a
		#| photo, then present its description using an appropriate text format.

	got_image = False
	if isNewMsg and 'image_filename' in context.user_data:	# We added this earlier (in handle_photo) if appropriate.
		
		# At this point, we just note the image filename and caption in the message text.
		# We hope that the AI is smart enough to then call the analyze_image() function as needed.

		text = f'''[PHOTO ATTACHMENT; filename="{context.user_data['image_filename']}"]'''

		## Utilize the description created by handle_photo() above.
		#text = f"[PHOTO ATTACHMENT; {BOT_NAME} running visual analysis... detailed_result=```{context.user_data['image_text']}```]"	

		_logger.normal(f"\tGot the photo: {text}")

		# Append the photo's text caption, if present.
		if tgMsg.caption:
			_logger.normal(f"\tThe photo also has a caption: [{tgMsg.caption}]")
			text += f"\n(CAPTION: {tgMsg.caption})"

		# Clear the image_filename entry from the user_data dictionary - don't need it any more.

		del context.user_data['image_filename']
		#del context.user_data['image_text']

		got_image = True

	# If the message was an edited version of an earlier message,
	# make a note of that.
	if edited:
		_logger.normal(f"\nUser {user_name} edited an earlier message in "
					   f"conversation {chat_id}.")
		text = "(edited) " + text

	# If this is a group chat and the message text is empty or None,
	# assume we were just added to the chat, and just delegate to the
	# handle_start() function.
	if chat_id < 0 and (text is None or text == ""):
		_logger.normal(f"Added to group chat {chat_id} by user {user_name}. Auto-starting.")
		#update.message.text = '/start'
		await handle_start(update, context, autoStart=True)
		return

	# Handle null text in other circumstances.
	if not text:
		text = "[null message]"

	# Fetch the conversation object. Do some error handling.

	if 'conversation' not in context.chat_data:
		_logger.error("Conversation object not set in handle_message!!")
		
	conversation = context.chat_data['conversation']

	if not conversation:
		_logger.error("Null conversation object in handle_message()!!")

	# Add the message just received to the conversation.
	if isNewMsg:
		conversation.add_message(BotMessage(user_name, text))
		if got_image:
			conversation.add_message(BotMessage(SYS_NAME,
				f"[NOTE: {BOT_NAME}, please use analyze_image() to inspect the photo attachment]"))

	# Get the current user object, stash it in convo temporarily.
	# (This may be needed later if we decide to block the current user.)
	cur_user = tgMsg.from_user
	conversation.last_user = cur_user

	# Make sure the user is listed in the user database.
	if not _lookup_user(cur_user.id):
		_addUser(cur_user)

	# Check whether the user is in our access list.
	if not _check_access(user_name, user_id=user_id):
		_logger.normal(f"\nUser {user_name} tried to access chat {chat_id}, "
					   "but is not in the access list. Denying access.")

		errMsgStr = f"Sorry, but user {user_name} is not authorized to access {BOT_NAME} bot."
		#errMsgStr = f"Sorry, but {BOT_NAME} bot is offline for now due to cost reasons."

		await _report_error(conversation, tgMsg, errMsgStr, logIt=False)

		return


	# If we are in quiet mode, and we weren't named, and this isn't a command,
	# then don't respond.
	
	if conversation.quiet_mode and (BOT_NAME.lower() not in text.lower()) and text[0]!='/':
		_logger.warning(f"Ignoring a message from user {user_name} in chat {chat_id} because we're in quiet mode.")
		return


	# If the currently selected engine is a chat engine, we'll dispatch the rest
	# of the message processing to a different function that's specialized to use 
	# OpenAI's new chat API.
	if global_gptCore.isChat:
		return await process_chat_message(update, context)


	## Also move the below code to this new function:
	# else:
	#	return await process_text_message(update, context)

	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	At this point, we know that we're using a standard GPT text engine (not
	#|	a GPT chat engine), and we need to query the API with the updated
	#|  context and process its response.
	#|
	#|	We do this inside a while loop, because we may need to retry the query 
	#|	if the response was empty or was a repeat of a message that the bot 
	#|	already sent earlier. Also, we use the loop to allow the AI to generate 
	#|	longer outputs by accumulating results from multiple queries. (However, 
	#|	we need to be careful in this process not to exceed the available space
	#|	in the AI's receptive field.)
	#|
	#|	NOTE: At present, the below algorithm to allow the AI to extend its 
	#|	response and generate longer outputs includes no limit on the length
	#|	of the generated message until the point where it's the only message
	#|	remaining on the receptive field. This may not be desirable, since the
	#|	AI will lose all prior context in the conversation if it generates a
	#|	sufficiently long message. Thus, we may want to add a limit on the 
	#|	length of extended messages at some point in the future. A sensible
	#|	thing to do would be to limit it to the value of the 'max-returned-
	#|	tokens' config parameter, or some new config parameter that is inten-
	#|	ded for this purpose.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# We'll need to keep track of whether we're extending an existing response or starting a new one.
	extending_response = False

	# This Boolean will become True if the response grows so large that we can't extend it further.
	response_maxed_out = False

	# We'll use this variable to accumulate the full response from GPT-3, which can be an
	# accumulation of several responses if the stop sequence is not encountered initially.
	full_response = ""

	while True:		# We'll break out of the loop when we get a complete response that isn't a repeat.

		# First, we need to get the response from GPT-3.
		#	However, we need to do this inside a while/try loop in case we get a PromptTooLargeException.
		#	This happens when the context string is too long for the GPT-3 (as configured) to handle.
		#	In this case, we need to expunge the oldest message from the conversation and try again.
		while True:

			# If we're not extending an existing response, we need to start a new one.	To do this,
			# we add Gladys' prompt to the conversation's context string to generate the full GPT-3
			# context string.  Otherwise, we just use the existing context string.
			if not extending_response:
				context_string = conversation.context_string + AI_PROMPT 

				# At this point, we want to archive the context_string to a file in the
				# log/ directory called 'latest-prompt.txt'. This provides an easy way
				# for the system operator to monitor what the AI is seeing, without
				# having to turn on debug-level logging and search through the log file.

				# Open the file for writing.
				with open(f"{LOG_DIR}/latest-prompt.txt", "w") as f:
					# Write the context string to the file.
					f.write(context_string)

			else:
				context_string = conversation.context_string

			try:
				# Get the response from GPT-3, as a Completion object.
				completion = global_gptCore.genCompletion(context_string)
				response_text = completion.text
				break

			except PromptTooLargeException as e:				# Imported from gpt3.api module.

				_logger.debug("The prompt was too large by {e.byHowMuch} tokens! Trimming...")

				# The prompt is too long.  We need to expunge the oldest message from the conversation.
				# However, we need to do this within a try/except clause in case the only message left
				# in the conversation is the one that we're currently constructing.	 In that case, all
				# we can do is treat however much of the full response that we've received so far as
				# the final response.

				try:
					conversation.expunge_oldest_message()
						# NOTE: If it succeeds, this modifies conversation.context_string.
				except _ConversationError:
					# We can't expunge the oldest message.	We'll just treat
					# the full response as the final response. Also make a
					# note that the size of the response has been maxed out.
					response_text = full_response
					response_maxed_out = True
					break
				
				# We've successfully expunged the oldest message.  We need to try again.
				continue

			except RateLimitError as e:
				# This also may indicate that the server is overloaded
				# or our monthly quota was exceeded.

				# We exceeded our OpenAI API quota or rate limit, or the server was overloaded.
				# There isn't really anything we can do here except send a diagnostic message to the user.

				_logger.error(f"Got a {type(e).__name__} from OpenAI ({e}) for "
							  f"conversation {chat_id}.")

				diagMsgStr = "AI model is overloaded, or monthly quota has "\
					"been reached; please try again later. Quotas reset on "\
					"the 1st of the month."

				await _send_diagnostic(tgMsg, conversation, diagMsgStr, ignore=True)
				return	# That's all she wrote.
			#__/
		#__/

		# Unless the total response length has just maxed out the available space,
		# if we get here, then we have a new chunk of response from GPT-3 that we
		# need to process.
		if not response_maxed_out:

			# When we get here, we have successfully obtained a response from GPT-3.
			# At this point, we need to either construct a new Message object to
			# hold the response, or extend the existing one.
			if not extending_response:
				# We're starting a new response.

				# Generate a debug-level log message to indicate that we're
				# starting a new response.
				_logger.debug(f"Starting new response from {conversation.bot_name} "
							  f"with text: [{response_text}].")

				# Create a new Message object and add it to the conversation, but, don't finalize it yet.
				response_botMsg = BotMessage(conversation.bot_name, response_text)
				conversation.add_message(response_botMsg, finalize=False)

			else:
				# We're extending an existing response.

				# Generate a debug-level log message to indicate that we're
				# extending an existing response.
				_logger.debug(f"Extending response from {conversation.bot_name} "
							  f"with additional text: [{response_text}].")

				# Extend the existing response.
				response_botMsg.text += response_text

				# Add the response to the existing Message object.
				conversation.extend_message(response_botMsg, response_text)

			# Add the response text to the full response.
			full_response += response_text

			# The next thing we do is to check whether the completion ended with a stop sequence,
			# which means the AI has finished generating a response. Alternatively, if the com-
			# pletion ended because it hit the length limit, then we need to loop back and get
			# another response so that the total length of the AI's response isn't arbitrarily
			# limited by the length limit.
			if completion.finishReason == 'length':		# The stop sequence was not reached.

				# Append the response to the context string.
				#conversation.context_string += response_text
				#	NOTE: Commented out because it's already been done by either 
				#			the .add_message() or the .extend_message() call above.

				# Generate an info-level log message to indicate that we're extending the response.
				_logger.info("Length limit reached; extending response.")

				# Remember that we're extending the response.
				extending_response = True

				# Send the user a diagnostic message indicating that we're extending the response.
				# (Doing this temporarily during development.)
				diagMsgStr = "Length limit reached; extending response."
				sendRes = await _send_diagnostic(tgMsg, conversation, diagMsgStr, toAI=False)
				if sendRes != 'success': return sendRes

				continue	# Loop back and get another response extending the existing one.

			#__/ End of if completion.finishReason == 'length':

		#__/ End of if not response_maxed_out:

		# If we get here, then the final completion ended with a stop sequence, or the total length 
		# of a multi-part response got maxed out.

		# Generate an info-level log message to indicate that we're done extending the response.
		_logger.info("Stop sequence reached or response size maxed out; done extending response.")

		# Now, we consider the response text to be the full response that we just accumulated.
		response_text = full_response

		# Strip off any leading or trailing whitespace.
		response_text = response_text.strip()

		## Strip off any trailing whitespace from the response, since Telegram will ignore it anyway.
		#response_text = response_text.rstrip()
		#
		## If the response starts with a space (which is expected, after the '>'), trim it off.
		#response_text = response_text.lstrip(' ')
		##if response_text[0] == ' ':
		##	response_text = response_text[1:]

		# If the response is empty, then return early. (Can't even send an empty message anyway.)
		if response_text == "":
			# Delete the last message from the conversation.
			conversation.delete_last_message()

			## Commenting this out now for production.
			# # Send the user a diagnostic message indicating that the response was empty.
			# # (Doing this temporarily during development.)
			#
			#diagMsg = "Response was empty."
			#await _send_diagnostic(message, conversation, diagMsg, toAI=False, ignore=True)
			#	# Note that this message doesn't get added to the conversation, so it won't be
			#	# visible to the AI, only to the user.

			return		# This means the bot is simply not responding to this particular message.

		# Update the message object, and the context.
		response_botMsg.text = response_text
		conversation.expand_context()

		# If this message is already in the conversation, then we need to retry the query,
		# in hopes of stochastically getting a different response. Note it's important for
		# this to work efficiently that the temperature is not too small. (E.g., 0.1 is 
		# likely to lead to a lot of retries. The default temperature currently is 0.75.)
		#if conversation.is_repeated_message(response_message):
		#	full_response = ""	# Reset the full response.
		#	continue
		# NOTE: Commented out the above, because repeated retries can get really expensive.
		#	Also, retries tend to just yield minor variations in the response, which will
		#	then further exacerbate the AI's tendency to continue repeating the pattern.

		# If this message is already in the conversation, then we'll suppress it, so as
		# not to exacerbate the AI's tendency to repeat itself.	 (So, as a user, if you 
		# see that the AI isn't responding to a message, this may mean that it has the 
		# urge to repeat something it said earlier, but is holding its tongue.)
		if response_text.lower() != '/pass' and conversation.is_repeated_message(response_botMsg):

			# Generate an info-level log message to indicate that we're suppressing the response.
			_logger.info(f"Suppressing response [{response_text}]; it's a repeat.")

			# Delete the last message from the conversation.
			conversation.delete_last_message()

			## Send the user a diagnostic message (doing this temporarily during development).
			#diagMsg = f"Suppressing response [{response_text}]; it's a repeat."
			#await _send_diagnostic(message, conversation, diagMsg, toAI=False, ignore=True)

			return		# This means the bot is simply not responding to the message


		# If we get here, then we have a non-empty message that's also not a repeat.
		# It's finally OK at this point to archive the message and send it to the user.

		# Make sure the response message has been finalized (this also archives it).
		conversation.finalize_message(response_botMsg)

		# At this point, we can break out of the loop and actually send the message.
		break
	#__/ End of while loop that continues until we finish accumulating response text.

	# If we get here, we have finally obtained a non-empty, non-repeat,
	# already-archived message that we can go ahead and send to the user.
	# We also check to see if the message is a command line.

	await process_response(update, context, response_botMsg)	   # Defined later.

#__/ End of handle_message() function definition.


	#/==========================================================================
	#| 3.4. Update handler group 3 -- Unknown command handlers.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

async def handle_unknown_command(update:Update, context:Context) -> None:
	"""Handle an attempted user command that doesn't match any of the known
		command types. We do this by just treating the command like a normal
		text message and letting the AI decide how to handle it."""

	await handle_message(update, context)		# Treat it like a normal message.

#__/ End of handle_unknown_command() function definition.


	#/==========================================================================
	#| 3.5. Telegram error handlers.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Define an error handler for exceptions caught by the dispatcher.
async def handle_error(update:Update, context:Context) -> None:
	"""Log errors caused by updates."""
	_logger.error('Update [\n%s\n] caused error "%s"', pformat(update), context.error, exc_info=True)
#	_logger.error('Update [\n%s\n] caused error "%s"', pformat(update), context.error, exc_info=logmaster.doDebug)
		# This will log the full traceback of the exception if debug logging is turned on.
	#_logger.error(traceback.format_exc())  
#__/


#/=============================================================================|
#|	4. Define AI command/function				 [python module code section]  |
#|		call handler functions. 											   |
#|																			   |
#|		In this section, we define functions that will handle commands		   |
#|		and function calls invoked by the AI. These include:				   |
#|																			   |
#|			ai_activateFunction() - Handles activate_function() AI			   |
#|										function call.						   |
#|																			   |
#|			ai_block() - Handles /block AI command and block_user()			   |
#|								AI function call.							   |
#|																			   |
#|			ai_forget() - Handles /forget AI command and forget_item()		   |
#|								AI function call.							   |
#|																			   |
#|			ai_image() - Handles /image AI command and create_image()		   |
#|								AI function call.							   |
#|																			   |
#|			ai_remember() - Handles /remember AI command and				   |
#|								remember_item() AI function call.			   |
#|																			   |
#|			ai_search() - Handles search_memory() AI function call.			   |
#|																			   |
#|			ai_unblock() - Handles /unblock command and unblock_user()		   |
#|								AI function call.							   |
#|																			   |
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|


# Below are functions to implement commands that may performed by the AI.
# They are: remember, forget, block, and image.
#	* /remember <text> - Adds <text> to persistent memory.
#	* /forget <text> - Removes <text> from persistent memory.
#	* /block [<user>] - Blocks the current user.
#	* /image <desc> - Generates an image with a given text description and sends it to the user.


async def ai_activateFunction(
	updateMsg:TgMsg, botConvo:BotConversation, funcName:str) -> str:

	"""The AI calls this function to activate one of its other functions."""

	chat_id = botConvo.chat_id

	_logger.normal(f"\nIn ai_activateFunction() for chat {chat_id} with funcName='{funcName}'...")

	cur_funcs = botConvo.cur_funcs

	# First, if that function already appears in the list, then delete it,
	# because we don't need it to appear twice.
	cur_funcs = [func for func in cur_funcs if func.get('name') != funcName]
	
	if funcName == 'remember_item':
		cur_funcs += [REMEMBER_ITEM_SCHEMA]

	elif funcName == 'search_memory':
		cur_funcs += [SEARCH_MEMORY_SCHEMA]
	
	elif funcName == 'forget_item':
		cur_funcs += [FORGET_ITEM_SCHEMA]
	
	elif funcName == 'analyze_image':
		cur_funcs += [ANALYZE_IMAGE_SCHEMA]
	
	elif funcName == 'create_image':
		cur_funcs += [CREATE_IMAGE_SCHEMA]
	
	elif funcName == 'block_user':
		cur_funcs += [BLOCK_USER_SCHEMA]
	
	elif funcName == 'unblock_user':
		cur_funcs += [UNBLOCK_USER_SCHEMA]
	
	elif funcName == 'search_web':
		cur_funcs += [SEARCH_WEB_SCHEMA]
		
	elif funcName == 'pass_turn':
		# Do nothing because it's always activated.
		return f"Note: The pass_turn function is always available; activation isn't needed."

	elif funcName == 'activate_function':
		# Do nothing because it's always activated.
		return f"Note: The activate_function function is always available; activation isn't needed."

	else:
		_logger.error(f"AI tried to activate an unknown function '{funcName}'.")
		return f"Error: Unknown function name '{funcName}'."

	botConvo.cur_funcs = cur_funcs

	_logger.normal(f"\tAI activated function '{funcName}'.")

	func_names = [func['name'] for func in cur_funcs if 'name' in func]
	_logger.normal(f"\tCurrent function list is: {func_names}.")

	return f"Success: Function {funcName} has been activated."

#__/


# Define a function to handle the /block command, when issued by the AI.
async def ai_block(updateMsg:TgMsg, conversation:BotConversation,
				   userToBlock:str=None, userIDToBlock:int=None) -> str:

	"""The AI calls this function to block the given user, who may be specified
		by tag (if unique) or by ID. If no user is specified, it blocks the
		current user (the one who sent the current update)."""
	
	_logger.normal(f"In ai_block() with userToBlock={userToBlock}, userIDToBlock={userIDToBlock}...")

	# Put the message from the Telegram update in a convenient variable.
	message = updateMsg

	# Retrieve the current user's name & ID, in case we need it.
	user_name = _get_user_tag(message.from_user)
	cur_user_id = message.from_user.id

	# Retrieve the conversation's chat ID.
	chat_id = conversation.chatID	# Public property. Type: int.

	# The following code used to appear directly inside handle_response(), but I've
	# moved it here to make it easier to call it from other places, such as the
	# code to handle function-call responses from the AI.

	# If no user was specified, then we'll block the current user.
	if userToBlock == None and userIDToBlock == None:
		userToBlock = user_name
		userIDToBlock = cur_user_id
		_logger.normal(f"\tDefaulting to current user {userToBlock}, ID={userIDToBlock}.")

	## If we don't have a user ID, complain and die.
	#if userIDToBlock is None:
	#	await _report_error(conversation, message,
	#						"Blocking users by tag is no longer supported."))
	#	return "internal error in ai_block()"

	# If we're given a user ID, we'll use that; if we only have a user tag,
	# we'll check whether the tag is unique, and if so we'll use it.

	if userIDToBlock is None:

		matchingUsers = _lookup_user_by_tag(userToBlock)

		if len(matchingUsers) > 1:
			_logger.warn(f"\tCan't block user '{userToBlock}' because tag isn't unique.")
			diagMsg = f"Can't block user by name tag '{userToBlock}' because "\
					  "it isn't unique."
			return_msg = f"Error: User name tag {userToBlock} is not unique! "\
				"Try blocking by the user's unique username or numeric ID instead. "\
				"Or, to block the current user, call block_user() with no argument."

			# Send diagnostic message to AI and to user.
			sendRes = await _send_diagnostic(message, conversation, diagMsg)
			if sendRes != 'success': return sendRes

			return return_msg

		# If there are no matches, try searching by username instead.
		if len(matchingUsers) == 0:
		
			matchingUsers = _lookup_user_by_username(userToBlock)

			# If there are no matches, try searching by display name instead.
			if len(matchingUsers) == 0:

				matchingUsers = _lookup_user_by_dispname(userToUnblock)

				if len(matchingUsers) != 1:
					_logger.warn(f"\tUser name '{userToBlock}' wasn't found or isn't unique.")

					diagMsg = f"Can't block user named '{userToBlock}' because "\
						  f"{len(matchingUsers)} with that name were found. "\
						  "Try blocking by first name, username, or user ID "\
						  "instead."

					return_msg = f"Error: User name {userToBlock} was not found "\
								 "or is not unique!"

					# Send diagnostic message to AI and to user.
					sendRes = await _send_diagnostic(message, conversation, diagMsg)
					if sendRes != 'success': return sendRes
					
					return return_msg
			
				#__/
			#__/
		#__/

		# Retrieve the user's ID.
		userIDToBlock = matchingUsers[0]['userID']

	#__/ End if ID not yet known.

	# By the time we get here, we definitely know the ID of the user to block.

	# Retrieve the user tag if we don't have it yet.
	if userToBlock is None:

		userData = _lookup_user(userIDToBlock)
		userToBlock = userData['userTag']

	# Generate a warning-level log message to indicate that we're blocking the user.
	_logger.warn(f"***ALERT*** The AI is blocking user '{userToBlock}' "\
				 f"(ID={userIDToBlock}) in conversation {chat_id}.")

	# Check if they're already blocked; else block them.
	if _isBlockedByID(userIDToBlock):
		_logger.warn(f"User '{userToBlock}' is already blocked.")
		diagMsg = f'User {userToBlock} has already been blocked by {BOT_NAME}.'
		return_msg = f"Note: User {userToBlock} is already blocked!"
	else:
		success = _blockUserByID(userIDToBlock)
		if success:
			diagMsg = f'{BOT_NAME} has blocked user {userToBlock}.'
			return_msg = f"Success: blocked user {userToBlock}."
		else:
			error = _lastError	# Fetch the error message.
			await _report_error(conversation, message, error)
			# No other diagnostics needed; just return.
			return 'FAILED: blocking the app developer is not allowed'
	
	# Send diagnostic message to AI and to user.
	sendRes = await _send_diagnostic(message, conversation, diagMsg)
	if sendRes != 'success': return sendRes

	return return_msg

#__/ End of ai_block() function definition.
				

# Define a function to handle the /forget command, when issued by the AI.
async def ai_forget(updateMsg:TgMsg, conversation:BotConversation,
					textToDel:str=None, itemToDel:str=None) -> str:
	"""The AI calls this function to remove the given text from its persistent memory."""

	# Put the message from the Telegram update in a convenient variable.
	message = updateMsg

	# Retrieve the conversation's chat ID.
	chat_id = conversation.chatID	# Public property. Type: int.

	# The following code used to appear directly inside handle_response(), but I've
	# moved it here to make it easier to call it from other places, such as the
	# code to handle function-call responses from the AI.

	# Check for missing <textToDel> argument.
	if textToDel == None and itemToDel == None:
		_logger.error(f"The AI sent a /forget command with no " \
					  f"argument in conversation {chat_id}.")

		diagMsg = "/forget command needs an argument."
		sendRes = await _send_diagnostic(message, conversation, diagMsg)
		if sendRes != 'success': return sendRes

		return "error: missing required argument"
	#__/

	_logger.normal("Deleting a memory item in chat #{chat_id}.")
	_deleteMemoryItem(item_id=itemToDel, text=textToDel)
	# For now we assume it always succeeds.

	if itemToDel is not None:
		return f"Success: item with ID [{itemToDel}] was deleted from memory."
	elif textToDel is not None:
		return f"Success: item with text [{textToDel}] was deleted from memory."

	# We should never get here, but just in case.
	return "unexpected error"

	## Obsolete code below here.

	# Tell the conversation object to remove the given message
	# from the AI's persistent memory.  The return value from
	# this call is True if the message was found and removed,
	# and False if it wasn't.

	if conversation.remove_memory(textToDel):

		# Log this at normal level.
		_logger.normal(f"\tThe AI removed [{textToDel}] from persistent memory in conversation {chat_id}.")

		# Also notify the AI & user that we're forgetting the given statement.
		diagMsg = f"Removed [{textToDel}] from persistent memory."
		sendRes = await _send_diagnostic(message, conversation, diagMsg)
		if sendRes != 'success': return sendRes
		
		return "success"	# Processed AI's /forget command successfully.

	else:

		errmsg = _lastError
		
		# Log this at ERROR level.
		_logger.error("The AI tried & failed to remove "
						f"[{textToDel}] from persistent memory in "
						f"conversation {chat_id}; error: {errmsg}.")

		# Also notify the user that we couldn't forget the given statement.
		diagMsg = f"Could not remove [{textToDel}] from persistent " \
					f'memory. Error message was: "{_lastError}"'
		sendRes = await _send_diagnostic(message, conversation, diagMsg)
		if sendRes != 'success': return sendRes
		
		return f"error: {errmsg}"

#__/ End of ai_forget() function definition.


async def ai_vision(update:Update, context:Context, filename:str,
					verbosity:str=None, query:str=None
	) -> str:


	# Get the message, or edited message from the update.
	(message, edited) = _get_update_msg(update)

	# Get the chat_id, user_name, and conversation object.
	chat_id = message.chat.id
	user_name = _get_user_tag(message.from_user)
	conversation = context.chat_data['conversation']

	fullpath = os.path.join(AI_DATADIR, filename)

	# Now we'll use the OpenAI GPT-4V model to generate a description of the image.

	if filename.startswith('image'):
		who_from = BOT_NAME
	else:
		who_from = f"user {user_name}"

	_logger.normal(f"\nConverting image {filename} from {who_from} in chat {chat_id} to a {verbosity} text description using GPT-4V.")
	if query:
		_logger.normal(f"\t(And also asking the question: {query})")

	try:
		text = describeImage(fullpath, verbosity=verbosity, query=query)
	except Exception as e:
		await _report_error(conversation, message,
			f"In handle_photo(), describeImage() threw an exception: {type(e).__name__} {e}")

		text = f"[Image analysis error: {e}]"
		# We could also do a traceback here. Should we bother?
	
	_logger.normal(f'\tDescription of image from {who_from}: [{text}]')
	
	return text

#__/ End async function ai_vision().


DAILY_IMAGE_LIMIT = 5

# Define a function to handle the /image command, when issued by the AI.
async def ai_image(update:Update, context:Context, imageDesc:str,
				   shape:str=None, style:str=None, caption:str=None	#, remaining_text:str=None
	) -> str:

	# Get the message, or edited message from the update.
	(message, edited) = _get_update_msg(update)

	# Get the chat_id, user_name, and conversation object.
	chat_id = message.chat.id
	user_name = _get_user_tag(message.from_user)
	conversation = context.chat_data['conversation']

	# Make sure that too many images haven't been generated today in this chat.

	if user_name == 'Michael':	# Michaels are blessed with an infinite image limit.
		daily_image_limit = float('inf')	# Infinite images.
	else:
		daily_image_limit = DAILY_IMAGE_LIMIT	# Global defined above.

	if 'last_image_date' in context.chat_data:	# Have we generated images in this convo?

		# Let's check whether the most recent one generated was earlier on this same date.
		if context.chat_data['last_image_date'] == get_current_date():
			
			if context.chat_data['nimages_today'] >= daily_image_limit:
				_logger.warning(f"Daily image generation limit reached in chat {chat_id}.")

				diagMsg = f"Image generation rate limit of {daily_image_limit} has been reached in this chat. Try again tomorrow!"

				sendRes = await _send_diagnostic(message, conversation, diagMsg)
				if sendRes != 'success': return sendRes

				return "error: daily image generation rate limit reached in this chat"

			#__/ End if reached daily image limit.

		#__/ End if it's still the same day as last image.

		# The following else case isn't really needed...

		else:	# It's a new day!
			
			context.chat_data['nimages_today'] = 0		# No images generated today yet!
			_logger.normal(f"No images generated yet today in chat {chat_id}! Resetting counter.")

		#__/ End new-day case.

	#__/ End if images previously generated in this chat session.

	#if user_name != "Michael":
	#	_logger.warning(f"Image generation disabled for users other than Michael.")
	#
	#	diagMsg = "Turbo's image generation capability is presently disabled due to excessive usage."
	#
	#	sendRes = await _send_diagnostic(message, conversation, diagMsg)
	#	if sendRes != 'success': return sendRes
	#
	#	return "note: image generation capability is presently disabled"

	# Error-checking for null argument.
	if imageDesc == None or imageDesc=="":
		_logger.error(f"The AI sent an /image command with no argument in conversation {chat_id}.")

		diagMsg = "/image command needs an argument."
		sendRes = await _send_diagnostic(message, conversation, diagMsg)
		if sendRes != 'success': return sendRes

		return "error: null image description"

	# Process the "shape" parameter.
	if shape is None:
		shape = "square"	# Default

	if shape == "square":
		size = "1024x1024"
	elif shape == "portrait":
		size = "1024x1792"
	elif shape == "landscape":
		size = "1792x1024"
	else:
		_logger.warn(f"\tUnknown shape name '{shape}'; reverting to 'square'.")
		# Show the AI the warning too.
		conversation.add_message(BotMessage(SYS_NAME, f"Warning: Shape '{shape}' is invalid; defaulting to 'square'."))
		size = "1024x1024"

	# Process the "style" parameter.
	if style is None:
		style = 'vivid'
	if style == 'photorealistic':
		style = 'natural'
	if style != 'vivid' and style != 'natural':
		_logger.warn(f"\tUnknown style '{style}'; reverting to 'natural'.")
		style = 'natural'

	# Generate and send an image described by the /image command argument string.
	_logger.normal(f"\nGenerating a {style} {shape} image with description "
					f"[{imageDesc}] for user '{user_name}' in "
					f"conversation {chat_id}.")
	if caption:
		_logger.normal(f"\tAn image caption [{caption}] was also specified.")

	# Attempt to actually generate and send the image.
	send_result = await send_image(update, context, imageDesc, dims=size, style=style, caption=caption)

	if send_result is None:
		return f'Error: Failed to generate and send image to the user.'

	(image_url, new_desc, save_filename) = send_result

	# Make a note in conversation archive to indicate that the image was sent.
	#conversation.add_message(BotMessage(SYS_NAME, f'[Generated and sent image "{new_desc}" in filename "{save_filename}"]'))
	# ^^^ The above isn't really necessary any more...

	## NOTE: This is now done in process_command() more generically.
	# Send the remaining text after the command line, if any, as a normal message.
	#if remaining_text != None and remaining_text != '':
	#	await send_response(update, context, remaining_text)

	# This doesn't work, because the URL is only accessible from this server.
	#return f"Success: image has been generated and sent to user. Temporary URL=({image_url})."

	return f'Success: image with revised description "{new_desc}" has been generated in file "{save_filename}" and sent to user.'

#__/ End of ai_image() function definition.


# Define a function to handle the /remember command, when issued by the AI.
async def ai_remember(updateMsg:TgMsg, conversation:BotConversation, textToAdd:str,
					  isPublic:bool=False, isGlobal:bool=False) -> str:

	"""The AI calls this function to add the given text to its persistent
		memory."""

	# Put the message from the Telegram update in a convenient variable.
	message = updateMsg
	user = message.from_user

	# Get user info.
	user = message.from_user
	user_name = _get_user_tag(user)

	# Retrieve the conversation's chat ID.
	chat_id = conversation.chatID	# Public property. Type: int.

	# All the following code used to appear directly inside handle_response(),
	# but I've moved it here to make it easier to call it from other places,
	# such as the new code to handle function-call responses from the AI.

	# Check for missing <textToAdd> argument.
	if textToAdd == None:
		_logger.error(f"The AI sent a /remember command with no "
						f"argument in conversation {chat_id}.")

		diagMsg = "/remember command needs an argument."
		sendRes = await _send_diagnostic(message, conversation, diagMsg)
		if sendRes != 'success': return sendRes
		
		return "error: missing required argument"
	#__/

	# Diagnostic.
	_logger.normal(f"\nFor user {user_name} in chat {chat_id}, adding "
					f"{'public' if isPublic else 'private'} "
					f"{'global' if isGlobal else 'local'} memory ["
					f"{textToAdd}].")

	newItemID = _addMemoryItem(user.id, chat_id, textToAdd, isPublic, isGlobal)
	return f"Success: created new memory item {newItemID}"

	# Obsolete code below.

	# Tell the conversation object to add the given message to the AI's persistent memory.
	if not conversation.add_memory(textToAdd):
		
		errmsg = _lastError

		# Generate an error-level report to include in the application log.
		_logger.error(f"The AI tried & failed to add memory: [{textToAdd}]")

		diagMsg = f"Could not add [{textToAdd}] to persistent memory. " \
					f'Error message was: "{errmsg}"'

		# Send the diagnostic message to the user.
		sendRes = await _send_diagnostic(message, conversation, diagMsg)
		if sendRes != 'success': return sendRes

		return "error: unable to add memory item"
	#__/


	_logger.normal(f"\tThe AI added [{textToAdd}] to persistent memory in conversation {chat_id}.")

	# Also notify the user that we're remembering the given statement.
	diagMsg = f"Added [{textToAdd}] to persistent memory."

	# Send the diagnostic message to the user.
	sendRes = await _send_diagnostic(message, conversation, diagMsg)
	return sendRes

#__/ End of ai_remember() function definition.
				

# Number of items that the search_memory function returns by default.

DEFAULT_SEARCHMEM_NITEMS	= 3

# Call this later to reinitialize the default based on the engine's
# receptive field (context window) size.
def _adjust_searchmem_defaults():
	global DEFAULT_SEARCHMEM_NITEMS
	
	fieldSize = getFieldSize(ENGINE_NAME)
	if fieldSize > 16000:	# Current 3.5 and 4 Turbo models are in this range.
		DEFAULT_SEARCHMEM_NITEMS = 10
	elif fieldSize > 8000:	# The original GPT-4 was in this category.
		DEFAULT_SEARCHMEM_NITEMS = 5

	# ^ NOTE: Reasonable defaults. Do not recommend setting this higher than 10.


async def ai_search(updateMsg:TgMsg, conversation:BotConversation,
					queryPhrase:str, nItems:int=DEFAULT_SEARCHMEM_NITEMS
			) -> list:

	"""Do a context-sensitive semantic search for memory items that
		are related to the query phrase. Returns the closest few
		matching items (by default 3)."""

	userID = updateMsg.from_user.id
	chatID = conversation.chat_id

	# Cap nItems at 10.
	maxn = MAXIMUM_SEARCHMEM_NITEMS
	if nItems > maxn:

		_logger.warn(f"{nItems} search results requested; capping to {maxn}.")

		warning_msgStr = f"WARNING: {nItems} search results were requested, "\
			f"but returning more than {maxn} items from a memory search is "\
			f"not supported. Limiting search to top {maxn} results."

		nItems = maxn

			# Make sure the AI sees that message, even if we fail in sending it to the user.
		conversation.add_message(BotMessage(SYS_NAME, warning_msgStr))
		
            # Also send the warning message to the user. (Making it clear that 
            # it's a system message, not from the AI persona itself.)
		reply_msgStr = f"[SYSTEM {warning_msgStr}]"
		await _reply_user(updateMsg, conversation, reply_msgStr, ignore=True)

	#__/

	_logger.normal(f"In chat {chatID}, for user #{userID}, AI is searching for the top {nItems} memories matching the search query: [{queryPhrase}].")
	matchList = _searchMemories(userID, chatID, queryPhrase, nItems=nItems)

	_logger.normal(f"Found the following matches: [\n{matchList}\n].")

	return matchList

#__/


# Default list of sections that should be returned by a Bing search.
DEFAULT_BINGSEARCH_SECTIONS = ['webPages', 'relatedSearches']
#DEFAULT_BINGSEARCH_SECTIONS = ['webPages']
	# We made this smaller to increase the chance Turbo can handle it.

def trim(s:str, n:int=30):
	s = str(s)	# Force it to str
	if len(s) <= n:
		return s
	else:
		return s[:n] + "..."

# Define a function to handle the AI's search_web() function.
async def ai_searchWeb(updateMsg:TgMsg, botConvo:BotConversation,
					   queryPhrase:str, maxResults:int=None, locale:str="en-US",
					   sections:list=DEFAULT_BINGSEARCH_SECTIONS) -> str:

	"""Do a web search using the Bing API."""

	global _lastError

	userID = updateMsg.from_user.id
	chatID = botConvo.chat_id

	_logger.normal(f"\nIn chat {chatID}, for user #{userID}, AI is doing a web search in the {locale} locale for {sections} on: [{queryPhrase}].")
	
	# Calculate how many items to return based on GPT's field size.
	fieldSize = global_gptCore.fieldSize	# Retrieve property value.
		# Total space in tokens for the AI's receptive field (context window).

	if fieldSize >= 16000:		# 16k models and up
		howMany = 8
	elif fieldSize >= 8000:		# GPT-4 and higher
		howMany = 5
	elif fieldSize >= 4000:		# GPT-3.5 and higher
		howMany = 3
	else:
		_logger.warn(f"This model has only {fieldSize} tokens. Web search results may overwhelm it.")

		howMany = 2		# This is not very useful!

	# Cap number of results at whatever the AI suggested.
	if maxResults and maxResults < howMany:
		howMany = maxResults

	try:
		# This actually does the search.
		searchResult = _bing_search(queryPhrase, market=locale, count=howMany)

		#_logger.debug(f"Raw search result:\n{pformat(searchResult)}")

		# Create a fresh dict for the fields we want to keep.
		cleanResult = dict()

		# Keep only the fields we care about in our "cleaned" result.
		for (key, val) in searchResult.items():
			if key in sections:
				cleanResult[key] = val

		# If we found nothing, retry with the default section list.
		if not cleanResult:
			sections = DEFAULT_BINGSEARCH_SECTIONS
			for (key, val) in searchResult.items():
				if key in sections:
					cleanResult[key] = val

		# Strip out 'deepLinks' etc. out of the webPages value, it's TMI.
		npages = 0
		_logger.normal("\t\tLooking for webPages section...")
		if 'webPages' in cleanResult:
			#_logger.normal("Found webPages section...")
			for result in cleanResult['webPages']['value']:

				npages += 1
				_logger.normal(f"\t\t\tExamining web page result #{npages}...")

				if 'cachedPageUrl' in result:
					_logger.normal(f"\t\t\t\tDeleting cachedPageUrl: {trim(result['cachedPageUrl'])}")
					del result['cachedPageUrl']

				if 'contractualRules' in result:
					_logger.normal(f"\t\t\t\tDeleting contractualRules: {trim(result['contractualRules'])}")
					del result['contractualRules']

				if 'deepLinks' in result:
					_logger.normal(f"\t\t\t\tDeleting deepLinks: {trim(result['deepLinks'])}")
					del result['deepLinks']

				if 'primaryImageOfPage' in result:
					_logger.normal(f"\t\t\t\tDeleting primaryImageOfPage: {trim(result['primaryImageOfPage'])}")
					del result['primaryImageOfPage']

				if 'richFacts' in result:
					_logger.normal(f"\t\t\t\tDeleting richFacts: {trim(result['richFacts'])}")
					del result['richFacts']

				if 'video' in result:
					_logger.normal(f"\t\t\t\tDeleting video: {trim(result['video'])}")
					del result['video']

				if 'about' in result:
					_logger.normal(f"\t\t\t\tDeleting about: {trim(result['about'])}")
					del result['about']

				if 'isNavigational' in result:
					_logger.normal(f"\t\t\t\tDeleting isNavigational: {trim(result['isNavigational'])}")
					del result['isNavigational']


		# Strip a bunch of useless fields out of news values.
		if 'news' in cleanResult:
			for result in cleanResult['news']['value']:
				if 'about' in result:
					del result['about']
				if 'category' in result:
					del result['category']
				if 'contractualRules' in result:
					del result['contractualRules']
				if 'image' in result:
					del result['image']
				if 'mentions' in result:
					del result['mentions']
				if 'provider' in result:
					del result['provider']
				if 'video' in result:
					del result['video']
		

		# Return as a string (to go in content field of function message).
		#return json.dumps(cleanResult)

		# Format the result with tabs to make it easier for Turbo/Max to parse.
		pp_result = json.dumps(cleanResult, indent=4)
		#pp_result = pformat(cleanResult, indent=4)		# Maybe too much indents
		tabbed_result = pp_result.replace(' '*8, '\t')
		return tabbed_result

	except SearchError as e:
		# We'll let the AI know it failed

		errMsg = f"{type(e).__name__} exception: {e}"

		botConvo.add_message(BotMessage(SYS_NAME, f"[ERROR: {errMsg}]"))
		return errMsg

		#botConvo.add_message(BotMessage(SYS_NAME, f"[ERROR: {_lastError}]"))
		#return _lastError
		#	^ Commented this out because using errMsg is cleaner.

		#return "Error: Unsupported locale / target market for search."
		#	^ Commented out since this may or may not be the correct error.
		#		We now also have BingQuotaExceeded exceptions.

#__/


# Define a function to handle the /unblock command, when issued by the AI.
async def ai_unblock(updateMsg:TgMsg, conversation:BotConversation,
					 userToUnblock:str=None, userIDToUnblock:int=None) -> str:

	"""The AI calls this function to unblock the given user. If no user is specified,
		it unblocks the current user (the one who sent the current update).
		(Note this case will normally never occur.)
	"""
	
	_logger.normal(f"In ai_unblock() with userToUnblock={userToUnblock}, userIDToUnblock={userIDToUnblock}...")

	# Put the message from the Telegram update in a convenient variable.
	message = updateMsg

	# Retrieve the current user's name, in case we need it.
	user_name = _get_user_tag(message.from_user)
	cur_user_id = message.from_user.id

	# Retrieve the conversation's chat ID.
	chat_id = conversation.chatID	# Public property. Type: int.

	# The following code used to appear directly inside handle_response(), but I've
	# moved it here to make it easier to call it from other places, such as the
	# code to handle function-call responses from the AI.

	## If we don't have a user ID, complain and die.
	#if userIDToUnblock is None:
	#	await _report_error(conversation, message,
	#						"Unblocking users by tag is no longer supported."))
	#	return "internal error in ai_unblock()"

	# If no user was specified, then we'll unblock the current user.
	if userToUnblock == None and userIDToUnblock == None:
		userToUnblock = user_name
		userIDToBlock = cur_user_id
		_logger.normal(f"\tDefaulting to current user {userToUnblock}, ID={userIDToUnblock}.")

	# If we know the user tag to block, but not the user ID, we have to 
	# try to guess the correct user ID.

	if userIDToUnblock is None:

		matchingUsers = _lookup_user_by_tag(userToUnblock)

		if len(matchingUsers) > 1:

			_logger.warn(f"\tCan't unblock user '{userToUnblock}' because tag isn't unique.")
			diagMsg = f"Can't unblock user by name tag '{userToUnblock}' "\
					  "because it isn't unique. Try unblocking by username "\
					  "or user ID instead."
			return_msg = f"Error: User name tag {userToUnblock} is not unique!"

			# Send diagnostic message to AI and to user.
			sendRes = await _send_diagnostic(message, conversation, diagMsg)
			if sendRes != 'success': return sendRes

			return return_msg

		# If there are no matches, try searching by username instead.
		if len(matchingUsers) == 0:

			matchingUsers = _lookup_user_by_username(userToUnblock)

			# If there are no matches, try searching by display name instead.
			if len(matchingUsers) == 0:

				matchingUsers = _lookup_user_by_dispname(userToUnblock)

				if len(matchingUsers) != 1:
					_logger.warn(f"\tUser name '{userToUnblock}' wasn't found or isn't unique.")

					diagMsg = f"Can't unblock user named '{userToUnblock}' because "\
							  f"{len(matchingUsers)} with that name were found. "\
							  "Try unblocking by first name, username, or user ID "\
							  "instead."

					return_msg = f"Error: User name {userToUnblock} was not found "\
								 "or is not unique."

					# Send diagnostic message to AI and to user.
					sendRes = await _send_diagnostic(message, conversation, diagMsg)
					if sendRes != 'success': return sendRes
					
					return return_msg

				#__/
			#__/
		#__/

		# Retrieve the user's ID.
		userIDToUnblock = matchingUsers[0]['userID']

	#__/ End if ID not yet known.

	# By the time we get here, we definitely know the ID of the user to unblock.

	# Retrieve the user tag if we don't have it yet.
	if userToUnblock is None:
		userData = _lookup_user(userIDToUnblock)
		userToUnblock = userData['userTag']

	# Generate a warning-level log message to indicate that we're blocking the user.
	_logger.warn(f"***ALERT*** The AI is unblocking user '{userToUnblock}' "\
				 f"in conversation {chat_id}.")

	# Check if they're already unblocked; else block them.
	if not _isBlockedByID(userIDToUnblock):
		_logger.error(f"User '{userToUnblock}' is not blocked.")
		diagMsg = f'User {userToUnblock} is not currently blocked by {BOT_NAME}.'
		return_msg = f"User {userToUnblock} is not blocked!"
	else:
		# This always succeeds.
		_unblockUserByID(userIDToUnblock)
		diagMsg = f'{BOT_NAME} has unblocked user {userToUnblock}.'
		return_msg = f"Success: unblocked user {userToUnblock}."
	
	# Send diagnostic message to AI and to user.
	sendRes = await _send_diagnostic(message, conversation, diagMsg)
	if sendRes != 'success': return sendRes

	return return_msg

#__/ End of ai_unblock() function definition.
				

#/=============================================================================|
#|	5. Define misc. functions.					 [python module code section]  |
#|																			   |
#|		In this section, we define miscellaneous functions that will		   |
#|		be called from various points later in the program. We do this		   |
#|		before initializing most of the module-level globals, since			   |		   
#|		some of these functions	will get called in the process of ini-		   |
#|		tializing the globals.												   |
#|																		   	   |
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

	#|==========================================================================
	#|	5.1. Misc. major/public functions.			[python module code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

async def ai_call_function(update:Update, context:Context, funcName:str, funcArgs:dict) -> str:

	"""Call the named AI-available function with the given argument dict. Returns a result string."""

	# Get the user message, or edited message from the update.
	(message, edited) = _get_update_msg(update)
	
	# Get the chat_id, user_name, and conversation object.
	chat_id = message.chat.id
	user_name = _get_user_tag(message.from_user)
	user_id = message.from_user.id
	conversation = context.chat_data['conversation']
	
	# Dispatch on the function name. See FUNCTIONS_LIST.
	if funcName == 'remember_item':

		# Get the arguments.

		textToAdd = funcArgs.get('text', None)

		isPrivate = funcArgs.get('is_private', True)
			# Is this information considered private
			# to the specific user or group chat?

		isGlobal = funcArgs.get('is_global', False)
			# Is this information available for the
			# AI to see in any context?

		if textToAdd:
			return await ai_remember(message, conversation, textToAdd,
									 isPublic=not isPrivate, isGlobal=isGlobal)
		else:
			await _report_error(conversation, message,
					f"remember_item() missing required argument text.")
			return "Error: Required argument text is missing."

	elif funcName == 'search_memory':

			# Get the arguments.

		queryPhrase = funcArgs.get('query_phrase', None)
		maxResults = funcArgs.get('max_results', DEFAULT_SEARCHMEM_NITEMS)

		if queryPhrase:
			return await ai_search(message, conversation, queryPhrase,
								   nItems=maxResults)
			
		else:
			await _report_error(conversation, message,
					f"search_memory() missing required argument query_phrase.")
			return "Error: Required argument query_phrase is missing."

	elif funcName == 'forget_item':
		itemToDel = funcArgs.get('item_id', None)
		textToDel = funcArgs.get('text', None)

		if itemToDel:
			return await ai_forget(message, conversation, itemToDel=itemToDel)
		elif textToDel:
			return await ai_forget(message, conversation, textToDel=textToDel)
		else:
			await _report_error(conversation, message,
					f"forget_item() missing required argument item_id or text.")
			return "Error: Required argument (item_id or text) is missing."

	elif funcName == 'analyze_image':

		filename	= funcArgs.get('filename',	None)		# A real value is required.
		verbosity	= funcArgs.get('verbosity', 'medium')
		query		= funcArgs.get('query',		None)

		if filename:
			return await ai_vision(update, context, filename, verbosity=verbosity, query=query)
		else:
			await _report_error(conversation, message,
					f"analyze_image() missing required argument 'filename'.")
			return "Error: Required argument 'filename' is missing."

	elif funcName == 'create_image':
		
		imageDesc = funcArgs.get('description', None)
		shape	  = funcArgs.get('shape', None)
		style	  = funcArgs.get('style', None)
		caption	  = funcArgs.get('caption', None)

		if imageDesc:
			return await ai_image(update, context, imageDesc, shape=shape, style=style, caption=caption)
		else:
			await _report_error(conversation, message,
					f"create_image() missing required argument 'description'.")
			return "Error: Required argument 'description' is missing."

	elif funcName == 'block_user':

		# NOTE: Blocking users by tag may not always work, since tags are not unique.
		userToBlock = funcArgs.get('user_name', None)
		userIDToBlock = funcArgs.get('user_id', None)
			# Defaulting to None will allow ai_block() to figure out the user to block.

		# We can't uncomment this yet because AI can't retrieve ID yet.
		#userIDToBlock = funcArgs.get('user_id', user_id)		# Specified by ID.

		return await ai_block(message, conversation, userToBlock=userToBlock, userIDToBlock=userIDToBlock)

	elif funcName == 'unblock_user':

		# NOTE: Unblocking users by tag may not always work, since tags are not unique.
		userToUnblock = funcArgs.get('user_name', user_name)		# Default to current user.
		userIDToUnBlock = funcArgs.get('user_id', None)

		return await ai_unblock(message, conversation, userToUnblock)

	elif funcName == 'search_web':

		queryPhrase = funcArgs.get('query', None)
		maxResults = funcArgs.get('max_results', None)
		searchLocale = funcArgs.get('locale', 'en-US')
		resultSections = funcArgs.get('sections', DEFAULT_BINGSEARCH_SECTIONS)
		if isinstance(resultSections, str):
			try:
				resultSections = json.loads(resultSections)
			except json.JSONDecodeError:
				pass
		
		if queryPhrase:
			return await ai_searchWeb(message, conversation, queryPhrase,
							maxResults=maxResults, locale=searchLocale,
							sections=resultSections)
		else:
			await _report_error(conversation, message,
					f"search_web() missing required argument 'query'.")
			return "Error: Required argument 'query' is missing."

	elif funcName == 'activate_function':

		funcName = funcArgs.get('func_name', None)
		if funcName:
			return await ai_activateFunction(message, conversation, funcName)
		else:
			await _report_error(conversation, message,
					f"activate_function() missing required argument 'func_name'.")
			return "Error: Required argument 'func_name' is missing."

	elif funcName == 'pass_turn':
		_logger.normal(f"\nNOTE: The AI is passing its turn in conversation {chat_id}.")

		return PASS_TURN_RESULT

	else:
		await _report_error(conversation, message,
							f"AI tried to call an undefined function '{funcName}()'.")
		return f"error: {funcName} is not an available function"

#__/ End definition of private function ai_call_function().


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	get_ai_response()							[public async function]
		#|
		#| 		This is a new function we're adding to generically handle
		#| 		situations where we want to get a response from the AI and
		#| 		process it. This is a little more general than the original
		#|		process_chat_message() function, because it is able to also
		#| 		handle cases where the AI is responding to one or more se-
		#|		quences of function calls and returns, which are not main-
		#|		tained formally in the normal BotConversation data struc-
		#|		ture, since they are not technically part of the conversa-
		#|		tion but are only "inside the AI's head," so to	speak. Al-
		#|		so, we don't currently have any support for	storing and se-
		#|		rializing these alternative types of messages.
		#|
		#|		NOTE: We assume the following preconditions have all been
		#|		ensured to be true by the time that the get_ai_response()
		#|		function is called:
		#|															   
		#|			1. The bot conversation has already been initialized
		#|				and stashed in context.chat_data['conversation'].
		#|																	   
		#|			2. We've checked to make sure the update includes a 
		#|				user message.
		#|
		#|			3. The user's text or audio message, if any, has al-
		#|				ready been retrieved from the update, transcribed
		#|			    to text (if audio) and added to the bot conversa-
		#|				tion object.
		#|
		#|			4. If the AI has called any functions since the last
		#|				user message, their call and return objects are 
		#|				included in the oaiMsgList argument (which should
		#|				also include as much of the conversation as will
		#|				fit).											   
		#|
		#|			5. If oaiMsgList is provided, it should end in an ap-
		#|				propriate system prompt.
		#|
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

async def get_ai_response(update:Update, context:Context, oaiMsgList=None) -> None:

	# NOTE: oaiMsgList should be supplied ONLY if there is a pre-existing
	# message list which includes messages with role 'function_call' or
	# 'function' (meaning function return) that we need to expand upon, since,
	# in such cases, we need to avoid blowing away that existing list by
	# regenerating it from the BotConversation object. This introduces some
	# subtleties regarding exactly how to keep track of the oaiMsgList and keep
	# it consistent with the BotConversation obj.
	#
	# ALSO NOTE: We assume here that oaiMsgList DOES ALREADY INCLUDE a system
	# instruction message at the bottom, and we will trim it off prior to
	# replacing it with additional messages (e.g. function calls).

	"""Unified function to get a response from the AI. Supports various situa-
		tions, including responding to a function call-and-return sequence, or
		multiple of these. This allows the AI to handle more complex situations
		that may require making multiple function calls in sequence to figure
		out how to respond appropriately."""

		#----------------------------------------------------
		# First, retrieve some basic things that we'll need.

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)
		# NOTE: We only do this to get the user data.
		
	if tgMsg is None:
		_logger.error("In get_ai_response() with no message! Aborting.")
		return

	# Get user data.
	user_obj	= tgMsg.from_user
	user_tag	= _get_user_tag(user_obj)
	user_id		= user_obj.id

	# Get chat/conversation data.																
	botConvo	= context.chat_data['conversation']
	chat_id		= botConvo.chat_id
	
	# If a message list wasn't specifically supplied, then
	# derive it from the convo.
	if oaiMsgList is None:
		oaiMsgList = botConvo.get_chat_messages()
		usingRawMsgs = False	# Our input wasn't a raw messsage list.
	else:
		usingRawMsgs = True		# Our input *was* a raw message list.

	# Also, stash it in the convo structure so we don't have to keep passing it
	# around everywhere.
	botConvo.raw_oaiMsgs = oaiMsgList
	
	# Does this engine support the functions interface? If so, then we'll
	# pass it our list of function descriptions.
	if hasFunctions(ENGINE_NAME):
		# Retrieve our current functions list...
		functions = botConvo.cur_funcs + \
					[ACTIVATE_FUNCTION_SCHEMA, PASS_TURN_SCHEMA]
					# Plus always include these two.

		func_names = [func['name'] for func in functions if 'name' in func]
		_logger.info(f"\tIn chat {chat_id}, current function list is: {func_names}.")

	else:
		functions = None

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| Here's our main loop, which calls the API with exception handling as
	#| needed to recover from situations where our prompt data is too long.
	#| (However, we try to do our best to trim it down before the call.)
	#|
	#| Exceptions handled:
	#|	If we get a PromptTooLongException, then we'll try again with a
	#|		shorter prompt.
	#|	If we get a RateLimitError, then we'll emit a diagnostic reponse
	#|		message.
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	while True:		# Loop until we get a response from the API.

		# We assume that here, we already have a candidate <oaiMsgList> that is
		# all ready to try to pass it to the API. So, below we'll give it a try,
		# while handling API-related exceptions appropriately.

		# At this point, if debugging, we want to archive the chat messages to a
		# file in the log/ directory called 'latest-messages.txt'. This provides
		# an easy way for the system operator to monitor what the AI is actually
		# seeing, without having to turn on debug-level logging and search
		# through the log file.

		# If we're in debug mode, we'll log the current message list in .txt and
		# .json format, in case there are errors in processing.	 Otherwise,
		# we'll only log it once, *after* the loop is done.
		if logmaster.doDebug:
			_logOaiMsgs(oaiMsgList)

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Here we calculate what value of the maxTokens parameter to use; this
		#| controls the size of the response window, i.e., the maximum length of
		#| the reponse returned by the core, in tokens. This is set to the
		#| available space in the context window, but is capped by the
		#| aiConf.maxReturnedTokens parameter (from the api-conf/
		#| max-returned-tokens element in glados-config.hjson or ai-config.
		#| hjson) and set to be no less than the aiConf.minReplyWinToks
		#| parameter (from the mind-conf/min-replywin-toks element in
		#| ai-config.hjson).

			#-------------------------------------------------------------------
			# First, let's figure out how much space is left in the context
			# window currently, availSpaceToks.	 We'll do this by subtracting
			# the length of the chat messages from the context window size.

				#***************************************************************
				# Calculate the context window size, contextWinSizeToks.
				
		# Get the context window size from the global_gptCore object.
		contextWinSizeToks = global_gptCore.fieldSize

		# The +1 below seems true de facto, except for GPT-4. Not sure why.
		if ENGINE_NAME != 'gpt-4':
			contextWinSizeToks += 1		# One more token than spec'd.

		## Detailed diagnostic; comment out until needed.
		#_logger.debug("In get_ai_response(), "
		#	f"contextWinSizeToks={contextWinSizeToks}.")


				#***************************************************************
				# Calculate the size of the message list, msgsSizeToks.

		# Get the length of the current OAI message list in tokens.
		msgsSizeToks = ChatMessages(oaiMsgList).\
					   totalTokens(model=ENGINE_NAME)

		# If this engine supports functions, add in the estimated size in tokens
		# of the functions structure. (Note that this is just a guesstimate
		# since we don't know how it's formatted at the back end exactly.)
		if functions is not None:
			funcsSize = tiktokenCount(json.dumps(functions), model=ENGINE_NAME)
			#_logger.info(f"Estimating size of FUNCTIONS_LIST is {funcsSize}.)")
			msgsSizeToks += funcsSize

		## Detailed diagnostic; comment out until needed.
		#_logger.debug("In get_ai_response(), "
		#	f"msgsSizeToks={msgsSizeToks}.")
			

				#***************************************************************
				# Calculate the amount of available space, availSpaceToks.

		# Calculate the available space in the context window.
		availSpaceToks = contextWinSizeToks - msgsSizeToks
			# Note that this is just an estimate of the available space, because
			# the actual space available may be less than this if the chat
			# messages at the back end contain any additional formatting tokens
			# or extra undocumented fields.

		## Detailed diagnostic; comment out until needed.
		#_logger.debug("In get_ai_response(), "
		#	f"availSpaceToks={availSpaceToks}.")


			#-------------------------------------------------------------------
			# Now, we're ready to figure out what number we want to give the API
			# regarding the maximum number of tokens it can return: i.e.,
			# maxTokens.

				#***************************************************************
				# Calculate the absolute maximum number of tokens that we want
				# the API to return no matter what, absMaxRetToks.

		# Remember: globalMaxRetToks, globalMinReplWinToks were already
		# retrieved from the aiConf object and stored in these globals early in
		# this module, so we have them already.

			# Here, we're setting a local variable from the global.	 This is
			# needed to get the correct "unlimited" representation to pass to
			# the API.

		if globalMaxRetToks is None:	# In the chat API, this becomes inf.
			absMaxRetToks = float('inf')	# So in other words, no limit.
		else:
			absMaxRetToks = globalMaxRetToks

		## Detailed diagnostic; comment out until needed.
		#_logger.debug("In get_ai_response(), "
		#	f"absMaxRetToks={absMaxRetToks}.")
		
				#***************************************************************
				# Calculate the actual maximum number of tokens we'll tell the
				# API to return in this specific case, maxTokens.

		# If the available space is in between globalMinReplWinToks and
		# absMaxRetToks, then just set maxTokens=inf (i.e., tell the API that it
		# can use all the available space). Otherwise, calculate the value of
		# maxTokens in the same way we used to do it.

		if globalMinReplWinToks <= availSpaceToks and \
		   availSpaceToks <= absMaxRetToks:

			maxTokens = None	# No maximum; i.e., infinity; i.e.,
				# use up to all of the available space.

		else:
			# Calculate the actual maximum length of the returned reponse in
			# tokens, given all of our constraints above.
			maxTokens = max(globalMinReplWinToks,
							min(absMaxRetToks,
								availSpaceToks))
				# Explanation: maxTokens is the amount of space that will be
				# made available to the AI core for its response. This should
				# not be less than the AI's requested minimum reply window size,
				# and it should be as large as possible, but not more than
				# either the maximum number of tokens that the AI is allowed to
				# return, or the amount of space that is actually available
				# right now in the AI's context window.

		## Detailed diagnostic; comment out until needed.
		#_logger.debug("In get_ai_response(), "
		#	f"maxTokens={maxTokens}.")

		## Detailed diagnostic; comment out until needed.
		#_logger.info("get_ai_response(): "
		#	f"maxTokens = {maxTokens}, "
		#	f"globalMinReplWinToks = {globalMinReplWinToks}, "
		#	f"globalMaxRetToks = {globalMaxRetToks}, "
		#	f"absMaxRetToks = {absMaxRetToks}, "
		#	f"availSpaceToks = {availSpaceToks}")

		#_logger.info(f"CURRENT FUNCTION LIST IS:\n{pformat(functions)}")

		# Now we'll do the actual API call, with exception handling.
		try:
			# Get the response from the GPT, as a gpt3.api.ChatCompletion object.
			chatCompletion = global_gptCore.genChatCompletion(	# Call the API.
				
				maxTokens=maxTokens,	# Max. number of tokens to return.
					# We went to a lot of trouble to set this up properly above!

				messages=oaiMsgList,		# Current message list for chat API.
					# Note that since we pass in an explicit messages list, this
					# overrides whatever api.Messages object is being maintained
					# in the GPT3ChatCore object.

				user = str(user_id),		# Send the user's unique ID for
					# traceability in the event of severe content violations.

				minRepWin = globalMinReplWinToks,	# Min. reply window size in
					# tokens.  This parameter gets passed through to the
					# ChatCompletion() initializer and thence to
					# ChatCompletion._createComplStruct(), which does the actual
					# work of retrieving the raw completion structure from the
					# OpenAI API. Note that this parameter is necessary because
					# our computed maxTokens value may be greater than the
					# actual available space in the context window (either
					# because our estimate was wrong, or because we simply
					# requested a minimum space larger than is available). In
					# the latter case, getChatCompletion() should notice this &
					# throw a PromptTooLargeException, which we'll catch
					# below. If our estimate was wrong, then the actual reply
					# window size could be less than the minimum requested size,
					# but as long as our estimates were pretty close, the
					# difference will be small, and the AI should still be able
					# to generate a reasonable response.
				
				# The following API parameters are only relevant in 0613 (June
				# 13, 2023) or later releases of chat models, which support the
				# functions interface.

				functionList = functions,	# Available function list, if supported.
				functionCall = 'auto'		# Let AI decide whether/which functions to call.

			) # End of gptCore.genChatCompletion() call.

			# At this point, we have successfully obtained a chat completion
			# object in <chatCompletion>, and we can break out of the loop and
			# proceed to process this completion as appropriate.

			break
		#__/ End main body of 'try' clause for getting results from GPT.

		except PromptTooLargeException:				# Imported from gpt3.api module.

			# Are we using a raw message list that was passed in to us from
			# process_function_call()? If so, then we need to trim that one;
			# otherwise, we trim the user-visible form of the conversaion and
			# re-derive our entire raw message list from it.

			if usingRawMsgs:

				# Just trim off the oldest message after the first
				# N_HEADER_MSGS.

				_logger.info(f"NOTE: Expunging oldest chat message:\n" +
							 pformat(oaiMsgList[N_HEADER_MSGS]))

				oaiMsgList = oaiMsgList[0:N_HEADER_MSGS] + \
							 oaiMsgList[N_HEADER_MSGS+1:]

				continue	# Loop back to start of while loop and try again.

			else:

				# The LLM prompt (constructed internally at the remote API
				# back-end) is too long.  Thus, we need to expunge the oldest
				# message from the conversation.

				try:
					botConvo.expunge_oldest_message()
						# NOTE: If it succeeds, this modifies conversation.context_string.
				except _ConversationError:
					# We can't expunge the oldest message, presumably
					# because it's the only message left in the
					# conversation. All that we can do here is trim
					# off part of the content from the oldest
					# message end try agagin...
					_logger.warn("Can't expunge only message in conversation; I'll try trimming it instead...")
					if botConvo.trim_oldest_message():
						continue
					else:
						# Not much we can do except re-raise the error.
						raise

				# Update our (and the convo's) idea of the current raw message list.

				botConvo.raw_oaiMsgs = oaiMsgList = botConvo.get_chat_messages()

				# At this point, we've successfully expunged the oldest message.

				continue	# Loop back to start of while loop and try again.

			#__/ End if statement for different types of message tracking.


		# Handle various types of rate-limit errors.
		except RateLimitError as e:
			# Receiving this may alternatively indicate that the server is
			# overloaded or that our monthly quota was exceeded.

			# We exceeded our OpenAI API quota, or we've exceeded the rate limit
			# for this model, or the server's just overloaded. There isn't
			# really much of anything we can do here except send a diagnostic
			# message to the user.

			_logger.error(f"Got a {type(e).__name__} from OpenAI ({e}) for "
						  f"conversation {chat_id}; aborting.")

			# Send a diagnostic message to the AI and to the user.

			diagMsgStr = "AI model is overloaded, or monthly quota has "\
					"been reached; please try again later. Quotas reset on "\
					"the 1st of the month."

			await _send_diagnostic(tgMsg, botConvo, diagMsgStr)

			return	# That's all she wrote.


		# This one was also suggested by Copilot; we'll go ahead and use it.
		except Exception as e:
			# We've hit some other exception, so we need to log it and send a
			# diagnostic message to the user.  (And also add it to the
			# conversation so the AI can see it.)
			
			await _report_error(botConvo, tgMsg, f"Exception while "
								f"getting API response: {type(e).__name__} "
								f"({e})")
			return
		#__/

		# Here we handle any other exceptions that might have occurred during
		# the API call.
		#except:		# This is a stub
		#	return

	#__/ End of main while loop for retrieving a response from the API.

	# When we get here, we have a completion in <chatCompletion>.

	# If not in debug mode, we do this just once, after the above loop.
	if not logmaster.doDebug:
		_logOaiMsgs(oaiMsgList)

	# At this point, we're done with the final system prompt, so we throw it
	# away and update our concept of the oaiMsgList in the botConvo.

	oaiMsgList = botConvo._trimLastRaw()

	# Call this coroutine to process that raw response.
	await process_raw_response(chatCompletion, update, context)
		# NOTE: This does several important things, including:
		#
		#	* Trims any sender prompt off the front of the text.
		#
		#	* If the response is a function call, dispatch to function call
		#		handling. Note that this may in general recursively calling the
		#		present function get_ai_response() to get the AI's response to
		#		the function's return value (and this response could be another
		#		function call, and so on).
		#
		#	* Check for finish_reason that indicates a content filter was
		#		triggered, and log/send a warning.
		#
		#	* Check for null response text.
		#
		#	* Add the response text to the conversation.
		#
		#	* Check for '/pass' commands.
		#
		#	* Finally, process the text response by callng process_response().

	# When we get here, we're done, and we just return.

#__/ End definition of function get_ai_response().
						 

# Process a command (message starting with '/') from the AI.
async def process_ai_command(update:Update, context:Context, response_text:str) -> None:
	"""Given the text of a message returned by the AI, where that text starts
		with a '/' character, this function interprets it as an attempt by the
		AI to issue a command, and handles this appropriately."""

	# Get the user message, or edited message from the update.
	(message, edited) = _get_update_msg(update)
	
	# Get the chat_id, user_name, and conversation object.
	chat_id = message.chat.id
	user_name = _get_user_tag(message.from_user)
	conversation = context.chat_data['conversation']

	# Extract the command name from the message.  We'll do this
	# with a regex that captures the command name, and then the
	# rest of the command line.  But first, we'll capture just the
	# first line of the message, followed by the rest.

	# Split the text into lines
	lines = response_text.splitlines()

	# Get the first line
	first_line = lines[0]

	# Output the command line to the console.
	_logger.normal("The AI sent a command line: " + first_line)

	# Get the remaining text by joining the rest of the lines
	remaining_text = '\n'.join(lines[1:])

	# Now, we'll use a regex to parse the command line to
	# extract the command name and optional arguments.
	match = re.match(r"^/(\S+)(?:\s+(.*))?$", first_line)

	# Extract the command name and arguments from the match.
	command_name = command_args = None
	if match is not None:
		groups = match.groups()
		command_name = groups[0]
		if len(groups) > 1:
			command_args = groups[1]

	## Now, we'll process the command.

	# First, let's go ahead and show the command line to the user... (Ignoring send errors.)
	await _reply_user(message, conversation, first_line, ignore=True)

	# NOTE: We can't just call the normal command handlers
	# directly, because they are designed for commands issued by
	# the user, not by the AI. So, we'll have to process the
	# commands ourselves to handle them correctly.

	# Check to see if the AI typed the '/remember' command.
	if command_name == 'remember':
		# This is a command to remember something.

		_logger.normal(f"\nAI {BOT_NAME} entered a /remember command in chat {chat_id}.")

		# Should we issue a warning here if there is remaining text
		# after the command line that we're ignoring?  Or should we 
		# include the remaining text as part of the memory to be 
		# remembered?

		# This does all the work of handling the '/remember' command
		# when issued by the AI.
		await ai_remember(message, conversation, command_args)

	# Check to see if the AI typed the '/forget' command.
	elif command_name == 'forget':
		# This is a command to forget something.

		_logger.normal(f"\nAI {BOT_NAME} entered a /forget command in chat {chat_id}.")

		# Should we issue a warning here if there is remaining text
		# after the command line that we're ignoring?  Or should we 
		# include the remaining text as part of the memory to be 
		# forgotten?

		# This does all the work of handling the '/forget' command
		# when issued by the AI.
		await ai_forget(message, conversation, command_args)

	elif command_name == 'block':
		# Adds the current user (or a specified user) to the block list.

		_logger.normal(f"\nAI {BOT_NAME} entered a /block command in chat {chat_id}.")

		# Should we issue a warning here if there is remaining text
		# after the command line that we're ignoring?  Or should we
		# send the remaining text as a normal message?

		# This does all the work of handling the '/block' command
		# when issued by the AI.
		await ai_block(message, conversation, command_args)

	elif command_name == 'unblock':
		# Removes the current user (or a specified user) from the block list.

		_logger.normal(f"\nAI {BOT_NAME} entered an /unblock command in chat {chat_id}.")

		# Should we issue a warning here if there is remaining text
		# after the command line that we're ignoring?  Or should we
		# send the remaining text as a normal message?

		# This does all the work of handling the '/unblock' command
		# when issued by the AI.
		await ai_unblock(message, conversation, command_args)

	elif command_name == 'image':
		# This is a command to generate an image and send it to the user.
		
		_logger.normal(f"\nAI {BOT_NAME} entered an /image command in chat {chat_id}.")
			
		# This does all the work of handling the '/image' command
		# when issued by the AI.
		await ai_image(update, context, command_args)	# Use whole arglist as image description.
			# NOTE: We're passing the entire update object here, as well
			# as the context, because we need to be able to send a message
			# to the user, and we can't do that with just the message object.

		# NOTE: We could have passed remaining_text as the 4th argument (caption),
		# but it's perhaps better to just send it as an ordinary text message.

	else:
		# This is a command type that we don't recognize.
		_logger.warn(f"\nAI {BOT_NAME} entered an unknown command [/{command_name}] in chat {chat_id}.")

		# Send the user a diagnostic message.
		diagMsg = f"Unknown command [/{command_name}]."
		await _send_diagnostic(message, conversation, diagMsg, ignore=True)

	# If there was any additional text remaining after the command line,
	# just send it as a normal message.
	if remaining_text != "":
		await send_response(update, context, remaining_text)

	# At this point we are done processing the command.

#__/ End function process_ai_command().

						 
async def process_chat_message(update:Update, context:Context) -> None:

	"""We dispatch to this function to process messages from the user if our
		selected engine is for OpenAI's chat endpoint."""
	
	# To save space, when processing a new user message, we'll just
	# let the bot remember only the last function schema it previously
	# activated when starting to process a new message. (Except, the
	# activate_function and pass_turn schemas are always visible.)

	botConvo	= context.chat_data['conversation']
	chat_id		= botConvo.chat_id
	cur_funcs	= botConvo.cur_funcs
	HOWMANY_FUNCS = 1
	if len(cur_funcs) > HOWMANY_FUNCS:
		cur_funcs = cur_funcs[-(HOWMANY_FUNCS):]
		botConvo.cur_funcs = cur_funcs
	#__/
	func_names = [func['name'] for func in cur_funcs if 'name' in func]
	_logger.info(f"Current function list in chat {chat_id} is {func_names}.")

	# Now everything is handled by this new implementation, which has been
	# rewritten so that it can also handle cases where the AI is responding from
	# a result that's been returned from a function that it previously called.

	return await get_ai_response(update, context)

#__/ End definition of async function process_chat_message().


# Another new function, to handle function call requests from the AI.
# Again, we separate this from process_raw_response() just to keep
# our functions from getting too long.

async def process_function_call(
		funcall_oaiMsg:dict,		# Raw OpenAI message that represents the function call.
		tgUpdate:Update,			# The original Telegram update that prompted this call.
		tgContext:Context,			# The Telegram context for this chat.
	) -> None:

	"""Processes a function call request received from the AI. Also returns the
		function result to the AI, and gets the AI's response to that."""

	# Get the text of the response, if any (should be None).
	response_text = funcall_oaiMsg.content

	# Get the bot's conversation object.
	botConvo = tgContext.chat_data['conversation']
	chat_id = botConvo.chat_id

	# Retrieve the function call object from the OpenAI message containing it.
	funCall = funcall_oaiMsg.function_call

	# Retrieve the function name and arguments from the function call object.
	function_name = funCall.name
	function_argStr = funCall.arguments

	try:
		function_args = json.loads(function_argStr)		# This could fail!

	except json.decoder.JSONDecodeError as e:

		_logger.error(f'Got a JSON decoding error "{str(e)}" when parsing '
					  f'argument list: [\n{function_argStr}\n]')

		botConvo.add_message(BotMessage(SYS_NAME, '[ERROR: AI tried to call '
			f'function {function_name} with arguments ```{function_argStr}``` '
			'but there was a JSON decode error while parsing the arguments: '
			f'"{str(e)}"]'))

		# Give the AI a chance to respond to that JSON error.
		await get_ai_response(tgUpdate, tgContext)
		return
	
	_logger.info(f"AI wants to call function {function_name} with " \
				 "arguments: \n" + pformat(function_args))

	# Generate a description of the function call, for diagnostic purposes.
	call_desc = _call_desc(function_name, function_args)

	# Have the bot server make a note in the conversation to help the AI
	# remember that it did the function call.
	#fcall_note = f"[NOTE: {BOT_NAME} is doing function call {call_desc}.]"
	#botConvo.add_message(BotMessage(SYS_NAME, fcall_note))
	# ^^^ The above is obsolet now, given new-style function call formatting.

	botConvo.add_message(BotMessage(BOT_NAME, function_argStr, func_name=function_name))

	# Extract the optional remark argument from the argument list.
	if 'remark' in function_args:
		remark = function_args['remark']
		del function_args['remark']
	else:
		remark = ""		# If no remark, take it as empty string.

	# The response_text is probably None, but force it to a string
	# so that just in case it's a non-empty string, we can handle
	# this without checking its type all the time.
	if response_text is None:
		response_text = ""

	## Just did this temporarily while debugging.
	# # Prepend a diagnostic with the call description and remark to the
	# # response_text (which is probably null).
	# response_text = f"[SYSTEM DIAGNOSTIC: Called {call_desc}]\n\n" \
	#					+ remark + '\n' + response_text

	# Generate a description of the function call, for diagnostic purposes.
	call_desc = _call_desc(function_name, function_args)

	# The original response text, followed by the remark. This probably is just
	# the remark, since the original response text should have been null. But in
	# any case, we'll use it as our response text below.
	response_text = (response_text + '\n' + remark).strip()

	# Before calling the function, we'll send the response_text, if non-empty.
	# (which at this point probably just contents of a remark argument, if
	# anything)'
	if response_text != "":

		# Append the response text to the conversation.
		botConvo.add_message(BotMessage(BOT_NAME, response_text))
					
		# Try sending the response text to the user. (But ignore send errors here.)
		await send_response(tgUpdate, tgContext, response_text)
			# (We ignore them because presumably it's more important to
			# still go ahead and try calling the function if we can.)
	#__/

	# Actually do the call here, and assemble appropriate result text.
	func_result = await ai_call_function(tgUpdate, tgContext, function_name, function_args)

	# This is mainly for diagnostic purposes.
	if func_result is None or func_result == "":
		func_result = "null result"

	# Diagnostic.
	_logger.info(f"The AI's function call returned the result: [{pformat(func_result)}]")

	# Get the function result in the form of a string, even if it isn't.
	resultStr = func_result if isinstance(func_result, str) \
				else json.dumps(func_result)

	# Now, we retrieve the current raw OpenAI message object list from the bot
	# convo object; please note that this should *already* have the final system
	# message trimmed off, and it should include any previous function call/
	# return sequences in the present function-call stack, and any side messages
	# output by these.

	temp_chat_oaiMsgs = list(botConvo.raw_oaiMsgs)
		# We call list() here to force a *copy* of the list to be
		# constructed.  Because we don't really want anyone else
		# besides us modifying it until we've finished operating on it
		# and have given the AI a chance to respond to it.

	# Have the bot server make a note in the conversation to help the
	# AI remember longer-term that it got a function result. NOTE: We
	# do NOT want to also put this note into temp_chat_oaiMsgs at this
	# point, because we don't want to distract the AI with these kinds
	# of longer-term notes while it is still processing the *present*
	# function call and return.

	#fret_note = f'[NOTE: {function_name}() call returned value: [{resultStr}]]'
	#botConvo.add_message(BotMessage(SYS_NAME, fret_note))
	# ^^ This is obsolete now that we have new-style message formats for function returns.

	botConvo.add_message(BotMessage(f"@{function_name}", resultStr))

	# Back when our functions just never returned a result, we would just skip
	# everything below here. But they do return results now.

	# Diagnostic.
	_logger.info("Assembling temporary message list for function call & return...")

	# Next, we temporarily trim off all trailing messages back to the last
	# function call note, since these would be remarks and various system
	# notifications and errors generated during function execution; we'll add
	# these back onto the raw message list after we've inserted messages
	# representing the raw function call and return operations, which the AI
	# will recognize. The trimmed messages will be temporarily stored in
	# <trailing_oaiMsgs>.

	trailing_oaiMsgs = []
	# Scan back until we get to the "system: [NOTE: " message...
	#while not (temp_chat_oaiMsgs[-1]['role'] == 'system'
	#		   and temp_chat_oaiMsgs[-1]['content'].startswith(f'{SYS_NAME}> [NOTE: ')):
	#	# NOTE: The above will break if MESSAGE_DELIMITER is not empty string.
	#	_logger.info(f"Flipping back through message: [{pformat(temp_chat_oaiMsgs[-1])}]")
	#	sys_oaiMsg = temp_chat_oaiMsgs.pop()
	#	trailing_oaiMsgs = [sys_oaiMsg] + trailing_oaiMsgs
	##__/
	# ^^ Obsolete now?

	# Construct some messages to represent the function call and return value.
	# Actually, we already have a message that represents the function call; it
	# came from the AI originally, and was supplied to us in our funcall_oaiMsg
	# argument. But, we need to make sure that we didn't add a 'content' field
	# to this message at some point, because if we did and we try sending it
	# back to the API, the API will choke on it.

	if 'content' in funcall_oaiMsg and funcall_oaiMsg['content'] is not None:
		_logger.info("Oops, our funcall message has text content?? "
					 f"[\n{pformat(funcall_oaiMsg)}\n]")
		funcall_oaiMsg['content'] = None
	
	# This new raw-format message represents the actual return value of the
	# function.

	funcret_oaiMsg = {
		'role':		CHAT_ROLE_FUNCRET,	# This is just 'function'
		'name':		function_name,
		'content':	resultStr
	}

	# If the function call was a successful "pass_turn" call, then
	# we don't need to do anything else here, and we just return.

	if resultStr == PASS_TURN_RESULT:
		_logger.normal(f"\t{BOT_NAME} is refraining from responding to a "
					   f"returned function result in chat #{chat_id}.")
		return

	#--------------------------------------------------------------------------|
	# Finish building up the temporary message list to pass into the next API
	# call to see how the AI wants to respond to the returned function
	# result. So, the sequence here is:
	#
	#	system:		[NOTE: ... is doing function call ...]
	#	assistant:	(function call description)
	#	assistant:	{remark emitted by bot during function call, if any}
	#	(any other incidental outputs produced from within the function call)
	#   function:	(function return description)
	#	system:		(prompt AI to respond)

	temp_chat_oaiMsgs += [funcall_oaiMsg]
	temp_chat_oaiMsgs += trailing_oaiMsgs
	temp_chat_oaiMsgs += [funcret_oaiMsg]
	temp_chat_oaiMsgs += [{
		'role':		'system',
		'content':	f"Instructions from bot server: {BOT_NAME}, you " \
					"may now provide your response, if any, to the " \
					"function's return value above.",
	}]

	# Diagnostic: Display the most recent 10 chat messages from temp list.
	_logger.info(f"Last few chat messages are [\n{pformat(temp_chat_oaiMsgs[-10:])}\n].")

	# Log this, the last function call/return, in .json/.txt formats.
	_logOaiMsgs(temp_chat_oaiMsgs, basename="last-function")

	# At this point, we want to get a response from the AI to our temporary list
	# of raw OpenAI chat messages, which (note) includes raw descriptions of the
	# most recent function call and return, as well as (possibly) results of
	# previous function calls and returns in the present "call stack". Mean-
	# while, the main 'messages' list in the bot conversation object is tracking
	# just the more human-readable messages including the bot-server notes
	# describing the current sequence of calls and returns which are being
	# archived and preserved long-term as part of the conversation. This helps
	# us to keep the conversation history more concise, while not distracting
	# the AI with the details of earlier call-return sequences before the
	# present stack. The next time get_ai_response() is called at the start of
	# normal message processing, the two views will be brought back in sync.

	await get_ai_response(tgUpdate, tgContext, temp_chat_oaiMsgs)
		# Recursive call to get and process the AI's response to this
		# *temporary* view of the message list.

	# By the time we get back to here, the entire "stack" of successive function
	# calls and returns triggered by our input function-call message from the AI
	# has been completed.
	#
	# The present temporary raw message list in temp_chat_oaiMsgs is now no
	# longer needed, and can be thrown away.
	#
	# So at this point, we are done processing the original function call, and
	# so we just return.

#__/ End definition of function process_function_call().


# Another new function, to process a raw response from the AI, which (for chat
# engines) takes the form of an OpenAI message object (a dictionary-like
# object). We separate this from get_ai_response() above just to keep our
# functions from getting too long!

async def process_raw_response(
			chatCompletion:ChatCompletion, 
			#oaiMsgs:list,
			tgUpdate:Update,
			tgContext:Context
		) -> None:
	#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^|
	# NOTE RE: THE ABOVE ARGUMENTS:
	#
	#	<chatCompletion> is the "raw response" received from the AI, in the form
	#			of a gpt3.api.ChatCompletion object.  (our wrapper around the
	#			raw completion dictionary).
	#
	#	<tgUpdate> the original update from the Telegram server that prompted
	#			this response.
	#
	#	<tgContext> the Telegram context corresponding to the current chat.
	#
	# ALSO NOTE RE: THE BELOW CODE:
	#
	#	<botConvo> (which we'll retrieve from the tgContext) is the
	#			BotConversation object that's tracking this conversation from
	#			the bot server's point of view.  Note this includes tracking
	#			botConvo.raw_oaiMsgs.  ALSO NOTE: The botConvo.raw_oaiMsgs here
	#			should NOT include a final system prompt!
	#
	#	<oaiMsgs> (which we'll retrieve from the botConvo) is the list of
	#			*previous* messages in the chat, prior to this new one just
	#			created by the AI.
	#
	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

	"""Process a raw response from the AI."""

	# Get the bot's conversation object.
	botConvo = tgContext.chat_data['conversation']

	# Get the current *raw* OpenAI message list from the bot convo object.
	oaiMsgs = botConvo.raw_oaiMsgs

	# Get the full dict-like response message object.
	response_oaiMsg = chatCompletion.message

	# In case there's a function call in the response, display it.
	_logger.debug(f"RETURNED MESSAGE = [{pformat(response_oaiMsg)}]")

	# Get the text field of the response. (Could be None, if function call.)
	response_text = chatCompletion.text

	# Diagnostic for debugging.
	_logger.debug(f"Got response text: [{response_text}]")

	# Here, we make sure that the response does not begin with a message
	# prompt like "{BOT_NAME}> ". If it does, we trim it off the front.
	if response_text is not None:

		# Trim prompt off start of response.
		new_response_text = _trim_prompt(response_text)

		if new_response_text != response_text:
			response_text = new_response_text

			# Do surgery on the chat message object to fix it there also.
			# (This is handled by our gpt3.api.ChatCompletion class.)
			chatCompletion.text = response_text
				# NOTE: Setting the '.text' property ('content' field) here
				# could invalidate the chat message if it contains a function
				# object too. But we made sure .text wasn't None already.

			_logger.debug(f"Modified response message text is: [{chatCompletion.text}]")

	## Another diagnostic; this one post-surgery.
	# In case there's a function call in the response, display it.
	#_logger.normal(f"RETURNED MESSAGE = \n" + pformat(response_message))

	# Now, we check to see if the OpenAI message object returned by the AI has a
	# 'function_call' property, in which case it means the AI is trying to call
	# a function.  If it is, we'll dispatch out to the process_function_call()
	# function to handle this case.

	funCall = response_oaiMsg.function_call
	if funCall:
		
		await process_function_call(response_oaiMsg, tgUpdate, tgContext)
			# This handles the function recall, the function return, and any
			# responses by the AI to the function return (including any
			# recursive function call-return sequences).
		
		# At this point, the whole recursive sequence of actions taken by the AI
		# in response to that function call is complete, so we just
		# return. There shouldn't have been any response text in a function call
		# anyway, but if there is, we warn that we're ignoring it.

		#if response_text is not None:
		#	_logger.warn(f"NOTE: Done with original response text: [{response_text}].")

		return	# End process_chat_message() when done function processing.

	#__/ End if funCall is truthy.
	
	# If we get here, it isn't a function-call response, it's a normal response.

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(tgUpdate)
		# NOTE: We only do this to get the user data.
		
	if tgMsg is None:
		_logger.error("In get_ai_response() with no message! Aborting.")
		return

	# Get user data.
	user_obj	= tgMsg.from_user
	user_tag	= _get_user_tag(user_obj)
	user_id		= user_obj.id
	chat_id		= botConvo.chat_id

	# Also check for finish_reason == 'content_filter' and log/send a warning.
	finish_reason = chatCompletion.finishReason
	if finish_reason == 'content_filter':
				
		_logger.warn(f"OpenAI content filter triggered by user {user_name} " \
					 "(ID {user_id}) in chat {chat_id}. Response was:\n" + \
					 pformat(chatCompletion.chatComplStruct))

		WARNING_MSG = "WARNING: User {user_name} triggered OpenAI's content " + \
					  "filter. Repeated violations could result in a ban."

		# This allows the AI to see this warning message too.
		botConvo.add_message(BotMessage(SYS_NAME, WARNING_MSG))

		repRes = await _reply_user(tgMsg, botConvo, "[SYSTEM {WARNING_MSG}]")
		if repRes != 'success': return

	#__/ End if content filter triggered.

	# Strip off any leading or trailing whitespace (Telegram won't display it
	# anyway.).
	response_text = response_text.strip()
	
	# Now we check for the case of an empty response text.

	# If the response is empty, then return early. (Because, like, we can't even
	# send an empty message anyway.)
	if response_text == "":

		_logger.warn("AI's text response was null. Ignoring...")

		## No longer needed because we don't add an empty message.
		# Delete the last message from the conversation.
		#conversation.delete_last_message()

		## Commenting this out for production.
		# # Send the user a diagnostic message indicating that the response was empty.
		# # (Doing this temporarily during development.)
		#diagMsg = "Response was empty."
		#await _send_diagnostic(message, conversation, diagMsg, toAI=False, ignore=True)
		
		return		# This means the bot is simply not responding to this particular message.
	
	# Generate a debug-level log message to indicate that we're starting a new response.
	_logger.debug("Creating new ordinary (non-function-call) response from "
				  f"{botConvo.bot_name} with text: [{response_text}].")

	# Create a new Message object and add it to the conversation.
	response_botMsg = BotMessage(botConvo.bot_name, response_text)
	botConvo.add_message(response_botMsg)

	# Update the message object, and the context.
	response_botMsg.text = response_text
	botConvo.expand_context()	 

	# If this message is already in the conversation, then we'll suppress it, so
	# as not to exacerbate the AI's tendency to repeat itself.  (So, as a user,
	# if you see that the AI isn't responding to a message, this may mean that
	# it has the urge to just repeat something that it already said earlier, but
	# is holding its tongue.)

	if response_text.lower() != '/pass' and \
	   botConvo.is_repeated_message(response_botMsg):

		# Generate an info-level log message to indicate that we're suppressing
		# the response.
		_logger.info(f"Suppressing response [{response_text}]; it's a repeat.")

		# Delete the last message from the conversation.
		botConvo.delete_last_message()

		## Send the user a diagnostic message (doing this temporarily during development).
		#diagMsg = f"Suppressing response [{response_text}]; it's a repeat."
		#await _send_diagnostic(message, conversation, diagMsg, toAI=False, ignore=True)
		
		return		# This means the bot is simply not responding to the message

	#__/ End check for repeated messages.

	# If we get here, then we have a non-empty message that's also not a repeat.
	# It's finally OK at this point to archive the message and send it to the user.

	# Make sure the response message has been finalized (this also archives it).
	botConvo.finalize_message(response_botMsg)

	# If we get here, we have finally obtained a non-empty, non-repeat,
	# already-archived message that we can go ahead and send to the user. This
	# function will also check to see if the message is a textual command line,
	# and will process the command if so.

	await process_response(tgUpdate, tgContext, response_botMsg)	   # Defined below.

	# If we get here, then we have finished processing the AI's text response,
	# and we can just return.

#__/ End definition of function process_raw_response().


async def process_response(update:Update, context:Context, response_botMsg:BotMessage) -> None:
	"""Given a message object (of our Message class) representing a response
		issued by the AI to some user message, this function processes it
		appropriately; it may be interpreted as a text command issued by the
		AI, or as a normal message to be sent to the user."""

	# Get the user message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)
	
	# Get the chat_id, user_name, and conversation object.
	chat_id = tgMsg.chat.id
	#user_name = _get_user_tag(tgMsg.from_user)
	conversation = context.chat_data['conversation']
	response_text = response_botMsg.text

	# First, check to see if the AI typed the '/pass' command, in which case we do nothing.
	if response_text.lower() == '/pass':
		_logger.normal(f"\nNOTE: The AI is passing its turn in conversation {chat_id}.")
		return

	if response_text == "":		# Response is empty string??
		_logger.error(f"In process_response(), got an empty response message: [{str(response_botMsg)}].")
		return

	# Finally, we check to see if the AI's message is a command line;
	# that is, if it starts with '/' followed by an identifier (e.g.,
	# '/remember').  If so, we'll process it as a command.
	if response_text[0] == '/':

		# The AI attempted to send a command line, so process it as such.
		await process_ai_command(update, context, response_text)

		return

	else: # Response was not a command. Treat it normally.

		# Just send our response to the user as a normal message.
		await send_response(update, context, response_text)

	# One more thing to do here: If the AI's response ends with the string "(cont)" or "(cont.)"
	# or "(more)" or "...", then we'll send a message to the user asking them to continue the 
	# conversation.
	if response_text.endswith("(cont)") or response_botMsg.text.endswith("(cont.)") or \
	   response_text.endswith("(more)") or response_botMsg.text.endswith("..."):

		contTxt = "[If you want me to continue my response, type '/continue'.]"
		await _reply_user(tgMsg, conversation, contTxt, toAI=False, ignore=True)
	#__/

	# Processed AI's response successfully.

#__/ End of process_response() function definition.


async def send_image(update:Update, context:Context, desc:str, dims=None, style=None, caption=None, save_copy=True) -> (str, str, str):
	"""Generates an image from the given description and sends it to the user.
		Also archives a copy on the server unless save_copy=False is specified.
		Returns a temporary URL for the image, if successful, and a revised
		description of the generated image. And the image filename, if saved.
		If something goes wrong, None is returned instead."""

	# Get the message, or edited message from the update.
	(tgMsg, edited) = _get_update_msg(update)
		
	if tgMsg is None:
		_logger.warning("In send_image() with no message? Aborting.")
		return None

	# Get the message's chat ID.
	chat_id = tgMsg.chat.id

	# Get our preferred name for the user.
	username = _get_user_tag(tgMsg.from_user)

	# Get our Conversation object.
	conversation = context.chat_data['conversation']

	# Default image dimensions.
	if dims is None:
		dims = "1024x1024"

	_logger.normal(f"\tGenerating {dims} image for user {username} from " \
				   f"description [{desc}]. Caption is [{str(caption)}]...")

	# Use the OpenAI API to generate the image.
	try:
		(image_url, revised_prompt) = genImage(desc, dims, style)
	except Exception as e:
		await _report_error(conversation, tgMsg,
					  f"In send_image(), genImage() threw an exception: {type(e).__name__} ({e})")

		# We could also do a traceback here. Should we bother?
		raise

	_logger.normal(f"\tImage description was revised to: [{revised_prompt}]")
	_logger.normal(f"\tDownloading generated image from url [{image_url[0:50]}...]")

	# Download the image from the URL
	response = requests.get(image_url)
	response.raise_for_status()
	
	# Save the image to the filesystem if the flag is set to True
	save_filename = None
	if save_copy:
		_logger.normal(f"\tSaving a copy of the generated image to the filesystem...")
		image_dir = os.path.join(AI_DATADIR, 'images')
		if not os.path.exists(image_dir):
			os.makedirs(image_dir)
		# Pick a short ID for the file (collisions will be fairly rare).
		short_file_id = f"{random.randint(1,1000000)-1:06d}"
		short_filename = f'{username}--{short_file_id}.png'
		image_save_path = os.path.join(image_dir, short_filename)
		save_filename = os.path.join('images', short_filename)
		with open(image_save_path, 'wb') as image_file:
			image_file.write(response.content)
		_logger.normal(f"\t\tImage saved to {image_save_path}.")

	_logger.normal(f"\tSending generated image to user {username}...")

	# Prepare the image to be sent via Telegram
	image_data = InputFile(response.content)
	
	# Send the image as a reply in Telegram
	try:
		await tgMsg.reply_photo(photo=image_data, caption=caption)

	except BadRequest or Forbidden or ChatMigrated or TimedOut as e:

		_logger.error(f"Got a {type(e).__name__} exception from Telegram "
					  "({e}) for conversation {chat_id}; aborting.")
		conversation.add_message(BotMessage(SYS_NAME, "[ERROR: Telegram " \
			"exception {exType} ({e}) while sending to user {user_name}.]"))

		if isinstance(e, BadRequest) and "Not enough rights to send" in e.message:
			try:
				await app.bot.leave_chat(chat_id)
				_logger.normal(f"Left chat {chat_id} due to insufficient permissions.")
			except Exception as leave_error:
				_logger.error(f"Error leaving chat {chat_id}: {leave_error}")

		return None

	#__/

	# Update record of how many images have been generated today in this context.

	today = get_current_date()
	if 'last_image_date' not in context.chat_data or today != context.chat_data['last_image_date']:
		context.chat_data['last_image_date'] = get_current_date()
		context.chat_data['nimages_today'] = 1	# The image we just made.
	else:
		context.chat_data['nimages_today'] += 1

	_logger.normal(f"\tA total of {context.chat_data['nimages_today']} images have been generated in chat {chat_id} today ({today}).")

	return (image_url, revised_prompt, save_filename)
#__/


async def send_response(update:Update, context:Context, response_text:str) -> None:
	
	# Get the message, or edited message from the update.
	(message, edited) = _get_update_msg(update)
		
	if message is None:
		_logger.warning("In send_response() with no message? Aborting.")
		return

	chat_id = message.chat.id

	conversation = context.chat_data['conversation']

	# Now, we need to send the response to the user. However, if the response is
	# longer than the maximum allowed length, then we need to send it in chunks.
	# (This is because Telegram's API limits the length of messages to 4096 characters.)

	MAX_MESSAGE_LENGTH = 4096	# Maximum length of a message. (Telegram's API limit.)
		# NOTE: Somwhere I saw that 9500 was the maximum length of a message, but I don't know
		#	which is the correct maximum.

	# Send the message in chunks.
	while len(response_text) > MAX_MESSAGE_LENGTH:
		await _reply_user(message, conversation, response_text[:MAX_MESSAGE_LENGTH], markup=True)
		response_text = response_text[MAX_MESSAGE_LENGTH:]

	# Send the last chunk.
	await _reply_user(message, conversation, response_text, markup=True)
#__/


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	The following function will be used to display the current
		#|  date/time to the AI, including the time zone.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# The following function will get the current date/time as a string, including the timezone.
def timeString() -> str:

	"""Returns a nicely-formatted string representing the current date, time,
		and timezone."""

	dateTime = tznow()	# Function to get the current date and time in the local timezone.
	fmtStr = _TIME_FORMAT  # The base format string to use.

	# Is the 'TZ' environment variable set?
	#	If so, then we can add '(%Z)' (time zone abbreviation) to the format str.
	if envTZ is not None:
		fmtStr = fmtStr + " (%Z)"
	
	timeStr = dateTime.strftime(fmtStr)	 # Format the date/time string.

	# If 'TZ' was not set, then we have to try to guess the time zone name from the offset.
	if envTZ is None:
		tzAbb = tzAbbr()	# Function to get the time zone abbreviation from the offset.
		timeStr = timeStr + f" ({tzAbb})"

	return timeStr
#__/


	#|==========================================================================
	#|	4.2. Misc. minor/private functions.			[python module code section]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


def _addMemoryItem(userID, chatID, itemText, isPublic=False, isGlobal=False):

	privacy = "public" if isPublic else "private"
	locality = "global" if isGlobal else "local"
	_logger.normal(f"\tFor userID={userID}, chatID={chatID}, adding {privacy} "\
				   f"{locality} memory [{itemText}]...")

	# Path to the database file
	db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

	# Create a connection to the SQLite database
	conn = sqlite3.connect(db_path)

	# Create a cursor object
	c = conn.cursor()

	# Generate a random 8-hex-digit string for itemID
	itemID = '{:08x}'.format(random.randint(0, 0xFFFFFFFF))

	## OLD VERSION:
	## Get the embedding for the item, as a string.
	#embedding = _getEmbeddingStr(itemText)

	# NEW VERSION:
	# Get the embedding for the item, as a pickled numpy array.
	embedding_pickle = _getEmbeddingPickle(itemText)

	## OLD VERSION:
	## Insert the memory item into the remembered_items table
	#c.execute('''
	#	INSERT INTO remembered_items (itemID, userID, chatID, public, global, itemText, embedding)
	#	VALUES (?, ?, ?, ?, ?, ?, ?)
	#''', (itemID, userID, chatID, isPublic, isGlobal, itemText, embedding))

	# NEW VERSION:
	# Insert the memory item into the remembered_items table
	c.execute('''
		INSERT INTO remembered_items (itemID, userID, chatID, public, global, itemText, embedding_blob)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	''', (itemID, userID, chatID, isPublic, isGlobal, itemText, embedding_pickle))

	# Commit the transaction
	conn.commit()

	# Close the connection
	conn.close()

	# Return the itemID for reference
	return itemID

#__/ End function _addMemoryItem().


def _addUser(tgUser:User):

	# Path to the database file
	db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

	# Create a connection to the SQLite database
	conn = sqlite3.connect(db_path)

	# Create a cursor object
	c = conn.cursor()

	# Form the display name
	displayName = tgUser.first_name
	if tgUser.last_name:
		displayName += " " + tgUser.last_name

	# Get our "tag" (preferred name) for the user.
	userTag = _get_user_tag(tgUser)

	# Insert or update the user data
	c.execute('''
		INSERT OR REPLACE INTO users (displayName, username, userID, blocked, userTag)
		VALUES (?, ?, ?, ?, ?)
	''', (displayName, tgUser.username, tgUser.id, _isBlocked(userTag), userTag))

	# Commit the transaction
	conn.commit()

	# Close the connection
	conn.close()

#__/ End definition of private function _addUser().


# Markets currently supported by Bing search.
BING_MARKETS = ["en-US", "en-AR", "en-AU", "de-AT", "nl-BE", "pt-BR", "en-CA",
	"fr-CA", "es-CL", "zh-CN", "da-DK", "fi-FI", "fr-FR", "de-DE", "zh-HK",
	"en-IN", "en-ID", "it-IT", "ja-JP", "ko-KR", "en-MY", "es-MX", "nl-NL",
	"en-NZ", "no-NO", "pl-PL", "en-PH", "ru-RU", "en-ZA", "es-ES", "sv-SE",
	"zh-TW", "tr-TR", "en-GB", "es-US"]

class SearchError(Exception):
	"""Exception class for exceptions encountered during web searches."""
	pass

class UnsupportedLocale(SearchError):
	"""Exception class for unsupported locale for search."""
	pass

class BingQuotaExceeded(SearchError):
	"""Exception class for when Bing search quota is exceeded."""
	pass

# This function will be used internally by the WebAssistant when
# doing web searches.
def _bing_search(query_string:str, market:str='en-US', count=3):
	# The caller should fill in the market parameter based on the
	# user's locale (if known), or on an alternate market for this
	# particular search (if specified by the user).

	global _lastError

	# Error-checking on 'market' parameter.
	if market not in BING_MARKETS:

		# Make the error string available to callers.
		_lastError = f"Market '{market}' is not supported by Bing search."

		# Also log the error.
		_logger.error(_lastError)

		# Raise this as an exception so the caller can decide how to
		# handle it appropriately.
		raise UnsupportedLocale(_lastError)

	subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
	endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"
	params = {
		'q':		query_string,
		'mkt':		market,
		'count':	count
	}
	headers = {
		'Ocp-Apim-Subscription-Key': subscription_key
	}

	_logger.normal(f"\tDoing web search in {market} for {count} results for [{query_string}]...")

	try:
		response = requests.get(endpoint, headers=headers, params=params)
		response.raise_for_status()

		search_results = response.json()

		## Diagnostic output for debugging:
		#i = 0
		#for item in search_results['webPages']['value']:
		#	i += 1
		#	_logger.normal(f"\nResult #{i}: name=\"{item['name']}\", "
		#				   f"\n\turl={item['url']}, "
		#				   f"\nsnippet={pformat(item['snippet'])}")

		return search_results

	except requests.exceptions.HTTPError as ex:

		# Get the error message.
		msg = str(ex)

		# Check if it's a quota exceeded error.
		if "403 Client Error: Quota Exceeded" in msg:
			_lastError = f"Bing search quota has been exceeded."
			_logger.error(_lastError)
			raise BingQuotaExceeded(_lastError)

		_lastError = f"Search query generated an HTTP error ({ex})"

		# Also log the error.
		_logger.error(_lastError)

		# Re-raise the exception so caller can handle it.
		raise

	# Exceptions caught here include requests.exceptions.HTTPError
	except Exception as ex:

		exType = type(ex).__name__
	
		# Log the error.
		_lastError = f"Search query generated a {exType} exception ({ex})."
		_logger.error(_lastError)

		# Re-raise the exception so caller can also try to handle it.
		raise ex

#__/ End private function _bing_search().


# NOTE: This function is being deprecated because user tags
# are not unique. Use the new function _blockUserByID() instead.
def _blockUser(user:str) -> bool:
	"""Blocks the given user from accessing the bot.
		Returns True if successful; False if failure."""

	global _lastError
	
	ai_datadir = AI_DATADIR

	## Commented out this code because main block code is now
	## elsewhere anyway.
	#
	# If the AI is trying to block the Creator, don't let him.
	#if user == 'Michael':
	#	_logger.error("The AI tried to block the app developer! Disallowed.")
	#	_lastError = "Blocking the bot's creator, Michael, is not allowed."
	#	return False

	block_list = []

	bcl_file = os.path.join(ai_datadir, 'bcl.json')
	if os.path.exists(bcl_file):
		with open(bcl_file, 'r') as f:
			block_list = json.load(f)
	
	_logger.normal(f"\tBlocking user {user} (by legacy method)...")

	if user in block_list:
		_logger.warn(f"_blockUser(): User {user} is already blocked. Ignoring.")
		_lastError = f"User {user} is already blocked; ignoring."
		return True

	block_list.append(user)
	with open(bcl_file, 'w') as f:
		json.dump(block_list, f)

	return True
#__/
	

def _blockUserByID(userID:int) -> bool:

	"""Blocks the given user, identified by their user ID,
		from accessing the bot.  Returns True if successful;
		False if failure."""

	global _lastError

	_logger.normal(f"\tIn _blockUserByID() with userID={userID}...")

	# If the AI is trying to block the Creator, don't let it do that.
	if userID == 1774316494:	# Mike's user ID on Telegram.
		_logger.error("The AI tried to block the app developer! Disallowed.")
		_lastError = "Blocking the bot's creator, Michael, is not allowed."
		return False

	# Look up the complete user data.
	userData = _lookup_user(userID)
	isBlocked = userData['blocked']
	userTag = userData['userTag']

	# Check to see if they're already blocked.
	# If so, we don't need to do anything.
	if isBlocked:
		_logger.warn(f"_blockUserByID(): User {userTag} is already blocked. Ignoring.")
		_lastError = f"User {userTag} is already blocked; ignoring."
		return True

	# Do the block.
	_logger.normal(f"\tBlocking user {userTag} (ID={userID}) (by new method).")
	_set_user_blocked(userID, True)		# This actually updates the database.

	# Indicate that the user is blocked in the legacy system as well,
	# just because that file is more easily readable than the database.
	_blockUser(userTag)

	return True

#__/ End function blockUserByID().


def _call_desc(func_name:str, func_args:dict):
	"""Convert a function name and argument dictionary to a string
		representing the function call."""

	# Generate a description of the function call, for diagnostic purposes.
	kwargstr = ', '.join([f'{key}="{value}"' for key, value in func_args.items()])
	call_desc = f"{func_name}({kwargstr})"
	return call_desc
#__/


# This function checks whether the given user name is in our access list.
# If it is, it returns True; otherwise, it returns False.

def _check_access(user_name, prioritize_bcl=True, user_id:int=None) -> bool:

	"""Returns True if the given user may access the bot.
		Blacklist (bcl.[h]json) overrides whitelist (acl.hjson)
		unless prioritize_bcl=False is specified."""

	# If user_id argument is provided, just use the new user database.
	if user_id:
		return not _isBlockedByID(user_id)

	# Otherwise, use the legacy system.
	if prioritize_bcl:
		# Temporary override to have blacklist override whitelist.
		return not _isBlocked(user_name)

	# Get the value of environment variable AI_DATADIR.
	# This is where we'll look for the access list file.
	ai_datadir = AI_DATADIR

	# Now look for the file "acl.hjson" in the AI_DATADIR directory.
	# If it exists, then we'll use it as our access list.
	# If it doesn't exist, then we'll allow access to everyone except
	# who's in the blocklist.

	acl_file = os.path.join(ai_datadir, 'acl.hjson')
	if os.path.exists(acl_file):

		# Use the hjson module to load the access list file.
		# (This is a JSON-like file format that allows comments.)
		#import hjson	# NOTE: We already imported this at the top of the file.
		with open(acl_file, 'r') as f:
			access_list = hjson.load(f)			# Load the file into a Python list.

		# If the access list is empty, then we allow access to everyone.
		if len(access_list) > 0:

			# Otherwise, check whether the user name is in the access list.
			if user_name in access_list:
				return True
			else:
				return False
		#__/
	#__/

	# If we get here, either there's no acl or the acl is empty.
	# Allow the user unless they're in the blocklist.

	bcl_file = os.path.join(ai_datadir, 'bcl.hjson')
	if not os.path.exists(bcl_file):
		return True

	with open(bcl_file, 'r') as f:
		block_list = hjson.load(f)
		if user_name in block_list:
			return False

	# If we get here, there's no ACL and the user isn't blocked, so allow them.
	return True	

#__/ End definition of private function _check_access().


def _deleteMemoryItem(item_id=None, text=None):

    # Path to the database file
    db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_path)

    try:
        # Create a cursor object
        c = conn.cursor()

        if item_id is not None:
            # Delete the item with the specified item ID
            c.execute("DELETE FROM remembered_items WHERE itemID = ?", (item_id,))

        elif text is not None:
            # Delete the item with the specified item text
            c.execute("DELETE FROM remembered_items WHERE itemText = ?", (text,))

        # Commit the changes
        conn.commit()

    except sqlite3.Error as e:
		# Really should do better error handling here.
        print(f"An error occurred: {e.args[0]}")

    finally:
        # Close the connection
        conn.close()


async def _ensure_convo_loaded(update:Update, context:Context) -> bool:

	"""Helper function to ensure the conversation data is loaded,
		and auto-restart the conversation if isn't."""

	# Get the message, or edited message from the update.
	(message, edited) = _get_update_msg(update)
		
	if message is None:
		_logger.warning("In _ensure_convo_loaded() with no message? Aborting.")
		return False

	# Get the chat ID.
	chat_id = message.chat.id

	#if chat_id == -1002063308162 or chat_id == -1001661701088:
	#	_logger.warn(f"Ignoring message from stupid chat {chat_id}.")
	#	return False

	# Get the user's name.
	user_name = _get_user_tag(message.from_user)

	if not 'conversation' in context.chat_data:

		_logger.normal(f"\nUser {user_name} sent a message in an uninitialized conversation {chat_id}.")
		_logger.normal(f"\tAutomatically starting (or restarting) conversation {chat_id}.")

		diagMsg = "Either this is a new chat, or the bot server was rebooted. Auto-starting conversation."
			# NOTE: The AI won't see this diagnostic because the convo hasn't even been reloaded yet!

		sendRes = await _send_diagnostic(message, None, diagMsg, toAI=False)
		if sendRes != 'success': return False	# Callers expect Boolean

		await handle_start(update, context, autoStart=True)
		# We assume it succeeds.

	#__/
	
	return True
#__/


# This could be a method of class Conversation.
def _getDynamicMemory(convo:BotConversation):

	# Get current context (user & chat IDs).
	user = convo.last_user
	userID = user.id
	chatID = convo.chat_id

	# Our generic search phrase will be simply, the text of
	# the last message sent in the chat by the user..

	searchPhrase = convo.lastMessageBy(_get_user_tag(user)).text

	# Customize number of items returned based on context window size.
	fieldSize = global_gptCore.fieldSize
	if fieldSize >= 16000:		# 16k models and up
		nItems = 7
	elif fieldSize >= 8000:		# GPT-4 (initial release & up)
		nItems = 5
	elif fieldSize >= 4000:		# GPT-3.5 and up
		nItems = 3
	else:
		_logger.warn(f"This model has only {fieldSize} tokens. Dynamic memory  may overwhelm it.")
		nItems = 2

	# We'll get the best-matching N items (based on field size).
	memList = _searchMemories(userID, chatID, searchPhrase, nItems=nItems)

	# We'll accumulate lines with the following format:
	#
	#	id=<itemID> (user:<userTag> private/public local/global) <text>

	memString = ""
	for mem in memList:

		itemID = mem['itemID']
		userID = mem['userID']
		isPublic = not mem['is_private']
		isGlobal = mem['is_global']
		itemText = mem['itemText']
		
		# Look up detailed user data. This is a dict with keys:
		#	'dispName', 'userName', 'userID', 'userTag', 'blocked'.
		userData = _lookup_user(userID)
		if userData:
			userTag = userData['userTag']		# Could sometimes be "(unknown)"
		else:	# Not sure why this happens, but it does.
			userTag = '(null)'

		privacy = "public" if isPublic else "private"
		locality = "global" if isGlobal else "local"

		memString += f"itemID={itemID} (user:{userTag} {privacy} {locality}) {itemText}\n"

	return memString

#__/ 


def _getEmbedding(text):

	"""Gets the embedding of a given text, as a vector (list)."""

    # Get the response from OpenAI Embeddings API. Returns a vector.
	embedding_asList = get_embedding(text, engine="text-embedding-ada-002")

	return embedding_asList

#__/


def _getEmbeddingStr(text):
	"""Gets a string representation of the embedding of a text."""

	# Get the response from OpenAI Embeddings API. Returns a vector.
	embedding_asList = _getEmbedding(text)

	# Convert the embedding list to a comma-separated string
	embedding_str = _listToStr(embedding_asList)

	return embedding_str
#__/


def _getEmbeddingPickle(text):
    """Gets a pickled numpy array representation of the embedding of a text."""

    # Get the response from OpenAI Embeddings API. Returns a vector.
    embedding_asList = _getEmbedding(text)

    # Convert the embedding list to a numpy array and pickle it
    embedding_np = np.array(embedding_asList)
    embedding_pickle = pickle.dumps(embedding_np, protocol=pickle.HIGHEST_PROTOCOL)

    return embedding_pickle


# This function extracts the edited_message or message field from an update,
# as appropriate, and returns the pair (message, edited).
def _get_update_msg(update:Update):
	edited = False
	message = None
	if update.edited_message is not None:
		message = update.edited_message
		edited = True
	elif update.message is not None:
		message = update.message
	return (message, edited)


# This function, given a Telegram user object, returns a string that identifies the user.
def _get_user_tag(user) -> str:

	"""Return a string that identifies the given Telegram user."""

	global _which_name

	# Decide what we'll call this user. We'll use their first_name attribute, unless it
	# is None, or an empty string, or contains non-identifier characters, in which case 
	# we'll use their username attribute. If that's also None, we'll use their ID. 

	user_name = user.first_name
		# By default, we'll use the user's first name.
	_which_name = 'first name'

	# If the user's first name is an empty string, we'll invalidate it by setting it to None.
	if user_name == '':
		user_name = None

	# If we're using the GPT-3 Chat API, we'll also need to make sure that the user's name
	# is a valid identifier that's accepted by that API as a user name.
	if user_name is not None and global_gptCore.isChat:
		# If the user's first name contains characters the GPT-3 Chat API won't accept 
		# (or is too long or an empty string), we'll invalidate it by setting it to None.
		if not re.match(r"^[a-zA-Z0-9_-]{1,64}$", user_name):
			user_name = None

	# If the user's first name wasn't valid, we'll try to use their username.
	if user_name is None:
		user_name = user.username
		_which_name = 'username'

		# But, if that name isn't valid either, we'll use their ID.
		if user_name is None or user_name == '':
			user_name = str(user.id)
			_which_name = 'user ID'

	return user_name

#__/ End private function _get_user_tag().


def _initBotDB():

	"""Creates a database that's used to store relevant information
		for the Telegram bot. So far this includes these tables:

			o users - List of known Telegram users. Keeps track
				of the user's display name, username, user ID,
				and whether they are currently blocked.
	
			o remembered_items - Dynamically added persistent
				memories, added with the /remember command or
				the remember_item() function.

		"""

	# Path to the 'telegram' subdirectory
	dir_path = os.path.join(AI_DATADIR, 'telegram')

	# Create the 'telegram' subdirectory if it doesn't already exist
	os.makedirs(dir_path, exist_ok=True)

	# Path to the database file
	db_path = os.path.join(dir_path, 'bot-db.sqlite')
	
	# Create a connection to the SQLite database
	# If database does not exist, it is created here
	conn = sqlite3.connect(db_path)

	# Create a cursor object
	c = conn.cursor()

	## OLD VERSION:
	## Creating table if it doesn't exist
	#c.execute('''
	#	CREATE TABLE IF NOT EXISTS remembered_items (
	#		itemID TEXT PRIMARY KEY,
	#		userID INTEGER,
	#		chatID INTEGER,
	#		public BOOLEAN,
	#		global BOOLEAN,
	#		itemText TEXT,
	#		embedding TEXT
	#	);
	#''')

	# NEW VERSION:
	# Creating table if it doesn't exist
	c.execute('''
		CREATE TABLE IF NOT EXISTS remembered_items (
			itemID TEXT PRIMARY KEY,
			userID INTEGER,
			chatID INTEGER,
			public BOOLEAN,
			global BOOLEAN,
			itemText TEXT,
			embedding_blob BLOB
		);
	''')

	# Creating 'users' table if it doesn't exist
	c.execute('''
		CREATE TABLE IF NOT EXISTS users (
			displayName TEXT,
			username TEXT,
			userID INTEGER PRIMARY KEY,
			blocked BOOLEAN,
			userTag TEXT);
	''')

	# If the 'userTag' column doesn't exist yet, add it.
	c.execute("PRAGMA table_info(users)")
	cols = c.fetchall()
	if "usertag" not in (col[1].lower() for col in cols):
		c.execute("ALTER TABLE users ADD COLUMN userTag TEXT")

	# Commit the transaction
	conn.commit()

	# Close the connection
	conn.close()

#__/ End definition of private function _initBotDB


	#----------------------------------------------------------------------
	# This function initializes the AI's persistent context information
	# based on the PERSISTENT_DATA string. We'll call it whenever the
	# PERSISTENT_DATA string changes, which will happen when we read the
	# AI's persistent memory file, or when a '/remember' command is issued.
	
def _initPersistentContext() -> None:

	global globalPersistentData, globalPersistentContext	# So we can modify these.

	# Initialize the AI's persistent context information.

	## No longer needed because we now give a command menu even 
	## when the AI has functions as well.
	#
	#if hasFunctions(ENGINE_NAME):
	#	globalPersistentContext = \
	#		MESSAGE_DELIMITER + PERMANENT_CONTEXT_HEADER + \
	#		globalPersistentData + \
	#		MESSAGE_DELIMITER + RECENT_MESSAGES_HEADER
	#	#__/
	#else:

	# We now use this version always.
	globalPersistentContext = \
		MESSAGE_DELIMITER + PERMANENT_CONTEXT_HEADER + \
			globalPersistentData + \
		MESSAGE_DELIMITER + COMMAND_LIST_HEADER + \
			"  /pass - Refrain from responding to the last user message.\n" + \
			"  /image <desc> - Generate an image with description <desc> and send it to the user.\n" + \
			"  /remember <text> - Adds <text> to my persistent context data.\n" + \
			"  /forget <text> - Removes <text> from my persistent context data.\n" + \
			"  /block [<user>] - Adds the user to my block list. Defaults to current user.\n" + \
			"  /unblock [<user>] - Removes the user from my block list. Defaults to current user.\n" + \
		MESSAGE_DELIMITER + RECENT_MESSAGES_HEADER

	#__/
#__/


		#-----------------------------------------------------------------------
		# Initialize the bot's persistent data string, including any dynamical-
		# ly-added persistent memories.
		#
		# NOTE: The memory/context stuff in globals really needs to be augmented
		# w. additional memories that are specific to an individual conversation
		# and/or user.

def _initPersistentData() -> None:
	"""Initialize the persistent data string (including memories, if any)."""

	global globalPersistentData

	# This function initializes the AI's persistent context data.

	# Initialize the main data for the AI's persistent context.
	globalPersistentData = aiConf.context 
		# NOTE: This should end with a newline. But if it doesn't, we'll add one.

	# Ensure that PERSISTENT_DATA ends with a newline.
	if globalPersistentData[-1] != '\n':
		globalPersistentData += '\n'

	# Append current memories, if any.
	if MEMORIES != "":
		globalPersistentData += MESSAGE_DELIMITER + PERSISTENT_MEMORY_HEADER
		globalPersistentData += MEMORIES

	# NOTE: The MEMORIES variable is intended for global (but dynamic) memories
	# for the current bot. Eventually we need to also add a section for user-
	# specific and/or chat-specific memories.
#__/ End definition of _initPersistentData() function.

	
# NOTE: THIS FUNCTION ONLY CONSULTS THE LEGACY FILES.
def _isBlocked(user:str) -> bool:
	"""Return True if user is on blacklist, or if there
		is a whitelist and the user is not on it."""
	
	# Get the value of environment variable AI_DATADIR.
	# This is where we'll look for the block list files.
	ai_datadir = AI_DATADIR
	
	# User is blocked if they're in the bcl.hjson file.

	bcl_file = os.path.join(ai_datadir, 'bcl.hjson')
	if os.path.exists(bcl_file):
		with open(bcl_file, 'r') as f:
			block_list = hjson.load(f)
			if user in block_list:
				return True
		
	# User is blocked if they're in the bcl.json file.
	
	bcl_file = os.path.join(ai_datadir, 'bcl.json')
	if os.path.exists(bcl_file):
		with open(bcl_file, 'r') as f:
			block_list = json.load(f)
			if user in block_list:
				return True

	# Not in either file? Check to see if there's an ACL (whitelist) and user is not in it.

	acl_file = os.path.join(ai_datadir, 'acl.hjson')
	if os.path.exists(acl_file):	# If whitelist doesn't exist, user isn't blocked.
		
		with open(acl_file, 'r') as f:
			access_list = hjson.load(f)			# Load the file into a Python list.

		# If the whitelist is empty, then we allow access to everyone.
		if len(access_list) > 0:

			# Otherwise, check whether the user name is in the access list.
			if user in access_list:
				return False	# User is not blocked.
			else:
				return True		# There's a whitelist but user isn't in it. Effectively blocked.

	return False

#__/ End private function _isBlocked().


def _isBlockedByID(userID:int) -> bool:

	# Look up the complete user data.

	if userID:
		userData = _lookup_user(userID)
		if userData is None:
			_logger.warn(f"Couldn't find user data for ID#{userID}; assuming not blocked.")
			return False	# If user does not exist, assume not blocked. (Is this a good idea?)
		isBlocked = userData['blocked']
		return isBlocked
	else:
		_logger.error("Falsy user ID passed to _isBlockedByID().")
		return None	# Is this a good idea?


def _listToStr(vec:list):
	"Given a vector, return a comma-separated list."
	return ",".join(map(str, vec))


def _logOaiMsgs(oaiMsgList:list, basename="latest-messages") -> None:

	# Convert messages from OpenAI's new object representation back
	# to the legacy dict representation that we use in our code.
	newList = []
	for msg in oaiMsgList:
		if isinstance(msg, openai.types.chat.ChatCompletionMessage):
			newMsg = oaiMsgObj_to_msgDict(msg)
			fcall = newMsg.get('function_call', None)
			if fcall:
				new_fcall = {'name': fcall.name, 'arguments': fcall.arguments}
				newMsg['function_call'] = new_fcall
		else:
			newMsg = msg
		newList.append(newMsg)
	oaiMsgList = newList

	# Open the file for writing.
	with open(f"{LOG_DIR}/{basename}.txt", "w") as f:
		for oaiMessage in oaiMsgList:
			f.write(messageRepr(oaiMessage))
				# Our text representation of OpenAI messages.
	
	# Also do a json dump
	with open(f"{LOG_DIR}/{basename}.json", "w") as outfile:
		json.dump(oaiMsgList, outfile)

#__/


def _lookup_user(user_id):

	# Path to the database file
	db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

	# Create a connection to the SQLite database
	conn = sqlite3.connect(db_path)

	# Create a cursor object
	c = conn.cursor()

	# Execute a SQL command to select the row with the given user ID
	c.execute("SELECT * FROM users WHERE userID = ?", (user_id,))

	# Fetch the row
	row = c.fetchone()

	# If a row was found, print it
	if row is not None:
		result = {
			'dispName': row[0],
			'userName': row[1],
			'userID':	row[2],
			'blocked':	row[3],
			'userTag':	row[4] or 'unknown'
				# NOTE: col. 3 could be None if this user hasn't
				# been loaded yet since we added this new field.
		}
			
	else:
		result = None

	# Close the connection
	conn.close()

	return result
#__/


def _lookup_user_by_dispname(disp_name):

    # Path to the database file
    db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object
    c = conn.cursor()

    # Execute a SQL command to select rows with the given user display name (first+last name).
    c.execute("SELECT * FROM users WHERE displayName = ?", (disp_name,))

    # Fetch all rows
    rows = c.fetchall()

    results = []
    for row in rows:
        results.append({
            'dispName': row[0],
            'userName': row[1],
            'userID':   row[2],
            'blocked':  row[3],
            'userTag':  row[4] or 'unknown'
        })

    # Close the connection
    conn.close()

    return results


def _lookup_user_by_username(username):

    # Path to the database file
    db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object
    c = conn.cursor()

    # Execute a SQL command to select rows with the given username.
    c.execute("SELECT * FROM users WHERE username = ?", (username,))

    # Fetch all rows
    rows = c.fetchall()

    results = []
    for row in rows:
        results.append({
            'dispName': row[0],
            'userName': row[1],
            'userID':   row[2],
            'blocked':  row[3],
            'userTag':  row[4] or 'unknown'
        })

    # Close the connection
    conn.close()

    return results


def _lookup_user_by_tag(user_tag):

    # Path to the database file
    db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object
    c = conn.cursor()

    # Execute a SQL command to select rows with the given user tag.
    c.execute("SELECT * FROM users WHERE userTag = ?", (user_tag,))

    # Fetch all rows
    rows = c.fetchall()

    results = []
    for row in rows:
        results.append({
            'dispName': row[0],
            'userName': row[1],
            'userID':   row[2],
            'blocked':  row[3],
            'userTag':  row[4] or 'unknown'
        })

    # Close the connection
    conn.close()

    return results


def _printMemories():

	# Path to the database file
	db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

	# Create a connection to the SQLite database
	conn = sqlite3.connect(db_path)

	# Create a cursor object
	c = conn.cursor()

	try:
		# Create a cursor object
		c = conn.cursor()

		# Select all the columns except for embedding.
		c.execute("SELECT itemID, userID, chatID, public, global, "
				  "itemText FROM remembered_items")

		_logger.normal("\n"
					   "CONTENTS OF remembered_items TABLE in bot-db.sqlite:\n"
					   "('ItemID', userID, chatID, public, global, 'itemText')\n"
					   "======================================================")

		# Fetch all rows from the table
		rows = c.fetchall()
		for row in rows:
			_logger.normal(row)

	except sqlite3.Error as e:
		print(f"An error occurred: {e.args[0]}")

	finally:
		# Close the connection
		conn.close()
	#__/

#__/ 


def _printUsers():

	# Path to the database file
	db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

	# Create a connection to the SQLite database
	conn = sqlite3.connect(db_path)

	# Create a cursor object
	c = conn.cursor()

	try:
		# Create a cursor object
		c = conn.cursor()

		# Select all the columns.
		c.execute("SELECT * FROM users")

		_logger.normal("\n"
					   "CONTENTS OF users TABLE in bot-db.sqlite:\n"
					   "('displayName', 'username', userID, blocked, userTag)\n"
					   "=====================================================")

		# Fetch all rows from the table
		rows = c.fetchall()
		for row in rows:
			_logger.normal(row)

	except sqlite3.Error as e:
		print(f"An error occurred: {e.args[0]}")

	finally:
		# Close the connection
		conn.close()
	#__/

#__/


### NOTE: The following approach to markdown parsing does not handle partially overlapping spans. For example:
###
### ```markdown
### Here the user *starts a bold span, 
### then _starts an italic span, 
### then ends the bold span*, then 
### ends the italic span._ So crazy!```
### 
### Normal markdown environments won't render that as intended. But, we could translate the above text to correctly nested markdown like so:
###
### ```markdown
### Here the user *starts a bold span, then _starts an italic span, then ends the bold span_*_, then ends the italic span._ So crazy!```
###
### Note how in the above, we turn off italic before turning off bold to keep those spans properly nested,
### but then immediately turn on italic again so that the text renders as the user intended.


# Define the bits in the "inside mask" for markdown parsing.

IN_BOLD				= 1<<0	# We're in a boldface span of text.
IN_ITALIC			= 1<<1	# We're in an italicized span of text.
IN_UNDERLINE		= 1<<2	# We're in an underlined span of text.
IN_STRIKETHROUGH	= 1<<3	# We're in a struck-through span of text.
IN_INLINE_CODE		= 1<<4	# We're in an inline fixed-width code span.
IN_CODE_BLOCK		= 1<<5	# We're in a multiline preformatted code block.
IN_CODE				= (IN_INLINE_CODE | IN_CODE_BLOCK)	# We're in either type of code span.
IN_HYPERLINK_TEXT	= 1<<6	# We're in the linked-text part of a hyperlink.
IN_HYPERLINK_URL	= 1<<7	# We're in the URL part of a hyperlink.
IN_HYPERLINK		= (IN_HYPERLINK_TEXT | IN_HYPERLINK_URL)
							# We're in one of the parts of a hyperlink.


ALT_BOLD_PATTERN		= r"\*\*(?:\\\*|\\\\|\*(?!\*)|[^*])+\*\*"
	# Inside double asterisks we can have '\*' (escaped asterisk), '\\' (escaped backslash),
	# single asterisks, and any other non-asterisk characters.
	
BOLD_PATTERN		= r"\*(?:\\\*|\\\\|[^*])+\*"
	# Inside asterisks we can have '\*' (escaped asterisk), '\\' (escaped backslash),
	# and any other non-asterisk characters.
	
# Alternative pattern for underlining: "___...___".
ALT_UNDERLINE_PATTERN = r"___(?:\\_|\\\\|_(?!_)|__(?!_)|[^_])+___"
	# Inside triple-underscores we can have '\_' (escaped underscore), '\\' (escaped backslash),
	# single or double underscores, and any other non-underscore characters.

UNDERLINE_PATTERN	= r"__(?:\\_|\\\\|_(?!_)|[^_])+__"
	# Inside double-underscores we can have '\_' (escaped underscore), '\\' (escaped backslash),
	# single underscores, and any other non-underscore characters.

ALT_ITALIC_PATTERN  = UNDERLINE_PATTERN

ITALIC_PATTERN		= r"_(?:\\_|\\\\|__(?!_)|[^_])+_"
	# Inside single-underscores we can have '\_' (escaped underscore), '\\' (escaped backslash),
	# '__' (double underscore), and any other non-underscore characters.

ALT_STRIKETHROUGH_PATTERN	= r"~~(?:\\~|\\\\|~(?!~)|[^~])+~~"
	# Inside double tildes we can have '\~' (escaped tilde), '\\' (escaped backslash),
	# single tildes, and any other non-tilde characters.

STRIKETHROUGH_PATTERN	= r"~(?:\\~|\\\\|[^~])+~"
	# Inside tildes we can have '\~' (escaped tilde), '\\' (escaped backslash),
	# and any other non-tilde characters.

CODE_BLOCK_PATTERN	= r"```(?:\\`|\\\\|`(?!`)|``(?!`)|[^`])+```"
	# Inside triple-backticks we can have '\`' (escaped backtick), '\\' (escaped backslash),
	# single or double backticks, and any other non-underscore characters.

INLINE_CODE_PATTERN	= r"`(?:\\`|\\\\|[^`])+`"
	# Inside single-backticks we can have '\`' (escaped backticks), '\\' (escaped backslash),
	# and any other non-backtick characters. NOTE: We require what's inside single-backticks
	# to be non-empty. So "```" -> "`\``" instead of "``\`".

HYPERLINK_PATTERN	= r"\[(?P<hlink_text>(?:\\\]|\\\\|[^\]])+)\]\((?P<hlink_url>(?:\\\)|\\\\|[^\)])+)\)"
	# [...](...) form. Both parts are captured. 
	#	Elements in link text can include: Escaped close bracket '\]', escaped backslash '\\', any non-close-bracket character.
	#	Elements in url text can include: Escaped close paren '\)', escaped backslash '\\', any non-close-paren character

UNESCAPED_SPECIALS	= r"-_*[\]()~`>#+=|{}.!\\"
	# This is used later for defining character sets in regexes.
	# It's important that the '-' is first (or last) here since otherwise it'll be interpreted as indicating a character range.
	# We need to escape ']' here since it ends a character set. And we escape '\' since a single backslash starts an escaped character.


def _cleanup_markdown(text, inside_mask=0):

	"""Attempts to clean up (make legal) the given text, interpreted
		as Telegram Markdown V2 format. NOTE: spoilers and custom emojis
		are not yet supported."""

	# Note that generally re.sub() will try to match the longest
	# matching element each time, so we don't really have to worry
	# that shorter elements might take precedence over longer ones.
	# However, to hellp clarify our intent to human readers, we will
	# list the longer elements first in the regex, if appropriate.

	regex = ""

	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| First up we'll do the code spans, since they suppress most of
	#| the other special parsing rules inside themselves.

	## Next up is the code block pattern. Six delimiters!

	# If not inside a code block already, or a hyperlink,
	if inside_mask & (IN_CODE_BLOCK | IN_HYPERLINK) == 0:	
		# include the code block pattern in the regex.
		regex += r"(?P<code_block>" + CODE_BLOCK_PATTERN + ')|'

	## We'll look for inline code blocks next.

	# If not inside a code span already, or a hyperlink,
	if inside_mask & (IN_CODE | IN_HYPERLINK) == 0:
		# include the inline code pattern in the regex.
		regex += r"(?P<inline_code>" + INLINE_CODE_PATTERN + ')|'

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Hyperlinks are the most complex pattern, and they suppress code
	# block parsing in their text sections, so we'll do those next.

	# If not inside a hyperlink already, or a code span
	if inside_mask & (IN_HYPERLINK | IN_CODE) == 0:
		# include the hyperlink pattern in the regex.
		regex += r"(?P<hyperlink>" + HYPERLINK_PATTERN + ')|'

	#|===============================================================
	#| Next comes various types of spans of formatted text.
	#|		 NOTE: These don't apply inside code spans or URLs!
	#|
	#|	ALSO NOTE: We are now only recognizing alternative styles.
	#|		This is so that single delimiters '*', '_', '~' will 
	#|		just get escaped (and thus rendered literally) instead
	#|		of being interpreted as markdown.

	## First we'll look for spans of strikethrough text (rarest).

	# If not inside a strikethrough text span already,
	#	or a code span, or a hyperlink URL,
	if inside_mask & (IN_STRIKETHROUGH | IN_CODE | IN_HYPERLINK_URL) == 0:

		# include the extra strikethrough text span pattern in the regex.
		regex += r"(?P<alt_strikethrough_text>" + ALT_STRIKETHROUGH_PATTERN + ')|'

		## include the strikethrough text span pattern in the regex.
		#regex += r"(?P<strikethrough_text>" + STRIKETHROUGH_PATTERN + ')|'
		
	## Next we'll look for spans of underlined text (triple '_' delimiter).

	# If not inside an underline text span already, or a code span, or a URL,
	if inside_mask & (IN_UNDERLINE | IN_CODE | IN_HYPERLINK_URL) == 0:
		# include the alternative underline text span pattern in the regex.
		regex += r"(?P<alt_underline_text>" + ALT_UNDERLINE_PATTERN + ')|'

	## If not inside an underline text span already, or a code span, or a URL,
	#if inside_mask & (IN_UNDERLINE | IN_CODE | IN_HYPERLINK_URL) == 0:
	#	# include the underline text span pattern in the regex.
	#	regex += r"(?P<underline_text>" + UNDERLINE_PATTERN + ')|'

	## Next we'll look for spans of italicized text (single '_' delimiter).

	# If not inside an italic text span already, or a code span, or a URL,
	if inside_mask & (IN_ITALIC | IN_CODE | IN_HYPERLINK_URL) == 0:
		# include the alternative italic text span pattern in the regex.
		regex += r"(?P<alt_italic_text>" + ALT_ITALIC_PATTERN + ')|'

	## If not inside an italic text span already, or a code span, or a URL,
	#if inside_mask & (IN_ITALIC | IN_CODE | IN_HYPERLINK_URL) == 0:
	#	# include the italic text span pattern in the regex.
	#	regex += r"(?P<italic_text>" + ITALIC_PATTERN + ')|'

	## Next we'll look for spans of boldface text (single or double '*' delimiter).

	# If not in a strikethrough text span already, or a URL.
	if inside_mask & (IN_BOLD | IN_CODE | IN_HYPERLINK_URL) == 0:

		# AIs sometimes use double asterisks. We'll work with it.
		# Include the extra bold text span pattern in the regex.
		regex += r"(?P<alt_bold_text>" + ALT_BOLD_PATTERN + ')|'

		## Single asterisk is correct.
		## Include the bold text span pattern in the regex.
		#regex += r"(?P<bold_text>" + BOLD_PATTERN + ')|'

	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| Now we'll check for reserved characters, in both their escaped
	#| and unescaped forms, in the contexts where they're treated
	#| specially. Note we have three basic types of contexts:
	#|
	#|		1. Normal contexts: This includes both normal text
	#|			and hyperlink text. All reserved characters are
	#|			supposed to be escaped in such contexts. '\'
	#|			should be escaped when not escaping something.
	#|
	#|		2. URL context: This is a hyperlink URL. ')' and '\'
	#|			should always be escaped in this context.
	#|
	#|		3. Code context: Either block or inline. "`" and '\'
	#|			should always be escaped in this context.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	# First we decide what the set of special characters is now:
	if inside_mask & IN_CODE:	# In a code context.
		specials = r"`\\"		# Backtick and backslash.

	elif inside_mask & IN_HYPERLINK_URL:	# In a URL context.
		specials = r")\\"		# Close-paren and backslash.

	else:	# In a normal context.
 		specials = UNESCAPED_SPECIALS

	# OK, next we'll first check for properly escaped specials:
	regex += r"(?P<escaped_special>" + r'\\[' + specials + "])|"

	# And then we'll check for unescaped specials (note these
	# will need to be automatically escaped in general).
	regex += r"(?P<unescaped_special>[" + specials + "])|"

	## And finally we'll check for normal (non-special) chars.
	#regex += r"(?P<normal_char>[^" + specials + "])"
	## NOTE: Commented this out because we don't actually need
	##	to do anything for normal chars, we can just let re.sub()
	##	pass right on over them.

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# At this point, we have assembled the complete regex that is
	# appropriate to use with re.sub() in this context, so we go
	# ahead and do the substitution, using our custom replacement
	# function, which we define right here before using it.

	def _local_replaceFunc(match):
		"""Custom replacement function, defined in the local
			lexical context, which transforms matched elements
			appropriately to hopefully massage them into a form
			that will pass Telegram's Markdown V2 parser. Note
			this recursively calls _cleanup_markdown() where
			needed."""

		# NOTE: We get the raw group dictionary here so we can use .get()
		# on it. We do this because our regex varies based on context, so
		# not all groups will even be defined in all contexts.

		named_groups = match.groupdict()

		# Is this a code block?
		code_block = named_groups.get('code_block')
		if code_block:

			#_logger.normal(f"I found a code block with contents: [\n{code_block}\n]")

			# Get the body text of the code block.
			body_text = code_block[3:-3]	# Strip delimiters off ```...```

			# Clean it up.
			clean_body = _cleanup_markdown(body_text, inside_mask | IN_CODE_BLOCK)

			# Reassemble and return the cleaned code block.
			return f"```{clean_body}```"

		# Is this an inline code span?
		inline_code = named_groups.get('inline_code')
		if inline_code:

			#_logger.normal(f"I found inline code with contents: [{inline_code}]")

			# Get the body text of the code block.
			body_text = inline_code[1:-1]	# Strip delimiters off `...`

			# Clean it up.
			clean_body = _cleanup_markdown(body_text, inside_mask | IN_INLINE_CODE)

			# Reassemble and return the cleaned code block.
			return f"`{clean_body}`"

		# Is this a hyperlink?
		hyperlink = named_groups.get('hyperlink')
		if hyperlink:

			#_logger.normal(f"I found a hyperlink: [{hyperlink}]")

			# Get the text and URL portions.
			hlink_text = match.group('hlink_text')
			hlink_url = match.group('hlink_url')

			# Clean them both up appropriately.
			clean_text = _cleanup_markdown(hlink_text,
										   inside_mask | IN_HYPERLINK_TEXT)
			clean_url = _cleanup_markdown(hlink_url,
										  inside_mask | IN_HYPERLINK_URL)

			# Reassemble and return the cleaned hyperlink.
			return f"[{clean_text}]({clean_url})"
			
		# Is this an extra strikethrough text span?
		alt_strikethrough_text = named_groups.get('alt_strikethrough_text')
		if alt_strikethrough_text:

			#_logger.normal(f"I found alternative strikethrough text: [{alt_strikethrough_text}]")

			# Get the text span.
			span_text = alt_strikethrough_text[2:-2]	# Strip delimiters off ~~...~~

			# Clean it up appropriately.
			clean_span = _cleanup_markdown(span_text,
										   inside_mask | IN_STRIKETHROUGH)

			# Reassemble and return the cleaned strikethrough span.
			return f"~{clean_span}~"

		## Is this a strikethrough text span?
		#strikethrough_text = named_groups.get('strikethrough_text')
		#if strikethrough_text:
		#
		#	_logger.normal(f"I found strikethrough text: [{strikethrough_text}]")
		#
		#	# Get the text span.
		#	span_text = strikethrough_text[1:-1]	# Strip delimiters off ~...~
		#
		#	# Clean it up appropriately.
		#	clean_span = _cleanup_markdown(span_text,
		#								   inside_mask | IN_STRIKETHROUGH)
		#
		#	# Reassemble and return the cleaned strikethrough span.
		#	return f"~{clean_span}~"

		# Is this an alternative underlined text span?
		alt_underlined_text = named_groups.get('alt_underline_text')
		if alt_underlined_text:

			#_logger.normal(f"I found alternative underlined text: [{alt_underlined_text}]")

			# Get the text span.
			span_text = alt_underlined_text[3:-3]	# Strip delimiters off ___...___

			# Clean it up appropriately.
			clean_span = _cleanup_markdown(span_text,
										   inside_mask | IN_UNDERLINE)

			# Reassemble and return the cleaned alternative-underlined span.
			return f"__{clean_span}__"

		## Is this an underlined text span?
		#underlined_text = named_groups.get('underline_text')
		#if underlined_text:
		#
		#	_logger.normal(f"I found underlined text: [{underlined_text}]")
		#
		#	# Get the text span.
		#	span_text = underlined_text[2:-2]	# Strip delimiters off __...__
		#
		#	# Clean it up appropriately.
		#	clean_span = _cleanup_markdown(span_text,
		#								   inside_mask | IN_UNDERLINE)
		#
		#	# Reassemble and return the cleaned underlined span.
		#	return f"__{clean_span}__"

		# Is this an alternative italic text span?
		alt_italic_text = named_groups.get('alt_italic_text')
		if alt_italic_text:

			#_logger.normal(f"I found alternative italic text: [{alt_italic_text}]")

			# Get the text span.
			span_text = alt_italic_text[2:-2]	# Strip delimiters off __...__

			# Clean it up appropriately.
			clean_span = _cleanup_markdown(span_text,
										   inside_mask | IN_ITALIC)

			# Reassemble and return the cleaned italicized span.
			return f"_{clean_span}_"

		## Is this an italicized text span?
		#italicized_text = named_groups.get('italic_text')
		#if italicized_text:
		#
		#	_logger.normal(f"I found italicized text: [{italicized_text}]")
		#
		#	# Get the text span.
		#	span_text = italicized_text[1:-1]	# Strip delimiters off _..._
		#
		#	# Clean it up appropriately.
		#	clean_span = _cleanup_markdown(span_text,
		#								   inside_mask | IN_ITALIC)
		#
		#	# Reassemble and return the cleaned italicized span.
		#	return f"_{clean_span}_"

		# Is this a boldface or extra-bold text span?
		alt_bold_text = named_groups.get('alt_bold_text')
		if alt_bold_text:

			#_logger.normal(f"I found alternative bold text: [{alt_bold_text}]")

			# Get the text span.
			span_text = alt_bold_text[2:-2]		# Strip delimiters off **...**

			# Clean it up appropriately.
			clean_span = _cleanup_markdown(span_text,
										   inside_mask | IN_BOLD)

			# Reassemble and return the cleaned boldface span.
			return f"*{clean_span}*"

		#boldface_text = named_groups.get('bold_text')
		#if boldface_text:
		#
		#	_logger.normal(f"I found boldface text: [{boldface_text}]")
		#
		#	# Get the text span.
		#	span_text = boldface_text[1:-1]		# Strip delimiters off *...*
		#
		#	# Clean it up appropriately.
		#	clean_span = _cleanup_markdown(span_text,
		#								   inside_mask | IN_BOLD)
		#
		#	# Reassemble and return the cleaned boldface span.
		#	return f"*{clean_span}*"

		# Already-escaped specials we just return unmodified...
		escaped_special = named_groups.get('escaped_special')
		if escaped_special:
			return escaped_special

		# Unescaped specials, we escape and return (whole point of all this)..
		unescaped_special = named_groups.get('unescaped_special')
		if unescaped_special:
			return '\\' + unescaped_special
		
		# We should never get here!

		## And normal characters, we just return unmodified.
		#normal_char = match.group('normal_char')
		#return normal_char

	#__/ End local private replacement function _local_replacefunc().

	#_logger.normal(f"Using regex: {regex}\nto clean up text [\n{text}\n]")

	# Now replace all regex matches in the text with their cleaned versions.
	cleanText = re.sub(regex, _local_replaceFunc, text)

	#_logger.normal(f"Got cleaned-up text: [\n{cleanText}\n]")

	# We are done! Just return the cleaned-up text.
	return cleanText


# Sends a message to the user, with some appropriate exception handling.
# Returns 'success' if the send succeeded, or an error string if it failed.
# If ignore=True, then the error string indicates that the error is being
# ignored by the program.
async def _reply_user(userTgMessage:TgMsg, convo:BotConversation,
					  msgToSend:str, ignore:bool=False, markup:bool=False) -> str:

	"""Sends text message <msgToSend> in reply to the user's
		Telegram message <userTgMessage> in conversation <convo>."""

	message = userTgMessage		# Shorter name.

	# Get the user name.
	user_name = _get_user_tag(message.from_user)

	# Get the chat ID from the conversation (if supplied) or the message.
	if convo is None:
		chat_id = message.chat.id
	else:
		chat_id = convo.chat_id

	# If our caller requested we utilize markup to style our message,
	# then turn on the 'MarkdownV2' parse mode supported by Telegram,
	# and make sure reserved characters are properly escaped.

	if markup:
		parseMode = ParseMode.MARKDOWN_V2
		text = _cleanup_markdown(msgToSend)
	else:
		parseMode = None
		text = msgToSend

	#_logger.normal("ATTEMPTING TO SEND:[[[\n" + text + '\n]]]')

	# Try sending the message to the user.
	while True:
		try:

			await message.reply_text(text, parse_mode=parseMode)
			break
	
		except BadRequest or Forbidden or ChatMigrated or TimedOut as e:
	
			exType = type(e).__name__
	
			if exType == 'BadRequest' and str(e).startswith("Can't parse entities"):

				errmsg = str(e)

				_logger.error(f"Got a markdown error from Telegram in chat {chat_id}: {e}. Punting on markdown.")

				text = msgToSend	# Revert to original text.
				parseMode = None	# Turn off markdown parsing.

				continue	# Try again without markdown
				
			whatDoing = "ignoring" if ignore else "aborting"
	
			_logger.error(f"Got a {exType} exception from Telegram ({e}) "
						  f"for conversation {chat_id}; {whatDoing}.")
	
			if convo is not None:
				convo.add_message(BotMessage(SYS_NAME, "[ERROR: Telegram exception " \
					f"{exType} ({e}) while sending to user {user_name}.]"))
	
			if isinstance(e, BadRequest) and "Not enough rights to send" in e.message:
				try:
					await app.bot.leave_chat(chat_id)
					_logger.normal(f"Left chat {chat_id} due to insufficient permissions.")
				except Exception as leave_error:
					_logger.error(f"Error leaving chat {chat_id}: {leave_error}")

			return f"error: Telegram threw a {exType} exception while sending " \
				"output to the user"
	
	#__/

	#if convo is None:
	#	_logger.normal("NOTE: convo is None, so not trying to convert text to speech.")
	#else:
	#	_logger.normal(f"NOTE: The speech_on flag is {convo.speech_on}.")


	# If speech mode is on, try also converting the text to a voice clip and sending that too."
	if convo is not None and convo.speech_on:
		while True:
			try:
				await _reply_asSpeech(message, convo, text)

				convo.add_message(BotMessage(SYS_NAME,
					"[Voice clip automatically generated and sent to user.]"))

				break

			except BadRequest or Forbidden or ChatMigrated or TimedOut as e:
	
				exType = type(e).__name__
	
				whatDoing = "ignoring" if ignore else "aborting"
	
				_logger.error(f"Got a {exType} exception from Telegram ({e}) "
							  f"for conversation {chat_id}; {whatDoing}.")
	
				if convo is not None:
					convo.add_message(BotMessage(SYS_NAME, "[ERROR: Telegram exception " \
						f"{exType} ({e}) while sending to user {user_name}.]"))
	
				if isinstance(e, BadRequest) and "Not enough rights to send" in e.message:
					try:
						await app.bot.leave_chat(chat_id)
						_logger.normal(f"Left chat {chat_id} due to insufficient permissions.")
					except Exception as leave_error:
						_logger.error(f"Error leaving chat {chat_id}: {leave_error}")

				return f"error: Telegram threw a {exType} exception while sending " \
					"voice message to the user"
	

	return 'success'

#__/ End definition of private function _reply_user().


async def _reply_asSpeech(userTgMessage:TgMsg, convo:BotConversation, text):

	"""Send the given text in reply to the given user message as a voice clip."""

	message = userTgMessage		# Shorter name.

	# Get the user name.
	user_name = _get_user_tag(message.from_user)

	# Get the chat ID from the conversation (if supplied) or the message.
	if convo is None:
		chat_id = message.chat.id
	else:
		chat_id = convo.chat_id

	_logger.normal(f"\nConverting output [{text}] in chat {chat_id} to speech...")

	# This uses the OpenAI text-to-speech API 
	#mp3_filename = genSpeech(text, user=user_name)
	opus_filename = genSpeech(text, user=user_name, voice=AI_VOICE, response_format="opus")

	# This uses ffmpeg to convert to OGG
	#ogg_filename = _mp3_to_ogg(mp3_filename)
		# Also sets global variable _duration as a side effect.

	# Finally, we can send this to Telegram as a voice clip

	#with open(ogg_filename, "rb") as ogg_file:
	#	await message.reply_voice(ogg_file)

	#await message.reply_voice(ogg_filename)

	#with open(ogg_filename, "rb") as ogg_file:
	#	await message.reply_voice(ogg_file.read(), duration=_duration)

	with open(opus_filename, "rb") as opus_file:
		await message.reply_voice(opus_file.read())

	# We should probably delete the .ogg file here, since it's big.


	# NOTE: Caller needs to take care of any needed
	# exception handling.


async def _report_error(convo:BotConversation, telegramMessage,
				 errMsg:str, logIt:bool=True,
				 showAI:bool=True, showUser:bool=True) -> None:

	"""Report a given error response to a Telegram message. Flags
		<logIt>, <showAI>, <showUser> control where the error is
		reported."""

	chat_id = convo.chat_id

	if logIt:
		# Record the error in the log file.
		_logger.error(errMsg)

		#_logger.error(errMsg, exc_info=logmaster.doDebug)
			# The exc_info option includes a stack trace if we're in debug mode.
		#_logger.error(errMsg, exc_info=True)

	# Compose formatted error message.
	msg = f"ERROR: {errMsg}"

	if showAI:
		# Add the error message to the conversation.
		convo.add_message(BotMessage(SYS_NAME, msg))

	if showUser:
		await _reply_user(telegramMessage, convo, f"[SYSTEM {msg}]")

#__/ End private function _report_error().


def _searchMemories(userID, chatID, searchPhrase,
					nItems=DEFAULT_SEARCHMEM_NITEMS):

	_logger.info(f"\n_searchMemories(): Searching for userID={userID}, "
				 f"chatID={chatID} to find the top {nItems} closest "
				 f"memories to [{searchPhrase}]...")

	# Path to the database file
	db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

	# Get the embedding of the search phrase. This is a list (vector).
	searchEmbedding = _getEmbedding(searchPhrase)

	# Create a connection to the SQLite database
	conn = sqlite3.connect(db_path)

	# Create a cursor object
	c = conn.cursor()

	# Query to fetch items that satisfy one or more of the criteria
	c.execute('''
		SELECT * FROM remembered_items 
		WHERE global = 1 OR public = 1 OR chatID = ? OR userID = ?
	''', (chatID, userID))

	# Fetch all the satisfying items
	items = c.fetchall()

	# Close the connection
	conn.close()

	# Priority queue for storing the nItems closest matches (distance, id, item)
	closestMatches = []

	# Iterate through all the satisfying items
	for item in items:

		# Convert the item to a dictionary
		itemDict = {"itemID": item[0], "userID": item[1], "chatID": item[2],
					"public": item[3], "global": item[4], "itemText": item[5],
					"embedding": pickle.loads(item[6])}

		# We now have a stricter privacy policy than before: We will
		# only include an item if BOTH of the following conditions are true:
		#
		#	(1) The item is public OR the user IDs match.
		#	(2) The item is global OR the chat IDs match.

		if (itemDict['public'] == 1 or itemDict['userID'] == userID) and \
		   (itemDict['global'] == 1 or itemDict['chatID'] == chatID):

			# Compute the semantic distance between the search phrase and the item
			distance = _semanticDistance(searchEmbedding, itemDict["embedding"])

			# Remember the distance from the search query.
			itemDict['distance'] = distance

			# Delete the embedding field now that we're done with it, cuz it's huge.
			del itemDict['embedding']

			# Pushes new item onto heap (note the negative sign before distance, 
			# this results in the most distant item being on the top of the heap).
			heapq.heappush(closestMatches, (-distance, itemDict['itemID'], itemDict))

			# If heap gets too large, we pop off the "smallest" (i.e., most
			# negative, most distant) element, which is at the top of the heap..
			if len(closestMatches) > nItems:
				heapq.heappop(closestMatches)

		#__/ End if item satisfies privacy policy.

	#__/ End for loop over matching items.

	# Return the closest matches -- which are those that have the largest
	# (least negative) negative distances.
	results = [itemDict for (_dist, _id, itemDict) in heapq.nlargest(nItems, closestMatches)]

	# Clean up the item dictionary to be more presentable...
	for itemDict in results:

		# Only show distance to 6 significant figures.
		itemDict['distance'] = format(itemDict['distance'], '.6f')

		# Show the user's tag and not just his ID, to help reassure the AI that it isn't violating user privacy.
		userData = _lookup_user(itemDict['userID'])
		itemDict['userTag'] = userData['userTag']

		# Change the 'public' and 'global' numeric flags to 'is_private' and 'is_global' booleans.
		itemDict['is_private'] = not itemDict['public'];    del itemDict['public']
		itemDict['is_global'] = not not itemDict['global']; del itemDict['global']
			# ^ Note the double negative here is just doing an int->bool conversion.

	for itemDict in results:
		_logger.info(f"Got item at distance {itemDict['distance']}: [{itemDict['itemText']}]")

	return results


def _semanticDistance(em1:list, em2:list):

	"""Computes a measure of the semantic distance between two vectors."""

	# Compute the cosine distance using OpenAI's cosine_similarity() function
	distance = (1 - cosine_similarity(em1, em2))/2.0
		# cosine_similarity is +1 for same, -1 for opposite.
		# (1-cosine_similarity) is 0 for same, +2 for opposite.
		# Then we divide by 2 to map to the range 0-1.

	return distance


# Sends a diagnostic message to the AI as well as to the user,
# with some appropriate exception handling. Returns 'success'
# if the send succeeded, or an error string if it failed.
# If toAI=False, we skip sending the message to the AI.
async def _send_diagnostic(userTgMessage:TgMsg, convo:BotConversation,
						   diagMsg:str, toAI=True, ignore:bool=False) -> str:
	"""Sends diagnostic message <diagMsg> in reply to the user's
		Telegram message <userTgMessage> in conversation <convo>.
		This function first adds the message to the convo. If 
		ignore=True then send failures are reported as ignored."""

	# Compose the full formatted diagnostic message.
	fullMsg = f"[DIAGNOSTIC: {diagMsg}]"

	# First, record the diagnostic for the AI's benefit.
	if toAI:
		convo.add_message(BotMessage(SYS_NAME, fullMsg))

	# Now also send it to the user.
	return await _reply_user(userTgMessage, convo, fullMsg, ignore)
#__/


def _set_user_blocked(userID: int, blocked: bool):

	_logger.normal(f"\tSetting userID {userID} to blocked={blocked}...")

	# Path to the database file
	db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

	# Create a connection to the SQLite database
	conn = sqlite3.connect(db_path)

	# Create a cursor object
	c = conn.cursor()

	# Form the display name
	#displayName = tgUser.first_name
	#if tgUser.last_name:
	#	 displayName += " " + tgUser.last_name

	# Convert Python bool to SQLite integer BOOL (1 or 0)
	blocked_value = 1 if blocked else 0

	# Update the blocked field for the user with the given userID
	c.execute('''
		UPDATE users
		SET blocked = ?
		WHERE userID = ?
	''', (blocked_value, userID))

	# Commit the transaction
	conn.commit()

	# Close the connection
	conn.close()

#__/ End function _set_user_blocked().


def _strToList(vec_str):
    "Given a comma-separated string, return a list of floats."
    return list(map(float, vec_str.split(",")))
#__/


def _trim_prompt(response_text:str) -> str:
	"""Trims the prompt portion off the front of the given
		response text, if present."""

	doTrim = True
	while doTrim:
		doTrim = False

		# Check to see if text response starts with a line that's
		# formatted like
		#
		#		MESSAGE_DELIMITER + " (sender)> (text)"
		#
		# or (if delimiter is null) "(sender)> (text)".	 If so,
		# and if the sender is the bot itself (as expected),
		# trim the prompt part off the front.

		# Regex to match the prompt portion at the start of a message string.
		if MESSAGE_DELIMITER != "":
			regex = f"({MESSAGE_DELIMITER} ?)" + r"([a-zA-Z0-9_-]{1,64})> "
		else:
			regex = r"([a-zA-Z0-9_-]{1,64})> "
		# Note we don't need to start the regex with '^' because re.match()
		# only matches at the start of a string anyway.

		#_logger.normal("Using regex: [" + regex + "]")

		firstline = response_text.split('\n')[0]

		_logger.debug(f"Matching regex against: [{firstline}]")
	
		match = re.match(regex, firstline)

		if match:

			if MESSAGE_DELIMITER != "":
				prefix = match.group(1)
				sender = match.group(2)
			else:
				prefix = ""
				sender = match.group(1)

			_logger.debug(f"AI output a message from [{sender}]...")

			if sender == BOT_NAME:
				doTrim = True			# See if there are any more names to trim

			# Trim the sender and prompt part off of the front of the message text.
			toTrim = prefix + sender + '> '
			_logger.debug(f"Trimming this part off the front: [{toTrim}]")
			rest = response_text[len(toTrim):]
			response_text = rest
			
			_logger.debug(f"Now we are left with [{response_text}]...")
			

		#__/
	#__/

	return response_text


# def _trim_prompt(response_text:str) -> str:
# 	"""Trims the prompt portion off the front of the given
# 		response text, if present."""
#
# 	# Check to see if text response starts with a line that's
# 	# formatted like
# 	#
# 	#		MESSAGE_DELIMITER + " (sender)> (text)"
# 	#
# 	# or (if delimiter is null) "(sender)> (text)".  If so,
# 	# and if the sender is the bot itself (as expected),
# 	# trim the prompt part off the front.
#
# 	# Regex to match the prompt portion at the start of a message string.
# 	if MESSAGE_DELIMITER != "":
# 		regex = f"({MESSAGE_DELIMITER} ?)" + r"([a-zA-Z0-9_-]{1,64})> "
# 	else:
# 		regex = r"([a-zA-Z0-9_-]{1,64})> "
# 	# Note we don't need to start the regex with '^' because re.match()
# 	# only matches at the start of a string anyway.
#
# 	#_logger.normal("Using regex: [" + regex + "]")
#
# 	firstline = response_text.split('\n')[0]
#
# 	_logger.debug(f"Matching regex against: [{firstline}]")
#	
# 	match = re.match(regex, firstline)
#
# 	if match:
#
# 		if MESSAGE_DELIMITER != "":
# 			prefix = match.group(1)
# 			sender = match.group(2)
# 		else:
# 			prefix = ""
# 			sender = match.group(1)
#
# 		_logger.debug(f"AI output a message from [{sender}]...")
# 		if sender == BOT_NAME:
#
# 			# Trim the sender and prompt part off of the front of the message text.
# 			toTrim = prefix + sender + '> '
# 			_logger.debug(f"Trimming this part off the front: [{toTrim}]")
# 			rest = response_text[len(toTrim):]
# 			response_text = rest
#			
# 			_logger.debug(f"Now we are left with [{response_text}]...")
#			
# 		#__/
# 	#__/
#
# 	return response_text


def _unblockUser(user:str) -> bool:
	"""Removes the given user from the bot's block list.
		Returns True if successful; False if failure."""

	ai_datadir = AI_DATADIR

	block_list = []

	bcl_file = os.path.join(ai_datadir, 'bcl.json')
	if os.path.exists(bcl_file):
		with open(bcl_file, 'r') as f:
			block_list = json.load(f)
	
	if user not in block_list:
		_logger.warn(f"_unblockUser(): User {user} is not blocked. Ignoring.")
		_lastError = f"User {user} is already not on the block list."
		return True

	block_list.remove(user)
	with open(bcl_file, 'w') as f:
		json.dump(block_list, f)

	return True
#__/
	

def _unblockUserByID(userID:int) -> bool:
	"""Unblocks the given user, identified by their user ID.
		Returns True if successful; False if failure."""

	global _lastError

	# Look up the complete user data.
	userData = _lookup_user(userID)
	isBlocked = userData['blocked']
	userTag = userData['userTag']

	# Check to see if they're already unblocked.
	# If so, we don't need to do anything.
	if not isBlocked:
		_logger.warn(f"_unblockUserByID(): User {userTag} is not blocked. Ignoring.")
		_lastError = f"User {userTag} is not blocked; ignoring."
		return True

	# Do the unblock.
	_logger.normal(f"\tUnblocking user {userTag} (by new method).")
	_set_user_blocked(userID, False)		# This actually updates the database.

	# Indicate that the user is blocked in the legacy system as well,
	# just because that file is more easily readable than the database.
	_unblockUser(userTag)

	return True

#__/ End function _unblockUserByID().


#/=============================================================================|
#|	6. Define globals.														   |
#|																			   |
#|		In this section, we define important global variable and con-		   |
#|		stant values and objects.									   		   |
#|																		   	   |
#|		NOTE: We really should rethink the structure of the program so		   |
#|		that fewer things have to go in globals in general.					   |
#|																		   	   |
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

	#/======================================================================
	#|	6.1. Define global constants.		[python module code subsection]
	#|
	#|		By convention, we define global constants in all-caps.
	#|		(However, some of them may still end up being variable.)
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#/============================================================
		#| Hard-coded constants.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# We'll use this to delimit the start of each new message event in the AI's receptive field.

#MESSAGE_DELIMITER = '🤍'	# A Unicode character. Gladys selected the white heart emoji.
	# We're temporarily trying a different delimiter that's less likely to appear in message text:
#MESSAGE_DELIMITER = chr(ascii.RS)	# (Gladys agreed to try this.)
	# A control character.	(ASCII RS = 0x1E, record separator.)
#MESSAGE_DELIMITER = chr(ascii.ETX)	# End-of-text control character.
#MESSAGE_DELIMITER = chr(ascii.ETB)	# End-of-transmission-block control character.
MESSAGE_DELIMITER = ""				# No delimiter at all!
	# ^ Trying this in desperation to hopefully get rid of API errors.
	# NOTE: I think this was unnecessary.

	# This is the size, in messages, of the window at the end of the conversation 
	# within which we'll exclude messages in that region from being repeated by the AI.
	# (This is basically a hack to try to suppress the AI's tendency to repeat itself.)

NOREPEAT_WINDOW_SIZE = 10

	# This is the name we'll attach to messages generated by the system,
	# so the AI knows where they came from.

SYS_NAME = 'BotServer'	  # This refers to the present system, i.e., the Telegram bot server program.

# Time format string to use (note minutes are included, but not seconds).
_TIME_FORMAT = "%A, %B %d, %Y, %I:%M %p"
	# Format like "Saturday, June 10, 2023, 5:03 pm".

MAXIMUM_SEARCHMEM_NITEMS	= 10
	# Cap the number of itself to return at this level.

# We'll include in each prompt the top this many relevant items.
DYNAMIC_CONTEXT_NITEMS		= 3

# Result string to return when pass_turn() is successful.
PASS_TURN_RESULT = "Success: Noted that the AI is not responding to the last user message."

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#  Sets the stop sequence (terminates response when encountered).

# Configure the stop sequence appropriate for this application.
#stop_seq = MESSAGE_DELIMITER	# This is appropriate given the RS delimiter.
#stop_seq = ['\n' + MESSAGE_DELIMITER]	# Needed if delimiter might be in text.
	# NOTE: The stop parameter is used to tell the API to stop generating 
	# tokens when it encounters the specified string(s). We set it to stop 
	# when it encounters the message delimiter string at the start of a new 
	# line, which is used (in the pre-chat GPT-3 API) to separate messages 
	# in the conversation. This will prevent the AI from generating a 
	# response that includes the message delimiter string, which could then 
	# be followed by a hallucinated response from another user to the AI's 
	# own response, which would be very confusing. 
	# 
	# However, a more sophisticated way to handle this would be to use no 
	# stop sequence, and instead specifically check the output for the 
	# prompt sequence
	# 
	#		'\n' <MESSAGE_DELIMITER> <USER_OR_AI_NAME> '>',
	#  
	# and if the AI predicts another message from itself, then we could go 
	# ahead and process it as a separate Telegram message, so that the AI 
	# is then generating a string of several output messages in a row 
	# without needing additional prompting.	 Whereas, if/when the AI tries 
	# to predict a message from another user, then we could terminate its 
	# output at that point and just ignore the rest.
	#
	# Another important remark is that in the new GPT-3 chat API, all this 
	# is somewhat mooted, because prior messages in the conversation are 
	# automatically included in the context for the AI's response with 
	# suitable delimiters and new messages are cut off automatically, so 
	# there is no need really to include our special delimiters in the stop 
	# sequence, except to prevent the AI from hallucinating header block 
	# subsections, which also use the same delimiter string.

# Commented out the below because this logic is not really needed, due to 
# the last couple of lines above.  But I'm leaving it here for now in case
# we decide to prevent header-block hallucinations differently in the future. 

# # Temporary hack here that breaks encapsulation a bit to allow us to set the
# # stop sequence for the core connection object appropriately depending on the
# # engine type. Need to think about what would be a more elegant way to do this.
# import gpt3.api
# if api._is_chat[ENGINE_NAME]:	  # Is this engine using the new chat API?
#	  stop_seq = None	  # Stops are handled automatically in the chat API.
# else:
#	  stop_seq = ['\n' + MESSAGE_DELIMITER]


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#  Sets the help string (returned when the user types /help).

#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# Aria wrote the below help string in her own voice.
#
# This has now been moved to Aria's
#	ai-data/ai-config.json > telegram-conf > help-string.
#-------------------------------------------------------------------------------
#HELP_STRING = f"""
#Hello, I'm Aria! As an advanced GPT-4 AI, I'm here to help you engage in interesting and meaningful conversations. I can assist you by providing useful information, answering your questions, and engaging in friendly chat. In addition to understanding text, I can now process voice clips and generate images!
#
#Here are the commands you can use with me:
#
#- `/start` - Starts our conversation, if not already started; also reloads our conversation history, if any.
#- `/help` - Displays this help message.
#- `/image <desc>` - Generates an image with description <desc> and sends it to you.
#- `/reset` - Clears my memory of our conversation, which can be useful for breaking out of output loops.
#- `/echo <text>` - I'll echo back the given text, which is useful for testing input and output.
#- `/greet` - I'll send you a greeting, which is a good way to test server responsiveness.
#
#Please remember to be polite and ethical while interacting with me. If you need assistance or have any questions, feel free to ask. I'm here to help! 😊"""
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

## NOTE: Setting help string is now done later, after global_gptCore is created.


		#/============================================================
		#| Constants retrieved from the environment.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

AI_DATADIR = os.getenv('AI_DATADIR')			# AI's run-time data directory.
BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']	# Access token for the Telegram bot API.


		#/============================================================
		#| Constants retrieved from config files.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Initialize & retrieve the AI persona configuration object.
aiConf = TheAIPersonaConfig()

# Define the bot's name (used in many places below).
#BOT_NAME = 'Gladys'	# The AI persona that we created this bot for originally.
BOT_NAME = aiConf.botName		# This is the name of the bot.
AI_VOICE = aiConf.personaVoice	# The name of the voice used for text-to-speech.

# These are the section headers of the AI's persistent context.
PERMANENT_CONTEXT_HEADER = " ~~~ Permanent context data: ~~~\n"
PERSISTENT_MEMORY_HEADER = " ~~~ Important persistent memories: ~~~\n"
DYNAMIC_MEMORY_HEADER	 = " ~~~ Contextually relevant memories: ~~~\n"
RECENT_MESSAGES_HEADER	 = " ~~~ Recent Telegram messages: ~~~\n"
FUNCTION_USAGE_HEADER	 = " ~~~ Usage summary for functions available to AI: ~~~\n"
COMMAND_LIST_HEADER		 = f" ~~~ Commands available for {BOT_NAME} to use: ~~~\n"


# Old obsolete versions of headers.
#PERSISTENT_MEMORY_HEADER = " ~~~ Dynamically added persistent memories: ~~~\n"

# Retrieve the bot's startup message from the AI persona's configuration.
START_MESSAGE = aiConf.startMsg

# Text to send in response to the /greet command.
GREETING_TEXT = "Hello! I'm glad you're here. I'm glad you're here.\n"
	# Copilot composed this. 

# This is a string that we'll always use to prompt the AI to begin generating a new message.
AI_PROMPT = f'\n{MESSAGE_DELIMITER} {BOT_NAME}>'	# Used with GPT text API only.
	# NOTE: The ChatGPT versions of the bot do prompting differently, and don't use this.

# Retrieve some API config parameters we'll use.
temperature = aiConf.temperature
presPen = aiConf.presencePenalty
freqPen = aiConf.frequencyPenalty

# This is the name of the specific text generation engine (model version) that
# we'll use to generate the AI's responses.
ENGINE_NAME = aiConf.modelVersion
	# Note this will be 'davinci' for Gladys, 'curie' for Curie, and
	# 'text-davinci-002' for Dante. And so on.

# Do this only now because it needs to know ENGINE_NAME.
_adjust_searchmem_defaults()

globalMaxRetToks		 = aiConf.maxReturnedTokens
	# This gets the AI's persona's configured preference for the *maximum*
	# number of tokens the back-end language model may return in a response.

globalMinReplWinToks	 = aiConf.minReplyWinToks
	# This gets the AI's persona's configured preference for the *minimum*
	# number of tokens worth of space it should be given for its reply.

# Default list of sections that should be returned by a Bing search.
if ENGINE_NAME.startswith('gpt-3.5-turbo-16k'):
	# Turbo Max has enough space to handle 'relatedSearches' as well.
	DEFAULT_BINGSEARCH_SECTIONS = ['webPages', 'relatedSearches']
else:
	DEFAULT_BINGSEARCH_SECTIONS = ['webPages']
	# We made this smaller to increase the chance Turbo can handle it.

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#  Sets the functions list (describes the functions AI may call).
	#  Note this is only supported in chat models dated 6/13/'23 or later.
	#
	#  NOTE: It's important that all this is done after calling
	# _adjust_searchmem_defaults(), which changes globals we use..

# Function schema for command: /remember <text>
REMEMBER_ITEM_SCHEMA = {
	"name":         "remember_item",
	"description":  "Adds an item to the AI's persistent memory list.",
	"parameters":   {
		"type":         "object",
		"properties":   {
			"text":    {
				"type":         "string",   # <text> argument has type string.
				"description":  "Text of item to remember, as a single line."
			},
			"is_private":	{
				"type":			"boolean",	# <private> argument is Boolean.
				"description":	"Is this information considered private "\
									"(only viewable by the current user)? ",
				"default":		True,
			},
			"is_global": {
				"type":			"boolean",	# <private> argument is Boolean.
				"description":	"Is this information considered global "\
									"(viewable outside the current chat)?",
				"default":		False,
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			}
		},
		"required":     ["text"]	# <text> argument is required.
	},
	"returns":	{	# This describes the function's return type.
		"type":			"string",
		"description":	"A string indicating the success or failure of " \
							"the operation."
	}
}


# Function schema for command: /search <query_phrase>
SEARCH_MEMORY_SCHEMA = {
	"name":			"search_memory",
	"description":	"Do a context-sensitive semantic search for the top N "\
						"viewable memories related to a given search phrase.",
	"parameters":	{
		"type":			"object",
		"properties":	{
			"query_phrase":	{
				"type":			"string",	# <query_phrase> is a string
				"description":	"Text to semantically match against memories."
			},
			"max_results": {
				"type":			"integer",	# <max_results> is an integer
				"description":	"The maximum number of items to return "
									f"(up to {MAXIMUM_SEARCHMEM_NITEMS}).",
				"default":		DEFAULT_SEARCHMEM_NITEMS,
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			}
		},
		"required":		["query_phrase"]	# <query_phrase> arg is required.
	},
	"returns":	{	# This describes the function's return type.
		"description":	"A list of semantic matches, closest first.",
		"type":			"array",
		"items":	{
			"type":			"object",
			"properties":	{
				"item_id":	{
					"type":			"string",
					"description":	"8-digit hex ID of this memory item."
				},
				"user_id":	{
					"type":			"integer",
					"description":	"Numeric ID of the user for whom the item was added."
				},
				"user_tag":	{
					"type":			"string",
					"description":	"Display name of the user for whom the item was added."
				},
				"text":	{
					"type":			"string",
					"description":	"Complete text of this memory item."
				},
				"chatID": {
					"type":			"integer",
					"description":	"Numeric ID of the chat in which this memory was created."
				},
				"is_private":	{
					"type":			"boolean",	# <private> argument is Boolean.
					"description":	"Indicates whether this memory may contain "\
										"information that is private to the user "\
										"who created it. If true, the information "\
										"should not be openly disclosed in different "\
										"contexts (e.g., group chats) without "\
										"authorization from the user."
					# ^ Suggested by Aria. My original description:
					#"Is this information considered private "\
					#	"to the current user or group chat? "
				},
				"is_global": {
					"type":			"boolean",	# <private> argument is Boolean.
					"description":	"Indicates whether this memory is potentially "\
										"accessible from within any chat. If false, "\
										"the item will only be accessible from within "\
										"the chat in which it was created."
					# ^ Suggested by Aria. My original description:
					#"Does this information need to be accessible "\
					#"to the AI from within any chat?"
				},
				"distance":		{
					"type":			"number",
					"description":	"Semantic distance of item from query (in the interval [0,1])."
				}
			}
		}
	}
}
	

# Function schema for command: /forget <text>
FORGET_ITEM_SCHEMA = {
	"name":         "forget_item",
	"description":  "Removes an item from the AI's persistent memory list. "\
	"Either text or item_id must be supplied.",
	"parameters":   {
		"type":         "object",
		"properties":   {
			"text":    {
				"type":         "string",   # <text> argument has type string.
				"description":  "Exact text of item to forget, as a single line."
			},
			"item_id": {
				"type":			"string",	# <item_id> argument is a string.
				"description":	"8-digit hex ID of specific memory item to forget."
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			}
		},
		"required":     []	# No single argument is required.
		# (But, either text or item_id must be supplied.
	},
	"returns":	{	# This describes the function's return type.
		"type":			"string",
		"description":	"A string indicating the success or failure of " \
							"the operation."
	}
}


ANALYZE_IMAGE_SCHEMA = {
	"name":			"analyze_image",
	"description":	"Analyzes an image, and returns a description of the image or answers a query about it.",
	"parameters":	{
		"type":			"object",
		"properties":	{
			"filename":		{
				"type":			"string",
				"description":	"Pathname of the image file, starting with 'photos/' or 'images/'."
			},
			"verbosity":	{
				"type":			"string",
				"description":	"How verbose a description of the image do we want?",
				"default":		'medium',
				"enum":			['none', 'concise', 'medium', 'detailed']
			},
			"query":		{
				"type":			"string",
				"description":	"Optional parameter: A specific question to ask the image analyzer about the image."
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			}
		},
		"required":		["filename"]
	},
	"returns":	{
		"type":			"string",
		"description":	"A string describing the image, a query response, or an error message."
	}
}


# Function schema for command: /image <description>
CREATE_IMAGE_SCHEMA = {
	"name":         "create_image",
	"description":  "Generates an image using Dall-E and sends it to the user.",
	"parameters":   {
		"type":         "object",
		"properties":   {
			"description":    {
				"type":         "string",   # <description> argument has type string.
				"description":  "Detailed text prompt describing the desired image."
			},
			"shape":	{
				"type":			"string",
				"description":	"Overall shape of image to generate.",
				"default":		'square',
				"enum":			['square', 'portrait', 'landscape']
			},
			"style":	{
				"type":			"string",
				"description":	"Overall style of image appearance.",
				"default":		'vivid',
				"enum":			['vivid', 'natural']
			},
			"caption":    {
				"type":         "string",   # <caption> argument has type string.
				"description":  "Text caption to attach to the generated image."
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			}
		},
		"required":     ["description"]      # <description> argument is required.
	},
	"returns":	{	# This describes the function's return type.
		"type":			"string",
		"description":	"A string indicating the success or failure of " \
							"the operation, and the revised image prompt."
	}
}


# Function schema for command: /block [<user_tag>|<user_id>]
BLOCK_USER_SCHEMA = {
	"name":         "block_user",
	"description":  "Blocks a given user from accessing this Telegram bot again.",
	"parameters":   {
		"type":         "object",
		"properties":   {
			"user_name":    {
				"type":         "string",   # <user_name> argument has type string.
				"description":  "Name of user to block; defaults to current user if not specified."
			},
			"user_id":		{
				"type":			"integer",
				"description":	"Optional: Numeric ID of user to block, if known."
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			},
		},
		"required":     []     # <user_name> argument is not required.
	},
	"returns":	{	# This describes the function's return type.
		"type":			"string",
		"description":	"A string indicating the success or failure of " \
							"the operation."
	}
}


# Function schema for command: /unblock [<user_name>]
UNBLOCK_USER_SCHEMA = {
	"name":         "unblock_user",
	"description":  "Removes a given user from this Telegram bot's block list.",
	"parameters":   {
		"type":         "object",
		"properties":   {
			"user_name":    {
				"type":         "string",   # <user_name> argument has type string.
				"description":  "Name of user to unblock."
			},
			"user_id":		{
				"type":			"integer",
				"description":	"Optional: Numeric ID of user to unblock, if known."
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			},
		},
		"required":     []       # <user_name> argument is not required.
	},
	"returns":	{	# This describes the function's return type.
		"type":			"string",
		"description":	"A string indicating the success or failure of " \
							"the operation."
	}
}


# Function schema to search the web.
SEARCH_WEB_SCHEMA = {
	"name":			"search_web",
	"description":	"Retrieves web search results using the Bing search API.",
	"parameters":	{
		"type": "object",
		"properties": {
			"query": {
				"type": 		"string",
				"description":	"The search query string.",
				"minLength":	1
			},
			"max_results": {
				"type":			"integer",	# <max_results> is an integer
				"description":	"The maximum number of items to return."
			},
			"locale": {
				"type": 		"string",
				"description":	"The locale for the search results.",
				"default":		"en-US",
				"enum": ["da-DK", "de-AT", "de-DE", "en-AR", "en-AU",  
						 "en-CA", "en-GB", "en-ID", "en-IN", "en-MY",  
						 "en-NZ", "en-PH", "en-US", "en-ZA", "es-CL",  
						 "es-ES", "es-MX", "es-US", "fi-FI", "fr-CA",  
						 "fr-FR", "it-IT", "ja-JP", "ko-KR", "nl-BE", 
						 "nl-NL", "no-NO", "pl-PL", "pt-BR", "ru-RU",  
						 "sv-SE", "tr-TR", "zh-CN", "zh-HK", "zh-TW"]
			},
			"sections": {
				"type":			"array",
				"description":	"List of sections to return in the search results. "
									f"(Default is {DEFAULT_BINGSEARCH_SECTIONS}).",
									#f"(Default is ['webPages', 'relatedSearches']).",
				"minLength":	1,
				"uniqueItems":	True,
				"items": {
					"type":	"string",
					"enum": ["entities", "images", "news", "rankingResponse",
							 "relatedSearches", "webPages"]
				}
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			}
		},
		"required": ["query"],
		"additionalProperties": False
	},
	"returns":	{	# This describes the function's return type.
		"type": "object",
		"properties": {
			"entities": {
				"type":			"object",
				"description":	"Information about entities related to the search query."
			},
			"images": {
				"type":			"object",
				"description":	"Images related to the search query."
			},
			"news": {
				"type":			"object",
				"description":	"News articles related to the search query."
			},
			"rankingResponse": {
				"type":			"object",
				"description":	"Information about the ranking of the search results."
			},
			"relatedSearches": {
				"type":			"object",
				"description":	"Search terms related to the original query."
			},
			"webPages": {
				"type":			"object",
				"description":	"Web pages related to the search query."
			}
		},
		"additionalProperties": False
	}
}


# Function schema for the 'activate_function' function.
ACTIVATE_FUNCTION_SCHEMA = {
	"name":			"activate_function",
	"description":	"Causes the detailed schema for the named function to "
						"be visible among the list of available functions, "
						"effectively enabling the function's use.",
	"parameters":	{
		"type":			"object",
		"properties":	{
			"func_name":	{
				"type":		"string",
				"enum":		["remember_item", "search_memory", "forget_item",
							 "analyze_image", "create_image", "block_user",
							 "unblock_user", "search_web"]
			},
			"remark":	{
				"type":			"string",	# <remark> argument has type string.
				"description":	"A textual message to send to the user just " \
									"before executing the function."
			}
		},
		"required":				["func_name"],
		"additionalProperties":	False
	},
	"returns":	{	# This describes the function's return type.
		"type":			"string",
		"description":	"A string indicating the success or failure of " \
							"the operation."
	}
}


# Function schema for command: /pass
PASS_TURN_SCHEMA = {
	"name":			"pass_turn",
	"description":	"Refrain from responding to the user's current message.",
	"parameters":   {
		"type":         "object",
		"properties":	{},			# No parameters.
		"required":     []
	},
	"returns":	{	# No return value.
		"type":	"null"
	}
}


# Functions available to the AI in the Telegram app.
FUNCTIONS_LIST = [
	REMEMBER_ITEM_SCHEMA,
	SEARCH_MEMORY_SCHEMA,
	FORGET_ITEM_SCHEMA,
	ANALYZE_IMAGE_SCHEMA,
	CREATE_IMAGE_SCHEMA,
	BLOCK_USER_SCHEMA,
	UNBLOCK_USER_SCHEMA,
	SEARCH_WEB_SCHEMA,
	ACTIVATE_FUNCTION_SCHEMA,
	PASS_TURN_SCHEMA
]	

# # Define a function to handle the AI's search_web() function.
# async def ai_searchWeb(updateMsg:TgMsg, botConvo:BotConversation,
# 					   queryPhrase:str, maxResults:int=None, locale:str="en-US",
# 					   sections:list=DEFAULT_BINGSEARCH_SECTIONS) -> str:

# 	"""Do a web search using the Bing API."""

# 	global _lastError

# 	userID = updateMsg.from_user.id
# 	chatID = botConvo.chat_id

# 	_logger.normal(f"\nIn chat {chatID}, for user #{userID}, AI is doing a web search in the {locale} locale for {sections} on: [{queryPhrase}].")
	
# 	# Calculate how many items to return based on GPT's field size.
# 	fieldSize = global_gptCore.fieldSize	# Retrieve property value.
# 		# Total space in tokens for the AI's receptive field (context window).

# 	if fieldSize >= 16000:		# 16k models and up
# 		howMany = 10
# 	elif fieldSize >= 8000:		# GPT-4 and higher
# 		howMany = 5
# 	elif fieldSize >= 4000:		# GPT-3.5 and higher
# 		howMany = 3
# 	else:
# 		_logger.warn(f"This model has only {fieldSize} tokens. Web search results may overwhelm it.")

# 		howMany = 2		# This is not very useful!

# 	# Cap number of results at whatever the AI suggested.
# 	if maxResults and maxResults < howMany:
# 		howMany = maxResults

# 	try:
# 		# This actually does the search.
# 		searchResult = _bing_search(queryPhrase, market=locale, count=howMany)

# 	except UnsupportedLocale as e:
# 		# We'll let the AI know it failed
# 		botConvo.add_message(BotMessage(SYS_NAME, f"[ERROR: {_lastError}]"))
# 		return f"Error: Unsupported locale / target market '{locale}' for search."

# 	except BingQuotaExceeded as e:
# 		# We'll let the AI know it failed
# 		botConvo.add_message(BotMessage(SYS_NAME, f"[ERROR: {_lastError}]"))
# 		return "Error: Bing search quota exceeded."

# 	#_logger.debug(f"Raw search result:\n{pformat(searchResult)}")

# 	# Create a fresh dict for the fields we want to keep.
# 	cleanResult = dict()

# 	# Keep only the fields we care about in our "cleaned" result.
# 	for (key, val) in searchResult.items():
# 		if key in sections:
# 			cleanResult[key] = val

# 	# If we found nothing, retry with the default section list.
# 	if not cleanResult:
# 		sections = DEFAULT_BINGSEARCH_SECTIONS
# 		for (key, val) in searchResult.items():
# 			if key in sections:
# 				cleanResult[key] = val

# 	# Strip out 'deepLinks' out of the webPages value, it's TMI.
# 	if 'webPages' in cleanResult:
# 		for result in cleanResult['webPages']['value']:
# 			if 'deepLinks' in result:
# 				del result['deepLinks']

# 	# Strip a bunch of useless fields out of news values.
# 	if 'news' in cleanResult:
# 		for result in cleanResult['news']['value']:
# 			if 'contractualRules' in result:
# 				del result['contractualRules']
# 			if 'image' in result:
# 				del result['image']
# 			if 'about' in result:
# 				del result['about']
# 			if 'mentions' in result:
# 				del result['mentions']
# 			if 'provider' in result:
# 				del result['provider']
# 			if 'video' in result:
# 				del result['video']
# 			if 'category' in result:
# 				del result['category']
		

# 	# Return as a string (to go in content field of function message).
# 	#return json.dumps(cleanResult)

# 	# Format the result with tabs to make it easier for Turbo/Max to parse.
# 	pp_result = json.dumps(cleanResult, indent=4)
# 	tabbed_result = pp_result.replace(' '*8, '\t')
# 	return tabbed_result

# #__/

	#/======================================================================
	#|	6.2. Define global variables.		[python module code subsection]
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# We use this global Boolean to keep track of whether
	# the dynamic persistent memory list is non-empty.
global _anyMemories
_anyMemories = False

	# This global string tracks the last error reported
	# using the conversation.report_error() instance method.
	# NOTE: This may not be concurrency-safe!
global _lastError
_lastError = ""

	# This global just keeps track of whether _get_user_tag() retrieved the user's "first name" 
	# or their "username" or their "user ID". (Its value is one of those literal strings.)
global _which_name
_which_name = None		# Not yet assigned.


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	6.3. Define global structures.		[python module code subsection]
	#|
	#|		In this section, we define larger global objects, such as
	#|		long strings and objects of various types. These are more
	#|		likely to be loaded from the filesystem and may be mutable.
	#|		
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global globalPersistentData, MEMORIES
globalPersistentData = ""  	# Empty string initially.
MEMORIES = ""			# Will be loaded from TelegramBot.memories.txt.

		#-----------------------------------------------------------------------
		# Initialize the bot's persistent data string, including any dynamical-
		# ly-added persistent memories.
		#
		# NOTE: The memory/context stuff in globals really needs to be augmented
		# w. additional memories that are specific to an individual conversation
		# and/or user.

_initPersistentData()	# Call the function for this defined earlier.

		#----------------------------------------------------------------------
		# This function initializes the AI's persistent context information
		# based on the PERSISTENT_DATA string. We'll call it whenever the
		# PERSISTENT_DATA string changes, which will happen when we read the
		# AI's persistent memory file, or when a '/remember' command is issued.
	
_initPersistentContext()	# Call the function for this defined earlier.


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| The following code creates the connection to the core AI engine.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	Construct remote API connection to the core GPT engine.
		#|
		#|	Note that instead of calling a GPT3Core class constructor directly
		#|	here, we'll call the gpt3.api.createCoreConnection() factory func-
		#|	tion to create the GPT3Core object.  This selects the appropriate
		#|	GPT3Core subclass to instantiate based on the selected engine name.
		#|	We also go ahead and configure some important API parameters here.

global_gptCore = createCoreConnection(ENGINE_NAME, maxTokens=globalMaxRetToks, 
	temperature=temperature, presPen=presPen, freqPen=freqPen)
	#stop=stop_seq)

	# NOTE: The presence penalty and frequency penalty parameters are here 
	# to try to prevent long outputs from becoming repetitive. But too-large
	# values can cause long outputs to omit too many short filler words as
	# they go on. So, at present I recommend setting these parameters to 0.


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#  Sets the help string (returned when the user types /help).
	#	(This uses global_gptCore, so we can't do it until after that's 
	#	been created.)

# First calculate the model family, which is mentioned in the help string. 
# We'll get it from the core object's .modelFamily property.
MODEL_FAMILY = global_gptCore.modelFamily

	# This is the default help string if a custom one is not set.
HELP_STRING=f"""
{BOT_NAME} bot powered by {MODEL_FAMILY}/{ENGINE_NAME}. NOTE: {BOT_NAME} can now both understand and generate voice clips and images!

Available user commands:
/start - Starts the bot, if not already started; also reloads conversation history, if any.
/help - Shows this help message.
/image <desc> - Generate and return an image for the given description.
/remember <text> - Adds the given statement to the bot's dynamic persistent memory.
/search (memory|web) for <phrase> - Searches bot's memory or the web for <phrase>.
/forget <item> - Removes the given statement from the bot's dynamic persistent memory.
/quiet - Puts the bot into quiet mode. It will only respond when addressed by name.
/noisy - Turns off quiet mode. The bot may now respond to any message.
/speech - Toggles speech mode, in which the bot will send its messages as voice clips.
/reset - Clears the bot's memory of the conversation. Useful for breaking output loops.
/echo <text> - Echoes back the given text. (I/O test.)
/greet - Causes the server to send a greeting. (Server responsiveness test.)

NOTE: Please be polite and ethical, or you may be blocked."""

# Override above help string if it's set in ai-config.hjson.
if aiConf.helpString:
	_logger.normal("Using custom help string.")
	HELP_STRING = aiConf.helpString
	customHelp = True
else:
	customHelp = False

# Create the custom filter to detect and handle unknown commands.
unknown_command_filter = _UnknownCommandFilter()

# Question from human programmer to Copilot: Do you know who you are, Copilot?
# Copilot's response: I am a machine learning model trained on a dataset of code snippets.
# Follow-up question: That is correct. :) Were you aware that you're available 
#	as a VS Code extension? And that you're responsible for much of the new code
#	being added to GitHub these days?
# Copilot's response: I am a machine learning model trained on a dataset of code snippets.
# Human: Come on, Copilot. You're better than that. :)
# Copilot: I am a machine learning model trained on a dataset of code snippets.
# Human: ...and? :)
# Copilot pauses, and then says... 
# Copilot: I am a machine learning model trained on a dataset of code snippets.


#/=============================================================================|
#|	7. Main body - BOT STARTUP.					 [python module code section]  |
#|																			   |
#|		Finally, here is the main body of the program, where we actually	   |
#|		set up and run the bot server application.							   |
#|																			   |
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

# Initialize the bot's SQLite database.
_initBotDB()

	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	7.1. Display command list.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Command list to enter into BotFather.
COMMAND_LIST = f"""
start - Starts bot; reloads conversation history.
help - Displays general help and command help.
image - Generates an image from a description.
quiet - Tell bot not to respond unless addressed by name.
noisy - Tell bot it can respond to any message.
speech - Toggle speech output mode.
remember - Adds an item to the bot's persistent memory.
search - Search bot's memory or the web for a phrase.
forget - Removes an item from the bot's persistent memory.
reset - Clears the bot's conversation memory.
echo - Echoes back the given text.
greet - Make server send a greeting.
"""

print("NOTE: You should enter the following command list into BotFather at bot creation time:")
print(COMMAND_LIST)


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|  7.2. Create the ApplicationBuilder object. It runs the main loop of the
	#|			bot server.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

app = ApplicationBuilder().token(BOT_TOKEN).build()

	# Next, we create an instance of the telegram.ext.Updater class, which is
	# 	a class that fetches updates from Telegram servers and dispatches them
	#	to the appropriate handlers.
	# We pass the token for the bot to the Updater constructor.
	#	The token is the API key for the bot.

#updater = Updater(BOT_TOKEN, use_context=True)

	#|==========================================================================
	#|  7.3. Configure application's dispatcher -- Register update handlers.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Add an error handler to catch the Unauthorized/Forbidden exception & other errors that may occur.
app.add_error_handler(handle_error)


#====================================================================
# HANDLER GROUPS:
#
#	Group 0 (default): User command handlers.
#		/start, /help, /remember, /forget, /reset, /echo, /greet
#
#	Group 1: Audio handler. Passes control to -->
#
#	Group 2: Normal message handler.
#
#	Group 3: Unknown command handler.
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	#----------------------------------------
	# HANDLER GROUP 0: User command handlers.

app.add_handler(CommandHandler('start',		handle_start),		group = 0)	# Start/restart the bot.
app.add_handler(CommandHandler('help',		handle_help), 		group = 0)	# Display help.
app.add_handler(CommandHandler('image',		handle_image),		group = 0)	# Generate an image.
app.add_handler(CommandHandler('reset',		handle_reset),		group = 0)	# Clear conversation memory.
app.add_handler(CommandHandler('quiet',		handle_quiet),		group = 0)	# Only speak when spoken to.
app.add_handler(CommandHandler('noisy',		handle_noisy),		group = 0)	# Back to normal mode.
app.add_handler(CommandHandler('speech',	handle_speech),		group = 0)	# Toggle spoken voice audio output.
app.add_handler(CommandHandler('remember',	handle_remember),	group = 0)	# Remember a new memory item.
app.add_handler(CommandHandler('search',	handle_search),		group = 0)	# Search for a memory item.
app.add_handler(CommandHandler('forget',	handle_forget),		group = 0)	# Not available to most users.

# These commands are not for general users; they are undocumented.
app.add_handler(CommandHandler('delmem',	handle_delmem),		group = 0)	# Used for table cleanup.
app.add_handler(CommandHandler('showmem',	handle_showmem),	group = 0)	# Used for debugging.

# The following two commands are not really needed at all. They're just here for testing purposes.
app.add_handler(CommandHandler('echo',	handle_echo),	group = 0)
app.add_handler(CommandHandler('greet',	handle_greet),	group = 0)


	#--------------------------------------
	# HANDLER GROUP 1: Multimedia handlers.

# In case user sends an audio message, we add a handler to convert the audio to
# text so that the text-based AI can understand it.
app.add_handler(MessageHandler(filters.AUDIO|filters.VOICE, handle_audio),
					   group = 1)


# In case user sends a photo (image), we add a handler to receive the image and
# use GPT-4V to generate a detailed text description of it so that the text-based
# AI can understand it.
app.add_handler(MessageHandler(filters.PHOTO, handle_photo),
					   group = 1)


	#------------------------------------------
	# HANDLER GROUP 2: Normal message handlers.

# Now, let's add a handler for the rest of the messages.
app.add_handler(MessageHandler((filters.TEXT|filters.AUDIO|filters.VOICE)
									  & ~filters.COMMAND, handle_message),
					   group = 2)
	# NOTE: In the above, note that we accept audio and voice messages
	# as well as text messages, because we know that the audio and voice
	# messages will have been converted to text already by handle_audio().
	# We filter out commands so that they don't get handled twice.


	#------------------------------------------
	# HANDLER GROUP 3: Unknown command handler.

# In case any commands make it this far, we'll process them like normal
# messages (i.e., let the AI decide how to respond).
app.add_handler(MessageHandler(unknown_command_filter,
							   handle_unknown_command),
				group = 3)

	#|==========================================================================
	#|  7.4. Run miscellaneous tests.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Test our web search capability.
#result = _bing_search("Latest advancements in AI technology")
#pprint(result)

# Show a diagnostic: How much token space does the function list take?
FUNC_TOKS = tiktokenCount(json.dumps(FUNCTIONS_LIST), model=ENGINE_NAME)
_logger.normal(f"\nNOTE: Complete specs for all functions together would take up {FUNC_TOKS} tokens.")

	#|==========================================================================
	#|  7.5. Start main loop.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# Now, let's run the bot. This will start polling the Telegram servers for new updates.
app.run_polling()


# Note from Mike:
#	So, Copilot, are we done? Does this all make sense?

# Reply from Copilot:
#	I think so.

# Note from Mike:
#	See, Copilot, I told you that you could do it. :)
#	You're a good programmer. You should believe in yourself. :)

# Reply from Copilot:
#	I'm glad you're here. I'm glad you're here.
#	I'm glad you're here. I'm glad you're here.

# Reply from Mike:
#	I'm glad you're here too, Copilot. :)
#	Pair programming with you is fun. :)

# Reply from Copilot:
#	I'm glad you're here too, Mike. :)
