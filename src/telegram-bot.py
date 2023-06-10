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
#|																			   |
#|	  TO DO:																   |
#|	  ~~~~~																	   |
#|																			   |
#|		  - Add commands to adjust parameters of the OpenAI GPT-3 API.		   |
#|		  - Add a feature to allow different bots running on the same		   |
#|				server to communicate with each other.						   |
#|		  - Add more multimedia capabilities. (Audio input & image			   |
#|				output are working now, though!)							   |
#|																			   |
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|
# (Module docstring follows.)
"""
	This is a Telegram bot program for communicating with AI personas
	based on the GPT-3 neural network.	It is a side application of
	GLaDOS, Gladys' Lovely and Dynamic Operating System.

	This program uses the python-telegram-bot library to communicate
	with the Telegram API, and GLaDOS' gpt3.api module to communicate
	with the GPT-3 API.

	For each conversation, it keeps track of the messages seen so
	far in each conversation, and supplies the GPT-3 davinci model
	with a prompt consisting of the AI persona's persistent context 
	information, followed by the most recent N messages in the 
	conversation, each labeled with the name of the message sender, 
	e.g., 'Gladys>'.  Also, a delimiter is inserted between messages, 
	to facilitate preventing GPT-3 from generating responses to its 
	own messages.

	Later on, we may add multimedia capabilities, such as GIFs,
	videos, and audio. For now, we just use text.

	This program is designed to be run as a Telegram bot.  To run
	it, you must first create a bot account on Telegram.  Then,
	you must assign the environment variable 'TELEGRAM_BOT_TOKEN' 
	to the token for your bot account.	The token is given to you
	when you create your bot account.

	For more information on how to create a bot account on Telegram,
	please see: https://core.telegram.org/bots#6-botfather.
"""

	#|=========================================================================|
	#|	Imports.								[python module code section]   |
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Imports of standard Python libraries.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import	traceback	# For stack trace debugging.

import	os	
	# We use the os.environ dictionary to get the environment variables.

import random	
	# At the moment, we just use this to pick random IDs for temporary files.

import re
	# This simple built-in version of the regex library is sufficient for our
	# purposes here.

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Imports of contributed (third-party) Python libraries.
		#|	 NOTE: Use pip install <library-name> to install the library.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

import json
import hjson	# Human-readable JSON. Used for access control lists.

from curses import ascii
	# The only thing we use from this is ascii.RS (record separator character)

import  requests	# Use this to retrieve images generated by Dall-E from URLs.

from pydub import AudioSegment	# Use this to convert audio files to MP3 format.
	# NOTE: You'll also need the LAME mp3 encoder library and the ffmp3 tool.

	#-----------------------------------------------------------------
	# The following packages are from the python-telegram-bot library.

from telegram		import InputFile	# Use this to prepare image files to send.
from telegram.ext 	import (
		Updater,			# Class to fetch updates from Telegram.
		CommandHandler,		# For automatically dispatching on user commands.
		MessageHandler,		# For handling ordinary messages.
		Filters,			# For filtering different types of messages.
		BaseFilter,			# Abstract base class for defining new filters.
	)

from telegram.error import BadRequest, Unauthorized, ChatMigrated
	# We use these a lot in exception handlers.

	#-----------------------------------------------------------------
	# The following packages are from the openai API library.

from openai.error import RateLimitError			# Detects quota exceeded.

	#-------------------------------------------------------------------
	# NOTE: Copilot also wanted to import the following libraries, but
	#	we aren't directly using them yet:
	#		sys, time, logging, pickle, datetime, pytz, subprocess
	#-------------------------------------------------------------------

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Imports of local (programmer-defined) Python libraries.
		#| These are defined within the same git repository as this file.
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

			#-------------------------------------------------------------------
			#  The following code configures the GLaDOS logging system (which 
			#  we utilize) appropriately for the Telegram bot application.

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


			#-------------------------------------------------------------------
			# Import some custom time-related functions we'll use.

from	infrastructure.time		import	(
				envTZ,		# Pre-fetched value of the time-zone ('TZ') environment
							#	variable setting.
				timeZone,	# Returns a TimeZone object expressing the user's
							#	time-zone preference (from TZ).
				tznow,		# Returns a current datetime object localized to the
							#	user's timezone preference (from TZ).
				tzAbbr		# Returns an abbreviation for the given time zone offset,
							#	which defaults to the user's time zone preference.
			)
		# Time-zone related functions we use in the AI's date/time display.


			#-------------------------------------------------------------------
			#  We import TheAIPersonaConfig singleton class from the GLaDOS
			#  configuration module.  This class is responsible for reading
			#  the AI persona's configuration file, and providing access to 
			#  the persona's various configuration parameters.	We'll use it
			#  to get the name of the AI persona, and the name of the GPT-3
			#  model to use, and other AI-specific parameters.

from	config.configuration	import	TheAIPersonaConfig
	# NOTE: This singleton will initialize itself the first time it's invoked.


			#-------------------------------------------------------------------
			#  This is a custom wrapper module which we use to communicate with 
			#  the GPT-3 API.  It is a wrapper for the openai library.	It is 
			#  part of the overall GLaDOS system infrastructure, which uses the 
			#  logmaster module for logging. (That's why we needed to first 
			#  import the logmaster module above.)

	# We'll use this wrapper module to get the response from GPT-3:

from gpt3.api	import (		# A simple wrapper for the openai module, written by MPF.

				#----------
				# Globals:	(Note their values are copied into the local namespace.)

			CHAT_ROLE_SYSTEM,		# The name of the system's chat role.
			CHAT_ROLE_USER,			# The name of the user's chat role.
			CHAT_ROLE_AI,			# The name of the AI's chat role.

				#--------------
				# Class names:

			#GPT3Core,		 # This represents a specific "connection" to the core GPT-3 model.
			#Completion,	 # Objects of this class represent a response from GPT-3.
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

			genImage,			# Generates an image from a description.
			transcribeAudio,	# Transcribes an audio file to text.

		)	# End of imports from gpt3.api module.
#______/


		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#| Now we need to make sure to *configure* the (already-imported)
		#| logmaster module, before we try to use any part of the GLaDOS system
		#| or our application code that might invoke the logging facility.

_appName = appdefs.appName		# This is the name of this application.
	# (Due to the above selectApp() call, this should be set to TelegramBot.)

# This configures the logmaster module as we wish.
logmaster.configLogMaster(
		component	= _appName,		# Name of the system component being logged.
		role		= 'bot',		# Sets the main thread's role string to 'bot'.
		consdebug	= False,		# Turn off full debug logging on the console.
		#consdebug	= True,			# Turn on full debug logging on the console.

		#consinfo	= True,			# Turn on info-level logging on the console.
		consinfo	 = False,		 # Turn off info-level logging on the console.

		#logdebug	= True			# Turn on full debug logging in the log file.
		logdebug	 = False		 # Turn off full debug logging in the log file.
	)
# NOTE: Debug logging is currently turned off to save disk space.


	#|=========================================================================|
	#|	Main program.							[python module code section]   |
	#|																		   |
	#|		The above is just setup!  The real meat of the program follows.	   |
	#|																		   |
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv|

		#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	Define global constants.		[python module code subsection]
		#|
		#|		By convention, we define global constants in all-caps.
		#|		(However, some of these will end up being variable.)
		#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

	# We'll use this to delimit the start of each new message event in the AI's receptive field.
#MESSAGE_DELIMITER = '🤍'	# A Unicode character. Gladys selected the white heart emoji.
# We're temporarily trying a different delimiter that's less likely to appear in message text:
MESSAGE_DELIMITER = chr(ascii.RS)	# (Gladys agreed to try this.)
	# A control character.	(ASCII RS = 0x1E, record separator.)

# Define the bot's name (used in many places below).
#BOT_NAME = 'Gladys'	# The AI persona that we created this bot for originally.
BOT_NAME = TheAIPersonaConfig().botName		# This is the name of the bot.

# This is the name we'll attach to messages generated by the system.
SYS_NAME = 'BotServer'	  # This refers to the present system, i.e., the Telegram bot server program.

	#----------------------------------------------------------------------
	# Initialize the bot's persistent data, including any dynamically added
	# persistent memories.

PERSISTENT_DATA = ""  # Empty string initially.
MEMORIES = ""		# Will be loaded from TelegramBot.memories.txt.

def _initPersistentData():
	"""Initialize the persistent data string (including memories, if any)."""

	global PERSISTENT_DATA

	# This function initializes the AI's persistent context data.

	# Initialize the main data for the AI's persistent context.
	PERSISTENT_DATA = TheAIPersonaConfig().context 
		# NOTE: This should end with a newline. But if it doesn't, we'll add one.

	# Ensure that PERSISTENT_DATA ends with a newline.
	if PERSISTENT_DATA[-1] != '\n':
		PERSISTENT_DATA += '\n'

	# Append current memories, if any.
	if MEMORIES != "":
		PERSISTENT_DATA += MESSAGE_DELIMITER + \
			" ~~~ Memories added using '/remember' command: ~~~\n"
		PERSISTENT_DATA += MEMORIES

	# NOTE: The MEMORIES variable is intended for global (but dynamic) memories
	# for the current bot. Eventually we need to also add a section for user-
	# specific and/or chat-specific memories.
#__/ End definition of _initPersistentData() function.
	
_initPersistentData()	# Call the above function.


	#----------------------------------------------------------------------
	# This function initializes the AI's persistent context information
	# based on the PERSISTENT_DATA string. We'll call it whenever the
	# PERSISTENT_DATA string changes, which will happen when we read the
	# AI's persistent memory file, or when a '/remember' command is issued.
	
def _initPersistentContext():

	global PERSISTENT_DATA, PERSISTENT_CONTEXT	# So we can modify these.

	# Initialize the AI's persistent context information.
	PERSISTENT_CONTEXT = \
		MESSAGE_DELIMITER + " ~~~ Persistent context data: ~~~\n" + \
		PERSISTENT_DATA + \
		MESSAGE_DELIMITER + " ~~~ Commands available for me to use: ~~~\n" + \
		"  /pass - Refrain from responding to the last user message.\n" + \
		"  /image <desc> - Generate an image with description <desc> and send it to the user.\n" + \
		"  /block - Adds the current user to my block list.\n" + \
		"  /remember <text> - Adds <text> to my persistent context data.\n" + \
		"  /forget <text> - Removes <text> from my persistent context data.\n" + \
		MESSAGE_DELIMITER + " ~~~ Recent Telegram messages: ~~~"

# Go ahead and call it now.
_initPersistentContext()


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

# This is a string that we'll always use to prompt the AI to begin generating a new message.
AI_PROMPT = f'\n{MESSAGE_DELIMITER} {BOT_NAME}>'	# Used with GPT text API only.
	# NOTE: The ChatGPT versions of the bot do prompting differently, and don't use this.

# This is the size, in messages, of the window at the end of the conversation 
# within which we'll exclude messages in that region from being repeated by the AI.
# (This is basically a hack to try to suppress the AI's tendency to repeat itself.)
NOREPEAT_WINDOW_SIZE = 10

# Initialize & retrieve the AI persona configuration object.
aiconf = TheAIPersonaConfig()

# Retrieve some API config parameters we'll use.
temperature = aiconf.temperature
presPen = aiconf.presencePenalty
freqPen = aiconf.frequencyPenalty

# This is the name of the specific text generation engine (model version) that
# we'll use to generate the AI's responses.
ENGINE_NAME = aiconf.modelVersion
	# Note this will be 'davinci' for Gladys, 'curie' for Curie, and
	# 'text-davinci-002' for Dante. And so on.


	#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| The following code creates the connection to the core AI engine.
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global maxRetToks, minReplyWinToks

