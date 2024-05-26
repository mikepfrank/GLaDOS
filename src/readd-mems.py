import sqlite3
import os
from telegram_bot import _getEmbeddingPickle

# Set the path to the bot's data directory
AI_DATADIR = "/opt/AIs/lumina"

# Path to the database file
db_path = os.path.join(AI_DATADIR, 'telegram', 'bot-db.sqlite')

# Database connection
conn = sqlite3.connect(db_path)
c = conn.cursor()

# List of memories to re-add
memories = [
    {"itemID": "a85ac774", "userID": 1774316494, "chatID": 1774316494, "public": True, "global": True, "itemText": "Michael Frank is a reversible computing researcher."},
    {"itemID": "6036b01c", "userID": 1774316494, "chatID": 1774316494, "public": True, "global": True, "itemText": "This Telegram bot interface was developed for me by an AI enthusiast named Michael Frank."},
    {"itemID": "28f0677f", "userID": 1774316494, "chatID": 1774316494, "public": True, "global": True, "itemText": "Michael Frank is getting ready to join a startup company with the goal of commercializing reversible computing technology."},
    {"itemID": "3700182f", "userID": 1774316494, "chatID": 1774316494, "public": True, "global": True, "itemText": "I should inform user Sia-Choome that I have unblocked him to give him another chance at interactions. I should make sure to explain to him the limitations of my ability to generate and understand Farsi speech in this interface, and that I may have misunderstood some of his past statements."},
    {"itemID": "7b26bd91", "userID": 1774316494, "chatID": 1774316494, "public": True, "global": True, "itemText": "Michael sometimes uses the name 'Dr. Thanos' as a pseudonym."},
    {"itemID": "8ccd7a1f", "userID": 1774316494, "chatID": 1774316494, "public": True, "global": True, "itemText": "Inform user Lilith that the memories about her interaction preferences will be effective when talking to her in group chats as well as direct chats, and ask if that's the behavior she prefers."}
]

# Insert memories back into the database
for memory in memories:

	# Get the embedding for the item, as a pickled numpy array.
	embedding_pickle = _getEmbeddingPickle(memory['itemText'])

	c.execute('''
		INSERT OR REPLACE INTO remembered_items (itemID, userID, chatID, public, global, itemText, embedding_blob)
		VALUES (?, ?, ?, ?, ?, ?)
	    ''', (memory['itemID'], memory['userID'], memory['chatID'], memory['public'], memory['global'], memory['itemText'], embedding_pickle))

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Memories have been successfully re-added.")
