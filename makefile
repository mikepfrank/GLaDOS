# Typing 'make' with no arguments will attempt to 
# launch the experimental GladOS server process.
# Other useful rules follow.

default:
	make run-glados

# Run the simple test application.
run-test:
	./run-test.sh

# Launch the experimental GladOS server process.
run-glados:
	./run-server.sh

# Launch the Telegram bot server.
run-bot:
	./runbot.sh

# NOTE: For the below 2 rules to work, user must define 
# environment variable AI_DATADIR to the desired install
# location, such as /opt/AIs/${AI_NAME}, or similar.
# (And /opt/AIs must be writable by the AI's user account.)

data-dir:
	mkdir -p $(AI_DATADIR)

# Install AI's data files (outside of the local git repo).
install-data:
	make data-dir
	cp -r ai-data/* $(AI_DATADIR)

# Should we add a rule to install the current Python source
# tree somewhere too?

# Update the models.json file.
update-models:
	-mv models.json models.json.prev
	make models.json

models.json:
	bash -c "curl https://api.openai.com/v1/models -H 'Authorization: Bearer $(OPENAI_API_KEY)'" > models.json

# Clean up the API stats.
# This effectively resets all stats to 0.
# (May also be needed after engine list changes.
clean-stats:
	rm $(AI_DATADIR)/api-stats.*

help:
	@echo ""
	@echo "The rules in the makefile are:"
	@echo ""
	@echo "    * clean-stats - Zero out the current day's usage stats."
	@echo "    * data-dir - Create the AI's persistent data directory."
	@echo "    * help - Display this help."
	@echo "    * install-data - Install the AI's initial data files."
	@echo "    * models.json - Create models.json if it doesn't exist."
	@echo "    * run-bot - Run the Telegram bot server."
	@echo "    * run-glados (default) - Run the GLaDOS server."
	@echo "    * run-test - Run the simple test application."
	@echo "    * update-models - Update the models.json file."
	@echo ""
