import sqlite3
import os

# Define the database name
db_name = 'email-generation.db'
FILE_STORAGE_PATH = 'file_storage'

# Remove the existing database if it exists
if os.path.exists(db_name):
    os.remove(db_name)
    print(f"Existing database {db_name} removed.")

# Connect to the SQLite database (it will create a new one)
conn = sqlite3.connect(db_name)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create the Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL
)
''')

# Insert a default user 'admin'
cursor.execute('''
INSERT INTO Users (username, password, first_name, last_name)
VALUES ('admin', 'adminpassword', 'Admin', 'User')
''')

# Create the EmailHistory table with the username field
cursor.execute('''
CREATE TABLE IF NOT EXISTS EmailHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    linkedinUrl TEXT NOT NULL,
    userPrompt TEXT NOT NULL,
    selectedDocuments TEXT NOT NULL,
    selectedEmails TEXT NOT NULL,
    generatedEmail TEXT NOT NULL,
    username TEXT NOT NULL
)
''')

# Create necessary directories
os.makedirs(f'{FILE_STORAGE_PATH}/admin', exist_ok=True)
os.makedirs(f'{FILE_STORAGE_PATH}/admin/company_documents', exist_ok=True)
os.makedirs(f'{FILE_STORAGE_PATH}/admin/sample_emails', exist_ok=True)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created, Users table and EmailHistory table created, and default user 'admin' added successfully")