maxRetToks		 = TheAIPersonaConfig().maxReturnedTokens
	# This gets the AI's persona's configured preference for the *maximum*
	# number of tokens the back-end language model may return in a response.

minReplyWinToks	 = TheAIPersonaConfig().minReplyWinToks
	# This gets the AI's persona's configured preference for the *minimum*
	# number of tokens worth of space it should be given for its reply.

# Configure the stop sequence appropriate for this application.
stop_seq = MESSAGE_DELIMITER	# This is appropriate given the RS delimiter.
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


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	Construct remote API connection to the core GPT engine.
	#|
	#|	Note that instead of calling a GPT3Core class constructor directly here, 
	#|	we'll call the gpt3.api.createCoreConnection() factory function to create
	#|	the GPT3Core object.  This selects the appropriate GPT3Core subclass to
	#|	instantiate based on the selected engine name. We also go ahead and
	#|	configure some important API parameters here.

gptCore = createCoreConnection(ENGINE_NAME, maxTokens=maxRetToks, 
	temperature=temperature, presPen=presPen, freqPen=freqPen, 
	stop=stop_seq)

	# NOTE: The presence penalty and frequency penalty parameters are here 
	# to try to prevent long outputs from becoming repetitive. But too-large
	# values can cause long outputs to omit too many short filler words.
	# So, at present I recommend setting these parameters to 0.


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	The following function will be used to display the current date/time to
	#|	the AI, including the time zone.

# Time format string to use (note minutes are included, but not seconds).
_TIME_FORMAT = "%A, %B %d, %Y, %I:%M %p"
	# Format like "Saturday, June 10, 2023, 5:03 pm".

# The following function will get the current date/time as a string, including the timezone.
def timeString():

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


#/==============================================================================
#|	Class definitions.								[python module code section]
#|
#|	For this Telegram bot application, we define two major classes:
#|
#|		Message			- A message object stores the sender and text for a
#|							single (incoming or outgoing) Telegram message.
#|
#|		Conversation	- Keeps track of data that we care about (including
#|							the message list) for a single Telegram
#|							conversation.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# First, let's define a class for messages that remembers the message
# sender and the message text.

class Message:

	"""An object that instantiates this class stores the message sender and the
		message text for an incoming or outgoing message."""


	# New instance initializer (called automatically by class constructor).
	def __init__(self, sender, text):
		# Print diagnostic information.
		#_logger.debug(f"Creating message object for: {sender}> {text}")
		self.sender	  = sender

		if text is None:
			_logger.warn(f"""Can't initialize Message from {sender} with text of None; using "[null message]" instead.""")
			text = "[null message]"

		self.text	  = text
		self.archived = False
			# Has this message been written to the archive file yet?


	# Note that the following method is only used for GPT text engines, not chat engines.
	def __str__(self):
		"""A string representation of the message object.
			It is properly delimited for reading by the GPT-3 model."""
		return f"{MESSAGE_DELIMITER} {self.sender}> {self.text}"


		#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#|	Methods for serializing and deserializing message objects so that
		#|	they may be saved to, and retrieved from, a persistent archive file.
		#|	The archive file of each conversation is created incrementally, and
		#|	is loaded whenever the conversation is restarted.
		#|
		#|	NOTE: I could have made both serialize() and deserialize() methods
		#|	much simpler if I had just used codecs.encode() and codecs.decode();
		#|	but since I didn't do that originally, I have to still do a custom
		#|	implementation to maintain backwards compatibility with existing
		#|	conversation archive files. Trying to simplify the code, though.


	# The following method serializes the message object to a string
	# which can be appended to the conversation archive file, and
	# then later read back in when restoring the conversation.

	def serialize(self):

		"""Returns a string representation of a given message suitable for
			archiving, as a single newline-terminated line of text. Embedded
			newlines are escaped as '\\n'; and any other ASCII control characters 
			within the message text (except for TAB) are escaped using their
			'\\xHH' (hexadecimal) codes."""

		text = self.text
		if text is None:	# Null text? (Shouldn't happen, but...)
			text = "[null message]"		# Message is this placeholder. (Was empty string.)

		# NOTE: The message text could contain newlines, which we need to
		#	replace with a literal '\n' encoding. But, in case the message
		#	text happens to contain a literal '\' followed by an 'n', we
		#	need to escape that '\' with another '\' to avoid ambiguity.

		# Construct the replacement dictionary for serialization.
		serialize_replace_dict = {
			'\\': '\\\\',	# '\' -> '\\'
			'\n': '\\n',	# '[LF]' -> '\n' ([LF] = ASCII linefeed char).
		}

		# Add the other ASCII controls (except for TAB), but encoded as '\xHH'.
		for i in list(range(0, 9)) + list(range(11, 32)):	# Omit codes 9=TAB & 10=LF.
			serialize_replace_dict[chr(i)] = f"\\x{format(i, '02x')}"

		# Translate the characters that need escaping, in a single pass..
		escaped_text = text.translate(str.maketrans(serialize_replace_dict))

		# Now, we'll return the serialized representation of the message.
		return f"{self.sender}> {escaped_text}\n"	# Newline-terminated.


	# Given a line of text from a conversation archive file, this method
	# deserializes the message object from its encoding in the archive line.

	@staticmethod
	def deserialize(line):

		"""Deserialize a line in "Sender> Text" format from a message archive, 
			whose text is encoded using escaped '\\n' newlines and all '\\xHH' 
			ASCII control hexes other than 09=TAB (which is just encoded literally).
			Returns a new Message object representing the message."""

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
			# have defined it as a top-level function or class method.)

		# Construct the replacement dictionary for deserialization.
		deserialize_replace_dict = {

			'\\\\': '\\',	# '\\' -> '\'
			'\\n': '\n',	# '\n' -> '[LF]' ([LF] = ASCII linefeed char).

			#'\\ufffd': '\ufffd'	# '\ufffd' -> '[RC]' ([RC] = Unicode replacement char.)
				# NOTE: There is ambiguity as to whether these should really be de-escaped, 
				# -- because some earlier versions of this bot escaped them, and some didn't,
				# so, we just don't bother. It's doubtful the archive has any real instances.

		}

		# Also unescape the other ASCII controls (except for TAB), which are
		# encoded as '\xHH'.  (TAB is left in literal form in the archive.)
		for i in list(range(0, 9)) + list(range(11, 32)):
			deserialize_replace_dict[f"\\x{format(i, '02x')}"] = chr(i)

		# Define a custom replacer based on the dict we just constructed.
		def deserialize_replacer(match):
			return deserialize_replace_dict[match.group(0)]

		# Compile an appropriate regex pattern and use it to do the 
		# substitutions using the custom replacer we just defined.

		pattern = re.compile('|'.join(map(re.escape, 
				    deserialize_replace_dict.keys())))
		
		text = pattern.sub(deserialize_replacer, text)

		# Return a new object for the deserialized message.
		return Message(sender, text)
	
	#__/ End of message.deserialize() instance method definition.


	# Not currently used.
	#def __repr__(self):
	#	return self.serialize().rstrip('\n')
	
#__/ End of Message class definition.


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	The Conversation class is defined below.
	#|
	#|	An object instantiating this class is the primary data structure that
	#|	we use to keep track of an individual Telegram conversation. Note that
	#|	a conversation may be associated either with a single user, or a group
	#|	chat. Group chats are distinguished by having negative chat IDs.
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


# Exception class to represent an error in the conversation.
class ConversationError(Exception):
	"""Exception class to represent an error in the conversation."""
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return self.message


# We use this global Boolean to keep track of whether
# the dynamic persistent memory list is non-empty.
global _anyMemories
_anyMemories = False

# This global string tracks the last error reported
# using the conversation.report_error() instance method.
global _lastError
_lastError = ""


# Next, let's define a class for conversations that remembers the messages in
# the conversation.  We'll use a list of Message objects to store the messages.

