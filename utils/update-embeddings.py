import sqlite3
import numpy as np
import pickle

import openai
import backoff

# Function to get embeddings as a list. Based on OpenAI's example.
EMBEDDING_MODEL = "text-embedding-ada-002"
@backoff.on_exception(backoff.expo, Exception, max_tries=6)
def _getEmbedding(text: str, engine=EMBEDDING_MODEL, **kwargs) -> list:

    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    return openai.Embedding.create(input=[text], engine=engine, **kwargs)\
		["data"][0]["embedding"]


# Function to get new embeddings from the text
def _getNewEmbedding(text):
    """Gets a new embedding of a text."""

    # Get the response from OpenAI Embeddings API. Returns a vector.
    embedding_asList = _getEmbedding(text)

    # Convert the embedding list to a numpy array and pickle it
    embedding_np = np.array(embedding_asList)
    embedding_pickle = pickle.dumps(embedding_np, protocol=pickle.HIGHEST_PROTOCOL)

    return embedding_pickle

# Function to update the embeddings in the database
def updateEmbeddings():
    # Fetch all items
    c.execute("SELECT * FROM remembered_items")
    rows = c.fetchall()

    # Update each item
    for row in rows:
        itemID, userID, chatID, public, global_, itemText, embedding_blob = row
        new_embedding_pickle = _getNewEmbedding(itemText)

        # Update the item in the database
        c.execute("""
            UPDATE remembered_items
            SET embedding_blob = ?
            WHERE itemID = ?
        """, (new_embedding_pickle, itemID))

    # Commit the changes
    conn.commit()
#__/

# Main body follows.

conn = sqlite3.connect('bot-db.sqlite')
c = conn.cursor()

updateEmbeddings()

conn.close()
