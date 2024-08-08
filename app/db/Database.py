import sqlite3
from datetime import datetime
from fastapi import HTTPException
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


    def insert_email(self, request_data, username, email):
        # Write to the database
        conn = sqlite3.connect('email-generation.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO EmailHistory (date, linkedinUrl, userPrompt, selectedDocuments, selectedEmails, generatedEmail, username)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                request_data['linkedin_url'],
                request_data['user_prompt'],
                ','.join(request_data['selected_documents']),
                ','.join(request_data['selected_emails']),
                email,
                username
            ))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail='Failed to write to the database') from e
        finally:
            conn.close()
            
            
    def fetch_email (self, username):
        conn = sqlite3.connect('email-generation.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT date, linkedinUrl, userPrompt, selectedDocuments, selectedEmails, generatedEmail
                FROM EmailHistory
                WHERE username = ?
            ''', (username,))
            
            rows = cursor.fetchall()
            
            email_history = []
            for row in rows:
                email_history.append({
                    'date': row[0],
                    'linkedinUrl': row[1],
                    'userPrompt': row[2],
                    'selectedDocuments': row[3],
                    'selectedEmails': row[4],
                    'generatedEmail': row[5]
                })
            
        except Exception as e:
            raise HTTPException(status_code=500, detail='Failed to fetch email history from the database') from e
        finally:
            conn.close()

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
        
        
    
    def insert_email(self, data: dict):
        try:
            client = MongoClient(self.connection_string)
            db = client['email-generation']
            collection = db['email-history']
            
            collection.insert_one(data)
            
        except errors.ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            return False
        except errors.OperationFailure as e:
            print(f"Operation failed: {e}")
            return False
            
            
    def insert_person(self, data: dict):
        try:
            client = MongoClient(self.connection_string)
            db = client['email-generation']
            collection = db['person-data']
            
            collection.insert_one(data)
            
        except errors.ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            return False
        except errors.OperationFailure as e:
            print(f"Operation failed: {e}")
            return False
        
    
    def fetch_emails(self, username: str):
        try:
            client = MongoClient(self.connection_string)
            db = client['email-generation']
            collection = db['email-history']

            query = {'username': username}
            results = collection.find(query, {
                'time': 1,
                'linkedinurl': 1,
                'user_prompt': 1,
                'selected_documents': 1,
                'selected_emails': 1,
                'generated_email': 1,
                '_id': 0  # Exclude the MongoDB _id field from the result
            })

            email_history = []
            for doc in results:
                email_history.append({
                    'date': doc.get('time'),
                    'linkedinUrl': doc.get('linkedinurl'),
                    'userPrompt': doc.get('user_prompt'),
                    'selectedDocuments': doc.get('selected_documents'),
                    'selectedEmails': doc.get('selected_emails'),
                    'generatedEmail': doc.get('generated_email')
                })

            return email_history

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch email history from the database: {e}")