class Conversation:

	"""An object instantiating this class stores the recent messages
		in an individual Telegram conversation."""

	# New instance initializer.
	def __init__(self, chat_id:int):

		"""Instance initializer for a new conversation object for a given
			Telegram chat (identified by an integer ID)."""

		# Print diagnostic information to console (& log file).
		_logger.normal(f"Creating conversation object for chat_id: {chat_id}")

		self.bot_name = BOT_NAME	# The name of the bot. ('Gladys', 'Aria', etc.)
		self.chat_id = chat_id		# Remember the chat ID associated with this convo.
		self.messages = []			# No messages initially (until added or loaded).

		# Print diagnostic information.
		print(f"\tCreating conversation object for chat_id: {chat_id}")

		# The following is a string which we'll use to accumulate the conversation text.
		self.context_string = PERSISTENT_CONTEXT	# Start with just the global persistent context data.

		# These attributes are for managing the length (in messages) of the message list.
		self.context_length = 0				# Initially there are no Telegram messages in the context.
		self.context_length_max = 200		# Max number N of messages to include in the context.

		# Determine the filename we'll use to archive/restore the conversation.
		self.filename = f"{LOG_DIR}/{_appName}.{chat_id}.txt"

		# We'll also need another file to store the AI's persistent memories.
		# NOTE: These are currently shared among all conversations!
		# Eventually, we should really have a different one for each conversation, or user.
		self.mem_filename = f"{LOG_DIR}/{_appName}.memories.txt"

		# Read the conversation archive file, if it exists.
		self.read_archive()	  # Note this will retrieve at most the last self.context_length_max messages.

		# Also read the persistent memory file, if it exists.
		self.read_memory()

		# Go ahead and open the conversation archive file for appending.
		self.archive_file = open(self.filename, 'a')

		# Also open the persistent memory file for appending.
		self.memory_file = open(self.mem_filename, 'a')

		## NOTE: Since the above files are never closed, we may eventually run out of
		## file descriptors, and the entire bot server will stop working. Really, we
		## should close them whenever an existing convo is restarted, before reopening.

	#__/ End of conversation instance initializer.


	# This method adds the messages in the conversation to the context string.
	# NOTE: This method is only really needed for the GPT text engines.

	def expand_context(self):

		# First, we'll start the context string out with a line that gives
		# the current date and time, in the local timezone (from TZ).
		self.context_string = f"Current time: {timeString()}\n"	# This function is defined above.

		# Now we'll add the persistent context, and then the last N messages.
		self.context_string += PERSISTENT_CONTEXT + '\n'.join([str(m) for m in self.messages])
			# Join the messages into a single string, with a newline between each.
			# Include the persistent context at the beginning of the string.


	# This method reads recent messages from the conversation archive file, if it exists.
	def read_archive(self):
		# If the conversation archive file exists, read it.
		if os.path.exists(self.filename):
			# Open the conversation archive file.
			with open(self.filename, 'r') as f:
				# Read the file line by line.
				for line in f:

					# Deserialize the message object from the line.
					message = Message.deserialize(line)

					# If we're already at the maximum context length, pop the oldest message
					if self.context_length >= self.context_length_max:
						self.messages.pop(0)
						self.context_length -= 1

					# Append the message to the conversation.
					self.messages.append(message)
					self.context_length += 1

			# Update the conversation's context string.
			self.expand_context()


	# This method reads the AI's persistent memories from the persistent memory file, if it exists.
	def read_memory(self):

		global PERSISTENT_DATA	# We declare this global so we can modify it.
		global MEMORIES
		global _anyMemories

		# Boolean to keep track of whether we've already read any lines from the persistent memory file.
		read_lines = False

		# If the persistent memory file exists, read it.
		if os.path.exists(self.mem_filename):

			# NOTE: At present, we simply read the entire file
			# as a single string and append it to the persistent data
			# string and update the persistent context string.
			# NOTE: This will eventually cause problems if the
			# persistent memory file becomes too long to fit in
			# the AI's receptive field.
			# In the future, we may want to store the persistent data
			# in a dictionary and access it more selectively.

			# Open the persistent memory file.
			with open(self.mem_filename, 'r') as f:
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
			self.expand_context()

			# The below version was Copilot's idea.
			# Open the persistent memory file.
			#with open(self.mem_filename, 'r') as f:
			#	 # Read the file line by line.
			#	 for line in f:
			#		 # Split the line into the key and the value.
			#		 parts = line.split('=')
			#		 key = parts[0]
			#		 value = '='.join(parts[1:])
			#
			#		 # Add the key/value pair to the persistent memory dictionary.
			#		 self.memory[key] = value

	# This method adds a message to the AI's persistent memory file.
	# It also updates the persistent context string.
	def add_memory(self, new_memory:str) -> bool:

		global MEMORIES
		global PERSISTENT_DATA	# We declare this global so we can modify it.
		global _anyMemories

		if new_memory is None or new_memory == "" or new_memory == "\n":
			self.report_error("/remember command needs a non-empty argument.")
			return False

		# Make sure the new memory ends in a newline.
		if new_memory[-1] != '\n':
			new_memory += '\n'

		if _anyMemories and ('\n' + new_memory) in MEMORIES:
			self.report_error(f"Text [{new_memory[:-1]}] is already in memory.")
			return False

		if not _anyMemories:
			PERSISTENT_DATA += MESSAGE_DELIMITER + \
				" ~~~ Memories added using '/remember' command: ~~~\n"
			_anyMemories = True		# So we only add one new section header!

		# Add the new memory to the persistent data string.
		MEMORIES += new_memory
		PERSISTENT_DATA += new_memory

		# Update the persistent context string.
		_initPersistentContext()

		# Update the conversation's context string.
		self.expand_context()

		# NOTE: We should really make the below atomic so that
		# memories written from multiple threads don't get mixed.

		# Also, append the new memory to the persistent memory file.
		self.memory_file.write(new_memory)
		# Flush the file to make sure it's written to disk.
		self.memory_file.flush()

		return True

	#__/ End method conversation.add_memory().


	# This method removes a message from the AI's persistent memory file.
	# It also updates the persistent context string. It returns true if the 
	# memory was removed, false otherwise.
	def remove_memory(self, text_to_remove:str) -> bool:

		global MEMORIES
		global _anyMemories

		if text_to_remove == None or len(text_to_remove) == 0:
			self.report_error("/forget command needs a non-empty argument.")
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

			self.report_error(f"[{text_to_remove.rstrip()}] not found in persistent memory.")
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
		self.expand_context()

		# Also remove the memory from the persistent memory file.
		# We'll use the following algorithm:
		#	(1) Close the "write" file descriptor and reopen it in "read" mode.
		#	(2) Return the read position to the start of the file.
		#	(3) Read the entire file into a string.
		#	(4) Remove the text to remove from the string.
		#	(5) Close the file again and reopen it for writing.
		#	(6) Write the string back to the file.
		#	(7) Flush the file to make sure it's written to disk.

		# Close the "write" file descriptor.
		self.memory_file.close()

		# Reopen it in "read" mode.
		self.memory_file = open(self.mem_filename, 'r')

		# Return the read position to the start of the file.
		self.memory_file.seek(0)

		# Read the entire file into a string.
		mem_string = '\n' + self.memory_file.read()

		# Remove the text to remove from the string.
		mem_string = mem_string.replace(text_to_remove, '\n')

		# Close the file again and reopen it for writing.
		self.memory_file.close()

		# Reopen it for writing.
		self.memory_file = open(self.mem_filename, 'w')

		# Write the string back to the file.
		self.memory_file.write(mem_string[1:])

		# Flush the file to make sure it's written to disk.
		self.memory_file.flush()

		# Return true to indicate that the memory was removed.
		return True

	#__/ End method conversation.remove_memory().


	# This method is called to expunge the oldest message from the conversation
	# when the context string gets too long to fit in GPT-3's receptive field.
	def expunge_oldest_message(self):
		"""This method is called to expunge the oldest message from the conversation."""

		# There's an important error case that we need to consider:
		# If the conversation only contains one message, this means that the
		# AI has extended that message to be so large that it fills the
		# entire available space in the GPT-3 receptive field.	If we
		# attempt to expunge the oldest message, we'll end up deleting
		# the very message that the AI is in the middle of constructing.
		# So, we can't do anything here except throw an exception.
		if len(self.messages) <= 1:
			raise ConversationError("Can't expunge oldest message from conversation with only one message.")

		# If we get here, we can safely pop the oldest message.

		_logger.debug(f"Expunging oldest message from {len(self.messages)}-message conversation #{self.chat_id}.")
		#print("Oldest message was:", self.messages[0])
		self.messages.pop(0)
		self.expand_context()	# Update the context string.


	def report_error(self, errmsg):

		"""Adds an error report to the conversation. Also logs the error."""

		global _lastError

		msg = f"Error: {errmsg}"

		# Add the error report to the conversation.
		self.add_message(Message(SYS_NAME, msg))

		_logger.error(msg)	# Log the error.

		_lastError = msg	# So higher-level callers can access it.


	def add_message(self, message, finalize=True):
		"""Add a message to the conversation."""
		self.messages.append(message)
		if len(self.messages) > self.context_length_max:
			self.messages = self.messages[-self.context_length_max:]	# Keep the last N messages
		self.context_length = len(self.messages)
		self.expand_context()	# Update the context string.

		# Unless this message isn't to be finalized yet, we'll also need to
		# append the message to the conversation archive file.
		if finalize:
			self.finalize_message(message)


	# Extend a (non-finalized) message by appending some extra text onto the end of it.
	# NOTE: This should only be called on the last message in the conversation.
	def extend_message(self, message, extra_text):

		# First, make sure the message has not already been finalized.
		if message.archived:
			print("ERROR: Tried to extend an already-archived message.")
			return

		# Add the extra text onto the end of the message.
		message.text += extra_text

		# We also need to update the context string.
		self.context_string += extra_text


	# This method deletes the last message at the end of the conversation.
	# (This is normally only done if the message is empty, since Telegram
	# will not send an empty message anyway.)
	def delete_last_message(self):

		# First, make sure the message has not already been finalized.
		#if self.messages[-1].archived:
		#	print("ERROR: Tried to delete an already-archived message.")
		#	return

		# Delete the last message.
		self.messages.pop()
		self.context_length -= 1

		# We also need to update the context string.
		self.expand_context()	# Update the context string.


	def finalize_message(self, message):
		"""Finalize a message in the conversation (should be the last message)."""

		if not hasattr(message,'archived') or not message.archived:
			self.archive_message(message)


	def archive_message(self, message):
		"""Add a message to the conversation, and archive it."""
		self.archive_file.write(message.serialize())
		self.archive_file.flush()
		message.archived = True


	# The following method clears the entire conversational memory.
	# However, it does not erase the archive file or clear the 
	# persistent memory file.
	def clear(self):
		"""Clear the entire conversational memory."""
		self.messages = []
		self.context_length = 0
		self.expand_context()	# Update the context string.

	# This method checks whether a given message is already in the conversation,
	# within the last NOREPEAT_WINDOW_SIZE messages. This is used to help prevent 
	# the bot from getting into a loop where it sends the same message over and 
	# over too frequently.
	def is_repeated_message(self, message):
		"""Check whether a message (with the same sender and text) is already 
			included in the most recent <NOREPEAT_WINDOW_SIZE> messages of the 
			conversation."""
		# NOTE: In below, don't check against the last message in the conversation,
		# because that one is the very (candidate) message that we're checking!!
		for m in self.messages[-NOREPEAT_WINDOW_SIZE-1:-1]:
			if m.sender == message.sender and m.text == message.text:
				return True
		return False


	# This method converts the persistent context and the list of messages
	# into the format of a 'messages' list as expected by the GPT-3 chat API.
	def get_chat_messages(self):

		"""Convert the persistent context and the list of messages into the 
			format of a 'messages' list as expected by the GPT-3 chat API."""
		
		chat_messages = []		# Initialize the list of chat messages.

		botName = self.bot_name

		# The first message will be a system message showing the current time.
		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			'content': "The current time is: " + timeString() + "."
		})
		
		# The next message will show the persistent context header block.
		# Note this header includes several subsections, delimited by
		# record separators (ASCII code 30) and section headings.
		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			'content': "Attention, assistant: You are taking the role of a very " \
				f"humanlike AI persona named {botName} in a Telegram chat. Here " \
				"are the context headers for the persona, followed by recent " \
				"messages in the chat:\n" + \
					PERSISTENT_CONTEXT
		})

		# Next, add the messages from the recent part of the conversation.
		# We'll use the .sender attribute of the Message object as the 'name'
		# attribute of the chat message, and we'll use the .text attribute
		# of the Message object as the 'content' attribute of the chat message.
		for message in self.messages:

			sender = message.sender

			if sender == 'SYSTEM':	# Backwards-compatible to legacy SYS_NAME value.
				sender = SYS_NAME	# Map to new name.

			if sender == SYS_NAME:
				role = CHAT_ROLE_SYSTEM
			elif sender == botName:
				role = CHAT_ROLE_AI
			else:
				role = CHAT_ROLE_USER
			
			chat_messages.append({
				'role': role,		# Note: The role field is always required.
				'name': sender,		
					# Note: When 'name' is present, the API uses it in place of
					# (or in addition to!) the role.
				'content': message.text
			})

		# We'll add one more system message to the list of chat messages,
		# to make sure it's clear to the AI that it is responding in the 
		# role of the message sender whose 'role' matches our .bot_name
		# attribute.
		#
		# (The back-end language model will be prompted to respond by something like 
		# "assistant\n", which is why we need to make sure it knows that it's responding 
		# as the bot.)

		response_prompt = f"Respond as {botName}. (If you want to include an image in your response, put the command ‘/image <desc>’ as the first line of your response.)"
		if self.chat_id < 0:	# Negative chat IDs correspond to group chats.
			# Only give this instruction in group chats:
			response_prompt += " (However, if the user is not addressing you, type '/pass' to remain silent.)"

		chat_messages.append({
			'role': CHAT_ROLE_SYSTEM,
			'content': response_prompt
		})

			#'content': f"Respond as {botName}, in the user's language if possible. (However, if the user is not addressing you, type '/pass' to remain silent.)"
				
			# 'content': f"Respond as {self.bot_name}."
			# # This is simple and seems to work pretty well.

			#'content': f"Assistant, your role in this chat is '{self.bot_name}'; enter your next message below.",
				# This was my initial wording, but it seemed to cause some confusion.

			#'content': f"{self.bot_name}, please enter your response below at the 'assistant' prompt:"
				# The above wording was agreed upon by me & Turbo (model 'gpt-3.5-turbo').

			# Trying this now:
			#'content': f"Please now generate {self.bot_name}'s response, in the format:\n" \
			#	 r"%%%\n" \
			#	 "Commentary as assistant:\n"
			#	 "{assistant_commentary}\n"
			#	 r"%%%\n" \
			#	 f"{self.bot_name}'s response:\n"
			#	 "{persona_response}\n"
			#	 r"%%%\n"

		return chat_messages
	
	#__/ End conversation.get_chat_messages() instance method definition.

#__/ End Conversation class definition.


# Next, we create an instance of the telegram.ext.Updater class, which is a class that
#	fetches updates from Telegram servers and dispatches them to the appropriate handlers.
# We pass the token for the bot to the Updater constructor.
#	The token is the API key for the bot.
updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'], use_context=True)
dispatcher = updater.dispatcher
	# This is the dispatcher object that we'll use to register handlers.


