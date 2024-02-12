= src/telegram directory =

In this directory, we are going to work on gradually refactoring and
modularizing the Telegram bot code for easier maintainability.

Some ideas for modules to create here:

	 * `message.py` - Defines the BotMessage class to represent a
	 		message in the bot's conversation history.

	 * `conversation.py` - Defines the BotConversation class to
	 		represent the information associated with a given chat.

	* `database.py` - Interface to the bot server's database of
			known users and dynamic persistent memories.

	* `handlers.py` - Defines Telegram event handler functions.

	* `functions.py` - Defines the function call interface that's
			made available to the AI models that support it.

	* `telegram.py` - Defines the interface to Telegram itself.

	* `openai.py` - Defines the interface to the OpenAI library
			and models. (This uses src/gpt3/api.py under the hood.)

	* `memory.py` - Interface to dynamic persistent memory features.

	* `blocking.py` - Interface to block/unblock user features.

	* `web.py` - Interface for web searching and browsing.
			(Note only search is implemented so far.)
