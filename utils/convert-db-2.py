# convert-db-2.py
# This utility (written by Aria) converts the database from old format to new format.
#
#	-> The old format stored embeddings as comma-separated strings of ASCII floats.
#	-> The new format stores embeddings as blobs of pickled numpy arrays.
#
# The new format takes up <40% as much space as the old one.

import sqlite3
import numpy as np
import pickle

# Function to convert embedding string to pickle
def _embeddingStrToPickle(embedding_str):
    embedding_list = [float(x) for x in embedding_str.split(',')]
    embedding_array = np.array(embedding_list)
    pickled_embedding = pickle.dumps(embedding_array, protocol=pickle.HIGHEST_PROTOCOL)
    return pickled_embedding

# Connect to the database
conn = sqlite3.connect('bot-db.sqlite')
c = conn.cursor()

# Begin a transaction
c.execute('BEGIN TRANSACTION')

# Create new table with the embedding_blob column
c.execute('''
    CREATE TABLE remembered_items_new (
        itemID TEXT PRIMARY KEY,
        userID INTEGER,
        chatID INTEGER,
        public BOOLEAN,
        global BOOLEAN,
        itemText TEXT,
        embedding_blob BLOB
    )
''')

# Fetch data from the old table
c.execute("SELECT * FROM remembered_items")
rows = c.fetchall()

# Copy data from the old table to the new one, converting embeddings
for row in rows:
    itemID, userID, chatID, public, global_, itemText, embedding_str = row
    embedding_pickle = _embeddingStrToPickle(embedding_str)
    c.execute('''
        INSERT INTO remembered_items_new (itemID, userID, chatID, public, global, itemText, embedding_blob)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (itemID, userID, chatID, public, global_, itemText, embedding_pickle))

# Commit changes
conn.commit()

# Drop the old table
c.execute('DROP TABLE remembered_items')

# Rename the new table to the original name
c.execute('ALTER TABLE remembered_items_new RENAME TO remembered_items')

# Commit changes and close connection
conn.commit()
conn.close()
