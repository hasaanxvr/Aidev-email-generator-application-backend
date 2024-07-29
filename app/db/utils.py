import sqlite3

def username_exists(db_name, username):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()


    cursor.execute('SELECT COUNT(*) FROM Users WHERE username = ?', (username,))
    count = cursor.fetchone()[0]


    conn.close()


    return count > 0



def insert_user(db_name, username, password, first_name, last_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Insert a new user into the Users table
    cursor.execute('''
    INSERT INTO Users (username, password, first_name, last_name)
    VALUES (?, ?, ?, ?)
    ''', (username, password, first_name, last_name))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"User '{username}' added successfully")
    
    
    
def login_valid(db_name, username, password):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query to validate the username and password
    cursor.execute('SELECT password FROM Users WHERE username = ?', (username,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    if result is None:
        return False

    stored_password = result[0]
    return stored_password == password