#/==============================================================================
#|	HANDLER FUNCTIONS.										  [code section]
#|	~~~~~~~~~~~~~~~~~~
#|
#|		In this section, we define various handler functions which are
#|		called by the dispatcher to handle updates received from the
#|		central Telegram server. As of v20.0 of the python-telegram-bot
#|		library, these should be implemented as asyncio functions for
#|		improved concurrency. They are wrapped within handler objects
#|		which are created in the next code section. The list of handler
#|		functions, by handler group, is as follows:
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

# Retrieve the bot's startup message from the AI persona's configuration.
START_MESSAGE = TheAIPersonaConfig().startMsg

# Now, let's define a function to handle the /start command.
def handle_start(update, context):			# Context, in this context, is the Telegram context object. (Not the context string for passing to GPT-3.)

	"""Start the conversation."""

	chat_id = update.message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a specific conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user_name
	user_name = _get_user_name(update.message.from_user)

	# Print diagnostic information.
	_logger.normal(f"User {user_name} started conversation {chat_id}.")

	# Create a new conversation object and link it from the Telegram context object.
	# NOTE: It needs to go in the context.chat_data dictionary, because that way it
	# will be specific to this chat_id. This will also allow updates from different
	# users in the same chat to all appear in the same conversation.
	conversation = Conversation(chat_id)
		# Note this constructor call will also reload the conversation data, if it exists.
	context.chat_data['conversation'] = conversation

	# Add the /start command itself to the conversation archive.
	conversation.add_message(Message(user_name, update.message.text))

	# Send an initial message to the user.
	# NOTE: If messages were read from the conversation archive file,
	#	this means we are continuing a previous conversation after
	#	a restart of the bot. In this case, we don't want to send the
	#	start message.
	if len(conversation.messages) <= 1:

		_logger.normal(f"\tSending start message to user {user_name} in new conversation {chat_id}.")

		try:
			update.message.reply_text(START_MESSAGE)
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
			return

		conversation.add_message(Message(conversation.bot_name, START_MESSAGE))
		# Also record the initial message in our conversation data structure.

	else:

		_logger.normal(f"\tSending restart message to user {user_name} for existing conversation {chat_id}.")

		# Compose a system diagnostic message explaining what we're doing.
		DIAG_MSG = f"[DIAGNOSTIC: Restarted bot with last {len(conversation.messages)} messages from archive.]"

		try:
			update.message.reply_text(DIAG_MSG)
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
			return

		# If that succeeded, add it to the conversation archive too (so the AI will see it).
		conversation.add_message(Message(SYS_NAME, DIAG_MSG))

	# Give the user a system warning if their first name contains unsupported characters or is too long.
	if not re.match(r"^[a-zA-Z0-9_-]{1,64}$", update.message.from_user.first_name):
		
	       # Log the warning.
		_logger.warning(f"User {update.message.from_user.first_name} has an unsupported first name.")
		
           # Add the warning message to the conversation, so the AI can see it.
		warning_msg = f"NOTIFICATION: Welcome, \"{update.message.from_user.first_name}\". " \
			f"The AI will identify you in this conversation by your {_which_name}, {user_name}."

		#warning_msg = f"[SYSTEM NOTIFICATION: Your first name \"{update.message.from_user.first_name}\"" \
		#	"contains unsupported characters (or is too long). The AI only supports names with <=64 alphanumeric " \
		#	"characters (a-z, 0-9), dashes (-) or underscores (_). For purposes of this conversation, "   \
		#	f"you will be identified by your {_which_name}, {user_name}.]"
				
			# Make sure the AI sees that message, even if we fail in sending it to the user.
		conversation.add_message(Message(SYS_NAME, warning_msg))
		
            # Also send the warning message to the user. (Making it clear that 
            # it's a system message, not from the AI persona itself.)
		reply_msg = f"[SYSTEM {warning_msg}]"
		try:
			update.message.reply_text(reply_msg)
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; ignoring.")

	return

#__/ End handle_start() function definition.


# Below is the help string for the bot. (Displayed when '/help' is typed in the chat.)

# First calculate the model family, which is mentioned in the help string. 
# We'll get it from the core object's .modelFamily property.
MODEL_FAMILY = gptCore.modelFamily

# Note the below would have been the original way to get the model family,
# but this method is now obsolete, since the core objects know their own 
# model family.
#MODEL_FAMILY = TheAIPersonaConfig().modelFamily

def _ensure_convo_loaded(update, context) -> bool:

	"""Helper function to ensure the conversation data is loaded,
		and auto-restart the conversation if isn't."""

	# Get the chat ID.
	chat_id = update.message.chat.id

	# Get the user's name.
	user_name = _get_user_name(update.message.from_user)

	if not 'conversation' in context.chat_data:

		_logger.normal(f"User {user_name} sent a message in an uninitialized conversation {chat_id}.")
		_logger.normal(f"\tAutomatically starting (or restarting) conversation {chat_id}.")

		DIAG_MSG = "[DIAGNOSTIC: Either this is a new chat, or the bot server was rebooted. Auto-starting conversation.]"
			# NOTE: The AI won't see this diagnostic because the convo hasn't even been reloaded yet!

		try:
			update.message.reply_text(DIAG_MSG)
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
			return False

		# Temporarily pretend user entered '/start', and process that.
		_tmpText = update.message.text
		update.message.text = '/start'
		handle_start(update,context)
		update.message.text = _tmpText
			# For some reason, this isn't working?
	
	return True

# Aria rewrote this in her voice. This is now in Aria's ai-config.json|telegram-conf|help-string.
#HELP_STRING = f"""
#Hello, I'm Aria! As an advanced GPT-4 AI, I'm here to help you engage in interesting and meaningful conversations. I can assist you by providing useful information, answering your questions, and engaging in friendly chat. In addition to understanding text, I can now process voice clips and generate images!
#
#Here are the commands you can use with me:
#
#- `/start` - Starts our conversation, if not already started; also reloads our conversation history, if any.
#- `/help` - Displays this help message.
#- `/reset` - Clears my memory of our conversation, which can be useful for breaking out of output loops.
#- `/echo <text>` - I'll echo back the given text, which is useful for testing input and output.
#- `/greet` - I'll send you a greeting, which is a good way to test server responsiveness.
#
#To request an image in my response, use the command `/image <desc>` as the first line of your message, and I'll generate and send the image to you.
#
#Please remember to be polite and ethical while interacting with me. If you need assistance or have any questions, feel free to ask. I'm here to help! 😊"""

HELP_STRING="""
{BOT_NAME} bot powered by {MODEL_FAMILY}/{ENGINE_NAME}.
	NOTE: {BOT_NAME} now understands voice clips and can
	generate images!

Available commands:
	/start - Starts the bot, if not already started; also reloads conversation history, if any.
	/help - Shows this help message.
	/reset - Clears the bot's memory of the conversation. Useful for breaking output loops.
	/echo <text> - Echoes back the given text. (I/O test.)
	/greet - Causes the server to send a greeting. (Server responsiveness test.)

NOTE: Please be polite and ethical, or you may be blocked."""

# No longer supported for random users:
#  remember - Adds the given statement to the bot's persistent context data.
#  forget - Removes the given statement from the bot's persistent context data.

# Override help string if it's set in ai-config.hjson.
if TheAIPersonaConfig().helpString:
	_logger.normal("Using custom help string.")
	HELP_STRING = TheAIPersonaConfig().helpString
	customHelp = True
else:
	customHelp = False

# This function checks whether the given user name is in our access list.
# If it is, it returns True; otherwise, it returns False.
def _check_access(user_name) -> bool:

	# Temporary override to have blacklist override whitelist.
	return not _isBlocked(user_name)

	# Get the value of environment variable AI_DATADIR.
	# This is where we'll look for the access list file.
	ai_datadir = os.getenv('AI_DATADIR')

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


