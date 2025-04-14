import sqlite3
import os
import uuid
from datetime import datetime

# Use a database file named 'database.db'. You can override this with the environment variable SQLITE_DB.
db_path = os.environ.get("SQLITE_DB", "database.db")
# Set check_same_thread=False if you plan to use the connection in different threads (for example, in a web app)
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

def init_db():
    # Create the 'users' table.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY
        )
    ''')
    # Create the 'collections' table.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            collection_id TEXT PRIMARY KEY,
            user_id TEXT,
            name TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    # Create the 'chat_history' table.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY(collection_id) REFERENCES collections(collection_id)
        )
    ''')
    conn.commit()

# Initialize the database tables.
init_db()

def makeUser(user_id):
    # Check if the user exists.
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
        conn.commit()
        print(f"User {user_id} created in database.")
    else:
        print(f"User {user_id} found in database.")

def add_collection(user_id, collection_name):
    # Generate a unique collection ID.
    collection_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO collections (collection_id, user_id, name) VALUES (?, ?, ?)",
        (collection_id, user_id, collection_name)
    )
    conn.commit()
    return collection_id

def delete_collection(user_id, collection_id):
    # Delete the collection only if it belongs to the specified user.
    cursor.execute(
        "DELETE FROM collections WHERE collection_id = ? AND user_id = ?",
        (collection_id, user_id)
    )
    # Also remove any associated chat history.
    cursor.execute(
        "DELETE FROM chat_history WHERE collection_id = ?",
        (collection_id,)
    )
    conn.commit()

def get_collections(user_id):
    cursor.execute(
        "SELECT collection_id, name FROM collections WHERE user_id = ?",
        (user_id,)
    )
    results = cursor.fetchall()
    # Format the rows as a list of dictionaries.
    return [{"collectionId": row[0], "name": row[1]} for row in results]

def add_message(user_id, collection_id, role, content):
    # Verify that the collection belongs to the user.
    cursor.execute(
        "SELECT collection_id FROM collections WHERE collection_id = ? AND user_id = ?",
        (collection_id, user_id)
    )
    if not cursor.fetchone():
        print("Collection not found for user.")
        return
    # Create a new message with an ISO-formatted UTC timestamp.
    timestamp = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO chat_history (collection_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (collection_id, role, content, timestamp)
    )
    conn.commit()

def get_chat_history(user_id, collection_id):
    # Confirm that the given collection belongs to the user.
    cursor.execute(
        "SELECT collection_id FROM collections WHERE collection_id = ? AND user_id = ?",
        (collection_id, user_id)
    )
    if not cursor.fetchone():
        return []
    # Retrieve the chat history ordered by insertion.
    cursor.execute(
        "SELECT role, content, timestamp FROM chat_history WHERE collection_id = ? ORDER BY id",
        (collection_id,)
    )
    rows = cursor.fetchall()
    print("The chat history retrieved is: " + str(rows))
    return [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in rows]

# Example usage:
if __name__ == "__main__":
    user_id = "google_user_id_123"
    makeUser(user_id)
    collection_id = add_collection(user_id, "My First Collection")
    add_message(user_id, collection_id, "user", "Hello, LLM!")
    add_message(user_id, collection_id, "assistant", "Hello! How can I help you?")
    history = get_chat_history(user_id, collection_id)
    print("Final chat history:", history)
