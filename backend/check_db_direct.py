#!/usr/bin/env python3
"""
Direct script to check database tables and their data.
"""
import sqlite3

# Connect to the SQLite database
db_path = "todo_app.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Checking database tables and data...")

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables in database: {[table[0] for table in tables]}")

# Check conversation table if it exists
if 'conversation' in [table[0] for table in tables]:
    print("\n--- Conversation Table ---")
    cursor.execute("SELECT * FROM conversation;")
    conversations = cursor.fetchall()
    print(f"Total conversations: {len(conversations)}")
    for conv in conversations:
        print(f"ID: {conv[0]}, User ID: {conv[1]}, Created: {conv[2]}, Updated: {conv[3]}")

# Check chatmessage table if it exists
if 'chatmessage' in [table[0] for table in tables]:
    print("\n--- ChatMessage Table ---")
    # Get column info
    cursor.execute("PRAGMA table_info(chatmessage);")
    columns = cursor.fetchall()
    print("ChatMessage table structure:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - {col[4]}")

    cursor.execute("SELECT * FROM chatmessage;")
    messages = cursor.fetchall()
    print(f"\nTotal messages: {len(messages)}")
    for msg in messages:
        print(f"Row: {msg}")  # Print the whole row to see the actual structure

conn.close()
print("\nDatabase check completed!")