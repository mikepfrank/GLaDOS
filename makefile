# Typing 'make' with no arguments will attempt to 
# launch the experimental GladOS server process.
# Other useful rules follow.

default:
	make run-glados

# Run the test application.
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

data-dir:
	mkdir -p $(AI_DATADIR)

# Install AI's data files outside the local git repo.
install-data:
	make data-dir
	cp -r ai-data/* $(AI_DATADIR)

# Update the models.json file.
update-models:
	$(shell curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" > models.json)

# Clean up the API stats.
clean-stats:
	rm $(AI_DATADIR)/api-stats.*
