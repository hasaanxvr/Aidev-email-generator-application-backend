import sqlite3
from pymongo import MongoClient, errors

# Parent class for Database
class Database:
    def login_valid(username:str, password:str):
        raise NotImplementedError('The subclasses should implement this function!')
    
    def insert_user(username: str, password: str, first_name: str, last_name: str):
        raise NotImplementedError('The subclasses should implement this function!')
    
    def username_exists(username: str):
        raise NotImplementedError('The subclasses should implement this function!')
    

# For SQLite
class SqliteDatabase(Database):
    def __init__(self):
        self.db_name = 'email-generation.db'
    
    def login_valid(self, username: str, password: str):
        conn = sqlite3.connect(self.db_name)
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

        
    def username_exists(self, username: str):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM Users WHERE username = ?', (username,))
        count = cursor.fetchone()[0]

        conn.close()

        return count > 0
    
    
    def insert_user(self, username: str, password: str, first_name: str, last_name: str):
        conn = sqlite3.connect(self.db_name)
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



# For MongoDB
class MongoDatabase(Database):
    def __init__(self):
        self.connection_string = 'mongodb+srv://admin:admin@email-generation-test.h6h63hm.mongodb.net/email-generation?retryWrites=true&w=majority&appName=email-generation-test'
        
    def login_valid(self, username: str, password: str) -> bool:
        try:
            client = MongoClient(self.connection_string)
            db = client['email-generation']
            collection = db['users']
            query = {'username': username}
            
            user = collection.find_one(query)
            
            if user and user['password'] == password:
                return True
            else:
                return False
        except errors.ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            return False
        except errors.OperationFailure as e:
            print(f"Operation failed: {e}")
            return False
        
    def username_exists(self, username: str) -> bool:
        try:
            client = MongoClient(self.connection_string)
            db = client['email-generation']
            collection = db['users']
            
            query = {'username': username}
            
            user = collection.find_one(query)
            
            return user is not None
        except errors.ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            return False
        except errors.OperationFailure as e:
            print(f"Operation failed: {e}")
            return False
            
    def insert_user(self, username: str, password: str, first_name: str, last_name: str) -> bool:
        try:
            client = MongoClient(self.connection_string)
            db = client['email-generation']
            collection = db['users']
            
            if self.username_exists(username):
                print("Username already exists.")
                return False
            
            user = {
                'username': username,
                'password': password,
                'first_name': first_name,
                'last_name': last_name
            }
            
            collection.insert_one(user)
            return True
        except errors.ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            return False
        except errors.OperationFailure as e:
            print(f"Operation failed: {e}")
            return False