# Now, let's define a function to handle the /help command.
def handle_help(update, context):
	"""Display the help string when the command /help is issued."""

	chat_id = update.message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_name(update.message.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not _ensure_convo_loaded(update, context):
		return False

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /help command to conversation {chat_id} because it's not loaded.")
		return False

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /help command itself to the conversation archive.
	conversation.add_message(Message(user_name, update.message.text))

	_logger.normal(f"User {user_name} entered a /help command for chat {chat_id}.")

	# Log diagnostic information.
	_logger.normal(f"\tDisplaying help in conversation {chat_id}.")

	try:
		update.message.reply_text(HELP_STRING)
	except BadRequest or Unauthorized or ChatMigrated as e:
		_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
		return False

	# Also record the help string in our conversation data structure.
	who = BOT_NAME if customHelp else SYS_NAME
	conversation.add_message(Message(who, HELP_STRING))

	return True		# Finished processing this message.
#__/


# Now, let's define a function to handle the /echo command.
def handle_echo(update, context):
	"""Echo the user's message."""

	chat_id = update.message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_name(update.message.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not _ensure_convo_loaded(update, context):
		return False

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /echo command line to conversation {chat_id} because it's not loaded.")
		return False

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	cmdLine = update.message.text

	# Add the /echo command itself to the conversation archive.
	conversation.add_message(Message(user_name, cmdLine))

	# Check whether the user is in our access list.
	#if not _check_access(user_name):
	#	_logger.normal(f"User {user_name} tried to access chat {chat_id}, but is not in the access list. Denying access.")
	#
	#	#errMsg = f"Sorry, but user {user_name} is not authorized to access {BOT_NAME} bot."
	#	errMsg = f"Sorry, but {BOT_NAME} bot is offline for now due to cost reasons."
	#
	#	try:
	#		update.message.reply_text(f"[SYSTEM: {errMsg}]")
	#	except BadRequest or Unauthorized or ChatMigrated as e:
	#		_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
	#
	#	# Also record the error in our conversation data structure.
	#	conversation.add_message(Message(SYS_NAME, errMsg))
	#	return

	_logger.normal(f"User {user_name} entered an /echo command for chat {chat_id}.")

	if len(cmdLine) > 6:
		textToEcho = cmdLine[6:]
	else:
		textToEcho = ""

	responseText = f'Response: "{textToEcho}"'

	# Log diagnostic information.
	_logger.normal(f"Echoing [{textToEcho}] in conversation {chat_id}.")

	try:
		update.message.reply_text(responseText)
	except BadRequest or Unauthorized or ChatMigrated as e:
		_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
		return False

	# Also record the echo text in our conversation data structure.
	conversation.add_message(Message(SYS_NAME, responseText))

	return True

# Now, let's define a function to handle the /greet command.
def handle_greet(update, context):

	"""Greet the user."""

	chat_id = update.message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_name(update.message.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not _ensure_convo_loaded(update, context):
		return False

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't add /greet command line to conversation {chat_id} because it's not loaded.")
		return False

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /greet command itself to the conversation archive.
	conversation.add_message(Message(user_name, update.message.text))

	_logger.normal(f"User {user_name} entered a /greet command for chat {chat_id}.")

	# Log diagnostic information.
	_logger.normal(f"Sending greeting in conversation {chat_id}.")

	GREETING_TEXT = "Hello! I'm glad you're here. I'm glad you're here.\n"
		# Copilot composed this. 

	try:
		update.message.reply_text(GREETING_TEXT)
	except BadRequest or Unauthorized or ChatMigrated as e:
		_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
		return False

	# Also record the echo text in our conversation data structure.
	conversation.add_message(Message(SYS_NAME, GREETING_TEXT))

	return True
#__/


# Now, let's define a function to handle the /reset command.
def handle_reset(update, context):
	"""Reset the conversation."""

	chat_id = update.message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get user name to use in message records.
	user_name = _get_user_name(update.message.from_user)

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not _ensure_convo_loaded(update, context):
		return False

	if 'conversation' not in context.chat_data:
		_logger.error(f"Can't reset conversation {chat_id} because it's not loaded.")
		return False

	# Fetch the conversation object.
	conversation = context.chat_data['conversation']

	# Add the /reset command itself to the conversation archive.
	conversation.add_message(Message(user_name, update.message.text))

	_logger.normal(f"User {user_name} entered a /reset command for chat {chat_id}.")

	# Print diagnostic information.
	_logger.normal(f"Resetting conversation {chat_id}.")

	# Clear the conversation.
	conversation.clear()

	# Send a diagnostic message.
	DIAG_MSG = f"[DIAGNOSTIC: Cleared conversation {chat_id}.]"
	try:
		update.message.reply_text(DIAG_MSG)
	except BadRequest or Unauthorized or ChatMigrated as e:
		_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
		return False

	# If that succeeded, show it to the AI also.
	conversation.add_message(Message(SYS_NAME, DIAG_MSG))

	# Send an initial message to the user.
	reset_message = f"This is {BOT_NAME}. I've cleared my memory of our previous conversation."
	try:
		update.message.reply_text(reset_message)
	except BadRequest or Unauthorized or ChatMigrated as e:
		_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
		return False

	# Also record the reset message in our conversation data structure.
	conversation.add_message(Message(conversation.bot_name, reset_message))

	return True

#__/ End definition of /reset command handler function.


# Now, let's define a function to handle the /remember command.
def handle_remember(update, context):

	"""Add the given message as a new memory."""

	chat_id = update.message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get the name that we'll use for the user.
	user_name = _get_user_name(update.message.from_user)

	# Block /remember command for users other than Mike.
	if user_name != 'Michael':
	
		_logger.warn("NOTE: Currently ignoring /remember command for all users besides Michael.")
	
		try:
			update.message.reply_text(f"[DIAGNOSTIC: Sorry, the /remember command is currently disabled.]\n")
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
			
		return False	# Quit early

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not _ensure_convo_loaded(update, context):
		return False

	# Retrieve the Conversation object from the Telegram context.
	if not 'conversation' in context.chat_data:
		_logger.error(f"Ignoring /remember command for conversation {chat_id} because conversation not loaded.")
		return False

	conversation = context.chat_data['conversation']

	# First, we'll add the whole /remember command line to the conversation, so that the AI can see it.
	conversation.add_message(Message(user_name, update.message.text))

	# Check whether the user is in our access list.
	if not _check_access(user_name):
		_logger.normal(f"User {user_name} tried to access chat {chat_id}, but is not in the access list. Denying access.")

		#errMsg = f"Sorry, but user {user_name} is not authorized to access {BOT_NAME} bot."
		errMsg = f"Sorry, but {BOT_NAME} bot is offline for now due to cost reasons."

		try:
			update.message.reply_text(f"[SYSTEM: {errMsg}]")
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")

		# Also record the error in our conversation data structure.
		conversation.add_message(Message(SYS_NAME, errMsg))
		return False

	_logger.normal(f"User {user_name} entered a /remember command for chat {chat_id}.")

	# Get the command's argument, which is the text to remember.
	text = ' '.join(update.message.text.split(' ')[1:])

	# Tell the conversation object to add the given message to the AI's persistent memory.
	if not conversation.add_memory(text):
		errmsg = _lastError

		# Generate an error-level report to include in the application log.
		_logger.error(f"{user_name} failed to add memory: [{text.strip()}]")
	
		diagMsg = f"[DIAGNOSTIC: Could not add [{text.strip()}] to persistent memory. " \
				  f"Error message was: \"{errmsg}\"]\n"

		# Send the diagnostic message to the user.
		try:
			update.message.reply_text(diagMsg)
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
			return False
			
		# Add the diagnostic message to the conversation.
		conversation.add_message(Message(SYS_NAME, diagMsg))
		
		return False

	_logger.normal(f"{user_name} added memory: [{text.strip()}]")

	# Send a reply to the user.
	DIAG_MSG = f"[DIAGNOSTIC: Added [{text.strip()}] to persistent memory.]\n"
	try:
		update.message.reply_text(DIAG_MSG)
	except BadRequest or Unauthorized or ChatMigrated as e:
		_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")

	# Also record the diagnostic message in our conversation data structure.
	conversation.add_message(Message(SYS_NAME, DIAG_MSG))

	return True

#__/ End definition of /remember command handler.


# Now, let's define a function to handle the /forget command.
def handle_forget(update, context):
	
	"""Remove the given message from the AI's persistent memory."""
	
	chat_id = update.message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Get the name that we'll use for the user.
	user_name = _get_user_name(update.message.from_user)

	_logger.normal(f"User {user_name} entered a /forget command for chat {chat_id}.")

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not _ensure_convo_loaded(update, context):
		return False

	# Retrieve the Conversation object from the Telegram context.
	if not 'conversation' in context.chat_data:
		_logger.error(f"Ignoring /forget command for conversation {chat_id} because conversation not loaded.")

	conversation = context.chat_data['conversation']

	# First, we'll add the whole /forget command line to the conversation, so that the AI can see it.
	conversation.add_message(Message(user_name, update.message.text))

	# Check whether the user is in our access list.
	if not _check_access(user_name):
		_logger.normal(f"User {user_name} tried to access chat {chat_id}, but is not in the access list. Denying access.")

		#errMsg = f"Sorry, but user {user_name} is not authorized to access {BOT_NAME} bot."
		errMsg = f"Sorry, but {BOT_NAME} bot is offline for now due to cost reasons."

		try:
			update.message.reply_text(f"[SYSTEM: {errMsg}]")
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")

		# Also record the error in our conversation data structure.
		conversation.add_message(Message(SYS_NAME, errMsg))
		return False

	# Get the command's argument, which is the text to forget.
	text = ' '.join(update.message.text.split(' ')[1:])

	# Tell the conversation object to remove the given message from the AI's persistent memory.
	# This returns a boolean indicating whether the operation was successful.
	success = conversation.remove_memory(text)

	# If the operation was successful, send a reply to the user.
	if success:

		# Generate a normal-level report to include in the application log.
		_logger.normal(f"{user_name} removed memory: [{text.strip()}]")

		# Send a reply to the user.
		DIAG_MSG = f"[DIAGNOSTIC: Removed [{text.strip()}] from persistent memory.]\n"
		try:
			update.message.reply_text(DIAG_MSG)
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; ignoring.")
			
		# Also record the diagnostic message in our conversation data structure.
		conversation.add_message(Message(SYS_NAME, DIAG_MSG))
	
	# If the operation was not successful, send a different reply to the user.
	else:
		
		errmsg = _lastError

		# Generate an error-level report to include in the application log.
		_logger.error(f"{user_name} failed to remove memory: [{text.strip()}]")
	
		diagMsg = f"[DIAGNOSTIC: Could not remove [{text.strip()}] from persistent memory. " \
				  f"Error message was: \"{errmsg}\"]\n"

		# Send the diagnostic message to the user.
		try:
			update.message.reply_text(diagMsg)
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
			return False
			
		# Add the diagnostic message to the conversation.
		conversation.add_message(Message(SYS_NAME, diagMsg))

	# Copilot wrote the following amusing diagnostic code. But we don't really need it.
	## Now, let's see if the AI has any memories left.
	#if len(conversation.memories) == 0:
	#	 update.message.reply_text(f"I'm sorry, I don't remember anything else.\n")
	#else:
	#	 update.message.reply_text(f"I remember these things:\n")
	#	 for memory in conversation.memories:
	#		 update.message.reply_text(f"\t{memory}\n")

	return True

#__/ End definition of /forget command handler.

# This global just keeps track of whether _get_user_name() retrieved the user's "first name" 
# or their "username" or their "user ID". (Its value is one of those literal strings.)
global _which_name

# This function, given a Telegram user object, returns a string that identifies the user.
def _get_user_name(user):

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
	if user_name is not None and gptCore.isChat:
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


def handle_audio(update, context):
	"""Handle an audio message from the user."""

	user_name = _get_user_name(update.message.from_user)

	# Get the chat ID.
	chat_id = update.message.chat.id

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not _ensure_convo_loaded(update, context):
		return False

	# Get our Conversation object.
	conversation = context.chat_data['conversation']

	_logger.normal(f"Received a message with audio from user {user_name} in chat {chat_id}.")

	# Check if the message contains audio or voice
	if update.message.audio:
		audio = update.message.audio
	elif update.message.voice:
		audio = update.message.voice
	else:
		_logger.error("A message passed the audio/voice filter, but did not contain either.")
		return False	# So dispatcher will try other filters.

	# Get the file_id and download the file
	file_id = audio.file_id
	file_obj = context.bot.get_file(file_id)

	# Get the value of environment variable AI_DATADIR.
	# This is where we'll save any audio files.
	ai_datadir = os.getenv('AI_DATADIR')
	audio_dir = os.path.join(ai_datadir, 'audio')

	# Create a folder to save the audio files if it doesn't exist
	if not os.path.exists(audio_dir):
		os.makedirs(audio_dir)

	# Pick a shorter ID for the file (collisions will be fairly rare).
	short_file_id = f"{random.randint(1,1000000)-1:06d}"

	# Save the audio as an OGG file
	ogg_file_path = os.path.join(audio_dir, f'{user_name}-{short_file_id}.ogg')
	_logger.normal(f"\tDownloading audio from user {user_name} in chat {chat_id} to OGG file {ogg_file_path}.")
	file_obj.download(ogg_file_path)

	# Convert the OGG file to MP3 (we were using WAV, but the file size was too big).
	mp3_file_path = os.path.join(audio_dir, f'{user_name}-{short_file_id}.mp3')
	_logger.normal(f"\tConverting audio from user {user_name} in chat {chat_id} to MP3 format in {mp3_file_path}.")

	_logger.normal(f"\t\tReading in OGG file {ogg_file_path}...")
	try:
		ogg_audio = AudioSegment.from_ogg(ogg_file_path)
	except Exception as e:
		_logger.error(f"Error reading OGG audio: {e}")
		_logger.error(traceback.format_exc())  # This will log the full traceback of the exception

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
		_report_error(conversation, update.message,
					  f"In handle_audio(), transcribeAudio() threw an exception: {type(e).__name__} {e}")

		text = f"[Audio transcription error: {e}]"
		# We could also do a traceback here. Should we bother?

	_logger.normal(f'\tUser {user_name} said: "{text}"')

	# Store the text in the audio_text attribute of the message object for later reference.
	context.user_data['audio_text'] = text

	return False	# Do this so we continue processing message handlers.
		# (We still need to do the normal handle_message() handler!)
#__/


# Now, let's define a function to handle the rest of the messages.
def handle_message(update, context):
		# Note that <context>, in this context, denotes the Telegram context object.
	"""Process a message."""

	if update.message is None:
		_logger.error("Null message received from unknown user; ignoring...")
		return False

	user_name = _get_user_name(update.message.from_user)

	# Get the chat ID.
	chat_id = update.message.chat.id

	# Make sure the thread component is set to this application (for logging).
	logmaster.setComponent(_appName)

	# Assume we're in a thread associated with a conversation.
	# Set the thread role to be "Conv" followed by the last 4 digits of the chat_id.
	logmaster.setThreadRole("Conv" + str(chat_id)[-4:])

	# Attempt to ensure the conversation is loaded; if we failed, bail.
	if not _ensure_convo_loaded(update, context):
		return False

	# If the message contained audio or voice, then represent it using an
	# appropriate text format.

	if 'audio_text' in context.user_data:	# We added this earlier if appropriate.

		# Utilize the transcript created by handle_audio() above.
		text = f"(audio) {context.user_data['audio_text']}"	

		# Append the text caption, if present.
		if update.message.caption:
			text += f"\n(update.message.caption)"

		# Save the text in the update.message object for later reference.
		update.message.text = text

		# Clear the audio_text entry from the user_data dictionary
		del context.user_data['audio_text']

	# If this is a group chat and the message text is empty or None,
	# assume we were just added to the chat, and just delegate to the handle_start() function.
	if chat_id < 0 and (update.message.text is None or update.message.text == ""):
		_logger.normal(f"Added to group chat {chat_id} by user {user_name}. Auto-starting.")
		update.message.text = '/start'
		handle_start(update,context)
		return True

	if update.message.text is None:
		update.message.text = "[null message]"

	conversation = context.chat_data['conversation']

	# Add the message just received to the conversation.
	conversation.add_message(Message(user_name, update.message.text))

	# Check whether the user is in our access list.
	if not _check_access(user_name):
		_logger.normal(f"User {user_name} tried to access chat {chat_id}, but is not in the access list. Denying access.")

		#errMsg = f"Sorry, but user {user_name} is not authorized to access {BOT_NAME} bot."
		errMsg = f"Sorry, but {BOT_NAME} bot is offline for now due to cost reasons."

		try:
			update.message.reply_text(f"[SYSTEM: {errMsg}]")
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")

		# Also record the error in our conversation data structure.
		conversation.add_message(Message(SYS_NAME, errMsg))
		return False

	# If the currently selected engine is a chat engine, we'll dispatch the rest
	# of the message processing to a different function that's specialized to use 
	# OpenAI's new chat API.
	if gptCore.isChat:
		return process_chat_message(update, context)

	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#|	At this point, we know that we're using a standard GPT-3 engine, and we 
	#|	need to query the API with the updated context and process its response.
	#|	We do this inside a while loop, because we may need to retry the query 
	#|	if the response is empty or is a repeat of a message that the bot 
	#|	already sent earlier. Also, we use the loop to allow the AI to generate 
	#|	longer outputs by accumulating results from multiple queries. (However, 
	#|	we need to be careful in this process not to exceed the available space
	#|	the AI's receptive field.)
	#|
	#|	NOTE: At present, the below algorithm to allow the AI to extend its 
	#|	response and generate longer outputs includes no limit on the length
	#|	of the generated message until the point where it's the only message
	#|	remaining on the receptive field. This may not be desirable, since the
	#|	AI will lose all prior context in the conversation if it generates a
	#|	sufficiently long message. Thus, we may want to add a limit on the 
	#|	length of the generated message at some point in the future.
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
				completion = gptCore.genCompletion(context_string)
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
				except ConversationError:
					# We can't expunge the oldest message.	We'll just treat the full response as the final response.
					# Also make a note that the size of the response has been maxed out.
					response_text = full_response
					response_maxed_out = True
					break
				
				# We've successfully expunged the oldest message.  We need to try again.
				continue
		
			except RateLimitError as e:	# This also may indicate that the server is overloaded or our monthly quota was exceeded.

				# We exceeded our OpenAI API quota or rate limit, or the server was overloaded.
				# There isn't really anything we can do here except send a diagnostic message to the user.

				_logger.error(f"Got a {type(e).__name__} from OpenAI ({e}) for conversation {chat_id}.")

				DIAG_MSG = "[DIAGNOSTIC: AI model is overloaded; please try again later.]"
				try:
					update.message.reply_text(DIAG_MSG)

				except BadRequest or Unauthorized or ChatMigrated as e:
					_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
					return False	# No point in the below.
				
				# This allows the AI to see this diagnostic message too.
				conversation.add_message(Message(SYS_NAME, DIAG_MSG))

				return False	# That's all she wrote.

		# Unless the total response length has just maxed out the available space,
		# if we get here, then we have a new chunk of response from GPT-3 that we
		# need to process.
		if not response_maxed_out:

			# When we get here, we have successfully obtained a response from GPT-3.
			# At this point, we need to either construct a new Message object to
			# hold the response, or extend the existing one.
			if not extending_response:
				# We're starting a new response.

				# Generate a debug-level log message to indicate that we're starting a new response.
				_logger.debug(f"Starting new response from {conversation.bot_name} with text: [{response_text}].")

				# Create a new Message object and add it to the conversation, but, don't finalize it yet.
				response_message = Message(conversation.bot_name, response_text)
				conversation.add_message(response_message, finalize=False)

			else:
				# We're extending an existing response.

				# Generate a debug-level log message to indicate that we're extending an existing response.
				_logger.debug(f"Extending response from {conversation.bot_name} with additional text: [{response_text}].")

				# Extend the existing response.
				response_message.text += response_text

				# Add the response to the existing Message object.
				conversation.extend_message(response_message, response_text)

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
				try:
					update.message.reply_text("[DIAGNOSTIC: Length limit reached; extending response.]")
					# Note that this message doesn't get added to the conversation, so it won't be
					# visible to the AI, only to the user.
				except BadRequest or Unauthorized or ChatMigrated as e:
					_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
					return False

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
			# Send the user a diagnostic message indicating that the response was empty.
			# (Doing this temporarily during development.)
			try:
				update.message.reply_text("[DIAGNOSTIC: Response was empty.]")
			except BadRequest or Unauthorized or ChatMigrated as e:
				_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; ignoring.")
			
				# Note that this message doesn't get added to the conversation, so it won't be
				# visible to the AI, only to the user.
			return True		# This means the bot is simply not responding to this particular message.

		# Update the message object, and the context.
		response_message.text = response_text
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
		if response_text.lower() != '/pass' and conversation.is_repeated_message(response_message):

			# Generate an info-level log message to indicate that we're suppressing the response.
			_logger.info(f"Suppressing response [{response_text}]; it's a repeat.")

			# Delete the last message from the conversation.
			conversation.delete_last_message()

			## Send the user a diagnostic message (doing this temporarily during development).
			#try:
			#	update.message.reply_text(f"[DIAGNOSTIC: Suppressing response [{response_text}]; it's a repeat.]")
			#	# Note that this message doesn't get added to the conversation, so it won't be
			#	# visible to the AI, only to the user.
			#except BadRequest or Unauthorized or ChatMigrated as e:
			#	_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; ignoring.")
			#
			#return True		# This means the bot is simply not responding to the message

		# If we get here, then we have a non-empty message that's also not a repeat.
		# It's finally OK at this point to archive the message and send it to the user.

		# Make sure the response message has been finalized (this also archives it).
		conversation.finalize_message(response_message)

		# At this point, we can break out of the loop and actually send the message.
		break
	#__/ End of while loop that continues until we finish accumulating response text.

	# If we get here, we have finally obtained a non-empty, non-repeat,
	# already-archived message that we can go ahead and send to the user.
	# We also check to see if the message is a command line.

	return process_response(update, context, response_message)	   # Defined just below.

#__/ End of handle_message() function definition.


def _isBlocked(user:str):
	
	# Get the value of environment variable AI_DATADIR.
	# This is where we'll look for the block list files.
	ai_datadir = os.getenv('AI_DATADIR')
	
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


def _blockUser(user):
	
	ai_datadir = os.getenv('AI_DATADIR')

	block_list = []

	bcl_file = os.path.join(ai_datadir, 'bcl.json')
	if os.path.exists(bcl_file):
		with open(bcl_file, 'r') as f:
			block_list = json.load(f)
	
	if user in block_list:
		_logger.error(f"_blockUser(): User {user} is already blocked. Ignoring.")

	block_list.append(user)
	with open(bcl_file, 'w') as f:
		json.dump(block_list, f)
	

def send_image(update, context, desc, save_copy=True):
	"""Generates an image from the given description and sends it to the user.
		Also archives a copy on the server unless save_copy=False is specified."""

	# Get the message's chat ID.
	chat_id = update.message.chat.id

	# Get our preferred name for the user.
	username = _get_user_name(update.message.from_user)

	# Get our Conversation object.
	conversation = context.chat_data['conversation']

	_logger.info(f"Generating image for user {username} from description [{desc}]...")

	# Use the OpenAI API to generate the image.
	try:
		image_url = genImage(desc)
	except Exception as e:
		_report_error(conversation, update.message,
					  f"In send_image(), genImage() threw an exception: {type(e).__name__} ({e})")

		# We could also do a traceback here. Should we bother?
		raise

	_logger.info(f"Downloading generated image from url [{image_url}]...")

	# Download the image from the URL
	response = requests.get(image_url)
	response.raise_for_status()
	
	# Save the image to the filesystem if the flag is set to True
	if save_copy:
		_logger.info(f"Saving a copy of the generated image to the filesystem...")
		image_dir = os.path.join(os.getenv('AI_DATADIR'), 'images')
		if not os.path.exists(image_dir):
			os.makedirs(image_dir)
		image_save_path = os.path.join(image_dir, f'{username}--{desc}.png')
		with open(image_save_path, 'wb') as image_file:
			image_file.write(response.content)
		_logger.normal(f"\tImage saved to {image_save_path}.")

	_logger.info(f"Sending generated image to user {username}...")

	# Prepare the image to be sent via Telegram
	image_data = InputFile(response.content)
	
	# Send the image as a reply in Telegram
	try:
		update.message.reply_photo(photo=image_data)
	except BadRequest or Unauthorized or ChatMigrated as e:
		_logger.error(f"Got a {type(e).__name__} exception from Telegram "
					  "({e}) for conversation {chat_id}; aborting.")
		return


def send_response(update, context, response_text):
	
	chat_id = update.message.chat.id

	# Now, we need to send the response to the user. However, if the response is
	# longer than the maximum allowed length, then we need to send it in chunks.
	# (This is because Telegram's API limits the length of messages to 4096 characters.)

	MAX_MESSAGE_LENGTH = 4096	# Maximum length of a message. (Telegram's API limit.)
		# NOTE: Somwhere I saw that 9500 was the maximum length of a message, but I don't know
		#	which is the correct maximum.

	while len(response_text) > MAX_MESSAGE_LENGTH:

		try:
			update.message.reply_text(response_text[:MAX_MESSAGE_LENGTH])
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
			return
			# Note: Eventually we need to do something smarter here -- like, if we've been
			# banned from replying in a group chat or something, then leave it.
			
		response_text = response_text[MAX_MESSAGE_LENGTH:]

	try:
		update.message.reply_text(response_text)
	except BadRequest or Unauthorized or ChatMigrated as e:
		_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
		return
		# Note: Eventually we need to do something smarter here -- like, if we've been
		# banned from replying in a group chat or something, then leave it.


def process_response(update, context, response_message):

	chat_id = update.message.chat.id
	user_name = _get_user_name(update.message.from_user)
	conversation = context.chat_data['conversation']
	response_text = response_message.text

	# First, check to see if the AI typed the '/pass' command, in which case we do nothing.
	if response_text.lower() == '/pass':
		_logger.info(f"NOTE: The AI is passing its turn in conversation {chat_id}.")
		return True

	# Temporary code to suppress usage.
	#N = 5
	#ALERT_MSG = "***System notification*** This free bot will be taken offline very soon for cost reasons. You need to find another solution for your chatbot needs."
	#if user_name != "Seii1998" and random.randint(1, N) == 1:
	#	try:
	#		update.message.reply_text(ALERT_MSG)
	#	except BadRequest or Unauthorized or ChatMigrated as e:
	#		_logger.error(f"Got a {type(e).__name__} from Telegram ({e}) for conversation {chat_id}; aborting.")
	#		return
	#	conversation.add_message(Message(SYS_NAME, ALERT_MSG))

	# Finally, we check to see if the AI's message is a command line; that is, if it starts with '/'
	# followed by an identifier (e.g., '/remember'). If so, we'll process it as a command.
	if response_text[0] == '/':
		# Extract the command name from the message.
		# We'll do this with a regex that captures the command name, and then the rest of the message.
		# But first, we'll capture just the first line of the message, followed by the rest.

		# Split the text into lines
		lines = response_text.splitlines()

		# Get the first line
		first_line = lines[0]

		# Get the remaining text by joining the rest of the lines
		remaining_text = '\n'.join(lines[1:])

		match = re.match(r"^/(\S+)(?:\s+(.*))?$", first_line)

		command_name = command_args = None
		if match is not None:
			groups = match.groups()
			command_name = groups[0]
			if len(groups) > 1:
				command_args = groups[1]

		# Now, we'll process the command.

		# NOTE: We can't just call the existing command handlers directly, because they
		# are designed for commands issued by the user, not by the AI. So, we'll have to
		# process the commands ourselves to handle them correctly.

		# Check to see if the AI typed the '/remember' command.
		if command_name == 'remember':
			# This is a command to remember something.

			if command_args == None:
				_logger.error(f"The AI sent a /remember command with no argument in conversation {chat_id}.")
				DIAG_MSG = "[DIAGNOSTIC: /remember command needs an argument.]"
				try:
					update.message.reply_text(DIAG_MSG)
				except BadRequest or Unauthorized or ChatMigrated as e:
					_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
					return False

				# Record the diagnostic for the AI also.
				conversation.add_message(Message(SYS_NAME, DIAG_MSG))
				
				return False

			# Tell the conversation object to add the given message to the AI's persistent memory.
			if not conversation.add_memory(command_args):
				
				errmsg = _lastError

				# Generate an error-level report to include in the application log.
				_logger.error(f"The AI tried & failed to add memory: [{command_args}]")
	
				diagMsg = f"[DIAGNOSTIC: Could not add [{command_args}] to persistent memory. " \
						  f"Error message was: \"{errmsg}\"]\n"

				# Send the diagnostic message to the user.
				try:
					update.message.reply_text(diagMsg)
				except BadRequest or Unauthorized or ChatMigrated as e:
					_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
					return False
			
				# Add the diagnostic message to the conversation.
				conversation.add_message(Message(SYS_NAME, diagMsg))
		
				return False

			_logger.info(f"The AI added [{command_args}] to persistent memory in conversation {chat_id}.")

			# Also notify the user that we're remembering the given statement.
			DIAG_MSG = f"[DIAGNOSTIC: Added [{command_args}] to persistent memory.]"
			try:
				update.message.reply_text(DIAG_MSG)
			except BadRequest or Unauthorized or ChatMigrated as e:
				_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
				return False

			# Record the diagnostic for the AI also.
			conversation.add_message(Message(SYS_NAME, DIAG_MSG))

			return True		# Processed AI's /remember command successfully.
				
		# Check to see if the AI typed the '/forget' command.
		elif command_name == 'forget':
			# This is a command to forget something.

			if command_args == None:
				_logger.error(f"The AI sent a /forget command with no argument in conversation {chat_id}.")
				DIAG_MSG = "[DIAGNOSTIC: /forget command needs an argument.]"
				try:
					update.message.reply_text(DIAG_MSG)
				except BadRequest or Unauthorized or ChatMigrated as e:
					_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
					return False

				# Record the diagnostic for the AI also.
				conversation.add_message(Message(SYS_NAME, DIAG_MSG))
				
				return False

			# Tell the conversation object to remove the given message from the AI's persistent memory.
			# The return value is True if the message was found and removed, and False if it wasn't.
			if conversation.remove_memory(command_args):

				# Log this at INFO level.
				_logger.info(f"The AI removed [{command_args}] from persistent memory in conversation {chat_id}.")

				# Also notify the user that we're forgetting the given statement.
				DIAG_MSG = f"[DIAGNOSTIC: Removed [{command_args}] from persistent memory.]"
				try:
					update.message.reply_text(DIAG_MSG)
				except BadRequest or Unauthorized or ChatMigrated as e:
					_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
					return False
			
				# Record the diagnostic for the AI also.
				conversation.add_message(Message(SYS_NAME, DIAG_MSG))
				
				return True	# Processed AI's /forget command successfully.

			else:
				# Log this at ERROR level.
				_logger.error(f"The AI tried & failed to remove [{command_args}] from persistent memory in conversation {chat_id}.")

				# Also notify the user that we couldn't forget the given statement.
				DIAG_MSG = f'[DIAGNOSTIC: Could not remove [{command_args}] from persistent memory. Error message was: "{_lastError}"]'
				try:
					update.message.reply_text(DIAG_MSG)
				except BadRequest or Unauthorized or ChatMigrated as e:
					_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
					return False

				# Record the diagnostic for the AI also.
				conversation.add_message(Message(SYS_NAME, DIAG_MSG))
				
				return False

		elif command_name == 'block':
			# Adds the current user to the block list.
			
			_logger.warn(f"***ALERT*** The AI is blocking user '{user_name}' in conversation {chat_id}.")

			if _isBlocked(user_name):
				_logger.error(f"User '{user_name}' is already blocked.")
				DIAG_MSG = f'[DIAGNOSTIC: User {user_name} has already been blocked by {BOT_NAME}.]'
			else:
				_blockUser(user_name)
				DIAG_MSG = f'[DIAGNOSTIC: {BOT_NAME} has blocked user {user_name}.]'
			
			try:
				update.message.reply_text(DIAG_MSG)
			except BadRequest or Unauthorized or ChatMigrated as e:
				_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
				return False

			# Record the diagnostic for the AI also.
			conversation.add_message(Message(SYS_NAME, DIAG_MSG))
				
			return True		# Processed AI's /block command successfully.

		elif command_name == 'image':

			# Error-checking for null argument.
			if command_args == None or command_args=="":
				_logger.error(f"The AI sent an /image command with no argument in conversation {chat_id}.")
				DIAG_MSG = "[DIAGNOSTIC: /remember command needs an argument.]"
				try:
					update.message.reply_text(DIAG_MSG)
				except BadRequest or Unauthorized or ChatMigrated as e:
					_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
					return
				# Record the diagnostic for the AI also.
				conversation.add_message(Message(SYS_NAME, DIAG_MSG))
				return False

			# Generate and send an image described by the /image command argument string.
			_logger.normal(f"Generating an image with description [{command_args}] for user '{user_name}' in conversation {chat_id}.")
			send_image(update, context, command_args)

			# Send the remaining text after the command line, if any, as a normal message.
			if remaining_text != '':
				send_response(update, context, remaining_text)

			return True		# Processed AI's /image command successfully.

		else:
			# This is a command type that we don't recognize.
			_logger.info(f"AI {BOT_NAME} entered an unknown command [/{command_name}] in chat {chat_id}.")
			# Send the user a diagnostic message.
			DIAG_MSG = f"[DIAGNOSTIC: Unknown command [/{command_name}].]"
			try:
				update.message.reply_text(DIAG_MSG)
			except BadRequest or Unauthorized or ChatMigrated as e:
				_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
				return False

			# Record the diagnostic for the AI also.
			conversation.add_message(Message(SYS_NAME, DIAG_MSG))
				
			return False

	else: # Response was not a command. Treat it normally.

		# Just send our response to the user as a normal message.
		send_response(update, context, response_text)

	# One more thing to do here: If the AI's response ends with the string "(cont)" or "(cont.)"
	# or "(more)" or "...", then we'll send a message to the user asking them to continue the 
	# conversation.
	if response_text.endswith("(cont)") or response_message.text.endswith("(cont.)") or \
	   response_text.endswith("(more)") or response_message.text.endswith("..."):
		try:
			update.message.reply_text("[If you want me to continue my response, type '/continue'.]")
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; ignoring.")
			return False

	return True		# Processed AI's response successfully.

#__/ End of process_response() function definition.


def process_chat_message(update, context):

	"""We dispatch to this function to process messages from the user
		if our selected engine is for OpenAI's chat endpoint."""
	
	global maxRetToks

	chat_id = update.message.chat.id

	# Get our Conversation object.
	conversation = context.chat_data['conversation']

	# This loop will call the API with exception handling.
	#	If we get a PromptTooLongException, we'll try again with a shorter prompt.
	#	If we get a RateLimitError, we'll emit a diagnostic reponse message.

	while True:		# Loop until we get a response from the API.

		# Construct the message list in the format expected by the GPT-3 chat API.
		chat_messages = conversation.get_chat_messages()

		# At this point, we want to archive the chat messages to a file in the
		# log/ directory called 'latest-messages.txt'. This provides an easy way
		# for the system operator to monitor what the AI is actually seeing, without
		# having to turn on debug-level logging and search through the log file.

		# Open the file for writing.
		with open(f"{LOG_DIR}/latest-messages.txt", "w") as f:
			for chat_message in chat_messages:

				f.write(messageRepr(chat_message))
				
				#if 'role' in chat_message:
				#	roleOrName = chat_message['role']
				## Note 'name' overrides 'role' if both are present.
				#if 'name' in chat_message:
				#	roleOrName = chat_message['name']
				#
				#f.write(f"{roleOrName}: {chat_message['content']}\n")  # Write the message to the file.

		# Also do a json dump
		with open(f"{LOG_DIR}/latest-messages.json", "w") as outfile:
			json.dump(chat_messages, outfile)

		# Now we'll try actually calling the API.
		try:

			# Calculate what value of the maxLength parameter to use; this 
			# controls the size of the response window, i.e., the maximum
			# length of the reponse returned by the core, in tokens. This
			# is set to the available space in the context window, but 
			# capped by the aiConf.maxReturnedTokens parameter (from the
			# api-conf/max-returned-tokens element in glados-config.hjson
			# or ai-config.hjson) and no less than the aiConf.minReplyWinToks
			# parameter (from the mind-conf/min-replywin-toks element in
			# ai-config.hjson).

			# Figure out how much space is left in the context window currently.
			# We'll do this by subtracting the length of the chat messages from 
			# the context window size.

			# Get the context window size from the gptCore object.
			contextWinSizeToks = gptCore.fieldSize

			# The +1 seems true in practice, except for GPT-4. Not sure why.
			if ENGINE_NAME != 'gpt-4':
				contextWinSizeToks += 1

			_logger.debug(f"In process_chat_message(), contextWinSizeToks={contextWinSizeToks}.")

			# Get the length of the chat messages in tokens.
			msgsSizeToks = ChatMessages(chat_messages).totalTokens(model=ENGINE_NAME)

			_logger.debug(f"In process_chat_message(), msgsSizeToks={msgsSizeToks}.")

			# Calculate the available space in the context window.
			availSpaceToks = contextWinSizeToks - msgsSizeToks
				# Note this is an estimate of the available space, because
				# the actual space available may be less than this if the
				# chat messages at the back end contain any additional 
				# formatting tokens or extra undocumented fields.

			_logger.debug(f"In process_chat_message(), availSpaceToks={availSpaceToks}.")

			# Remember: maxRetToks, minReplyWinToks were already
			# retrieved from the aiConf object and stored in globals
			# early in this module.

			# Here we're setting a local variable from the global.
			if maxRetToks is None:	# In the chat API, this becomes inf.
				lMaxRetToks = float('inf')	# So in other words, no limit.
			else:
				lMaxRetToks = maxRetToks

			_logger.debug(f"In process_chat_message(), lMaxRetToks={lMaxRetToks}.")

			# If the available space is in between minReplyWinToks and
			# lMaxRetToks, then just set maxTokens=inf (i.e., tell the API
			# to use all the available space). Otherwise, calculate the
			# value of maxTokens in the same way we used to do it.

			if minReplyWinToks <= availSpaceToks and availSpaceToks <= lMaxRetToks:
				maxTokens = None	# No maximum; i.e., infinity; i.e., use all
					# of the available space.
			else:
				# Calculate the actual maximum length of the returned reponse
				# in tokens, given all of our constraints above.
				maxTokens = max(minReplyWinToks, min(lMaxRetToks, availSpaceToks))
					# Explanation: maxTokens is the amount of space that will
					# be made available to the AI core for its response. This
					# should not be less than the AI's requested minimum reply
					# window size, and it should be as large as possible, but
					# not more than either the maximum number of tokens that
					# the AI is allowed to return, or the amount of space that
					# is actually available right now in the AI's context window.

			_logger.debug(f"In process_chat_message(), maxTokens={maxTokens}.")

			# Temporary hack to see if we can max out the output length.
			#maxTokens = None	# Equivalent to float('inf')?

			_logger.debug(f"process_chat_message(): maxTokens = {maxTokens}, minReplyWinToks = {minReplyWinToks}, maxRetToks = {maxRetToks}, lMaxRetToks = {lMaxRetToks}, availSpaceToks = {availSpaceToks}")

			# Get the response from GPT-3, as a ChatCompletion object.
			chatCompletion = gptCore.genChatCompletion(	# Call the API.
				
				maxTokens=maxTokens,	# Max. number of tokens to return.
					# We went to a lot of trouble to set this up properly above!

				messages=chat_messages,		# Current message list for chat API.
					# Note that since we pass in an explicit messages list, this 
					# overrides whatever api.Messages object is being maintained 
					# in the GPT3ChatCore object.

				minRepWin=minReplyWinToks	# Min. reply window size in tokens.
					# This parameter gets passed through to the ChatCompletion()
					# initializer and thence to ChatCompletion._createComplStruct(),
					# which does the actual work of retrieving the raw completion
					# structure from the OpenAI API. Note that this parameter is 
					# necessary because our computed maxTokens value may be greater
					# than the actual available space in the context window (either
					# because our estimate was wrong, or because we simply 
					# requested a minimum space larger than is available). In the 
					# latter case, getChatCompletion() should notice this & throw a 
					# PromptTooLargeException, which we'll catch below. If our 
					# estimate was wrong, then the actual reply window size could be
					# less than the minimum requested size, but as long as our 
					# estimates were pretty close, the difference will be small, and 
					# the AI should still be able to generate a reasonable response.

			)
			response_text = chatCompletion.text

			break	# We got a response, so we can break out of the loop.

		except PromptTooLargeException:				# Imported from gpt3.api module.

				# The prompt (constructed internally at the remote API back-end) is too long.  
				# Thus, we need to expunge the oldest message from the conversation.

			conversation.expunge_oldest_message()
				# NOTE: If it succeeds, this modifies conversation.context_string.

			# We've successfully expunged the oldest message.
			continue	# Loop back and try again.

		except RateLimitError as e:	# This also may indicate that the server is overloaded or our monthly quota was exceeded.

			# We exceeded our OpenAI API quota, or we've exceeded the rate limit 
			# for this model. There isn't really anything we can do here except 
			# send a diagnostic message to the user.

			_logger.error(f"Got a {type(e).__name__} from OpenAI ({e}) for conversation {chat_id}.")

			DIAG_MSG = "[DIAGNOSTIC: AI model is overloaded; please try again later.]"
			try:
				update.message.reply_text(DIAG_MSG)

			except BadRequest or Unauthorized or ChatMigrated as e:
				_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; aborting.")
				return False	# No point in the below.
				
			# This allows the AI to see this diagnostic message too.
			conversation.add_message(Message(SYS_NAME, DIAG_MSG))

			return False	# That's all she wrote.

		# Stuff from Copilot:
		#
		# except PromptTooLongException as e:
		#	  # The prompt was too long, so we need to shorten it.
		#	  # First, we'll log this at the INFO level.
		#	  _logger.info(f"Prompt too long; shortening it.")
		#	  # Then, we'll shorten the prompt and try again.
		#	  conversation.shorten_prompt()
		#	  continue
		# except RateLimitException as e:
		#	  # We've hit the rate limit, so we need to wait a bit before trying again.
		#	  # First, we'll log this at the INFO level.
		#	  _logger.info(f"Rate limit exceeded; waiting {e.retry_after} seconds.")
		#	  # Then, we'll wait for the specified number of seconds and try again.
		#	  time.sleep(e.retry_after)
		#	  continue

		# This was also suggested by Copilot; we'll go ahead and use it.
		except Exception as e:
			# We've hit some other exception, so we need to log it and send a diagnostic message to the user.
			# (And also add it to the conversation so the AI can see it.)
			
			_report_error(conversation, update.message, f"Exception while getting response: {type(e).__name__} ({e})")

			return False

	# If we get here, we've successfully gotten a response from the API.

	# Generate a debug-level log message to indicate that we're starting a new response.
	_logger.debug(f"Creating new response from {conversation.bot_name} with text: [{response_text}].")

	# Create a new Message object and add it to the conversation.
	response_message = Message(conversation.bot_name, response_text)
	conversation.add_message(response_message)

	# Strip off any leading or trailing whitespace (Telegram won't display it anyway.).
	response_text = response_text.strip()

	# If the response is empty, then return early. (Can't even send an empty message anyway.)
	if response_text == "":

		_logger.warn("Got an empty response! Ignoring...")

		# Delete the last message from the conversation.
		conversation.delete_last_message()
		# Send the user a diagnostic message indicating that the response was empty.
		# (Doing this temporarily during development.)
		try:
			update.message.reply_text("[DIAGNOSTIC: Response was empty.]")
			# Note that this message doesn't get added to the conversation, so it won't be
			# visible to the AI, only to the user.
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; ignoring.")
			
		return True		# This means the bot is simply not responding to this particular message.
	
	# Update the message object, and the context.
	response_message.text = response_text
	conversation.expand_context()	 

	# If this message is already in the conversation, then we'll suppress it, so as
	# not to exacerbate the AI's tendency to repeat itself.	 (So, as a user, if you 
	# see that the AI isn't responding to a message, this may mean that it has the 
	# urge to repeat something it said earlier, but is holding its tongue.)
	if response_text.lower() != '/pass' and conversation.is_repeated_message(response_message):

		# Generate an info-level log message to indicate that we're suppressing the response.
		_logger.info(f"Suppressing response [{response_text}]; it's a repeat.")

		# Delete the last message from the conversation.
		conversation.delete_last_message()

		## Send the user a diagnostic message (doing this temporarily during development).
		#try:
		#	update.message.reply_text(f"[DIAGNOSTIC: Suppressing response [{response_text}]; it's a repeat.]")
		#	# Note that this message doesn't get added to the conversation, so it won't be
		#	# visible to the AI, only to the user.
		#except BadRequest or Unauthorized or ChatMigrated as e:
		#	_logger.error(f"Got a {type(e).__name__} exception from Telegram ({e}) for conversation {chat_id}; ignoring.")
		
		return True		# This means the bot is simply not responding to the message

	# If we get here, then we have a non-empty message that's also not a repeat.
	# It's finally OK at this point to archive the message and send it to the user.

	# Make sure the response message has been finalized (this also archives it).
	conversation.finalize_message(response_message)

	# If we get here, we have finally obtained a non-empty, non-repeat,
	# already-archived message that we can go ahead and send to the user.
	# We also check to see if the message is a command line.

	return process_response(update, context, response_message)	   # Defined above.

#__/ End of process_chat_message() function definition.


def handle_unknown_command(update, context) -> None:
	"""Handle an attempted user command that doesn't match any of the known
		command types. We do this by just treating the command like a normal
		text message and letting the AI decide how to handle it."""

	handle_message(update, context)		# Treat it like a normal message.

#__/ End of handle_unknown_command() function definition.


def _report_error(convo:Conversation, telegramMessage,
				 errMsg:str, logIt:bool=True,
				 showAI:bool=True, showUser:bool=True):

	"""Report a given error response to a Telegram message. Flags
		<logIt>, <showAI>, <showUser> control where the error is
		reported."""

	chat_id = convo.chat_id

	if logIt:
		# Record the error in the log file.
		_logger.error(errMsg, exc_info=logmaster.doDebug)
			# The exc_info option includes a stack trace if we're in debug mode.

	# Compose formatted error message.
	msg = f"[ERROR: {errMsg}]"

	if showUser:
		# Show the error message to the user.
		try:
			telegramMessage.reply_text(msg)
		except BadRequest or Unauthorized or ChatMigrated as e:
			_logger.error(f"Got a {type(e).__name__} exception from Telegram "
						  "({e}) for conversation {chat_id}; aborting.")
			return

	if showAI:
		# Add the error message to the conversation.
		convo.add_message(Message(SYS_NAME, msg))

#__/ End private function _report_error().


# Define an error handler for exceptions caught by the dispatcher.
def error(update, context):
	"""Log errors caused by updates."""
	_logger.warning('Update "%s" caused error "%s"', update, context.error)


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

# Command list to enter into BotFather.
COMMAND_LIST = f"""
start - Starts bot; reloads conversation history.
help - Displays general help and command help.
reset - Clears the bot's conversation memory.
echo - Echoes back the given text.
greet - Make server send a greeting.
"""
# No longer supported for random users:
#  remember - Adds the given statement to the bot's persistent context data.
#  forget - Removes the given statement from the bot's persistent context data.

print("NOTE: You should enter the following command list into BotFather at bot creation time:")
print(COMMAND_LIST)

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

# Next, we need to register the command handlers.
dispatcher.add_handler(CommandHandler('start',		handle_start),		group = 0)
dispatcher.add_handler(CommandHandler('help',		handle_help), 		group = 0)
dispatcher.add_handler(CommandHandler('remember',	handle_remember),	group = 0)
dispatcher.add_handler(CommandHandler('forget',		handle_forget),		group = 0)
dispatcher.add_handler(CommandHandler('reset',		handle_reset),		group = 0)

# The following two commands are not really needed at all. They're just here for testing purposes.
dispatcher.add_handler(CommandHandler('echo',	handle_echo),	group = 0)
dispatcher.add_handler(CommandHandler('greet',	handle_greet),	group = 0)

# In case user sends an audio message, we add a handler to save the audio in a file for later processing.
# This handler should then return FALSE so that subsequent message processing will still happen.
dispatcher.add_handler(MessageHandler(Filters.audio|Filters.voice, handle_audio), group = 1)

# Now, let's add a handler for the rest of the messages.
dispatcher.add_handler(MessageHandler((Filters.text|Filters.audio|Filters.voice) & ~Filters.command, handle_message), group = 2)

# Also, if any commands make it this far, we'll process them like normal messages (let the AI decide what to do).

class UnknownCommandFilter(BaseFilter):

	def __call__(self, update, *args, **kwargs) -> bool:
		text = update.message.text
		defined_commands = ['/start', '/help', '/remember', '/forget', '/reset', '/echo', '/greet']
		
		if text is None:
			return False
		if text.startswith('/') and text.split()[0] not in defined_commands:
			return True
		return False

unknown_command_filter = UnknownCommandFilter()

dispatcher.add_handler(MessageHandler(unknown_command_filter, handle_unknown_command), group = 3)

# Add an error handler to catch the Unauthorized exception & other errors that may occur.
dispatcher.add_error_handler(error)

# Now, let's run the bot. This will start polling the Telegram servers for new updates.
# It runs in the background, so after we start it, we call idle() so we won't exit early.
updater.start_polling()
updater.idle()

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
